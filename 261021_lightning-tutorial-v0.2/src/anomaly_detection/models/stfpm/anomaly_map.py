# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/image/stfpm/anomaly_map.py
# Adapted imports, local weights, and project style.


import torch
from torch import nn
from torch.nn import functional as F  # noqa: N812


class AnomalyMapGenerator(nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.distance = torch.nn.PairwiseDistance(p=2, keepdim=True)

    @staticmethod
    def compute_layer_map(
        teacher_features: torch.Tensor,
        student_features: torch.Tensor,
        image_size: tuple[int, int] | torch.Size,
    ) -> torch.Tensor:
        norm_teacher_features = F.normalize(teacher_features)
        norm_student_features = F.normalize(student_features)

        layer_map = 0.5 * torch.norm(norm_teacher_features - norm_student_features, p=2, dim=-3, keepdim=True) ** 2
        return F.interpolate(layer_map, size=image_size, align_corners=False, mode="bilinear")

    def compute_anomaly_map(
        self,
        teacher_features: dict[str, torch.Tensor],
        student_features: dict[str, torch.Tensor],
        image_size: tuple[int, int] | torch.Size,
    ) -> torch.Tensor:
        batch_size = next(iter(teacher_features.values())).shape[0]
        anomaly_map = torch.ones(batch_size, 1, image_size[0], image_size[1])
        for layer in teacher_features:
            layer_map = self.compute_layer_map(teacher_features[layer], student_features[layer], image_size)
            anomaly_map = anomaly_map.to(layer_map.device)
            anomaly_map *= layer_map

        return anomaly_map

    def forward(self, **kwargs: dict[str, torch.Tensor]) -> torch.Tensor:
        if not ("teacher_features" in kwargs and "student_features" in kwargs):
            msg = f"Expected keys `teacher_features` and `student_features. Found {kwargs.keys()}"
            raise ValueError(msg)

        teacher_features: dict[str, torch.Tensor] = kwargs["teacher_features"]
        student_features: dict[str, torch.Tensor] = kwargs["student_features"]
        image_size: tuple[int, int] | torch.Size = kwargs["image_size"]

        return self.compute_anomaly_map(teacher_features, student_features, image_size)
