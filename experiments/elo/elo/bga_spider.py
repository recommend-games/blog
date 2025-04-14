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
        },
        "JOBDIR": ".jobs",
    }

    max_rank_scraped = None
    regex = re.compile("globalUserInfos=(.+);$", flags=re.MULTILINE)

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
