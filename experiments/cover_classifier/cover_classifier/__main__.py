"""Train the cover classifier model."""

import logging
import sys
from pathlib import Path

import torch

from cover_classifier.model import train

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def main():
    """Train the cover classifier model."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

    model_path = Path().resolve() / "models" / "cover_classifier.pt"
    model_path.parent.mkdir(parents=True, exist_ok=True)

    train(
        data_dir=BASE_DIR.parent / "board-game-data",
        images_dir=BASE_DIR.parent / "board-game-scraper" / "images",
        device=device,
        model_path=model_path,
        resume=True,
    )


if __name__ == "__main__":
    main()
