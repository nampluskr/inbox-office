from collections.abc import Callable

import torch
from torch.utils.data import DataLoader, Subset

from src.torch.tasks.classification.data.cifar10.dataset import DATA_ROOT, CIFAR10Dataset
from src.torch.tasks.classification.data.cifar10.transform import CIFAR10Transform


class CIFAR10Dataloader(DataLoader):
    def __init__(
        self,
        root: str = DATA_ROOT,
        split: str = "train",
        valid_size: int | None = 5000,
        seed: int = 42,
        batch_size: int = 32,
        num_workers: int = 0,
        pin_memory: bool = True,
        image_size: int = 224,
        transform: Callable | None = None,
        target_transform: Callable | None = None,
        use_default_transform: bool = True,
        shuffle: bool | None = None,
        drop_last: bool = False,
        collate_fn: Callable | None = None,
    ):
        if split not in ("train", "valid", "test"):
            raise ValueError("split must be one of train/valid/test")
        if valid_size is not None and (
            not isinstance(valid_size, int) or isinstance(valid_size, bool) or valid_size < 1
        ):
            raise ValueError("valid_size must be a positive integer or None")
        if split == "valid" and valid_size is None:
            raise ValueError("The valid split requires valid_size")
        if transform is None and use_default_transform:
            transform = CIFAR10Transform(train=(split == "train"), image_size=image_size)

        dataset = CIFAR10Dataset(
            root=root,
            train=(split != "test"),
            transform=transform,
            target_transform=target_transform,
        )
        if split != "test" and valid_size is not None:
            if valid_size >= len(dataset):
                raise ValueError("valid_size must be smaller than the training source")
            # Use an independent generator so loader iteration cannot change the split.
            indices = torch.randperm(
                len(dataset), generator=torch.Generator().manual_seed(seed),
            ).tolist()
            indices = indices[valid_size:] if split == "train" else indices[:valid_size]
            dataset = Subset(dataset, indices)

        super().__init__(
            dataset,
            batch_size=batch_size,
            shuffle=(split == "train") if shuffle is None else shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=drop_last,
            collate_fn=collate_fn,
            generator=torch.Generator().manual_seed(seed),
        )
