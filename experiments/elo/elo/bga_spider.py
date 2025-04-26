from collections.abc import Generator
from datetime import datetime, timezone
import jmespath
import json
import math
import re
import time
from typing import Any

from scrapy import FormRequest, Request, Selector, Spider
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
    base_url = "https://en.boardgamearena.com/"
    start_urls = (base_url,)

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": False,
        "DOWNLOAD_DELAY": 10,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 16,
        "LOG_FORMATTER": "scrapy_extensions.QuietLogFormatter",
        "FEED_EXPORT_BATCH_ITEM_COUNT": 100_000,
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

    request_token_url = "/account/auth/getRequestToken.html"
    request_token_path = jmespath.compile("data.request_token")
    request_token: str | None = None

    game_list_url = "/gamelist?allGames="
    game_list_regex = re.compile("globalUserInfos=(.+);$", flags=re.MULTILINE)

    scrape_rankings = False
    ranking_path = jmespath.compile("data.ranks")
    max_rank_scraped = None

    scrape_matches = True
    base_match_url = "/message/board"
    match_path = jmespath.compile("data.news")
    max_matches_per_page = 9500

    ordinal_regex = re.compile(r"(\d+)(st|nd|rd|th)")
    integer_regex = re.compile(r"(\d+)")

    def parse(self, response: Response) -> Request:
        return FormRequest(
            url=response.urljoin(self.request_token_url),
            formdata={"bgapp": "bga"},
            callback=self.parse_request_token,
            method="POST",
        )

    def parse_request_token(self, response: Response) -> Request | None:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        payload = response.json()
        request_token = self.request_token_path.search(payload)

        if not request_token:
            self.logger.error("Request token not found in response <%s>", response.url)
            return

        self.request_token = request_token

        return Request(
            url=response.urljoin(self.game_list_url),
            callback=self.parse_games,
            headers={"X-Request-Token": request_token},
        )

    def parse_games(self, response: Response) -> Generator[dict | Request]:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        for text in response.xpath(
            "//script[@type = 'text/javascript']/text()"
        ).getall():
            match = self.game_list_regex.search(text)
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
                        headers={"X-Request-Token": self.request_token},
                    )

                if self.scrape_matches:
                    games_played = int(game.get("games_played", 0))
                    priority = games_played // (2 * self.max_matches_per_page)
                    yield Request(
                        url=self.build_match_url(response, game["id"]),
                        method="GET",
                        callback=self.parse_matches,
                        meta={"game_id": game["id"]},
                        priority=priority,
                        headers={"X-Request-Token": self.request_token},
                    )

    def parse_ranking(self, response: Response) -> Generator[dict | Request]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        game_id = response.meta["game_id"]
        payload = response.json()

        entries = self.ranking_path.search(payload)

        if not entries:
            self.logger.error("Ranking not found in response <%s>", response.url)
            return

        rank_nos = []

        for entry in entries:
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
                priority=response.request.priority - 1,
            )

    def build_match_url(
        self,
        response: Response,
        game_id: int,
        from_time: int = None,
        from_id: int = None,
    ) -> str:
        params = {
            "type": "lastresult",
            "id": str(game_id),
            "social": "false",
            "per_page": str(self.max_matches_per_page),
            "dojo.preventCache": str(int(time.time() * 1000)),
        }

        if from_time is not None and from_id is not None:
            params["page"] = "0"
            params["from_time"] = str(from_time)
            params["from_id"] = str(from_id)

        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.base_match_url}?{query}"
        return response.urljoin(url)

    def parse_matches(self, response: Response) -> Generator[dict[str, Any] | Request]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        game_id = response.meta["game_id"]
        payload = response.json()

        matches = self.match_path.search(payload)

        if not matches:
            self.logger.error("Matches not found in response <%s>", response.url)
            return

        last_id = None
        last_timestamp = None

        for match in matches:
            match["game_id"] = game_id
            match["type"] = "match"
            match["scraped_at"] = now
            try:
                match["players"] = list(self.parse_match_html(match["html"]))
            except Exception:
                match["players"] = None
            last_id = match.get("id")
            last_timestamp = match.get("timestamp")
            yield match

        if last_id and last_timestamp:
            yield Request(
                url=self.build_match_url(response, game_id, last_timestamp, last_id),
                method="GET",
                callback=self.parse_matches,
                meta={"game_id": game_id},
                priority=response.request.priority - 1,
                headers={"X-Request-Token": self.request_token},
            )

    def parse_match_html(self, html: str) -> Generator[dict[str, Any]]:
        selector = Selector(text=html, type="html")

        for player_div in selector.css("div.board-score-entry"):
            rank_text = player_div.xpath("text()[1]").get() or ""
            match = self.ordinal_regex.search(rank_text)
            place = int(match.group(1)) if match else None

            player_link = player_div.css("a.playername")
            player_href = player_link.xpath("@href").get() or ""
            player_id = int(player_href.split("=")[-1]) if "=" in player_href else None

            player_name = player_link.xpath("text()").get()
            score_text = player_link.xpath("following-sibling::text()[1]").get() or ""
            match = self.integer_regex.search(score_text)
            score = int(match.group(1)) if match else None

            yield {
                "player_id": player_id,
                "player_name": player_name,
                "place": place,
                "score": score,
            }
