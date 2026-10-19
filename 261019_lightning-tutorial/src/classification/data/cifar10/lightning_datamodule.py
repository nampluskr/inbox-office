import os

import lightning.pytorch as pl
import torch
from torch.utils.data import DataLoader, random_split

from src.classification.data.cifar10.dataset import CIFAR10Dataset
from src.classification.data.cifar10.transform import CIFAR10Transform


class CIFAR10DataModule(pl.LightningDataModule):
    def __init__(
        self,
        root="E:/datasets/cifar10",
        valid_size=5000,
        seed=42,
        batch_size=16,
        num_workers=0,
        image_size=224,
    ):
        super().__init__()
        self.root = root
        self.valid_size = valid_size
        self.seed = seed
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.image_size = image_size

        self.train_dataset = None
        self.valid_dataset = None
        self.test_dataset = None

    def prepare_data(self):
        data_dir = os.path.join(self.root, "cifar-10-batches-py")
        batch_names = [f"data_batch_{index}" for index in range(1, 6)]
        batch_names.append("test_batch")

        for batch_name in batch_names:
            batch_path = os.path.join(data_dir, batch_name)
            if not os.path.isfile(batch_path):
                raise FileNotFoundError(batch_path)

    def setup(self, stage=None):
        if stage in (None, "fit", "validate"):
            train_source = CIFAR10Dataset(
                root=self.root,
                train=True,
                transform=CIFAR10Transform(train=True, image_size=self.image_size),
            )
            valid_source = CIFAR10Dataset(
                root=self.root,
                train=True,
                transform=CIFAR10Transform(train=False, image_size=self.image_size),
            )

            if not 0 < self.valid_size < len(train_source):
                raise ValueError("valid_size must be between 1 and the training sample count")

            _, self.train_dataset = random_split(
                train_source,
                [self.valid_size, len(train_source) - self.valid_size],
                generator=torch.Generator().manual_seed(self.seed),
            )
            self.valid_dataset, _ = random_split(
                valid_source,
                [self.valid_size, len(valid_source) - self.valid_size],
                generator=torch.Generator().manual_seed(self.seed),
            )

        if stage in (None, "test", "predict"):
            self.test_dataset = CIFAR10Dataset(
                root=self.root,
                train=False,
                transform=CIFAR10Transform(train=False, image_size=self.image_size),
            )

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            generator=torch.Generator().manual_seed(self.seed),
        )

    def val_dataloader(self):
        return DataLoader(
            self.valid_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def predict_dataloader(self):
        return self.test_dataloader()
