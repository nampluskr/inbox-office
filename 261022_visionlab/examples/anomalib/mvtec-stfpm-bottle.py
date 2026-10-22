import os

from lightning.pytorch import seed_everything
from lightning.pytorch.loggers import CSVLogger
from timm.models import register_model
from timm.models.resnet import resnet18

from anomalib.engine import Engine
from anomalib.models import Stfpm

from _common import LocalMVTecAD


WEIGHTS_PATH = "E:/backbones/resnet18-f37072fd.pth"


@register_model
def local_resnet18(pretrained=False, **kwargs):
    # Use the local teacher weights through timm's native configuration.
    if pretrained and not os.path.isfile(WEIGHTS_PATH):
        raise FileNotFoundError(WEIGHTS_PATH)
    kwargs["pretrained_cfg_overlay"] = {
        "file": WEIGHTS_PATH, "hf_hub_id": None, "url": "",
    }
    return resnet18(pretrained=pretrained, **kwargs)


def main():
    seed_everything(42, workers=True)
    datamodule = LocalMVTecAD(
        root="E:/datasets/mvtec",
        category="bottle",
        train_batch_size=8,
        eval_batch_size=8,
        num_workers=0,
        val_split_mode="from_test",
        val_split_ratio=0.4,
        seed=42,
    )
    model = Stfpm(backbone="local_resnet18", visualizer=False)
    engine = Engine(
        default_root_dir="outputs/anomalib/stfpm",
        logger=CSVLogger("outputs/anomalib", name="stfpm"),
        max_epochs=10,
        devices=1,
    )
    engine.fit(model=model, datamodule=datamodule)
    engine.test(model=model, datamodule=datamodule)


if __name__ == "__main__":
    main()
