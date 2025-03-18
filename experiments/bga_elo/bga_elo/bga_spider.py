from collections.abc import Generator
import json
import re

from scrapy import FormRequest, Request, Spider
from scrapy.http import Response, TextResponse


class BgaSpider(Spider):
    name = "bga"
    start_urls = ("https://en.boardgamearena.com/gamelist?allGames=",)

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }

    max_ranking_pages = 10
    regex = re.compile("globalUserInfos=(.+);$", flags=re.MULTILINE)

    def parse(self, response: Response) -> Generator[dict | Request]:
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
                    meta={
                        "game_id": game["id"],
                        "start": 0,
                    },
                )

    def parse_ranking(self, response: Response) -> Generator[dict | Request]:
        game_id = response.meta["game_id"]
        start = response.meta["start"]

        if start < self.max_ranking_pages - 1:
            yield response.request.replace(
                formdata={
                    "game": str(game_id),
                    "start": str(start + 1),
                    "mode": "elo",
                },
                meta={
                    "game_id": game_id,
                    "start": start + 1,
                },
            )

        if not isinstance(response, TextResponse):
            return

        payload = response.json()

        for entry in payload["data"]["ranks"]:
            entry["game_id"] = game_id
            yield entry
