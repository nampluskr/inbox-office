import gzip
import os
import struct
from collections.abc import Callable

import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2


class MNISTTransform(v2.Compose):
    def __init__(self, in_channels: int = 1):
        if in_channels not in (1, 3):
            raise ValueError("MNIST in_channels must be 1 or 3")
        operations = [v2.ToImage()]
        if in_channels == 3:
            operations.append(v2.Grayscale(num_output_channels=3))
        operations.extend([
            v2.Pad(2, fill=0),
            v2.ToDtype(torch.float32, scale=True),
        ])
        super().__init__(operations)

    def forward(self, image):
        # torchvision 0.17 ToImage expects NumPy images in HWC format.
        if isinstance(image, np.ndarray) and image.ndim == 2:
            image = image[..., np.newaxis]
        return super().forward(image)


class MNISTDataset(Dataset):
    def __init__(
        self,
        root: str,
        split: str = "train",
        transform: Callable | None = None,
    ):
        if split not in ("train", "test"):
            raise ValueError("split must be 'train' or 'test'; valid uses a train subset")
        prefix = "train" if split == "train" else "t10k"
        self.transform = transform
        image_bytes = self._read_file(root, f"{prefix}-images-idx3-ubyte")
        label_bytes = self._read_file(root, f"{prefix}-labels-idx1-ubyte")
        if len(image_bytes) < 16 or len(label_bytes) < 8:
            raise ValueError("MNIST IDX headers are incomplete")
        magic, count, height, width = struct.unpack(">IIII", image_bytes[:16])
        label_magic, label_count = struct.unpack(">II", label_bytes[:8])
        if magic != 2051 or label_magic != 2049:
            raise ValueError("Invalid MNIST IDX magic numbers")
        if (height, width) != (28, 28) or count != label_count:
            raise ValueError("Expected matching MNIST labels and 28x28 images")
        if len(image_bytes) != 16 + count * height * width:
            raise ValueError("MNIST image payload size does not match its header")
        if len(label_bytes) != 8 + count:
            raise ValueError("MNIST label payload size does not match its header")
        self.images = np.frombuffer(image_bytes, dtype=np.uint8, offset=16)
        self.images = self.images.reshape(count, height, width).copy()
        self.targets = np.frombuffer(label_bytes, dtype=np.uint8, offset=8).copy()
        if np.any(self.targets > 9):
            raise ValueError("MNIST labels must be between 0 and 9")

    @staticmethod
    def _read_file(root, filename):
        path = os.path.join(root, filename)
        if os.path.isfile(path):
            with open(path, "rb") as file:
                return file.read()
        if os.path.isfile(path + ".gz"):
            with gzip.open(path + ".gz", "rb") as file:
                return file.read()
        raise FileNotFoundError(f"MNIST file not found: {path} or {path}.gz")

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, index):
        image = self.images[index]
        if self.transform is not None:
            image = self.transform(image)
        return image, int(self.targets[index])
