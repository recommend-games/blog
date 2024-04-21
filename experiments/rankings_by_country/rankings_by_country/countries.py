from functools import cache
import json
import logging
from pathlib import Path
from country_converter import CountryConverter

LOGGER = logging.getLogger(__name__)
CONVERTER = CountryConverter()
MAPPING_FILE = Path(__file__).parent / "country_mapping.json"


@cache
def load_country_mapping(path: str | Path = MAPPING_FILE) -> dict[str, str]:
    path = Path(path).resolve()
    LOGGER.info("Loading country mapping from <%s>", path)
    with path.open() as file:
        return json.load(file)


@cache
def get_country_code(country_name: str) -> str | None:
    country_mapping = load_country_mapping()
    country = country_mapping.get(country_name)
    if country:
        return country
    return CONVERTER.convert(names=country_name, to="ISO2", not_found="") or None
