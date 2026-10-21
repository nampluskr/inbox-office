# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/image/stfpm/torch_model.py
# Adapted imports, local weights, and project style.


from collections.abc import Sequence

import torch
from torch import nn

from src.anomaly_detection.models.common.inference_batch import InferenceBatch
from src.anomaly_detection.models.common.timm import TimmFeatureExtractor

from src.anomaly_detection.models.stfpm.anomaly_map import AnomalyMapGenerator


class STFPMModel(nn.Module):

    def __init__(
        self,
        layers: Sequence[str],
        backbone: str = "resnet18",
    ) -> None:
        super().__init__()
        self.tiler = None

        self.backbone = backbone
        self.teacher_model = TimmFeatureExtractor(
            backbone=self.backbone, pre_trained=True, layers=layers,
        ).eval()
        self.student_model = TimmFeatureExtractor(
            backbone=self.backbone,
            pre_trained=False,
            layers=layers,
            requires_grad=True,
        )

        # teacher model is fixed
        for parameters in self.teacher_model.parameters():
            parameters.requires_grad = False

        self.anomaly_map_generator = AnomalyMapGenerator()

    def train(self, mode=True):
        super().train(mode)
        self.teacher_model.eval()
        return self

    def forward(
        self,
        images: torch.Tensor,
    ) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]] | InferenceBatch:
        output_size = images.shape[-2:]
        if self.tiler:
            images = self.tiler.tile(images)
        teacher_features: dict[str, torch.Tensor] = self.teacher_model(images)
        student_features: dict[str, torch.Tensor] = self.student_model(images)

        if self.tiler:
            for layer, data in teacher_features.items():
                teacher_features[layer] = self.tiler.untile(data)
            for layer, data in student_features.items():
                student_features[layer] = self.tiler.untile(data)

        if self.training:
            return teacher_features, student_features

        anomaly_map = self.anomaly_map_generator(
            teacher_features=teacher_features,
            student_features=student_features,
            image_size=output_size,
        )
        pred_score = torch.amax(anomaly_map, dim=(-2, -1))
        return InferenceBatch(pred_score=pred_score, anomaly_map=anomaly_map)
