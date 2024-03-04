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

    def __init__(
        self,
        *,
        num_classes: int,
        weights: ResNet50_Weights,
        learning_rate: float = 1e-3,
    ):
        super().__init__()

        self.res_net: ResNet = resnet50(weights=weights)
        res_net_out_features = self.res_net.fc.in_features
        self.res_net.fc = nn.Identity()
        # freeze resnet layers
        self.res_net.requires_grad_(False)

        self.layers = nn.Sequential(
            nn.Linear(res_net_out_features, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

        self.loss_fn = nn.BCEWithLogitsLoss()

        self.learning_rate = learning_rate

        self.train_accuracy = M.Accuracy(task="multilabel", num_labels=num_classes)
        self.train_f1 = M.F1Score(task="multilabel", num_labels=num_classes)

        self.val_accuracy = M.Accuracy(task="multilabel", num_labels=num_classes)
        self.val_f1 = M.F1Score(task="multilabel", num_labels=num_classes)

        self.test_accuracy = M.Accuracy(task="multilabel", num_labels=num_classes)
        self.test_f1 = M.F1Score(task="multilabel", num_labels=num_classes)

        self.save_hyperparameters()

    def forward(self, x):
        return self.layers(self.res_net(x))

    def training_step(self, batch, batch_idx=0, dataloader_idx=0):
        images, labels, _ = batch
        logits = self(images)

        loss = self.loss_fn(logits, labels.float())
        self.log("train_loss", loss)

        outputs = F.sigmoid(logits)

        self.train_accuracy(outputs, labels)
        self.log("train_accuracy", self.train_accuracy, prog_bar=True)

        self.train_f1(outputs, labels)
        self.log("train_f1", self.train_f1)

        return loss

    def validation_step(self, batch, batch_idx=0, dataloader_idx=0):
        images, labels, _ = batch
        logits = self(images)

        loss = self.loss_fn(logits, labels.float())
        self.log("val_loss", loss)

        outputs = F.sigmoid(logits)

        self.val_accuracy(outputs, labels)
        self.log("val_accuracy", self.val_accuracy)

        self.val_f1(outputs, labels)
        self.log("val_f1", self.val_f1)

        return loss

    def test_step(self, batch, batch_idx=0, dataloader_idx=0):
        images, labels, _ = batch
        logits = self(images)

        loss = self.loss_fn(logits, labels.float())
        self.log("test_loss", loss)

        outputs = F.sigmoid(logits)

        self.test_accuracy(outputs, labels)
        self.log("test_accuracy", self.test_accuracy)

        self.test_f1(outputs, labels)
        self.log("test_f1", self.test_f1)

        return loss

    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=self.learning_rate)


def train(
    data_dir: str | Path,
    images_dir: str | Path,
    test_size: float = 0.05,
    val_size: float = 0.05,
    batch_size: int = 128,
    num_epochs: int = 10,
    model_dir: str | Path | None = None,
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
        shuffle=False,
    )
    val_dataloader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    # TODO: Load model from best checkpoint if it exists

    model = CoverClassifier(num_classes=num_classes, weights=weights)

    trainer = L.Trainer(
        max_epochs=num_epochs,
        default_root_dir=Path(model_dir).resolve() if model_dir else None,
    )

    # TODO: Checkpoints, early stopping, logger, tune learning rate etc.

    trainer.fit(
        model=model,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
    )

    trainer.test(model, dataloaders=test_dataloader)

    # TODO: Link best checkpoint

    print_game_results(model, test_dataloader, dataset.classes, max_results=3)

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
