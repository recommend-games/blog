from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, kw_only=True)
class GameData:
    bgg_id: int
    name: str
    date_review: date | datetime
    days_before: int = 60
    days_after: int = 30
    max_control_games: int = 300


REVIEWS = (
    GameData(
        bgg_id=332686,
        name="John Company",
        date_review=date(2023, 11, 28),
    ),
    GameData(
        bgg_id=330592,
        name="Phantom Ink",
        date_review=date(2023, 10, 26),
    ),
    GameData(
        bgg_id=368061,
        name="Zoo Vadis",
        date_review=date(2023, 10, 19),
    ),
    GameData(
        bgg_id=358386,
        name="Moon",
        date_review=date(2023, 10, 12),
    ),
    GameData(
        bgg_id=351538,
        name="Bamboo",
        date_review=date(2023, 10, 5),
    ),
    GameData(
        bgg_id=350184,
        name="Earth",
        date_review=date(2023, 9, 28),
    ),
    GameData(
        bgg_id=354568,
        name="Amun-Re",
        date_review=date(2023, 9, 22),
    ),
    GameData(
        bgg_id=11,
        name="Bohnanza",
        date_review=date(2023, 9, 14),
    ),
    GameData(
        bgg_id=311031,
        name="Five Three Five",
        date_review=date(2023, 8, 23),
    ),
    GameData(
        bgg_id=298383,
        name="Golem",
        date_review=date(2023, 8, 17),
    ),
    GameData(
        bgg_id=386937,
        name="Lacuna",
        date_review=date(2023, 8, 3),
    ),
    GameData(
        bgg_id=331571,
        name="My Gold Mine",
        date_review=date(2023, 7, 19),
    ),
    GameData(
        bgg_id=367771,
        name="Stomp the Plank",
        date_review=date(2023, 7, 6),
    ),
    GameData(
        bgg_id=177478,
        name="IKI",
        date_review=date(2023, 6, 29),
    ),
    GameData(
        bgg_id=362944,
        name="War of the Ring: The Card Game",
        date_review=date(2023, 6, 15),
    ),
    GameData(
        bgg_id=281549,
        name="Beast",
        date_review=date(2023, 6, 9),
    ),
    GameData(
        bgg_id=276086,
        name="Hamlet",
        date_review=date(2023, 5, 25),
    ),
    GameData(
        bgg_id=267609,
        name="Guards of Atlantis II",
        date_review=date(2023, 5, 18),
    ),
    GameData(
        bgg_id=295770,
        name="Frosthaven",
        date_review=date(2023, 5, 11),
    ),
    GameData(
        bgg_id=350205,
        name="Horseless Carriage",
        date_review=date(2023, 2, 9),
    ),
    GameData(
        bgg_id=811,
        name="Rummikub",
        date_review=date(2023, 1, 26),
    ),
    GameData(
        bgg_id=366013,
        name="Heat: Pedal to the Metal",
        date_review=date(2022, 12, 22),
    ),
)
