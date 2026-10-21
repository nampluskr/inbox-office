# lightning-tutorial

순수 PyTorch 모델과 데이터 처리를 유지하면서 학습·검증·평가·예측을 Lightning으로 실행하는 예제 프로젝트입니다. 모델 알고리즘과 Lightning Wrapper를 분리하고, 학습한 순수 모델 가중치를 공통 Predictor로 복원할 수 있습니다.

## 지원 범위

| Task | 데이터셋 | 모델 |
|---|---|---|
| Classification | MNIST, CIFAR-10 | MLP, custom CNN, ResNet18, ResNet50, EfficientNet-B0 |
| Anomaly detection | MVTec AD, BTAD | STFPM, EfficientAD |

지원 목록은 구현 범위입니다. 실행 확인 범위는 task별 진행 문서에서 구분합니다. VisA와 별도 binary classification task는 후속 기획입니다.

## 준비

Python 3.11 환경과 PyTorch·torchvision·Lightning·torchmetrics·PyYAML·jsonargparse의 signatures 지원·timm이 필요합니다. PyTorch와 torchvision은 사용하는 CPU·CUDA 환경에 맞게 함께 준비하세요. 프로젝트의 확인된 패키지 버전은 [classification 진행 상태](specs/v0.2/classification/PROGRESS.md)와 [anomaly detection 진행 상태](specs/v0.2/anomaly_detection/PROGRESS.md)에 기록되어 있습니다.

PyTorch·torchvision 준비 후, 기존 확인 환경의 나머지 의존성은 다음처럼 설치할 수 있습니다.

```powershell
python -m pip install lightning==2.5.5 torchmetrics==1.9.0 PyYAML==6.0.3 "jsonargparse[signatures]==4.40.2" timm==1.0.30
```

[paths.example.toml](paths.example.toml)을 프로젝트 루트의 `paths.toml`로 복사하고 데이터셋 디렉터리와 pretrained 가중치 파일 경로를 수정하세요. 로컬 설정 파일은 Git에서 제외됩니다. 데이터와 모델 가중치는 자동 다운로드하지 않습니다.

이하 `python`은 필요한 패키지가 설치된 환경의 실행 파일입니다. 모든 명령은 프로젝트 루트에서 실행합니다.

## 빠른 시작

MNIST·MLP 학습:

```powershell
python -m src.classification.trainers.lightning_cli fit --data mnist --model mlp
```

MVTec bottle·STFPM 학습:

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data mvtec --data.category bottle --model stfpm --model.backbone resnet18
```

CLI의 `fit`은 학습을 수행합니다. 평가·예측은 `validate`·`test`·`predict`로 실행하며, 저장한 설정과 checkpoint를 재사용합니다. Python 예제는 학습 후 best checkpoint 테스트와 순수 가중치 저장까지 수행합니다.

## 결과 저장

기본 저장 위치는 `outputs/<실험 이름>/version_*/`입니다.

| 파일 | 용도 |
|---|---|
| `config.yaml`, `hparams.yaml` | 실행 설정과 모델 hyperparameter |
| `metrics.csv` | 학습·검증·평가 지표 |
| `checkpoints/best.ckpt`, `checkpoints/last.ckpt` | Lightning 복원·학습 재개 |
| `test_metrics.json`, `model.pt` | Python 예제의 테스트 결과와 best 순수 모델 가중치 |

## 문서

| 읽을 내용 | Classification | Anomaly detection |
|---|---|---|
| 사용법 | [USAGE](specs/v0.2/classification/USAGE.md) | [USAGE](specs/v0.2/anomaly_detection/USAGE.md) |
| 목적·범위 | [INTENT](specs/v0.2/classification/INTENT.md) | [INTENT](specs/v0.2/anomaly_detection/INTENT.md) |
| 구조·인터페이스 | [SPEC](specs/v0.2/classification/SPEC.md) | [SPEC](specs/v0.2/anomaly_detection/SPEC.md) |
| 설계 결정 | [DECISIONS](specs/v0.2/classification/DECISIONS.md) | [DECISIONS](specs/v0.2/anomaly_detection/DECISIONS.md) |
| 진행·검증 상태 | [PROGRESS](specs/v0.2/classification/PROGRESS.md) | [PROGRESS](specs/v0.2/anomaly_detection/PROGRESS.md) |

공통 개발 기준은 [INTENT](specs/v0.2/INTENT.md)·[SPEC](specs/v0.2/SPEC.md)·[DECISIONS](specs/v0.2/DECISIONS.md)를 따릅니다. 이전 구현 이력은 [v0.1 문서](specs/v0.1/DECISIONS.MD)에 보존합니다. 기존 `notebooks/` 예제는 이전 import를 포함하므로 현행 실행에는 task별 CLI와 `examples/`를 사용하세요.

## 참조와 라이선스

STFPM·EfficientAD와 공통 특징 추출·타일링 구현은 [anomalib](https://github.com/open-edge-platform/anomalib)을 참조했습니다. 고정 커밋과 원본 대비 변경 사항은 [anomaly detection 설계 결정](specs/v0.2/anomaly_detection/DECISIONS.md)에 기록합니다. 재사용 코드의 저작권·SPDX 표기와 [Apache-2.0 라이선스 원문](specs/v0.1/licenses/Apache-2.0.txt)을 유지합니다.
