import os
import sys

PROJECT_DIR = os.path.normpath(os.path.join(os.path.abspath(os.getcwd()), ".."))

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)


import lightning.pytorch as pl

from src.anomaly_detection.data.mvtec.lightning_datamodule import MVTecDataModule
from src.anomaly_detection.models.stfpm.model import STFPMModel
from src.anomaly_detection.models.stfpm.lightning_module import STFPMModule
from src.anomaly_detection.models.stfpm.loss import STFPMLoss

## data
DATA_ROOT = "E:/datasets/mvtec"
CATEGORY = "bottle"
SEED = 42
VALID_RATIO = 0.4
BATCH_SIZE = 8
NUM_WORKERS = 0
IMAGE_SIZE = 256

## model
WEIGHTS_PATH = "E:/backbones/resnet18-f37072fd.pth"
LAYERS = ("layer1", "layer2", "layer3")

## train
pl.seed_everything(SEED, workers=True)


data_module = MVTecDataModule(
    root=DATA_ROOT,
    category=CATEGORY,
    valid_ratio=VALID_RATIO,
    seed=SEED,
    batch_size=BATCH_SIZE,
    num_workers=NUM_WORKERS,
    image_size=IMAGE_SIZE,
)

model = STFPMModel(
    weights_path=WEIGHTS_PATH,
    layers=LAYERS,
)

lightning_model = STFPMModule(
    model=model,
    loss_fn=STFPMLoss(),
    learning_rate=0.4,
    momentum=0.9,
    weight_decay=0.001,
)

logger = pl.loggers.CSVLogger(
    save_dir=os.path.join(PROJECT_DIR, "outputs"),
    name="anomaly-mvtec-stfpm",
)

checkpoint = pl.callbacks.ModelCheckpoint(
    dirpath=os.path.join(logger.log_dir, "checkpoints"),
    filename="best",
    monitor="valid_image_auroc",
    mode="max",
    save_top_k=1,
    save_last=True,
)

trainer = pl.Trainer(
    accelerator="auto",
    devices=1,
    precision="32-true",
    max_epochs=2,
    limit_train_batches=10,
    # AUROC requires both normal and anomalous samples.
    limit_val_batches=1.0,
    num_sanity_val_steps=0,
    log_every_n_steps=1,
    logger=logger,
    callbacks=[checkpoint],
    default_root_dir=logger.log_dir,
)

trainer.fit(
    model=lightning_model,
    datamodule=data_module,
)

