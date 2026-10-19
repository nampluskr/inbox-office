# lightning-tutorial

순수 PyTorch 모델과 데이터 처리·독립 추론을 유지하면서 학습·검증·평가·예측을 Lightning native로 구성하는 예제 프로젝트다. 모델 알고리즘은 `model.py`, 학습 실행 Hook은 `lightning_module.py`에 분리한다.

## 문서

| 문서 | 역할 |
| --- | --- |
| [INTENT.MD](specs/v0.1/INTENT.MD) | 목적과 설계 원칙 |
| [AGENTS.md](AGENTS.md) | 작업 지침 |
| [PLAN.MD](specs/v0.1/PLAN.MD) | 구현 계획과 현재 상태 |
| [DECISIONS.MD](specs/v0.1/DECISIONS.MD) | 구현 결정과 참조 확인 이력 |
| [Apache-2.0.txt](specs/v0.1/licenses/Apache-2.0.txt) | 보관 중인 라이선스 원문 |

## 수동 정리 직후 확인 기록

2026-10-19 수동 정리 직후 폴더와 파일 목록을 확인했다. 아래 기록은 당시 현황이다. 이후 작성된 노트북과 CNN 통합의 현재 구성은 아래 각 절을 따른다. CIFAR-10·ResNet50과 MVTec·STFPM의 모델·loss·metric·Lightning Wrapper, Dataset·transform, YAML 설정, 공통 Predictor와 순수 유틸리티가 남아 있었다.

- 모델별 `lightning_cli.py`와 공통 `src/utils/lightning_cli.py`, `src/utils/lightning_data.py`는 없다.
- `notebooks/`와 `outputs/`는 비어 있다. 이전 노트북·체크포인트·검증 보고서는 현재 없다.
- `specs/v0.1/README.md`, `THIRD_PARTY_NOTICES.md`, `references.json`은 없다. 프로젝트 안내는 루트 README에서 관리한다.
- 여러 Python 패키지와 `tests/`에 `__pycache__`가 남아 있다. 없는 CLI·DataModule 소스에 대응하는 `.pyc`도 남아 있으므로 캐시를 구현 현황으로 간주하지 않는다.
- `.git`이 없어 Git 이력 기준으로 삭제·변경 목록을 비교할 수 없다.

이번 확인은 파일과 폴더의 존재 여부를 대상으로 했다. 정리 후 모델 실행·학습·평가·테스트와 환경 확인은 수행하지 않았다.

## 폴더 구조와 파일 목록

`__init__.py`와 `__pycache__`는 생략했다. 코드와 노트북 구조에는 이후 CNN 통합 변경을 반영했다. `outputs/`의 실행별 산출물은 생략했다. `__init__.py`는 `src/`, 각 task·data·dataset·models·model 패키지, `src/inference/`, `src/utils/`, `tests/`에 있다.

```text
lightning-tutorial/
├── .gitignore
├── AGENTS.md
├── README.md
├── notebooks/
│   ├── classification-cifar10-resnet50.ipynb
│   └── anomaly-mvtec-stfpm.ipynb
├── outputs/
├── specs/
│   └── v0.1/
│       ├── DECISIONS.MD
│       ├── INTENT.MD
│       ├── PLAN.MD
│       └── licenses/Apache-2.0.txt
├── src/
│   ├── classification/
│   │   ├── configs/
│   │   │   ├── default.yaml
│   │   │   ├── data/cifar10.yaml
│   │   │   └── models/cnn.yaml
│   │   ├── data/cifar10/
│   │   │   ├── dataset.py
│   │   │   └── transform.py
│   │   └── models/cnn/
│   │       ├── model.py
│   │       ├── loss.py
│   │       ├── metric.py
│   │       └── lightning_module.py
│   ├── anomaly_detection/
│   │   ├── configs/
│   │   │   ├── default.yaml
│   │   │   ├── data/mvtec.yaml
│   │   │   └── models/stfpm.yaml
│   │   ├── data/mvtec/
│   │   │   ├── dataset.py
│   │   │   └── transform.py
│   │   └── models/stfpm/
│   │       ├── model.py
│   │       ├── loss.py
│   │       ├── metric.py
│   │       └── lightning_module.py
│   ├── inference/predictor.py
│   └── utils/
│       ├── config.py
│       └── io.py
└── tests/
    ├── run_notebooks.py
    └── test_examples.py
```

## 실행 환경과 로컬 자산

| 항목 | 지정 위치 |
| --- | --- |
| 작업 폴더 | `D:\projects\lightning-tutorial` |
| Python | `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe` |
| 데이터셋 | `E:\datasets` |
| pretrained 가중치 | `E:\backbones` |

Python 실행과 패키지 확인·설치에는 지정 실행 파일을 명시하고 pip는 해당 Python의 `-m pip`로 호출한다. 데이터와 가중치는 자동 다운로드하지 않는다.

기존 문서에 기록된 로컬 자산은 다음과 같다. 이번 문서 갱신에서 외부 자산의 존재 여부는 다시 확인하지 않았다.

- CIFAR-10: `E:\datasets\cifar10\cifar-10-batches-py`
- MVTec bottle: `E:\datasets\mvtec\bottle`
- ResNet50 pretrained: `E:\backbones\resnet50-0676ba61.pth`
- STFPM teacher pretrained: `E:\backbones\resnet18-f37072fd.pth`
- MVTec 분할: 원본 폴더를 읽고 노트북에서 seed 42로 정상·이상별 valid 40%·test 60%를 분리한다. JSON 파일은 사용하지 않는다.

정리 전 환경 확인 기록은 Python 3.11.8, PyTorch 2.2.1+cu118, torchvision 0.17.1+cu118, Lightning 2.5.5, jsonargparse 4.40.2, torchmetrics 1.9.0, PyYAML 6.0.3, NVIDIA RTX A4000의 CUDA 사용 가능 상태다. 이번 문서 갱신에서는 패키지를 변경하거나 환경을 재검증하지 않았다.

## CNN 분류 모델

`src.classification.models.cnn.model.ClassificationModel`은 `backbone="resnet50"`을 기본값으로 사용한다. `custom`, `resnet18`, `resnet50`, `efficientnet_b0`를 지원하며 loss·metric·Lightning Wrapper도 `cnn/`에 둔다. 모델 설정은 `src/classification/configs/models/cnn.yaml`이다. 이전 `resnet50` 패키지와 설정 파일은 새 경로로 대체했다.

```python
from src.classification.models.cnn.model import ClassificationModel

model = ClassificationModel(
    backbone="resnet50",
    num_classes=10,
    weights_path="E:/backbones/resnet50-0676ba61.pth",
)
```

torchvision backbone은 자동 다운로드 없이 생성한다. 지정한 로컬 ImageNet 가중치를 원래 분류층에 로드한 뒤 클래스 수에 맞게 분류층을 교체한다. `weights_path=None`은 무작위 초기화 또는 학습 가중치의 별도 복원에 사용한다. 지정 경로가 없거나 가중치 구조가 다르면 오류를 표시한다. `custom`에는 backbone 가중치를 전달할 수 없다.

기존 ResNet50의 `backbone.*` 파라미터 이름을 유지하므로 같은 클래스 수의 순수 `state_dict`를 새 모델에 복원할 수 있도록 구성했다. 이번 변경에서는 코드 참조와 형식을 확인했으며 모델 import·forward·가중치 복원·Lightning 학습·테스트는 실행하지 않았다. 지정 Python 환경과 패키지도 재검증하거나 변경하지 않았다.

## 노트북

- [classification-cifar10-resnet50.ipynb](notebooks/classification-cifar10-resnet50.ipynb): CIFAR-10 Dataset 분할과 Lightning 학습 예제.
- [anomaly-mvtec-stfpm.ipynb](notebooks/anomaly-mvtec-stfpm.ipynb): MVTec 원본 폴더를 읽고 JSON 없이 정상·이상별로 valid·test를 분리하는 STFPM 학습 예제.

MVTec Dataset은 `train=True`로 정상 학습 데이터를, `train=False`로 전체 평가 데이터를 읽는다. 노트북에서 seed 42와 `VALID_RATIO=0.4`로 원본 test를 나눠 각각 `Subset`으로 연결한다. `mvtec.yaml`의 valid·test Dataset은 분리 전 소스이므로 YAML만 직접 연결하면 평가 데이터가 겹친다. 분할은 노트북에서처럼 외부에서 한 번 수행해야 한다. 이번 MVTec 변경 후 학습과 테스트는 실행하지 않았다.

## 실행 안내와 검증 범위

모델별 CLI와 공통 Lightning 연결 파일이 없어 기존 `fit`, `validate`, `test`, `predict` 모듈 명령은 현재 사용할 수 없다. 예전 이름의 노트북 실행 명령은 현재 사용 안내에서 제외했다. YAML 파일이 남아 있는 것만으로 실행 연결이 완성된 상태는 아니다.

`tests/test_examples.py`에는 없는 `src.utils.lightning_cli.export_weights`와 `outputs/verification_*`의 산출물을 사용하는 검증이 있다. `tests/run_notebooks.py`의 기존 실행 대상 노트북도 없다. 남아 있는 검증 코드 전체가 현재 상태에서 통과한다고 볼 수 없다.

정리 전 문서에는 두 모델의 batch size 2·학습 2배치·1 epoch 실행, CIFAR-10 검증·평가·예측 각 2배치, STFPM 검증 33개·평가 50개·예측 2배치, 8개 테스트 통과와 노트북 코드 셀 실행이 기록되어 있었다. 이 기록은 [PLAN.MD](specs/v0.1/PLAN.MD)에 이력으로 보존하며 현재 파일 상태의 검증 결과로 간주하지 않는다.

공통 Predictor는 순수 모델의 `state_dict`를 복원하는 용도다. 이전 체크포인트 변환 함수 `src.utils.lightning_cli.export_weights`는 현재 없다. 이전 `best.ckpt`, `last.ckpt`, `model.pt`, 설정·CSV·metric JSON·예측 결과도 비어 있는 `outputs/`에 존재하지 않는다.

전체 학습 성능, 다중 장치, 다른 MVTec 범주와 전체 anomalib 런타임 대비 수치 동등성은 기존 검증 범위에도 포함되지 않았다. 참조 구현과 차이는 [DECISIONS.MD](specs/v0.1/DECISIONS.MD)에 기록되어 있다.
