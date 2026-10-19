# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Adapted from anomalib STFPM torch_model.py and anomaly_map.py.
# Changed: local torchvision features, dict outputs, no tiling or anomalib runtime.
import torch
from torch import nn
from torch.nn import functional as functional
from torchvision.models import resnet18
from torchvision.models.feature_extraction import create_feature_extractor


class AnomalyMapGenerator(nn.Module):
    @staticmethod
    def compute_layer_map(teacher_features, student_features, image_size):
        teacher = functional.normalize(teacher_features)
        student = functional.normalize(student_features)
        layer_map = 0.5 * torch.norm(teacher - student, p=2, dim=-3, keepdim=True) ** 2
        return functional.interpolate(layer_map, size=image_size, align_corners=False, mode="bilinear")

    def forward(self, teacher_features, student_features, image_size):
        first = next(iter(teacher_features.values()))
        anomaly_map = first.new_ones((first.shape[0], 1, *image_size))
        for layer in teacher_features:
            anomaly_map = anomaly_map * self.compute_layer_map(
                teacher_features[layer], student_features[layer], image_size,
            )
        return anomaly_map


class STFPMModel(nn.Module):
    def __init__(
        self, weights_path: str | None = None,
        layers: tuple[str, ...] = ("layer1", "layer2", "layer3"),
    ):
        super().__init__()
        if not layers or len(set(layers)) != len(layers) or any(layer not in ("layer1", "layer2", "layer3") for layer in layers):
            raise ValueError("layers must be unique ResNet18 layer1/layer2/layer3 names")
        teacher = resnet18(weights=None)
        if weights_path is not None:
            teacher.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True), strict=True)
        self.teacher_model = create_feature_extractor(teacher, return_nodes=list(layers)).eval()
        self.student_model = create_feature_extractor(resnet18(weights=None), return_nodes=list(layers))
        self.teacher_model.requires_grad_(False)
        self.anomaly_map_generator = AnomalyMapGenerator()

    def train(self, mode=True):
        super().train(mode)
        self.teacher_model.eval()
        return self

    def forward(self, images):
        with torch.no_grad():
            teacher_features = self.teacher_model(images)
        student_features = self.student_model(images)
        if self.training:
            return teacher_features, student_features
        anomaly_map = self.anomaly_map_generator(teacher_features, student_features, images.shape[-2:])
        return {"pred_score": anomaly_map.amax(dim=(-2, -1)), "anomaly_map": anomaly_map}
