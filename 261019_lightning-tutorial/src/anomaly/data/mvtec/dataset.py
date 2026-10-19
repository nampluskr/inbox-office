import os
from collections.abc import Callable

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


class MVTecDataset(Dataset):
    def __init__(
        self, root: str, train: bool = True,
        category: str = "bottle", transform: Callable | None = None,
    ):
        self.category_dir = os.path.join(root, category)
        self.transform = transform
        self.train = train
        split_dir = os.path.join(self.category_dir, "train" if train else "test")
        if not os.path.isdir(split_dir):
            raise FileNotFoundError(split_dir)
        defect_names = ["good"] if train else sorted(
            name for name in os.listdir(split_dir)
            if os.path.isdir(os.path.join(split_dir, name))
        )
        self.ids = []
        self.targets = []
        for defect in defect_names:
            defect_dir = os.path.join(split_dir, defect)
            if not os.path.isdir(defect_dir):
                raise FileNotFoundError(defect_dir)
            for filename in sorted(os.listdir(defect_dir)):
                if not filename.lower().endswith(".png"):
                    continue
                if not os.path.isfile(os.path.join(defect_dir, filename)):
                    continue
                stem = os.path.splitext(filename)[0]
                if not train and defect != "good":
                    mask_path = self._mask_path(defect, stem)
                    if not os.path.isfile(mask_path):
                        raise FileNotFoundError(mask_path)
                self.ids.append(f"{'train_good' if train else defect}/{stem}")
                self.targets.append(int(defect != "good"))
        if not self.ids:
            raise ValueError(f"No MVTec PNG images found in '{split_dir}'")

    def _image_path(self, defect, stem):
        split_dir, defect_dir = ("train", "good") if defect == "train_good" else ("test", defect)
        return os.path.join(self.category_dir, split_dir, defect_dir, stem + ".png")

    def _mask_path(self, defect, stem):
        return os.path.join(self.category_dir, "ground_truth", defect, stem + "_mask.png")

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, index):
        defect, stem = self.ids[index].split("/")
        with Image.open(self._image_path(defect, stem)) as file:
            image = file.convert("RGB")
        target = {}
        if not self.train:
            mask = np.zeros((image.height, image.width), dtype=np.int64)
            if defect != "good":
                with Image.open(self._mask_path(defect, stem)) as file:
                    mask = (np.asarray(file.convert("L")) > 0).astype(np.int64)
            target = {"label": torch.tensor(int(defect != "good")), "mask": torch.from_numpy(mask)}
        if self.transform is not None:
            return self.transform(image, target)
        from torchvision.transforms.v2 import functional

        return functional.to_dtype(functional.to_image(image), torch.float32, scale=True), target
