"""Board game dataset."""

from itertools import islice
import json
import logging
from pathlib import Path
import random
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
        max_samples: int | None = None,
        require_any_type: bool = False,
    ):
        image_root_dir = Path(image_root_dir).resolve()
        self.types_mlb = self.read_types_file(types_file)

        self.classes = self.types_mlb.classes
        self.classes_set = frozenset(self.classes)
        LOGGER.info("Game types: %s", self.classes)

        self.transform = transform
        self.require_any_type = require_any_type

        self.bgg_ids, self.images, self.labels = self.read_games_file(
            games_file,
            image_root_dir,
            max_samples,
        )

        assert len(self.bgg_ids) == len(self.images) == len(self.labels)
        LOGGER.info("Loaded %d games and images in total", len(self.bgg_ids))

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
        max_samples: int | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Read games from file."""

        games_file = Path(games_file).resolve()
        LOGGER.info("Reading games from file <%s>", games_file)
        with games_file.open(encoding="utf-8") as file:
            lines = islice(file, max_samples) if max_samples else file
            games = (
                self._parse_game(json.loads(line), image_dir) for line in tqdm(lines)
            )
            bgg_ids, images, labels = zip(*filter(None, games))
        bgg_ids_tensor = torch.tensor(bgg_ids, dtype=torch.int32)
        images_tensor = torch.stack(images)
        labels_tensor = torch.stack(labels)
        return bgg_ids_tensor, images_tensor, labels_tensor

    def _parse_game(
        self,
        game: dict[str, Any],
        image_dir: Path,
    ) -> tuple[int, torch.Tensor, torch.Tensor] | None:
        bgg_id: int | None = self.JMESPATH_BGG_ID.search(game)
        image_path_str: str | None = self.JMESPATH_IMAGE_PATH.search(game)
        game_types_raw: list[str] | None = self.JMESPATH_GAME_TYPES.search(game)

        if not bgg_id or not image_path_str:
            return None

        game_type_labels = [
            t
            for s in game_types_raw or ()
            if (t := s.split(":")[0]) in self.classes_set
        ]
        game_types = self.types_mlb.transform([game_type_labels])[0]
        if self.require_any_type and not any(game_types):
            LOGGER.debug("No valid game types for game <%s>", bgg_id)
            return None

        image_path = Path(image_dir / image_path_str).resolve()
        if not image_path.exists():
            LOGGER.debug(
                "Image file <%s> for game <%s> does not exist",
                image_path,
                bgg_id,
            )
            return None

        if random.random() > 0.15:
            # randomly skip 85% of images
            return None

        image = self._read_and_transform_image(str(image_path))

        return bgg_id, image, torch.from_numpy(game_types)

    def _read_and_transform_image(self, image_path: str) -> torch.Tensor:
        image = read_image(image_path)
        if self.transform:
            image = self.transform(image)
        return image

    def __len__(self) -> int:
        return len(self.bgg_ids)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.images[idx], self.labels[idx], self.bgg_ids[idx]