import os
import sys

PROJECT_DIR = os.path.normpath(os.path.join(os.path.abspath(os.getcwd()), ".."))

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import torch
from torch.utils.data import random_split
import lightning.pytorch as pl

from src.classification.data.cifar10.dataset import CIFAR10Dataset
from src.classification.data.cifar10.transform import CIFAR10Transform
from src.classification.models.cnn.model import ClassificationModel
from src.classification.models.cnn.lightning_module import ClassificationModule
from src.classification.models.cnn.loss import ClassificationLoss


## data
DATA_ROOT = "E:/datasets/cifar10"
SEED = 42
BATCH_SIZE = 16
NUM_WORKERS = 0

## model
BACKBONE = "resnet50"
WEIGHTS_PATH = "E:/backbones/resnet50-0676ba61.pth"
NUM_CLASSES = 10

## train
pl.seed_everything(SEED, workers=True)


train_source = CIFAR10Dataset(
    root=DATA_ROOT,
    train=True,
    transform=CIFAR10Transform(train=True),
)
valid_source = CIFAR10Dataset(
    root=DATA_ROOT,
    train=True,
    transform=CIFAR10Transform(train=False),
)
test_dataset = CIFAR10Dataset(
    root=DATA_ROOT,
    train=False,
    transform=CIFAR10Transform(train=False),
)

_, train_dataset = random_split(
    train_source,
    [5000, len(train_source) - 5000],
    generator=torch.Generator().manual_seed(SEED),
)
valid_dataset, _ = random_split(
    valid_source,
    [5000, len(valid_source) - 5000],
    generator=torch.Generator().manual_seed(SEED),
)

data_module = pl.LightningDataModule.from_datasets(
    train_dataset=train_dataset,
    val_dataset=valid_dataset,
    test_dataset=test_dataset,
    predict_dataset=test_dataset,
    batch_size=BATCH_SIZE,
    num_workers=NUM_WORKERS,
)

model = ClassificationModel(
    backbone=BACKBONE,
    num_classes=NUM_CLASSES,
    weights_path=WEIGHTS_PATH,
)

lightning_model = ClassificationModule(
    model=model,
    num_classes=NUM_CLASSES,
    loss_fn=ClassificationLoss(),
    learning_rate=0.001,
    weight_decay=0.0001,
)

logger = pl.loggers.CSVLogger(
    save_dir=os.path.join(PROJECT_DIR, "outputs"),
    name="classification-cifar10-resnet50",
)

checkpoint = pl.callbacks.ModelCheckpoint(
    dirpath=os.path.join(logger.log_dir, "checkpoints"),
    filename="best",
    monitor="valid_loss",
    mode="min",
    save_top_k=1,
    save_last=True,
)

trainer = pl.Trainer(
    accelerator="auto",
    devices=1,
    precision="32-true",
    max_epochs=2,
    limit_train_batches=10,
    limit_val_batches=10,
    # num_sanity_val_steps=0,
    # log_every_n_steps=1,
    logger=logger,
    callbacks=[checkpoint],
    default_root_dir=logger.log_dir,
)

trainer.fit(
    model=lightning_model,
    datamodule=data_module,
)
