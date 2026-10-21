# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/image/efficient_ad/torch_model.py
# Adapted imports, local weights, frozen teacher, and calibration guards.


import logging
import math
from enum import Enum

import torch
from torch import nn
from torch.nn import functional as F  # noqa: N812
from torchvision.transforms import v2 as transforms

from src.anomaly_detection.models.common.inference_batch import InferenceBatch

logger = logging.getLogger(__name__)


def imagenet_norm_batch(x: torch.Tensor) -> torch.Tensor:
    mean = torch.tensor([0.485, 0.456, 0.406])[None, :, None, None].to(x.device)
    std = torch.tensor([0.229, 0.224, 0.225])[None, :, None, None].to(x.device)
    return (x - mean) / std


def reduce_tensor_elems(tensor: torch.Tensor, m: int = 2**24) -> torch.Tensor:
    tensor = torch.flatten(tensor)
    if len(tensor) > m:
        # select a random subset with m elements.
        perm = torch.randperm(len(tensor), device=tensor.device)
        idx = perm[:m]
        tensor = tensor[idx]
    return tensor


class EfficientAdModelSize(str, Enum):

    M = "medium"
    S = "small"


class SmallPatchDescriptionNetwork(nn.Module):

    def __init__(self, out_channels: int, padding: bool = False) -> None:
        super().__init__()
        pad_mult = 1 if padding else 0
        self.conv1 = nn.Conv2d(3, 128, kernel_size=4, stride=1, padding=3 * pad_mult)
        self.conv2 = nn.Conv2d(128, 256, kernel_size=4, stride=1, padding=3 * pad_mult)
        self.conv3 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1 * pad_mult)
        self.conv4 = nn.Conv2d(256, out_channels, kernel_size=4, stride=1, padding=0 * pad_mult)
        self.avgpool1 = nn.AvgPool2d(kernel_size=2, stride=2, padding=1 * pad_mult)
        self.avgpool2 = nn.AvgPool2d(kernel_size=2, stride=2, padding=1 * pad_mult)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = imagenet_norm_batch(x)
        x = F.relu(self.conv1(x))
        x = self.avgpool1(x)
        x = F.relu(self.conv2(x))
        x = self.avgpool2(x)
        x = F.relu(self.conv3(x))
        return self.conv4(x)


class MediumPatchDescriptionNetwork(nn.Module):

    def __init__(self, out_channels: int, padding: bool = False) -> None:
        super().__init__()
        pad_mult = 1 if padding else 0
        self.conv1 = nn.Conv2d(3, 256, kernel_size=4, stride=1, padding=3 * pad_mult)
        self.conv2 = nn.Conv2d(256, 512, kernel_size=4, stride=1, padding=3 * pad_mult)
        self.conv3 = nn.Conv2d(512, 512, kernel_size=1, stride=1, padding=0 * pad_mult)
        self.conv4 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1 * pad_mult)
        self.conv5 = nn.Conv2d(512, out_channels, kernel_size=4, stride=1, padding=0 * pad_mult)
        self.conv6 = nn.Conv2d(out_channels, out_channels, kernel_size=1, stride=1, padding=0 * pad_mult)
        self.avgpool1 = nn.AvgPool2d(kernel_size=2, stride=2, padding=1 * pad_mult)
        self.avgpool2 = nn.AvgPool2d(kernel_size=2, stride=2, padding=1 * pad_mult)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = imagenet_norm_batch(x)
        x = F.relu(self.conv1(x))
        x = self.avgpool1(x)
        x = F.relu(self.conv2(x))
        x = self.avgpool2(x)
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))
        return self.conv6(x)


class Encoder(nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.enconv1 = nn.Conv2d(3, 32, kernel_size=4, stride=2, padding=1)
        self.enconv2 = nn.Conv2d(32, 32, kernel_size=4, stride=2, padding=1)
        self.enconv3 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)
        self.enconv4 = nn.Conv2d(64, 64, kernel_size=4, stride=2, padding=1)
        self.enconv5 = nn.Conv2d(64, 64, kernel_size=4, stride=2, padding=1)
        self.enconv6 = nn.Conv2d(64, 64, kernel_size=8, stride=1, padding=0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.enconv1(x))
        x = F.relu(self.enconv2(x))
        x = F.relu(self.enconv3(x))
        x = F.relu(self.enconv4(x))
        x = F.relu(self.enconv5(x))
        return self.enconv6(x)


class Decoder(nn.Module):

    def __init__(self, out_channels: int, padding: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.padding = padding
        # use ceil to match output shape of PDN
        self.deconv1 = nn.Conv2d(64, 64, kernel_size=4, stride=1, padding=2)
        self.deconv2 = nn.Conv2d(64, 64, kernel_size=4, stride=1, padding=2)
        self.deconv3 = nn.Conv2d(64, 64, kernel_size=4, stride=1, padding=2)
        self.deconv4 = nn.Conv2d(64, 64, kernel_size=4, stride=1, padding=2)
        self.deconv5 = nn.Conv2d(64, 64, kernel_size=4, stride=1, padding=2)
        self.deconv6 = nn.Conv2d(64, 64, kernel_size=4, stride=1, padding=2)
        self.deconv7 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        self.deconv8 = nn.Conv2d(64, out_channels, kernel_size=3, stride=1, padding=1)
        self.dropout1 = nn.Dropout(p=0.2)
        self.dropout2 = nn.Dropout(p=0.2)
        self.dropout3 = nn.Dropout(p=0.2)
        self.dropout4 = nn.Dropout(p=0.2)
        self.dropout5 = nn.Dropout(p=0.2)
        self.dropout6 = nn.Dropout(p=0.2)

    def forward(self, x: torch.Tensor, image_size: tuple[int, int] | torch.Size) -> torch.Tensor:
        last_upsample = (
            math.ceil(image_size[0] / 4) if self.padding else math.ceil(image_size[0] / 4) - 8,
            math.ceil(image_size[1] / 4) if self.padding else math.ceil(image_size[1] / 4) - 8,
        )
        x = F.interpolate(x, size=(image_size[0] // 64 - 1, image_size[1] // 64 - 1), mode="bilinear")
        x = F.relu(self.deconv1(x))
        x = self.dropout1(x)
        x = F.interpolate(x, size=(image_size[0] // 32, image_size[1] // 32), mode="bilinear")
        x = F.relu(self.deconv2(x))
        x = self.dropout2(x)
        x = F.interpolate(x, size=(image_size[0] // 16 - 1, image_size[1] // 16 - 1), mode="bilinear")
        x = F.relu(self.deconv3(x))
        x = self.dropout3(x)
        x = F.interpolate(x, size=(image_size[0] // 8, image_size[1] // 8), mode="bilinear")
        x = F.relu(self.deconv4(x))
        x = self.dropout4(x)
        x = F.interpolate(x, size=(image_size[0] // 4 - 1, image_size[1] // 4 - 1), mode="bilinear")
        x = F.relu(self.deconv5(x))
        x = self.dropout5(x)
        x = F.interpolate(x, size=(image_size[0] // 2 - 1, image_size[1] // 2 - 1), mode="bilinear")
        x = F.relu(self.deconv6(x))
        x = self.dropout6(x)
        x = F.interpolate(x, size=last_upsample, mode="bilinear")
        x = F.relu(self.deconv7(x))
        return self.deconv8(x)


class AutoEncoder(nn.Module):

    def __init__(self, out_channels: int, padding: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.encoder = Encoder()
        self.decoder = Decoder(out_channels, padding)

    def forward(self, x: torch.Tensor, image_size: tuple[int, int] | torch.Size) -> torch.Tensor:
        x = imagenet_norm_batch(x)
        x = self.encoder(x)
        return self.decoder(x, image_size)


class EfficientAdModel(nn.Module):

    def __init__(
        self,
        teacher_out_channels: int = 384,
        model_size: EfficientAdModelSize = EfficientAdModelSize.S,
        padding: bool = False,
        pad_maps: bool = True,
    ) -> None:
        super().__init__()

        model_size = EfficientAdModelSize(model_size)
        self.pad_maps = pad_maps
        self.teacher: MediumPatchDescriptionNetwork | SmallPatchDescriptionNetwork
        self.student: MediumPatchDescriptionNetwork | SmallPatchDescriptionNetwork

        if model_size == EfficientAdModelSize.M:
            self.teacher = MediumPatchDescriptionNetwork(out_channels=teacher_out_channels, padding=padding).eval()
            self.student = MediumPatchDescriptionNetwork(out_channels=teacher_out_channels * 2, padding=padding)

        elif model_size == EfficientAdModelSize.S:
            self.teacher = SmallPatchDescriptionNetwork(out_channels=teacher_out_channels, padding=padding).eval()
            self.student = SmallPatchDescriptionNetwork(out_channels=teacher_out_channels * 2, padding=padding)

        else:
            msg = f"Unknown model size {model_size}"
            raise ValueError(msg)

        self.ae: AutoEncoder = AutoEncoder(out_channels=teacher_out_channels, padding=padding)
        self.teacher_out_channels: int = teacher_out_channels

        self.mean_std: nn.ParameterDict = nn.ParameterDict(
            {
                "mean": torch.zeros((1, self.teacher_out_channels, 1, 1)),
                "std": torch.zeros((1, self.teacher_out_channels, 1, 1)),
            },
        )

        self.quantiles: nn.ParameterDict = nn.ParameterDict(
            {
                "qa_st": torch.tensor(0.0),
                "qb_st": torch.tensor(0.0),
                "qa_ae": torch.tensor(0.0),
                "qb_ae": torch.tensor(0.0),
            },
        )

        self.teacher.requires_grad_(False)
        self.mean_std.requires_grad_(False)
        self.quantiles.requires_grad_(False)

    def train(self, mode: bool = True):
        super().train(mode)
        self.teacher.eval()
        return self

    @staticmethod
    def is_set(p_dic: nn.ParameterDict) -> bool:
        return any(value.sum() != 0 for _, value in p_dic.items())

    @staticmethod
    def _is_set_tensor(p_dic: nn.ParameterDict) -> torch.Tensor:
        return torch.stack([value.sum() != 0 for value in p_dic.values()]).any()

    def _normalize_teacher(self, teacher_output: torch.Tensor) -> torch.Tensor:
        is_set = self._is_set_tensor(self.mean_std)
        std = torch.where(is_set, self.mean_std["std"], torch.ones_like(self.mean_std["std"]))
        return torch.where(is_set, (teacher_output - self.mean_std["mean"]) / std, teacher_output)

    @staticmethod
    def choose_random_aug_image(image: torch.Tensor) -> torch.Tensor:
        transform_functions = [
            transforms.functional.adjust_brightness,
            transforms.functional.adjust_contrast,
            transforms.functional.adjust_saturation,
        ]
        # Sample a coefficient from U(0.8, 1.2).
        coefficient = torch.FloatTensor(1).uniform_(0.8, 1.2).item()
        idx = int(torch.randint(0, len(transform_functions), (1,)).item())
        transform_function = transform_functions[idx]
        return transform_function(image, coefficient)

    def forward(
        self,
        batch: torch.Tensor,
        batch_imagenet: torch.Tensor | None = None,
        normalize: bool = True,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor] | InferenceBatch:
        if self.training and batch_imagenet is None:
            raise ValueError("Training requires an ImageNette penalty batch")
        student_output, distance_st = self.compute_student_teacher_distance(batch)
        if self.training:
            return self.compute_losses(batch, batch_imagenet, distance_st)

        map_st, map_stae = self.compute_maps(batch, student_output, distance_st, normalize)
        anomaly_map = 0.5 * map_st + 0.5 * map_stae
        pred_score = torch.amax(anomaly_map, dim=(-2, -1))
        return InferenceBatch(pred_score=pred_score, anomaly_map=anomaly_map)

    def compute_student_teacher_distance(self, batch: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        with torch.no_grad():
            teacher_output = self._normalize_teacher(self.teacher(batch))

        student_output = self.student(batch)
        distance_st = torch.pow(teacher_output - student_output[:, : self.teacher_out_channels, :, :], 2)
        return student_output, distance_st

    def compute_losses(
        self,
        batch: torch.Tensor,
        batch_imagenet: torch.Tensor,
        distance_st: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Student loss
        distance_st = reduce_tensor_elems(distance_st)
        d_hard = torch.quantile(distance_st, 0.999)
        loss_hard = torch.mean(distance_st[distance_st >= d_hard])
        student_output_penalty = self.student(batch_imagenet)[:, : self.teacher_out_channels, :, :]
        loss_penalty = torch.mean(student_output_penalty**2)
        loss_st = loss_hard + loss_penalty

        # Autoencoder and Student AE Loss
        aug_img = self.choose_random_aug_image(batch)
        ae_output_aug = self.ae(aug_img, batch.shape[-2:])

        with torch.no_grad():
            teacher_output_aug = self.teacher(aug_img)
            if self.is_set(self.mean_std):
                teacher_output_aug = (teacher_output_aug - self.mean_std["mean"]) / self.mean_std["std"]

        student_output_ae_aug = self.student(aug_img)[:, self.teacher_out_channels :, :, :]

        distance_ae = torch.pow(teacher_output_aug - ae_output_aug, 2)
        distance_stae = torch.pow(ae_output_aug - student_output_ae_aug, 2)

        loss_ae = torch.mean(distance_ae)
        loss_stae = torch.mean(distance_stae)
        return (loss_st, loss_ae, loss_stae)

    def compute_maps(
        self,
        batch: torch.Tensor,
        student_output: torch.Tensor,
        distance_st: torch.Tensor,
        normalize: bool = True,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        image_size = batch.shape[-2:]
        # Eval mode.
        with torch.no_grad():
            ae_output = self.ae(batch, image_size)

            map_st = torch.mean(distance_st, dim=1, keepdim=True)
            map_stae = torch.mean(
                (ae_output - student_output[:, self.teacher_out_channels :]) ** 2,
                dim=1,
                keepdim=True,
            )

        if self.pad_maps:
            map_st = F.pad(map_st, (4, 4, 4, 4))
            map_stae = F.pad(map_stae, (4, 4, 4, 4))
        map_st = F.interpolate(map_st, size=image_size, mode="bilinear")
        map_stae = F.interpolate(map_stae, size=image_size, mode="bilinear")

        if normalize:
            # Select with a tensor mask instead of branching on parameter values, so dynamo can export it.
            is_set = self._is_set_tensor(self.quantiles)
            q = self.quantiles
            range_st = torch.where(is_set, q["qb_st"] - q["qa_st"], torch.ones_like(q["qa_st"]))
            range_ae = torch.where(is_set, q["qb_ae"] - q["qa_ae"], torch.ones_like(q["qa_ae"]))
            map_st = torch.where(is_set, 0.1 * (map_st - q["qa_st"]) / range_st.clamp_min(1e-12), map_st)
            map_stae = torch.where(is_set, 0.1 * (map_stae - q["qa_ae"]) / range_ae.clamp_min(1e-12), map_stae)
        return map_st, map_stae

    def get_maps(self, batch: torch.Tensor, normalize: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
        student_output, distance_st = self.compute_student_teacher_distance(batch)
        return self.compute_maps(batch, student_output, distance_st, normalize)
