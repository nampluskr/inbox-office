trainer:
  accelerator: auto
  devices: 1
  precision: 32-true
  max_epochs: 5
  log_every_n_steps: 50
  num_sanity_val_steps: 2
  enable_progress_bar: true
  enable_model_summary: false
  check_val_every_n_epoch: 1
  default_root_dir: outputs
  logger:
    save_dir: outputs
    name: classification-mnist-mlp
  callbacks:
    checkpoint:
      filename: best
      monitor: valid_loss
      mode: min
      save_top_k: 1
      save_last: true
      auto_insert_metric_name: false
    metrics_printer: {}
