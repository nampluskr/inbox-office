import os
import sys


def main():
    if __package__ in (None, ""):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        # Resolve configuration contents and output paths from the project root.
        os.chdir(project_root)

    from lightning.pytorch.cli import LightningCLI

    from src.lightning.tasks.classification.datamodule import ClassificationData
    from src.lightning.tasks.classification.taskmodule import ClassificationModule

    LightningCLI(
        model_class=ClassificationModule,
        datamodule_class=ClassificationData,
        save_config_kwargs={"overwrite": False},
        auto_configure_optimizers=True,
    )


if __name__ == "__main__":
    main()
