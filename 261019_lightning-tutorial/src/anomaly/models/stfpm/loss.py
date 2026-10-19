# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Adapted from anomalib STFPM loss.py; documentation removed for project style.
import torch
from torch import nn
from torch.nn import functional as functional


class STFPMLoss(nn.Module):
    def compute_layer_loss(self, teacher_feats, student_feats):
        height, width = teacher_feats.shape[2:]
        teacher = functional.normalize(teacher_feats)
        student = functional.normalize(student_feats)
        return (0.5 / (width * height)) * functional.mse_loss(teacher, student, reduction="sum")

    def forward(self, teacher_features, student_features):
        return torch.stack([
            self.compute_layer_loss(teacher_features[layer], student_features[layer])
            for layer in teacher_features
        ]).sum()
