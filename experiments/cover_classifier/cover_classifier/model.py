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
    )
    num_classes = len(dataset.classes)

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

    model_path = Path(model_path).resolve() if model_path else None

    if resume and model_path and model_path.exists():
        LOGGER.info("Resuming training from %s", model_path)
        model.load_state_dict(torch.load(model_path))
    else:
        model.fc = nn.Linear(model.fc.in_features, num_classes)

    LOGGER.info("Training model on %s", device)
    model.to(device)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 10
    for epoch in range(num_epochs):
        print(f"Epoch {epoch+1:>3d}/{num_epochs:>3d}")

        model.train()
        for images, labels in tqdm(train_dataloader):
            optimizer.zero_grad()
            outputs = model(images.to(device))
            loss = criterion(outputs, labels.float().to(device))
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            losses = torch.tensor(
                [
                    criterion(model(inputs.to(device)), labels.float().to(device))
                    for inputs, labels in tqdm(test_dataloader)
                ]
            )
            print(f"Loss: {losses.mean().item():>7.4f}")

            images, labels = next(iter(test_dataloader))
            output = F.sigmoid(model(images[:3, ...].to(device)))
            print(labels[:3, ...].to(device), output)

        if model_path:
            torch.save(model.state_dict(), model_path)

    return model
