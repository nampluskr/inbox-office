# dl-lightning 작업 지침

## 작업 위치와 진행 방식

- 작업 폴더는 `D:\projects\dl-lightning`이다. 코드와 프로젝트 지침은 이 폴더에 작성한다.
- 이 프로젝트에는 `project-workflow`의 문서 작성·프로젝트 초기화·버전 관리 절차를 적용하지 않는다.
- 사용자의 요청에 따라 작은 단위로 코드를 작성하고, 실행 확인과 사용자 평가·피드백을 바탕으로 반복 개선한다.
- 예제 코드는 사용자가 작성을 요청할 때 작성한다. 환경·참고문서 정리 요청을 코드 작성이나 패키지 설치 요청으로 확대하지 않는다.
- 최초 구현 대상은 로컬 CIFAR-10 데이터셋을 사용하는 간단한 classification 예제다.
- 문서의 전체 지원 방향을 첫 예제의 필수 구현 범위로 확대하지 않는다.

## 프로젝트의 주목적과 참조 원본

- 가장 큰 목적은 `D:\projects\_clones\cv_boilerplate`의 순수 PyTorch 기반 학습·평가 실행 구현을 Lightning native 구현으로 대체하는 것이다.
- 기존 모델·Dataset·DataLoader·변환·후처리·독립 Predictor는 순수 PyTorch 영역으로 유지하고, 학습 프레임워크의 책임은 Lightning 영역에 둔다.
- `cv_boilerplate`는 읽기 전용 참조 원본이다. 원본을 수정하거나 프로젝트 전체를 복사하지 않는다.
- 현재 구현은 CIFAR-10부터 작은 단위로 진행한다. 원본의 전체 기능 이식은 개별 사용자 요청에 따라 진행한다.

## Python 코딩 스타일과 적용 규칙

근거는 `D:\projects\_clones\cv_boilerplate\AGENTS.md`와 `CLAUDE.md`의 Code Style Rules 및 실제 classification 모델·Dataset·transform 코드다.

- 경로는 `os.path`로 처리하고 `pathlib.Path`를 사용하지 않는다.
- PEP 8 네이밍을 따른다. 변수·함수는 `snake_case`, 클래스는 `PascalCase`, 상수는 `UPPER_SNAKE_CASE`로 작성한다.
- 멤버 변수에 별도 접두사를 붙이지 않는다. private 표기가 필요하면 단일 언더스코어만 사용한다.
- 등호·콜론의 세로 정렬을 하지 않는다. dict 리터럴에도 동일하게 적용한다.
- 자체 데이터 split은 `train`, `valid`, `test`로 통일한다. 검증 크기는 `valid_size`, 분류 모델의 백본 선택 인자는 사용자 지정에 따라 `backbone`으로 표기한다. 선택한 이름을 저장하는 멤버는 `backbone_name`, 실제 네트워크 멤버는 `backbone`으로 구분한다.
- Lightning native의 `val_dataloader`, `validation_step` 등 공식 API 이름은 그대로 유지한다. 자체 split의 `valid`를 해당 Hook에 연결한다.
- docstring은 사용하지 않는다. 모듈·클래스·함수·메서드 모두에 적용한다. 필요한 설명은 간결한 영어 `#` 주석 또는 한국어 Markdown 문서로 작성한다. 코드·경로·라이브러리 이름은 원문 표기를 유지한다.
- 원본의 실제 transform 코드처럼 `torchvision.transforms.v2`를 기본으로 사용한다.
- pretrained 아키텍처는 `weights=None`으로 만들고 로컬 가중치를 `load_state_dict`로 주입한다. 데이터셋·백본을 자동 다운로드하거나 누락된 pretrained 가중치를 조용히 무작위 초기화로 대체하지 않는다. 처음부터 학습하는 경우는 명시적으로 구분한다.
- 공통 실행 코드는 특정 Task나 Dataset 이름에 따라 분기하지 않는다. 불필요한 추상화 계층과 원본의 registry·engine 복제를 추가하지 않는다.
- 학습 결과는 로컬 설정·히스토리·메트릭 파일로 기록한다. 별도 요청 없이 TensorBoard·W&B 같은 실험 관리 도구를 추가하지 않는다.

원본의 WSL2·conda 환경, Lightning 금지, Phase·문서 체인·다중 에이전트·교차 검토 절차는 가져오지 않는다. 이 프로젝트의 Windows Python 환경, Lightning native 사용, 사용자 피드백 중심 진행 방식을 따른다.

## 실행 환경과 로컬 자산

- Python 실행 파일: `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe`
- Python 실행과 패키지 확인·설치에는 위 실행 파일을 명시적으로 사용한다. pip는 해당 실행 파일의 `-m pip`로 호출한다.
- 지정 Python에 `lightning==2.5.5`, `pytorch-lightning==2.5.5`, `jsonargparse[signatures]==4.40.2`를 설치했다. 기존 PyTorch 2.2.1+cu118·torchvision 0.17.1+cu118·torchmetrics 1.9.0을 유지한다. 패키지 변경 시 호환성을 확인하고 버전과 확인 결과를 README에 기록한다.
- 데이터셋 기본 경로: `E:\datasets`
- pretrained backbone 가중치 기본 경로: `E:\backbones`
- CIFAR-10의 실제 저장 구조와 backbone 파일명을 먼저 확인한다. 확인하지 않은 하위 경로나 파일명을 가정하지 않는다.
- 기존 로컬 데이터와 가중치를 우선 사용한다. 추가 다운로드가 필요하면 필요성과 대상을 사용자에게 설명한다.
- 데이터와 pretrained 원본 가중치를 프로젝트 폴더로 복사하거나 덮어쓰지 않는다.

## 목적과 구현 기준

참고 문서의 위치는 `D:\projects\_ideas\pytorch-lightning-ignite`다. 이 폴더는 목적과 구현 방향을 확인하는 참고 위치이며, 작업 폴더가 아니다.

- `INTENT.md`: 프로젝트 목적과 기본 원칙.
- `DECISIONS.md`: 사용자가 확정한 설계 방향.
- `BRIEF.md`: 전체 범위와 구현·검증 방향.
- `refs/`: 필요한 주제의 상세 검토 자료.

참고 문서와 현재 사용자 요청이 다르면 현재 사용자 요청을 우선한다. 참고 문서와 원본 자산은 수정하지 않는다.

- Lightning 구현과 검증을 먼저 진행한다. Ignite는 후속 요청에 따라 구현한다.
- 순수 PyTorch `nn.Module`을 분류 Wrapper에 전달하며 기존 모델의 `forward()`에 학습 프레임워크 의존성을 넣지 않는다.
- native `LightningModule`, `Trainer`, `LightningDataModule`, 실제 `LightningCLI`를 기준으로 구현한다.
- native `fit`, `validate`, `test`, `predict`와 config·명령줄 덮어쓰기 방식을 활용한다.
- 기존 Dataset과 DataLoader를 재사용하고, 기본 전처리는 Dataset의 transform을 활용한다. 학습용 변환과 평가·추론용 변환을 구분하고 중복 적용하지 않는다.
- CIFAR-10은 `src/torch/tasks/classification/data/cifar10/dataset.py`의 `CIFAR10Dataset(torch.utils.data.Dataset)`으로 구현한다. `torchvision.datasets.CIFAR10`을 사용하지 않고 로컬 Python 배치 파일을 직접 읽는다.
- Oxford Pets는 `src/torch/tasks/classification/data/oxford_pets/dataset.py`에 `OxfordPetsClassification(Dataset)`으로 둔다. 원본의 37개 품종·0-based 타깃·JSON split 규약을 유지한다. `train`·`valid`·`test` 샘플 ID 목록이 담긴 `split_path`를 명시하며, split 중복과 알 수 없는 ID를 검사한다. transform은 CIFAR-10과 동일하게 이미지에 적용하고 target_transform은 별도로 받는다.
- `data/oxford_pets/transform.py`의 `OxfordPetsTransform(v2.Compose)`은 학습 시 RandomResizedCrop·수평 뒤집기, 평가·추론 시 비율 유지 Resize·CenterCrop을 적용하고 ImageNet 정규화를 사용한다. 기본 image_size는 224이며 Dataset과 Predictor의 원시 입력 경로에서 공유한다.
- `data/cifar10/dataset.py`에는 `CIFAR10Dataset`, `data/cifar10/transform.py`에는 `CIFAR10Transform`과 각 관련 상수를 둔다. factory 함수는 만들지 않는다. Dataset별 `dataloader.py`가 Dataset·transform과 기본 Loader 설정을 구성한다. CIFAR-10 Loader는 train/valid 분할을 담당한다. 기존 Dataset 주입 방식에서는 Lightning DataModule의 분할 기능도 사용할 수 있으나 두 분할 방식을 동시에 적용하지 않는다.
- 공통 Predictor는 `src/torch/inference/predictor.py`에 두고 Task별 클래스를 직접 import하지 않는다. `preprocess`·`postprocess` callable을 외부에서 전달받고 모델 출력은 `outputs`로 다룬다. 현재 입력 계약은 이미지 CHW·NCHW 텐서다.
- 분류 전처리는 `src/torch/tasks/classification/preprocessors/classification.py`의 `ClassificationPreprocess`, 분류 후처리는 `src/torch/tasks/classification/postprocessors/classification.py`에 둔다. 기본 전처리는 Dataset이 반환한 입력 객체를 수정·복사하지 않고 그대로 반환한다. 원시 이미지에는 평가용 `CIFAR10Transform`을 명시적으로 연결하며, 이미 변환된 배치는 같은 transform을 재적용하지 않는다.
- 후처리는 순수 PyTorch 코드로 공유하고 Loss와 Metric에 필요한 원시 출력을 유지한다.
- 독립 추론 구현 시 Lightning 없이 순수 PyTorch 모델과 저장된 가중치로 실행할 수 있게 한다.
- 코드는 `src/torch`와 `src/lightning`으로 분리한다. `src` 바로 아래에는 `torch`, `lightning` 두 폴더를 두며, 루트에 Python 진입점을 두지 않는다. 데이터와 설정은 각 Task 아래에 둔다.

## 폴더 구조와 산출물 저장

- 프로젝트 루트의 폴더는 `src`, `docs`, `tests`, `notebooks`, `outputs`로 구성한다.
- 순수 PyTorch 코드는 `src/torch`, Lightning 코드는 `src/lightning`에 둔다.
- 공통 Predictor는 `src/torch/inference`에 둔다. 분류 CNN과 보조 클래스는 `src/torch/tasks/classification/models/cnn/model.py`에 두며 `ClassificationModel`을 registry·factory 없이 직접 생성한다. Dataset과 전용 transform은 `data/{dataset_name}/dataset.py`·`transform.py`로 분리하고, 현재 분류 공통 전처리·후처리는 `preprocessors/classification.py`·`postprocessors/classification.py`에 둔다.
- 지원하는 backbone 문자열은 `custom`, `resnet18`, `resnet50`, `efficientnet_b0`다. 알 수 없는 값은 오류로 처리한다. `num_classes`는 양의 정수이며 기본값은 CIFAR-10의 10이다. pretrained 백본의 `weights_path=None`은 무작위 초기화 모드이며, 경로가 주어지면 로컬 ImageNet 가중치를 엄격히 로드한 뒤 분류 head를 교체한다. custom에 weights_path를 지정하면 오류로 처리한다. 학습한 전체 모델의 가중치는 Predictor.load_weights 또는 load_state_dict로 복원한다.
- LightningCLI 진입점은 `src/lightning/tasks/classification/main.py`, 분류 설정은 `src/torch/tasks/classification/configs`에 둔다. `cifar10.yaml`·`oxford_pets.yaml`은 공통 `seed_everything`·`model`·`data`·`optimizer` 섹션을 사용하되 내용은 순수 PyTorch 객체와 설정만 포함한다. Lightning 클래스 경로와 Trainer·Logger·Callback·출력 경로 설정은 포함하지 않는다.
- YAML 공통 유틸리티는 `src/torch/utils/config.py`에 `load_yaml(path)`·`merge_config(base, overrides)`로 둔다. UTF-8과 safe_load를 사용하고 최상위 dict가 아니면 오류로 처리한다. 병합 시 dict는 재귀 병합하고 리스트·일반 값·None은 교체하며, 입력 dict를 수정하지 않고 독립된 dict를 반환한다. Lightning import·객체 생성·실행 ID 생성·파일 저장은 하지 않는다.
- Lightning 실행용 설정은 `src/lightning/tasks/classification/configs/cifar10.yaml`에 완전한 설정으로 직접 작성한다. 순수 PyTorch YAML의 model·data·optimizer·seed 항목을 명시적으로 중복 포함하고 Trainer·CSVLogger·ModelCheckpoint 설정을 추가한다. 다른 YAML을 읽거나 상속·병합하지 않으며 자동 동기화하지 않는다. 순수 PyTorch 클래스의 재사용은 유지한다.
- Lightning YAML의 기본 실행 ID는 run_001이며 trainer.default_root_dir·logger.version·callbacks.dirpath를 함께 수정한다. 로그와 best/last 체크포인트는 outputs/cifar10/run_001 바로 아래에 저장하도록 설정한다. 기존 Python 설정 모듈과 get_config API는 사용하지 않는다. Task별 main.py와 자동 실행 ID 생성은 이번 구현에 포함하지 않으며 실제 적용 검증은 후속 작업이다.
- 분류 Wrapper `ClassificationModule`은 `src/lightning/tasks/classification/taskmodule.py`, 분류 데이터 클래스 `ClassificationData`은 `src/lightning/tasks/classification/datamodule.py`에 정의한다. CLI는 향후 `LightningCLI(ClassificationModule, ClassificationData)`처럼 클래스를 명시하는 fixed-class 방식으로 연결한다. YAML의 `model`·`data` 바로 아래에는 이 생성자에 전달할 인자를 두고, 순수 모델은 `model.model`에 연결한다. 패키지 설치와 Wrapper·DataModule import 확인은 완료했으며 학습·추론 실행과 CLI 객체 생성 검증은 사용자 요청에 따라 후속으로 진행한다. CLI 진입점은 아직 구현 전이다.
- Wrapper는 외부 모델·Loss·preprocess·postprocess를 받고 native fit·validate·test·predict Hook을 구현한다. loss·micro accuracy·macro F1 상태는 단계별로 분리한다. forward는 모델의 원시 출력을 반환하고 preprocess는 step에서 한 번 적용한다. 기본 optimizer는 AdamW이며 LightningCLI의 optimizer 자동 구성으로 교체할 수 있다.
- DataModule은 모델·Loss·Metric·Task별 타깃 형식을 다루지 않는 공용 데이터 계층이다. 단계별 Dataset 또는 기존 DataLoader를 받는다. 같은 단계에 둘 다 전달하면 오류로 처리한다. 직접 전달된 Loader는 그대로 재사용하고, 예측 데이터가 없으면 테스트 데이터를 사용한다. fit의 검증 데이터는 선택 사항이다. 분할은 setup에서 한 번 수행하고 반복 호출 시 유지한다. 사용자 정의 collate_fn이 필요하면 해당 설정이 적용된 DataLoader를 전달한다.
- docstring은 추가하지 않으며 LightningCLI의 중첩 객체 생성을 위한 생성자 타입 힌트는 허용한다. 사용자 요청으로 패키지 설치와 LightningCLI·Wrapper·DataModule import 및 CUDA 상태 확인을 완료했다. 테스트 작성·실행, YAML 기반 CLI 객체 생성과 학습·추론 검증은 별도 사용자 요청까지 보류한다.
- DataModule의 `valid_size`가 정수이면 CIFAR-10의 학습 원본을 겹치지 않는 train/valid 인덱스로 나누며, null이면 외부 JSON으로 이미 분리된 Oxford Pets Dataset을 그대로 사용한다. Oxford Pets의 split 파일은 원본 `_clones/cv_boilerplate/configs/splits/oxford_pets.json`을 읽기 전용으로 참조하며, 상대 경로는 프로젝트 루트에서 해석한다.
- LightningCLI 기반 평가는 같은 진입점의 `validate`, `test`, `predict`를 활용한다. 평가 전용 파일이 필요하면 `src/lightning`에 둔다. 순수 PyTorch 독립 평가 진입점은 필요 시 `src/torch`에 둔다.
- 설치된 `torch`, `lightning`과의 이름 충돌을 피하도록 내부 모듈은 `src.torch.*`, `src.lightning.*`로 참조한다. 향후 CLI 구현 시 프로젝트 루트에서 `python -m src.lightning.tasks.classification.main` 형태로 실행하고 `src`를 `PYTHONPATH`에 추가하지 않는다.
- 실행 산출물은 `outputs/cifar10/{run_id}/` 바로 아래에 파일로 저장한다. `{run_id}` 아래에는 하위 폴더를 생성하지 않는다.
- 실행 설정, Lightning 체크포인트, 순수 모델 가중치, 학습 히스토리, 최종 메트릭, 예측 결과와 그래프를 파일명으로 구분한다. Logger와 Callback도 별도 하위 폴더를 만들지 않도록 설정한다.
- pretrained 원본은 `E:\backbones`에서 재사용하고, 학습으로 생성한 가중치는 해당 실행의 outputs 경로에 저장한다.
- 폴더 구조의 확정은 코드·설정·예제 산출물 생성 요청을 의미하지 않는다.

## 전체 폴더 배치 기준

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

- 전체 구조는 배치 기준이며 현재 작성된 구현만 배치한다. 미구현 기능의 파일과 빈 폴더는 생성하지 않는다.
- Task별 `taskmodule.py`·`datamodule.py`의 클래스명은 `ClassificationModule`·`ClassificationData`를 사용한다.
- 모델 전용 전처리·후처리·Loss·Metric은 모델 폴더, 여러 모델이 공유하는 구현은 Task의 공통 폴더에 둔다. 공통 transform도 실제 공유 구현이 있을 때 추가한다.

### 데이터 기본값과 YAML 재정의 방향

- 사용할 Dataset별 Loader 클래스는 YAML에서 명시하고, 생략한 인자는 해당 클래스의 기본값을 사용한다.
- Dataset별 `dataloader.py`는 데이터 경로·학습/평가 transform·분할·배치·worker 설정의 기본 구성을 제공한다. YAML에는 변경할 값만 명시할 수 있게 한다.
- Task의 DataModule은 단계별 Loader를 Lightning Hook에 연결하며, 생략한 설정으로 Loader의 기본값을 덮어쓰지 않는다.
- Dataset별 분할과 transform 적용은 한 곳에서 담당한다. 학습·평가 데이터가 겹치거나 resize·정규화가 중복 적용되지 않게 한다.
- 아직 기본 경로가 확정되지 않은 필수 입력은 명시적으로 받는다. 현재 Oxford Pets의 `split_path`는 필수다.
- Dataset별 DataLoader를 구현했다. 기존 YAML은 Dataset 주입 방식을 유지하며, Loader를 직접 전달할 때는 DataModule의 `valid_size=None`을 사용해 중복 분할을 피한다. DataModule은 전달된 Loader의 기본값을 변경하지 않는다.

- Dataset별 Loader 클래스명은 사용자 지정에 따라 `CIFAR10Dataloader`·`OxforPetsDataloader`를 사용한다. Oxford Pets Loader의 `split_path`는 필수다. 기본 transform 대신 사용자 callable을 전달할 수 있고, 기본 변환을 끄려면 `use_default_transform=False`를 지정한다.

## PyTorch와 Lightning의 분리 원칙

- 순수 PyTorch 파일과 Lightning 파일은 별도 모듈로 완전히 분리한다. 한 파일에 두 영역의 구현을 섞지 않는다.
- 순수 PyTorch 영역: 네트워크 `nn.Module`, `torch.utils.data.Dataset`과 `DataLoader`, `torchvision.transforms`, 순수 PyTorch `Predictor(model)`, 공통 후처리.
- Lightning 영역: 모델 Wrapper인 `LightningModule`, native `Trainer` 사용 코드, `LightningDataModule`, `LightningCLI`.
- 순수 PyTorch 영역은 Lightning 영역을 import하거나 Lightning 설치·객체·Hook·체크포인트 형식을 요구하지 않는다. Lightning 없이 모델·데이터·변환·Predictor를 사용할 수 있어야 한다.
- Lightning 영역은 특정 네트워크·데이터셋·변환·Predictor의 구체 구현에 결합하지 않는다. 모델은 `nn.Module`, 데이터는 Dataset/DataLoader 등 PyTorch 표준 객체로 외부에서 전달받는다.
- 두 영역의 구체 객체 생성과 연결은 실행 진입점 또는 CLI 설정에서 수행한다. 패키지 초기화 시 다른 영역을 자동 import하지 않는다.
- 순수 PyTorch Predictor는 전달받은 모델로 추론하며 Lightning Wrapper나 Trainer를 호출하지 않는다. 독립 추론용 가중치는 순수 모델의 `state_dict`로 복원할 수 있게 하고, Lightning 체크포인트 변환은 Lightning 측 또는 별도 연결 코드에서 처리한다.
- Lightning이 내부적으로 PyTorch를 사용하는 것은 정상적인 의존성이다. 분리의 기준은 사용자 정의 두 영역 사이의 구체 구현 의존성과 실행 의존성을 없애는 것이다.

## 명령과 문서

- 명령 실행 전에 `C:\Users\wonhee.nam\.codex\RTK.md`를 읽고 따른다.
- 이모지를 사용하지 않는다.
- 마크다운은 UTF-8로 저장하고 저장 후 한글이 깨지지 않았는지 확인한다.
