"""Train the cover classifier model."""

import logging
import sys
from pathlib import Path

from cover_classifier.model import train

PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent.parent


def main():
    """Train the cover classifier model."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )

    save_dir = PROJECT_DIR / "models"
    model_path = save_dir / "cover_classifier.ckpt"

    train(
        data_dir=BASE_DIR.parent / "board-game-data",
        images_dir=BASE_DIR.parent / "board-game-scraper" / "images",
        batch_size=128,
        num_epochs=10,
        save_dir=save_dir,
        model_path=model_path,
        fast_dev_run=False,
    )


if __name__ == "__main__":
    main()
