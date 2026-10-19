# lightning-tutorial 작업 지침

## 작업 범위와 기준

- 작업 위치는 `D:\projects\lightning-tutorial`이다.
- 관련 명세 문서는 `specs/v0.1/`에 저장한다. 작업 지침 `AGENTS.md`는 프로젝트 루트에만 둔다.
- 예제 실행 노트북은 `notebooks/`에 저장한다. 노트북에는 모델 알고리즘이나 Lightning Wrapper를 중복 구현하지 않고 모델별 CLI를 호출한다.
- 목적과 설계 원칙은 [INTENT.MD](specs/v0.1/INTENT.MD), 프로젝트 안내는 [README.md](README.md), 구현 순서와 진행 상태는 [PLAN.MD](specs/v0.1/PLAN.MD)를 따른다.
- 현재 사용자 요청을 우선한다. 기존 프로젝트의 지침은 참조 자료이며 현재 구조와 충돌하는 규칙을 가져오지 않는다.
- 사용자 요청에 따라 작은 단위로 구현하고 실행 결과와 피드백을 반영한다. 문서 작성 요청을 코드 작성·패키지 설치·전체 이식으로 확대하지 않는다.
- 미구현 기능의 빈 파일과 폴더를 미리 만들지 않는다. 불필요한 registry·engine·추상화 계층을 추가하지 않는다.
- 초기 구현 대상은 CIFAR-10·ResNet50과 MVTec·STFPM이다. 다른 task·데이터셋·모델은 후속 요청에 따라 다룬다.

## 코드 배치와 의존성

- `src/classification`과 `src/anomaly_detection` 아래에 각각 `configs`, `data`, `models`를 둔다.
- 모델별 폴더에 `model.py`, `loss.py`, `metric.py`, `lightning_module.py`, `lightning_cli.py`를 필요한 만큼 작성한다.
- 데이터셋별 폴더에 `dataset.py`와 `transform.py`를 둔다. 추가 데이터 연결 파일이 필요하면 역할과 배치를 먼저 정리한다.
- 설정은 task별 `configs/default.yaml`, `configs/data/{dataset_name}.yaml`, `configs/models/{model_name}.yaml`로 나눈다. native CLI의 반복 `--config`로 이 순서대로 결합하고 마지막 CLI 인자로 덮어쓴다.
- 공통 Predictor는 `src/inference/predictor.py`, 공통 파일·설정 처리는 `src/utils/io.py`·`config.py`에 둔다.
- 공통 Lightning 연결은 `src/utils/lightning_data.py`·`lightning_cli.py`에 둔다. 순수 유틸리티와 패키지 초기화에서 이 파일을 자동 import하지 않는다.
- 기존 `src/torch`·`src/lightning` 배치는 사용하지 않는다. 두 영역은 task의 모델 폴더 안에서 파일과 의존성으로 분리한다.
- 프로젝트 내부 모듈은 `src.*`로 참조하고 CLI는 프로젝트 루트에서 모듈로 실행한다. 루트에 Python 진입점을 두지 않는다.

## 순수 PyTorch와 Lightning의 분리

- `model.py`는 순수 `nn.Module`이다. 모델 구조와 연산·입출력 동작을 최대한 보존하고 `forward()`에 Lightning Hook이나 학습 실행 제어를 넣지 않는다.
- Dataset·DataLoader·transform·loss·metric·후처리·Predictor는 Lightning 없이 사용할 수 있어야 한다.
- `lightning_module.py`는 순수 모델을 감싸는 Wrapper다. 학습·검증·평가·예측 Hook, optimizer 연결, 단계별 metric 상태 관리와 로깅을 담당한다.
- Wrapper에 모델 알고리즘을 중복 구현하지 않는다. 외부에서 모델·loss 등 필요한 구성요소를 전달받고, 구체 객체의 생성과 조립은 CLI 또는 설정에서 담당한다.
- 실제 `LightningModule`, `Trainer`, 필요한 `LightningDataModule`, `LightningCLI`를 사용한다. native `fit`, `validate`, `test`, `predict`와 설정 덮어쓰기를 활용한다.
- 순수 PyTorch 파일은 Lightning 파일을 import하지 않는다. 패키지 초기화도 Lightning의 자동 import를 유발하지 않게 한다.
- 공통 Predictor는 task별 구체 클래스나 Lightning Wrapper·Trainer를 참조하지 않는다. 전처리·후처리는 외부 callable로 연결한다.
- 독립 추론용 가중치는 순수 모델의 `state_dict`로 복원한다. Lightning 체크포인트 변환은 Lightning 측 또는 별도 연결 코드에서 처리한다.
- 데이터 분할과 전처리를 중복 적용하지 않는다. 학습용 변환과 평가·추론용 변환을 구분한다.

## 참조 원본

- `D:\projects\dl-lightning`: 기존 목적·분리 원칙과 CIFAR-10·ResNet50 구현을 참조한다.
- `D:\projects\_clones\cv_boilerplate`: MVTec 데이터 처리와 `src/tasks/anomaly/models/stfpm.py`, 관련 loss·metric·후처리·설정을 참조한다.
- [anomalib STFPM](https://github.com/open-edge-platform/anomalib/tree/main/src/anomalib/models/image/stfpm): 상위 알고리즘과 Wrapper 구현을 참조한다.
- STFPM의 `model.py`는 anomalib의 `torch_model.py`를 순수 PyTorch 수준에서 최대한 보존한 기존 구현을 바탕으로 작성한다.
- STFPM의 `lightning_module.py`는 anomalib의 `lightning_model.py`를 최대한 참조한다. 모델별 학습·검증 흐름과 optimizer 구성을 검토하고 native Lightning으로 연결한다.
- anomalib 전용 기반 클래스·배치 형식·실행 계층은 자동으로 도입하지 않는다. 분리 원칙에 필요한 연결만 조정하고 원본과 다른 동작은 문서에 기록한다.
- 참조 코드 재사용 시 원본의 저작권·라이선스 표기를 유지한다. 구현 시 참조한 버전 또는 커밋을 기록한다.
- 참조 프로젝트와 데이터·원본 가중치는 수정하지 않는다. 프로젝트 전체 복사나 기존 작업 폴더로의 코드 작성을 하지 않는다.

## Python 스타일

- 경로는 `os.path`로 처리하고 `pathlib.Path`를 사용하지 않는다.
- PEP 8 네이밍을 따른다. 변수·함수는 `snake_case`, 클래스는 `PascalCase`, 상수는 `UPPER_SNAKE_CASE`로 작성한다.
- 멤버 변수에 별도 접두사를 붙이지 않는다. private 표기가 필요하면 단일 언더스코어를 사용한다.
- 등호·콜론을 세로 정렬하지 않는다.
- docstring은 작성하지 않는다. 필요한 코드 설명은 간결한 영어 `#` 주석으로, 문서는 한국어로 작성한다. 원본 저작권·라이선스 표기는 유지한다.
- 자체 데이터 split은 `train`, `valid`, `test`를 사용한다. Lightning 공식 API 이름은 그대로 사용한다.
- transform은 기존 구현처럼 `torchvision.transforms.v2`를 기본으로 사용한다.
- pretrained 네트워크는 자동 다운로드 없이 생성하고 로컬 가중치를 명시적으로 로드한다. 필요한 가중치가 없으면 오류를 표시하며 무작위 초기화로 조용히 대체하지 않는다.
- 학습 결과는 로컬 설정·히스토리·metric 파일로 기록한다. 별도 요청 없이 TensorBoard·W&B를 추가하지 않는다.

## 실행 환경과 검증

- 지정 Python 실행 파일은 `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe`다. Python 실행과 패키지 확인·설치는 이 실행 파일을 명시한다. pip는 해당 Python의 `-m pip`를 사용한다.
- 사용자가 지정한 데이터셋 위치는 `E:\datasets`, pretrained 가중치 위치는 `E:\backbones`다. 해당 위치의 로컬 파일을 우선 사용하고, 실제 하위 경로와 파일은 구현 전에 확인한다.
- 이전 프로젝트의 패키지·CUDA 확인 결과를 현재 검증 결과로 간주하지 않는다. 환경을 확인하고 변경 사항과 검증 결과를 README에 기록한다.
- 데이터와 가중치를 자동 다운로드하지 않는다. 추가 다운로드가 필요하면 필요성과 대상을 사용자에게 설명한다.
- 검증은 변경 범위에 맞게 수행한다. 순수 모델 import·forward, Lightning 실행, 가중치 복원과 독립 추론을 구분해 확인한다.
- 실행하지 않은 학습·평가·테스트를 완료로 기록하지 않는다. PLAN의 상태는 실제 결과에 따라 갱신한다.

## 명령과 문서

- 명령 실행 전 `C:\Users\wonhee.nam\.codex\RTK.md`를 읽고 따른다. 외부 명령은 RTK를 사용하며 PowerShell cmdlet은 RTK proxy로 실행한다.
- 이모지를 사용하지 않는다.
- Markdown은 UTF-8로 저장한다. 저장 후 엄격한 UTF-8 디코딩과 한글 본문 확인으로 인코딩을 검증한다.
