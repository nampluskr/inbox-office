# configs/public.py: batch experiment combinations for the public dataset stage

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import MODELS

BASE = {
    "dataset": "public",
    "csv_path": [
        "data/public/smartdoc/gt_corners.csv",
        "data/public/midv2020/gt_corners.csv",
    ],
    "image_size": 512,
    "batch_size": 4,
    "max_epochs": 100,
    "patience": 5,
    "train_size": 2000,
    "valid_size": 1000,
    "test_size": 1000,
}

CONFIGS = [{**BASE, **model} for model in MODELS]
