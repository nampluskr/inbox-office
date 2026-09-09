# task 프로젝트 공통 구조

## 목적

로컬의 독립된 task 프로젝트를 별도 package 설치 없이 공통 engine에 연결하기 위한 폴더와 로딩 규칙을 정의한다.

## 폴더 구조

```text
<task-name>/
├── task.toml
├── base.yaml
└── src/
    └── <task_package>/
        ├── __init__.py
        ├── registry.py
        ├── adapters/
        │   └── <model-name>.py
        ├── models/
        │   └── <model-name>.py
        ├── data/
        ├── losses/
        ├── metrics/
        ├── preprocessors/
        ├── postprocessors/
        ├── optimizers/
        └── schedulers/
```

task 루트에 고정된 `adapter.py` 진입점은 없다. 대신 model마다
`adapters/<model-name>.py`(engine 계약을 구현하는 Adapter 클래스)와
`models/<model-name>.py`(순수 `nn.Module`)가 각각 하나씩 있고,
`registry.py`가 이 둘을 연결한다. model 구현이 여러 파일로 나뉘어야 하는
경우(예: 전용 loss, augmenter가 필요한 model)에는 예외적으로
`models/<model-name>/`처럼 폴더로 둘 수 있다.

`registry.py`는 `data/`, `adapters/`와 같은 위치에 하나만 두고, 선택 가능한
항목이 2개 이상인 구성요소의 `*_REGISTRY` dict(예: `MODEL_REGISTRY`,
`DATA_REGISTRY`, `LOSS_REGISTRY`)를 전부 여기에 모은다. 구성요소별로
`registry.py`를 나누지 않는다 — task마다 registry 파일이 여러 개 흩어지지
않고 한 곳에서 "이 task가 선택 가능한 것이 무엇인지"를 확인할 수 있다.
`MODEL_REGISTRY`의 값은 `adapters/<model-name>.py`의 Adapter 클래스다.
`task.toml`의 `task.registry` 필드가 이 파일을 가리키고, task-runner의
source 로딩 절차가 job의 `params.model.name`으로 이 dict를 조회해 해당
Adapter 클래스를 바로 가져와 쓴다. 선택 항목이 하나뿐인 구성요소는
registry에 넣지 않고 그 모듈을 직접 사용한다.

`base.yaml`은 이 task의 모든 섹션(`data`/`preprocessor`/`model`/`loss`/
`optimizer`/`scheduler`/`metric`/`postprocessor`)에 대한 기본값을 담는다.
job 정의(`batch.json`)의 `params`는 이 기본값 위에 override할 값만 갖고,
adapter가 실행 시점에 `base.yaml` 위에 `params`를 덮어써 최종 설정을
만든다. model별로 별도 기본값 파일(예: `model.yaml`)은 두지 않는다 — task당
`base.yaml` 하나만 존재하므로, model을 바꾸는 job은 그 model이 필요로 하는
값을 `params`에서 전부 직접 지정해야 한다. 자세한 병합 순서는
`refs/batch-definition-mock.md`를 따른다.

`data`와 `models`는 task가 소유한다. `losses`, `metrics`, `preprocessors`,
`postprocessors`, `optimizers`와 `schedulers`는 task에 필요할 때 둔다. `data`는
dataset과 dataloader를 나누지 않고 하나로 묶는다 — task나 model에 따라 별도
dataloader 없이 배열을 그대로 쓰는 경우(예: 향후 NumPy, scikit-learn backend)가
있어, 둘을 항상 분리된 구성요소로 가정하지 않는다.

`preprocessors`(입력 변형)와 `postprocessors`(출력 변형)를 하나의
`transforms`로 합치지 않는 이유는, 둘이 적용되는 시점과 목적이 다르기
때문이다. 전처리는 `data`가 샘플을 만들 때 함께 적용되고, 후처리는 model의
forward 결과에 evaluate/predict에서 적용된다. 어떤 task가 실제로 이 둘을
쓸지, 어떻게 구성할지는 adapter가 정한다.

model은 공통 engine을 import하거나 전용 기반 클래스를 상속하지 않는 순수 backend model로 유지한다. `adapters/<model-name>.py`의 Adapter 클래스만 공통 계약을 구현하여 task와 engine을 연결한다.

## model이 여러 개인 task — task를 model 개수만큼 쪼개지 않는다

한 task 안에 model이 여러 개이고 각 model의 학습 절차(loss, optimizer,
augmentation 등)가 서로 크게 다른 경우에도, model 하나당 task 하나를
만들지 않는다. `models/<model-name>.py`(순수 forward)와
`adapters/<model-name>.py`(그 model 전용 `train_step`/`eval_step`/
`predict_step`/`configure_optimizer`를 구현하는 Adapter 클래스)로 나누고,
`registry.py`의 `MODEL_REGISTRY`가 model 이름과 그 Adapter 클래스를
연결한다.

`base.yaml` 병합, `resolved.json` 기록, checkpoint 경로 조합처럼 **model과
무관하게 모든 Adapter가 공유하는 로직**은 task-runner 저장소 자신이
`BaseAdapter`로 제공한다(`src/<task_runner_package>/adapter/base.py`).
각 `adapters/<model-name>.py`는 `BaseAdapter`를 상속하고, 그 model에서
실제로 달라지는 hook만 구현한다 — task 프로젝트가 task-runner를 package로
설치하지는 않지만, engine을 구동하는 프로세스 자신이 이미 task-runner를
갖고 있으므로 adapter 코드에서 `from task_runner.adapter.base import
BaseAdapter`처럼 바로 import할 수 있다. 이 import는 model에는 허용하지
않는 것과 달리 adapter에는 허용된다 — adapter 자체가 engine과 연결되는
자리이기 때문이다.

```python
# adapters/resnet_mock.py
from task_runner.adapter.base import BaseAdapter
from ..models.resnet_mock import ResnetMock

class ResnetMockAdapter(BaseAdapter):
    def prepare_train(self, context):
        params = self._resolve_params(context)
        self._model = ResnetMock(backbone=params["model"]["backbone"])
        ...
```

어떤 model의 Adapter를 쓸지는 이 클래스 내부가 아니라 **task-runner의
source 로딩 절차가 job의 `params.model.name`을 보고 미리 결정**한다 —
`registry.py`에서 해당 클래스를 조회해 바로 그 클래스를 사용하므로, Adapter
자신은 다른 model로 분기하는 코드를 갖지 않는다.

이 판단의 근거와 전체 예시 코드는 `refs/model-wrapper-pattern.md`,
`refs/base-adapter-sample.py`, `refs/adapter-sample.py`,
`refs/registry-sample.py`를 따른다.

## 경로 입력

CLI는 다음 option으로 task 프로젝트 root를 받는다.

```text
--task_dir <task-project-path>
```

## source 로딩

1. `--task_dir`을 절대 경로로 정규화한다.
2. root의 `task.toml`을 읽고 검증한다.
3. `<task_dir>/src`와 선언된 task package가 존재하는지 확인한다.
4. `<task_dir>/src`를 현재 job process의 import 경로에 추가한다.
5. `task.toml`에 선언된 `task.registry`를 import한다.
6. job(batch.json의 해당 job 항목)의 `params.model.name`으로 그 registry의
   `MODEL_REGISTRY`를 조회해 Adapter 클래스를 가져온다.
7. 그 Adapter 클래스가 공통 계약을 만족하는지 검사한 뒤 job을 실행한다.

adapter를 고정된 진입점 하나로 미리 import하지 않는다 — 어떤 model의
Adapter를 쓸지는 job마다 다를 수 있으므로, model이 정해진 뒤에야
import한다. 계약 검사(7단계)도 task 로딩 시점 1회가 아니라 **job마다** 그
model의 Adapter에 대해 수행한다.

task 프로젝트를 package 또는 editable mode로 설치하지 않는다. task와 backend가 요구하는 dependency는 실행 환경에 이미 준비되어 있어야 한다.

## task manifest

`task.toml`은 task 프로젝트를 공통 engine에 연결하는 최소 정보만 가진다.

```toml
schema_version = 1

[task]
type = "classification"
backend = "pytorch"
package = "classification_task"
registry = "classification_task.registry:MODEL_REGISTRY"
```

| field | 의미 |
| --- | --- |
| `schema_version` | manifest schema version |
| `task.type` | task 종류 |
| `task.backend` | adapter가 사용하는 실행 backend |
| `task.package` | `<task_dir>/src` 아래의 source package |
| `task.registry` | `module:object` 형식의 model registry import 경로 |

`task.toml`에는 dataset, model과 parameter 목록을 넣지 않는다. 선택 가능한 구성요소와 각 parameter 규격은 registry와 그 Adapter들이 제공한다. manifest는 source 연결만 담당하고 실행 가능한 catalog는 task가 소유한다.

하나의 task 프로젝트와 adapter는 정확히 하나의 backend에만 연결한다. 같은 종류의 task를 다른 backend로 구현할 때는 별도의 task 프로젝트로 분리하고 각 프로젝트가 자신의 manifest와 registry를 제공한다.

## optimizer와 scheduler

optimizer와 scheduler의 종류, 생성 방법과 설정은 task가 소유한다. 공통 backend engine은 특정 optimizer나 scheduler를 선택하거나 생성하지 않으며, 둘을 필수 구성요소로 가정하지 않는다.

```text
optimizer = None
scheduler = None
```

학습에 optimizer나 scheduler가 필요하면 adapter가 task 구현에서 준비한다. 학습이 없거나 다른 방식으로 parameter를 갱신하는 task는 `None`을 유지할 수 있다.

## data source 책임

data(dataset과 dataloader를 포함한 구체 data source)는 task가 생성하고 소유한다. 공통 engine은 PyTorch `DataLoader` 같은 구체 타입을 생성하거나 검사하지 않는다.

adapter는 실행 모드별 data source를 다음 공통 method로 제공한다.

```text
train_data(context) -> Iterable
validate_data(context) -> Iterable
evaluate_data(context) -> Iterable
predict_data(context) -> Iterable
```

v0.1 PyTorch task는 보통 각 method에서 task가 준비한 `DataLoader`를 반환한다. `validate_data`는 `valid` split을, `evaluate_data`는 `test` split을 반환한다. batch의 tuple, mapping, tensor와 가변 길이 목록 같은 내부 구조도 task 계약이며, engine은 이를 해석하거나 변환하지 않고 해당 step hook에 그대로 전달한다.

```text
source = adapter.train_data(context)

for batch in source:
    result = adapter.train_step(batch, context)
```

`iter_train_batches`처럼 순회 자체를 task hook으로 감싸지 않는다. task는 data source를 제공하고 engine은 공통 lifecycle에 따라 그 data source를 순회한다. 이를 통해 epoch, step, 중단과 공통 hook 호출 순서는 engine이 일관되게 관리하면서도 data 구성은 task에 남길 수 있다.

이 iterable 계약은 우선 batch 실행이 가능한 v0.1 PyTorch backend에 적용한다. 향후 전체 dataset에 대해 한 번의 `fit`을 수행하는 backend는 억지로 batch iterable을 구현하게 하지 않고, 해당 backend가 제공하는 실행 capability를 별도로 정의한다.

### validate와 evaluate

`validate`와 `evaluate`는 같은 평가 loop와 `eval_step` 계약을 사용한다. 둘의 차이는 data split과 실행 목적뿐이다.

| 구분 | data source | 목적 |
| --- | --- | --- |
| `validate` | `validate_data`가 제공하는 `valid` split | 학습 중 상태 확인과 model 선택 |
| `evaluate` | `evaluate_data`가 제공하는 `test` split | 학습 완료 model의 최종 성능 평가 |

학습 lifecycle은 각 epoch 뒤에 필요할 때 `validate_data`를 순회하며 `eval_step`을 실행한다. 독립된 `evaluate` 명령은 `prepare_evaluate` 이후 `evaluate_data`를 순회하며 같은 `eval_step`을 실행한다. 공통 engine은 두 경우 모두 동일한 평가 loop를 사용하고 context의 stage만 `validate` 또는 `evaluate`로 구분한다.

`test` split은 학습 중 validation, checkpoint 선택, early stopping과 scheduler 판단에 사용하지 않는다. `valid` split 결과와 `test` split 결과도 서로 다른 stage 결과로 기록한다.

### metrics

metrics의 종류, 생성, 상태와 계산 방법은 adapter가 정의하고 소유한다. metrics는 `validate`와 `evaluate`에서 사용하며 공통 engine이나 backend engine이 metric 객체를 생성하거나 metric별 입력 형식을 해석하지 않는다.

두 실행은 다음과 같은 동일한 metric lifecycle을 따른다.

```text
adapter.reset_metrics(context)

for batch in data_source:
    step_result = adapter.eval_step(batch, context)
    adapter.update_metrics(step_result, context)

metrics = adapter.compute_metrics(context)
```

engine은 이 hook들을 정해진 순서로 호출하고 최종 결과를 기록한다. 각 hook의 실제 구현, metric state와 `eval_step` 결과를 metric 입력으로 바꾸는 방법은 adapter가 담당한다.

validation을 시작할 때와 evaluation을 시작할 때 metric state를 각각 reset한다. 따라서 `valid` 결과가 뒤의 `test` 결과에 누적되거나 서로 섞이지 않는다. 학습 중 loss와 진행 log는 step 실행 결과이며 이 평가 metrics 계약과 구분한다. predict에서는 이 metrics lifecycle을 사용하지 않는다.

### 실행 준비와 parameter 갱신

각 실행 모드의 준비는 `prepare_train`, `prepare_evaluate`, `prepare_predict` hook에서 시작한다. 공통 engine은 선택된 실행 모드에 해당하는 준비 hook을 호출할 뿐이며, model, data source, checkpoint와 task state를 어떤 방식으로 준비할지는 task adapter가 정한다.

학습에 optimizer가 필요한 task는 자신의 `prepare_train` 구현에서 `configure_optimizer`를 호출한다. `configure_optimizer`라는 분리 방식은 Lightning의 학습 구성 방식을 참조하지만, 반환 객체를 공통 engine에 넘겨 engine이 갱신을 수행하는 구조는 사용하지 않는다.

```text
common engine
    -> adapter.prepare_train(context)
        -> task.configure_optimizer()
        -> task가 optimizer와 scheduler를 자신의 state에 보관

common engine
    -> adapter.train_data(context)
    -> 반환된 data source를 반복
        -> adapter.train_step(batch, context)
            -> task가 forward와 loss 계산
            -> task가 backward와 parameter update 수행
            -> task가 step 결과만 반환

    -> epoch 뒤 validation이 필요한 경우
        -> adapter.reset_metrics(context)
        -> adapter.validate_data(context)
        -> 반환된 valid data source를 반복
            -> adapter.eval_step(batch, context)
            -> adapter.update_metrics(step_result, context)
        -> adapter.compute_metrics(context)
```

evaluate와 predict도 같은 경계를 따른다.

```text
common engine
    -> adapter.prepare_evaluate(context)
    -> adapter.reset_metrics(context)
    -> adapter.evaluate_data(context)
    -> 반환된 test data source를 반복
        -> adapter.eval_step(batch, context)
        -> adapter.update_metrics(step_result, context)
    -> adapter.compute_metrics(context)

common engine
    -> adapter.prepare_predict(context)
    -> adapter.predict_data(context)
    -> 반환된 data source를 반복하며 adapter.predict_step(batch, context)
```

`prepare_evaluate`와 `prepare_predict`는 optimizer 구성을 전제로 하지 않는다. checkpoint 로딩, 평가 또는 예측용 dataloader 준비, threshold나 후처리 상태 복원처럼 해당 실행 모드에 필요한 동작을 task가 구현한다.

`configure_optimizer`의 기본 결과는 다음과 같다.

```text
optimizer = None
scheduler = None
```

task가 optimizer나 scheduler를 사용하면 task 내부 state에 저장한다. 공통 engine은 이 객체를 인자로 받거나 읽거나 호출하지 않는다. 따라서 `zero_grad`, `backward`, `optimizer.step`과 `scheduler.step`의 실행 시점도 task가 정한다.

예를 들어 일반적인 PyTorch classification task는 `train_step`마다 `zero_grad`, forward, loss, backward와 `optimizer.step`을 수행할 수 있다. GAN task는 같은 hook 안에서 generator와 discriminator optimizer를 서로 다른 횟수로 실행할 수 있다. optimizer가 없는 통계 기반 또는 추론 전용 task는 기본값 `None`을 그대로 유지한다.

## hook 책임

공통 engine은 lifecycle과 hook 호출 순서만 소유한다. 개별 hook의 구현은 task adapter가 소유한다.

| 구분 | 공통 engine | task adapter |
| --- | --- | --- |
| lifecycle | train, evaluate, predict loop와 hook 호출 순서를 진행 | 호출된 hook의 실제 동작을 구현 |
| 학습 준비 | `prepare_train` 호출 | model, 학습 data source와 task state를 준비하고 필요하면 `configure_optimizer` 호출 |
| 평가 준비 | `prepare_evaluate` 호출 | checkpoint, test data source와 평가용 task state 준비 |
| 예측 준비 | `prepare_predict` 호출 | checkpoint, 예측 data source와 후처리용 task state 준비 |
| data 접근 | 실행 모드에 맞는 `*_data` 호출 후 반환된 iterable 순회 | 구체 data source를 생성하고 반환 |
| batch 학습 | `train_step` 호출 | forward, loss, backward와 parameter update 수행 |
| validation | `valid` split에서 `eval_step` 호출 | task별 validation 계산과 step 결과 생성 |
| evaluate | `test` split에서 `eval_step` 호출 | task별 최종 평가 계산과 step 결과 생성 |
| metrics | validation/evaluation에서 metric lifecycle hook을 순서대로 호출 | metric 정의, 상태 초기화, 갱신과 최종 계산 |
| 예측 | `predict_step` 호출 | task별 추론과 후처리 결과 생성 |
| optimizer/scheduler | 객체를 생성, 보관, 검사 또는 호출하지 않음 | 생성, 보관, 호출과 checkpoint state 정의 |

engine이 제공하는 것은 hook을 실행할 공통 시점이지 hook의 공통 구현이 아니다. 특정 task에만 필요한 hook도 adapter 내부에서 정의한다. engine의 lifecycle에 없는 task 전용 동작은 이미 호출된 공통 hook 안에서 task가 조합한다.

## job parameter 전달

job 정의(`batch.json`)의 `params`는 `data`/`preprocessor`/`model`/`loss`/
`optimizer`/`scheduler`/`metric`/`postprocessor` 섹션으로 나누는 관례를
쓰되, 이 구조는 engine의 계약이 아니라 mock adapter들 사이의 관례다. engine은 `context.params`에 통째로 담아
모든 hook에 그대로 넘길 뿐 내부 key를 해석하거나 검증하지 않는다. 자세한
스키마와 sweep 표현 방식은 `refs/batch-definition-mock.md`를 따른다.

`epochs`(epoch loop 횟수)와 `validate`(epoch 뒤 validation 수행 여부)는
`params`가 아니라 job 정의의 고정 값이며, adapter가 아니라 **공통 engine이
소유**한다. engine이 이 값을 읽어 학습 loop 반복 횟수와 validation 호출
시점을 직접 제어한다.

checkpoint 저장·로드 경로는 여전히 adapter가 정하지만, 여러 variant가 같은
`task_dir`을 학습하는 경우(조건 비교 실행)에는 `params._variant`로 경로를
분리해야 서로 덮어쓰지 않는다.

## v0.1 검증 fixture

```text
tasks/
├── classification/
├── segmentation/
├── detection/
└── anomaly_detection/
```

각 폴더는 위 공통 구조를 따르는 독립 task 프로젝트를 mock으로 재현한다. mock의 목적은 알고리즘 성능이 아니라 폴더 규칙, source 로딩, adapter 계약과 공통 PyTorch engine 연결을 검증하는 것이다.
