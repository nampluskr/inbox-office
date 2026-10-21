import os
import warnings

import lightning.pytorch as pl
import torch
import yaml
from lightning.pytorch.callbacks import Callback, ModelCheckpoint
from lightning.pytorch.loggers import CSVLogger

from src.utils.io import save_json


def save_run_config(trainer, config):
    # Initialize CSVLogger before writing files into its experiment directory.
    _ = trainer.logger.experiment
    os.makedirs(trainer.log_dir, exist_ok=True)
    with open(os.path.join(trainer.log_dir, "config.yaml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False, allow_unicode=True)


def save_run_results(trainer, model, results):
    save_json(os.path.join(trainer.log_dir, "test_metrics.json"), results)
    # Pass the plain model after trainer.test restores the best checkpoint.
    state_dict = {name: value.detach().cpu() for name, value in model.state_dict().items()}
    torch.save(state_dict, os.path.join(trainer.log_dir, "model.pt"))


class MetricsPrinter(Callback):
    def __init__(self):
        self.validation_ran = False

    def on_train_epoch_start(self, trainer, pl_module):
        self.validation_ran = False

    def on_validation_end(self, trainer, pl_module):
        if trainer.sanity_checking:
            return
        if trainer.state.fn == "fit":
            self.validation_ran = True
        else:
            self._print_metrics(trainer, pl_module, ("valid_image_auroc", "valid_pixel_auroc"))

    def on_train_epoch_end(self, trainer, pl_module):
        names = ("train_loss",)
        if self.validation_ran:
            names += ("valid_image_auroc", "valid_pixel_auroc")
        # The current epoch's train loss is available after the train loop finishes.
        self._print_metrics(trainer, pl_module, names)

    def _print_metrics(self, trainer, pl_module, names):
        if not trainer.is_global_zero:
            return
        metrics = trainer.callback_metrics
        values = " ".join(
            f"{name}={metrics[name].item():.4f}"
            for name in names
            if name in metrics
        )
        pl_module.print(f"Epoch {trainer.current_epoch + 1} | {values}")


def create_logger(config: dict | None = None) -> CSVLogger:
    if config is not None and not isinstance(config, dict):
        raise TypeError("logger must be a dictionary of CSVLogger arguments or None")
    logger_args = {"save_dir": "outputs", "name": "anomaly_detection"}
    if config is not None:
        if "class_path" in config or "init_args" in config:
            raise ValueError("logger accepts CSVLogger arguments directly, without class_path or init_args")
        logger_args.update(config)
    return CSVLogger(**logger_args)


def create_callbacks(
    config: dict | list[Callback | dict] | None = None,
) -> list[Callback]:
    callback_args = {
        "checkpoint": {
            "filename": "best", "monitor": "valid_image_auroc", "mode": "max",
            "save_top_k": 1, "save_last": True, "auto_insert_metric_name": False,
        },
        "metrics_printer": {},
    }
    extra_callbacks = []
    if config is None:
        entries = []
    elif isinstance(config, dict):
        entries = [config]
    elif isinstance(config, list):
        entries = config
    else:
        raise TypeError("callbacks must be a dictionary, a CLI callback list, or None")
    for entry in entries:
        if isinstance(entry, Callback):
            extra_callbacks.append(entry)
            continue
        if not isinstance(entry, dict):
            raise TypeError("Callback entries must be argument dictionaries or Callback objects")
        for name, arguments in entry.items():
            if name not in callback_args:
                raise ValueError(f"Unsupported callback configuration: {name!r}")
            if not isinstance(arguments, dict):
                raise TypeError(f"callbacks.{name} must be an argument dictionary")
            callback_args[name].update(arguments)
    return [
        ModelCheckpoint(**callback_args["checkpoint"]),
        MetricsPrinter(**callback_args["metrics_printer"]),
        *extra_callbacks,
    ]


class AnomalyLitTrainer(pl.Trainer):
    def __init__(
        self,
        logger: dict | None = None,
        callbacks: dict | list[Callback | dict] | None = None,
        **kwargs,
    ):
        warnings.filterwarnings(
            "ignore",
            message=r"The '(train|val|test|predict)_dataloader' does not have many workers",
            category=UserWarning,
            module=r"lightning\.pytorch\.trainer\.connectors\.data_connector",
        )
        super().__init__(
            logger=create_logger(logger), callbacks=create_callbacks(callbacks), **kwargs,
        )
