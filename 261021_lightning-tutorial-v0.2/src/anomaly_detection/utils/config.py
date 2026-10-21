import os
import tomllib
from copy import deepcopy

import yaml


def load_paths_config(path: str | None = None) -> dict:
    if path is None:
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(project_dir, "paths.toml")
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Path configuration not found: {path}. Copy paths.example.toml to paths.toml."
        )
    with open(path, "rb") as file:
        paths = tomllib.load(file)
    config_dir = os.path.dirname(path)
    datasets = paths.setdefault("datasets", {})
    backbones = paths.setdefault("backbones", {})
    if not isinstance(datasets, dict) or not isinstance(backbones, dict):
        raise ValueError("datasets and backbones must be TOML tables")
    for name, directory in datasets.items():
        datasets[name] = _resolve_config_path(directory, config_dir)
    for name, weights_path in backbones.items():
        backbones[name] = _resolve_config_path(weights_path, config_dir)
    return paths


def _resolve_config_path(path: str, config_dir: str) -> str:
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Configured paths must be non-empty strings")
    if not os.path.isabs(path):
        path = os.path.join(config_dir, path)
    return os.path.abspath(path)


def get_dataset_dir(dataset_name: str, paths: dict) -> str:
    if dataset_name not in paths.get("datasets", {}):
        raise ValueError(f"Dataset is not registered in paths configuration: {dataset_name!r}")
    dataset_dir = paths["datasets"][dataset_name]
    if not os.path.isdir(dataset_dir):
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
    return dataset_dir


def get_backbone_dir(backbone_name: str, paths: dict) -> str:
    if backbone_name not in paths.get("backbones", {}):
        raise ValueError(f"Backbone is not registered in paths configuration: {backbone_name!r}")
    weights_path = paths["backbones"][backbone_name]
    if not os.path.isfile(weights_path):
        raise FileNotFoundError(f"Backbone weights not found: {weights_path}")
    return weights_path


def resolve_config_paths(
    config: dict, dataset_name: str, paths_file: str | None = None,
) -> dict:
    resolved = deepcopy(config)
    paths = None
    dataset_dir = resolved["data"].get("root")
    if dataset_dir is None:
        paths = load_paths_config(paths_file)
        dataset_dir = get_dataset_dir(dataset_name, paths)
    else:
        dataset_dir = _resolve_config_path(dataset_dir, os.getcwd())
        if not os.path.isdir(dataset_dir):
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
    resolved["data"]["root"] = dataset_dir

    model = resolved.get("model", {})
    weights_path = model.get("weights_path")
    backbone_name = model.get("backbone")
    if weights_path is not None:
        weights_path = _resolve_config_path(weights_path, os.getcwd())
        if not os.path.isfile(weights_path):
            raise FileNotFoundError(f"Backbone weights not found: {weights_path}")
        model["weights_path"] = weights_path
    elif backbone_name is not None and backbone_name != "custom":
        if paths is None:
            paths = load_paths_config(paths_file)
        model["weights_path"] = get_backbone_dir(backbone_name, paths)
    return resolved


def load_yaml(path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError(f"YAML must contain a configuration dictionary: {path}")
    return config


def merge_config(*configs: dict | str) -> dict:
    merged = {}
    for config in configs:
        if isinstance(config, str):
            config = load_yaml(config)
        if not isinstance(config, dict):
            raise TypeError("Each config must be a dictionary or a YAML file path")
        for key, value in config.items():
            if isinstance(merged.get(key), dict) and isinstance(value, dict):
                merged[key] = merge_config(merged[key], value)
            else:
                merged[key] = deepcopy(value)
    return merged
