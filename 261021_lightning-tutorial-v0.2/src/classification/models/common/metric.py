from torch import nn
from torchmetrics.classification import MulticlassAccuracy, MulticlassF1Score


class ClassificationMetric(nn.ModuleDict):
    def __init__(self, num_classes: int):
        super().__init__({
            "acc": MulticlassAccuracy(num_classes=num_classes, average="micro"),
            "f1": MulticlassF1Score(num_classes=num_classes, average="macro"),
        })

    def update_metrics(self, logits, targets):
        for metric in self.values():
            metric.update(logits.detach(), targets)
