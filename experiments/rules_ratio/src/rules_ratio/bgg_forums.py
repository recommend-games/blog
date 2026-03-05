from collections.abc import Generator
import csv
import os
import scrapy
from pytility import parse_int
from scrapy import Request, Response


class BggForumsSpider(scrapy.Spider):
    name = "bgg-forums"
    base_domain = "boardgamegeek.com"
    allowed_domains = (base_domain,)
    base_api_url = f"https://{base_domain}/xmlapi2"

    custom_settings = {
        "DOWNLOAD_DELAY": 10,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "CONCURRENT_REQUESTS_PER_IP": 8,
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
                    bgg_id = parse_int(row.get("bgg_id"))
                    if not bgg_id:
                        self.logger.warning("Skipping row with invalid bgg_id: %s", row)
                        continue
                    num_votes = parse_int(row.get("num_votes")) or 0
                    self.logger.debug(
                        "Scheduling forums request for game ID <%s> (%d votes)",
                        bgg_id,
                        num_votes,
                    )
                    yield Request(
                        url=f"{self.base_api_url}/forumlist?id={bgg_id}&type=thing",
                        callback=self.parse,
                        priority=num_votes,
                    )

        except Exception as e:
            self.logger.error("Error reading games file <%s>", self.games_file)

    def parse(self, response: Response) -> Generator[dict]:
        pass
