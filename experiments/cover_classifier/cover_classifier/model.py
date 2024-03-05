"""Train a model to classify board game covers."""

import logging

import lightning
import torchmetrics
from torch import nn, optim
from torch.nn import functional as F
from torchvision.models import ResNet, ResNet50_Weights, resnet50

LOGGER = logging.getLogger(__name__)


class CoverClassifier(lightning.LightningModule):
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

        self.train_accuracy = torchmetrics.Accuracy(
            task="multilabel",
            num_labels=num_classes,
        )
        self.train_f1 = torchmetrics.F1Score(
            task="multilabel",
            num_labels=num_classes,
        )

        self.val_accuracy = torchmetrics.Accuracy(
            task="multilabel",
            num_labels=num_classes,
        )
        self.val_f1 = torchmetrics.F1Score(
            task="multilabel",
            num_labels=num_classes,
        )

        self.test_accuracy = torchmetrics.Accuracy(
            task="multilabel",
            num_labels=num_classes,
        )
        self.test_f1 = torchmetrics.F1Score(
            task="multilabel",
            num_labels=num_classes,
        )

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
