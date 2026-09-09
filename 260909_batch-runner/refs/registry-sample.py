# tasks/classification/src/classification_task/registry.py
#
# task.toml의 task.registry가 가리키는 파일. task-runner의 source 로딩
# 절차는 job의 params.model.name으로 이 dict를 조회해 해당 Adapter
# 클래스를 바로 import해서 쓴다. 선택 항목이 2개 이상인 구성요소의
# *_REGISTRY dict를 전부 여기에 모은다.

from .adapters.resnet_mock import ResnetMockAdapter
from .adapters.efficientnet_mock import EfficientnetMockAdapter

MODEL_REGISTRY = {
    "resnet_mock": ResnetMockAdapter,
    "efficientnet_mock": EfficientnetMockAdapter,
}
