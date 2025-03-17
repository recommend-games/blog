import json
import re
import scrapy


class BgaSpider(scrapy.Spider):
    name = "bga"
    start_urls = ("https://en.boardgamearena.com/gamelist?allGames=",)

    regex = re.compile("globalUserInfos=(.+);$", flags=re.MULTILINE)

    def parse(self, response):
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
