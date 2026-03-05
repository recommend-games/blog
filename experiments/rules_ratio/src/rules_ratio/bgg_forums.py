from collections.abc import Generator
import csv
import os
import scrapy
from scrapy import Request, Response


class BggForumsSpider(scrapy.Spider):
    name = "bgg-forums"
    allowed_domains = ("boardgamegeek.com",)

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_extensions.middlewares.AuthHeaderMiddleware": 301,
        },
        "AUTH_HEADER_ENABLED": True,
        "AUTH_HEADER_NAME": "Authorization",
        "AUTH_TOKEN_ATTR": "auth_token",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.auth_token = os.getenv("BGG_API_AUTH_TOKEN")
        if not self.auth_token:
            self.logger.warning("No BGG API auth token configured, requests may fail")

        self.games_file = os.getenv("BGG_GAMES_FILE")

    def start_requests(self) -> Generator[Request]:
        if not self.games_file:
            self.logger.error("No games file configured, cannot start spider")
            return

        try:
            with open(self.games_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    game_id = row.get("game_id")
                    self.logger.info(f"Scheduling forums request for game ID {game_id}")
                    # TODO: yield
        except Exception as e:
            self.logger.error("Error reading games file <%s>", self.games_file)

    def parse(self, response: Response) -> Generator[dict]:
        pass
