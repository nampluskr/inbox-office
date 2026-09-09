# src/<task_runner_package>/adapter/base.py  (task-runner 저장소 자신의 공통 코드)
#
# task/model 내용과 무관한 공통 로직만 담는다 - base.yaml 병합, resolved.json
# 기록, checkpoint 경로 조합. model 선택(registry 조회)은 여기서 하지 않는다 -
# 어떤 model의 adapter를 쓸지는 task-runner의 source 로딩 절차가 job의
# params.model.name을 보고 미리 정하고, 그 model에 맞는 adapter 클래스를
# 바로 import해서 쓴다.

import json
from pathlib import Path

import yaml


def _deep_merge(base, override):
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class BaseAdapter:
    """모든 task, 모든 model의 adapter가 공유하는 공통 로직.
    train_step/eval_step/predict_step/configure_optimizer 등 실제 model
    로직은 subclass(adapters/<model-name>.py)가 구현한다."""

    def __init__(self, task_dir):
        self.task_dir = Path(task_dir)
        self._resolved_params = None

    def _resolve_params(self, context):
        base = yaml.safe_load((self.task_dir / "base.yaml").read_text(encoding="utf-8"))
        merged = _deep_merge(base["params"], context.params)
        self._resolved_params = merged
        (context.job_dir / "resolved.json").write_text(
            json.dumps(merged, indent=2), encoding="utf-8"
        )
        return merged

    def _checkpoint_path(self, params):
        variant = params.get("_variant")
        subdir = variant if variant else ""
        return self.task_dir / ".state" / subdir / "checkpoint.json"
