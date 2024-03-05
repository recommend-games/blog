"""Train a model to classify board game covers."""

import logging
import shutil
from pathlib import Path

import lightning
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchvision.models import ResNet50_Weights

from cover_classifier.data import BoardGameDataset
from cover_classifier.model import CoverClassifier

LOGGER = logging.getLogger(__name__)


def train(
    *,
    data_dir: str | Path,
    images_dir: str | Path,
    test_size: float = 0.05,
    val_size: float = 0.05,
    batch_size: int = 128,
    num_epochs: int = 10,
    save_dir: str | Path | None = None,
    model_path: str | Path | None = None,
    fast_dev_run: bool = False,
) -> nn.Module:
    """Train a model to classify board game covers."""

    data_dir = Path(data_dir).resolve()
    images_dir = Path(images_dir).resolve()
    save_dir = Path(save_dir).resolve() if save_dir else None
    model_path = Path(model_path).resolve() if model_path else None

    assert data_dir.is_dir(), f"Data directory does not exist: {data_dir}"
    assert images_dir.is_dir(), f"Images directory does not exist: {images_dir}"
    assert 0 < test_size < 1, f"Test size must be between 0 and 1: {test_size}"
    assert 0 < val_size < 1, f"Validation size must be between 0 and 1: {val_size}"
    assert (
        0 < test_size + val_size < 1
    ), f"Test and validation sizes must sum to less than 1: {test_size + val_size}"

    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
    if model_path:
        model_path.parent.mkdir(parents=True, exist_ok=True)

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
        dataset=dataset,
        lengths=(1 - test_size - val_size, test_size, val_size),
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

    if model_path and model_path.exists():
        LOGGER.info("Resuming model training from %s", model_path)
        model = CoverClassifier.load_from_checkpoint(model_path)
        assert model.hparams.num_classes == num_classes, (
            f"Model classes ({model.hparams.num_classes}) do not match "
            f"dataset classes ({num_classes})"
        )
    else:
        model = CoverClassifier(num_classes=num_classes, weights=weights)

    checkpoint_callback = lightning.pytorch.callbacks.model_checkpoint.ModelCheckpoint(
        monitor="val_loss",
        mode="min",
        save_top_k=3,
        save_last=True,
    )

    early_stopping_callback = lightning.pytorch.callbacks.early_stopping.EarlyStopping(
        monitor="val_loss",
        mode="min",
        min_delta=0.0,
        patience=5,
        verbose=True,
    )

    loggers = (
        [lightning.pytorch.loggers.csv_logs.CSVLogger(save_dir=save_dir)]
        if save_dir
        else []
    )

    trainer = lightning.Trainer(
        max_epochs=num_epochs,
        logger=loggers,
        callbacks=[checkpoint_callback, early_stopping_callback],
        default_root_dir=save_dir,
        fast_dev_run=fast_dev_run,
    )

    trainer.fit(
        model=model,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
    )

    trainer.test(
        model=model,
        dataloaders=test_dataloader,
    )

    if model_path:
        best_model_path = Path(checkpoint_callback.best_model_path).resolve()
        LOGGER.info("Copying best model from <%s> to <%s>", best_model_path, model_path)
        shutil.copyfile(src=best_model_path, dst=model_path)

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
