from collections.abc import Callable

import torch
import torch.nn as nn
import lightning.pytorch as pl
from src.classification.models.cnn.metric import classification_metrics


class ClassificationModule(pl.LightningModule):
    def __init__(
        self,
        model: nn.Module,
        num_classes: int,
        loss_fn: nn.Module | None = None,
        preprocess: Callable | None = None,
        postprocess: Callable | None = None,
        learning_rate: float = 0.001,
        weight_decay: float = 0.0001,
    ):
        super().__init__()
        if num_classes < 2:
            raise ValueError("num_classes must be at least 2")
        self.model = model
        self.num_classes = num_classes
        self.loss_fn = loss_fn if loss_fn is not None else nn.CrossEntropyLoss()
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.metrics = nn.ModuleDict({
            f"{stage}_metrics": classification_metrics(num_classes)
            for stage in ("train", "valid", "test")
        })
        self.save_hyperparameters(ignore=["model", "loss_fn", "preprocess", "postprocess"])

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.model(images)

    def _shared_step(self, batch, stage):
        if not isinstance(batch, (tuple, list)) or len(batch) != 2:
            raise ValueError("Classification steps require an (images, targets) batch")
        images, targets = batch
        if self.preprocess is not None:
            images = self.preprocess(images)
        logits = self(images)
        if not isinstance(logits, torch.Tensor) or logits.ndim != 2 or logits.shape[1] != self.num_classes:
            raise ValueError("Model must return logits with shape [batch, num_classes]")
        loss = self.loss_fn(logits, targets)
        metrics = self.metrics[f"{stage}_metrics"]
        metrics["accuracy"].update(logits.detach(), targets)
        metrics["f1"].update(logits.detach(), targets)
        self.log(
            f"{stage}_loss", loss,
            on_step=(stage == "train"), on_epoch=True,
            batch_size=targets.shape[0], sync_dist=True,
        )
        # Lightning computes and resets logged Metric objects at epoch boundaries.
        self.log(f"{stage}_accuracy", metrics["accuracy"], on_step=False, on_epoch=True)
        self.log(f"{stage}_f1", metrics["f1"], on_step=False, on_epoch=True)
        return loss

    def training_step(self, batch, batch_idx):
        return self._shared_step(batch, "train")

    def validation_step(self, batch, batch_idx):
        return self._shared_step(batch, "valid")

    def test_step(self, batch, batch_idx):
        return self._shared_step(batch, "test")

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        images = batch[0] if isinstance(batch, (tuple, list)) else batch
        if self.preprocess is not None:
            images = self.preprocess(images)
        outputs = self(images)
        return self.postprocess(outputs) if self.postprocess is not None else outputs

    def configure_optimizers(self):
        # LightningCLI can replace this using its native optimizer configuration.
        return torch.optim.AdamW(
            self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay,
        )
