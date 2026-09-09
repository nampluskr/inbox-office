# batch 정의 모사 — UI/대시보드 부재 시점의 생성·실행 경로

## 목적

UI/대시보드는 이 프로젝트 범위 밖이다. 대시보드 표가 할 일을 파일과 스크립트로
대신하여 `batch.json` 생성과 실행을 검증한다.

## 계층

```text
sweep-spec (비교하고 싶은 조건만 간결하게 표현)
        │  전개(expand) 스크립트
        ▼
batch.csv (완전히 펼쳐진 concrete 행 — 대시보드 표 모사)
        │  csv -> json 변환 스크립트
        ▼
batch.json (SSOT, batch/job 실행 계약)
        │  batch runner (run)
        ▼
adapter가 task_dir/base.yaml과 job의 params를 병합
        ▼
jobs/<job-id>/{job.log, resolved.json, artifacts/}
```

`batch.csv`와 `batch.json`은 각 행이 하나의 job(하나의 독립된 CLI 명령)이라는 원칙을
그대로 따른다. sweep-spec은 이 원칙을 깨지 않고, 여러 행을 손으로 다시 쓰지 않게
해주는 authoring 단계일 뿐이다. engine과 adapter는 sweep이라는 개념을 모른다.

`batch.csv`를 `batch.json`으로 바로 흡수하지 않고 별도 파일로 유지하는 이유는,
sweep-spec이 전개한 job 목록을 실행 전에 사람이 표로 눈으로 확인할 수 있는
중간 산물이 필요하기 때문이다. 나중에 실제 UI가 붙을 때도 UI가 다루는 자료구조는
결국 이 flat table 형태이므로, `batch.csv`가 그 형태를 미리 검증해 두는 역할을
한다.

## `batch.csv` 열 구성

| 열 | 종류 | 의미 |
| --- | --- | --- |
| `job_id` | 고정 | job 식별자, 실행 순서 = 행 순서 |
| `mode` | 고정 | `train` / `evaluate` / `predict` |
| `task_dir` | 고정 | task 프로젝트 경로 |
| `epochs` | 고정, engine 소유 | train에서만 의미. 공통 engine의 epoch loop 횟수 |
| `validate` | 고정(bool), engine 소유 | train 중 epoch마다 validation 수행 여부 |
| `early_stop` | 고정(dict), engine 소유 | `{enabled, patience, monitor, mode}` — epoch loop를 조기 종료할지 |
| `params` | 자유(JSON 문자열), adapter 소유 | data/preprocessor/model/loss/trainer/metric/postprocessor 세부값 |

`output_dir` 열은 두지 않는다. job 산출물은 항상 `jobs/<job-id>/artifacts/`에
격리되는 고정 경로를 쓴다.

`epochs`, `validate`, `early_stop`은 공통 engine이 epoch loop 횟수, validation
호출 여부와 조기 종료를 직접 제어하는 데 쓰는 값이다. 이들은 adapter가 아니라
**engine이 소유한다** — "공통 engine은 optimizer, scheduler, data 객체를
생성·검사하지 않는다"는 원칙과 별개로, epoch 진행과 그 종료 조건은 engine의
lifecycle 제어에 속하기 때문이다.

`early_stop`은 다음 형태의 dict다.

```json
{"enabled": true, "patience": 3, "monitor": "accuracy", "mode": "max"}
```

`enabled`가 없거나 `false`면 engine은 `epochs` 횟수만큼 그대로 돈다.
`enabled`가 `true`면 engine은 매 validation 후 `adapter.compute_metrics(context)`가
돌려주는 dict에서 `monitor`로 지정한 key 하나만 꺼내, `mode`(`max`/`min`) 방향으로
이전 최고값과 비교한다. `patience` 라운드 동안 개선이 없으면 학습 loop를
멈춘다. engine은 그 key가 의미하는 metric의 내용을 해석하지 않고, 이름으로
값 하나를 조회해 숫자 비교만 한다. `monitor`로 지정한 key가
`compute_metrics` 반환값에 없으면 job은 실행 시점에 실패로 기록된다.

## `params`의 내부 구조 — engine은 해석하지 않는다

`params`는 섹션으로 나누는 관례를 쓰지만, 이 구조는 **engine의 계약이 아니라
mock adapter들 사이의 관례**다. engine은 `context.params`에 통째로 담아
모든 hook에 그대로 넘길 뿐 내부 key를 읽거나 검증하지 않는다. "공통 engine은
반환된 data source를 iterable로만 순회하고 batch 내부 구조를 해석하지
않는다"는 원칙을 params에도 동일하게 적용한 것이다.

```json
{
  "data": {"name": "mock_cls_dataset", "batch_size": 32},
  "preprocessor": {"resize": 224, "normalize": true},
  "model": {"name": "resnet_mock", "backbone": "resnet18"},
  "loss": {"name": "cross_entropy"},
  "optimizer": {"name": "adam", "lr": 0.001, "weight_decay": 0.0001, "amp": true, "grad_clip_norm": 1.0},
  "scheduler": {"name": "cosine"},
  "metric": {"names": ["accuracy"]},
  "postprocessor": {"threshold": 0.5}
}
```

섹션은 mode 이름이 아니라 **ML pipeline 단계** 기준으로 나눈다.

| 섹션 | 의미 |
| --- | --- |
| `data` | dataset과 dataloader(나누지 않고 하나로 묶음) |
| `preprocessor` | 입력 변형 — augmentation, normalize 등 |
| `model` | model과 backbone |
| `loss` | loss 종류·설정 |
| `optimizer` | optimizer 종류·lr·weight decay·amp·gradient clipping |
| `scheduler` | learning rate scheduler 종류·설정 |
| `metric` | 평가 지표 |
| `postprocessor` | 출력 변형 — threshold, NMS, decode 등 |

`data`는 dataset과 dataloader를 나누지 않고 하나로 묶는다 — task나 model에
따라 별도 dataloader 없이 배열을 그대로 쓰는 경우가 있어, 둘을 항상 분리된
구성요소로 가정하지 않는다. `preprocessor`/`postprocessor`도 하나의
`transforms`로 합치지 않는다 — 전처리는 `data`가 샘플을 만들 때 적용되고
후처리는 model 결과에 적용되어 시점과 목적이 다르다. `amp`와
`grad_clip_norm`은 실제 update step을 수행하는 `optimizer` 섹션에 둔다 —
둘 다 optimizer 자신의 folder는 아니지만, `optimizer.step()` 호출 앞뒤의
학습 loop 실행 방식에 속하는 값이라 다른 자리가 없다.

어떤 mode가 어느 섹션을 실제로 읽는지는 adapter가 정하지만, 보통 train은
`data`/`preprocessor`/`model`/`loss`/`optimizer`/`scheduler`를, evaluate는
`data`/`preprocessor`/`model`/`metric`(필요하면 `postprocessor`)를,
predict는 `data`/`preprocessor`/`model`/`postprocessor`를 사용한다.

`params`의 유효성(그 task/model에 실제로 존재하는 조합인지)은 csv->json
변환 스크립트가 검사하지 않는다. job 실행 시 adapter가
`prepare_train`/`prepare_evaluate`/`prepare_predict`에서 검사한다.

## `task_dir/base.yaml` — task 전체 기본값

`params`에 매번 모든 섹션을 다 채우면 sweep-spec이 장황해지고, task마다
반복되는 기본값이 여러 곳에 흩어진다. 대신 task 프로젝트 루트에
`base.yaml` 하나를 두고, 그 task의 모든 섹션(`data`/`preprocessor`/`model`/
`loss`/`optimizer`/`scheduler`/`metric`/`postprocessor`)에 대한 기본값을
전부 담는다.

```text
<task-name>/
├── task.toml
├── base.yaml        <- 이 task의 전체 기본값 (신규)
└── src/<task_package>/...
```

병합은 **2단계**로 이뤄진다.

```text
task_dir/base.yaml (task 전체 기본값)
        │  adapter가 병합
        ▼
context.params (batch.json에서 온 값 — sweep-spec에서 비교하고 싶은 값만)
```

adapter는 `prepare_train`/`prepare_evaluate`/`prepare_predict`에서
`task_dir/base.yaml`을 읽고, 그 위에 `context.params`(job마다 다른 override)를
deep merge해 최종 설정을 만든다. engine은 이 병합을 모른다 — `context.params`를
그대로 넘길 뿐이고, `base.yaml`을 읽고 병합하는 것은 adapter의 책임이다.

이 병합의 결과(실제로 사용된 최종 설정)를 `jobs/<job-id>/resolved.json`에
기록한다. 즉 `resolved.json`은 `batch.json`의 `params`를 그대로 복사한 것이
아니라, **`base.yaml`로 기본값을 채운 뒤의 최종본**이다.

model마다 다른 기본값(예: model을 바꾸면 필요한 입력 해상도도 달라지는 경우)을
위한 별도 `model.yaml` 같은 파일은 두지 않는다 — task당 `base.yaml` 하나만
존재한다. 따라서 sweep-spec에서 model을 바꾸는 variant는 그 model이 실제로
필요로 하는 값을 전부 직접 override해야 한다. `base.yaml`은 하나의 기본
model 기준으로만 값을 채워 두기 때문이다.

## sweep-spec (조건 비교) — 방식 B: 명시적 변형 목록

전체 조합(격자) 생성 대신, 비교하고 싶은 조건만 이름 붙여 나열하고 `base` 대비
바뀐 값만 적는다. 하나의 batch(대시보드 테이블 하나)에 여러 task가 섞여 있을
수 있으므로, sweep-spec 파일은 **`base`+`variants` 블록의 목록**이다. 블록
하나가 task 하나(하나의 `task_dir`)에 대응한다.

```yaml
- base:
    task_dir: tasks/classification
    epochs: 10
    validate: true
    early_stop: {enabled: true, patience: 3, monitor: accuracy, mode: max}
    seed: 42
  variants:
    - name: bs32
      mode: [train, evaluate, predict]
    - name: bs16
      mode: [train, evaluate]
      params.data.batch_size: 16
    - name: bs64_resnet34
      mode: [train]
      params.data.batch_size: 64
      params.model.backbone: resnet34

- base:
    task_dir: tasks/segmentation
    epochs: 10
    validate: true
    seed: 42
  variants:
    - name: bs32
      mode: [evaluate]
```

`base.params`가 아예 없는 것을 볼 수 있다 — 이 batch의 두 task 모두
`task_dir/base.yaml`의 기본값을 그대로 쓰고, `variants`의 override만으로
충분하기 때문이다. `base.params`는 이번 batch 전체에 걸쳐 `base.yaml`을
덮어써야 할 값이 있을 때만 추가한다.

전개 규칙:

1. 파일은 `base`+`variants` 블록의 목록이며, 블록마다 독립적으로 아래 규칙을
   적용한다.
2. **`variants` 목록에 있는 것만 job으로 전개된다.** `base`는 각 variant가
   상속하는 기본값 틀일 뿐, 목록에 없으면 그 자체로는 실행되지 않는다.
3. `base`를 그대로 실행하고 싶으면 override 없는 variant 항목(예: `name: bs32`,
   덮어쓸 값 없음)을 명시적으로 추가한다. "`variants`가 없으면 `base`가 자동
   실행된다"는 암묵적 규칙은 쓰지 않는다 — `variants` 목록만 보고 몇 개 조건이
   도는지 항상 알 수 있어야 한다.
4. 각 `variant`는 속한 블록의 `base`를 복사한 뒤 dotted key로 지정된 값만
   덮어써 job 원형 하나를 만든다.
5. **각 variant는 `mode` 목록을 명시적으로 갖는다.** `train`/`evaluate`/
   `predict` 중 그 목록에 있는 mode에 대해서만 job이 만들어진다. "variant
   하나당 항상 3개 job이 생긴다"는 규칙은 쓰지 않는다 — `train`만 있는
   variant, `evaluate`만 있는 variant(예: 이미 학습된 checkpoint를 다른
   조건으로 다시 평가), `train`+`predict`만 있는 variant가 모두 가능하다.
   `mode`는 기본값 없이 항상 명시한다.
6. `job_id`는 `job-<task 이름>-<variant명>-<mode>` 형식으로 만든다. `<task 이름>`은
   `task_dir`의 마지막 경로 요소다. variant 이름은 블록(=task)마다 독립적으로
   재사용될 수 있으므로(예: 여러 task가 각각 `bs32`를 가짐), task 이름을 넣지
   않으면 서로 다른 task의 job_id가 충돌한다.
7. variant 이름은 `params._variant`에 함께 실어 adapter가 참조할 수 있게 한다.
   `evaluate`/`predict`만 있는 variant는 이 batch 안에 자신의 `train` job이
   없을 수 있다 — 그 경우 참조하는 checkpoint는 이 batch 이전에 이미
   `task_dir/.state/<variant명>/checkpoint.json`에 존재한다고 가정한다.

## checkpoint 경로와 variant

checkpoint 저장·로드는 batch/job 계층이 모르는 adapter 내부 관례다
(`task-project-layout.md` 참조). 다만 동일한 `task_dir`에 대해 서로 다른
variant가 각각 학습되면, variant를 구분하지 않는 고정 경로는 서로 덮어쓴다.

```text
tasks/classification/.state/bs16/checkpoint.json
tasks/classification/.state/bs64_resnet34/checkpoint.json
```

따라서 mock adapter는 checkpoint 경로를 `task_dir` 고정 경로가 아니라
`task_dir/.state/<params._variant>/checkpoint.json`처럼 variant로 분리된
경로에 저장·로드해야 한다. variant를 지정하지 않는 job(sweep을 쓰지 않는
단일 실행)은 `_variant`가 없으므로 `task_dir/.state/checkpoint.json` 같은
기본 경로를 그대로 쓸 수 있다.

## 아직 정하지 않은 것

- csv->json, sweep-spec->csv 변환 스크립트의 정확한 CLI 형식과 위치.
- `params` 유효성 검사 실패 시 job의 실행 전/후 상태 기록 방식.
- `task_dir/base.yaml`이 없는 task를 만났을 때의 처리(필수인지, 없으면
  빈 기본값으로 취급하는지).
