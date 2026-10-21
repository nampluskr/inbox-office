from collections.abc import Sequence

import torch
from torch import nn


class MLPModel(nn.Module):
    def __init__(
        self,
        image_size: int = 32,
        in_channels: int = 1,
        hidden_dims: Sequence[int] = (256, 128),
        num_classes: int = 10,
    ):
        super().__init__()
        if image_size < 1 or in_channels < 1 or num_classes < 2:
            raise ValueError("Image dimensions must be positive and num_classes >= 2")
        if not hidden_dims or any(size < 1 for size in hidden_dims):
            raise ValueError("hidden_dims must contain positive layer sizes")
        self.image_size = image_size
        self.in_channels = in_channels
        self.num_classes = num_classes
        dimensions = [in_channels * image_size * image_size, *hidden_dims]
        layers = [nn.Flatten(start_dim=1)]
        for input_size, output_size in zip(dimensions[:-1], dimensions[1:]):
            layers.extend([nn.Linear(input_size, output_size), nn.ReLU()])
        layers.append(nn.Linear(dimensions[-1], num_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        expected_shape = (self.in_channels, self.image_size, self.image_size)
        if images.ndim != 4 or tuple(images.shape[1:]) != expected_shape:
            raise ValueError(f"Expected input shape [batch, {expected_shape}]")
        return self.network(images)
