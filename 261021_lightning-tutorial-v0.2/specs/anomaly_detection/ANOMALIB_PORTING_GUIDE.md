# anomalib 모델 이식 가이드

이 문서는 anomalib의 이미지 이상 탐지 모델을 `src/anomaly_detection`에 추가할 때 적용할 절차다. 현재 구현 계약은 [SPEC.md](SPEC.md), 이미 선택한 설계와 원본 대비 차이는 [DECISIONS.md](DECISIONS.md), 실행 명령은 [USAGE.md](USAGE.md), 확인 상태는 [PROGRESS.md](PROGRESS.md)에 둔다.

## 원본을 먼저 고정한다

1. 이식할 모델의 anomalib 커밋과 `torch_model.py`, `lightning_model.py`, 보조 파일의 경로를 기록한다. 현재 STFPM·EfficientAD는 `baf5e5fe12bc73cd520523046ba1d68279462e69`을 참조한다. 이후 main 브랜치의 변경을 기존 구현의 계약으로 조용히 가져오지 않는다.
2. 순수 모델의 생성자·forward 입력과 반환값, 학습·평가 모드별 연산, loss, optimizer, 보정 통계와 checkpoint 상태를 먼저 읽는다.
3. 재사용한 코드에는 원본 저작권·SPDX와 참조 커밋을 남긴다. 원본과 달라지는 동작은 [DECISIONS.md](DECISIONS.md)에 이유와 함께 기록한다. 원본 docstring은 프로젝트 규칙에 맞춰 제거하고 필요한 설명만 간결한 영어 주석으로 남긴다.

참조 경로: [STFPM 순수 모델](https://github.com/open-edge-platform/anomalib/blob/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/models/image/stfpm/torch_model.py)·[STFPM 래퍼](https://github.com/open-edge-platform/anomalib/blob/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/models/image/stfpm/lightning_model.py), [EfficientAD 순수 모델](https://github.com/open-edge-platform/anomalib/blob/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/models/image/efficient_ad/torch_model.py)·[EfficientAD 래퍼](https://github.com/open-edge-platform/anomalib/blob/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/models/image/efficient_ad/lightning_model.py).

## 파일과 책임을 나눈다

| 위치 | 책임 |
|---|---|
| `models/<model>/model.py` | anomalib `torch_model.py`에 대응하는 순수 `nn.Module`, 모델 연산과 출력 |
| `models/<model>/loss.py`, `anomaly_map.py` 등 | 원본에 실제로 분리된 모델별 연산만 배치 |
| `models/<model>/lightning_model.py` | native `LightningModule`, 단계별 Hook·metric·optimizer·보정 연결 |
| `models/common/` | 여러 모델이 공유하는 `InferenceBatch`, `TimmFeatureExtractor`, `Tiler`, metric과 필수 유틸리티 |
| `data/<dataset>/`, `data/common/` | Dataset·Transform과 LightningDataModule, 데이터셋별 읽기 및 공통 분할 |
| `configs/models/<model>.yaml` | 실제 모델 래퍼의 생성자 인자와 필요한 데이터 설정 |
| `trainers/` | 모델·데이터 선택, 로컬 경로 확인, logger·callback·Trainer 생성 |

`model.py`에서 Lightning을 import하지 않는다. 순수 모델의 forward에 학습 Hook이나 CLI 동작을 넣지 않는다. 래퍼는 생성자 설정으로 순수 모델·loss·metric을 만들고 알고리즘 연산을 다시 작성하지 않는다. anomalib의 `AnomalibModule`, `Engine`, 전용 `Batch`와 실행 계층은 가져오지 않는다. 이 프로젝트의 배치는 `(images, targets)`이고 원본의 `InferenceBatch` 출력 계약은 `models/common`에서 제공한다.

## 생성자 인자를 맞춘다

순수 모델 생성자는 해당 커밋의 anomalib `torch_model.py`에 정의된 모델 생성자 인자와 순서를 따른다. `weights_path`, `tiler`처럼 이 프로젝트에서 필요한 연결을 순수 모델 생성자에 추가하지 않는다. native Lightning 래퍼는 해당 `lightning_model.py`의 모델·학습 인자를 따르되 `pre_processor`, `post_processor`, `evaluator`, `predictor`, `visualizer`는 제외한다. 원본에 없는 옵션을 편의상 래퍼 생성자에 미리 넣지 않는다.

| 현재 모델 | 순수 모델 인자 | native Lightning 래퍼 인자 |
|---|---|---|
| STFPM | `layers`, `backbone` | `backbone`, `layers` |
| EfficientAD | `teacher_out_channels`, `model_size`, `padding`, `pad_maps` | `imagenet_dir`, `teacher_out_channels`, `model_size`, `lr`, `weight_decay`, `padding`, `pad_maps` |

STFPM 순수 모델의 `layers`는 필수이고 래퍼의 기본값은 `layer1`·`layer2`·`layer3`이다. STFPM의 SGD 값은 원본처럼 래퍼 내부에 고정한다. EfficientAD의 학습률 인자명은 `lr`이다. 프로젝트의 로컬 데이터 경로 정책 때문에 EfficientAD 래퍼의 `imagenet_dir` 기본값은 `None`이며, 학습 시 `get_dataset_dir("imagenette", paths)`로 해석한다. 원본과 다른 기본값이나 입력 형식은 명시적으로 문서화한다.

## 로컬 자산을 연결한다

가중치와 데이터는 자동 다운로드하지 않는다. `paths.toml`의 `[backbones]`에는 backbone 이름과 파일 경로를, `[datasets]`에는 데이터셋 이름과 디렉터리 경로를 둔다. 경로 처리는 `os.path`를 사용한다.

- STFPM teacher는 공통 `TimmFeatureExtractor`에서 `get_backbone_dir(backbone, load_paths_config())`로 로컬 가중치를 찾아 로드한다. student는 pretrained 없이 생성한다. teacher는 `train()` 호출 후에도 eval 상태와 `requires_grad=False`를 유지한다.
- EfficientAD 순수 모델은 teacher 가중치를 자동 로드하지 않는다. 새 학습에서는 래퍼가 `get_backbone_dir(f"efficientad_{model_size}", load_paths_config())`로 PDN teacher 파일을 찾는다. 학습된 전체 `state_dict` 또는 Lightning checkpoint를 복원할 때는 포함된 teacher·통계·quantile을 사용한다.
- EfficientAD의 Imagenette penalty 입력은 `datasets.imagenette`로 등록한 루트의 `train/<class>`만 읽는다. 이상 탐지 데이터의 `normalize`는 false로 두어 모델 내부 정규화와 중복되지 않게 한다.

현재 가중치 로더는 기본 `paths.toml`을 직접 읽는다. 별도 `--paths_file`에 다른 backbone 파일을 지정하는 기능이 필요하면, 생성자 인자를 늘리기 전에 경로 전달 방식을 설계하고 실제 로더까지 같은 설정을 사용하는지 확인한다.

## native Lightning으로 연결한다

원본의 학습·검증·평가 순서를 순수 모델과 래퍼 사이에 배치한다. `training_step`은 순수 모델 결과로 loss를 계산하고, `validation_step`·`test_step`은 원본 출력으로 metric을 갱신한다. metric 상태는 단계별로 분리하고 epoch 경계에서 초기화한다. `configure_optimizers`에는 원본의 대상 파라미터와 학습률·스케줄러 동작을 반영한다.

STFPM은 student만 SGD로 갱신한다. EfficientAD는 teacher와 보정 파라미터를 고정하고 student·autoencoder만 Adam으로 갱신한다. EfficientAD의 teacher 통계는 정상 train, map quantile은 정상 valid로 계산하며 test는 보정에 사용하지 않는다. 평가·예측은 checkpoint의 보정값을 사용한다. 원본과 다른 통계 누적, scheduler 연결, 입력 크기 제한은 [DECISIONS.md](DECISIONS.md)에 기록한다.

Tiler는 STFPM의 선택적 모델 속성으로 연결한다. 순수 모델 생성 후 `model.tiler = Tiler(...)`로 지정하고 CLI에서는 `--tiler` 최상위 설정을 사용한다. Lightning checkpoint에는 Tiler 설정을 별도 항목으로 저장·복원한다. 순수 `state_dict`에는 Tiler 설정이 없으므로 독립 추론 시 같은 설정을 다시 연결한다.

## CLI·문서·확인 범위

새 모델을 추가할 때 실제 구현에 필요한 `configs/models/<model>.yaml`과 task의 `trainers/lightning_cli.py` 선택 분기만 추가한다. 선택값은 `selection.model`에, 모델 생성자 인자는 `model`에 둔다. 생성자에 없는 값을 `model` YAML로 전달하지 않는다. logger 이름·checkpoint 기준과 설정 저장은 기존 `AnomalyLitTrainer`를 따른다. 프로젝트 루트에 새 진입점이나 빈 파일을 만들지 않는다.

변경 후 다음 항목을 각각 확인하고 [PROGRESS.md](PROGRESS.md)에 실제 결과만 기록한다.

1. 원본과 현재 생성자 인자·기본값, 순수 모델의 import·forward·출력 형태, teacher 고정 및 가중치 누락 오류를 확인한다.
2. Dataset의 정상·이상 라벨, 마스크 연결, 전처리와 valid/test 분할을 확인한다. 공식 test를 나눴다면 전체 벤치마크 수치와 비교하지 않는다.
3. native `fit`, `validate`, `test`, `predict`와 checkpoint 복원, 독립 `state_dict` 추론을 구분해 확인한다. 실행하지 않은 단계는 완료로 기록하지 않는다.
4. [SPEC.md](SPEC.md)에 최종 계약을, [DECISIONS.md](DECISIONS.md)에 원본과 달라진 이유를, [USAGE.md](USAGE.md)에 실행 명령을 갱신한다. Markdown은 UTF-8로 저장하고 엄격한 디코딩과 한글 본문을 확인한다.
