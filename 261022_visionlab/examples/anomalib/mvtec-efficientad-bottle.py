import os

import torch
from lightning.pytorch import seed_everything
from lightning.pytorch.loggers import CSVLogger

from anomalib.engine import Engine
from anomalib.models import EfficientAd

from _common import LocalMVTecAD


TEACHER_PATH = "E:/backbones/efficientad_pretrained_weights/pretrained_teacher_small.pth"


class LocalEfficientAd(EfficientAd):
    # Override only the hooks that can download external assets.
    def prepare_pretrained_model(self):
        weights = torch.load(TEACHER_PATH, map_location="cpu", weights_only=True)
        self.model.teacher.load_state_dict(weights)

    def prepare_imagenette_data(self, image_size):
        if not os.path.isdir(self.imagenet_dir):
            raise FileNotFoundError(self.imagenet_dir)
        super().prepare_imagenette_data(image_size)


def main():
    seed_everything(42, workers=True)
    datamodule = LocalMVTecAD(
        root="E:/datasets/mvtec",
        category="bottle",
        train_batch_size=1,
        eval_batch_size=8,
        num_workers=0,
        val_split_mode="from_test",
        val_split_ratio=0.4,
        seed=42,
    )
    model = LocalEfficientAd(
        imagenet_dir="E:/datasets/imagenette2/train",
        model_size="small",
        visualizer=False,
    )
    engine = Engine(
        default_root_dir="outputs/anomalib/efficientad",
        logger=CSVLogger("outputs/anomalib", name="efficientad"),
        max_epochs=10,
        devices=1,
    )
    engine.fit(model=model, datamodule=datamodule)
    engine.test(model=model, datamodule=datamodule)


if __name__ == "__main__":
    main()
