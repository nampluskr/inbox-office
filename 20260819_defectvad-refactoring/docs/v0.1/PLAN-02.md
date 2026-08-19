## Phase P4 — Model Lifecycle Wave 1 Accepted

### Objective

안정화된 contract 위에서 서로 다른 모델 integration을 독립 workstream으로 수행한다. 기본 승인 후보는 auxiliary/calibration lifecycle의 EfficientAD와 no-gradient memory-bank lifecycle의 PatchCore다.

### References

- BRIEF: §5, §6.2, §13, §11 P-03/P-04/P-10
- PRD: FR-003~FR-008, FR-010~FR-024, NFR-001~NFR-011, CON-001~CON-011
- SPEC: §5.4~§5.5, §6~§12, §14~§18

### Prerequisites

P3 complete; approved models and all model-specific assets available.

### Scope

각 workstream은 pure upstream source, model adapter/config/tests 및 per-model acceptance만 수정한다. Generic engine, common task contract, global config schema 수정은 금지하며 필요 시 P4-T03 shared change review로 중단·승격한다.

### Expected Code Impact

- Add/replace: model-specific pure source, loss/map and integration modules
- Add/modify: `configs/anomaly/efficientad.yaml`, PatchCore config, asset/source manifests
- Add: model-specific parity/lifecycle/command/checkpoint/reference tests
- Avoid: unassigned changes to `src/core/*`, common anomaly contract and unrelated models

### Tasks

#### P4-T01 — Integrate EfficientAD on the established contract

- Description: pinned pure-PyTorch EfficientAD source를 최소 수정으로 통합하고 teacher statistics, student/AE optimization, Imagenette auxiliary stream, input normalization, validation quantile, step scheduler 및 state를 구현한다. Generic core insufficiency가 확인되면 독자 수정하지 않고 P4-T03에 보고한다.
- PRD refs: FR-003~FR-008, FR-010~FR-013, FR-017, FR-021~FR-024
- SPEC refs: §5.4~§5.5, §6, §7.2~§7.5, §8~§10, §14, §18
- Depends on: P3-T06
- Parallelizable: Yes
- Parallel Group: `MODEL-WAVE-1`
- Verification: pure parity, auxiliary lifecycle, transform/batch, train/evaluate/predict, checkpoint state, offline smoke and minimal reference comparison pass.

#### P4-T02 — Integrate PatchCore on the established contract

- Description: pinned pure-PyTorch PatchCore source를 최소 수정으로 통합하고 optimizer-none feature collection, coreset/memory-bank finalize, anomaly output 및 serialized state를 구현한다. Generic core insufficiency가 확인되면 독자 수정하지 않고 P4-T03에 보고한다.
- PRD refs: FR-003~FR-006, FR-010~FR-013, FR-017, FR-021~FR-024
- SPEC refs: §6, §7.2~§7.5, §8~§10, §14, §18
- Depends on: P3-T06
- Parallelizable: Yes
- Parallel Group: `MODEL-WAVE-1`
- Verification: pure parity, optimizer-none collect/finalize, train/evaluate/predict, checkpoint memory state, offline smoke and minimal reference comparison pass.

#### P4-T03 — Adjudicate shared contract change requests

- Description: model agents가 입증한 공통 capability gap만 별도 shared change로 검토한다. 승인 시 core 변경과 전체 lifecycle regression을 한곳에서 수행하고 P4-T01/P4-T02를 재개한다. 요청이 없으면 no-op gate로 기록한다.
- PRD refs: FR-024, NFR-004/NFR-005/NFR-010/NFR-013, CON-005
- SPEC refs: §3.3, §7.1, §17.2, §17.5
- Depends on: P3-T06
- Parallelizable: No
- Verification: request별 two-model evidence, SPEC compatibility, purity and full regression 결과가 존재하거나 no-request가 기록된다. P4-T01/P4-T02는 승인된 shared change가 필요한 동안 blocked 상태를 유지한다.

#### P4-T04 — Run per-model acceptance matrix

- Description: STFPM, EfficientAD, PatchCore 각각에 대해 smoke, command lifecycle, state round-trip, missing asset, minimal reference comparison과 provenance를 동일 checklist로 검증한다.
- PRD refs: FR-001, FR-010~FR-023, NFR-001/NFR-002/NFR-006~NFR-008/NFR-011
- SPEC refs: §9~§17
- Depends on: P4-T01, P4-T02, P4-T03
- Parallelizable: No
- Verification: model별 acceptance artifact와 실패 진단이 완전하며 shared contract regression이 통과한다.

#### P4-T05 — Freeze model integration wave

- Description: model workstream이 공통 engine을 복제하지 않았고 upstream diff/license 및 extension cost가 요구사항을 만족하는지 review한다.
- PRD refs: FR-003, FR-004, FR-024, NFR-003~NFR-005/NFR-010, CON-004~CON-005/CON-011
- SPEC refs: §6.1~§6.3, §17.5, §18
- Depends on: P4-T04
- Parallelizable: No
- Verification: source audit, architecture purity, duplicate framework scan and change-scope review pass.

### Verification

- Unit: pure model parity, model-specific loss/output/state
- Integration: EfficientAD auxiliary lifecycle and PatchCore collect/finalize lifecycle
- Smoke: per-model offline command matrix
- Reference benchmark: per-model minimal frozen comparison
- Regression: STFPM and existing task suites after merge

### Exit Criteria

- EfficientAD와 PatchCore workstream의 model-specific tests와 command matrix가 통과한다.
- 각 모델의 state가 새 process checkpoint round-trip에서 복원된다.
- 각 모델의 upstream source/diff/license와 asset provenance가 완전하다.
- Shared core change는 P4-T03을 거쳤으며 model agent의 독자 core redesign이 없다.
- STFPM 포함 세 lifecycle의 common workflow가 유지된다.

### Risks / Watch Items

- 두 agent가 같은 core/config schema를 독립 수정하는 것
- EfficientAD teacher quantile에 test data를 사용하는 것
- PatchCore memory bank가 checkpoint에서 누락되는 것

### Parallel Execution

- Parallel Group: `MODEL-WAVE-1`
- Workstreams: P4-T01 EfficientAD, P4-T02 PatchCore
- Shared Dependencies: P3-T06 contract, P0 assets/reference fixtures
- Merge/Gate requirement: core 변경 요청은 P4-T03에서 단일 shared task로 처리하고 P4-T04에서 통합 검증한다.

## Phase P5 — Cross-Model Reference Equivalence Proven

### Objective

Benchmark를 단순 leaderboard가 아니라 integration correctness gate로 완성한다. 동일하거나 명시적으로 동등한 protocol에서 pinned anomalib reference와 각 integration을 비교하고 tolerance, 반복 재현성, 차이 진단 및 실패 격리를 검증한다.

### References

- BRIEF: §8, §9 G-06/G-09, §11 P-05/P-07
- PRD: FR-018~FR-020, FR-022, FR-025, NFR-001/NFR-002/NFR-008/NFR-012, CON-008~CON-010, AC-008/AC-009/AC-013~AC-015/AC-020
- SPEC: §11, §12, §13.4, §15.2, §17.4

### Prerequisites

P4 complete; long benchmark assets and compute budget approved.

### Scope

Reference-equivalence manifest, protocol diff, repeated acceptance, cross-model summary와 failure isolation을 구현·실행한다. 모델 알고리즘 tuning이나 새 algorithm 연구는 하지 않는다.

### Expected Code Impact

- Modify: `src/bench/runner.py`, `control.py`, `leaderboard.py` and common construction path as already designed
- Add: reference manifest/diff schema, benchmark profiles, result diagnostics and validation scripts/tests
- Add: approved long-run configs and raw/result artifacts

### Tasks

#### P5-T01 — Implement reference manifest and protocol diff validation

- Description: model/source/config/dataset/split/transform/optimizer/weight/post-process/metric/environment identity를 기록하고 reference와 integration 차이를 구조화한다.
- PRD refs: FR-018~FR-020, FR-022, NFR-002/NFR-008
- SPEC refs: §11.2~§11.3, §13.4
- Depends on: P4-T05
- Parallelizable: Yes
- Parallel Group: `BENCH-PREP`
- Verification: intentional protocol mismatch가 정확한 field diff와 approval state를 생성한다.

#### P5-T02 — Harden benchmark isolation and result completeness

- Description: 한 model/category 실패가 독립 실행 결과를 손상시키지 않도록 status, error, unfinished scope와 artifact를 보존한다.
- PRD refs: FR-018, FR-025, NFR-008, AC-020
- SPEC refs: §11.5, §15.2
- Depends on: P4-T05
- Parallelizable: Yes
- Parallel Group: `BENCH-PREP`
- Verification: injected failure 후 성공 row, failure row, diagnostics와 leaderboard integrity가 보존된다.

#### P5-T03 — Approve empirical tolerance and reproducibility envelope

- Description: P0 pinned reference 반복과 target environment 반복으로 metric tolerance와 repeat count를 확정하고 acceptance 전에 기록한다.
- PRD refs: FR-019, NFR-001/NFR-002/NFR-012, CON-008
- SPEC refs: §11.4, §17.4, §21 OQ-007
- Depends on: P5-T01, P0-T05
- Parallelizable: No
- Verification: raw repeats, summary statistics, environment and approved tolerance record가 연결된다.

#### P5-T04 — Run per-model long reference acceptance

- Description: 승인된 모델 각각에 대해 pinned reference와 integration을 동일/equivalent protocol로 반복 실행한다.
- PRD refs: FR-019, FR-020, NFR-001/NFR-002/NFR-012, AC-008/AC-009/AC-014
- SPEC refs: §11.4, §17.4
- Depends on: P5-T02, P5-T03
- Parallelizable: Yes
- Parallel Group: `REFERENCE-RUNS`
- Verification: 각 모델 metric이 승인 tolerance를 통과하거나 complete protocol diagnosis를 남긴다.

#### P5-T05 — Validate cross-model controlled benchmark

- Description: 동일 category/control envelope에서 모델별 결과, protocol exception, resource profile과 failure status를 요약한다. 모델 고유 reference config를 억지로 동일 hyperparameter로 만들지 않는다.
- PRD refs: FR-018~FR-020, FR-025, NFR-008
- SPEC refs: §11.1~§11.5
- Depends on: P5-T04
- Parallelizable: No
- Verification: machine-readable results, human summary, protocol diff links and failure isolation evidence가 완전하다.

### Verification

- Unit: manifest/diff/result schema
- Integration: injected failure and resume/overwrite behavior
- Reference benchmark: per-model repeated acceptance and controlled cross-model summary
- Regression: existing benchmark workflow and leaderboard

### Exit Criteria

- 각 승인 모델의 reference comparison이 tolerance를 통과하거나 승인 가능한 protocol diagnosis를 남긴다.
- Tolerance가 acceptance run 전에 반복 evidence로 고정된다.
- Split 공유/leakage 상태가 결과에 명시된다.
- 한 실행 실패가 다른 결과를 삭제하거나 성공으로 오인시키지 않는다.
- Fast CI profile과 long reference profile이 분리된다.

### Risks / Watch Items

- 동일 hyperparameter 강제로 reference semantics를 훼손하는 것
- 실패 모델을 leaderboard에서 조용히 누락하는 것
- 비결정성 차이를 algorithm 오류 또는 반대로 단정하는 것

### Parallel Execution

- Parallel Groups: `BENCH-PREP`, `REFERENCE-RUNS`
- Workstreams: manifest/diff와 failure isolation 준비, 이후 모델별 long reference run
- Shared Dependencies: frozen reference protocol and P4 model acceptance
- Merge/Gate requirement: P5-T03 tolerance 승인 후에만 P5-T04 acceptance를 판정하고 P5-T05에서 통합한다.

## Phase P6 — Offline, Regression, and Release Evidence Complete

### Objective

승인된 모델과 기존 task 전체에서 offline, dependency, source purity, checkpoint 및 regression evidence를 최종 확인한다. 구현 범위와 운영 절차를 문서화하되 새로운 architecture나 모델을 추가하지 않는다.

### References

- BRIEF: §9 G-07~G-10, §10, §11
- PRD: NFR-003~NFR-011/NFR-013~NFR-014, CON-001~CON-007/CON-011, AC-003/AC-011/AC-012/AC-016~AC-019
- SPEC: §15~§19, §22

### Prerequisites

P5 complete.

### Scope

Network-blocked full lifecycle, negative asset tests, full regression, static purity/license audit와 final evidence index를 완료한다.

### Expected Code Impact

- Tests/scripts: offline lifecycle, purity/import/download scan, full task regression, reproducibility checks
- Documentation/artifacts: supported model protocol, asset preparation, provenance and acceptance evidence index
- Dependency files: only already approved minimal runtime/reference dependency separation

### Tasks

#### P6-T01 — Run network-blocked lifecycle and asset failure matrix

- Description: 모든 승인 모델의 train/evaluate/predict/benchmark를 local assets로 실행하고 dataset/weight/auxiliary asset 누락·불일치 실패를 검증한다.
- PRD refs: FR-023, NFR-006/NFR-011, CON-006~CON-007, AC-011~AC-012
- SPEC refs: §15, §16, §17.2
- Depends on: P5-T05
- Parallelizable: Yes
- Parallel Group: `FINAL-VALIDATION`
- Verification: network attempt 없음, full lifecycle 성공, negative cases의 actionable error와 no fallback 확인.

#### P6-T02 — Run full existing-task and benchmark regression

- Description: Classification, Segmentation, Detection, toy/anomaly와 common benchmark의 승인 suite를 실행한다.
- PRD refs: NFR-004/NFR-005/NFR-013, AC-018
- SPEC refs: §17.2
- Depends on: P5-T05
- Parallelizable: Yes
- Parallel Group: `FINAL-VALIDATION`
- Verification: full regression suite passes or every pre-existing failure is independently evidenced.

#### P6-T03 — Audit runtime purity, dependencies, source, and licenses

- Description: Lightning/anomalib Engine import, implicit download API, model-name core branch, vendored diff, notice와 unnecessary dependency를 검사한다.
- PRD refs: NFR-003/NFR-004/NFR-014, CON-001~CON-002/CON-004~CON-005/CON-011, AC-002~AC-003/AC-017
- SPEC refs: §16.3, §17.5, §19
- Depends on: P5-T05
- Parallelizable: Yes
- Parallel Group: `FINAL-VALIDATION`
- Verification: static scans, dependency review, source checksum/diff and attribution audit pass.

#### P6-T04 — Assemble final acceptance and reproducibility evidence

- Description: model별 pure/integration/dataset/metric/reference 결과와 protocol, asset, environment, unresolved limitations를 하나의 index로 연결한다.
- PRD refs: FR-022, NFR-002/NFR-007/NFR-008, AC-013/AC-019
- SPEC refs: §11.2, §13.4, §17, §22
- Depends on: P6-T01, P6-T02, P6-T03
- Parallelizable: No
- Verification: every acceptance criterion has linked machine-readable and human-readable evidence.

#### P6-T05 — Release gate review

- Description: BRIEF/PRD/SPEC 범위, non-goals, remaining decisions와 all phase exit criteria를 검토하여 완료 또는 명시적 block을 판정한다.
- PRD refs: CON-012, OOS-001~OOS-011
- SPEC refs: §1.4, §18, §21, §22
- Depends on: P6-T04
- Parallelizable: No
- Verification: requirement coverage, non-goal audit and release decision record are complete.

### Verification

- Unit/Integration: asset negative tests and checkpoint/state suites
- Smoke: all model command matrix with network blocked
- Reference benchmark: P5 evidence revalidated, not rerun without reason
- Regression: full existing task and common benchmark suite
- Static: dependency/import/download/model-branch/source/license scans

### Exit Criteria

- Offline full lifecycle and missing-asset failure matrix pass.
- Existing Classification/Segmentation/Detection and benchmark regression pass.
- Product runtime has no Lightning/anomalib Engine dependency or implicit download.
- Upstream source/diff/license and minimal dependency audit pass.
- Every in-scope acceptance criterion links to evidence; unresolved items are explicit blockers, not silent omissions.

### Risks / Watch Items

- reference-only dependencies leaking into product runtime
- long benchmark를 fast CI에 포함해 검증이 비현실적으로 되는 것
- documentation task에서 미승인 기능을 새 scope로 추가하는 것

### Parallel Execution

- Parallel Group: `FINAL-VALIDATION`
- Workstreams: P6-T01 offline, P6-T02 regression, P6-T03 purity/dependency audit
- Shared Dependencies: P5-T05
- Merge/Gate requirement: P6-T04가 세 evidence stream을 통합하고 P6-T05가 최종 판정한다.

## 4. Requirement Coverage Matrix

### 4.1 Functional Requirements

| PRD ID | SPEC Section | PLAN Phase/Task | Verification |
|---|---|---|---|
| FR-001 | §2.1, §8~§11 | P1-T02, P2-T03~T05, P4-T04 | command matrix |
| FR-002 | §2.3, §4.1 | P1-T01~T02 | registry/construction tests |
| FR-003 | §6.1~§6.2 | P0-T04, P2-T01, P4-T01~T02 | source manifest/parity |
| FR-004 | §6.1, §6.3 | P2-T01, P4-T01~T02/T05 | upstream diff audit |
| FR-005 | §3.3, §7, §8 | P2-T02, P3-T01~T05, P4-T01~T02 | heterogeneous lifecycle tests |
| FR-006 | §6.7, §7.3 | P2-T02, P3-T01, P4-T01~T02 | parameter/cadence tests |
| FR-007 | §5.4, §13.2 | P2-T02, P4-T01 | resolved transform tests |
| FR-008 | §5.5, §7.2 | P0-T03, P3-T03, P4-T01 | auxiliary stream tests |
| FR-009 | §5.3, §7.4 | P0-T02, P1-T04, P2-T03 | leakage/split tests |
| FR-010 | §9 | P1-T07, P2-T03~T04, P4-T04 | checkpoint evaluation |
| FR-011 | §10 | P1-T07, P2-T04, P4-T04 | file/directory prediction |
| FR-012 | §9, §10, §14 | P1-T03/T07, P2-T04, P3-T04 | calibrated round-trip |
| FR-013 | §4.2~§4.4 | P1-T01/T05, P2-T02, P4-T04 | output semantics tests |
| FR-014 | §5.2, §5.4 | P1-T04 | MVTec fixture tests |
| FR-015 | §4.4, §5 | P1-T01/T04 | dataset-independence contract |
| FR-016 | §12.2 | P0-T02, P1-T05, P5-T04 | metric fixture/parity |
| FR-017 | §4.5, §12 | P1-T03/T05, P2-T04, P4-T04 | post-process state tests |
| FR-018 | §11 | P2-T05, P5-T01~T05 | benchmark artifacts |
| FR-019 | §11.4 | P0-T04~T05, P2-T05, P5-T03~T04 | paired reference runs |
| FR-020 | §11.2~§11.3 | P0-T02, P2-T05, P5-T01/T04~T05 | protocol diff |
| FR-021 | §14 | P1-T03, P2-T04, P3-T04, P4-T04 | new-process round-trip |
| FR-022 | §13.4, §14, §16.4 | P0-T01/T03~T06, P1-T03/T06, P5-T01, P6-T04 | artifact completeness |
| FR-023 | §6.4, §15~§16 | P0-T03, P1-T06, P6-T01 | offline/negative asset tests |
| FR-024 | §3.2, §6.3 | P1-T02, P2-T02/T06, P3-T05~T06, P4-T05 | integration change review |
| FR-025 | §11.5, §15.2 | P5-T02/T05 | injected failure test |

### 4.2 Non-Functional Requirements

| PRD ID | SPEC Section | PLAN Phase/Task | Verification |
|---|---|---|---|
| NFR-001 | §11.4, §17.4 | P0-T05, P2-T05, P5-T03~T04 | approved tolerance benchmark |
| NFR-002 | §5.3, §14, §17.4 | P0-T01/T05, P1-T03, P3-T04, P5-T03~T04, P6-T04 | repeat/round-trip evidence |
| NFR-003 | §6.1~§6.2, §17.5 | P0-T04, P2-T01, P4-T05, P6-T03 | source diff audit |
| NFR-004 | §3.2, §17.5 | P1-T01, P2-T06, P3-T05, P6-T03 | purity scan |
| NFR-005 | §3.3, §7.1 | P2-T06, P3-T01/T05~T06, P6-T02 | lifecycle extension tests |
| NFR-006 | §16 | P0-T03, P1-T06, P4-T04, P6-T01 | network-blocked lifecycle |
| NFR-007 | §17 | P1-T01/T05/T07, P3-T05, P6-T04 | layered evidence |
| NFR-008 | §11.3, §15.2 | P2-T05, P5-T01~T05, P6-T04 | diagnostics/artifacts |
| NFR-009 | §3.2, §4.4, §5 | P1-T01/T04 | alternate contract review |
| NFR-010 | §3, §6.3, §18 | P1-T02, P2-T06, P3-T06, P4-T05 | responsibility review |
| NFR-011 | §15 | P0-T06, P1-T02/T06, P3-T04, P6-T01 | fail-fast negative tests |
| NFR-012 | §11.4, §17.4 | P0-T02/T05, P5-T03~T04 | repeated statistics |
| NFR-013 | §17.2 | P1-T07, P3-T05, P4-T03, P6-T02 | full regression |
| NFR-014 | §19 | P0-T03, P6-T03 | dependency audit |

### 4.3 Constraints

| PRD ID | SPEC Section | PLAN Phase/Task | Verification |
|---|---|---|---|
| CON-001 | §3.3, §8 | P3-T01~T05, P6-T03 | runtime/import inspection |
| CON-002 | §6.2, §17.5 | P0-T04, P6-T03 | Lightning/Engine scan |
| CON-003 | §2, §3.1 | P1-T02~T03, P3-T01~T04 | lifecycle ownership review |
| CON-004 | §4.5, §6.1 | P2-T01~T02, P4-T01~T02, P6-T03 | algorithm parity/diff |
| CON-005 | §3.2, §17.5 | P2-T06, P3-T05~T06, P4-T03/T05, P6-T03 | model-name conditional scan |
| CON-006 | §16 | P0-T03, P1-T06, P3-T03, P6-T01 | offline tests |
| CON-007 | §6.4, §15 | P0-T03, P1-T06, P6-T01 | no-fallback tests |
| CON-008 | §6.1, §11.2 | P0-T02/T04~T05, P5-T03 | pinned manifest |
| CON-009 | §5.3, §7.4 | P0-T02, P1-T04~T05, P2-T03 | split-access tests |
| CON-010 | §5.2~§5.3 | P0-T02, P1-T04, P5-T01 | explicit split manifest |
| CON-011 | §6.2, §17.5 | P0-T04, P2-T01, P4-T05, P6-T03 | license/source audit |
| CON-012 | §1, §21 | P0-T01/T06, P6-T05 | conflict/release review |

### 4.4 Acceptance Criteria

| PRD ID | SPEC Section | PLAN Phase/Task | Verification |
|---|---|---|---|
| AC-001 | §8~§11 | P2-T03~T05, P4-T04 | model command matrix |
| AC-002 | §6.1~§6.2 | P2-T01, P4-T05, P6-T03 | source audit |
| AC-003 | §6.2, §19 | P6-T03 | runtime/import scan |
| AC-004 | §7 | P3-T05, P4-T01~T04 | gradient/aux/no-gradient matrix |
| AC-005 | §5.4~§6.7, §13 | P2-T02, P4-T01~T02, P5-T01 | resolved protocol inspection |
| AC-006 | §5 | P1-T04 | MVTec data tests |
| AC-007 | §4.4, §12 | P1-T05, P5-T04 | metric parity |
| AC-008 | §11.4, §17.4 | P5-T03~T04 | tolerance acceptance |
| AC-009 | §11.3 | P2-T05, P5-T01/T04 | protocol diagnosis |
| AC-010 | §14.5 | P1-T03, P2-T04, P3-T04, P4-T04 | new-process parity |
| AC-011 | §16 | P6-T01 | network-blocked matrix |
| AC-012 | §15 | P1-T06, P6-T01 | missing asset failures |
| AC-013 | §11.2, §13.4 | P0-T05, P5-T01, P6-T04 | artifact schema |
| AC-014 | §11.4 | P5-T03~T04 | repeated runs |
| AC-015 | §5.3, §7.4 | P1-T04, P2-T03, P5-T01 | leakage instrumentation |
| AC-016 | §3.2~§3.3, §6.3 | P3-T06, P4-T05 | integration change review |
| AC-017 | §3.2, §17.5 | P2-T06, P3-T05, P6-T03 | purity scan |
| AC-018 | §17.2 | P6-T02 | full regression |
| AC-019 | §17 | P4-T04, P6-T04 | evidence matrix |
| AC-020 | §11.5, §15.2 | P5-T02 | injected failure |

### 4.5 Current Gap Closure

| PRD ID | SPEC Section | PLAN Phase/Task | Verification |
|---|---|---|---|
| GAP-001 | §6.1~§6.3 | P0-T04, P2-T01, P4-T01~T02 | upstream source/diff |
| GAP-002 | §3.3, §7.3 | P3-T01/T05, P4-T02 | optimizer-none test |
| GAP-003 | §6.7 | P2-T02 | student-only optimizer test |
| GAP-004 | §5.4 | P4-T01 | EfficientAD input protocol |
| GAP-005 | §5.5, §7.2 | P3-T03, P4-T01 | auxiliary loader test |
| GAP-006 | §7.2~§7.4 | P3-T02/T05, P4-T02 | collect/finalize test |
| GAP-007 | §10, §12.3, §14 | P1-T03, P2-T04, P3-T04 | state round-trip |
| GAP-008 | §12.2 | P0-T02, P1-T05, P5-T04 | metric parity |
| GAP-009 | §5.2~§5.3, §21 | P0-T02, P1-T04 | approved split manifest |
| GAP-010 | §11 | P0-T05, P5-T01~T05 | equivalence artifacts |
| GAP-011 | §11.2, §13.4 | P0-T01/T03~T05, P6-T04 | provenance completeness |
| GAP-012 | §6.4, §19, §21 | P0-T03~T04, P6-T03 | dependency/asset decision |
| GAP-013 | §11.4, §17.4 | P0-T05, P5-T03~T04 | repeated baseline |

### 4.6 Out-of-Scope Guards

| PRD ID | PLAN Treatment |
|---|---|
| OOS-001 | anomalib Engine/CLI/callback 재구현 task 없음; P6-T03에서 runtime import 차단 |
| OOS-002 | 모델 정확도 개선 연구 task 없음; P5는 protocol equivalence만 진단 |
| OOS-003 | P2/P4 source diff gate로 대규모 rewrite 금지 |
| OOS-004 | legacy trainer/evaluator/factory 이식 task 없음 |
| OOS-005 | anomalib API/checkpoint compatibility task 없음 |
| OOS-006 | P3에서 heterogeneous lifecycle을 지원하고 단일 training step 강제 금지 |
| OOS-007 | D-003에서 승인한 초기 모델만 계획 |
| OOS-008 | MVTec만 초기 dataset task로 계획 |
| OOS-009 | 원격 tracking, registry, cloud orchestration task 없음 |
| OOS-010 | P5 tolerance는 numerical equivalence이며 bitwise 동일성 아님 |
| OOS-011 | P1/P6은 local asset preflight만 구현하며 download service 없음 |

## 5. SPEC Implementation Coverage

| SPEC Section | PLAN Phase/Task | Notes |
|---|---|---|
| §1 Purpose and Scope | P0-T01/T06, P6-T05 | hierarchy and scope gates |
| §2 Current Architecture Summary | P0-T01, P1-T02 | actual checkout reconciliation |
| §3 Target Architecture | P1-T01~T03, P2-T06, P3, P4-T03 | minimal extension and purity |
| §4 Anomaly Detection Task Contract | P1-T01/T05, P2-T02 | executable contract tests |
| §5 Dataset Integration | P0-T02~T03, P1-T04, P3-T03 | MVTec, splits, auxiliary data |
| §6 Model Integration | P0-T04, P2-T01~T02, P4-T01~T02 | upstream source and adapters |
| §7 Model Lifecycle Variations | P2, P3, P4 | staged lifecycle proof |
| §8 Training Flow | P2-T03, P3-T01~T03, P4 | gradient/aux/no-gradient |
| §9 Evaluation Flow | P1-T07, P2-T04, P4-T04 | checkpoint-only evaluation |
| §10 Prediction Flow | P1-T07, P2-T04, P4-T04 | calibrated outputs |
| §11 Benchmark/Reference Equivalence | P0-T04~T05, P2-T05, P5 | early and cross-model gates |
| §12 Metrics/Post-processing | P1-T03/T05, P5-T04 | ownership and parity |
| §13 Configuration | P0-T02~T03, P1-T02/T06, P5-T01 | validated resolved protocol |
| §14 Checkpoint/State | P1-T03, P2-T04, P3-T04, P4-T04 | new-process round-trip |
| §15 Errors | P1-T06, P5-T02, P6-T01 | fail-fast and isolation |
| §16 Offline | P0-T03, P1-T06, P6-T01/T03 | local assets only |
| §17 Testing | every phase; P6-T04 | layered evidence |
| §18 Legacy Migration | P2-T01, P4-T05, P6-T03 | evidence only, no framework port |
| §19 Dependencies | P0-T03~T04, P1-T05, P6-T03 | minimum approved dependencies |
| §20 PRD Traceability Matrix | §4 of this PLAN, P6-T04 | complete mapping |
| §21 Open Questions | §3, P0-T01~T06 | decisions tied to blocking phase |
| §22 Implementation Impact | P1~P6 Expected Code Impact | paths revalidated after D-001 |

## 6. Plan Self-Review

- BRIEF 범위 밖의 algorithm research, legacy framework, MLOps 또는 download service phase가 없다.
- 모든 FR/NFR/CON/AC/GAP ID가 최소 한 task와 verification에 연결되며 OOS는 별도 guard로 처리한다.
- 첫 모델 전 P1은 contract, dataset, metric, state와 asset validation으로 제한한다.
- STFPM vertical slice 후에만 auxiliary/no-gradient capability를 공통화한다.
- Model-specific workstream은 `src/core/*`와 common contract를 독자 수정할 수 없다.
- EfficientAD와 PatchCore는 stable contract 이후 `MODEL-WAVE-1`에서 병렬화한다.
- Per-model reference comparison은 P2/P4에서 수행하고 cross-model long gate는 P5에서 수행한다.
- Fast smoke와 long reference benchmark를 분리한다.
- Offline/local asset, checkpoint model-specific state, leakage 및 existing-task regression이 exit criteria에 포함된다.
- 각 Phase는 객관적인 artifact/test gate를 가지며 다음 Phase dependency가 명시된다.
