# lightning-tutorial 프로젝트 의도

## 목적

기존 `D:\projects\dl-lightning`의 목적을 바탕으로 현재 폴더에서 프로젝트를 처음부터 다시 구성한다. `cv_boilerplate`의 순수 PyTorch 모델과 데이터 처리·독립 추론 코드를 유지하면서, 학습·검증·평가·예측 실행을 Lightning native 구현으로 구성한다.

핵심은 순수 PyTorch 모델 파일과 Lightning Wrapper 파일을 완전히 분리하는 것이다. 모델의 알고리즘과 입출력 동작은 최대한 보존하고, 학습 프레임워크의 책임은 별도 Wrapper와 실행 계층에 둔다.

작은 예제부터 구현하고 실행 결과와 사용자 피드백을 바탕으로 확장한다. 기존 프로젝트의 코드와 설계를 일괄 복사하지 않고, 필요한 구성요소를 검토하며 다시 작성한다.

## 기본 원칙

- 네트워크, Dataset, DataLoader, transform, loss, metric, 공통 후처리와 Predictor는 순수 PyTorch 영역으로 유지한다. 이 영역은 Lightning을 import하거나 설치를 요구하지 않는다.
- 모델별 LightningModule에서 순수 PyTorch 구성요소를 연결하고 학습·검증·평가·예측 단계를 구현한다.
- 모델별 LightningCLI를 실행 진입점으로 사용하고 Lightning의 Trainer와 설정 기능을 활용한다.
- 공통 Predictor는 순수 PyTorch 모델과 가중치로 독립 추론을 수행한다. LightningModule이나 Trainer를 요구하지 않는다.
- 기존 로컬 데이터셋과 pretrained 가중치를 재사용하며 원본을 수정하거나 프로젝트로 복사하지 않는다.
- 실제로 필요한 코드와 폴더만 작성한다. 아래 구조의 모든 task와 모델을 처음부터 구현하지 않는다.

## 코드 배치

`src` 바로 아래에 task별 폴더를 둔다. 공통 추론과 유틸리티는 task 폴더와 같은 수준에 둔다. 아래는 설계상 배치 기준이다. 사용자 수동 정리 후 실제 파일 목록은 루트 [README.md](../../README.md)를 따른다. 현재 모델별 CLI와 공통 Lightning 연결 파일은 없다.

```text
src/
├── {task_name}/                     # classification, anomaly_detection, gan
│   ├── configs/
│   │   ├── default.yaml
│   │   ├── data/
│   │   │   └── {dataset_name}.yaml
│   │   └── models/
│   │       └── {model_name}.yaml
│   ├── data/
│   │   └── {dataset_name}/          # mvtec, visa, btad 등
│   │       ├── dataset.py
│   │       └── transform.py
│   └── models/
│       └── {model_name}/            # stfpm, efficientad 등
│           ├── model.py
│           ├── loss.py
│           ├── metric.py
│           ├── lightning_module.py
│           └── lightning_cli.py
├── inference/
│   └── predictor.py
└── utils/
    ├── io.py
    ├── config.py
    ├── lightning_data.py           # 공통 Lightning 데이터 연결
    └── lightning_cli.py            # 공통 Lightning 실행 연결
```

순수 PyTorch 코드와 Lightning 코드는 파일 단위로 분리한다. 같은 모델 폴더에 배치하더라도 `model.py`·`loss.py`·`metric.py`에서 Lightning 구현을 참조하지 않는다.

### 분리의 기준

- `model.py`는 순수 `nn.Module`로 작성한다. 모델의 `forward()`에 Lightning Hook이나 학습 실행 제어를 넣지 않는다.
- `lightning_module.py`는 순수 모델을 감싸는 Wrapper다. 학습·검증·평가·예측 Hook, optimizer 연결, metric 집계와 로깅 등 Lightning의 책임을 담당한다. 모델 알고리즘을 Wrapper에 중복 구현하지 않는다.
- Wrapper는 외부에서 전달받은 모델·loss 등 필요한 구성요소를 연결한다. 구체 객체의 생성과 조립은 CLI 또는 설정에서 수행하고, 데이터는 Dataset·DataLoader 등 PyTorch 표준 객체로 연결한다.
- 순수 PyTorch 영역을 import할 때 패키지 초기화를 통해 Lightning이 자동으로 import되지 않게 한다.
- 독립 추론은 순수 모델의 `state_dict`로 복원한다. Lightning 체크포인트를 변환하는 책임은 Lightning 측 또는 별도 연결 코드에 둔다.
- 파일을 나누는 것에 더해 실행 의존성도 분리한다. Lightning 없이 모델·데이터·변환·Predictor를 사용할 수 있어야 한다.

## 설정의 역할

### Python과 로컬 자산

- Python 실행 파일은 `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe`를 사용한다.
- Python 실행과 패키지 확인·설치에는 위 실행 파일을 명시한다. pip는 해당 실행 파일의 `-m pip`로 호출한다.
- pretrained 가중치는 `E:\backbones`에 있는 로컬 파일을 사용한다.
- 데이터셋은 `E:\datasets`에 있는 로컬 파일을 사용한다.
- 위 두 경로는 사용자가 지정한 자산 위치다. CIFAR-10·MVTec의 하위 폴더와 ResNet50·STFPM에 사용할 가중치 파일명은 구현 전에 실제 목록을 확인한다.
- 원본 자산을 수정하거나 프로젝트 폴더로 복사하지 않고 설정에서 해당 경로를 참조한다.

### 설정 파일

- `configs/default.yaml`: task의 공통 기본 설정.
- `configs/data/{dataset_name}.yaml`: 데이터셋 경로, transform, 데이터 로딩 등 데이터별 설정.
- `configs/models/{model_name}.yaml`: 모델과 해당 모델의 학습에 필요한 설정.

native LightningCLI의 반복 `--config`로 공통 → 데이터 → 모델 YAML 순서로 결합하고 마지막 CLI 인자로 덮어쓰는 것을 설계 기준으로 한다. 현재 CLI 파일은 없다. 파일 현황과 확인한 환경은 [README.md](../../README.md), 구체적인 데이터 연결과 산출물 규칙은 [DECISIONS.MD](DECISIONS.MD)에 기록한다.

## 초기 구현 범위

다음 두 예제를 초기 구현 대상으로 한다. task 폴더 이름은 `classification`과 `anomaly_detection`을 사용한다.

| Task | 데이터셋 | 모델 | 참조 프로젝트 |
| --- | --- | --- | --- |
| `classification` | CIFAR-10 | ResNet50 | `D:\projects\dl-lightning` |
| `anomaly_detection` | MVTec | STFPM | `D:\projects\_clones\cv_boilerplate` |

### CIFAR-10 · ResNet50

- 데이터 코드는 `src/classification/data/cifar10/`, 모델·loss·metric·Lightning Wrapper는 `src/classification/models/cnn/`에 둔다.
- 설정은 `src/classification/configs/default.yaml`, `data/cifar10.yaml`, `models/cnn.yaml`로 나눈다.
- 기존 `dl-lightning`의 CIFAR-10 Dataset·transform·DataLoader와 CNN `ClassificationModel`을 참조한다. `custom`, `resnet18`, `resnet50`, `efficientnet_b0`를 지원하고 기본값과 초기 노트북은 `backbone="resnet50"`을 사용한다.
- 기존 Lightning Wrapper·DataModule·CLI를 참고하되, 현재 프로젝트의 모델별 `lightning_module.py`·`lightning_cli.py` 배치에 맞게 구성한다.

### MVTec · STFPM

- 데이터 코드는 `src/anomaly_detection/data/mvtec/`, 모델 코드는 `src/anomaly_detection/models/stfpm/`에 둔다.
- 설정은 `src/anomaly_detection/configs/default.yaml`, `data/mvtec.yaml`, `models/stfpm.yaml`로 나눈다.
- 참조 원본의 `src/tasks/anomaly/models/stfpm.py`와 `configs/anomaly/stfpm.yaml`을 기준으로 모델과 학습 설정을 검토한다.
- STFPM의 상위 참조 원본은 [anomalib STFPM](https://github.com/open-edge-platform/anomalib/tree/main/src/anomalib/models/image/stfpm)이다. 사용자는 기존 `cv_boilerplate`의 STFPM을 작성할 때 anomalib의 `torch_model.py`를 순수 PyTorch 수준에서 최대한 유지했다.
- 새 `model.py`도 anomalib의 [torch_model.py](https://github.com/open-edge-platform/anomalib/blob/main/src/anomalib/models/image/stfpm/torch_model.py)와 기존 구현을 함께 참조해 모델 구조와 연산·입출력 동작을 최대한 보존한다. Lightning과 독립적으로 사용할 수 있도록 필요한 의존성과 입출력 연결만 조정한다.
- 새 `lightning_module.py`는 anomalib의 [lightning_model.py](https://github.com/open-edge-platform/anomalib/blob/main/src/anomalib/models/image/stfpm/lightning_model.py)를 최대한 참조해 작성한다. 모델별 학습·검증 흐름과 optimizer 구성을 참고하면서 프로젝트의 native Lightning Wrapper로 구현한다.
- anomalib 코드는 모델 알고리즘과 Wrapper 동작의 참조 원본이다. 해당 파일의 anomalib 전용 기반 클래스·배치 형식·실행 계층을 그대로 도입하는 것으로 해석하지 않는다. 필요한 연결 변경은 순수 PyTorch와 Lightning의 분리 원칙을 따른다.
- 같은 task의 `dataset.py`, `transform.py`, `metric.py`, `postprocess.py` 등 관련 코드를 검토하고 필요한 기능을 현재 구조에 맞게 배치한다.
- 원본의 학습 실행 계층은 LightningModule과 LightningCLI로 구성한다. 초기 예제는 MVTec bottle의 원본 폴더를 읽고 JSON 없이 valid·test를 분리하며 image AUROC·pixel AUROC로 평가한다.

참조 프로젝트는 읽기 전용으로 사용한다. 기존 폴더 구조나 실행 프레임워크를 그대로 이식하지 않고 두 예제에 필요한 구현을 재사용한다. `gan`, `visa`, `btad`, `efficientad` 등은 향후 확장을 위한 배치 예시로 남긴다.

목적과 분리 원칙은 기존 `D:\projects\dl-lightning\AGENTS.md`와 `README.md`를 참조한다. 기존의 `src/torch`·`src/lightning` 폴더 구분은 현재 요청한 task 중심 배치로 대체하되, 두 영역의 책임과 의존성 분리 원칙은 유지한다.

## 구현 시 확인할 결과

- 선택한 task·데이터셋·모델로 학습과 검증을 실행할 수 있다.
- 저장한 가중치를 복원해 평가와 예측을 실행할 수 있다.
- 순수 PyTorch 모델과 공통 Predictor로 Lightning 없이 추론할 수 있다.
- 학습용 변환과 평가·추론용 변환을 구분하고 중복 적용하지 않는다.
- 사용한 설정, 학습 결과, 가중치를 로컬 파일로 확인할 수 있다.

## 진행 방식

이 문서는 목적과 코드 배치 원칙을 유지한다. 구현 결정은 [DECISIONS.MD](DECISIONS.MD), 현재 구조와 검증 범위는 [README.md](../../README.md), 진행 상태는 [PLAN.MD](PLAN.MD)에 기록한다. 코드는 사용자 요청에 따라 작은 단위로 작성하고 실행 확인과 피드백을 거쳐 개선한다.

Markdown 문서는 UTF-8로 저장하고 한글 인코딩을 확인한다. 문서와 코드 설명에 이모지를 사용하지 않는다.
