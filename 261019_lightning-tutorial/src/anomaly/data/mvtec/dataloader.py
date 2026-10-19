from collections.abc import Callable

import torch
from torch.utils.data import DataLoader, random_split

from src.anomaly_detection.data.mvtec.dataset import MVTecDataset
from src.anomaly_detection.data.mvtec.transform import MVTecTransform


class MVTecDataloader(DataLoader):
    def __init__(
        self,
        root: str = "E:/datasets/mvtec",
        category: str = "bottle",
        split: str = "train",
        valid_ratio: float = 0.4,
        seed: int = 42,
        batch_size: int = 8,
        num_workers: int = 0,
        pin_memory: bool = True,
        image_size: int = 256,
        transform: Callable | None = None,
        shuffle: bool | None = None,
        drop_last: bool = False,
        collate_fn: Callable | None = None,
    ):
        if split not in ("train", "valid", "test"):
            raise ValueError("split must be one of train/valid/test")
        if not 0 < valid_ratio < 1:
            raise ValueError("valid_ratio must be between 0 and 1")

        if transform is None:
            transform = MVTecTransform(image_size=image_size)

        dataset = MVTecDataset(
            root=root,
            category=category,
            train=(split == "train"),
            transform=transform,
        )

        if split != "train":
            if any(dataset.targets.count(label) < 2 for label in (0, 1)):
                raise ValueError("Each label needs at least two samples for valid/test AUROC")
            valid_size = max(2, min(len(dataset) - 2, int(len(dataset) * valid_ratio)))

            # Retry a deterministic split until both subsets contain both labels.
            for attempt in range(100):
                valid_dataset, test_dataset = random_split(
                    dataset,
                    [valid_size, len(dataset) - valid_size],
                    generator=torch.Generator().manual_seed(seed + attempt),
                )
                valid_labels = {dataset.targets[index] for index in valid_dataset.indices}
                test_labels = {dataset.targets[index] for index in test_dataset.indices}
                if valid_labels == test_labels == {0, 1}:
                    dataset = valid_dataset if split == "valid" else test_dataset
                    break
            else:
                raise ValueError("Could not split both labels into valid and test")

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
