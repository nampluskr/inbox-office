import torch
from lightning.pytorch import LightningDataModule
from torch.utils.data import DataLoader, Dataset, IterableDataset, Subset


class ClassificationData(LightningDataModule):
    def __init__(
        self,
        train_dataset: Dataset | None = None,
        valid_dataset: Dataset | None = None,
        test_dataset: Dataset | None = None,
        predict_dataset: Dataset | None = None,
        valid_size: int | None = None,
        seed: int = 42,
        batch_size: int = 32,
        num_workers: int = 0,
        pin_memory: bool = False,
        train_loader: DataLoader | None = None,
        valid_loader: DataLoader | None = None,
        test_loader: DataLoader | None = None,
        predict_loader: DataLoader | None = None,
    ):
        super().__init__()
        self.train_dataset = train_dataset
        self.valid_dataset = valid_dataset
        self.test_dataset = test_dataset
        self.predict_dataset = predict_dataset
        self.train_loader = train_loader
        self.valid_loader = valid_loader
        self.test_loader = test_loader
        self.predict_loader = predict_loader
        self.valid_size = valid_size
        self.seed = seed
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.split_ready = False

        for stage in ("train", "valid", "test", "predict"):
            if getattr(self, f"{stage}_dataset") is not None and getattr(self, f"{stage}_loader") is not None:
                raise ValueError(f"Provide either {stage}_dataset or {stage}_loader, not both")
        if valid_size is not None:
            if not isinstance(valid_size, int) or isinstance(valid_size, bool) or valid_size < 1:
                raise ValueError("valid_size must be a positive integer or None")
            if train_loader is not None or valid_loader is not None:
                raise ValueError("valid_size cannot be combined with existing train/valid loaders")

    def _setup_split(self):
        if self.split_ready:
            return
        if self.train_dataset is None or self.valid_dataset is None:
            raise ValueError("Splitting requires both train_dataset and valid_dataset")
        if isinstance(self.train_dataset, IterableDataset) or isinstance(self.valid_dataset, IterableDataset):
            raise ValueError("Splitting requires indexable datasets")
        if len(self.train_dataset) != len(self.valid_dataset):
            raise ValueError("Train and valid sources must have the same sample count and ordering")
        if self.valid_size >= len(self.train_dataset):
            raise ValueError("valid_size must be smaller than the training source")
        indices = torch.randperm(
            len(self.train_dataset), generator=torch.Generator().manual_seed(self.seed),
        ).tolist()
        # Separate source instances preserve their respective train/eval transforms.
        self.train_dataset = Subset(self.train_dataset, indices[self.valid_size:])
        self.valid_dataset = Subset(self.valid_dataset, indices[:self.valid_size])
        self.split_ready = True

    def _require_source(self, stage):
        if getattr(self, f"{stage}_dataset") is None and getattr(self, f"{stage}_loader") is None:
            raise ValueError(f"No dataset or loader was provided for {stage}")

    def setup(self, stage: str | None = None):
        if stage not in (None, "fit", "validate", "test", "predict"):
            raise ValueError(f"Unsupported stage: {stage!r}")
        if stage in (None, "fit", "validate") and self.valid_size is not None:
            self._setup_split()
        if stage == "fit":
            self._require_source("train")
        elif stage == "validate":
            self._require_source("valid")
        elif stage == "test":
            self._require_source("test")
        elif stage == "predict":
            if self.predict_dataset is None and self.predict_loader is None:
                self._require_source("test")

    def _get_loader(self, stage, required=True):
        loader = getattr(self, f"{stage}_loader")
        if loader is not None:
            return loader
        dataset = getattr(self, f"{stage}_dataset")
        if dataset is None:
            if required:
                self._require_source(stage)
            return []
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=(stage == "train" and not isinstance(dataset, IterableDataset)),
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            generator=torch.Generator().manual_seed(self.seed),
        )

    def train_dataloader(self):
        return self._get_loader("train")

    def val_dataloader(self):
        return self._get_loader("valid", required=False)

    def test_dataloader(self):
        return self._get_loader("test")

    def predict_dataloader(self):
        stage = "test" if self.predict_dataset is None and self.predict_loader is None else "predict"
        return self._get_loader(stage)
