import os
import pickle
from collections.abc import Callable

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms import v2


CLASS_NAMES = (
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class CIFAR10Transform(v2.Compose):
    def __init__(self, train=False, image_size=32):
        if image_size < 1:
            raise ValueError("image_size must be positive")
        operations = []
        if train:
            operations.extend([v2.RandomCrop(32, padding=4), v2.RandomHorizontalFlip()])
        operations.extend([
            v2.Resize((image_size, image_size), antialias=True),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])
        super().__init__(operations)


class CIFAR10Dataset(Dataset):
    def __init__(
        self, root: str, train=True,
        transform: Callable | None = None, target_transform: Callable | None = None,
    ):
        self.root = root
        self.train = train
        self.transform = transform
        self.target_transform = target_transform
        self.classes = list(CLASS_NAMES)
        self.class_to_idx = {name: index for index, name in enumerate(self.classes)}

        batch_names = [f"data_batch_{index}" for index in range(1, 6)] if train else ["test_batch"]
        images = []
        self.targets = []
        for batch_name in batch_names:
            batch_path = os.path.join(root, "cifar-10-batches-py", batch_name)
            # Original CIFAR-10 Python batches contain Python 2 pickle objects.
            with open(batch_path, "rb") as file:
                batch = pickle.load(file, encoding="latin1")
            data = np.asarray(batch["data"])
            targets = np.asarray(batch["labels"])
            if data.ndim != 2 or data.shape[1] != 3072 or data.dtype != np.uint8:
                raise ValueError(f"Invalid CIFAR-10 image data in '{batch_path}'")
            if (
                targets.shape != (len(data),)
                or not np.issubdtype(targets.dtype, np.integer)
                or np.any((targets < 0) | (targets >= len(self.classes)))
            ):
                raise ValueError(f"Invalid CIFAR-10 labels in '{batch_path}'")
            images.append(data)
            self.targets.extend(targets.tolist())

        # Batch rows store all red pixels, then green pixels, then blue pixels.
        self.data = np.concatenate(images, axis=0).reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, index):
        image = Image.fromarray(self.data[index])
        target = torch.tensor(self.targets[index], dtype=torch.long)
        if self.transform is not None:
            image = self.transform(image)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return image, target
