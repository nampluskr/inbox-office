# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/components/feature_extractors/utils.py
# Adapted imports, local weights, and project style.


import torch
from torch.fx.graph_module import GraphModule


def dryrun_find_featuremap_dims(
    feature_extractor: GraphModule,
    input_size: tuple[int, int],
    layers: list[str],
) -> dict[str, dict[str, int | tuple[int, int]]]:
    device = next(feature_extractor.parameters()).device
    dryrun_input = torch.empty(1, 3, *input_size).to(device)
    was_training = feature_extractor.training
    feature_extractor.eval()
    with torch.no_grad():
        dryrun_features = feature_extractor(dryrun_input)
    if was_training:
        feature_extractor.train()
    return {
        layer: {
            "num_features": dryrun_features[layer].shape[1],
            "resolution": dryrun_features[layer].shape[2:],
        }
        for layer in layers
    }
