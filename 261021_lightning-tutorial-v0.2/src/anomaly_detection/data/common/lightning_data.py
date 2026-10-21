import os

import lightning.pytorch as pl
import torch
from torch.utils.data import DataLoader, random_split

from src.anomaly_detection.data.common.dataset import AnomalyTransform


class AnomalyLitData(pl.LightningDataModule):
    dataset_class = None

    def __init__(
        self,
        root: str | None = None,
        category: str = "bottle",
        valid_ratio: float = 0.4,
        seed: int = 42,
        batch_size: int = 8,
        num_workers: int = 0,
        pin_memory: bool = True,
        image_size: int = 256,
        normalize: bool = True,
    ):
        super().__init__()
        if root is None:
            raise ValueError("root is required; resolve the dataset path before creating the DataModule")
        if not 0 < valid_ratio < 1:
            raise ValueError("valid_ratio must be between 0 and 1")
        self.save_hyperparameters()
        self.root = root
        self.category = category
        self.valid_ratio = valid_ratio
        self.seed = seed
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.image_size = image_size
        self.normalize = normalize
        self.train_dataset = None
        self.valid_dataset = None
        self.test_dataset = None

    def prepare_data(self):
        category_dir = os.path.join(self.root, self.category)
        for directory in (os.path.join(category_dir, "train", self.dataset_class.normal_name),
                          os.path.join(category_dir, "test")):
            if not os.path.isdir(directory):
                raise FileNotFoundError(directory)

    def setup(self, stage=None):
        if stage in (None, "fit") and self.train_dataset is None:
            self.train_dataset = self.dataset_class(
                self.root, train=True, category=self.category,
                transform=AnomalyTransform(self.image_size, normalize=self.normalize),
            )
        if stage in (None, "fit", "validate", "test", "predict") and self.valid_dataset is None:
            dataset = self.dataset_class(
                self.root, train=False, category=self.category,
                transform=AnomalyTransform(self.image_size, normalize=self.normalize),
            )
            if any(dataset.targets.count(label) < 2 for label in (0, 1)):
                raise ValueError("Each label needs at least two samples for valid/test AUROC")
            valid_size = max(2, min(len(dataset) - 2, int(len(dataset) * self.valid_ratio)))
            for attempt in range(100):
                valid_dataset, test_dataset = random_split(
                    dataset, [valid_size, len(dataset) - valid_size],
                    generator=torch.Generator().manual_seed(self.seed + attempt),
                )
                valid_labels = {dataset.targets[index] for index in valid_dataset.indices}
                test_labels = {dataset.targets[index] for index in test_dataset.indices}
                if valid_labels == test_labels == {0, 1}:
                    self.valid_dataset = valid_dataset
                    self.test_dataset = test_dataset
                    break
            else:
                raise ValueError("Could not split both labels into valid and test")

    def _make_loader(self, dataset, shuffle=False):
        return DataLoader(
            dataset, batch_size=self.batch_size, shuffle=shuffle,
            num_workers=self.num_workers, pin_memory=self.pin_memory,
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
