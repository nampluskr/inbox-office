trainer:
  accelerator: auto
  devices: 1
  max_epochs: 10
  precision: 32-true
  log_every_n_steps: 1
  num_sanity_val_steps: 0
  gradient_clip_val: 0
  enable_progress_bar: true
  enable_model_summary: false
  check_val_every_n_epoch: 1
  default_root_dir: outputs
  logger:
    save_dir: outputs
    name: anomaly-mvtec-bottle-stfpm-resnet18
  callbacks:
    checkpoint:
      filename: best
      monitor: valid_image_auroc
      mode: max
      save_top_k: 1
      save_last: true
      auto_insert_metric_name: false
    metrics_printer: {}
