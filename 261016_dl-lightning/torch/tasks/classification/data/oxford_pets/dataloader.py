from collections.abc import Callable

import torch
from torch.utils.data import DataLoader

from src.torch.tasks.classification.data.oxford_pets.dataset import (
    DATA_ROOT,
    OxfordPetsClassification,
)
from src.torch.tasks.classification.data.oxford_pets.transform import OxfordPetsTransform


class OxforPetsDataloader(DataLoader):
    def __init__(
        self,
        split_path: str,
        root: str = DATA_ROOT,
        split: str = "train",
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
        if transform is None and use_default_transform:
            transform = OxfordPetsTransform(train=(split == "train"), image_size=image_size)

        dataset = OxfordPetsClassification(
            root=root,
            split=split,
            split_path=split_path,
            transform=transform,
            target_transform=target_transform,
        )
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
