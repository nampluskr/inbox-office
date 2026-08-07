# src/utils/paths.py: local dataset and backbone path resolution for Windows and WSL environments

import os


WSL_DATASET_ROOT = "/mnt/d/datasets"
WSL_BACKBONE_ROOT = "/mnt/d/backbones"
WINDOWS_DATASET_ROOT = "E:/datasets"
WINDOWS_BACKBONE_ROOT = "E:/backbones"
WINDOWS_DATASET_MAPPINGS = {
    "/mnt/d/datasets/midv2020_processed": "midv_2020/midv2020_processed",
    "/mnt/d/datasets/smart_doc_extracted": "smartdoc_2015/smart_doc_extracted",
}

DATASET_ROOT = os.environ.get(
    "ROI_DATASET_ROOT",
    WINDOWS_DATASET_ROOT if os.name == "nt" else WSL_DATASET_ROOT,
)
BACKBONE_ROOT = os.environ.get(
    "ROI_BACKBONE_ROOT",
    WINDOWS_BACKBONE_ROOT if os.name == "nt" else WSL_BACKBONE_ROOT,
)


def resolve_dataset_path(path):
    """Map legacy WSL dataset paths to the active environment root."""
    if os.name != "nt" or not path.startswith(WSL_DATASET_ROOT):
        return path
    for legacy_path, relative_path in WINDOWS_DATASET_MAPPINGS.items():
        if path == legacy_path or path.startswith(legacy_path + "/"):
            suffix = path[len(legacy_path):].lstrip("/")
            return os.path.join(DATASET_ROOT, relative_path, *suffix.split("/"))
    suffix = path[len(WSL_DATASET_ROOT):].lstrip("/")
    return os.path.join(DATASET_ROOT, *suffix.split("/"))


def backbone_path(*parts):
    """Return a path below the active local backbone root."""
    return os.path.join(BACKBONE_ROOT, *parts)
