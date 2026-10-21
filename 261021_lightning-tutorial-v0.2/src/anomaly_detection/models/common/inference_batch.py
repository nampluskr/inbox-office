# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, data/dataclasses/torch/base.py
from typing import NamedTuple

import torch


class InferenceBatch(NamedTuple):
    pred_score: torch.Tensor | None = None
    pred_label: torch.Tensor | None = None
    anomaly_map: torch.Tensor | None = None
    pred_mask: torch.Tensor | None = None
