import os
import sys


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.chdir(project_root)
    print("Python:", sys.executable)
    print("Project:", project_root)

    # Import existing PyTorch and Lightning components.
    import csv
    import json
    from datetime import datetime

    import torch
    import yaml
    from lightning.pytorch import Trainer, seed_everything
    from lightning.pytorch.callbacks import ModelCheckpoint
    from lightning.pytorch.loggers import CSVLogger
    from torch.utils.data import Subset

    from src.lightning.tasks.classification.datamodule import ClassificationData
    from src.lightning.tasks.classification.taskmodule import ClassificationModule
    from src.torch.inference.predictor import Predictor
    from src.torch.tasks.classification.data.cifar10.dataset import (
        CLASS_NAMES,
        DATA_ROOT,
        CIFAR10Dataset,
    )
    from src.torch.tasks.classification.data.cifar10.transform import CIFAR10Transform
    from src.torch.tasks.classification.models.cnn.model import ClassificationModel
    from src.torch.tasks.classification.postprocessors.classification import ClassificationPostprocess
    from src.torch.tasks.classification.preprocessors.classification import ClassificationPreprocess

    print("PyTorch:", torch.__version__)
    print("CUDA:", torch.cuda.is_available())

    # Edit these settings to configure the run.
    seed = 42
    max_epochs = 10
    learning_rate = 0.001
    weight_decay = 0.0001
    valid_size = 5000
    num_classes = len(CLASS_NAMES)
    data_options = {
        "root": DATA_ROOT,
        "seed": seed,
        "batch_size": 32,
        "num_workers": 0,
        "pin_memory": True,
        "image_size": 224,
    }
    run_id = "custom_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = os.path.join("outputs", "cifar10", run_id)
    seed_everything(seed, workers=True)

    print("Data:", data_options["root"])
    print("Output:", os.path.abspath(output_dir))

    # Separate training sources retain their respective train/eval transforms.
    train_transform = CIFAR10Transform(train=True, image_size=data_options["image_size"])
    eval_transform = CIFAR10Transform(train=False, image_size=data_options["image_size"])
    train_dataset = CIFAR10Dataset(
        root=data_options["root"], train=True, transform=train_transform,
    )
    valid_dataset = CIFAR10Dataset(
        root=data_options["root"], train=True, transform=eval_transform,
    )
    test_dataset = CIFAR10Dataset(
        root=data_options["root"], train=False, transform=eval_transform,
    )

    # Predict only the first 16 test samples to keep the example output small.
    predict_dataset = Subset(test_dataset, range(min(16, len(test_dataset))))
    data = ClassificationData(
        train_dataset=train_dataset,
        valid_dataset=valid_dataset,
        test_dataset=test_dataset,
        predict_dataset=predict_dataset,
        valid_size=valid_size,
        seed=data_options["seed"],
        batch_size=data_options["batch_size"],
        num_workers=data_options["num_workers"],
        pin_memory=data_options["pin_memory"],
    )
    # ClassificationData splits once and creates all stage loaders.
    data.setup("fit")
    print({
        "train": len(data.train_dataset),
        "valid": len(data.valid_dataset),
        "test": len(data.test_dataset),
        "predict": len(data.predict_dataset),
    })

    # Configure the model, logging, checkpoints and saved run settings.
    module = ClassificationModule(
        model=ClassificationModel(backbone="custom", num_classes=num_classes),
        num_classes=num_classes,
        preprocess=ClassificationPreprocess(),
        postprocess=ClassificationPostprocess(),
        learning_rate=learning_rate,
        weight_decay=weight_decay,
    )
    os.makedirs(output_dir, exist_ok=False)
    logger = CSVLogger(save_dir="outputs/cifar10", name="", version=run_id)
    checkpoint = ModelCheckpoint(
        dirpath=output_dir,
        filename="best",
        monitor="valid_loss",
        mode="min",
        save_top_k=1,
        save_last=True,
        auto_insert_metric_name=False,
        enable_version_counter=False,
    )
    trainer = Trainer(
        accelerator="auto",
        devices=1,
        precision="32-true",
        max_epochs=max_epochs,
        default_root_dir=output_dir,
        logger=logger,
        callbacks=[checkpoint],
        log_every_n_steps=10,
    )

    config = {
        "seed": seed,
        "model": {"backbone": "custom", "num_classes": num_classes},
        "data": {**data_options, "valid_size": valid_size},
        "optimizer": {"name": "AdamW", "lr": learning_rate, "weight_decay": weight_decay},
        "trainer": {"max_epochs": max_epochs, "accelerator": "auto", "devices": 1, "precision": "32-true"},
        "output_dir": output_dir,
    }
    with open(os.path.join(output_dir, "config.yaml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, allow_unicode=True, sort_keys=False)

    # Train the custom CNN from scratch.
    trainer.fit(module, datamodule=data)
    print("Best checkpoint:", checkpoint.best_model_path)
    print("Best valid_loss:", checkpoint.best_model_score)

    # Evaluate the checkpoint with the lowest validation loss.
    valid_metrics = trainer.validate(module, datamodule=data, ckpt_path="best")
    test_metrics = trainer.test(module, datamodule=data, ckpt_path="best")
    metrics = {"valid": valid_metrics, "test": test_metrics}
    with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

    # Save predictions for the first 16 test samples.
    prediction_batches = trainer.predict(module, datamodule=data, ckpt_path="best")
    labels = torch.cat([batch["labels"].detach().cpu() for batch in prediction_batches])
    probabilities = torch.cat([batch["probabilities"].detach().cpu() for batch in prediction_batches])
    predict_loader = data.predict_dataloader()
    targets = torch.cat([targets for _, targets in predict_loader])
    rows = []
    for index, (target, label, probability) in enumerate(zip(targets, labels, probabilities)):
        rows.append({
            "test_index": index,
            "target": int(target),
            "target_name": CLASS_NAMES[int(target)],
            "prediction": int(label),
            "prediction_name": CLASS_NAMES[int(label)],
            "confidence": float(probability.max()),
        })
    with open(os.path.join(output_dir, "predictions.csv"), "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)

    # Export pure PyTorch weights and restore them in Predictor.
    best_module = ClassificationModule.load_from_checkpoint(
        checkpoint.best_model_path,
        map_location="cpu",
        model=ClassificationModel(backbone="custom", num_classes=num_classes),
        preprocess=ClassificationPreprocess(),
        postprocess=ClassificationPostprocess(),
    )
    weights_path = os.path.join(output_dir, "model.pt")
    torch.save(best_module.model.state_dict(), weights_path)

    predictor = Predictor(
        ClassificationModel(backbone="custom", num_classes=num_classes),
        postprocess=ClassificationPostprocess(),
        device="cuda" if torch.cuda.is_available() else "cpu",
    )
    predictor.load_weights(weights_path)
    images, targets = next(iter(predict_loader))
    outputs = predictor.predict_batch(images)
    print("Weights:", weights_path)
    print("Targets:", targets.tolist())
    print("Predictions:", outputs["labels"].cpu().tolist())


if __name__ == "__main__":
    main()
