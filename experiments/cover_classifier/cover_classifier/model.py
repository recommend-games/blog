"""Train a model to classify board game covers."""

import logging
from pathlib import Path

import torch
from torch import nn
from torch import optim
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchvision.models import resnet50, ResNet, ResNet50_Weights

from tqdm import tqdm

from cover_classifier.data import BoardGameDataset

LOGGER = logging.getLogger(__name__)


def train(
    data_dir: str | Path,
    images_dir: str | Path,
    test_size: float = 0.01,
    batch_size: int = 128,
    device: str | torch.device = torch.device("cpu"),
    model_path: str | Path | None = None,
    resume: bool = False,
) -> nn.Module:
    """Train a model to classify board game covers."""

    data_dir = Path(data_dir).resolve()
    images_dir = Path(images_dir).resolve()

    assert data_dir.is_dir(), f"Data directory does not exist: {data_dir}"
    assert images_dir.is_dir(), f"Images directory does not exist: {images_dir}"
    assert 0 < test_size < 1, f"Test size must be between 0 and 1: {test_size}"

    weights = ResNet50_Weights.DEFAULT
    model: ResNet = resnet50(weights=weights)

    dataset = BoardGameDataset(
        games_file=data_dir / "scraped" / "bgg_GameItem.jl",
        types_file=data_dir / "scraped" / "bgg_GameType.csv",
        image_root_dir=images_dir,
        transform=weights.transforms(),
        require_any_type=True,
        device=device,
    )
    num_classes = len(dataset.classes)
    # TODO: games without any type should be in a holdout set meant for human review

    train_dataset, test_dataset = random_split(dataset, (1 - test_size, test_size))
    LOGGER.info(
        "Split into %d training and %d test samples",
        len(train_dataset),
        len(test_dataset),
    )
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        # num_workers=8,
    )
    test_dataloader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=True,
        # num_workers=8,
    )

    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model_path = Path(model_path).resolve() if model_path else None

    if resume and model_path and model_path.exists():
        LOGGER.info("Resuming training from %s", model_path)
        model.load_state_dict(torch.load(model_path))

    LOGGER.info("Training model on %s", device)
    model.to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # TODO: Let Lightning handle training loop
    num_epochs = 10
    for epoch in range(num_epochs):
        print(f"Epoch {epoch+1:>3d}/{num_epochs:>3d}")

        model.train()
        for images, labels, _ in tqdm(train_dataloader):
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels.float())
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            losses = torch.tensor(
                [
                    criterion(model(inputs), labels.float())
                    for inputs, labels, _ in tqdm(test_dataloader)
                ]
            )
            print(f"Loss: {losses.mean().item():>7.4f}")
            print_game_results(model, test_dataloader, dataset.classes, max_results=3)

        if model_path:
            torch.save(model.state_dict(), model_path)

    return model


@torch.no_grad()
def print_game_results(model, dataloader, classes, max_results: int | None = None):
    """Print results for a batch of games."""
    image_batch, label_batch, bgg_id_batch = next(iter(dataloader))
    if max_results:
        image_batch, label_batch, bgg_id_batch = (
            image_batch[:max_results],
            label_batch[:max_results],
            bgg_id_batch[:max_results],
        )
    model.eval()
    prediction_batch = F.sigmoid(model(image_batch))
    for bgg_id, labels, predictions in zip(bgg_id_batch, label_batch, prediction_batch):
        print(f"https://boardgamegeek.com/boardgame/{bgg_id.item()}")
        for pred, label, class_ in sorted(
            zip(predictions, labels, classes),
            reverse=True,
        ):
            print(f"\t{class_:15}: {pred:>6.1%} ({label})")
