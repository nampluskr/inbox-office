# v0.3 Lightning Wrapper 설계 초안

## 사용자 의도

- visionlab의 `XXXLitModel`은 순수 PyTorch 모델을 감싸는 native Lightning Wrapper로 정의한다.
- Wrapper는 `lightning.pytorch.LightningModule`을 직접 상속하고 anomalib 클래스는 import하거나 상속하지 않는다.
- 생성자 인자 이름·순서·기본값은 대응하는 anomalib 2.0.0의 `lightning_model.py`와 동일하게 유지한다.
- PreProcessor·PostProcessor·Evaluator·Visualizer 인자는 원본처럼 `True`·`False` 또는 구성요소 객체를 받는다. 객체와 Enum은 visionlab에서 정의한 타입을 사용한다.
- 모델 알고리즘을 Wrapper에 중복 구현하지 않는다. 순수 모델·loss·전처리·후처리·평가·이미지 생성은 Lightning 없이 사용할 수 있게 한다.
- Wrapper가 단계별 처리 순서, optimizer, 보정과 metric 상태, 결과 전달과 checkpoint 연결을 관리한다.
- Trainer의 평가 실행과 metric 계산을 구분하고, Evaluator는 기존 순수 metric 또는 TorchMetrics를 묶는 최소 구성요소로 유지한다.
- PostProcessor의 상세 설계는 이 문서에 작성하고 데이터의 공간 변환·배치·Tiler 좌표계는 [DATA.md](DATA.md)와 연결한다.
- STFPM·EfficientAD의 학습·보정·평가 차이를 구분하고 코드 스켈레톤으로 연결 구조를 제시한다.
- 이 초안은 `WRAPPER.md` 한 개에 작성하고 다른 문서와 실행 코드는 수정하지 않는다.
- 로컬 데이터·가중치만 사용하며 자동 다운로드하거나 원본 자산을 수정하지 않는다.
- 문서는 한국어로 작성하고 이모지를 사용하지 않는다. 코드 설명은 간결한 영어 주석으로 작성한다.
- Markdown은 UTF-8로 저장하고 엄격한 UTF-8 디코딩과 한글 본문을 확인한다.

작성일: 2026-10-22. 상태: 설계 초안, 구현 미착수.

아래 경로·타입·Hook 스켈레톤은 목표 구조다. 실제 구현이나 실행 검증이 완료되었다는 뜻이 아니다. 생략한 부분은 `...`으로 표현하며 완전한 실행 코드를 제공하지 않는다.

이번 사용자 요청은 기존 v0.3 문서의 처리 객체 주입 금지와 시각화 기본 비활성 계약을 변경한다. 이 초안에서는 **원본과 같은 구성요소 객체 입력 및 `visualizer=True` 기본값**을 우선한다. 기존 문서와 코드는 이번 작업에서 변경하지 않으므로 향후 구현 시 해당 차이를 함께 정리해야 한다.

## 1. 구조와 책임

```text
visionlab/anomaly_detection/
  models/
    stfpm/
      model.py                # Pure STFPMModel
      loss.py                 # Pure STFPMLoss
      lightning_model.py      # STFPMLitModel
    efficientad/
      model.py                # Pure EfficientAdModel and model-size enum
      lightning_model.py      # EfficientAdLitModel
    components/tiling/
      tiler.py                # Pure Tiler
  common/
    inference_batch.py
    pre_processor.py
    post_processor.py
    evaluator.py
    visualizer.py             # Pure ImageVisualizer
    lightning_visualizer.py   # Native file-saving Callback
```

| 구성 | 책임 |
|---|---|
| 순수 모델 | 모델 구조, 특징·loss 관련 모델 연산, raw 예측과 모델 고유 영속 상태 |
| 순수 loss | 원본 모델이 별도 loss를 제공하는 경우 해당 계산 |
| PreProcessor | 배치 입력 확인과 모델별 정규화 |
| PostProcessor | 검증 기반 통계·임계값 보정, 점수 정규화와 이진 예측 |
| Evaluator | 지표의 update·compute·reset |
| ImageVisualizer | 표시 이미지·heatmap·mask·overlay 생성 |
| Lightning Wrapper | 객체 조립, 단계별 Hook, optimizer·scheduler, 보정·metric 연결과 결과 반환 |
| 시각화 Callback | Wrapper가 반환한 완료 결과를 소비하여 로컬 파일 저장 |

Wrapper끼리 공통 기반 클래스를 미리 추가하지 않는다. 실제 공유되는 순수 기능은 위 구성요소에서 재사용한다. 패키지 초기화가 Lightning Wrapper를 자동 import하여 순수 모델 사용에 Lightning을 요구하지 않게 한다.

## 2. anomalib과 동일한 생성자

### 인자 호환 범위

기준은 설치된 anomalib **2.0.0**의 각 모델 `lightning_model.py`다. 인자 이름·위치·기본값과 의미를 맞추며 모든 모델에 공통 인자 목록을 억지로 적용하지 않는다. `model`·`loss` 객체나 원본에 없는 `weights_path`·`teacher_path`·`tiler` 인자를 추가하지 않는다.

경로는 `str`과 `os.PathLike`를 수용하고 내부 처리는 `os.fspath()`·`os.path`를 사용한다. 원본의 pathlib 타입 주석을 그대로 import하지 않는다. `EfficientAdModelSize`는 visionlab의 순수 Enum으로 정의하며 `S="small"`, `M="medium"`과 해당 문자열을 지원한다.

다음 스켈레톤의 `PreProcessor`·`PostProcessor`·`Evaluator`는 visionlab 순수 구성요소다. `Visualizer`는 visionlab의 `ImageVisualizer`를 가리키는 import 별칭이다. anomalib 객체나 anomalib Enum을 입력하는 호환 계층은 추가하지 않는다.

### STFPM

```python
# Constructor signature adapted from anomalib 2.0.0.
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

import lightning.pytorch as pl

from visionlab.anomaly_detection.common.evaluator import Evaluator
from visionlab.anomaly_detection.common.post_processor import PostProcessor
from visionlab.anomaly_detection.common.pre_processor import PreProcessor
from visionlab.anomaly_detection.common.visualizer import ImageVisualizer as Visualizer


class STFPMLitModel(pl.LightningModule):
    def __init__(
        self,
        backbone: str = "resnet18",
        layers: Sequence[str] = ("layer1", "layer2", "layer3"),
        pre_processor: PreProcessor | bool = True,
        post_processor: PostProcessor | bool = True,
        evaluator: Evaluator | bool = True,
        visualizer: Visualizer | bool = True,
    ) -> None:
        super().__init__()
        # Create the pure STFPMModel and STFPMLoss internally.
        # Resolve each component from True, False or a visionlab instance.
        # Save reconstructible settings separately from live objects.
        ...
```

STFPM 학습률은 원본 생성자 인자가 아니므로 Wrapper에 새 `lr` 인자를 추가하지 않는다. optimizer는 원본과 같이 student 파라미터만 대상으로 생성한다.

### EfficientAD

아래 코드의 처리 구성요소 import는 위 STFPM 스켈레톤과 동일하다.

```python
# Constructor signature adapted from anomalib 2.0.0.
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import PathLike

import lightning.pytorch as pl

from visionlab.anomaly_detection.models.efficientad.model import EfficientAdModelSize


class EfficientAdLitModel(pl.LightningModule):
    def __init__(
        self,
        imagenet_dir: PathLike[str] | str = "./datasets/imagenette",
        teacher_out_channels: int = 384,
        model_size: EfficientAdModelSize | str = EfficientAdModelSize.S,
        lr: float = 0.0001,
        weight_decay: float = 0.00001,
        padding: bool = False,
        pad_maps: bool = True,
        pre_processor: PreProcessor | bool = True,
        post_processor: PostProcessor | bool = True,
        evaluator: Evaluator | bool = True,
        visualizer: Visualizer | bool = True,
    ) -> None:
        super().__init__()
        # Resolve model size, create the pure model and resolve components.
        # Keep ImageNette setup and model statistics in their training hooks.
        # Save reconstructible settings separately from live objects.
        ...
```

### 구성요소 선택

| 입력 | 처리 |
|---|---|
| `True` | 해당 모델의 기본 구성요소를 내부 생성 |
| `False` | 해당 구성요소 비활성화 |
| 올바른 visionlab 객체 | 전달한 객체 사용 |
| `None`·잘못된 타입 | 오류 보고 |

단순 truthiness로 객체를 판별하지 않고 bool과 구성요소 타입을 구별한다. 기본 구성은 `configure_pre_processor()`·`configure_post_processor()`·`configure_evaluator()`·`configure_visualizer()`와 같은 모델별 생성 메서드로 표현할 수 있다. 이 메서드들은 공통 anomalib 기반 클래스를 요구하지 않는다.

`pre_processor=False`이면 Wrapper는 정규화를 수행하지 않는다. 호출자가 모델에 맞는 입력을 준비해야 하며, 정규화 전 시각화 이미지가 필요하면 해당 원본도 별도로 확보해야 한다. EfficientAD는 어떤 입력 경로에서도 외부 ImageNet 정규화를 중복 적용하지 않는다.

`post_processor=False`이면 raw 예측만 반환하고 processed 결과와 후처리 F1은 생성하지 않는다. `evaluator=False`이면 metric을 생성하지 않으며 Trainer의 checkpoint monitor도 존재하지 않는 지표를 요구하지 않도록 실행 조립에서 맞춘다. `visualizer=False`이면 생성·저장 Callback을 연결하지 않는다.

## 3. 처리 순서와 Lightning Hook

공통 입력은 [DATA.md](DATA.md)의 `(images, target)` 배치다. 원본 anomalib Batch를 요구하지 않으며 생성자 호환이 Batch 타입이나 반환 객체의 동일성까지 의미하지는 않는다. 모델 알고리즘 입력에는 이미지와 모델이 실제 요구하는 값만 전달한다.

```text
train:
Dataset Transform → PreProcessor → 모델 학습 forward → loss → optimizer

fit validation:
모델 고유 보정 → PreProcessor → raw 예측
             → raw metric 갱신 + PostProcessor 보정 수집 → epoch 종료에 확정

test/predict:
Dataset Transform → PreProcessor → raw 예측 → PostProcessor
                 → metric 또는 결과 반환 → 시각화 Callback
```

| 단계·Hook | 실행 책임 |
|---|---|
| `on_train_start` | EfficientAD의 로컬 teacher·Imagenette 준비와 필요한 teacher 통계 계산 |
| `training_step` | 전처리 후 모델별 forward·loss, 학습 로그와 loss 반환 |
| `on_validation_start` | fit validation에서 필요한 EfficientAD map quantile 계산. 독립 validate에서는 저장 상태 유지 |
| `on_validation_epoch_start` | valid metric 초기화, 실제 fit validation일 때만 후처리 수집 상태 초기화 |
| `validation_step` | raw 예측·raw AUROC 갱신, 실제 fit validation에서만 후처리 수집 |
| `on_validation_epoch_end` | 실제 fit validation의 후처리 상태 확정, valid metric 집계·로그 |
| `on_test_epoch_start`·`test_step`·`on_test_epoch_end` | test metric 초기화, 저장된 후처리 적용, raw AUROC·후처리 F1 집계 |
| `predict_step` | 저장 상태로 예측·후처리하고 원본 대응 정보를 포함한 결과 반환. 정답 없이 실행 가능 |
| `on_save_checkpoint`·`on_load_checkpoint` | 추가 설정과 상태의 저장·복원 연결. nn.Module buffer는 state_dict로 보존 |
| `configure_callbacks` | 활성 Visualizer를 사용하는 native 저장 Callback 연결 |

fit validation과 standalone validate는 native Trainer 실행 상태로 구별한다. sanity validation은 학습 후 보정 결과로 취급하지 않으며 영속 보정 상태를 덮어쓰지 않는다. EfficientAD의 초기 실행은 원본과 같이 `num_sanity_val_steps=0`을 Trainer에 명시한다.

전처리는 Wrapper의 raw 모델 호출 경로에서 한 번 수행한다. train·validation·test·predict가 공유하는 raw 호출 메서드는 PreProcessor와 순수 모델까지만 실행하고, PostProcessor는 단계별 평가 경로에서 명시적으로 적용한다. 이로써 fit validation의 raw 수집에 이미 clipping한 결과가 들어가는 것을 막는다. `forward(images)`는 이 raw 호출 계약을 사용하며 anomalib의 후처리 포함 forward와의 차이를 기록한다.

독립 validate는 기본 raw AUROC만 계산한다. standalone validate·test·predict에서 teacher 통계·quantile·공통 후처리 임계값을 다시 맞추지 않는다. fit 중 수집·확정한 상태만 checkpoint에 저장한다.

### Hook 연결 스켈레톤

다음 메서드들은 두 Wrapper에 필요한 공통 호출 관계를 보여준다. 실제 모델별 training_step·보정 처리는 각 모델 클래스에 둔다. `self.evaluator`는 valid/test 누적 상태를 분리해 관리한다.

```python
def forward(self, images):
    inputs = self.pre_processor(images) if self.pre_processor is not None else images
    return self.model(inputs)


def on_validation_epoch_start(self):
    # Reset valid metrics and only reset calibration for real fit validation.
    ...


def validation_step(self, batch, batch_idx):
    images, target = batch
    raw = self(images)
    # Update valid raw metrics when evaluator is enabled.
    # Collect calibration only during real fit validation.
    ...


def on_validation_epoch_end(self):
    # Finalize calibration before the corresponding checkpoint is saved.
    # Compute and log valid metrics, then clear temporary collection state.
    ...


def test_step(self, batch, batch_idx):
    images, target = batch
    raw = self(images)
    processed = self.post_processor(raw) if self.post_processor is not None else None
    # Update test raw AUROC and available processed F1.
    # Return raw, processed, display images and source metadata.
    ...


def predict_step(self, batch, batch_idx, dataloader_idx=0):
    # Run the same prediction path without requiring labels or masks.
    ...
```

## 4. PostProcessor 상세 설계

PostProcessor는 순수 `nn.Module`이며 Lightning Hook을 갖지 않는다. Wrapper가 검증 데이터 수집·상태 확정·예측 적용을 제어한다. 계산 알고리즘은 PostProcessor에 유지한다.

### 보정과 정규화

image score와 pixel anomaly map에 대해 각각 raw min·max, F1 기반 raw 임계값과 유효 상태를 관리한다. fit validation 전체 표본을 기준으로 보정하며 배치별 임계값을 평균하지 않는다. 임계값 후보·동률 규칙은 원본 anomalib 2.0.0과 대조해 구현 시 고정한다.

기본 정규화·threshold는 활성화한다. 정규화는 임계값 중심 변환을 기준으로 한다.

```text
normalized = clamp((raw - threshold) / (maximum - minimum) + 0.5, 0, 1)
```

정규화만 사용하고 threshold 계산을 끈 경우 중심값은 `(minimum + maximum) / 2`다. 이 경우 이진 예측은 만들지 않는다. threshold가 활성화된 경우 정규화 후 값의 `0.5` 초과 또는 정규화하지 않은 raw 값의 저장 임계값 초과로 이진 예측한다.

raw score·map을 제자리에서 수정하지 않고 processed 결과를 별도로 만든다. 정규화 score를 확률로 가정하지 않는다. 단순 `(raw-min)/(max-min)` 정규화로 바꾸지 않는다.

### 상태와 오류

| 구분 | 상태·동작 |
|---|---|
| 영속 상태 | image/pixel min·max·임계값, 각 경로의 유효 상태와 처리 활성 설정 |
| 임시 상태 | 현재 validation epoch의 통계 누적과 임계값 선택용 수집 결과 |
| 평가·예측 | 영속 상태 읽기 전용, 현재 test 배치로 재보정하지 않음 |
| 누락 상태 | 활성 처리에 필요한 상태가 없으면 오류. 후처리를 끈 raw 경로에는 요구하지 않음 |
| 비유한 값·상수 범위 | 유효하지 않은 상태로 표시. max=min인 정규화 경로는 오류 |
| 정답 부족 | image/pixel 각각 임계값 보정 가능성을 판단. 라벨·마스크 또는 두 클래스가 없으면 미보정 |

image 임계값을 pixel에 자동 재사용하지 않는다. 보정에 실패한 epoch의 일부 상태를 이전 값과 조용히 섞지 않는다. 영속 상태는 epoch 수집 결과를 검증한 뒤 일관되게 확정한다. 활성 경로를 보정할 수 없으면 원인을 보고하고 해당 상태를 사용하는 실행을 허용하지 않는다.

### 순수 PostProcessor 스켈레톤

아래 메서드 이름은 visionlab 연결을 위한 초안이며 anomalib PostProcessor의 전체 API 호환을 약속하지 않는다.

```python
from torch import nn


class PostProcessor(nn.Module):
    def __init__(self, normalization=True, threshold=True):
        super().__init__()
        # Register persistent calibration buffers and processing settings.
        ...

    def reset_collection(self):
        # Clear temporary epoch data without changing fitted buffers.
        ...

    def update(self, raw, target):
        # Collect detached validation statistics and threshold inputs.
        ...

    def finalize(self):
        # Validate the full epoch, then commit fitted calibration buffers.
        ...

    def forward(self, raw):
        # Apply fitted state and return separate processed predictions.
        ...
```

## 5. Evaluator・Visualizer와 결과 전달

### Trainer·Wrapper·Evaluator의 역할

native `Trainer.validate()`·`test()`는 평가 루프와 Hook 호출을 제공하지만 모델에 맞는 AUROC·F1을 자동 선택하거나 예측·정답 필드를 연결하지 않는다. 해당 연결은 LightningModule 또는 평가 구성요소가 정의해야 한다.

| 구성요소 | 담당 기능 |
|---|---|
| Trainer | 평가 루프, 장치·분산 실행, 단계별 Hook 호출과 로그 전달 |
| Lightning Wrapper | raw·processed 예측과 정답 선택, Evaluator 호출, `self.log_dict()` 로깅 |
| 순수 metric 또는 TorchMetrics | AUROC·F1 등 지표 계산, 표본·픽셀 누적 상태 관리 |
| visionlab Evaluator | valid/test별 지표 구성과 `update`·`compute`·`reset` 조립 |

별도 Evaluator는 Lightning의 필수 요소가 아니다. Wrapper가 metric 객체를 직접 사용할 수도 있다. visionlab에서는 원본과 같은 `evaluator=True / False / 객체` 생성자 계약, 여러 모델의 평가 연결 재사용, Lightning 없는 순수 PyTorch 평가를 위해 얇은 Evaluator를 유지한다. 새 평가 루프나 metric 알고리즘을 구현하는 목적은 아니다.

anomalib 2.0.0의 Evaluator는 `nn.Module`과 `Callback`을 함께 상속하여 배치 종료 Hook에서 metric을 갱신하고 epoch 종료 Hook에서 로깅한다. visionlab Evaluator는 순수 `nn.Module`로 정의하고 Trainer 참조·Lightning Hook·로깅·파일 저장을 포함하지 않는다. native Hook과 로깅은 Wrapper에 둔다.

```text
Trainer 평가 루프
  → Wrapper: 예측·정답 필드 연결
  → Evaluator: 단계별 metric 갱신·전체 집합 집계
  → Wrapper: self.log_dict()로 최종 지표 기록
```

### 지표 입력과 상태

Evaluator는 순수 metric을 재사용하며 valid/test 상태를 분리한다. 기본 validation은 raw Image·Pixel AUROC, test는 raw Image·Pixel AUROC와 후처리된 Image·Pixel F1이다. 후처리가 clipping한 값을 raw AUROC에 사용하지 않는다. F1은 저장 임계값으로 만든 bool 예측을 사용한다.

정답이 없거나 AUROC가 단일 클래스라 계산 불가인 경우 사유를 기록하고 0으로 채우지 않는다. threshold 또는 PostProcessor를 끄면 해당 F1을 생략한다. 같은 validation에서 선택한 임계값의 F1을 독립 테스트 성능으로 보고하지 않는다.

| API | 입력·결과 |
|---|---|
| `reset(stage)` | `"valid"` 또는 `"test"`의 누적 상태만 초기화 |
| `update(stage, raw, processed, target)` | raw score·map, 선택적 processed 예측, 정답을 해당 단계의 metric에 전달 |
| `compute(stage)` | 해당 단계의 전체 평가 집합으로 계산한 지표명→scalar Tensor 매핑 반환 |

valid/test는 서로 다른 metric 인스턴스를 사용한다. `processed=None`이어도 raw 지표는 계산 가능하며, 후처리 F1은 필요한 bool 예측이 있을 때만 계산한다. mask가 없으면 pixel 지표를 계산하지 않는다. 생략·계산 불가 사유는 진단 정보로 Wrapper에 전달하고 지표 dict에 0이나 임의의 대체값을 넣지 않는다. 출력 지표명은 valid/test와 raw AUROC·후처리 F1의 출처를 식별하도록 정하며, 기존 monitor 이름 `valid_image_auroc`는 유지한다.

AUROC와 F1은 전체 표본·픽셀의 누적 상태로 계산한다. 배치별 AUROC나 F1을 산출해 평균하지 않는다. 분산 평가에서는 metric 상태를 올바르게 동기화해 전체 집합 기준으로 계산하며, 프로세스별 AUROC를 `sync_dist=True`로 평균하는 것을 대체 구현으로 사용하지 않는다.

### Evaluator 스켈레톤과 Wrapper 호출

목표 위치는 `common/evaluator.py`다. 기존 순수 metric 또는 TorchMetrics를 재사용하고, device 이동이 연결되도록 metric 객체를 `nn.ModuleDict` 등 등록 가능한 모듈 속성으로 보관한다. 아래 API는 visionlab 초안이며 anomalib Evaluator 생성자의 전체 호환을 요구하지 않는다.

```python
from torch import nn


class Evaluator(nn.Module):
    def __init__(self, val_metrics=None, test_metrics=None):
        super().__init__()
        # Register separate metric instances for valid and test.
        # Metric configuration and field mapping are omitted here.
        ...

    def reset(self, stage):
        # Reset only the selected stage's accumulation and diagnostics.
        ...

    def update(self, stage, raw, processed, target):
        # Route raw predictions to AUROC and binary predictions to F1.
        # Record unavailable metrics without substituting zero values.
        ...

    def compute(self, stage):
        # Return scalar metric tensors computed from the full stage state.
        # Synchronize distributed metric states before final computation.
        ...
```

`evaluator=True`는 Wrapper의 기본 metric 구성으로 위 객체를 생성한다. `False`이면 reset·update·compute와 metric 로그를 모두 생략한다. visionlab Evaluator 객체를 전달하면 그 설정을 사용한다. Evaluator는 임계값을 선택하거나 PostProcessor 상태를 갱신하지 않는다.

이 문서는 수동 compute·reset 방식으로 통일한다. Wrapper는 epoch 시작에 reset, 배치마다 update, epoch 종료에 compute 후 Tensor dict를 로깅하고 상태를 비운다. 같은 metric 객체를 다시 `self.log()`에 전달하거나 Evaluator Callback을 함께 등록해 중복 집계·reset하지 않는다. 이미 전역 집계한 최종 scalar를 프로세스별 지표 평균으로 재해석하지 않는다.

```python
def on_validation_epoch_start(self):
    if self.evaluator is not None:
        self.evaluator.reset("valid")
    # Reset PostProcessor collection only for real fit validation.
    ...


def validation_step(self, batch, batch_idx):
    images, target = batch
    raw = self(images)
    if self.evaluator is not None:
        self.evaluator.update("valid", raw, None, target)
    # Collect PostProcessor calibration only for real fit validation.
    ...


def on_validation_epoch_end(self):
    # Finalize eligible calibration before checkpoint selection and saving.
    ...
    if self.evaluator is not None:
        metrics = self.evaluator.compute("valid")
        if metrics:
            self.log_dict(metrics, on_step=False, on_epoch=True)
        # Report unavailable-metric diagnostics before clearing stage state.
        self.evaluator.reset("valid")
```

test도 같은 순서로 `"test"` 상태를 초기화·갱신·집계한다. `test_step`은 PostProcessor 적용 후 `update("test", raw, processed, target)`을 호출한다. 정답 없는 predict에서는 Evaluator를 호출하지 않는다. 순수 PyTorch 평가에서도 같은 세 API를 직접 호출할 수 있고 최종 dict를 기록하는 방식은 호출자가 결정한다.

### Visualizer와 결과 전달

Wrapper는 평가·예측 결과에 `raw`, 선택적 `processed`, 정규화 전 표시 이미지, `sample_id`, `image_path`와 선택적 label·mask를 함께 전달한다. 원본 `InferenceBatch`는 순수 모델의 출력 형식으로 유지하고 메타데이터를 순수 모델의 forward 인자로 추가하지 않는다.

기본 score는 `[B,1]`, anomaly map은 `[B,1,H,W]`를 기준으로 한다. 표시 이미지·정답 마스크·예측 map은 [DATA.md](DATA.md)의 전체 입력 좌표계에 대응해야 한다. Tiler 사용 여부와 관계없이 원본 파일 해상도 자동 복원은 포함하지 않는다.

`visualizer=True`는 기본 ImageVisualizer 생성과 test·predict 저장 Callback 연결을 뜻한다. Callback은 완료된 결과만 읽고 보정·metric·예측을 변경하지 않는다. 기본 저장 위치는 Trainer 실행 폴더 아래 `images`이며 단계·범주·sample ID로 경로를 구분한다. 같은 Callback을 task Trainer가 중복 추가하지 않도록 조립에서 확인한다.

객체를 전달하면 해당 visionlab ImageVisualizer로 이미지를 생성하고 같은 native 저장 연결을 사용한다. 순수 ImageVisualizer 자체는 Callback을 상속하지 않는다. 정답이나 예측 mask가 없으면 해당 표시를 생략한다. heatmap 표시용 스케일은 평가 점수와 별도로 취급한다.

## 6. 모델별 학습과 보정

| 항목 | STFPM | EfficientAD |
|---|---|---|
| 기본 PreProcessor | 입력 확인·ImageNet 정규화 | 입력 확인, 외부 정규화 없음 |
| 학습 대상 | student만 학습, teacher eval·gradient 고정 | student·autoencoder 학습, teacher 고정 |
| 학습 반환과 loss | teacher/student 특징 → 별도 STFPMLoss | 순수 모델의 세 loss → 합산 |
| optimizer | SGD, lr 0.4, momentum 0.9, dampening 0, weight_decay 0.001 | Adam, 생성자의 lr·weight_decay |
| 추가 학습 데이터 | 없음 | 로컬 Imagenette train penalty 입력 |
| 모델 고유 보정 | 없음 | 정상 train teacher mean/std, 정상 valid map quantile |
| Tiler | 선택적 연결, 특징 추출 후 계층별 untile | 초기 설계에서는 연결하지 않음 |

EfficientAD의 초기 지원 조건은 256×256·학습 batch 1·단일 장치·gradient accumulation 1이다. Imagenette도 `[0,1]`로 전달하고 모델 내부 정규화를 중복하지 않는다. 원본의 학습 데이터 변환·통계·quantile 연산을 대조하며 계산은 순수 연산에 두고 Hook은 실행과 상태 갱신만 연결한다.

학습 재개에서는 복원된 teacher·mean/std를 불필요하게 초기화하지 않는다. fit validation에서는 정상 valid로 quantile을 보정한 뒤 해당 상태의 raw 예측을 공통 PostProcessor에 수집한다. 독립 평가에서는 quantile을 재계산하지 않는다. 이는 원본 2.0.0의 무조건적인 `on_validation_start` 갱신과 구별하는 visionlab 실행 계약이다.

### scheduler 기준과 원본 차이

STFPM 원본은 scheduler를 사용하지 않는다. EfficientAD 원본은 유효 학습 예산의 95%를 기준으로 StepLR step_size를 정하고 gamma 0.1을 사용한다. 설치된 2.0.0은 학습 step 수로 step_size를 계산하면서 반환 설정에 `interval`을 명시하지 않아 native Lightning 기본 epoch 호출과 차이가 생길 수 있다.

이 초안은 기존 프로젝트의 학습 step 기준 의도를 따라 `interval="step"`, `frequency=1`을 명시하는 방향으로 작성한다. 이 선택은 원본과 동일한 인자 계약과 별개인 실행 차이로 기록한다. 실제 구현 시 유효 optimizer step 수·종료 예산·변경 step을 계산하고 짧은 예산에서 step_size가 0이 되는 경우도 검증해야 한다. 원본과의 수치 동등성은 미검증이다.

### 로컬 자산과 Tiler 조립

경로는 실행 조립에서 명시 설정 또는 선택한 `paths.toml`을 한 번 해석해 로컬 자산 연결에 전달한다. teacher 연결 방식은 순수 모델·특징 추출기와 실행 조립 사이에서 구체화하며, 이 초안에서는 새로운 Wrapper 생성자 인자나 전역 가변 경로를 추가하지 않는다. 필요한 자산이 없으면 오류를 보고하고 자동 다운로드·무작위 대체를 하지 않는다.

Tiler는 순수 모델의 `tiler` 속성에 별도로 연결한다. Wrapper 생성자에 원본에 없는 타일 인자를 넣지 않는다. 전체 입력 해상도·타일 크기·stride·가장자리 처리·특징 복원은 [DATA.md](DATA.md)의 계약을 따른다. 학습 전에 조립한 Tiler 설정은 해당 모델의 checkpoint·독립 추론 설정에 함께 보존한다.

## 7. 저장·복원과 독립 추론

| 저장 대상 | 복원 목적 |
|---|---|
| 순수 모델 state_dict | 학습 파라미터·teacher·모델 고유 mean/std·quantile |
| PostProcessor state_dict | 보정 min/max·임계값·유효 상태 |
| optimizer·scheduler | 학습 재개 |
| 구조·구성요소 설정 | 같은 모델과 처리 구성을 재생성 |
| Tiler·공간 변환 설정 | 같은 타일링과 입력 좌표계 복원 |

PreProcessor·PostProcessor를 nn.Module 속성으로 연결하면 해당 buffer는 Wrapper state_dict에 포함된다. 임시 metric 누적값이나 validation 수집 배치를 추론용 영속 상태와 혼동하지 않는다. 최종 valid metric으로 checkpoint를 선택할 때 같은 epoch의 후처리 상태가 확정된 뒤 저장되는지 확인한다. native ModelCheckpoint의 monitor는 기본 Evaluator 사용 시 `valid_image_auroc`를 기준으로 한다.

구성요소 인스턴스를 그대로 하이퍼파라미터에 저장하는 방식에 의존하지 않는다. 기본 구성요소는 생성 설정으로 복원하고, 커스텀 객체는 재생성 정보와 상태 저장 계약을 제공해야 한다. 일반화한 registry나 임의 객체 pickle 복원은 추가하지 않는다. 해당 정보가 없으면 checkpoint 복원 시 호출자가 같은 visionlab 객체를 명시적으로 다시 전달해야 하며 자동 복원을 보장하지 않는다.

독립 추론은 순수 모델·PreProcessor·PostProcessor와 필요한 설정을 조립한다. Lightning Wrapper·Trainer에 의존하지 않으며, 완전한 학습 state를 복원할 때 원본 pretrained 파일이나 Imagenette를 다시 요구하지 않게 한다. 이를 위한 초기화·자산 로딩 분리는 구현 전에 구체화한다. 기존 checkpoint와의 자동 키 변환은 이 초안에 포함하지 않는다.

## 8. 사용 형태와 검증 기준

아래는 구현 완료 후의 native Lightning 사용 형태다. `data`는 DATA.md의 DataModule이며 local 자산 연결은 사전에 준비한다.

```python
from lightning.pytorch import Trainer

from visionlab.anomaly_detection.models.stfpm.lightning_model import STFPMLitModel


model = STFPMLitModel(visualizer=False)
trainer = Trainer(max_epochs=10, devices=1)
trainer.fit(model, datamodule=data)
trainer.test(model, datamodule=data)
```

이 test 호출은 명시한 모델의 현재 상태를 평가한다. best checkpoint를 평가할 때는 실제 checkpoint 경로를 명시하고 그 안의 모델·후처리 상태를 함께 복원한다. EfficientAD는 `EfficientAdLitModel(imagenet_dir="E:/datasets/imagenette2/train", visualizer=False)`와 함께 DataModule의 `train_batch_size=1` 및 Trainer의 `num_sanity_val_steps=0`을 설정한다.

향후 구현에서 다음을 확인한다.

- STFPM 6개·EfficientAD 11개 생성자 인자 이름·순서·기본값을 anomalib 2.0.0과 대조한다.
- anomalib 없이 Wrapper가 동작하고, 순수 모델·처리 구성요소는 Lightning 없이 import·실행되는지 확인한다.
- 각 처리 인자의 True·False·visionlab 객체와 잘못된 타입 입력을 확인한다. 시각화 기본 활성과 Callback 중복 방지도 확인한다.
- Evaluator가 Trainer·Lightning Hook·로깅에 의존하지 않고 Wrapper가 reset·update·compute·로그를 연결하는지 확인한다.
- valid/test 상태 분리, 두 epoch 연속 실행의 상태 초기화, metric 객체와 scalar의 중복 로깅·집계 방지를 확인한다.
- 배치 분할을 바꾸어도 전체 집합 지표가 일치하는지 확인하고, 단일 클래스·정답 또는 mask 누락·후처리 비활성에서 지표 생략 사유를 확인한다. 분산 환경의 전체 metric 상태 집계도 별도로 검증한다.
- train·validation·test·predict의 정규화 1회 적용, raw 보존과 표시 이미지·마스크 대응을 확인한다.
- sanity validation·독립 평가에서 보정 상태가 변경되지 않고 실제 fit validation에서만 확정되는지 확인한다.
- 상수 점수·비유한 통계·정답 부족·미보정·단일 클래스·정답 없는 predict를 구별해 처리하는지 확인한다.
- STFPM의 teacher 고정·student gradient·Tiler 복원, EfficientAD의 세 loss·teacher 통계·quantile·scheduler 변경 시점을 확인한다.
- 모델과 같은 epoch의 후처리 상태, 기본·커스텀 구성요소, 학습 재개·독립 추론의 저장·복원을 구분해 확인한다.

이번 작업은 문서 초안 작성이다. 생성자와 모델별 연결은 설치 소스 및 기존 명세를 읽어 정리했다. 구현·import·학습·평가·성능 동등성·checkpoint 복원은 실행하지 않았다.

## 9. 참조와 구현 전 구체화할 사항

참조 기준은 anomalib 2.0.0 설치 소스의 다음 파일이다. 원본을 재사용할 때 저작권·라이선스 표기를 유지하고 실제 구현에서 참조한 버전 또는 커밋을 기록한다.

- `anomalib/models/image/stfpm/lightning_model.py`
- `anomalib/models/image/efficient_ad/lightning_model.py`
- `anomalib/models/components/base/anomalib_module.py`
- `anomalib/metrics/evaluator.py`
- [Lightning과 TorchMetrics 연결](https://lightning.ai/docs/torchmetrics/latest/user-guide/lightning): native metric 로그 연결과 수동 compute·reset 방식의 비교 참고.
- 기존 v0.3 [SPEC.md](SPEC.md)와 데이터 처리 설계 [DATA.md](DATA.md)

초안 이후에는 생성자 계약을 유지하는 로컬 자산 전달 방식, 커스텀 구성요소 재생성 설정, PostProcessor 임계값 선택의 세부 규칙, 분산 실행의 전역 통계·metric 집계와 구체적인 독립 추론 산출물 포맷을 확정해야 한다. 이 항목들을 구현 완료로 간주하거나 빈 코드·추상화 계층으로 미리 생성하지 않는다.
