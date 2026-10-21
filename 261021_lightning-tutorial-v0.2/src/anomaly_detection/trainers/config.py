import os
from copy import deepcopy

from src.utils.config import (
    get_backbone_dir,
    get_dataset_dir,
    load_paths_config,
    resolve_config_paths,
)


def resolve_anomaly_config_paths(config, paths_file=None, training=True):
    selection = config["selection"]
    resolved = resolve_config_paths(
        {**config, "model": {}}, dataset_name=selection["data"], paths_file=paths_file,
    )
    model = deepcopy(config["model"])
    if selection["model"] == "stfpm":
        if training:
            get_backbone_dir(model["backbone"], load_paths_config(paths_file))
        resolved["model"] = model
        return resolved
    # Evaluation restores all weights and calibration from the checkpoint.
    paths = None
    if training:
        paths = load_paths_config(paths_file)
        get_backbone_dir(f"efficientad_{model['model_size']}", paths)
    if training and model.get("imagenet_dir") is None:
        model["imagenet_dir"] = get_dataset_dir("imagenette", paths)
    if model.get("imagenet_dir") is not None:
        model["imagenet_dir"] = os.path.abspath(model["imagenet_dir"])
    if training:
        train_dir = os.path.join(model["imagenet_dir"], "train")
        if not os.path.isdir(train_dir):
            raise FileNotFoundError(f"ImageNette train directory not found: {train_dir}")
    resolved["model"] = model
    return resolved
