import asyncio
import csv
import os
from collections.abc import AsyncGenerator, Generator, Iterable
from pathlib import Path
from typing import Any

from pytility import parse_date, parse_float, parse_int
from scrapy import Spider
from scrapy.http import Request, TextResponse


class BggForumsSpider(Spider):
    name = "bgg-forums"
    base_domain = "boardgamegeek.com"
    allowed_domains = (base_domain,)
    base_api_url = f"https://{base_domain}/xmlapi2"

    start_request_yield_interval = 100
    """Max distinct request priorities (Scrapy opens one disk queue per priority; caps open FDs)."""
    max_priority_buckets = 32

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
            f"{_results_dir}/forums-%(time)s-%(batch_id)05d.jl": {
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

        games_file = Path(self.games_file).resolve()
        self.logger.info("Reading games from file <%s>", games_file)

        requests = self._requests_from_games_file(games_file)
        async for request in self._yield_start_requests(requests):
            yield request

    def _requests_from_games_file(self, games_file: Path) -> Generator[Request]:
        try:
            with games_file.open("r", encoding="utf-8") as f:
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
                        priority=self._priority_bucket(num_votes),
                    )

        except Exception:
            self.logger.error("Error reading games file <%s>", self.games_file)

    def _priority_bucket(self, num_votes: int) -> int:
        """Map num_votes to a bounded priority in [0, max_priority_buckets) to limit open queue FDs."""
        if num_votes <= 0:
            return 0
        return min(self.max_priority_buckets - 1, max(0, num_votes.bit_length() - 1))

    async def _yield_start_requests(
        self,
        requests: Iterable[Request],
    ) -> AsyncGenerator[Request]:
        chunk_size = self.start_request_yield_interval
        for index, request in enumerate(requests, start=1):
            yield request
            if chunk_size > 0 and index % chunk_size == 0:
                await asyncio.sleep(0)

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
