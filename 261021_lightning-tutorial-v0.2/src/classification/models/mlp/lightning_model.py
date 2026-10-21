import lightning.pytorch as pl
import torch
from torch import nn

from src.classification.models.common.metric import ClassificationMetric
from src.classification.models.common.postprocess import ClassificationPostprocess
from src.classification.models.mlp.model import MLPModel


class MLPLitModel(pl.LightningModule):
    def __init__(
        self,
        image_size: int = 32,
        in_channels: int = 1,
        hidden_dims: list[int] | None = None,
        num_classes: int = 10,
        learning_rate: float = 0.001,
        weight_decay: float = 0.0001,
    ):
        super().__init__()
        if num_classes < 2:
            raise ValueError("num_classes must be at least 2")
        self.save_hyperparameters()
        self.model = MLPModel(
            image_size=image_size,
            in_channels=in_channels,
            hidden_dims=hidden_dims if hidden_dims is not None else [256, 128],
            num_classes=num_classes,
        )
        self.loss_fn = nn.CrossEntropyLoss()
        self.postprocess = ClassificationPostprocess()
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.metrics = nn.ModuleDict({
            f"{stage}_metrics": ClassificationMetric(num_classes)
            for stage in ("train", "valid", "test")
        })

    def forward(self, images):
        return self.model(images)

    def _shared_step(self, batch, stage):
        images, targets = batch
        logits = self(images)
        if logits.ndim != 2 or logits.shape[1] != self.num_classes:
            raise ValueError("Model must return [batch, num_classes] logits")
        loss = self.loss_fn(logits, targets)
        metrics = self.metrics[f"{stage}_metrics"]
        metrics.update_metrics(logits, targets)
        self.log(
            f"{stage}_loss", loss,
            on_step=False, on_epoch=True,
            batch_size=targets.shape[0], sync_dist=True,
            prog_bar=False,
        )
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
        return torch.optim.AdamW(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )
