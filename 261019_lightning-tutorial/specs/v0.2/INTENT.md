# lightning-tutorial v0.2 기획 의도

## v0.1 대비 변경 방향

v0.2는 v0.1의 순수 PyTorch와 Lightning 분리 원칙을 유지하면서, task별 코드 배치와 이름 규칙, 설정 조합 및 실행 방법을 일관되게 정리하는 것을 목표로 한다. 이 문서는 최초 기획 문서이며, 아래의 폴더 구조와 사용 예시는 구현하려는 형태를 나타낸다. 실제 구현 완료 상태를 뜻하지 않는다.

### Task별 기본 구조와 공통 코드

모든 task는 `src/{task_name}/` 아래에 `configs/`, `data/`, `models/`, `trainers/`의 기본 4개 폴더를 사용한다. 데이터셋과 모델이 달라져도 같은 위치에서 설정·데이터·모델·실행 구성을 찾을 수 있게 한다.

`common/`은 공유하는 구현이 실제로 필요한 범위에만 둔다. 분류 모델들이 공유하는 loss·metric은 `models/common/`에 배치하고, 여러 데이터셋이 공유하는 전처리는 필요할 때 `data/common/`에 배치한다. task 루트나 모든 하위 폴더에 `common/`을 일괄 추가하지 않는다. task별 내부 파일 목록도 동일하게 강제하지 않는다.

### 순수 모델과 Lightning 구성요소의 이름

순수 PyTorch 모델은 `model.py`의 `MLPModel`, `CNNModel`, `STFPMModel`처럼 이름을 정하고, Lightning Wrapper는 `lightning_model.py`의 `MLPLitModel`, `CNNLitModel`, `STFPMLitModel`처럼 `Lit`으로 구분한다. DataModule도 `lightning_data.py`의 `MNISTLitData`, `CIFAR10LitData`처럼 이름을 통일한다.

모델 알고리즘은 순수 모델에 유지하고, 학습·검증·평가·예측 Hook과 optimizer 연결, 단계별 metric 상태 관리는 Lightning Wrapper가 담당한다. Dataset·Transform·loss·metric·전처리·후처리와 독립 추론은 Lightning 없이 사용할 수 있도록 구성한다.

### 학습 실행 구성의 분리

v0.1의 모델별 CLI와 공통 Lightning 연결 배치를 task별 `trainers/` 중심으로 정리한다. `LitTrainer`는 `pl.Trainer`의 인자를 재조립하고, `LitCLI`는 `LightningCLI`의 설정과 클래스 연결을 구성하는 역할로 제한한다. 학습 루프와 명령 실행은 Lightning의 기본 동작을 활용한다.

logger와 callback은 Trainer 생성에 필요한 구성요소이므로 `lightning_trainer.py`에 함께 둔다. 별도의 logger·callback 구성 클래스는 필수로 만들지 않는다. task 간 조립 코드가 같다면 공유할 수 있도록 하되, task별 차이가 설정값뿐인 경우 YAML로 표현한다.

### 설정과 사용 흐름의 통일

설정은 task의 `default.yaml`, 데이터별 YAML, 모델별 YAML, `trainer.yaml`로 구분한다. 공통 → 데이터 → 모델 → Trainer 순서로 병합하고, 뒤에 전달한 값이 앞의 값을 덮어쓰도록 한다. Trainer 실행 옵션과 logger·callback 설정은 `trainer.yaml`에서 관리한다.

Python 사용 예시는 설정 병합 → 시드 설정 → 데이터 생성 → 모델 생성 → Trainer 생성 → 학습 → best 체크포인트 평가의 흐름으로 통일한다. 데이터셋과 모델을 바꿔도 같은 형태로 실행할 수 있게 하며, `LitCLI`를 사용하는 경로도 같은 구성 기준을 따른다.

### 분류 방식과 예제 범위

기존 `classification`은 `num_classes >= 2`인 다중 클래스 분류와 `nn.CrossEntropyLoss`를 기준으로 유지한다. 이 방식은 출력 클래스가 2개인 이진 분류도 표현할 수 있다. 별도 task로 검토하는 `binary_classification`은 출력 하나와 `nn.BCEWithLogitsLoss`를 사용하는 방식으로 구분한다. 이 경우 클래스 수 2와 출력 수 1을 구별하고, 양성 라벨과 예측 임계값을 명시한다. 구체적인 데이터셋과 폴더 구조·사용 예시는 후속 기획에서 정한다.

분류 예제는 MNIST·MLP와 CIFAR-10·CNN으로 같은 실행 패턴을 확인한다. 이상 탐지는 MVTec·STFPM과 VisA·EfficientAD로 확장하는 구성을 계획한다. 공통 기능을 재사용하되 모델별 알고리즘과 필요한 학습 동작은 각 모델에 유지한다.

### 전처리·후처리와 독립 추론

전처리는 데이터 영역, 후처리는 모델 영역에서 책임에 따라 관리한다. 데이터셋 고유 변환은 해당 Dataset·Transform에 두고, 공유할 입력 전처리가 생기면 `data/common/preprocess.py`를 추가한다. task 공통 출력 처리는 `models/common/postprocess.py`, 모델 고유 출력 처리는 해당 모델의 `postprocess.py`에 배치하는 방향으로 검토한다. 실제로 필요한 파일만 추가한다.

학습용 변환과 평가·추론용 변환을 구분하고, 이미 변환된 입력에 전처리를 중복 적용하지 않는다. 모델 알고리즘에 해당하는 anomaly map·score 계산은 모델에 유지하고, 확률·라벨 변환과 임계값 판정 등은 후처리에서 담당한다. Lightning Wrapper와 독립 Predictor는 같은 전처리·후처리 구현을 재사용할 수 있게 연결한다. 정규화 값이나 임계값처럼 학습·검증에서 결정한 상태는 저장하고 추론 시 복원한다.

기존 로컬 데이터와 pretrained 가중치를 활용하고 순수 모델 가중치로 독립 추론하는 v0.1의 방향을 이어간다. 아래 폴더 구조와 사용 예시는 현재 작성한 기획안을 유지하며, 위에서 추가로 검토한 binary classification과 전처리·후처리 파일의 상세 배치는 후속 기획에서 반영한다.

## 폴더 구조

```text
src/
└── {task_name}/
    ├── configs/
    ├── data/
    ├── models/
    └── trainers/
```

### Trainer와 CLI의 역할

- task별 `trainers/`에는 `lightning_trainer.py`와 `lightning_cli.py`를 둔다.
- `lightning_trainer.py`의 `LitTrainer`는 `pl.Trainer`를 상속하고, 설정으로 logger와 callback 객체를 생성해 나머지 Trainer 인자와 함께 전달한다. 학습·검증·평가·예측 실행은 상속받은 Lightning 동작을 사용한다.
- logger와 callback 구성은 `lightning_trainer.py`에 포함한다. 필요하면 같은 파일 안에서 `create_logger()`와 `create_callbacks()` 함수로 나누고, 작은 사용자 callback 클래스도 이 파일에 둔다.
- 별도의 `lightning_logger.py`·`lightning_callback.py`와 `LitLogger`·`LitCallbacks` 클래스는 두지 않는다. callback 구현이 커져 별도 관리가 필요해지면 파일 분리를 검토한다.
- `LitTrainer`는 설정 딕셔너리뿐 아니라 이미 생성된 logger·callback 객체도 받을 수 있도록 구성한다. CLI가 생성한 객체는 그대로 전달한다.
- `lightning_cli.py`의 `LitCLI`는 `lightning.pytorch.cli.LightningCLI`를 상속하고, 모델·DataModule·`LitTrainer` 연결과 설정 파싱·인자 연결·설정 저장 정책을 구성한다. logger와 callback 생성 로직은 중복 구현하지 않는다.

## Classification

```text
src/
└── classification/
    ├── configs/
    │   ├── default.yaml
    │   ├── trainer.yaml
    │   ├── data/
    │   │   ├── mnist.yaml
    │   │   └── cifar10.yaml
    │   └── models/
    │       ├── mlp.yaml
    │       └── cnn.yaml
    ├── data/
    │   ├── mnist/
    │   │   ├── dataset.py            # MNISTDataset, MNISTTransform
    │   │   └── lightning_data.py     # MNISTLitData
    │   └── cifar10/
    │       ├── dataset.py            # CIFAR10Dataset, CIFAR10Transform
    │       └── lightning_data.py     # CIFAR10LitData
    ├── models/
    │   ├── common/
    │   │   ├── metric.py             # ClassificationMetric
    │   │   └── loss.py               # ClassificationLoss
    │   ├── mlp/
    │   │   ├── model.py              # MLPModel
    │   │   └── lightning_model.py    # MLPLitModel
    │   └── cnn/
    │       ├── model.py              # CNNModel
    │       └── lightning_model.py    # CNNLitModel
    └── trainers/
        ├── lightning_trainer.py     # LitTrainer, logger·callback 구성
        └── lightning_cli.py         # LitCLI
```

### Classification - MNIST - MLP

```python
import lightning.pytorch as pl

from src.classification.data.mnist.lightning_data import MNISTLitData
from src.classification.models.mlp.lightning_model import MLPLitModel
from src.classification.trainers.lightning_trainer import LitTrainer
from src.utils.config import merge_config

config = merge_config(
    "src/classification/configs/default.yaml",
    "src/classification/configs/data/mnist.yaml",
    "src/classification/configs/models/mlp.yaml",
    "src/classification/configs/trainer.yaml",
)
pl.seed_everything(config["seed"], workers=True)

data = MNISTLitData(**config["data"])
model = MLPLitModel(**config["model"])
trainer = LitTrainer(**config["trainer"])

trainer.fit(model, data)
trainer.test(model, data, ckpt_path="best", verbose=True)
```

### Classification - CIFAR10 - CNN

```python
import lightning.pytorch as pl

from src.classification.data.cifar10.lightning_data import CIFAR10LitData
from src.classification.models.cnn.lightning_model import CNNLitModel
from src.classification.trainers.lightning_trainer import LitTrainer
from src.utils.config import merge_config

config = merge_config(
    "src/classification/configs/default.yaml",
    "src/classification/configs/data/cifar10.yaml",
    "src/classification/configs/models/cnn.yaml",
    "src/classification/configs/trainer.yaml",
)
pl.seed_everything(config["seed"], workers=True)

data = CIFAR10LitData(**config["data"])
model = CNNLitModel(**config["model"])
trainer = LitTrainer(**config["trainer"])

trainer.fit(model, data)
trainer.test(model, data, ckpt_path="best", verbose=True)
```

## Anomaly Detection

```text
src/
└── anomaly_detection/
    ├── configs/
    │   ├── default.yaml
    │   ├── trainer.yaml
    │   ├── data/
    │   │   ├── mvtec.yaml
    │   │   └── visa.yaml
    │   └── models/
    │       ├── stfpm.yaml
    │       └── efficientad.yaml
    ├── data/
    │   ├── mvtec/
    │   │   ├── dataset.py            # MVTecDataset, MVTecTransform
    │   │   └── lightning_data.py     # MVTecLitData
    │   └── visa/
    │       ├── dataset.py            # VisADataset, VisATransform
    │       └── lightning_data.py     # VisALitData
    ├── models/
    │   ├── common/
    │   │   └── metric.py             # AnomalyMetric
    │   ├── stfpm/
    │   │   ├── model.py              # STFPMModel
    │   │   ├── loss.py               # STFPMLoss
    │   │   └── lightning_model.py    # STFPMLitModel
    │   └── efficientad/
    │       ├── model.py              # EfficientADModel
    │       ├── loss.py               # EfficientADLoss
    │       └── lightning_model.py    # EfficientADLitModel
    └── trainers/
        ├── lightning_trainer.py     # LitTrainer, logger·callback 구성
        └── lightning_cli.py         # LitCLI
```

### Anomaly Detection - MVTec - STFPM

```python
import lightning.pytorch as pl

from src.anomaly_detection.data.mvtec.lightning_data import MVTecLitData
from src.anomaly_detection.models.stfpm.lightning_model import STFPMLitModel
from src.anomaly_detection.trainers.lightning_trainer import LitTrainer
from src.utils.config import merge_config

config = merge_config(
    "src/anomaly_detection/configs/default.yaml",
    "src/anomaly_detection/configs/data/mvtec.yaml",
    "src/anomaly_detection/configs/models/stfpm.yaml",
    "src/anomaly_detection/configs/trainer.yaml",
)
pl.seed_everything(config["seed"], workers=True)

data = MVTecLitData(**config["data"])
model = STFPMLitModel(**config["model"])
trainer = LitTrainer(**config["trainer"])

trainer.fit(model, data)
trainer.test(model, data, ckpt_path="best", verbose=True)
```

### Anomaly Detection - VisA - EfficientAD

```python
import lightning.pytorch as pl

from src.anomaly_detection.data.visa.lightning_data import VisALitData
from src.anomaly_detection.models.efficientad.lightning_model import EfficientADLitModel
from src.anomaly_detection.trainers.lightning_trainer import LitTrainer
from src.utils.config import merge_config

config = merge_config(
    "src/anomaly_detection/configs/default.yaml",
    "src/anomaly_detection/configs/data/visa.yaml",
    "src/anomaly_detection/configs/models/efficientad.yaml",
    "src/anomaly_detection/configs/trainer.yaml",
)
pl.seed_everything(config["seed"], workers=True)

data = VisALitData(**config["data"])
model = EfficientADLitModel(**config["model"])
trainer = LitTrainer(**config["trainer"])

trainer.fit(model, data)
trainer.test(model, data, ckpt_path="best", verbose=True)
```
