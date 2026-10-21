import torch
import torch.nn as nn
import lightning.pytorch as pl

from src.classification.models.cnn.model import CNNModel
from src.classification.models.common.metric import ClassificationMetric
from src.classification.models.common.postprocess import ClassificationPostprocess


class CNNLitModel(pl.LightningModule):
    def __init__(
        self,
        num_classes: int = 10,
        learning_rate: float = 0.001,
        weight_decay: float = 0.0001,
        backbone: str = "resnet18",
        weights_path: str | None = None,
        in_channels: int = 3,
    ):
        super().__init__()
        if num_classes < 2:
            raise ValueError("num_classes must be at least 2")
        self.model = CNNModel(
            backbone=backbone,
            num_classes=num_classes,
            weights_path=weights_path,
            in_channels=in_channels,
        )
        self.num_classes = num_classes
        self.loss_fn = nn.CrossEntropyLoss()
        self.postprocess = ClassificationPostprocess()
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.metrics = nn.ModuleDict({
            f"{stage}_metrics": ClassificationMetric(num_classes)
            for stage in ("train", "valid", "test")
        })
        self.save_hyperparameters()

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.model(images)

    def _shared_step(self, batch, stage):
        if not isinstance(batch, (tuple, list)) or len(batch) != 2:
            raise ValueError("Classification steps require an (images, targets) batch")
        images, targets = batch
        logits = self(images)
        if not isinstance(logits, torch.Tensor) or logits.ndim != 2 or logits.shape[1] != self.num_classes:
            raise ValueError("Model must return logits with shape [batch, num_classes]")
        loss = self.loss_fn(logits, targets)
        metrics = self.metrics[f"{stage}_metrics"]
        metrics.update_metrics(logits, targets)
        self.log(
            f"{stage}_loss", loss,
            on_step=(stage == "train"), on_epoch=True,
            batch_size=targets.shape[0], sync_dist=True,
            prog_bar=False,
        )
        # Lightning computes and resets logged Metric objects at epoch boundaries.
        for name, metric in metrics.items():
            self.log(
                f"{stage}_{name}", metric,
                on_step=False, on_epoch=True, prog_bar=False,
            )
        return loss

    def training_step(self, batch, batch_idx):
        return self._shared_step(batch, "train")

    def validation_step(self, batch, batch_idx):
        return self._shared_step(batch, "valid")

    def test_step(self, batch, batch_idx):
        return self._shared_step(batch, "test")

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        images = batch[0] if isinstance(batch, (tuple, list)) else batch
        return self.postprocess(self(images))

    def configure_optimizers(self):
        # LightningCLI can replace this using its native optimizer configuration.
        return torch.optim.AdamW(
            self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay,
        )
