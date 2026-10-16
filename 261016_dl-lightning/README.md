# dl-lightning

가장 큰 목적은 `D:\projects\_clones\cv_boilerplate`의 순수 PyTorch 기반 학습·평가 실행 구현을 Lightning native 구현으로 대체하는 것이다. 기존 모델·Dataset·DataLoader·변환·후처리·독립 Predictor는 순수 PyTorch로 유지하고, 학습 프레임워크의 책임을 Lightning 영역으로 분리한다.

첫 구현 대상은 CIFAR-10 classification이며, 기능별 코드는 사용자 요청에 따라 작성한다. 원본 전체를 복사하거나 모든 기능을 한 번에 이식하지 않는다.

## 진행 방식

- 작업 위치는 `D:\projects\dl-lightning`이다.
- 이 프로젝트는 project-workflow 절차를 적용하지 않는다.
- 사용자 요청에 따라 코드를 작성하고, 사용자 평가와 피드백을 받아 반복 개선한다.
- 참고 문서의 전체 지원 범위를 한 번에 구현하지 않는다. 현재 사용자 요청을 우선한다.
- 에이전트 작업 지침은 [AGENTS.md](AGENTS.md)를 따른다.

## 작업환경

| 항목 | 지정 경로 또는 방침 |
| --- | --- |
| Python 실행 파일 | `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe` |
| 데이터셋 기본 경로 | `E:\datasets` |
| pretrained backbone 가중치 | `E:\backbones` |
| 첫 예제 대상 | 로컬 CIFAR-10 분류 |
| Lightning | `lightning==2.5.5`, `pytorch-lightning==2.5.5` 설치 완료 |
| LightningCLI 의존성 | `jsonargparse[signatures]==4.40.2` 설치 완료 |

Python 실행과 패키지 관리에는 위 실행 파일을 명시적으로 사용한다. 패키지는 해당 Python의 `-m pip`로 관리한다. 패키지 변경 시 기존 PyTorch·torchvision·CUDA 및 관련 의존성 상태를 확인한다.

확인한 환경은 Python 3.11.8, PyTorch 2.2.1+cu118, torchvision 0.17.1+cu118이며 CUDA를 사용할 수 있다. CIFAR-10은 `E:\datasets\cifar10\cifar-10-batches-py`, 사용 가능한 ResNet18 가중치는 `E:\backbones\resnet18-f37072fd.pth`에 있다. 원본 자산은 해당 위치에서 재사용한다.

2026-10-16에 지정 WinPython의 `Lib/site-packages`에 Lightning과 CLI 의존성을 설치했다. 설치 전 `pip install --dry-run`으로 변경 항목을 확인하고, PyTorch 2.2.1+cu118·torchvision 0.17.1+cu118·torchmetrics 1.9.0은 기존 버전을 유지했다.

- Lightning 2.5.5, pytorch-lightning 2.5.5, jsonargparse 4.40.2 버전을 확인했다.
- `LightningCLI`, 프로젝트의 `ClassificationModule`, 변경 전 데이터 클래스의 import가 성공했다. 현재 데이터 클래스명은 `ClassificationData`이며 이름 변경 후 import 실행은 하지 않았다.
- CUDA 빌드 버전은 11.8이며 `torch.cuda.is_available()`은 True, GPU 수는 1이다.
- 설치 전후 `pip check` 결과는 동일하다. 기존 Jupyter 관련 의존성인 `psutil`과 `python-dateutil`이 누락되어 있으며 이번 설치로 새로 발생한 의존성 문제는 없다.

이번 확인 범위는 패키지 설치·import·CUDA 상태다. 학습·추론, YAML을 통한 CLI 객체 생성, 프로젝트 테스트 실행은 후속 요청으로 진행한다.

## 참고 문서

참고 위치는 `D:\projects\_ideas\pytorch-lightning-ignite`다. 구현 작업은 `dl-lightning`에서 진행하고 참고 문서는 원래 위치에서 읽는다.

| 문서 | 참고할 내용 |
| --- | --- |
| [cv_boilerplate/AGENTS.md](../_clones/cv_boilerplate/AGENTS.md) | 원본 프로젝트의 Python 코딩 규칙 |
| [cv_boilerplate/CLAUDE.md](../_clones/cv_boilerplate/CLAUDE.md) | 원본 지침 요약 |
| [cv_boilerplate classification](../_clones/cv_boilerplate/src/tasks/classification) | 모델·Dataset·transform의 실제 구현 스타일 |
| [INTENT.md](../_ideas/pytorch-lightning-ignite/INTENT.md) | 프로젝트 목적과 기본 원칙 |
| [DECISIONS.md](../_ideas/pytorch-lightning-ignite/DECISIONS.md) | 사용자가 확정한 설계 방향 |
| [BRIEF.md](../_ideas/pytorch-lightning-ignite/BRIEF.md) | 전체 지원 방향, 범위와 검증 기준 |
| [refs/README.md](../_ideas/pytorch-lightning-ignite/refs/README.md) | 주제별 상세 검토 문서 안내 |

참고 문서의 구현 제안이나 미정 사항을 사용자 확정 요구로 간주하지 않는다. 참고 문서에 기재된 project-workflow 절차 대신 이 프로젝트의 진행 방식을 적용한다.

## 구현 방향

- Lightning native `LightningModule`, `Trainer`, `LightningDataModule`, 실제 `LightningCLI`를 활용한다.
- 기존 순수 PyTorch 모델을 Wrapper에 전달하고 Dataset/DataLoader와 변환을 재사용한다.
- native 학습·검증·평가·예측 기능을 유지한다. 후처리는 순수 PyTorch 코드로 공유하고 독립 추론은 Lightning 없이 실행할 수 있게 한다.
- Lightning 구현과 검증을 먼저 진행하고 Ignite는 후속 요청에 따라 다룬다.
- 코드는 `src/torch`와 `src/lightning`으로 분리하고, LightningCLI 진입점은 `src/lightning/tasks/classification/main.py`에 둔다.

## 폴더 구조

다음은 전체 배치 기준이다. 예시 파일과 폴더는 해당 구현이 필요할 때 생성한다. 문서는 `docs`, 검증 코드는 `tests`, 실험 노트북은 `notebooks`, 실행 산출물은 `outputs`에 둔다.

```text
src/torch/
├── tasks/
│   └── {task_name}/
│       ├── configs/                 # mnist.yaml, cifar10.yaml, oxford_pets.yaml
│       ├── data/
│       │   └── {dataset_name}/
│       │       ├── dataset.py
│       │       ├── dataloader.py
│       │       └── transform.py     # Dataset 전용 변환이 필요한 경우
│       ├── transforms/              # Task 공통 transform
│       ├── models/
│       │   └── {model_name}/        # cnn, mlp 등
│       │       ├── model.py
│       │       ├── preprocessor.py
│       │       ├── postprocessor.py
│       │       ├── loss.py          # 모델 전용 구현이 필요한 경우
│       │       └── metric.py        # 모델 전용 구현이 필요한 경우
│       ├── losses/
│       ├── metrics/
│       ├── preprocessors/
│       └── postprocessors/
├── inference/
│   └── predictor.py
└── utils/
    ├── config.py
    ├── seed.py
    └── io.py

src/lightning/
└── tasks/
    └── {task_name}/
        ├── configs/                 # cifar10.yaml 등
        ├── taskmodule.py
        ├── datamodule.py
        └── main.py                  # CLI
```

현재는 classification의 CIFAR-10·Oxford Pets Dataset과 전용 transform, `models/cnn/model.py`, 공통 `preprocessors/classification.py`·`postprocessors/classification.py`, 기존 YAML과 Lightning Wrapper·DataModule을 이 구조로 배치했다. 생성자 및 동작은 유지하며, Lightning 클래스는 `ClassificationModule`과 `ClassificationData`이다. 현재 전처리·후처리는 모델 전용이 아닌 분류 공통 구현으로 둔다.

MNIST·MLP·공통 transform·Loss·Metric·모델 전용 처리·seed/io 유틸리티·CLI는 아직 구현하지 않았다. 이들을 위한 빈 폴더도 생성하지 않는다. 필요한 패키지에는 `__init__.py`를 둔다.

### 데이터 기본값과 YAML 재정의 방향

- 사용할 Dataset별 Loader 클래스는 YAML에서 명시하고, 생략한 인자는 해당 클래스의 기본값을 사용한다.
- Dataset별 `dataloader.py`는 데이터 경로·학습/평가 transform·분할·배치·worker 설정의 기본 구성을 제공한다. YAML에는 변경할 값만 명시할 수 있게 한다.
- Task의 DataModule은 단계별 Loader를 Lightning Hook에 연결하며, 생략한 설정으로 Loader의 기본값을 덮어쓰지 않는다.
- Dataset별 분할과 transform 적용은 한 곳에서 담당한다. 학습·평가 데이터가 겹치거나 resize·정규화가 중복 적용되지 않게 한다.
- 아직 기본 경로가 확정되지 않은 필수 입력은 명시적으로 받는다. 현재 Oxford Pets의 `split_path`는 필수다.
- Dataset별 DataLoader를 구현했다. 기존 YAML은 Dataset 주입 방식을 유지하며, Loader를 직접 전달할 때는 DataModule의 `valid_size=None`을 사용해 중복 분할을 피한다. DataModule은 전달된 Loader의 기본값을 변경하지 않는다.

[cifar10.yaml](src/torch/tasks/classification/configs/cifar10.yaml)과 [oxford_pets.yaml](src/torch/tasks/classification/configs/oxford_pets.yaml)은 공통 `seed_everything`, `model`, `data`, `optimizer` 섹션을 사용하며 순수 PyTorch 모델·Loss·전처리·후처리·Dataset·transform·DataLoader 설정만 담는다. Lightning Wrapper·DataModule 클래스 경로, Trainer·Logger·Callback·출력 경로는 포함하지 않는다. 독립 Predictor도 필요한 순수 객체 설정을 읽어 재사용할 수 있다.

향후 CLI에서 `LightningCLI(ClassificationModule, ClassificationData)`처럼 클래스를 직접 지정하면 `model`·`data` 바로 아래 설정이 해당 클래스의 생성자 인자가 된다. 순수 모델의 위치는 `model.model`이며, 객체별 `class_path`·`init_args`는 순수 PyTorch 객체에만 사용한다. Wrapper와 DataModule은 코드 작성과 import 확인을 마쳤으며, CLI 진입점은 아직 구현 전이다. 패키지 설치는 완료했으며 학습·추론 실행과 YAML 파싱 검증은 후속 작업이다. 이전 순수 PyTorch 검증 결과가 이번 Lightning 코드의 동작을 보장하지는 않는다.

CIFAR-10은 `data.valid_size: 5000`으로 학습 원본을 분할한다. Oxford Pets는 JSON에서 이미 분리된 Dataset을 사용하므로 `valid_size: null`로 추가 분할을 생략한다. Oxford Pets의 split 경로는 프로젝트 루트 기준 `../_clones/cv_boilerplate/configs/splits/oxford_pets.json`이며, 원본 파일을 수정하거나 복사하지 않는다. 전체 split 크기는 train 3,129개·valid 551개·test 3,669개다. 실행 장치·학습 횟수·체크포인트·로그·출력 경로는 향후 Lightning 실행 계층에서 설정한다.

향후 구현할 LightningCLI 기반 평가는 `src/lightning/tasks/classification/main.py`의 `validate`, `test`, `predict` 명령을 활용한다. 평가 전용 파일이 필요하면 `src/lightning` 안에 둔다. Lightning 없이 실행하는 독립 평가 진입점은 필요 시 `src/torch`에 둔다.

내부 모듈은 `src.torch.*`, `src.lightning.*`로 참조하며, 향후 CLI 구현 시 프로젝트 루트에서 `python -m src.lightning.tasks.classification.main` 형태로 실행한다. 설치 패키지와 이름이 충돌하지 않도록 `src`를 `PYTHONPATH`에 추가하지 않는다.

실행마다 구분되는 `{run_id}`를 사용하고, 그 아래에는 하위 폴더 없이 모든 산출물을 저장한다. `best.ckpt`·`last.ckpt`는 Lightning 체크포인트, `model.pt`는 순수 모델 가중치, `history.csv`는 학습 히스토리, `metrics.json`은 최종 평가 결과의 예시다. Logger와 Callback도 이 저장 규칙을 따르도록 설정한다. pretrained 원본 가중치는 `E:\backbones`에 유지한다.

## PyTorch와 Lightning의 분리

두 영역은 파일과 모듈을 완전히 분리하고, 각 영역의 구체 구현을 독립적으로 교체할 수 있게 한다.

| 영역 | 포함할 구성요소 |
| --- | --- |
| 순수 PyTorch | 네트워크 `nn.Module`, `Dataset`, `DataLoader`, `torchvision.transforms`, `Predictor(model)`, 공통 후처리 |
| Lightning | 모델 Wrapper인 `LightningModule`, native `Trainer` 사용 코드, `LightningDataModule`, `LightningCLI` |

순수 PyTorch 영역은 Lightning을 import하거나 설치를 요구하지 않는다. 네트워크·데이터·변환·Predictor를 Lightning 없이 사용할 수 있어야 한다. Predictor는 순수 모델을 전달받아 실행하고 Lightning Wrapper나 Trainer에 의존하지 않는다.

Lightning 영역은 특정 네트워크나 데이터셋의 구체 구현을 직접 참조하지 않고, 외부에서 전달받은 PyTorch 표준 객체를 연결한다. 모델·데이터의 구체 객체 생성과 두 영역의 조립은 실행 진입점 또는 CLI 설정이 담당한다. Lightning 자체의 PyTorch 의존성은 유지한다.

독립 추론용 가중치는 순수 모델의 `state_dict`로 복원할 수 있게 한다. Lightning 체크포인트를 사용하는 경우 변환 책임은 Lightning 측 또는 별도 연결 코드에 둔다. 패키지 초기화 과정에서도 순수 PyTorch 사용이 Lightning import를 유발하지 않게 한다.

## Python 코딩 규칙

원본의 코딩 규칙을 적용한다. 경로는 `os.path`, 네이밍은 PEP 8, 자체 split 명칭은 `train`·`valid`·`test`로 통일한다. 멤버 변수 접두사와 등호·콜론 세로 정렬은 사용하지 않는다. 사용자 지정에 따라 모듈·클래스·함수·메서드에 docstring을 사용하지 않는다. 필요한 코드 설명은 간결한 영어 `#` 주석으로, Markdown 설명은 한국어로 작성한다. transform은 원본 구현처럼 `torchvision.transforms.v2`를 사용하고 pretrained 모델은 `weights=None`과 로컬 가중치 주입 방식으로 구성한다.

Lightning의 `val_dataloader` 같은 공식 API 이름은 그대로 유지한다. 원본의 WSL 환경, Lightning 금지와 Phase 절차는 이 프로젝트에 적용하지 않는다. 세부 규칙은 [AGENTS.md](AGENTS.md)에 기록했다.

## 현재 순수 PyTorch 코드

| 파일 | 내용 |
| --- | --- |
| [src/torch/tasks/classification/models/cnn/model.py](src/torch/tasks/classification/models/cnn/model.py) | 문자열 backbone으로 선택하는 ClassificationModel과 Custom CNN 보조 클래스 |
| [src/torch/tasks/classification/data/cifar10/dataset.py](src/torch/tasks/classification/data/cifar10/dataset.py) | CIFAR10Dataset. 전용 변환은 [transform.py](src/torch/tasks/classification/data/cifar10/transform.py)에 정의 |
| [src/torch/tasks/classification/data/oxford_pets/dataset.py](src/torch/tasks/classification/data/oxford_pets/dataset.py) | OxfordPetsClassification, 명시적인 JSON split 사용. 전용 변환은 [transform.py](src/torch/tasks/classification/data/oxford_pets/transform.py)에 정의 |
| [src/torch/inference/predictor.py](src/torch/inference/predictor.py) | 공통 Predictor, preprocess·postprocess 연결, 순수 가중치 저장·복원 |
| [src/torch/tasks/classification/preprocessors/classification.py](src/torch/tasks/classification/preprocessors/classification.py) | 입력 객체를 그대로 반환하는 ClassificationPreprocess |
| [src/torch/tasks/classification/postprocessors/classification.py](src/torch/tasks/classification/postprocessors/classification.py) | logits·확률·클래스 ID를 반환하는 ClassificationPostprocess |
| [tests/test_torch.py](tests/test_torch.py) | 로컬 자산 실행, 독립 추론, 전처리 중복 방지와 가중치 복원 검증 |

모델은 registry나 factory 없이 `ClassificationModel(backbone="custom", num_classes=10, weights_path=None)`로 생성한다. 지원하는 backbone은 `custom`, `resnet18`, `resnet50`, `efficientnet_b0`다. 기본값은 custom이며 알 수 없는 이름은 오류로 처리한다. 기존 네트워크 구조와 logits 반환, state_dict 키 구성을 유지한다. `num_classes`로 양의 정수를 전달하며 기본값은 10이다.

ResNet18·ResNet50·EfficientNet-B0의 `weights_path=None`은 무작위 초기화를 의미한다. 로컬 ImageNet pretrained 가중치를 사용하려면 경로를 지정한다. 경로가 잘못됐거나 가중치가 맞지 않으면 오류가 발생하며, 자동 다운로드나 무작위 초기화로의 대체는 하지 않는다. pretrained 가중치는 원래 head에 로드한 뒤 새 분류 head로 교체하므로 별도 학습이 필요하다. Custom CNN은 처음부터 학습하는 모델이며 `weights_path`를 지정하면 오류가 발생한다.

```python
from src.torch.tasks.classification.models.cnn.model import ClassificationModel

model = ClassificationModel(
    backbone="resnet50",
    num_classes=10,
    weights_path="E:/backbones/resnet50-0676ba61.pth",
)
```

확인한 로컬 가중치는 ResNet18의 `resnet18-f37072fd.pth`, ResNet50의 `resnet50-0676ba61.pth`, EfficientNet-B0의 `efficientnet_b0_rwightman-7f5810bc.pth`이며 모두 `E:\backbones`에 있다. 모델에 학습된 순수 가중치를 복원할 때는 `weights_path` 대신 완성된 모델에 `Predictor.load_weights()` 또는 `load_state_dict()`를 사용한다.

`CIFAR10Transform(train=False, image_size=224)`는 `v2.Compose`를 상속하며 기본 입력 크기 224와 ImageNet 정규화를 적용한다. `train=True`이면 학습용 무작위 증강을 추가한다.

`CIFAR10Dataset`은 `torch.utils.data.Dataset`을 직접 상속한다. `torchvision.datasets.CIFAR10`을 사용하지 않고 `root/cifar-10-batches-py`의 `data_batch_1`~`data_batch_5` 또는 `test_batch`를 읽는다. `__getitem__()`은 RGB 이미지와 `torch.long` 클래스 타깃을 반환하며, `transform`과 `target_transform`을 선택적으로 적용한다. 데이터 다운로드나 압축 해제는 수행하지 않는다.

`OxfordPetsClassification`은 원본 `cv_boilerplate`의 Oxford Pets Dataset을 registry·`src.core` 의존성 없이 구현한다. 기본 root는 `E:/datasets/oxford_pets`이며 `annotations/list.txt`를 샘플 기준으로 사용하고 `images/{sample_id}.jpg`를 읽는다. 37개 품종 라벨을 0~36의 `torch.long`으로 반환한다. JSON `split_path`는 필수이며 `train`, `valid`, `test` 각각에 확장자를 제외한 샘플 ID 목록이 있어야 한다. split 간 중복·split 내부 중복·알 수 없는 ID는 오류로 처리한다.

Oxford Pets도 CIFAR-10과 동일하게 `transform(image)`와 별도 `target_transform(target)`을 사용한다. 이미지 transform을 지정하지 않으면 RGB PIL 이미지를 반환한다. 원본의 `(image, target)` 결합 transform 방식은 이 프로젝트의 Dataset 인터페이스에 맞춰 변경했다. split 파일 생성이나 데이터 다운로드는 수행하지 않으며, 로컬 데이터 검증에는 임시 split 파일만 사용했다.

`data/oxford_pets/transform.py`의 `OxfordPetsTransform(train=False, image_size=224)`은 원본의 분류 변환을 따른다. 학습 시 `RandomResizedCrop(scale=(0.7, 1.0))`과 수평 뒤집기를 적용한다. 평가·추론 시 짧은 변을 `image_size * 256 / 224`로 resize한 뒤 center crop한다. 두 경로 모두 float32 변환과 ImageNet 정규화를 적용하며 target은 변경하지 않는다. Dataset의 transform과 Predictor의 원시 이미지 preprocess에 같은 평가용 클래스를 전달할 수 있다.

`data/cifar10/dataset.py`와 `data/cifar10/transform.py`에는 각각 Dataset과 transform 및 관련 상수를 정의하며 factory 함수는 두지 않는다. train/valid 분할은 실행 코드 또는 DataModule에서 동일한 seed로 인덱스를 생성하고 각 Dataset에 `Subset`을 적용한다. 학습용·검증용 Dataset은 각각의 transform을 사용하며 인덱스는 겹치지 않게 구성한다. 표준 `DataLoader`도 사용하는 쪽에서 직접 생성한다. Dataset에는 배치 크기·worker 수·Lightning 설정을 넣지 않는다.

`inference/predictor.py`는 모델과 외부 `preprocess`·`postprocess`를 연결하며 분류 Task를 직접 참조하지 않는다. `predict(image)`는 입력 한 장에 preprocess를 적용한다. preprocess를 생략하면 입력을 그대로 사용하므로 이미 변환된 CHW 텐서를 전달할 수 있다. `predict_batch(batch)`는 이미 변환된 NCHW 텐서를 받아 sample preprocess를 생략한다. 현재 Predictor의 입력 계약은 이미지 텐서이며, 모델 출력은 후처리를 생략하면 그대로 반환한다. 결과 텐서는 지정한 실행 장치에 유지된다.

분류 Task의 `ClassificationPreprocess()`는 Dataset이 반환한 입력 객체를 수정·복사하지 않고 그대로 반환한다. 정규화나 resize를 중복 적용하지 않는다. 원시 이미지를 추론할 때는 아래처럼 평가용 transform을 명시적으로 전달한다. `ClassificationPostprocess()`는 분류 logits를 해석하며 Lightning Wrapper에서도 재사용할 수 있다.

```python
from src.torch.tasks.classification.data.cifar10.transform import CIFAR10Transform
from src.torch.inference.predictor import Predictor
from src.torch.tasks.classification.postprocessors.classification import ClassificationPostprocess

predictor = Predictor(
    model,
    preprocess=CIFAR10Transform(train=False),
    postprocess=ClassificationPostprocess(),
    device="cuda",
)
```

프로젝트 루트에서 지정 Python으로 `-B -m unittest discover -s tests -v`를 실행하면 기존 순수 PyTorch 테스트를 실행할 수 있다. 이번 Lightning 코드에 대한 테스트는 아직 작성하거나 실행하지 않았다.

## Lightning 코드

분류 Wrapper와 공용 DataModule을 별도 파일로 작성했다. Lightning 설치와 두 클래스의 import 확인을 완료했다. 학습·추론 실행 검증과 CLI 진입점 구현은 후속 작업이다.

| 클래스 | 인터페이스와 동작 |
| --- | --- |
| [ClassificationModule](src/lightning/tasks/classification/taskmodule.py) | `model`, `num_classes`, 선택적 `loss_fn`, `preprocess`, `postprocess`, `learning_rate`, `weight_decay`를 받음 |
| [ClassificationData](src/lightning/tasks/classification/datamodule.py) | Task 공용. 단계별 Dataset 또는 기존 Loader와 분할·배치 설정을 받음 |

Wrapper의 `forward(images)`는 순수 모델의 출력을 반환한다. 학습·검증·테스트 step은 입력에 preprocess를 한 번 적용하고 logits로 Loss·Metric을 계산한다. 기본 Loss는 CrossEntropyLoss, Python Trainer 사용 시 기본 optimizer는 AdamW(lr=0.001, weight_decay=0.0001)다. 향후 LightningCLI에서는 YAML의 optimizer 설정으로 native 자동 구성을 사용한다.

기록할 지표는 `train`·`valid`·`test`별 loss, micro accuracy, macro F1이다. train loss는 step·epoch 단위로, 나머지는 epoch 단위로 기록하도록 작성했다. `predict_step`은 이미지 배치 또는 `(images, targets)` 배치를 받고 postprocess가 있으면 적용하며, 없으면 원시 출력을 반환한다. Dataset의 이미지 transform은 다시 적용하지 않고, Wrapper의 preprocess는 기본 입력 유지 또는 추가 배치 처리용으로 사용한다.

DataModule의 Dataset 인자는 `train_dataset`, `valid_dataset`, `test_dataset`, `predict_dataset`이며 Loader 인자는 `train_loader`, `valid_loader`, `test_loader`, `predict_loader`다. 같은 단계의 Dataset과 Loader를 동시에 지정하면 오류를 발생시킨다. 직접 전달된 Loader의 sampler·collate 설정은 변경하지 않는다.

DataModule은 분류 모델·Loss·Metric·타깃 형식을 직접 참조하지 않으므로 다른 Task에서도 사용할 수 있다. detection 등에서 사용자 정의 collate_fn이 필요하면 그 설정을 적용한 DataLoader를 전달한다. Dataset을 직접 전달하면 기본 collate 동작을 사용한다.

`valid_size`가 지정되면 길이와 샘플 순서가 같은 학습용·평가용 Dataset을 받아 seed 기반의 겹치지 않는 인덱스로 분할한다. 샘플 순서 일치는 호출자가 보장해야 한다. train·valid Loader를 이미 제공한 상태에서는 분할 옵션을 사용할 수 없다. `valid_size=None`이면 이미 분리된 Dataset을 유지한다. `setup()` 반복 호출 시 다시 분할하지 않는다.

`fit`에서는 검증 데이터가 없어도 사용할 수 있게 작성했다. 별도 `validate`·`test` 요청에는 해당 데이터가 필요하며, 예측용 데이터가 없으면 테스트 데이터를 사용한다. 기존 Loader가 없는 경우에만 표준 DataLoader를 생성하며 학습 데이터만 shuffle한다. 기본 `batch_size=32`, `num_workers=0`, `pin_memory=False`이고 YAML에서 덮어쓸 수 있다.

순수 추론용 가중치는 `module.model.state_dict()`에서 얻는다. native 체크포인트 복원 시에는 `model`과 필요한 `loss_fn`·`preprocess`·`postprocess` 객체를 명시적으로 전달한다. 두 Dataset에는 native CLI의 중첩 transform 생성을 위한 callable 타입 힌트를 추가했다.

## 공통 YAML 유틸리티와 독립 Lightning 설정

[src/torch/utils/config.py](src/torch/utils/config.py)에 YAML 로딩과 dict 병합 함수를 둔다. `load_yaml(path)`는 UTF-8 YAML을 safe_load로 읽고 최상위가 dict가 아니면 오류를 반환한다. `merge_config(base, overrides)`는 중첩 dict를 재귀 병합하고 리스트·일반 값·None은 교체한다. 입력을 수정하지 않으며 결과 dict는 독립된 객체다. Lightning 의존성·객체 생성·실행 ID 생성·파일 저장 기능은 포함하지 않는다.

```python
from src.torch.utils.config import load_yaml, merge_config

config = load_yaml("src/torch/tasks/classification/configs/cifar10.yaml")
config = merge_config(config, {"data": {"batch_size": 64}})
```

[src/lightning/tasks/classification/configs/cifar10.yaml](src/lightning/tasks/classification/configs/cifar10.yaml)은 순수 PyTorch YAML의 내용을 직접 중복 포함하고 Trainer·CSVLogger·ModelCheckpoint를 추가한 완전한 Lightning 설정이다. 다른 YAML을 읽거나 상속·병합하지 않는다. 순수 PyTorch 클래스는 재배치된 class_path로 재사용한다. 두 YAML의 설정은 독립적으로 수정하며 자동 동기화하지 않는다.

기본 Trainer 설정은 accelerator=auto, devices=1, precision=32-true, max_epochs=10, log_every_n_steps=10이다. CSV 로그와 valid_loss 최솟값 기준 best.ckpt·last.ckpt는 모두 `outputs/cifar10/run_001` 바로 아래에 저장하도록 설정했다. 새 실행에서는 trainer.default_root_dir·logger.version·callbacks.dirpath의 실행 ID를 함께 변경한다. 경로는 프로젝트 루트에서 해석한다.

기존 Python 설정 모듈과 get_config()는 제거했다. 자동 실행 ID 생성과 Task별 main.py는 아직 구현하지 않았으며, 후속 실행 계층에서 이 YAML을 native LightningCLI의 --config로 직접 읽도록 연결한다. 패키지 설치와 import 확인은 완료했으며, YAML 기반 객체 생성·테스트 작성·학습·추론 실행 검증은 후속 작업이다.

## 폴더 재배치 기록

2026-10-16에 기존 구현만 새 구조로 재배치하고 YAML class_path·테스트 import·문서 링크를 갱신했다. Dataset과 전용 transform을 파일로 분리했으며 클래스명·생성자·기본값·가중치 구조는 유지했다. 이전 모듈 경로의 호환 모듈은 제공하지 않는다. 새 DataLoader·CLI 구현과 기본값 동작 변경은 포함하지 않았다. 이번 재배치에서는 테스트·학습·추론·import 실행 검증을 수행하지 않았다.

## Dataset별 DataLoader

- [CIFAR10Dataloader](src/torch/tasks/classification/data/cifar10/dataloader.py)는 기본 경로 `E:/datasets/cifar10`에서 Dataset을 구성한다. 기본 `split="train"`, `valid_size=5000`, `seed=42`이며, train·valid Loader에 같은 root·valid_size·seed를 지정해야 두 split이 겹치지 않는다. `split="test"`는 원본 test 전체를 사용한다. `valid_size=None`은 train 전체를 사용하며 valid에는 지정할 수 없다.
- [OxforPetsDataloader](src/torch/tasks/classification/data/oxford_pets/dataloader.py)는 사용자 지정 클래스명을 사용한다. 기본 경로는 `E:/datasets/oxford_pets`이며 JSON `split_path`를 반드시 전달한다. JSON의 train·valid·test 분할을 그대로 사용한다. 기존 설정의 split 경로는 프로젝트 루트 기준 `../_clones/cv_boilerplate/configs/splits/oxford_pets.json`이다.
- 두 클래스는 순수 PyTorch `DataLoader`를 상속한다. 공통 기본값은 `batch_size=32`, `num_workers=0`, `pin_memory=True`, `image_size=224`, `seed=42`, `drop_last=False`다. `shuffle=None`이면 train만 shuffle하며 명시적인 bool로 변경할 수 있다.
- 기본 transform은 split에 맞는 기존 Dataset 전용 학습·평가 변환이다. `transform` callable을 전달하면 기본 변환을 대체한다. `transform=None`, `use_default_transform=False`이면 변환하지 않으므로 PIL 이미지가 반환된다. 이 경우 배치를 구성하려면 PIL을 처리하는 `collate_fn`이 필요하다. `target_transform`과 `collate_fn`도 전달할 수 있다.
- 생성자 인자를 명시하거나 YAML의 `class_path`·`init_args`로 객체와 변경할 값을 지정할 수 있다. 현재 YAML 파일은 기존 Dataset 구성을 유지한다. `ClassificationData`에는 train_loader·valid_loader·test_loader로 전달하고, `valid_size`는 기본값인 None을 유지한다.
- 이번 작업에서는 테스트·import·데이터 로딩·학습·추론 실행을 수행하지 않았다.
