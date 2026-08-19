## 11. Benchmark and Reference Equivalence

### 11.1 Benchmark 유형

`[설계]` 기존 benchmark runner를 유지하되 목적을 결과 metadata에서 구분한다.

- smoke/comparative run: pipeline과 여러 모델의 제한된 조건 비교
- reference-equivalence run: 하나의 integration run을 대응 anomalib reference run과 비교

Reference-equivalence에서는 모델 간 동일 optimizer/transform을 강제하지 않는다. 각 모델은 자신의 reference
protocol과 동등해야 하며, cross-model control의 차이는 승인된 exception으로 기록한다.

Implements: `FR-018`, `FR-019`, `FR-020`, `GAP-010`

### 11.2 Reference manifest

`[설계]` Reference run과 integration run은 다음 필드를 포함한 immutable manifest로 연결한다.

| 영역 | 필수 기록 |
|---|---|
| Source | anomalib repository, version/commit, model source paths, local integration revision |
| Model | model name/family, model size, backbone/layers, algorithm parameters |
| Dataset | name, release/version/checksum, category, root identity, split manifest |
| Assets | weight filename, source, checksum, load target, auxiliary dataset identity |
| Runtime | seed, device, AMP, determinism, Python/PyTorch/torchvision/metric library versions |
| Input | image size, resize/crop, normalization, augmentation, batch size, drop-last |
| Optimization | trainable parameters, optimizer, learning rate, weight decay, scheduler, cadence |
| Budget | epochs, max steps, early stopping, validation cadence |
| Output processing | map interpolation, smoothing, normalization, quantiles, thresholds |
| Metrics | name, implementation/version, fields, aggregation, FPR limit 등 parameters |
| Hardware | GPU, CUDA, driver, relevant deterministic warnings |

Implements: `FR-019`, `FR-020`, `FR-022`, `NFR-001`, `NFR-002`, `CON-008`

### 11.3 Protocol diff

`[설계]` Runner는 reference manifest와 resolved integration config를 비교해 field별 상태를 기록한다.

```text
equal
equivalent with documented translation
different with approved reason
missing / invalid
```

필수 field가 missing이거나 승인되지 않은 차이가 있으면 equivalence 결과를 pass로 판정하지 않는다.

Implements: `FR-020`, `NFR-008`, `NFR-011`

### 11.4 Tolerance 결정

`[미확정]` 수치를 임의로 정하지 않는다. Target revision과 protocol을 고정한 뒤 동일 reference run을 승인된
횟수만큼 반복해 hardware/library 환경에서의 분산을 측정한다. Integration tolerance는 reference 반복 분산,
metric 해상도 및 수치 오차를 근거로 사용자 승인 후 manifest에 기록한다.

Implements: `NFR-001`, `NFR-012`, `AC-008`, `GAP-013`

### 11.5 Failure isolation

`[설계]` 현재 benchmark의 per-split exception isolation을 유지한다. Failed row는 exception type, message,
protocol identity, partial artifact path 및 incomplete state를 기록하며 다른 independent run을 삭제하지 않는다.

Implements: `FR-025`, `NFR-008`, `AC-020`

## 12. Metrics and Post-processing

### 12.1 처리 단계

| 단계 | 책임 | Stateful 여부 |
|---|---|---|
| Raw model output | upstream pure model | model state |
| Output conversion | per-model adapter | stateless |
| Algorithm map normalization | upstream/per-model integration | model state 가능 |
| Protocol post-processing | anomaly task integration | adapter state 가능 |
| Threshold application | anomaly task integration | adapter state |
| Metric aggregation | registered metric | run-local state |

Implements: `FR-013`, `FR-016`, `FR-017`, `FR-021`

### 12.2 Metric 정의

`[설계]` Metric은 reference와 동일한 input field, interpolation, mask inclusion, threshold 및 aggregation을 사용한다.

- image AUROC: continuous `pred_score`와 binary label
- pixel AUROC: continuous anomaly map과 모든 evaluation image의 binary mask
- AUPRO/PRO: reference와 같은 connected-component와 FPR limit
- F1: validation에서 결정된 threshold를 test에 고정 적용
- threshold-free metric에 thresholded prediction을 입력하지 않음

`[미확정]` AUPRO/PRO와 F1의 초기 필수 포함 여부 및 metric implementation source는 target reference 선정 후
확정한다.

Implements: `FR-016`, `NFR-001`, `GAP-008`

### 12.3 Calibration

`[설계]` Threshold, min/max, quantile 및 score distribution state는 calibration source split과 함께 저장한다.
Calibration은 idempotent해야 하며 checkpoint restore 후 test/predict에서 재계산하지 않는다.

Implements: `FR-012`, `FR-017`, `FR-021`, `CON-009`

### 12.4 Score/map shape

`[설계]` Pixel metric 직전 anomaly map과 mask의 shape가 같아야 한다. Shape가 다르면 silent resize하지 않고,
reference에서 승인된 interpolation rule이 있을 때만 명시적으로 변환한다.

Implements: `FR-013`, `FR-014`, `NFR-011`

## 13. Configuration

### 13.1 기존 config 유지

`[설계]` 현재 top-level `meta`, `runtime`, `data`, `model`, `loss`, `metrics`, `adapter`, `optim`, `train`, `output`
구조와 `_base` merge/override를 유지한다. 새 config framework를 만들지 않는다.

Implements: `FR-001`, `CON-003`, `NFR-010`

### 13.2 Generic과 model-specific 경계

| 영역 | Generic config | Model-specific config |
|---|---|---|
| Runtime | device, seed, AMP, determinism, network policy | reference가 요구하는 제한 override |
| Data | root, split, workers, primary batch | normalization, batch constraint, auxiliary data spec |
| Model | registry name | backbone, layers, model size, local weights |
| Optimization | optimizer/scheduler schema | parameter selection과 reference values |
| Train | epochs/max steps, monitor | validation preparation 및 cadence requirement |
| Metric | metric list | reference-required parameters |
| Reference | manifest identity | upstream model/config/source mapping |

User는 model config 선택으로 내부 차이를 받으며 auxiliary iterator나 parameter group을 직접 조립하지 않는다.

Implements: `FR-006`, `FR-007`, `FR-008`, `FR-022`

### 13.3 Validation rules

`[설계]` Config validation은 construction 전에 다음을 검사한다.

- optimizer-required lifecycle에 optimizer가 존재하는가
- optimizer-free lifecycle에 잘못된 scheduler가 없는가
- scheduler cadence와 max steps/epochs가 유효한가
- required auxiliary loader와 local asset이 존재하는가
- model-specific input constraint가 충족되는가
- monitor metric이 선언되었는가
- reference manifest의 필수 field가 있는가
- split protocol이 명시되었는가

Implements: `FR-006`, `FR-008`, `FR-023`, `NFR-011`

### 13.4 Reference metadata

`[설계]` Benchmark config는 reference manifest를 path 또는 immutable identifier로 참조한다. Resolved run output에는
manifest snapshot과 protocol diff를 저장한다.

Implements: `FR-018`, `FR-019`, `FR-020`, `FR-022`

## 14. Checkpoint and State Management

### 14.1 Ownership

`[설계]` Checkpoint file I/O는 기존 core checkpoint module이 소유한다. Model과 adapter는 serializable state만
제공한다.

### 14.2 Checkpoint fields

기존 field를 유지하고 다음을 추가한다.

```text
adapter_state
global_step
lifecycle_state or equivalent readiness evidence
protocol/reference identity
checkpoint schema version
```

Model-specific tensor state는 우선 `model.state_dict`에 포함한다. Adapter state는 tensor와 JSON-compatible scalar를
지원하되 device-independent하게 restore되어야 한다.

Implements: `FR-012`, `FR-021`, `FR-022`, `NFR-002`

### 14.3 Save timing

`[설계]` 두 checkpoint 의미를 구분한다.

- selection state: validation monitor로 선택된 training state
- inference-ready state: 선택 state에 final calibration/finalization을 적용한 state

사용자-facing evaluate/predict는 inference-ready checkpoint를 기본으로 한다. 현재 `best.pth` convention을
유지할지 별도 이름을 사용할지는 backward compatibility 확인 후 결정한다.

Implements: `FR-009`, `FR-010`, `FR-012`, `FR-021`

### 14.4 Restore validation

`[설계]` Load 시 schema, model identity, adapter identity, required state, source revision 및 config compatibility를
검사한다. Adapter state가 필수인 calibrated model에서 누락되면 uncalibrated로 조용히 진행하지 않는다.

Implements: `FR-010`, `FR-012`, `FR-023`, `NFR-011`

### 14.5 State round-trip

`[설계]` 동일 input에 대해 save 전과 새 process restore 후의 raw output, calibrated score/label 및 map/mask를
허용 수치 오차 내에서 비교한다.

Implements: `AC-010`, `NFR-002`

## 15. Error Handling and Validation

### 15.1 Early errors

| 오류 | 검출 시점 | 동작 |
|---|---|---|
| unsupported registry name | config validation | available entries와 함께 실패 |
| incompatible model/adapter | construction | expected contract와 실제 identity를 보고 |
| missing local weight | asset validation | exact path와 asset id를 보고 |
| weight key/checksum mismatch | model construction | strict failure, random fallback 금지 |
| invalid dataset/category structure | dataset construction | expected directory/sample을 보고 |
| missing abnormal mask | dataset validation | sample id/path와 함께 실패 |
| invalid split or leakage | split validation | overlapping ids와 protocol을 보고 |
| missing auxiliary loader | pre-fit validation | required loader name을 보고 |
| optimizer/loss mismatch | pre-fit validation | lifecycle requirement를 보고 |
| non-ready checkpoint | evaluate/predict load | missing state와 preparation requirement를 보고 |
| reference manifest mismatch | benchmark preflight | field-level protocol diff를 보고 |
| metric shape/label mismatch | evaluation preflight | score/target shape와 metric id를 보고 |

Implements: `FR-023`, `FR-025`, `NFR-011`, `CON-007`

### 15.2 Exception boundary

`[설계]` CLI 단일 실행은 user-facing error로 실패한다. Benchmark는 현재처럼 독립 run boundary에서 exception을
failed result로 변환하며 traceback/log를 보존한다.

Implements: `FR-025`, `AC-020`

## 16. Offline / Local Asset Behavior

### 16.1 Network policy

`[설계]` 현재 process-start offline guard와 environment 설정을 유지한다. Third-party model constructor 및
dataset 준비 함수가 호출되기 전에 guard가 활성화되어야 한다.

Implements: `NFR-006`, `CON-006`

### 16.2 Local resolution

`[설계]` 모든 필수 asset은 resolved config 또는 asset manifest의 explicit absolute/local path로 resolution한다.
Environment default가 있더라도 resolved config에 최종 path를 기록한다.

Implements: `FR-022`, `FR-023`, `NFR-006`

### 16.3 Implicit download 방지

`[설계]` Architecture 생성은 `weights=None`, `pretrained=False` 또는 동등한 no-download mode를 사용한다. 이후
local state를 strict load한다. anomalib datamodule의 `prepare_data`, EfficientAD download helper 및 `torch.hub`
download path는 product runtime에서 호출하지 않는다.

Implements: `CON-002`, `CON-006`, `CON-007`, `OOS-011`

### 16.4 Asset manifest

`[설계]` Asset entry는 id, type, local path, source URL 또는 provenance, checksum, expected format, consumer 및
optional/required 상태를 가진다. Directory asset은 version marker 또는 deterministic file manifest를 사용한다.

Implements: `FR-008`, `FR-022`, `FR-023`, `NFR-002`

### 16.5 Optional online behavior

`[설계]` 향후 optional download 기능이 생겨도 offline core requirement와 분리되고 명시적 opt-in이어야 한다.
현재 범위에서는 구현하지 않는다.

Implements: `CON-006`, `OOS-011`

## 17. Testing Strategy

### 17.1 Unit tests

- upstream output type/shape에서 common anomaly output으로의 conversion
- image/mask transform alignment와 binary mask
- normal evaluation image의 zero mask
- optimizer-present/optimizer-none train-step validation
- trainable parameter selection과 scheduler cadence
- validation hook order
- auxiliary loader resolution
- metric input, reset, aggregation
- threshold/normalization state save/load
- missing/mismatched asset error
- reference manifest diff

Implements: `NFR-007`, `AC-006`, `AC-007`, `AC-012`, `AC-019`

### 17.2 Integration tests

- Dataset → collate → model → adapter → train/evaluate
- gradient lifecycle
- no-gradient collection/finalize lifecycle
- auxiliary loader lifecycle
- checkpoint save → new process load → evaluate/predict
- calibrated prediction과 visualization input
- benchmark failure isolation
- existing Classification/Segmentation/Detection regression

Implements: `AC-001`, `AC-004`, `AC-010`, `AC-016`, `AC-018`, `AC-020`

### 17.3 Smoke tests

`[설계]` 빠른 smoke는 local fixture 또는 승인된 small category/subset과 짧은 budget을 사용한다. 목적은 shape,
state transition, offline behavior 및 command completion이며 reference accuracy pass를 주장하지 않는다.

Implements: `FR-001`, `NFR-007`

### 17.4 Reference benchmark tests

`[설계]` Long-running reference test는 CI fast suite와 분리한다.

- pinned anomalib reference run
- same/equivalent integration run
- protocol diff가 승인 상태인지 확인
- 반복 reference 결과로 확정한 tolerance 적용
- raw metric/result/config/environment 보존

Implements: `FR-019`, `FR-020`, `NFR-001`, `NFR-002`, `NFR-012`, `AC-008`, `AC-009`, `AC-013`, `AC-014`

### 17.5 Static/purity tests

- core engine/CLI의 task명·model명 conditional 탐지
- Lightning/anomalib Engine runtime import 탐지
- implicit download API 탐지
- vendored source manifest와 local diff 검증
- license/notice 존재 검증

Implements: `NFR-003`, `NFR-004`, `CON-002`, `CON-005`, `CON-011`, `AC-002`, `AC-003`, `AC-017`

## 18. Migration from Legacy Repositories

| Legacy component | Action | Target | Reason |
|---|---|---|---|
| anomalib-derived `torch_model.py` | reference/compare, target revision에서 재취득 우선 | per-model algorithm area | legacy exact revision이 고정되지 않음 |
| `loss.py`, `anomaly_map.py` | reference/compare, upstream fidelity 검증 | per-model algorithm area | algorithm 의미 보존 |
| local `TimmFeatureExtractor` adaptation | adapt candidate | model component/offline loading | no-download architecture와 local weight 경험 |
| STFPM trainer | reference-only lifecycle evidence | per-model adapter specification | student-only SGD와 loss invocation 지식 |
| EfficientAD trainer | reference-only lifecycle evidence | per-model adapter specification | auxiliary loader, statistics, quantile 지식 |
| PatchCore/PaDiM trainer | reference-only lifecycle evidence | generic no-optimizer capability | collect/finalize 필요성 증거 |
| MVTec/VisA/BTAD Dataset | selective reference | current Dataset registry | parsing 규칙만 재사용, contract는 current 우선 |
| backbone filename mapping | adapt into asset manifest | offline asset validation | environment magic 제거와 provenance 필요 |
| `BaseTrainer` | remove | none | current `Trainer`와 중복 |
| `Evaluator`/Predictor | remove | none | current adapter/engine/CLI와 중복 |
| Factory | remove | none | current registry와 중복 |
| Config merge | remove | none | current config system과 중복 |
| EarlyStopper | reference only if approved protocol requires | current training config/capability | legacy framework 보존 불필요 |
| experiment loop scripts | remove | current benchmark runner | orchestration 중복 |
| `anomaly_detection_dev` Phase framework | reference-only | tests/document evidence | 구현 architecture source가 아님 |

Implements: `FR-003`, `FR-004`, `FR-024`, `NFR-010`, `OOS-004`

## 19. Dependency Changes

### 19.1 현재 확인

`[확인]` 현재 requirements는 PyTorch, torchvision, torchmetrics, PyYAML, Pillow 및 기존 task dependency를
포함하고 `timm`과 anomalib는 포함하지 않는다.

### 19.2 후보 dependency

| Candidate | 필요 근거 | 기존 dependency 대체 가능성 | Scope | 결정 상태 |
|---|---|---|---|---|
| `timm` | 분석한 STFPM upstream feature extractor | torchvision model injection으로 가능한지 target revision 검증 필요 | runtime | 미확정 |
| `safetensors` | 선택 backbone asset format이 요구할 수 있음 | `.pth`만 승인하면 불필요 | runtime optional | 미확정 |
| connected-component/AUPRO 지원 | reference metric이 AUPRO를 요구할 수 있음 | torch/torchmetrics로 동일 정의 구현 가능한지 검증 필요 | runtime/test | 미확정 |
| anomalib package | reference run에는 필요 | product runtime에는 허용하지 않음 | benchmark reference environment only | runtime 금지 |
| Lightning | anomalib reference run의 transitive dependency | product runtime에는 불필요 | reference environment only | runtime 금지 |

새 dependency는 target model/metric을 확정한 뒤 사용자 승인과 offline package availability를 확인한다. Reference
environment dependency와 product runtime dependency를 분리한다.

Implements: `NFR-014`, `CON-002`, `CON-006`, `GAP-012`

## 20. PRD Traceability Matrix

### 20.1 Functional Requirements

| PRD ID | Requirement | SPEC Section | Verification |
|---|---|---|---|
| FR-001 | 공통 실행 workflow | 2.1, 4.1, 8, 9, 10, 11 | command integration tests |
| FR-002 | Anomaly task 통합 | 2.3, 3, 4.1 | registry/construction test |
| FR-003 | anomalib pure model 재사용 | 4.5, 6.1, 6.2, 18 | source manifest/diff test |
| FR-004 | 최소 adaptation | 4.5, 6.1, 6.3, 18 | upstream diff review |
| FR-005 | 이질 lifecycle | 3.3, 7, 8 | gradient/no-gradient integration tests |
| FR-006 | model optimization | 3.3, 6.7, 7.3, 8 | parameter/cadence tests |
| FR-007 | model preprocessing | 5.4, 13.2 | resolved transform tests |
| FR-008 | auxiliary asset/data | 5.5, 7.2, 8, 16.4 | auxiliary loader integration test |
| FR-009 | 학습 결과 선택 | 5.3, 7.4, 8.2, 14.3 | leakage/selection tests |
| FR-010 | 평가 | 9, 14.4 | checkpoint evaluation test |
| FR-011 | prediction | 4.3, 10 | single/directory prediction tests |
| FR-012 | calibrated prediction | 9, 10, 12.3, 14 | checkpoint round-trip test |
| FR-013 | anomaly output semantics | 4.2~4.4, 10.2, 12 | output conversion tests |
| FR-014 | MVTec | 5.2, 5.4, 12.4 | dataset fixture/integration test |
| FR-015 | dataset 독립성 | 3.2, 4.4, 5.1, 5.6 | alternate dataset contract test |
| FR-016 | anomaly metric | 4.4, 9.2, 12.2 | metric equivalence tests |
| FR-017 | post-processing | 4.5, 10, 12 | state/threshold tests |
| FR-018 | benchmark orchestration | 2.7, 11, 13.4 | benchmark integration test |
| FR-019 | reference equivalence | 11, 17.4 | paired benchmark |
| FR-020 | protocol difference | 11.2~11.3, 13.4 | manifest diff test |
| FR-021 | checkpoint 완전성 | 6.8, 8.3, 12.3, 14 | round-trip test |
| FR-022 | 재현 정보 | 5.3, 11.2, 13.4, 14, 16.4 | artifact schema test |
| FR-023 | local asset 검증 | 6.4, 13.3, 15, 16 | offline/missing asset tests |
| FR-024 | 새 모델 추가 | 2.2, 3.2, 4.1, 6.3 | second-lifecycle integration review |
| FR-025 | 실패 격리 | 11.5, 15.2 | injected benchmark failure |

### 20.2 Non-Functional Requirements

| PRD ID | Requirement | SPEC Section | Verification |
|---|---|---|---|
| NFR-001 | reference 성능 | 11, 12.2, 17.4 | tolerance benchmark |
| NFR-002 | 재현성 | 5.3, 8.3, 11.2, 14, 16.4, 17.4 | repeated run/round-trip |
| NFR-003 | upstream fidelity | 4.5, 6.1~6.2, 17.5 | manifest/diff/static review |
| NFR-004 | task-agnostic engine | 2.3, 3.2, 7.1, 17.5 | purity scan/regression |
| NFR-005 | 확장성 | 3.2~3.3, 7.1, 17.2 | additional lifecycle test |
| NFR-006 | offline | 5.5, 6.4, 16 | network-blocked lifecycle |
| NFR-007 | testability | 17 | layered test evidence |
| NFR-008 | 관찰 가능성 | 2.9, 9.2, 11.3, 11.5, 15.2 | artifact/failure inspection |
| NFR-009 | dataset 독립성 | 3.2, 4.4, 5 | contract review |
| NFR-010 | 유지보수성 | 2.2, 3, 6.3, 18 | responsibility review |
| NFR-011 | 명시성 | 7.5, 10.3, 11.3, 13.3, 14.4, 15 | negative tests |
| NFR-012 | 수치 현실성 | 11.4, 17.4 | repeated reference statistics |
| NFR-013 | 기존 task 회귀 | 17.2 | existing task regression |
| NFR-014 | 최소 dependency | 19 | dependency review/offline install check |

### 20.3 Constraints

| PRD ID | Constraint | SPEC Section | Verification |
|---|---|---|---|
| CON-001 | pure PyTorch runtime | 3.3, 8 | dependency/runtime inspection |
| CON-002 | Lightning/Engine 금지 | 6.2, 16.3, 17.5, 19 | import/static scan |
| CON-003 | boilerplate lifecycle 소유 | 2, 3.1, 8, 14 | architecture review |
| CON-004 | algorithm 의미 보존 | 4.5, 6.1, 6.5 | upstream diff/model parity |
| CON-005 | engine model-name 분기 금지 | 3.2~3.3, 7.1, 17.5 | purity scan |
| CON-006 | local asset 우선 | 5.5, 6.4, 16, 19 | offline test |
| CON-007 | silent fallback 금지 | 6.4, 14.4, 15, 16.3 | negative asset test |
| CON-008 | reference revision 고정 | 6.1~6.2, 11.2, 13.4 | manifest validation |
| CON-009 | test leakage 금지 | 5.2~5.3, 7.4, 8.2, 9.1, 12.3 | split access test |
| CON-010 | split protocol 명시 | 5.2~5.3, 13.3 | split manifest test |
| CON-011 | license/attribution | 6.1~6.2, 17.5 | notice/source audit |
| CON-012 | 문서 우선순위 | 1, 21 | document review/user gate |

### 20.4 Out of Scope guards

| PRD ID | Guard | SPEC enforcement |
|---|---|---|
| OOS-001 | anomalib 전체 재구현 금지 | 1.4, 6.2, 19 |
| OOS-002 | 새 algorithm 연구 제외 | 1.4, 6.1 |
| OOS-003 | upstream 대규모 rewrite 제외 | 6.1 |
| OOS-004 | legacy framework 개선 제외 | 3.3, 6.3, 18 |
| OOS-005 | anomalib API compatibility 제외 | 6.2, 14 |
| OOS-006 | 단일 training step 강제 제외 | 3.3, 7 |
| OOS-007 | 모든 모델 즉시 지원 제외 | 7.2, 21 |
| OOS-008 | 모든 dataset 즉시 지원 제외 | 5.6, 21 |
| OOS-009 | Enterprise MLOps 제외 | 2.9 |
| OOS-010 | Bitwise 동일성 제외 | 11.4 |
| OOS-011 | 자동 download service 제외 | 16.3~16.5 |

### 20.5 Acceptance Criteria

| PRD ID | Acceptance | SPEC Section | Verification |
|---|---|---|---|
| AC-001 | 공통 command | 8~11, 17.2 | initial model command matrix |
| AC-002 | upstream 추적 | 6.1~6.2, 17.5 | source audit |
| AC-003 | Lightning 비의존 | 6.2, 17.5, 19 | runtime/import scan |
| AC-004 | 서로 다른 lifecycle | 7, 17.2 | gradient + non-standard model |
| AC-005 | model protocol | 5.4~5.5, 6.7, 11.2, 13 | resolved protocol inspection |
| AC-006 | dataset contract | 5, 17.1 | MVTec dataset tests |
| AC-007 | metric | 4.4, 12, 17.1 | reference metric fixtures |
| AC-008 | 성능 재현 | 11.4, 17.4 | approved tolerance benchmark |
| AC-009 | protocol 진단 | 11.3, 17.4 | forced diff report |
| AC-010 | checkpoint round-trip | 14.5, 17.2 | new-process parity |
| AC-011 | offline lifecycle | 16, 17.2 | blocked-network commands |
| AC-012 | missing asset | 15, 17.1 | negative tests |
| AC-013 | 재현성 기록 | 11.2, 13.4, 16.4 | artifact schema test |
| AC-014 | 반복 재현성 | 11.4, 17.4 | repeated runs |
| AC-015 | leakage 방지 | 5.3, 7.4, 9.1 | split access instrumentation |
| AC-016 | 새 모델 비용 | 3.2~3.3, 6.3, 17.2 | integration change review |
| AC-017 | engine 순수성 | 3.2, 7.1, 17.5 | conditional scan |
| AC-018 | 기존 task 회귀 | 17.2 | regression suite |
| AC-019 | 단계적 검증 | 17 | test evidence matrix |
| AC-020 | failure isolation | 11.5, 15.2 | injected failure benchmark |

### 20.6 Current Gap closure mapping

| Gap ID | Closure section | Evidence required |
|---|---|---|
| GAP-001 | 6.1~6.3, 18 | pinned upstream source and diff |
| GAP-002 | 3.3, 7.3, 8 | optimizer-none integration test |
| GAP-003 | 6.7, 13.2 | STFPM parameter selection test |
| GAP-004 | 5.4, 13.2 | EfficientAD input protocol test |
| GAP-005 | 5.5, 7.2, 8 | auxiliary loader test |
| GAP-006 | 7.2~7.4 | memory/statistics lifecycle test |
| GAP-007 | 10, 12.3, 14 | checkpoint round-trip |
| GAP-008 | 12.2, 17.4 | selected metric parity |
| GAP-009 | 5.2~5.3, 11.2, 21 | approved split manifest |
| GAP-010 | 11.1~11.3 | equivalence benchmark artifact |
| GAP-011 | 11.2, 13.4, 16.4 | provenance completeness test |
| GAP-012 | 6.2, 6.4, 19, 21 | dependency/asset decision |
| GAP-013 | 11.4, 17.4, 21 | repeated reference baseline |

## 21. Open Questions / Deferred Decisions

| ID | Question | Why it matters | Options | Recommended direction | Needed before PLAN defines |
|---|---|---|---|---|---|
| OQ-001 | 실제 current source는 어디인가 | 현재 workspace에는 source가 없어 uncommitted/local 차이를 검증하지 못함 | remote `71261cef` 사용 / local repo 제공 | 실제 구현 대상 checkout을 제공하고 revision 고정 | 모든 구현 범위 |
| OQ-002 | target anomalib revision은 무엇인가 | source, dependency, lifecycle, metric이 version별로 다름 | release tag / commit | 검증 가능한 commit hash 고정 | model/source 및 benchmark 작업 |
| OQ-003 | 최초 모델 집합은 무엇인가 | AC-004가 서로 다른 lifecycle을 요구 | STFPM+EfficientAD+PatchCore/PaDiM 중 선택 | gradient/auxiliary와 no-gradient lifecycle을 모두 포함 | model integration 범위 |
| OQ-004 | 최초 MVTec category 범위는 무엇인가 | 실행 비용과 metric tolerance에 영향 | bottle / 일부 category / 15 category | bottle로 pipeline 검증 후 reference 범위 확대가 합리적이나 사용자 확정 필요 | dataset/benchmark 범위 |
| OQ-005 | MVTec validation/test protocol은 무엇인가 | current disjoint 33/50과 anomalib default same-as-test가 다름 | strict disjoint / exact reference / 두 run 모두 | correctness reference와 leakage-safe final evaluation을 별도 protocol로 기록하는 방향 권장 | split manifest와 acceptance benchmark |
| OQ-006 | metric 초기 필수 세트는 무엇인가 | implementation dependency와 acceptance가 달라짐 | AUROC only / AUPRO/F1 포함 | target reference가 보고하는 metric을 필수로 선택 | metric 및 tolerance 작업 |
| OQ-007 | tolerance와 반복 횟수는 무엇인가 | AC-008 pass/fail 기준 | 고정 수치 / repeated baseline 기반 | target environment 반복 결과로 승인 | long benchmark execution |
| OQ-008 | upstream source transport 방식은 무엇인가 | update/diff/license 관리에 영향 | vendor / sync script / narrow package dependency | product runtime에서 anomalib 전체 dependency 없이 immutable source+diff가 남는 방식 | source integration 작업 |
| OQ-009 | `timm`을 허용하는가 | STFPM upstream fidelity와 offline package 가용성에 영향 | runtime dependency / module injection adaptation | target source diff가 더 작은 선택을 dependency 비용과 함께 승인 | STFPM integration |
| OQ-010 | AUPRO dependency를 어떻게 제공하는가 | exact metric parity에 영향 | upstream narrow port / existing libraries / 별도 verified implementation | reference fixture parity를 먼저 비교 | metric integration |
| OQ-011 | local asset inventory와 checksum은 무엇인가 | offline preflight와 reproducibility에 필요 | 현재 파일 조사 / 외부 준비 | 실제 사용 environment에서 manifest 작성 | model construction/benchmark |
| OQ-012 | checkpoint naming/backward compatibility 정책은 무엇인가 | selection state와 inference-ready state 구분 필요 | `best.pth` 갱신 / 별도 finalized checkpoint | 기존 CLI 기본을 깨지 않되 의미를 명시 | checkpoint implementation |
| OQ-013 | reference run environment를 분리할 수 있는가 | product runtime에는 anomalib/Lightning을 넣을 수 없음 | 별도 environment / 외부 결과 import | pinned 별도 reference environment 권장 | reference baseline |
| OQ-014 | full benchmark compute budget은 얼마인가 | STFPM/EfficientAD reference budget이 smoke보다 큼 | full official / capped equivalent / 외부 baseline | smoke와 acceptance benchmark를 분리 | PLAN의 verification 범위 |

Implements: `CON-008`, `CON-012`, `NFR-001`, `NFR-012`, `NFR-014`

## 22. Implementation Impact Summary

### 22.1 Existing files likely modified

`[설계 영향]` 실제 checkout 확인 후 경로를 다시 검증해야 하지만, revision `71261cef` 기준 예상 영향은 다음과
같다.

- `src/core/adapter.py`: optional optimization/state/validation hook contract
- `src/core/engine.py`: optimizer-none, scheduler cadence, validation hook, adapter state invocation
- `src/core/builders.py`: adapter-aware optimization과 named auxiliary loader construction
- `src/core/config.py`: optional optimizer, auxiliary data, reference metadata validation
- `src/core/checkpoint.py`: adapter/global-step/protocol state
- `src/cli/commands.py`: unified construction과 adapter checkpoint restore
- `src/bench/runner.py`, `control.py`, `leaderboard.py`: equivalence manifest/diff/result fields
- `src/tasks/anomaly/adapter.py`: common output/metric/post-processing behavior
- `src/tasks/anomaly/dataset.py`, `transform.py`, `postprocess.py`: contract 보완
- anomaly configs와 asset manifest

### 22.2 New modules likely required

- pinned upstream pure-model source area 또는 sync metadata
- per-model anomaly adapter/integration modules
- stateful anomaly post-processing state representation
- reference manifest/protocol diff validation
- selected reference metric implementation
- source/license/asset provenance manifest

정확한 module 이름과 directory는 실제 checkout과 OQ 결정 후 확정한다.

### 22.3 Reusable existing modules

- Registry와 `TaskAdapter`
- CLI command surface
- `Trainer.evaluate`/`predict`의 task-agnostic loop
- config inheritance/override
- `RunContext`, seed, device, deterministic mode
- offline guard와 strict local weight loader
- checkpoint container와 RNG capture
- MVTec parsing, split disjoint check, anomaly collate/visualization
- benchmark failure isolation, control, profiling, leaderboard
- JSON/YAML/CSV output utilities

### 22.4 Obsolete legacy modules

Legacy `BaseTrainer`, `Evaluator`, Predictor, Factory, Config, experiment loops 및 output manager는 이식하지 않는다.
Model trainer는 lifecycle evidence로만 사용한다.

### 22.5 High-risk integration points

- upstream model fidelity와 import/dependency closure
- EfficientAD auxiliary loader, normalization, quantile 및 scheduler cadence
- no-gradient model의 finalize 시점
- threshold/calibration checkpoint round-trip
- MVTec reference split과 leakage-safe split의 구분
- metric implementation과 map interpolation parity
- reference manifest completeness와 tolerance evidence
- core 변경 후 기존 task regression
- implicit network access 차단

### 22.6 PLAN readiness gate

PLAN 작성 전에 최소한 OQ-001, OQ-002, OQ-003, OQ-005, OQ-006, OQ-011, OQ-013, OQ-014에 대한 사용자
결정 또는 검증 가능한 사실이 필요하다. 이 결정 전에도 공통 contract 검토는 가능하지만, model integration과
reference benchmark의 완료 조건을 확정할 수는 없다.
