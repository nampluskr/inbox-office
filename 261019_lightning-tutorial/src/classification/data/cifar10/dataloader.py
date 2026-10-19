from collections.abc import Callable

import torch
from torch.utils.data import DataLoader, random_split

from src.classification.data.cifar10.dataset import DATA_ROOT, CIFAR10Dataset
from src.classification.data.cifar10.transform import CIFAR10Transform


class CIFAR10Dataloader(DataLoader):
    def __init__(
        self,
        root: str = DATA_ROOT,
        split: str = "train",
        valid_size: int = 5000,
        seed: int = 42,
        batch_size: int = 16,
        num_workers: int = 0,
        pin_memory: bool = True,
        image_size: int = 224,
        transform: Callable | None = None,
        target_transform: Callable | None = None,
        shuffle: bool | None = None,
        drop_last: bool = False,
        collate_fn: Callable | None = None,
    ):
        if split not in ("train", "valid", "test"):
            raise ValueError("split must be one of train/valid/test")
        if not isinstance(valid_size, int) or isinstance(valid_size, bool) or valid_size < 1:
            raise ValueError("valid_size must be a positive integer")

        if transform is None:
            transform = CIFAR10Transform(train=(split == "train"), image_size=image_size)

        dataset = CIFAR10Dataset(
            root=root,
            train=(split != "test"),
            transform=transform,
            target_transform=target_transform,
        )
        if split != "test":
            if valid_size >= len(dataset):
                raise ValueError("valid_size must be smaller than the training sample count")
            # Keep the split independent of the DataLoader's shuffle state.
            split_generator = torch.Generator().manual_seed(seed)
            valid_dataset, train_dataset = random_split(
                dataset,
                [valid_size, len(dataset) - valid_size],
                generator=split_generator,
            )
            dataset = train_dataset if split == "train" else valid_dataset

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
