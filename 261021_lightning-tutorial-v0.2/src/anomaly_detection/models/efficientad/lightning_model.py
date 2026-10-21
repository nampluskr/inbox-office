# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/image/efficient_ad/lightning_model.py
# Adapted to native Lightning, tuple batches, local assets, and task metrics.
import math
import os

import lightning.pytorch as pl
import torch
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import v2

from src.anomaly_detection.models.common.metric import AnomalyMetric
from src.anomaly_detection.models.efficientad.model import EfficientAdModel, EfficientAdModelSize, reduce_tensor_elems
from src.utils.config import get_backbone_dir, get_dataset_dir, load_paths_config


class EfficientAdLitModel(pl.LightningModule):
    def __init__(
        self,
        imagenet_dir: str | None = None,
        teacher_out_channels: int = 384,
        model_size: EfficientAdModelSize | str = EfficientAdModelSize.S,
        lr: float = 0.0001,
        weight_decay: float = 0.00001,
        padding: bool = False,
        pad_maps: bool = True,
    ):
        super().__init__()
        model_size = EfficientAdModelSize(model_size).value
        self.save_hyperparameters()
        # A checkpoint includes teacher weights and calibration parameters.
        self.model = EfficientAdModel(
            teacher_out_channels=teacher_out_channels, model_size=model_size,
            padding=padding, pad_maps=pad_maps,
        )
        self.valid_metrics = AnomalyMetric(signed_scores=True)
        self.test_metrics = AnomalyMetric(signed_scores=True)
        self.imagenet_dir = imagenet_dir
        self.model_size = model_size
        self.lr = lr
        self.weight_decay = weight_decay
        self.imagenet_loader = None
        self.imagenet_iterator = None

    def forward(self, images):
        return self.model(images)

    def _check_data(self):
        data = self.trainer.datamodule
        if data is None:
            raise ValueError("EfficientAD requires the task DataModule")
        if data.normalize:
            raise ValueError("EfficientAD requires data.normalize=false; normalization is inside the model")
        if data.image_size != 256:
            raise ValueError("EfficientAD currently requires data.image_size=256")
        return data

    def _check_calibration(self):
        if not self.model.is_set(self.model.mean_std) or not self.model.is_set(self.model.quantiles):
            raise RuntimeError("Load a fitted EfficientAD checkpoint with teacher statistics and map quantiles")

    def on_train_start(self):
        data = self._check_data()
        if self.trainer.world_size != 1:
            raise ValueError("EfficientAD calibration currently supports a single device")
        if data.batch_size != 1 or self.trainer.accumulate_grad_batches != 1:
            raise ValueError("EfficientAD requires batch_size=1 and accumulate_grad_batches=1")
        if self.imagenet_dir is None:
            self.imagenet_dir = get_dataset_dir("imagenette", load_paths_config())
        if not os.path.isdir(self.imagenet_dir):
            raise FileNotFoundError(f"Set model.imagenet_dir to the local ImageNette root directory: {self.imagenet_dir}")
        train_dir = os.path.join(self.imagenet_dir, "train")
        if not os.path.isdir(train_dir):
            raise FileNotFoundError(f"ImageNette train directory not found: {train_dir}")
        if not self.model.is_set(self.model.mean_std):
            weights_path = get_backbone_dir(f"efficientad_{self.model_size}", load_paths_config())
            self.model.teacher.load_state_dict(
                torch.load(weights_path, map_location=self.device, weights_only=True),
            )
            self.teacher_channel_mean_std(data.train_dataloader())
        transform = v2.Compose([
            v2.Resize((512, 512)),
            v2.RandomGrayscale(p=0.3),
            v2.CenterCrop((256, 256)),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
        ])
        dataset = ImageFolder(train_dir, transform=transform)
        self.imagenet_loader = DataLoader(
            dataset, batch_size=1, shuffle=True, num_workers=data.num_workers,
            pin_memory=data.pin_memory,
        )
        self.imagenet_iterator = iter(self.imagenet_loader)

    @torch.no_grad()
    def teacher_channel_mean_std(self, dataloader):
        channel_sum = None
        channel_sum_squared = None
        count = 0
        for images, _ in dataloader:
            features = self.model.teacher(images.to(self.device)).double()
            if channel_sum is None:
                channel_sum = features.sum(dim=(0, 2, 3))
                channel_sum_squared = features.square().sum(dim=(0, 2, 3))
            else:
                channel_sum += features.sum(dim=(0, 2, 3))
                channel_sum_squared += features.square().sum(dim=(0, 2, 3))
            count += features[:, 0].numel()
        if count == 0:
            raise ValueError("Teacher statistics require nonempty normal training data")
        mean = channel_sum / count
        std = (channel_sum_squared / count - mean.square()).clamp_min(1e-12).sqrt()
        self.model.mean_std["mean"].copy_(mean.float()[None, :, None, None])
        self.model.mean_std["std"].copy_(std.float()[None, :, None, None])

    def training_step(self, batch, batch_idx):
        try:
            penalty_images = next(self.imagenet_iterator)[0]
        except StopIteration:
            self.imagenet_iterator = iter(self.imagenet_loader)
            penalty_images = next(self.imagenet_iterator)[0]
        loss_st, loss_ae, loss_stae = self.model(batch[0], penalty_images.to(self.device))
        loss = loss_st + loss_ae + loss_stae
        self.log_dict(
            {"train_st": loss_st, "train_ae": loss_ae, "train_stae": loss_stae},
            on_step=False, on_epoch=True, batch_size=batch[0].shape[0], prog_bar=False,
        )
        self.log(
            "train_loss", loss, on_step=False, on_epoch=True,
            batch_size=batch[0].shape[0], prog_bar=False,
        )
        return {"loss": loss}

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(
            list(self.model.student.parameters()) + list(self.model.ae.parameters()),
            lr=self.lr, weight_decay=self.weight_decay,
        )
        steps = self.trainer.estimated_stepping_batches
        if not math.isfinite(steps) or steps < 1:
            raise ValueError("Set a finite positive Trainer max_steps or max_epochs")
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer, step_size=max(1, int(0.95 * steps)), gamma=0.1,
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {"scheduler": scheduler, "interval": "step", "frequency": 1},
        }

    @torch.no_grad()
    def map_norm_quantiles(self, dataloader):
        maps_st = []
        maps_ae = []
        for images, targets in dataloader:
            for image, label in zip(images, targets["label"], strict=True):
                if label.item() == 0:
                    map_st, map_ae = self.model.get_maps(image.unsqueeze(0).to(self.device), normalize=False)
                    maps_st.append(map_st.cpu())
                    maps_ae.append(map_ae.cpu())
        if not maps_st:
            raise ValueError("EfficientAD calibration requires normal validation samples")
        for suffix, maps in (("st", maps_st), ("ae", maps_ae)):
            values = reduce_tensor_elems(torch.cat(maps))
            qa = torch.quantile(values, 0.9)
            qb = torch.quantile(values, 0.995)
            self.model.quantiles[f"qa_{suffix}"].copy_(qa)
            self.model.quantiles[f"qb_{suffix}"].copy_(torch.maximum(qb, qa + 1e-12))

    def on_validation_start(self):
        self._check_data()
        if self.trainer.state.fn == "fit":
            if self.trainer.sanity_checking:
                raise ValueError("EfficientAD requires trainer.num_sanity_val_steps=0")
            self.map_norm_quantiles(self.trainer.datamodule.val_dataloader())
        else:
            # Standalone validation must preserve the checkpoint's calibration.
            self._check_calibration()

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

    def on_test_start(self):
        self._check_data()
        self._check_calibration()

    def on_test_epoch_start(self):
        self.test_metrics.reset()

    def test_step(self, batch, batch_idx):
        predictions = self(batch[0])
        self.test_metrics.update(predictions, batch[1])
        return predictions

    def on_test_epoch_end(self):
        self.log_dict({f"test_{key}": value for key, value in self.test_metrics.compute().items()})
        self.test_metrics.reset()

    def on_predict_start(self):
        self._check_data()
        self._check_calibration()

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        images = batch[0] if isinstance(batch, (tuple, list)) else batch
        return self(images)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("imagenet_iterator", None)
        return state
