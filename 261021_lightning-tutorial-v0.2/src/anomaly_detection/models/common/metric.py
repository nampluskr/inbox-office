import warnings

import torch
from torch import nn
from torchmetrics.classification import BinaryAUROC


class AnomalyMetric(nn.Module):
    def __init__(self, signed_scores: bool = False):
        super().__init__()
        self.signed_scores = signed_scores
        self.image = BinaryAUROC()
        self.pixel = BinaryAUROC()
        self.reset()

    def reset(self):
        self.image.reset()
        self.pixel.reset()
        self.image_classes = set()
        self.pixel_classes = set()

    def update(self, outputs, target):
        scores = outputs.pred_score.detach().flatten()
        maps = outputs.anomaly_map.detach().flatten()
        labels = target["label"].flatten().long()
        masks = target["mask"].flatten().long()
        # A single monotonic mapping prevents batch-dependent automatic sigmoid handling.
        if self.signed_scores:
            # EfficientAD's quantile calibration can produce negative values.
            scores = 0.5 + torch.atan(scores.double()) / torch.pi
            maps = 0.5 + torch.atan(maps.double()) / torch.pi
        else:
            scores = scores / (1 + scores)
            maps = maps / (1 + maps)
        self.image.update(scores, labels)
        self.pixel.update(maps, masks)
        self.image_classes.update(torch.unique(labels).tolist())
        self.pixel_classes.update(torch.unique(masks).tolist())

    def compute(self):
        values = {}
        for name in ("image", "pixel"):
            if getattr(self, f"{name}_classes") == {0, 1}:
                values[f"{name}_auroc"] = getattr(self, name).compute()
            else:
                warnings.warn(f"Skipping {name} AUROC: evaluation requires both classes", stacklevel=2)
        return values
