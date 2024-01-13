"""Train the cover classifier model."""

import logging
from pathlib import Path
import sys

from cover_classifier.model import train

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def main():
    """Train the cover classifier model."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )

    train(
        data_dir=BASE_DIR.parent / "board-game-data",
        images_dir=BASE_DIR.parent / "board-game-scraper" / "images",
    )


if __name__ == "__main__":
    main()
