from collections.abc import AsyncGenerator, Generator
import csv
import os
from typing import Any
from pytility import parse_date, parse_float
from pytility import parse_int
from scrapy import Spider
from scrapy.http import Request, TextResponse


class BggForumsSpider(Spider):
    name = "bgg-forums"
    base_domain = "boardgamegeek.com"
    allowed_domains = (base_domain,)
    base_api_url = f"https://{base_domain}/xmlapi2"

    _download_delay = parse_float(os.getenv("DOWNLOAD_DELAY")) or 10.0
    _results_dir = os.getenv("RESULTS_DIR", "results")
    _jobdir = os.getenv("JOBDIR", ".jobs")
    _concurrent_requests = parse_int(os.getenv("CONCURRENT_REQUESTS_PER_DOMAIN")) or 8
    _feed_batch_count = parse_int(os.getenv("FEED_EXPORT_BATCH_ITEM_COUNT")) or 10_000

    custom_settings = {
        "DOWNLOAD_DELAY": _download_delay,
        "CONCURRENT_REQUESTS_PER_DOMAIN": _concurrent_requests,
        "LOG_FORMATTER": "scrapy_extensions.QuietLogFormatter",
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_extensions.middlewares.AuthHeaderMiddleware": 301,
        },
        "FEED_EXPORT_BATCH_ITEM_COUNT": _feed_batch_count,
        "FEEDS": {
            f"{_results_dir}/games-%(time)s-%(batch_id)05d.jl": {
                "format": "jsonlines",
                "overwrite": False,
                "store_empty": False,
            },
        },
        "JOBDIR": _jobdir,
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

    async def start(self) -> AsyncGenerator[Request]:
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
                    yield Request(
                        url=f"{self.base_api_url}/forumlist?id={bgg_id}&type=thing",
                        callback=self.parse,
                        priority=num_votes,
                    )

        except Exception as e:
            self.logger.error("Error reading games file <%s>", self.games_file)

    def parse(self, response: TextResponse) -> Generator[dict[str, Any]]:
        bgg_id = parse_int(response.xpath("/forums/@id").get())
        if not bgg_id:
            self.logger.error(
                "Could not determine bgg_id for forums response: %s",
                response.url,
            )
            return

        for forum in response.xpath("/forums/forum"):
            forum_id = parse_int(forum.xpath("@id").get())
            if not forum_id:
                self.logger.warning(
                    "Skipping forum with invalid ID for game <%s>: %s",
                    bgg_id,
                    forum.get(),
                )
                continue

            yield {
                "bgg_id": bgg_id,
                "forum_id": forum_id,
                "title": forum.xpath("@title").get(),
                "num_threads": parse_int(forum.xpath("@numthreads").get()) or 0,
                "num_posts": parse_int(forum.xpath("@numposts").get()) or 0,
                "last_post_date": parse_date(forum.xpath("@lastpostdate").get()),
            }
