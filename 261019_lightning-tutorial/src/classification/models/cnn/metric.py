from torch import nn
from torchmetrics.classification import MulticlassAccuracy, MulticlassF1Score


def classification_metrics(num_classes):
    return nn.ModuleDict({
        "accuracy": MulticlassAccuracy(num_classes=num_classes, average="micro"),
        "f1": MulticlassF1Score(num_classes=num_classes, average="macro"),
    })
