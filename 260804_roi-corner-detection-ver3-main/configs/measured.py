# configs/measured.py: batch experiment combinations for the measured dataset stage

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import MODELS

BASE = {
    "dataset": "measured",
    "csv_path": ["data/measured/train/gt_corners.csv"],
    "test_csv_path": ["data/measured/test/gt_corners.csv"],
    "split_ratio": 0.8,
    "image_size": 512,
    "batch_size": 4,
    "max_epochs": 100,
    "patience": 10,
}

CONFIGS = [{**BASE, **model} for model in MODELS]
