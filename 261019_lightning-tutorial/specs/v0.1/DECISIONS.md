# 구현 결정과 참조 확인

## 2026-10-19 CNN 분류 모델 통합

- 사용자 요청에 따라 분류 모델·loss·metric·Lightning Wrapper를 `src/classification/models/cnn/`으로 통합했다. 순수 모델은 `ClassificationModel(backbone="resnet50", num_classes=10, weights_path=None)`로 정의한다. 이전 ResNet50 전용 패키지와 설정을 대체하며 호환용 모듈은 두지 않는다.
- `custom`, `resnet18`, `resnet50`, `efficientnet_b0`의 구조와 forward는 로컬 `dl-lightning`의 `src/torch/tasks/classification/models/cnn/model.py`를 참조했다. 참조 파일의 SHA-256은 `92cac55b6b6ef0bf2bd7cbda193a4ae943a7a99b7afba89795b2a9e4bad7d7b9`다. 원본 파일에 별도 저작권·라이선스 헤더는 없었다. 참조 프로젝트는 수정하지 않았다.
- 참조 구현과 달리 기본 backbone은 현재 예제 동작을 이어가도록 `resnet50`으로 지정했다. torchvision 네트워크는 `weights=None`으로 생성하고 로컬 ImageNet 가중치를 strict 로드한 뒤 분류층을 교체한다. `custom`에 backbone 가중치를 전달하거나 잘못된 backbone·클래스 수를 지정하면 오류를 표시한다.
- `backbone_name`은 일반 문자열 속성이며 기존 ResNet50과 같은 `backbone.*` 파라미터 구조를 유지한다. 같은 클래스 수의 순수 가중치 복원 호환성을 유지하도록 구현했으며 실제 복원은 실행하지 않았다.
- 분류 노트북은 `BACKBONE="resnet50"`과 새 모델·Wrapper·loss 경로를 사용하고 기존 Dataset·DataModule·Trainer 흐름을 유지한다. Wrapper의 클래스 수도 `NUM_CLASSES`를 사용한다. 기존 실행 출력과 실행 횟수는 초기화했다.
- 모델 YAML은 `cnn.yaml`로 변경하고 새 모델 클래스와 backbone 인자를 명시했다. 기존 검증 코드의 import·모델 생성도 갱신했다. 새로운 테스트는 추가하지 않았다.
- ResNet50 로컬 가중치 파일의 존재와 코드 참조·파일 형식을 확인했다. 모델 import·forward·가중치 복원·학습·테스트 및 환경 재검증은 실행하지 않았고 패키지는 변경하지 않았다.

## 2026-10-19 JSON 없는 MVTec 데이터 연결

- 사용자 요청에 따라 `MVTecDataset`에서 `split_path`·`split` 인자를 제거하고 CIFAR-10과 같은 `train=True/False` 인터페이스로 변경했다. `train=True`는 원본 `train/good`, `train=False`는 원본 `test`의 모든 결함 종류를 정렬해 읽는다. 이상 이미지의 마스크 누락은 생성 시 오류로 처리한다.
- `notebooks/anomaly-mvtec-stfpm.ipynb`에서 원본 test 데이터를 정상·이상 라벨별로 섞어 valid 40%·test 60%로 나눈다. seed 42와 서로 겹치지 않는 `Subset` 인덱스를 사용한다. bottle의 분할 크기는 기존과 같은 train 209·valid 33·test 50이 되지만 구성 샘플은 이전 JSON과 일치하지 않을 수 있다.
- 원본 train은 정상만 있으므로 valid image AUROC를 계산하기 위해 원본 test에서 검증 데이터를 분리한다. 이는 프로젝트의 검증 정책이며 원본의 공식 validation 분할이 아니다.
- Dataset은 폴더 읽기만 담당하고 valid·test 분리는 노트북에서 한 번 수행한다. YAML의 valid·test 항목은 전체 평가용 Dataset 소스를 나타내며, 실행에 연결하려면 노트북처럼 외부에서 분리해야 한다. YAML 자체로 서로 다른 평가 분할을 생성하지 않는다.
- 기존 Dataset 검증 코드는 새 생성자와 원본 폴더 크기에 맞게 수정했다. 이번 변경에서는 테스트·학습을 실행하지 않았다. 아래 JSON 관련 설명은 변경 전 이력이다.

## 2026-10-19 사용자 수동 정리 후 현황

- 모델별 `lightning_cli.py`, 공통 `src/utils/lightning_cli.py`·`lightning_data.py`는 현재 없다. 아래 설정·데이터 연결과 실행·산출물 설명은 정리 전 구현 결정의 이력이다.
- 모델·Wrapper·loss·metric, Dataset·transform, YAML, Predictor, `utils/io.py`·`config.py`와 기존 검증 코드는 남아 있다.
- `notebooks/`와 `outputs/`는 비어 있다. 기존 노트북·체크포인트·로그·검증 보고서는 현재 없다.
- `THIRD_PARTY_NOTICES.md`와 `references.json`은 없다. `licenses/Apache-2.0.txt`는 남아 있으나 라이선스 원문만으로 누락된 참조 파일별 해시·고지 내용을 확인할 수는 없다.
- `__pycache__`에는 없는 소스에 대응하는 캐시도 남아 있다. `.git`은 없어 Git 이력으로 삭제 목록을 비교할 수 없다.
- 이번 확인에서는 파일 목록을 확인하고 문서를 갱신했다. 모델 실행·학습·평가·테스트, 환경과 외부 자산의 재확인은 수행하지 않았다.

현재 구조는 루트 [README.md](../../README.md), 진행 상태는 [PLAN.MD](PLAN.MD)를 따른다. 삭제한 파일의 복구나 실행 구조 변경은 이번 문서 갱신에 포함하지 않는다.

## 정리 전 2026-10-19 환경 확인 기록

- Python 3.11.8, PyTorch 2.2.1+cu118, torchvision 0.17.1+cu118, Lightning 2.5.5, jsonargparse 4.40.2, torchmetrics 1.9.0, PyYAML 6.0.3을 지정 Python에서 확인했다.
- CUDA 사용 가능, GPU는 NVIDIA RTX A4000이다. 패키지는 변경하지 않았다.
- ipykernel과 pytest는 설치되어 있고 nbformat은 없다. 노트북은 표준 JSON으로 생성하고 코드 셀 문법과 실행을 별도로 확인한다.
- CIFAR-10: `E:\datasets\cifar10\cifar-10-batches-py`.
- MVTec: `E:\datasets\mvtec`, 첫 범주는 `bottle`.
- ResNet50 pretrained: `E:\backbones\resnet50-0676ba61.pth`.
- STFPM teacher pretrained: `E:\backbones\resnet18-f37072fd.pth`.

## 참조와 차이

기존 `dl-lightning`의 CIFAR-10 Dataset·transform·ResNet50 모델·ClassificationModule·ClassificationData·CLI·Predictor·설정 유틸리티를 검토했다. `cv_boilerplate`의 anomaly Dataset·transform·metric·STFPM·설정과 anomalib의 STFPM 모델·loss·anomaly map·Lightning Wrapper도 검토했다.

로컬 `cv_boilerplate`는 기존 확인 당시 확인 가능한 HEAD 커밋이 없었다. 로컬 참조 파일의 SHA-256을 `references.json`에 기록한 이력이 있으나 해당 파일은 현재 없다. anomalib는 아래 `main` URL에서 확인한 구현을 기준으로 하며 원격 커밋 해시는 확인하지 못했다. 고정 커밋에서의 원본 동등성을 검증했다고 주장하지 않는다.

- [torch_model.py](https://github.com/open-edge-platform/anomalib/blob/main/src/anomalib/models/image/stfpm/torch_model.py)
- [lightning_model.py](https://github.com/open-edge-platform/anomalib/blob/main/src/anomalib/models/image/stfpm/lightning_model.py)
- [loss.py](https://github.com/open-edge-platform/anomalib/blob/main/src/anomalib/models/image/stfpm/loss.py)
- [anomaly_map.py](https://github.com/open-edge-platform/anomalib/blob/main/src/anomalib/models/image/stfpm/anomaly_map.py)

현재 로컬 STFPM에는 원문과 달리 자체 구현임을 설명하는 주석이 있고 anomaly map은 레이어 평균, loss는 정규화 특징의 평균 MSE다. 사용자 의도에 따라 새 구현은 anomalib 기준인 레이어 map의 곱과 공간 크기로 나눈 sum MSE를 사용한다. 기존 로컬 구현과 수치가 달라지는 의도적인 변경이다.

anomalib의 `TimmFeatureExtractor`는 torchvision ResNet18의 `layer1`·`layer2`·`layer3` 추출로 대체한다. `InferenceBatch`는 같은 의미의 `pred_score`·`anomaly_map` dict로 대체한다. tiling은 초기 예제 범위에 포함하지 않는다. teacher는 eval과 gradient 비활성 상태를 유지하고 student만 학습한다. loss와 anomaly map 계산은 anomalib의 수식을 따른다.

## 정리 전 설정과 데이터 연결

- native LightningCLI의 반복 `--config`로 `default.yaml` → 데이터 YAML → 모델 YAML 순서로 결합한다. 뒤의 설정과 그 뒤에 지정한 CLI 인자가 우선한다. 별도 YAML 상속 프레임워크를 추가하지 않는다.
- 모델·loss·Dataset·transform은 YAML의 `class_path`·`init_args`로 외부 주입한다.
- 공통 Dataset 연결은 `src/utils/lightning_data.py`의 DataModule에 둔다. 이 파일만 Lightning에 의존하며 순수 설정·입출력 유틸리티는 이를 import하지 않는다.
- CIFAR-10은 원본 학습 데이터를 seed 42로 train 45,000·valid 5,000으로 나누고 test 10,000을 유지한다. 분할은 DataModule에서 한 번만 수행하며 train·valid의 transform은 별도다.
- MVTec bottle은 원본 `configs/splits/mvtec_bottle.json`을 읽기 전용으로 참조한다. split 중복·알 수 없는 ID·이미지와 마스크 누락을 검사한다. train은 정상만 사용한다.
- 분류 배치는 `(images, targets)`, anomaly 배치는 `(images, {label, mask})`다. anomaly train의 target은 빈 dict이며 평가 마스크는 이진 값이다.
- 분류는 loss·micro accuracy·macro F1, anomaly는 image AUROC·pixel AUROC를 기록한다. 이상/정상이 모두 없는 짧은 평가에서는 AUROC를 계산하지 않고 경고한다.
- 학습·평가 transform은 Dataset에서 적용한다. Predictor의 배치 입력은 이미 변환된 NCHW 텐서이며 transform을 재적용하지 않는다.

## 정리 전 실행과 산출물

- 모델별 `lightning_cli.py`는 공통 CLI 연결을 사용한다. STFPM optimizer 기본값은 anomalib처럼 student 대상 SGD(lr=0.4, momentum=0.9, weight_decay=0.001)다.
- `--run_dir`로 실행 위치를 지정한다. 생략하면 `outputs` 아래 고유 실행 폴더를 만든다.
- 각 실행 폴더 바로 아래에 단계별 설정, CSV 로그, best/last 체크포인트, 마지막 모델의 순수 `model.pt`, 단계별 metric JSON과 `predictions.pt`를 저장한다.
- 학습 로그를 보존하기 위해 기존 fit 설정이 있는 실행 폴더에서는 새 fit을 거부한다. checkpoint로 재개할 때도 새 실행 폴더를 지정한다. 평가·예측은 기존 실행 폴더와 `--ckpt_path`를 지정할 수 있으며 학습 CSV를 변경하지 않는다.
- 초기 검증은 작은 배치·짧은 학습으로 수행한다. 이를 모델 성능 검증이나 전체 학습 완료로 해석하지 않는다.
