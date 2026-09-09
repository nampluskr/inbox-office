# tasks/classification/src/classification_task/adapters/resnet_mock.py
#
# 이 model 전용 Adapter. task.toml이 가리키는 건 이 파일이 아니라
# registry.py다 - task-runner의 source 로딩 절차가 job의 params.model.name으로
# registry.py의 MODEL_REGISTRY를 조회해 이 클래스를 직접 골라 사용한다.

from task_runner.adapter.base import BaseAdapter

from ..models.resnet_mock import ResnetMock


class ResnetMockAdapter(BaseAdapter):
    def prepare_train(self, context):
        params = self._resolve_params(context)
        self._model = ResnetMock(backbone=params["model"]["backbone"])
        self._optimizer = self._model.configure_optimizer(params["optimizer"])
        self._scheduler = self._model.configure_scheduler(params["scheduler"], self._optimizer)

    def train_data(self, context):
        return self._model.build_dataloader(self._resolved_params["data"], split="train")

    def train_step(self, batch, context):
        return self._model.train_step(batch, self._optimizer)

    def prepare_evaluate(self, context):
        params = self._resolve_params(context)
        self._model = ResnetMock(backbone=params["model"]["backbone"])
        self._model.load_checkpoint(self._checkpoint_path(params))

    def validate_data(self, context):
        return self._model.build_dataloader(self._resolved_params["data"], split="valid")

    def evaluate_data(self, context):
        return self._model.build_dataloader(self._resolved_params["data"], split="test")

    def eval_step(self, batch, context):
        return self._model.eval_step(batch)

    def reset_metrics(self, context):
        self._model.reset_metrics(self._resolved_params["metric"])

    def update_metrics(self, step_result, context):
        self._model.update_metrics(step_result)

    def compute_metrics(self, context):
        return self._model.compute_metrics()

    def prepare_predict(self, context):
        params = self._resolve_params(context)
        self._model = ResnetMock(backbone=params["model"]["backbone"])
        self._model.load_checkpoint(self._checkpoint_path(params))

    def predict_data(self, context):
        return self._model.build_dataloader(self._resolved_params["data"], split="predict")

    def predict_step(self, batch, context):
        return self._model.predict_step(batch)
