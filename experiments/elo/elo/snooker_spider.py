from collections.abc import Generator, Iterable
from datetime import datetime, timezone
import os
from typing import Any

from scrapy import Request, Spider
from scrapy.http import Response, TextResponse
from scrapy.utils.misc import arg_to_iter


class BaseFilter:
    type_name: str

    def __init__(self, feed_options: dict[str, Any] | None) -> None:
        self.feed_options = feed_options

    def accepts(self, item: Any) -> bool:
        if "type" in item and item["type"] == self.type_name:
            return True
        return False


class EventFilter(BaseFilter):
    type_name = "event"


class MatchFilter(BaseFilter):
    type_name = "match"


class PlayerFilter(BaseFilter):
    type_name = "player"


class SnookerSpider(Spider):
    name = "snooker"

    api_url = "https://api.snooker.org/"
    start_season: int = 1974
    end_season: int | None = None
    tours = (
        "challenge",
        "ebsa",
        "ibsf",
        "main",
        "other",
        "q",
        "seniors",
        "women",
        "wsf",
    )

    custom_settings = {
        # Rate limit 10: requests per minute
        "DOWNLOAD_DELAY": 60 / 10,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "FEED_EXPORT_BATCH_ITEM_COUNT": 10_000,
        "FEEDS": {
            "results/snooker/events-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "item_filter": EventFilter,
                "overwrite": False,
                "store_empty": False,
            },
            "results/snooker/matches-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "item_filter": MatchFilter,
                "overwrite": False,
                "store_empty": False,
            },
            "results/snooker/players-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "item_filter": PlayerFilter,
                "overwrite": False,
                "store_empty": False,
            },
        },
        "JOBDIR": ".jobs",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.snooker_api_header = os.getenv("SNOOKER_API_HEADER")
        if not self.snooker_api_header:
            raise ValueError("SNOOKER_API_HEADER environment variable is not set")

    def start_requests(self) -> Iterable[Request]:
        end_season = self.end_season or datetime.now(timezone.utc).year
        for season in range(self.start_season, end_season + 1):
            yield Request(
                url=f"{self.api_url}?t=5&s={season}",
                callback=self.parse_season,
                headers={"X-Requested-By": self.snooker_api_header},
                priority=3,
            )
            for tour in arg_to_iter(self.tours):
                yield Request(
                    url=f"{self.api_url}?t=5&s={season}&tr={tour}",
                    callback=self.parse_season,
                    headers={"X-Requested-By": self.snooker_api_header},
                    priority=2,
                )

    def parse_season(self, response: Response) -> Generator[dict | Request]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        for event in response.json():
            event["type"] = "event"
            event["scraped_at"] = now
            yield event

            event_id = event["ID"]
            yield Request(
                url=f"{self.api_url}?t=6&e={event_id}",
                callback=self.parse_event,
                headers={"X-Requested-By": self.snooker_api_header},
            )

    def parse_event(self, response: Response) -> Generator[dict | Request]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        for match in response.json():
            match["type"] = "match"
            match["scraped_at"] = now
            yield match

            player_ids = {match["Player1ID"], match["Player2ID"]}
            for player_id in player_ids:
                yield Request(
                    url=f"{self.api_url}?p={player_id}",
                    callback=self.parse_players,
                    headers={"X-Requested-By": self.snooker_api_header},
                    priority=1,
                )

    def parse_players(self, response: Response) -> Generator[dict]:
        if not isinstance(response, TextResponse):
            self.logger.warning("Response <%s> is not a TextResponse", response.url)
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        for player in response.json():
            player["type"] = "player"
            player["scraped_at"] = now
            yield player
