from collections.abc import Generator
from datetime import datetime, timezone
import json
import math
import re
from typing import Any

from scrapy import FormRequest, Request, Spider
from scrapy.http import Response, TextResponse


class BaseFilter:
    type_name: str

    def __init__(self, feed_options: dict[str, Any] | None) -> None:
        self.feed_options = feed_options

    def accepts(self, item: Any) -> bool:
        if "type" in item and item["type"] == self.type_name:
            return True
        return False


class GameFilter(BaseFilter):
    type_name = "game"


class RankingFilter(BaseFilter):
    type_name = "ranking"


class MatchFilter(BaseFilter):
    type_name = "match"


class BgaSpider(Spider):
    name = "bga"
    start_urls = ("https://en.boardgamearena.com/gamelist?allGames=",)

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "FEED_EXPORT_BATCH_ITEM_COUNT": 10_000,
        "FEEDS": {
            "results/games-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "item_filter": GameFilter,
                "overwrite": False,
                "store_empty": False,
            },
            "results/rankings-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "item_filter": RankingFilter,
                "overwrite": False,
                "store_empty": False,
            },
            "results/matches-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "item_filter": MatchFilter,
                "overwrite": False,
                "store_empty": False,
            },
        },
        "JOBDIR": ".jobs",
    }

    scrape_rankings = False
    max_rank_scraped = None
    regex = re.compile("globalUserInfos=(.+);$", flags=re.MULTILINE)

    scrape_matches = False
    base_match_url = "https://en.boardgamearena.com/message/board"
    max_matches_per_page = 9500

    def parse(self, response: Response) -> Generator[dict | Request]:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        for text in response.xpath(
            "//script[@type = 'text/javascript']/text()"
        ).getall():
            match = self.regex.search(text)
            if not match:
                continue

            try:
                payload = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

            if not isinstance(payload, dict) or "game_list" not in payload:
                continue

            for game in payload["game_list"]:
                game["type"] = "game"
                game["scraped_at"] = now
                yield game

                if self.scrape_rankings:
                    yield FormRequest(
                        url=response.urljoin("/gamepanel/gamepanel/getRanking.html"),
                        method="POST",
                        formdata={
                            "game": str(game["id"]),
                            "start": "0",
                            "mode": "elo",
                        },
                        callback=self.parse_ranking,
                        meta={"game_id": game["id"]},
                        priority=0,
                    )

                if self.scrape_matches:
                    yield Request(
                        url=self.build_match_url(game["id"]),
                        callback=self.parse_matches,
                        meta={"game_id": game["id"]},
                    )

    def parse_ranking(self, response: Response) -> Generator[dict | Request]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        game_id = response.meta["game_id"]
        payload = response.json()

        rank_nos = []

        for entry in payload["data"]["ranks"]:
            entry["game_id"] = game_id
            entry["type"] = "ranking"
            entry["scraped_at"] = now
            yield entry
            rank_nos.append(int(entry["rank_no"]))

        max_rank_no = max(rank_nos, default=math.inf)

        if not self.max_rank_scraped or max_rank_no < self.max_rank_scraped:
            yield response.request.replace(
                formdata={
                    "game": str(game_id),
                    "start": str(max_rank_no),
                    "mode": "elo",
                },
                meta={"game_id": game_id},
                priority=-max_rank_no,
            )

    def build_match_url(self, game_id: int, from_time: int = None, from_id: int = None):
        params = {
            "type": "lastresult",
            "id": str(game_id),
            "social": "false",
            "per_page": str(self.max_matches_per_page),
            "dojo.preventCache": "1",  # TODO: timestamp
        }

        if from_time is not None and from_id is not None:
            params["page"] = "0"
            params["from_time"] = str(from_time)
            params["from_id"] = str(from_id)

        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_match_url}?{query}"

    def parse_matches(self, response: Response) -> Generator[dict[str, Any] | Request]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        game_id = response.meta["game_id"]
        payload = response.json()

        for match in payload["data"]["news"]:
            match["game_id"] = game_id
            match["type"] = "match"
            match["scraped_at"] = now
            # TODO: parse match["html"] for match results
            yield match

        # TODO: request next page
