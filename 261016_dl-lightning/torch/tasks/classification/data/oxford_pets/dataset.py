import json
import os
from collections.abc import Callable

import torch
from PIL import Image
from torch.utils.data import Dataset


DATA_ROOT = os.path.join("E:/datasets", "oxford_pets")


class OxfordPetsClassification(Dataset):
    def __init__(
        self, root=DATA_ROOT, split="train", transform: Callable | None = None,
        split_path=None, target_transform: Callable | None = None,
    ):
        if split not in ("train", "valid", "test"):
            raise ValueError(f"split must be one of train/valid/test, got '{split}'")
        if split_path is None:
            raise ValueError("OxfordPetsClassification requires a JSON split_path")

        self.root = root
        self.split = split
        self.transform = transform
        self.target_transform = target_transform
        self.split_path = split_path
        self.images_dir = os.path.join(root, "images")
        if not os.path.isdir(self.images_dir):
            raise FileNotFoundError(f"Oxford Pets images directory not found: {self.images_dir}")

        # list.txt defines the sample index; the images directory contains extra files.
        self.stem_to_class = {}
        class_names = {}
        list_path = os.path.join(root, "annotations", "list.txt")
        with open(list_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                stem, class_id = parts[0], int(parts[1])
                if not 1 <= class_id <= 37:
                    raise ValueError(f"Invalid class ID {class_id} in '{list_path}'")
                if stem in self.stem_to_class:
                    raise ValueError(f"Duplicate sample ID '{stem}' in '{list_path}'")
                self.stem_to_class[stem] = class_id
                class_names[class_id] = stem.rsplit("_", 1)[0]
        if set(class_names) != set(range(1, 38)):
            raise ValueError(f"Expected all 37 class IDs in '{list_path}'")
        self.classes = [class_names[class_id] for class_id in range(1, 38)]
        self.class_to_idx = {name: index for index, name in enumerate(self.classes)}

        with open(split_path, "r", encoding="utf-8") as file:
            split_dict = json.load(file)
        split_sets = {}
        for name in ("train", "valid", "test"):
            ids = split_dict.get(name)
            if not isinstance(ids, list) or not all(isinstance(stem, str) for stem in ids):
                raise ValueError(f"Split '{name}' must be a list of sample IDs")
            split_sets[name] = set(ids)
            if len(split_sets[name]) != len(ids):
                raise ValueError(f"Split '{name}' contains duplicate sample IDs")
            unknown = split_sets[name] - self.stem_to_class.keys()
            if unknown:
                raise ValueError(f"Split '{name}' references unknown IDs: {sorted(unknown)[:5]}")
        for first, second in (("train", "valid"), ("train", "test"), ("valid", "test")):
            overlap = split_sets[first] & split_sets[second]
            if overlap:
                raise ValueError(f"Splits '{first}' and '{second}' overlap: {sorted(overlap)[:5]}")

        self.ids = sorted(split_dict[split])
        self.samples = [(stem, self.stem_to_class[stem] - 1) for stem in self.ids]
        self.targets = [label for stem, label in self.samples]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        stem, label = self.samples[index]
        image_path = os.path.join(self.images_dir, stem + ".jpg")
        with Image.open(image_path) as source:
            image = source.convert("RGB")
        target = torch.tensor(label, dtype=torch.long)
        if self.transform is not None:
            image = self.transform(image)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return image, target
