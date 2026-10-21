import os

import lightning.pytorch as pl
import torch
from torch.utils.data import DataLoader, random_split

from src.classification.data.mnist.dataset import MNISTDataset, MNISTTransform


class MNISTLitData(pl.LightningDataModule):
    def __init__(
        self,
        root: str | None = None,
        valid_size: int = 5000,
        seed: int = 42,
        batch_size: int = 64,
        num_workers: int = 0,
        pin_memory: bool = True,
        in_channels: int = 1,
    ):
        super().__init__()
        if root is None:
            raise ValueError("root is required; resolve the dataset path before creating MNISTLitData")
        if in_channels not in (1, 3):
            raise ValueError("MNIST in_channels must be 1 or 3")
        self.root = root
        self.in_channels = in_channels
        self.valid_size = valid_size
        self.seed = seed
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.train_dataset = None
        self.valid_dataset = None
        self.test_dataset = None
        self.save_hyperparameters()

    def prepare_data(self):
        for prefix in ("train", "t10k"):
            for suffix in ("images-idx3-ubyte", "labels-idx1-ubyte"):
                path = os.path.join(self.root, f"{prefix}-{suffix}")
                if not os.path.isfile(path) and not os.path.isfile(path + ".gz"):
                    raise FileNotFoundError(f"MNIST file not found: {path} or {path}.gz")

    def setup(self, stage=None):
        if stage in (None, "fit", "validate") and self.train_dataset is None:
            dataset = MNISTDataset(self.root, "train", MNISTTransform(self.in_channels))
            if not 0 < self.valid_size < len(dataset):
                raise ValueError("valid_size must be between 1 and the train size minus 1")
            self.train_dataset, self.valid_dataset = random_split(
                dataset,
                [len(dataset) - self.valid_size, self.valid_size],
                generator=torch.Generator().manual_seed(self.seed),
            )
        if stage in (None, "test", "predict") and self.test_dataset is None:
            self.test_dataset = MNISTDataset(self.root, "test", MNISTTransform(self.in_channels))

    def _make_loader(self, dataset, shuffle=False):
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            generator=torch.Generator().manual_seed(self.seed),
        )

    def train_dataloader(self):
        return self._make_loader(self.train_dataset, shuffle=True)

    def val_dataloader(self):
        return self._make_loader(self.valid_dataset)

    def test_dataloader(self):
        return self._make_loader(self.test_dataset)

    def predict_dataloader(self):
        return self._make_loader(self.test_dataset)
