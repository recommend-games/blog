import json
import logging
from pathlib import Path
from typing import Any, Callable, Union
import jmespath
import polars as pl
from PIL import Image
from sklearn.preprocessing import MultiLabelBinarizer
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

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
        self.types_mlb = self.read_types_file(types_file)
        self.game_data = self.read_games_file(games_file)
        self.image_root_dir = Path(image_root_dir).resolve()
        self.transform = transform

    def read_types_file(self, types_file: str | Path) -> MultiLabelBinarizer:
        types_file = Path(types_file).resolve()
        LOGGER.info("Reading types from file <%s>", types_file)
        types = pl.read_csv(types_file)["name"].to_list()
        return MultiLabelBinarizer(classes=types).fit([])

    def read_games_file(self, games_file: Union[str, Path]) -> pl.DataFrame:
        games_file = Path(games_file).resolve()
        LOGGER.info("Reading games from file <%s>", games_file)
        with games_file.open() as file:
            games = (self._parse_game(json.loads(line)) for line in file)
            return pl.DataFrame(
                data=filter(None, games),
                schema=["bgg_id", "image_path", "types"],
                orient="row",
            )

    def _parse_game(self, game: dict[str, Any]) -> tuple | None:
        bgg_id: str = self.JMESPATH_BGG_ID.search(game)
        image_path = self.JMESPATH_IMAGE_PATH.search(game)
        game_types = self.JMESPATH_GAME_TYPES.search(game)
        if not bgg_id or not image_path or not game_types:
            return None
        game_types = self.types_mlb.transform([[t.split(":")[0] for t in game_types]])[
            0
        ]
        return bgg_id, image_path, game_types

    def __len__(self) -> int:
        return len(self.game_data)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        image_path = self.image_root_dir / self.game_data[idx, "image_path"]
        image = Image.open(image_path).convert("RGB")

        labels = torch.tensor(
            self.game_data[idx, "types"],
            dtype=torch.bool,
        )

        if self.transform:
            image = self.transform(image)

        return image, labels


# # Example usage:
# csv_file_path = "path/to/your/csv/file.csv"
# image_root_dir = "path/to/your/image/directory"

# # Define the data transformation
# transform = transforms.Compose(
#     [
#         transforms.Resize((224, 224)),
#         transforms.ToTensor(),
#     ]
# )

# # Create an instance of your custom dataset
# board_game_dataset = BoardGameDataset(
#     csv_file=csv_file_path, root_dir=image_root_dir, transform=transform
# )

# # Create a DataLoader to iterate over your dataset
# batch_size = 32
# data_loader = DataLoader(board_game_dataset, batch_size=batch_size, shuffle=True)

# # Example of accessing data in the DataLoader
# for inputs, labels in data_loader:
#     # Your training/validation loop here
#     pass
