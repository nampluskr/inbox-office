import argparse
import json
import os
import sys


PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import torch
from lightning.pytorch.cli import LightningCLI

from src.anomaly_detection.data.btad.lightning_data import BTADLitData
from src.anomaly_detection.data.mvtec.lightning_data import MVTecLitData
from src.anomaly_detection.data.visa.lightning_data import VisALitData
from src.anomaly_detection.models.efficientad.lightning_model import EfficientAdLitModel
from src.anomaly_detection.models.common.tiler import Tiler
from src.anomaly_detection.models.stfpm.lightning_model import STFPMLitModel
from src.anomaly_detection.trainers.config import resolve_anomaly_config_paths
from src.anomaly_detection.trainers.lightning_trainer import AnomalyLitTrainer
from src.utils.config import merge_config


DATASETS = ("mvtec", "btad", "visa")
MODELS = ("stfpm", "efficientad")


def select_components(args):
    selector = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    selector.add_argument("--data", choices=DATASETS)
    selector.add_argument("--model", choices=MODELS)
    selector.add_argument("--config", "-c", action="append", default=[])
    selector.add_argument("--model.backbone", dest="backbone")
    selector.add_argument("--model.model_size", dest="model_size")
    selector.add_argument("--data.category", dest="category")
    if hasattr(args, "as_dict"):
        args = args.as_dict()
    if isinstance(args, dict):
        args = merge_config(args)
        config = args[args["subcommand"]] if args.get("subcommand") else args
        selection = {"data": "mvtec", "model": "stfpm", **config.get("selection", {})}
        config["selection"] = selection
    else:
        selected, remaining = selector.parse_known_args(args)
        config = merge_config(*selected.config)
        selection = {"data": "mvtec", "model": "stfpm", **config.get("selection", {})}
        if selected.data is not None:
            selection["data"] = selected.data
        if selected.model is not None:
            selection["model"] = selected.model
        config_args = [value for path in selected.config for value in ("--config", path)]
        if remaining and remaining[0] in ("fit", "validate", "test", "predict"):
            args = [remaining[0], *config_args, *remaining[1:]]
        else:
            args = [*config_args, *remaining]
        if selected.backbone is not None:
            config = merge_config(config, {"model": {"backbone": selected.backbone}})
            args.extend(["--model.backbone", selected.backbone])
        if selected.model_size is not None:
            config = merge_config(config, {"model": {"model_size": selected.model_size}})
            args.extend(["--model.model_size", selected.model_size])
        if selected.category is not None:
            config = merge_config(config, {"data": {"category": selected.category}})
            args.extend(["--data.category", selected.category])
        # Selection is saved outside the model and data constructor arguments.
        args.extend(["--selection", json.dumps(selection)])
    if selection["data"] not in DATASETS or selection["model"] not in MODELS:
        selector.error(f"Invalid selection: {selection}; data={DATASETS}, model={MODELS}")
    if set(selection) != {"data", "model"}:
        selector.error("selection only accepts data and model")
    return selection, config, args


def build_default_config(selection, overrides):
    config_dir = os.path.join(PROJECT_DIR, "src", "anomaly_detection", "configs")
    config = merge_config(
        os.path.join(config_dir, "default.yaml"),
        os.path.join(config_dir, "data", f"{selection['data']}.yaml"),
        os.path.join(config_dir, "models", f"{selection['model']}.yaml"),
        os.path.join(config_dir, "trainer.yaml"),
    )
    variant_key = "backbone" if selection["model"] == "stfpm" else "model_size"
    variant = overrides.get("model", {}).get(variant_key, config["model"][variant_key])
    category = overrides.get("data", {}).get("category", config["data"]["category"])
    config["trainer"]["logger"]["name"] = (
        f"anomaly-{selection['data']}-{category}-{selection['model']}-{variant}"
    )
    config["selection"] = selection
    return config


def validate_config(config, selection):
    if config["selection"] != selection:
        raise ValueError("Final selection must match the selected data and model classes")
    if selection["model"] == "efficientad":
        if config["data"]["normalize"] or config["data"]["batch_size"] != 1:
            raise ValueError("EfficientAD requires data.normalize=false and data.batch_size=1")
        if config["data"]["image_size"] != 256:
            raise ValueError("EfficientAD currently requires data.image_size=256")
        if config["trainer"]["num_sanity_val_steps"] != 0:
            raise ValueError("EfficientAD requires trainer.num_sanity_val_steps=0")


class AnomalyLitCLI(LightningCLI):
    def __init__(self, default_config, from_command_line=False, **kwargs):
        self.default_config = default_config
        self.from_command_line = from_command_line
        super().__init__(**kwargs)

    def parse_arguments(self, parser, args):
        if self.from_command_line:
            # These arguments were intentionally normalized from sys.argv.
            self.config = parser.parse_args(args)
        else:
            super().parse_arguments(parser, args)

    def add_arguments_to_parser(self, parser):
        parser.description = (
            "Select YAMLs with --data mvtec|btad|visa and --model stfpm|efficientad. "
            "Override arguments with --data.xxx, --model.xxx and --trainer.xxx."
        )
        parser.add_argument("--selection", type=dict)
        parser.add_argument("--paths_file", type=str, default=None)
        parser.add_argument("--tiler", type=dict, default=None)
        parser.set_defaults(self.default_config)

    def before_instantiate_classes(self):
        torch.set_float32_matmul_precision("high")
        config = self.config[self.subcommand] if self.subcommand else self.config
        values = config.as_dict()
        selection = self.default_config["selection"]
        validate_config(values, selection)
        resolved = resolve_anomaly_config_paths(
            values, paths_file=config.paths_file, training=self.subcommand in (None, "fit"),
        )
        config.data.root = resolved["data"]["root"]
        if "imagenet_dir" in resolved["model"]:
            config.model.imagenet_dir = resolved["model"]["imagenet_dir"]

    def after_instantiate_classes(self):
        config = self.config[self.subcommand] if self.subcommand else self.config
        if self.default_config["selection"]["model"] == "stfpm" and config.tiler is not None:
            self.model.model.tiler = Tiler(**config.tiler)


def main(args=None, **kwargs):
    from_command_line = args is None
    if args is None:
        args = sys.argv[1:]
    selection, overrides, args = select_components(args)
    default_config = build_default_config(selection, overrides)
    model_class = STFPMLitModel if selection["model"] == "stfpm" else EfficientAdLitModel
    datamodule_class = {
        "mvtec": MVTecLitData,
        "btad": BTADLitData,
        "visa": VisALitData,
    }[selection["data"]]
    kwargs.setdefault("trainer_class", AnomalyLitTrainer)
    kwargs.setdefault("auto_configure_optimizers", False)
    return AnomalyLitCLI(
        default_config,
        from_command_line=from_command_line,
        model_class=model_class,
        datamodule_class=datamodule_class,
        args=args,
        **kwargs,
    )


if __name__ == "__main__":
    main()
