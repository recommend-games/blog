"""Train a model to classify board game covers."""

import logging
from pathlib import Path

import lightning as L
import torch
from torch import nn
from torch import optim
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchvision.models import resnet50, ResNet, ResNet50_Weights
import torchmetrics as M

# from tqdm import tqdm

from cover_classifier.data import BoardGameDataset

LOGGER = logging.getLogger(__name__)


class CoverClassifier(L.LightningModule):
    """Lightning module for cover classification."""

    def __init__(self, num_classes: int, weights: ResNet50_Weights):
        super().__init__()
        self.model: ResNet = resnet50(weights=weights)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        self.criterion = nn.BCEWithLogitsLoss()
        # self.accuracy = M.Accuracy(task="multilabel", num_labels=num_classes)
        # self.f1 = M.F1Score(task="multilabel", num_labels=num_classes)
        self.save_hyperparameters()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        images, labels, _ = batch
        outputs = self(images)
        loss = self.criterion(outputs, labels.float())
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        images, labels, _ = batch
        outputs = self(images)
        loss = self.criterion(outputs, labels.float())
        self.log("val_loss", loss)
        # self.accuracy(outputs, labels)
        # self.f1(outputs, labels)
        return loss

    def test_step(self, batch, batch_idx):
        images, labels, _ = batch
        outputs = self(images)
        loss = self.criterion(outputs, labels.float())
        self.log("test_loss", loss)
        # self.accuracy(outputs, labels)
        # self.f1(outputs, labels)
        return loss

    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=1e-3)

    # def training_epoch_end(self, outputs):
    #     self.log("train_acc", self.accuracy.compute())
    #     self.log("train_f1", self.f1.compute())

    # def validation_epoch_end(self, outputs):
    #     self.log("val_acc", self.accuracy.compute())
    #     self.log("val_f1", self.f1.compute())

    # def test_epoch_end(self, outputs):
    #     self.log("test_acc", self.accuracy.compute())
    #     self.log("test_f1", self.f1.compute())


def train(
    data_dir: str | Path,
    images_dir: str | Path,
    test_size: float = 0.05,
    val_size: float = 0.05,
    batch_size: int = 128,
    num_epochs: int = 10,
    # device: str | torch.device = torch.device("cpu"),
    model_dir: str | Path | None = None,
    # resume: bool = False,
) -> nn.Module:
    """Train a model to classify board game covers."""

    data_dir = Path(data_dir).resolve()
    images_dir = Path(images_dir).resolve()

    assert data_dir.is_dir(), f"Data directory does not exist: {data_dir}"
    assert images_dir.is_dir(), f"Images directory does not exist: {images_dir}"
    assert 0 < test_size < 1, f"Test size must be between 0 and 1: {test_size}"
    assert 0 < val_size < 1, f"Validation size must be between 0 and 1: {val_size}"
    assert (
        0 < test_size + val_size < 1
    ), f"Test and validation sizes must sum to less than 1: {test_size + val_size}"

    weights = ResNet50_Weights.DEFAULT

    dataset = BoardGameDataset(
        games_file=data_dir / "scraped" / "bgg_GameItem.jl",
        types_file=data_dir / "scraped" / "bgg_GameType.csv",
        image_root_dir=images_dir,
        transform=weights.transforms(),
        require_any_type=True,
        max_samples=1_000_000,
        # device=device,
    )
    num_classes = len(dataset.classes)
    # TODO: games without any type should be in a holdout set meant for human review

    train_dataset, test_dataset, val_dataset = random_split(
        dataset, (1 - test_size - val_size, test_size, val_size)
    )
    LOGGER.info(
        "Split into %d training, %d test and %d validation samples",
        len(train_dataset),
        len(test_dataset),
        len(val_dataset),
    )
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
    )
    test_dataloader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=True,
    )
    val_dataloader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    model = CoverClassifier(num_classes, weights)
    # model_path = Path(model_path).resolve() if model_path else None

    # if resume and model_path and model_path.exists():
    #     LOGGER.info("Resuming training from %s", model_path)
    #     model.load_state_dict(torch.load(model_path))

    # LOGGER.info("Training model on %s", device)
    # model.to(device)

    # criterion = nn.BCEWithLogitsLoss()
    # optimizer = optim.Adam(model.parameters(), lr=0.001)

    # TODO: Let Lightning handle training loop
    # num_epochs = 10
    # for epoch in range(num_epochs):
    #     print(f"Epoch {epoch+1:>3d}/{num_epochs:>3d}")

    #     model.train()
    #     for images, labels, _ in tqdm(train_dataloader):
    #         optimizer.zero_grad()
    #         outputs = model(images.to(device))
    #         loss = criterion(outputs, labels.float().to(device))
    #         loss.backward()
    #         optimizer.step()

    #     model.eval()
    #     with torch.no_grad():
    #         losses = torch.tensor(
    #             [
    #                 criterion(model(inputs.to(device)), labels.float().to(device))
    #                 for inputs, labels, _ in tqdm(test_dataloader)
    #             ]
    #         )
    #         print(f"Loss: {losses.mean().item():>7.4f}")
    #         print_game_results(model, test_dataloader, dataset.classes, max_results=3)

    #     if model_path:
    #         torch.save(model.state_dict(), model_path)

    trainer = L.Trainer(
        max_epochs=num_epochs,
        default_root_dir=Path(model_dir).resolve() if model_dir else None,
    )
    trainer.fit(
        model=model,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
    )
    trainer.test(model, dataloaders=test_dataloader)

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
            error = round(pred.item()) != label.item()
            print(f"\t{class_:15}: {pred:>6.1%} ({label} {'❌' if error else '✅'})")
