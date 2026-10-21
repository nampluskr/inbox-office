# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/image/stfpm/lightning_model.py
# Adapted to native Lightning, tuple batches, local weights, and task metrics.
from collections.abc import Sequence

import lightning.pytorch as pl
import torch

from src.anomaly_detection.models.common.metric import AnomalyMetric
from src.anomaly_detection.models.common.tiler import Tiler
from src.anomaly_detection.models.stfpm.loss import STFPMLoss
from src.anomaly_detection.models.stfpm.model import STFPMModel


class STFPMLitModel(pl.LightningModule):
    def __init__(
        self,
        backbone: str = "resnet18",
        layers: Sequence[str] = ("layer1", "layer2", "layer3"),
    ):
        super().__init__()
        self.save_hyperparameters()
        self.model = STFPMModel(layers=layers, backbone=backbone)
        self.loss = STFPMLoss()
        self.valid_metrics = AnomalyMetric()
        self.test_metrics = AnomalyMetric()

    def forward(self, images):
        return self.model(images)

    def on_save_checkpoint(self, checkpoint):
        tiler = self.model.tiler
        if tiler is not None:
            checkpoint["tiler"] = {
                "tile_size": (tiler.tile_size_h, tiler.tile_size_w),
                "stride": (tiler.stride_h, tiler.stride_w),
                "remove_border_count": tiler.remove_border_count,
                "mode": tiler.mode.value if hasattr(tiler.mode, "value") else tiler.mode,
            }

    def on_load_checkpoint(self, checkpoint):
        if checkpoint.get("tiler") is not None:
            self.model.tiler = Tiler(**checkpoint["tiler"])

    def training_step(self, batch, batch_idx):
        teacher_features, student_features = self(batch[0])
        loss = self.loss(teacher_features, student_features)
        self.log(
            "train_loss", loss, on_step=False, on_epoch=True,
            batch_size=batch[0].shape[0], sync_dist=True, prog_bar=True,
        )
        return {"loss": loss}

    def on_validation_epoch_start(self):
        self.valid_metrics.reset()

    def validation_step(self, batch, batch_idx):
        predictions = self(batch[0])
        self.valid_metrics.update(predictions, batch[1])
        return predictions

    def on_validation_epoch_end(self):
        self.log_dict(
            {f"valid_{key}": value for key, value in self.valid_metrics.compute().items()},
            prog_bar=False,
        )
        self.valid_metrics.reset()

    def on_test_epoch_start(self):
        self.test_metrics.reset()

    def test_step(self, batch, batch_idx):
        predictions = self(batch[0])
        self.test_metrics.update(predictions, batch[1])
        return predictions

    def on_test_epoch_end(self):
        self.log_dict({f"test_{key}": value for key, value in self.test_metrics.compute().items()})
        self.test_metrics.reset()

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        images = batch[0] if isinstance(batch, (tuple, list)) else batch
        return self(images)

    def configure_optimizers(self):
        return torch.optim.SGD(
            self.model.student_model.parameters(), lr=0.4,
            momentum=0.9, dampening=0.0, weight_decay=0.001,
        )
