import os

import lightning.pytorch as pl

from src.anomaly_detection.data.mvtec.dataloader import MVTecDataloader


class MVTecDataModule(pl.LightningDataModule):
    def __init__(
        self,
        root: str = "E:/datasets/mvtec",
        category: str = "bottle",
        valid_ratio: float = 0.4,
        seed: int = 42,
        batch_size: int = 8,
        num_workers: int = 0,
        pin_memory: bool = True,
        image_size: int = 256,
    ):
        super().__init__()
        self.root = root
        self.category = category
        self.valid_ratio = valid_ratio
        self.seed = seed
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.image_size = image_size

        self.train_loader = None
        self.valid_loader = None
        self.test_loader = None

    def prepare_data(self):
        category_dir = os.path.join(self.root, self.category)
        for split_dir in (os.path.join(category_dir, "train", "good"),
                          os.path.join(category_dir, "test")):
            if not os.path.isdir(split_dir):
                raise FileNotFoundError(split_dir)

    def setup(self, stage=None):
        loader_args = {
            "root": self.root,
            "category": self.category,
            "valid_ratio": self.valid_ratio,
            "seed": self.seed,
            "batch_size": self.batch_size,
            "num_workers": self.num_workers,
            "pin_memory": self.pin_memory,
            "image_size": self.image_size,
        }

        if stage in (None, "fit"):
            self.train_loader = MVTecDataloader(split="train", **loader_args)
        if stage in (None, "fit", "validate"):
            self.valid_loader = MVTecDataloader(split="valid", **loader_args)
        if stage in (None, "test", "predict"):
            self.test_loader = MVTecDataloader(split="test", **loader_args)

    def train_dataloader(self):
        return self.train_loader

    def val_dataloader(self):
        return self.valid_loader

    def test_dataloader(self):
        return self.test_loader

    def predict_dataloader(self):
        return self.test_loader
