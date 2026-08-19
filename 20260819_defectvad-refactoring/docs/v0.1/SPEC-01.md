# SPEC — Anomaly Detection Integration on `cv_boilerplate`

문서 상태: Initial Technical Specification  
상위 문서: `BRIEF.md`, `PRD.md`  
작성일: 2026-08-19  
현재 구현 분석 기준: `nampluskr/cv_boilerplate@71261cef`

## 1. Purpose and Scope

### 1.1 목적

이 문서는 `BRIEF.md`의 사용자 의도와 `PRD.md`의 검증 가능한 요구사항을 현재 `cv_boilerplate`
architecture에서 구현하기 위한 기술 설계를 정의한다.

핵심 목표는 다음과 같다.

- 기존 `train`, `evaluate`, `predict`, `benchmark` entry point를 유지한다.
- anomalib의 pure-PyTorch algorithm code를 가능한 한 그대로 유지한다.
- anomalib Lightning wrapper와 Engine이 담당하던 model-specific lifecycle만 `cv_boilerplate`의 기존
  adapter/hook 경계로 옮긴다.
- gradient training, auxiliary data, statistics fitting, memory bank 및 no-gradient fitting을 공통 engine의
  model-name 분기 없이 수용한다.
- reference protocol과 결과 차이를 재현 가능하게 기록한다.

Implements: `FR-001`~`FR-025`, `NFR-001`~`NFR-014`, `CON-001`~`CON-012`

### 1.2 설계 기준과 증거 수준

- `[확인]`은 실제 source에서 확인한 현재 동작이다.
- `[설계]`은 이 SPEC이 요구하는 target 동작이다.
- `[미확정]`은 구현 전에 사용자 또는 reference baseline으로 결정해야 하는 사항이다.

현재 작업 directory에는 `cv_boilerplate` source가 없으므로, 현재 architecture에 대한 사실은 PRD와 동일하게
공개 revision `71261cef`의 분석 결과를 기준으로 한다. 분석에 사용한 anomalib `c9eeefff`는 reference 구조를
파악하기 위한 기준일 뿐 target revision으로 확정하지 않는다.

### 1.3 포함 범위

- 현재 execution/config/construction/checkpoint/metric/output 흐름의 최소 확장
- Anomaly Detection task contract
- MVTec AD dataset contract
- anomalib pure model과 project-specific integration code의 경계
- model lifecycle variation
- train/evaluate/predict/benchmark call flow
- metric, post-processing, checkpoint 및 offline asset contract
- reference equivalence 기록과 검증
- legacy migration 판단과 dependency 영향

### 1.4 다루지 않는 범위

- 구현 순서, Phase, backlog 및 일정
- 초기 모델과 category의 최종 목록
- 임의의 metric tolerance 수치
- anomalib 전체 runtime 또는 API 호환 계층
- legacy framework의 재구성
- 모든 anomalib 모델과 dataset의 즉시 지원

Guards: `OOS-001`~`OOS-011`

## 2. Current Architecture Summary

### 2.1 Execution entry point

`[확인]` `python -m src`의 `src/__main__.py`가 network guard를 먼저 활성화하고 task package를 import해
registry를 채운 뒤 CLI command를 dispatch한다. 사용자-facing lifecycle은 `src/cli/commands.py`의
`train`, `evaluate`, `predict`, `run_benchmark`가 소유한다.

Implements: `FR-001`, `CON-003`

### 2.2 Config loading과 object construction

`[확인]` 현재 흐름은 다음과 같다.

```text
YAML path
  -> load_and_merge_base
  -> dotted --set override
  -> validate_config
  -> build_transforms
  -> MODELS / LOSSES / METRICS / ADAPTERS registry build
  -> DATASETS registry build
  -> build_dataloader
  -> build_optimizer / build_scheduler
```

`[확인]` 동일한 component construction 함수가 CLI와 benchmark runner에 중복되어 있다. 이 SPEC은 새 config
system을 만들지 않으며, 이 중복을 확장 과정에서 단일 construction path로 정리하는 것을 허용한다. 정리 자체는
anomaly 전용 abstraction이 아니라 현재 동작을 보존하는 공통화여야 한다.

Implements: `FR-002`, `FR-024`, `NFR-010`, `CON-003`

### 2.3 Task, model, dataset 관계

`[확인]` 별도 Task object는 없다. Task package가 import 시 Dataset, Transform, Model, Loss, Metric, Adapter를
각 registry에 등록한다. `TaskAdapter`가 batch forwarding, loss, metric, prediction, collate 및 lifecycle hook을
담당한다.

`[설계]` Anomaly integration도 이 구조를 유지한다. 새 Task class나 별도 anomaly Engine을 추가하지 않는다.

Implements: `FR-002`, `NFR-004`, `CON-005`

### 2.4 Training lifecycle

`[확인]` `Trainer.fit`은 다음 순서를 사용한다.

```text
model.to(device)
adapter.on_fit_start
for epoch:
    adapter.on_epoch_start
    Trainer._train_epoch
        model.train
        every batch: zero_grad -> adapter.train_step -> backward -> optimizer.step
    scheduler.step
    Trainer.evaluate(valid)
    adapter.on_epoch_end
    best/last checkpoint save
best model reload
adapter.on_fit_end
finalized model_state를 best checkpoint에 재저장
```

`[확인]` optimizer와 differentiable loss가 항상 존재한다고 가정하므로 PatchCore/PaDiM 계열을 정상적으로
표현하지 못한다. validation 직전 hook도 없어 EfficientAD의 validation map quantile lifecycle과 일치하지 않는다.

Implements: `FR-005`, `FR-006`, `GAP-002`, `GAP-003`, `GAP-006`

### 2.5 Evaluation lifecycle

`[확인]` `evaluate`는 config로 model과 adapter를 새로 만들고 checkpoint의 model state만 복원한 뒤
`Trainer.evaluate`로 metric을 계산한다. Adapter state는 checkpoint 대상이 아니다.

`[확인]` `Trainer.evaluate`는 `model.eval`, `adapter.reset_metrics`, `torch.no_grad`, batch별 `eval_step`과
metric update, 최종 compute를 수행한다.

Implements: `FR-010`, `FR-012`, `GAP-007`

### 2.6 Prediction lifecycle

`[확인]` `predict`는 단일 파일 또는 directory의 PIL image를 eval transform에 통과시키고 adapter collate 후
`predict_step`을 호출한다. 결과는 `predictions/predict.json`과 task-specific artifact로 저장한다.

`[확인]` 현재 anomaly threshold는 새 adapter에 복원되지 않아 calibrated label이 `None`이 될 수 있다.

Implements: `FR-011`, `FR-012`, `FR-013`, `GAP-007`

### 2.7 Benchmark lifecycle

`[확인]` benchmark runner는 base config와 split override를 merge하고 control field를 검사한 뒤 split마다
train/valid/test/profile을 실행한다. 한 split의 exception은 failed row로 격리되고 나머지 split은 계속된다.
결과는 control report, resolved config, metrics, environment 및 leaderboard에 기록된다.

`[확인]` 현재 anomaly benchmark는 동일 조건 모델 비교용 smoke benchmark이며, 모델별 anomalib reference와의
equivalence pair를 표현하지 않는다.

Implements: `FR-018`, `FR-019`, `FR-025`, `GAP-010`

### 2.8 Checkpoint와 state ownership

`[확인]` checkpoint는 model, optimizer, scheduler, scaler, epoch, best metric, monitor, config, environment 및
RNG state를 보존한다. Adapter/post-processor state는 보존하지 않는다.

`[설계]` 기존 checkpoint container를 유지하고 adapter state와 global step, protocol identity를 확장 필드로
추가한다. 별도 anomaly checkpoint format을 만들지 않는다.

Implements: `FR-021`, `FR-022`, `NFR-002`, `GAP-007`, `GAP-011`

### 2.9 Metrics와 output

`[확인]` 현재 anomaly adapter는 image/pixel `BinaryAUROC`를 update하고 gaussian smoothing 및 valid-only F1
threshold를 계산한다. Threshold는 model state가 아니라 adapter field다.

`[확인]` output 관리는 resolved YAML, JSON, CSV, log, checkpoint, visualization 및 leaderboard로 이미
구성되어 있다. 이 구조를 확장하고 별도 experiment tracking system을 도입하지 않는다.

Implements: `FR-016`, `FR-017`, `FR-022`, `NFR-008`, `OOS-009`

## 3. Target Architecture

### 3.1 Responsibility boundary

`[설계]` 책임 경계는 다음과 같다.

```text
cv_boilerplate core
  CLI / config / construction / device / common Trainer
  checkpoint container / run outputs / benchmark orchestration
  generic optimization execution / generic hook invocation
                    |
                    v
Anomaly task integration
  sample and output contract / collate / metric routing
  common anomaly post-processing / visualization
  adapter state serialization
                    |
                    v
Per-model integration
  upstream model invocation / loss invocation / trainable parameters
  optimizer and scheduler specification / auxiliary loader consumption
  model-specific prepare, validation-prepare, finalize
  upstream output conversion
                    |
                    v
Vendored or pinned anomalib pure-PyTorch algorithm
  architecture / loss / anomaly map / memory bank / statistics algorithm

Dataset integration
  directory parsing / sample metadata / split realization / mask loading
  model-independent geometric transform of image and mask
```

### 3.2 Dependency direction

`[설계]` dependency는 core에서 구체 모델로 향하지 않는다.

- core는 `TaskAdapter` contract와 generic optimization/state contract만 안다.
- anomaly common code는 upstream concrete model을 import하지 않는다.
- per-model integration은 anomaly common contract와 선택된 upstream model을 안다.
- upstream model code는 `cv_boilerplate` core, CLI, Dataset 또는 benchmark를 import하지 않는다.
- Dataset은 model 이름, optimizer, metric implementation을 알지 않는다.

Implements: `FR-015`, `FR-024`, `NFR-004`, `NFR-005`, `NFR-009`, `NFR-010`, `CON-005`

### 3.3 최소 core extension

`[설계]` 기존 `TaskAdapter`를 유지하면서 다음 capability만 추가한다.

1. optimizer가 없을 수 있는 train step
2. adapter가 trainable parameter와 optimizer/scheduler cadence를 정의하는 optimization specification
3. validation 직전과 직후의 optional hook
4. named auxiliary loader를 기존 loader mapping에 포함하는 construction
5. adapter state의 checkpoint save/load
6. epoch 및 step scheduler cadence의 generic 실행

별도 anomaly Trainer, callback framework, event bus 또는 general-purpose workflow engine은 추가하지 않는다.

Implements: `FR-005`, `FR-006`, `FR-008`, `FR-021`, `NFR-010`, `CON-001`, `OOS-004`, `OOS-006`

## 4. Anomaly Detection Task Contract

### 4.1 기존 extension 사용

`[설계]` Anomaly Detection은 기존 Dataset, Transform, Model, Metric, Adapter registry와 `TaskAdapter`를 사용한다.
별도 Task class는 만들지 않는다.

Implements: `FR-001`, `FR-002`, `FR-024`, `NFR-004`

### 4.2 Primary batch contract

`[설계]` primary batch는 현재 convention을 유지한다.

```text
images: Tensor[B, 3, H, W], float
targets: list[dict]
```

Train target는 normal-only one-class model에서 빈 dict일 수 있다. Evaluation target는 다음 공통 field를 사용한다.

```text
label: scalar integer tensor, 0=normal, 1=anomalous
mask: Tensor[H, W], integer binary mask
sample_id: stable dataset-independent identifier
path: source image path or equivalent source identifier
metadata: optional dataset-specific information
```

`sample_id`, `path`, `metadata`의 실제 전달 위치는 현재 tuple convention과 호환되도록 구현 시 확정하되,
model/loss/metric이 dataset-specific metadata에 의존해서는 안 된다.

Implements: `FR-013`, `FR-014`, `FR-015`, `NFR-009`

### 4.3 Model output contract

`[설계]` adapter가 core에 노출하는 normalized output은 다음 의미를 가진다.

```text
pred_score: Tensor[B]
anomaly_map: Tensor[B, H, W] | None
extras: optional mapping not consumed by common metric code
```

- `pred_score`는 클수록 anomalous해야 한다.
- localization 모델의 `anomaly_map`은 evaluation mask와 공간적으로 대응해야 한다.
- upstream의 `InferenceBatch`, dict, `(B,1,H,W)` 등 차이는 per-model integration이 변환한다.
- conversion은 값의 의미를 바꾸지 않으며 squeeze, field mapping 및 명시된 interpolation만 허용한다.

Implements: `FR-011`, `FR-013`, `FR-016`, `FR-017`

### 4.4 Metric input boundary

`[설계]` anomaly common adapter는 normalized output과 common target만 metric에 전달한다. Metric은 model 또는
dataset directory를 참조하지 않는다.

- image metric: `pred_score`, `label`
- pixel metric: `anomaly_map`, `mask`
- threshold metric: calibrated score/map와 binary target
- region metric: anomaly map과 connected-component semantics가 보존된 mask

Implements: `FR-015`, `FR-016`, `NFR-009`

### 4.5 Post-processing boundary

`[설계]` 처리 순서를 다음처럼 분리한다.

```text
upstream raw output
  -> per-model algorithm-defined map processing
  -> common representation conversion
  -> protocol-defined normalization/smoothing
  -> threshold application
  -> metric or user-facing prediction
```

Algorithm 의미에 포함된 처리는 upstream/per-model integration에 남기고, validation-derived threshold와 공통
prediction 변환은 stateful anomaly post-processing에 둔다.

Implements: `FR-003`, `FR-004`, `FR-017`, `NFR-003`, `CON-004`

## 5. Dataset Integration

### 5.1 Dataset 책임

`[설계]` Dataset은 directory parsing, sample identity, image/mask loading, label 생성 및 split membership만
소유한다. Model-specific normalization, optimizer, statistics fitting 및 threshold는 소유하지 않는다.

Implements: `FR-014`, `FR-015`, `NFR-009`, `NFR-010`

### 5.2 MVTec AD

`[설계]` 기존 `MVTecAnomaly`의 다음 동작을 유지한다.

- category root의 `train/good`, `test/<defect_type>`, `ground_truth/<defect_type>` parsing
- train은 normal sample만 반환
- `good` evaluation image는 label 0과 all-zero mask
- abnormal image는 label 1과 대응 ground-truth mask
- mask를 `{0,1}` integer로 변환
- image와 mask의 geometric transform alignment 유지
- stable split file 사용 및 train/valid/test disjoint 검증 가능

`[미확정]` Reference-equivalence run에서 disjoint valid/test를 사용할지 anomalib reference와 같은 split을 사용할지는
결정되지 않았다. Dataset 구현은 두 정책을 모두 explicit split manifest로 표현할 수 있어야 한다.

Implements: `FR-009`, `FR-014`, `CON-009`, `CON-010`

### 5.3 Split manifest

`[설계]` 모든 benchmark split은 materialized sample identifier 또는 동일하게 재현 가능한 split specification으로
기록한다. Manifest에는 dataset identity, category, seed, source population 및 train/valid/test membership을
포함한다. Validation과 test가 같으면 이를 명시적인 protocol flag로 기록한다.

Implements: `FR-009`, `FR-020`, `FR-022`, `NFR-002`, `CON-009`, `CON-010`

### 5.4 Transform ownership

`[설계]` Dataset-independent geometric transform은 existing transform registry를 사용한다. Model-specific config가
reference transform을 선택하며, 모든 anomaly model에 하나의 normalization을 강제하지 않는다.

- image와 mask에 같은 resize/crop geometry 적용
- mask interpolation은 nearest
- image normalization은 model config가 선택
- EfficientAD처럼 raw `[0,1]` input을 요구하는 모델은 Dataset이 아니라 model config가 normalization을 끈다.
- predict와 evaluation은 같은 resolved eval transform을 사용한다.

Implements: `FR-007`, `FR-014`, `FR-015`, `GAP-004`

### 5.5 Auxiliary dataset

`[설계]` primary `data` 구조를 유지하면서 model config가 named auxiliary data specification을 선언할 수 있게
확장한다. Construction은 기존 Dataset/Transform/DataLoader registry를 재사용해 loader mapping에 이름으로
추가한다. Adapter는 선언된 이름만 소비한다.

예시 의미:

```yaml
data:
  auxiliary:
    imagenette:
      name: local_image_folder
      root: /local/path
      batch_size: 1
      transform: {name: efficientad_penalty, params: {}}
```

이 예시는 schema 방향이며 최종 key 이름은 구현 전 config compatibility 검토로 확정한다.

Implements: `FR-008`, `FR-023`, `NFR-006`, `CON-006`

### 5.6 Future dataset

`[설계]` VisA/BTAD는 초기 구현 대상으로 확정하지 않는다. 향후 각 Dataset이 common sample contract로 parsing하고
동일 adapter/metric/model integration을 재사용할 수 있어야 한다.

Implements: `FR-015`, `NFR-009`, `OOS-008`

## 6. Model Integration

### 6.1 Upstream code reuse policy

`[설계]` 통합 대상마다 target anomalib revision과 pure-PyTorch dependency closure를 먼저 확정한다.

- algorithm file은 upstream naming과 module separation을 가능한 한 유지한다.
- formatting, output type 및 import convenience를 이유로 algorithm을 rewrite하지 않는다.
- project-specific code는 upstream file 밖에서 loss invocation, output conversion, lifecycle 및 asset injection을
  담당한다.
- 불가피한 upstream 수정은 source manifest와 diff record에 이유, 영향, 검증을 기록한다.

Implements: `FR-003`, `FR-004`, `NFR-003`, `CON-004`, `CON-008`, `CON-011`

### 6.2 Source transport boundary

`[미확정]` Vendoring과 별도 sync 방식은 확정하지 않는다. 어느 방식을 선택해도 다음 artifact가 필요하다.

- upstream repository URL
- version/commit
- copied source path 목록
- license/notice
- local patch 또는 diff
- source checksum
- dependency list

제품 runtime은 anomalib Lightning/Engine을 import하지 않는다.

Implements: `FR-003`, `FR-022`, `NFR-003`, `CON-002`, `CON-008`, `CON-011`

### 6.3 Per-model adapter

`[설계]` 기존 `TaskAdapter`가 model-specific integration point다. Anomaly common adapter는 output/metric/prediction
공통 동작을 제공하고, 실제 차이가 있는 모델은 이를 확장한 per-model adapter 또는 동등한 구성 객체로 다음을
정의한다.

- upstream training forward와 loss 호출
- trainable parameter selection
- optimizer/scheduler specification
- auxiliary loader 사용
- fit/validation/finalize hook
- upstream output conversion
- adapter/post-processing state

이 계층은 Trainer, Dataset parsing, logging, checkpoint file I/O 또는 benchmark orchestration을 소유하지 않는다.
따라서 legacy trainer나 LightningModule을 이름만 바꿔 복제하는 구조가 아니다.

Implements: `FR-004`, `FR-005`, `FR-006`, `FR-008`, `FR-024`, `NFR-010`, `OOS-004`

### 6.4 Model construction과 pretrained weight

`[설계]` Model registry는 upstream pure model 또는 이를 포함하는 최소 `nn.Module` container를 생성한다.
Pretrained architecture는 network-enabled constructor를 사용하지 않고 architecture와 local state loading을
분리한다.

- required weight path는 resolved config에 존재해야 한다.
- expected source, checksum, state-dict key contract를 검증한다.
- teacher/student처럼 일부 submodule만 load할 때 target submodule을 명시한다.
- required weight는 strict load를 기본으로 한다.
- missing/mismatch는 `LocalAssetError` 계열의 user-facing error다.

Implements: `FR-023`, `NFR-006`, `NFR-011`, `CON-006`, `CON-007`

### 6.5 Train/eval mode

`[설계]` Upstream model이 train/eval mode에 따라 output을 바꾸는 동작은 보존한다. Frozen teacher는 outer
`model.train()` 이후에도 eval 상태와 `requires_grad=False`를 유지해야 한다. 이 불변 조건은 pure model 또는
minimal container의 state behavior로 보장하고 test한다.

Implements: `FR-003`, `FR-005`, `NFR-003`, `CON-004`

### 6.6 Loss handling

`[설계]` Loss가 upstream 별도 module이면 그대로 생성해 per-model adapter가 호출한다. Loss가 model forward에
내장되어 있으면 adapter는 반환된 component를 합성하되 reference 식을 변경하지 않는다. Common anomaly
adapter는 서로 다른 모델의 valid loss를 공통 의미로 간주하지 않는다.

Implements: `FR-003`, `FR-006`, `NFR-003`

### 6.7 Optimization specification

`[설계]` `TaskAdapter`는 model과 resolved optimizer config를 바탕으로 다음 generic 정보를 core에 제공한다.

```text
optimizer: torch optimizer or None
scheduler: torch scheduler or None
scheduler_interval: "step" or "epoch"
trainable parameter groups
gradient clipping policy
```

구체 class 이름은 구현 시 기존 builder와의 compatibility를 고려해 정한다. Core는 interval과 optimizer 존재
여부만 처리하며 model 이름을 검사하지 않는다.

Implements: `FR-006`, `NFR-004`, `CON-005`, `GAP-003`

### 6.8 Model-specific state

`[설계]` 다음 상태는 가능한 경우 `nn.Module` parameter/buffer로 보존한다.

- teacher mean/std
- map quantile
- feature statistics
- memory bank/coreset
- model-specific normalization constant

Task-level threshold, score range 및 output calibration처럼 algorithm model 밖의 상태는 adapter state에 둔다.

Implements: `FR-012`, `FR-017`, `FR-021`

## 7. Model Lifecycle Variations

### 7.1 공통 lifecycle capability

`[설계]` Engine은 다음 generic 시점만 호출한다.

```text
fit preparation
train epoch start
train step
validation preparation
evaluation step
validation completion
fit finalization
```

현재 hook을 재사용하고 validation preparation/completion만 최소 추가한다. Hook invocation은 모든 task에 동일하며
model-name 조건을 갖지 않는다.

Implements: `FR-005`, `NFR-004`, `NFR-005`, `CON-005`

### 7.2 Lifecycle 비교

| 유형 / 예시 | Preparation | Training | Validation | Finalize | Inference | Checkpoint state | Required extension |
|---|---|---|---|---|---|---|---|
| Standard gradient | asset 확인 | loss, backward, optimizer step | metric | 선택적 calibration | forward | model/optimizer/scheduler | 기존 loop |
| STFPM teacher/student | teacher local weight, freeze/eval | student-only SGD, upstream loss | upstream anomaly map | threshold/post-process calibration | teacher/student discrepancy | teacher/student, calibration | parameter selection, adapter state |
| EfficientAD teacher/student/AE | teacher local weight, Imagenette loader, train-set mean/std | student+AE loss와 auxiliary penalty | validation 전에 normal map quantile 계산 | threshold/post-process calibration | normalized ST/AE map 결합 | model mean/std/quantiles, calibration | named auxiliary loader, validation hook, cadence |
| Feature statistics / PaDiM | backbone local weight | no-grad feature collection | validation 전에 statistics fit 완료 | 필요 시 threshold | Mahalanobis map | fitted statistics, selected feature indices | optimizer None, validation preparation |
| Memory bank / PatchCore | backbone local weight | no-grad embedding collection | validation 전에 coreset/memory finalize | 필요 시 threshold | nearest-neighbor score/map | memory bank, coreset state | optimizer None, validation preparation |
| No-gradient/post-fit | assets 확인 | state collection 또는 없음 | finalized state로 평가 | state completion | model-specific | finalized state | optional loss, optional optimizer |

`[미확정]` STFPM/EfficientAD/PatchCore/PaDiM 중 어떤 조합을 최초 acceptance model로 사용할지는 정하지 않는다.

Implements: `FR-005`, `FR-006`, `FR-008`, `AC-004`, `OOS-006`, `OOS-007`

### 7.3 No-optimizer train step

`[설계]` `adapter.train_step` 결과의 loss는 optimizer가 없는 lifecycle에서 `None`일 수 있다. Engine behavior는
다음과 같다.

- optimizer가 있으면 differentiable scalar loss를 요구하고 기존 AMP/backward/clip/step을 수행한다.
- optimizer가 없으면 `train_step`의 state collection side effect만 허용하고 backward/step을 수행하지 않는다.
- loss가 필요한 mode에서 누락되거나 optimizer 없는 mode에서 gradient update를 요구하면 validation error다.

Implements: `FR-005`, `FR-006`, `GAP-002`, `GAP-006`

### 7.4 Validation preparation

`[설계]` `Trainer.evaluate(..., split="valid")` 직전에 adapter validation-preparation hook을 호출한다.

- EfficientAD는 current epoch model로 validation normal map quantile을 계산한다.
- PatchCore/PaDiM은 수집된 train state를 inference-ready state로 finalize한다.
- Hook은 전달받은 loader mapping에서 명시적으로 허용된 train/valid/auxiliary data만 사용한다.
- final test evaluate에서는 calibration/fitting hook을 자동 재실행하지 않고 checkpoint state를 사용한다.

Implements: `FR-005`, `FR-009`, `FR-012`, `CON-009`

### 7.5 Lifecycle state transition

`[설계]` Model/adapter state는 최소한 `unprepared`, `collecting/training`, `inference_ready` 상태를 구분할 수 있어야
한다. 구현이 enum을 필요로 하는지는 모델 통합에서 결정하되, inference-ready가 아닌 checkpoint로 evaluate나
predict하면 명확히 실패해야 한다.

Implements: `FR-010`, `FR-011`, `FR-021`, `NFR-011`

## 8. Training Flow

### 8.1 Construction과 fit call flow

`[설계]` Target call flow는 다음과 같다.

```text
CLI train
  -> resolve_config / validate_config
  -> apply_network_policy
  -> create run_dir and save resolved config
  -> RunContext seed/device setup
  -> build primary and named auxiliary transforms
  -> build model, loss, metrics, adapter
  -> build primary and named auxiliary datasets/loaders
  -> adapter creates generic optimization specification
  -> Trainer.fit
       -> adapter.on_fit_start(model, loader_mapping, device)
       -> epoch loop
            -> adapter.on_epoch_start
            -> generic train epoch
                 -> adapter.train_step
                 -> optional optimization based on specification
                 -> optional step scheduler
            -> optional epoch scheduler
            -> adapter.on_validation_start
            -> Trainer.evaluate(valid)
            -> adapter.on_validation_end
            -> adapter.on_epoch_end
            -> selection checkpoint
       -> selected model reload when selection applies
       -> adapter.on_fit_end
       -> final model + adapter state checkpoint
  -> final metrics, protocol and environment output
```

Implements: `FR-001`, `FR-005`, `FR-006`, `FR-008`, `FR-009`, `FR-021`, `CON-001`, `CON-003`

### 8.2 Model selection

`[설계]` Model selection은 config의 monitor metric과 validation result를 사용한다. No-gradient 모델처럼 하나의
finalized state만 있는 경우 selection checkpoint와 final checkpoint가 같을 수 있다. Test result는 selection에
사용하지 않는다.

Implements: `FR-009`, `CON-009`

### 8.3 Resume

`[설계]` Resume은 model, adapter, optimizer, scheduler, scaler, epoch, global step 및 RNG state를 복원한다.
Auxiliary loader iterator 자체는 저장하지 않고, seed와 global step 또는 model-specific deterministic position으로
재구성한다. Reference equivalence가 정확한 iterator position을 요구하면 해당 position을 adapter state로 보존한다.

Implements: `FR-021`, `FR-022`, `NFR-002`

## 9. Evaluation Flow

### 9.1 Call flow

```text
CLI evaluate
  -> resolve/validate config and offline policy
  -> build eval transform, model, metrics, adapter, dataset, loader
  -> load checkpoint model_state + adapter_state
  -> validate inference_ready and protocol compatibility
  -> model.to(device), adapter.to(device)
  -> Trainer.evaluate under eval/no_grad
       -> adapter.eval_step
       -> raw output conversion
       -> checkpoint-derived post-processing
       -> metric update
  -> aggregate metrics
  -> save metrics and optional visualization
```

`[설계]` Evaluation은 statistics, memory bank 또는 threshold를 test data에서 새로 fit하지 않는다. Reference가
validation과 test를 공유하는 별도 run은 protocol metadata로 명시한다.

Implements: `FR-010`, `FR-012`, `FR-016`, `FR-017`, `FR-021`, `CON-009`

### 9.2 Output

`[설계]` 기존 `metrics_final.json`, visualization 및 log convention을 유지한다. Metric output은 level과 처리
상태를 구분할 수 있어야 한다.

```text
raw/reference-independent: image AUROC, pixel AUROC, optional AUPRO
calibrated: image F1, pixel F1, threshold-dependent fields
protocol: split id, post-processing id, metric implementation id
```

최종 JSON key의 상세 schema는 구현 전에 기존 leaderboard compatibility를 확인해 확정한다.

Implements: `FR-016`, `FR-020`, `FR-022`, `NFR-008`

## 10. Prediction Flow

### 10.1 Input

`[설계]` 현재 CLI convention인 단일 image path 또는 directory를 유지한다. Eval transform은 checkpoint와 resolved
model config에 호환되어야 한다.

### 10.2 Output

`[설계]` 각 sample prediction은 다음 의미를 제공한다.

```text
source path
sample identifier
anomaly score
anomaly map artifact or reference, when supported
predicted image label, when calibrated
predicted mask artifact or reference, when supported and calibrated
image/pixel threshold, when applicable
protocol/checkpoint identity
```

JSON에 대형 anomaly map을 직접 넣는 대신 기존 artifact output convention을 사용한다. Visualization은 동일한
post-processed map과 threshold를 입력으로 사용해야 한다.

Implements: `FR-011`, `FR-012`, `FR-013`, `FR-017`, `FR-022`

### 10.3 Uncalibrated behavior

`[설계]` Reference protocol이 threshold를 사용하지 않거나 checkpoint가 명시적으로 uncalibrated이면 score/map은
반환할 수 있지만 label/mask는 임의 threshold로 생성하지 않는다. 결과에 uncalibrated 상태를 명시한다.

Implements: `FR-011`, `NFR-011`
