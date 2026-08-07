# configs/synthetic.py: batch experiment combinations for the synthetic dataset stage

# BASE holds the fields shared by every experiment on the synthetic stage. Reuse
# the same model, network, head, and experiment identity as the public stage so
# train.py carries over weights from the public stage model.pth. Each entry in
# CONFIGS starts from BASE and overrides only what changes. The synthetic stage
# combines the fake, similar, and augmented sub datasets under data/synthetic.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import MODELS

BASE = {
    "dataset": "synthetic",
    "csv_path": [
        "data/synthetic/fake/gt_corners.csv",
        "data/synthetic/similar/gt_corners.csv",
        "data/synthetic/augmented/gt_corners.csv",
    ],
    "image_size": 512,
    "batch_size": 4,
    "max_epochs": 100,
    "patience": 5,
}

CONFIGS = [{**BASE, **model} for model in MODELS]
