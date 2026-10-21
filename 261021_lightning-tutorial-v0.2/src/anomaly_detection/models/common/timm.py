# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Source: anomalib baf5e5fe12bc73cd520523046ba1d68279462e69, models/components/feature_extractors/timm.py
# Adapted imports, local weights, and project style.


import functools
import logging
from collections.abc import Sequence
from typing import cast

import timm
import torch
from torch import nn
from torchvision.models.feature_extraction import create_feature_extractor

from src.anomaly_detection.models.common.utils import dryrun_find_featuremap_dims
from src.utils.config import get_backbone_dir, load_paths_config

logger = logging.getLogger(__name__)


def _disable_pos_embed_antialiasing() -> None:
    try:
        import timm.models.vision_transformer as vit
    except ImportError:
        return

    original = getattr(vit, "resample_abs_pos_embed", None)
    if original is None or getattr(original, "_anomalib_no_antialias", False):
        return

    @functools.wraps(original)
    def _no_antialias(*args, **kwargs):  # noqa: ANN202
        kwargs["antialias"] = False
        return original(*args, **kwargs)

    setattr(_no_antialias, "_anomalib_no_antialias", True)  # noqa: B010
    vit.resample_abs_pos_embed = _no_antialias


class TimmFeatureExtractor(nn.Module):

    def __init__(
        self,
        backbone: str | nn.Module,
        layers: Sequence[str | int],
        pre_trained: bool = True,
        requires_grad: bool = False,
        output_fmt: str = "NCHW",
        return_class_token: bool = False,
        norm: bool = True,
        dynamic_img_size: bool = True,
    ) -> None:
        super().__init__()

        pretrained_cfg_overlay = None
        if isinstance(backbone, str):
            if ":" in backbone:
                raise ValueError("Use a registered timm backbone name, not a remote model reference")
            if pre_trained:
                weights_path = get_backbone_dir(backbone, load_paths_config())
                # timm retains its model-specific filtering while loading only this file.
                pretrained_cfg_overlay = {
                    "file": weights_path, "source": "", "url": "", "hf_hub_id": None,
                }

        if output_fmt not in {"NCHW", "NLC"}:
            msg = f"output_fmt must be one of 'NCHW' or 'NLC', got '{output_fmt}'."
            raise ValueError(msg)

        self.backbone = backbone
        self.layers: list[str | int] = list(layers)
        self.requires_grad = requires_grad
        self.output_fmt = output_fmt
        self.return_class_token = return_class_token
        self.norm = norm
        self.out_dims: Sequence[int]

        # ViT backbones are extracted via ``forward_intermediates`` (the ``features_only`` API cannot
        # handle dynamic ViT input sizes).
        self._uses_intermediates = isinstance(backbone, str) and (output_fmt == "NLC" or "vit" in backbone.lower())

        if isinstance(backbone, nn.Module):
            # ``nn.Module`` backbones require string node names.
            layer_names = cast("list[str]", self.layers)
            self.feature_extractor = create_feature_extractor(
                backbone,
                return_nodes={layer: layer for layer in layer_names},
            )
            layer_metadata = dryrun_find_featuremap_dims(self.feature_extractor, (256, 256), layers=layer_names)
            self.out_dims = [cast("int", feature_info["num_features"]) for feature_info in layer_metadata.values()]

        elif self._uses_intermediates:
            # Transformer mode: use the full model with forward_intermediates (e.g. ViT/DINOv2).
            self.idx = [self._block_name_to_idx(layer) for layer in self.layers]
            self.feature_extractor = timm.create_model(
                backbone,
                pretrained=pre_trained,
                pretrained_cfg=None,
                pretrained_cfg_overlay=pretrained_cfg_overlay,
                dynamic_img_size=dynamic_img_size,
            )
            _disable_pos_embed_antialiasing()
            self.patch_size = self.feature_extractor.patch_embed.patch_size[0]
            self.num_prefix_tokens = getattr(self.feature_extractor, "num_prefix_tokens", 1)
            self.num_register_tokens = self.num_prefix_tokens - 1
            embed_dim = self.feature_extractor.num_features
            self.out_dims = [embed_dim] * len(self.layers)

        elif isinstance(backbone, str):
            if all(isinstance(layer, int) for layer in self.layers):
                self.idx = [layer for layer in self.layers if isinstance(layer, int)]
            else:
                self.idx = self._map_layer_to_idx()
            self.feature_extractor = timm.create_model(
                backbone,
                pretrained=pre_trained,
                pretrained_cfg=None,
                pretrained_cfg_overlay=pretrained_cfg_overlay,
                features_only=True,
                exportable=True,
                out_indices=self.idx,
            )
            self.out_dims = self.feature_extractor.feature_info.channels()
            self.reductions = self.feature_extractor.feature_info.reduction()

        else:
            msg = f"Backbone of type {type(backbone)} must be of type str or nn.Module."
            raise TypeError(msg)

        self._features = {layer: torch.empty(0) for layer in self.layers}

    @staticmethod
    def _block_name_to_idx(layer: str | int) -> int:
        if isinstance(layer, int):
            return layer
        try:
            return int(layer.rsplit(".", 1)[-1])
        except ValueError as exc:
            msg = f"In 'NLC' mode, layer names must be of the form 'blocks.<int>', got '{layer}'."
            raise ValueError(msg) from exc

    def _map_layer_to_idx(self) -> list[int]:
        idx = []
        model = timm.create_model(
            self.backbone,
            pretrained=False,
            features_only=True,
            exportable=True,
        )
        # model.feature_info.info returns list of dicts containing info,
        # inside which "module" contains layer name
        layer_names = [info["module"] for info in model.feature_info.info]
        for layer in self.layers:
            try:
                idx.append(layer_names.index(layer))
            except ValueError:  # noqa: PERF203
                msg = f"Layer {layer} not found in model {self.backbone}. Available layers: {layer_names}"
                logger.warning(msg)
                # Remove unfound key from layer dict
                self.layers.remove(layer)

        return idx

    def forward(self, inputs: torch.Tensor) -> dict[str | int, torch.Tensor]:
        if self._uses_intermediates:
            return self._forward_nlc(inputs)

        if self.requires_grad:
            features = self.feature_extractor(inputs)
        else:
            self.feature_extractor.eval()
            with torch.no_grad():
                features = self.feature_extractor(inputs)
        if not isinstance(features, dict):
            features = dict(zip(self.layers, features, strict=True))
        return features

    def _forward_nlc(self, inputs: torch.Tensor) -> dict[str | int, torch.Tensor]:
        if self.requires_grad:
            intermediates = self._run_intermediates(inputs)
        else:
            self.feature_extractor.eval()
            with torch.no_grad():
                intermediates = self._run_intermediates(inputs)

        features = {}
        for layer, out in zip(self.layers, intermediates, strict=True):
            if self.return_class_token:
                patch_tokens, prefix_tokens = out
                features[layer] = torch.cat([prefix_tokens, patch_tokens], dim=1)
            else:
                features[layer] = out
        return features

    def _run_intermediates(self, inputs: torch.Tensor) -> list:
        return self.feature_extractor.forward_intermediates(
            inputs,
            indices=self.idx,
            norm=self.norm,
            return_prefix_tokens=self.return_class_token,
            output_fmt=self.output_fmt,
            intermediates_only=True,
        )
