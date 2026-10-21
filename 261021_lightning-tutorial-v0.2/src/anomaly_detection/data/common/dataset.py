import os
from collections.abc import Callable

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import tv_tensors
from torchvision.transforms import v2
from torchvision.transforms.v2 import functional


class FolderAnomalyDataset(Dataset):
    normal_name = "good"
    extensions = (".png",)
    mask_suffix = "_mask"
    mask_extensions = (".png",)

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
        defect_names = [self.normal_name] if train else sorted(
            name for name in os.listdir(split_dir)
            if os.path.isdir(os.path.join(split_dir, name))
        )
        self.image_paths = {}
        self.ids = []
        self.targets = []
        for defect in defect_names:
            defect_dir = os.path.join(split_dir, defect)
            if not os.path.isdir(defect_dir):
                raise FileNotFoundError(defect_dir)
            for filename in sorted(os.listdir(defect_dir)):
                if not filename.lower().endswith(self.extensions):
                    continue
                if not os.path.isfile(os.path.join(defect_dir, filename)):
                    continue
                stem = os.path.splitext(filename)[0]
                if not train and defect != self.normal_name:
                    mask_path = self._mask_path(defect, stem)
                    if not os.path.isfile(mask_path):
                        raise FileNotFoundError(mask_path)
                sample_id = f"{'train_good' if train else defect}/{stem}"
                if sample_id in self.image_paths:
                    raise ValueError(f"Duplicate image stem: {sample_id}")
                self.ids.append(sample_id)
                self.image_paths[sample_id] = os.path.join(defect_dir, filename)
                self.targets.append(int(defect != self.normal_name))
        if not self.ids:
            raise ValueError(f"No supported anomaly images found in '{split_dir}'")

    def _image_path(self, defect, stem):
        return self.image_paths[f"{defect}/{stem}"]

    def _mask_path(self, defect, stem):
        directory = os.path.join(self.category_dir, "ground_truth", defect)
        for extension in self.mask_extensions:
            path = os.path.join(directory, stem + self.mask_suffix + extension)
            if os.path.isfile(path):
                return path
        return os.path.join(directory, stem + self.mask_suffix + self.mask_extensions[0])

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, index):
        defect, stem = self.ids[index].split("/")
        with Image.open(self._image_path(defect, stem)) as file:
            image = file.convert("RGB")
        target = {}
        if not self.train:
            mask = np.zeros((image.height, image.width), dtype=np.int64)
            if defect != self.normal_name:
                with Image.open(self._mask_path(defect, stem)) as file:
                    mask = (np.asarray(file.convert("L")) > 0).astype(np.int64)
            target = {"label": torch.tensor(int(defect != self.normal_name)), "mask": torch.from_numpy(mask)}
        if self.transform is not None:
            return self.transform(image, target)
        return functional.to_dtype(functional.to_image(image), torch.float32, scale=True), target


class AnomalyTransform:
    def __init__(self, image_size: int = 256, normalize: bool = True):
        transforms = [
            v2.Resize((image_size, image_size), antialias=True),
            v2.ToDtype({tv_tensors.Image: torch.float32, tv_tensors.Mask: torch.int64}, scale=True),
        ]
        if normalize:
            transforms.append(v2.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)))
        self.compose = v2.Compose(transforms)

    def __call__(self, image, target=None):
        image = functional.to_image(image)
        if target is None:
            return self.compose(image)
        if not target:
            return self.compose(image), {}
        image, mask = self.compose(image, tv_tensors.Mask(target["mask"]))
        return image, {**target, "mask": mask.to(torch.int64)}
