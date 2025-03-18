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
                yield {
                    "bgg_id": game["bgg_id"],
                    "bga_id": game["id"],
                    "bga_slug": game["name"],
                    "name": game["display_name_en"],
                    "games_played": game["games_played"],
                }

                yield FormRequest(
                    url=response.urljoin("/gamepanel/gamepanel/getRanking.html"),
                    method="POST",
                    formdata={
                        "game": str(game["id"]),
                        "start": "0",
                        "mode": "elo",
                    },
                    callback=self.parse_ranking,
                )

    def parse_ranking(self, response: Response) -> Generator[dict | Request]:
        if not isinstance(response, TextResponse):
            return

        payload = response.json()

        for entry in payload["data"]["ranks"]:
            yield entry
