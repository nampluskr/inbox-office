import torch
from torch import nn


class ClassificationPostprocess(nn.Module):
    def forward(self, logits: torch.Tensor) -> dict[str, torch.Tensor]:
        return {
            "probabilities": logits.softmax(dim=-1),
            "predictions": logits.argmax(dim=-1),
        }
