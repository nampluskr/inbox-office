# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Adapted from anomalib STFPM lightning_model.py.
# Changed: native Lightning, injected model/loss, tuple batches and independent metrics.
import torch
import lightning.pytorch as pl
from torch import nn

from src.anomaly_detection.models.stfpm.metric import AnomalyMetrics


class STFPMModule(pl.LightningModule):
    def __init__(
        self, model: nn.Module, loss_fn: nn.Module,
        learning_rate: float = 0.4, momentum: float = 0.9, weight_decay: float = 0.001,
    ):
        super().__init__()
        self.model = model
        self.loss_fn = loss_fn
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.valid_metrics = AnomalyMetrics()
        self.test_metrics = AnomalyMetrics()
        self.save_hyperparameters(ignore=["model", "loss_fn"])

    def forward(self, images):
        return self.model(images)

    def training_step(self, batch, batch_idx):
        teacher_features, student_features = self(batch[0])
        loss = self.loss_fn(teacher_features, student_features)
        self.log("train_loss", loss, on_step=False, on_epoch=True, batch_size=batch[0].shape[0])
        return loss

    def on_validation_epoch_start(self):
        self.valid_metrics.reset()

    def validation_step(self, batch, batch_idx):
        self.valid_metrics.update(self(batch[0]), batch[1])

    def on_validation_epoch_end(self):
        self.log_dict({f"valid_{key}": value for key, value in self.valid_metrics.compute().items()})
        self.valid_metrics.reset()

    def on_test_epoch_start(self):
        self.test_metrics.reset()

    def test_step(self, batch, batch_idx):
        self.test_metrics.update(self(batch[0]), batch[1])

    def on_test_epoch_end(self):
        self.log_dict({f"test_{key}": value for key, value in self.test_metrics.compute().items()})
        self.test_metrics.reset()

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        return self(batch[0])

    def configure_optimizers(self):
        return torch.optim.SGD(
            (parameter for parameter in self.model.parameters() if parameter.requires_grad),
            lr=self.learning_rate, momentum=self.momentum, dampening=0.0, weight_decay=self.weight_decay,
        )
