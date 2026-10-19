from copy import deepcopy

import yaml


def load_yaml(path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError(f"YAML must contain a configuration dictionary: {path}")
    return config


def merge_config(base: dict, overrides: dict) -> dict:
    if not isinstance(base, dict) or not isinstance(overrides, dict):
        raise TypeError("base and overrides must be dictionaries")
    merged = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged
