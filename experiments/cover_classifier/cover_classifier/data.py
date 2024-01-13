"""Board game dataset."""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Union
import jmespath
import polars as pl
from sklearn.preprocessing import MultiLabelBinarizer
import torch
from torch.utils.data import Dataset
from torchvision.io import read_image
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)


class BoardGameDataset(Dataset):
    """Board game dataset."""

    JMESPATH_BGG_ID = jmespath.compile("bgg_id")
    JMESPATH_IMAGE_PATH = jmespath.compile("image_file[0].path")
    JMESPATH_GAME_TYPES = jmespath.compile("game_type")

    def __init__(
        self,
        games_file: str | Path,
        types_file: str | Path,
        image_root_dir: str | Path,
        transform: Callable | None = None,
    ):
        image_root_dir = Path(image_root_dir).resolve()
        self.types_mlb = self.read_types_file(types_file)
        self.classes = self.types_mlb.classes
        self.classes_set = frozenset(self.classes)
        self.game_data = self.read_games_file(games_file, image_root_dir)
        self.transform = transform

    def read_types_file(self, types_file: str | Path) -> MultiLabelBinarizer:
        """Read types from file."""

        types_file = Path(types_file).resolve()
        LOGGER.info("Reading types from file <%s>", types_file)
        types = pl.read_csv(types_file)["name"].to_list()
        return MultiLabelBinarizer(classes=types).fit([])

    def read_games_file(
        self,
        games_file: Union[str, Path],
        image_dir: Path,
    ) -> pl.DataFrame:
        """Read games from file."""

        games_file = Path(games_file).resolve()
        LOGGER.info("Reading games from file <%s>", games_file)
        with games_file.open(encoding="utf-8") as file:
            games = (
                self._parse_game(json.loads(line), image_dir) for line in tqdm(file)
            )
            return pl.DataFrame(
                data=filter(None, games),
                schema=["bgg_id", "image_path", "types"],
                orient="row",
            )

    def _parse_game(
        self,
        game: dict[str, Any],
        image_dir: Path,
    ) -> tuple[int, str, list[int]] | None:
        bgg_id: int | None = self.JMESPATH_BGG_ID.search(game)
        image_path_str: str | None = self.JMESPATH_IMAGE_PATH.search(game)
        game_types_raw: list[str] | None = self.JMESPATH_GAME_TYPES.search(game)

        if not bgg_id or not image_path_str or not game_types_raw:
            return None

        image_path = Path(image_dir / image_path_str).resolve()
        if not image_path.exists():
            LOGGER.debug(
                "Image file <%s> for game <%s> does not exist",
                image_path,
                bgg_id,
            )
            return None

        game_type_labels = [
            t for s in game_types_raw if (t := s.split(":")[0]) in self.classes_set
        ]
        game_types = self.types_mlb.transform([game_type_labels])[0]
        if not any(game_types):
            LOGGER.debug("No valid game types for game <%s>", bgg_id)
            return None

        return bgg_id, str(image_path), game_types

    def __len__(self) -> int:
        return len(self.game_data)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        image_path = self.game_data[idx, "image_path"]
        image = read_image(image_path)

        labels = torch.tensor(
            self.game_data[idx, "types"],
            dtype=torch.bool,
        )

        if self.transform:
            image = self.transform(image)

        return image, labels
