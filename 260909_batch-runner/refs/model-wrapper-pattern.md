# model마다 다른 학습 절차를 하나의 task 안에서 수용하는 방법

## 문제

`_clones/defectvad`(anomaly detection 20개 model 보유)처럼, 하나의 task
안에 여러 model이 있고 각 model의 학습 절차(loss, optimizer, augmentation,
학습 필요 여부)가 서로 크게 다른 경우가 있다. 예를 들어 `padim`은
optimizer와 loss가 없고 `training_step`이 forward만 한 뒤 `on_train_end`에서
통계적 `fit()`을 한 번 수행하지만, `draem`은 전용 `DraemLoss`,
`PerlinAnomalyGenerator`(augmentation), 선택적 `sspcab` 분기까지 있는
완전히 다른 절차를 쓴다.

이런 다양성 때문에 model 하나당 task 하나(`tasks/anomaly_detection_padim`,
`tasks/anomaly_detection_draem`, ...)로 쪼개야 하는 것처럼 보일 수 있지만,
그럴 필요가 없다.

## 근거 1 — task 분리는 backend 기준이지 model 기준이 아니다

`planning-origin.md`가 정한 task 분리 기준은 backend뿐이다. "같은 task를
다른 backend로 구현할 때는 별도의 task 프로젝트로 분리한다." model이
다르다는 이유로 task를 분리하는 규칙은 없다. 오히려 "사용자가 선택할 수
있는 구성요소"(model, backbone 등)라는 개념 자체가 하나의 task 안에 여러
model이 공존하는 것을 전제로 한다.

## 근거 2 — `roi-corner-detection-ver3`가 이미 같은 문제를 풀어봤다

`_clones/defectvad-refactoring/docs/dev/v0.1/comparison/03_MODEL_AND_ADAPTER.md`는
`defectvad`, `roi-corner-detection-ver3`, `cv_boilerplate` 세 저장소의
model/adapter 경계를 비교한 문서다. 이 중 `roi-corner-detection-ver3`의
구조가 지금 문제와 정확히 같은 모양이다.

```text
BaseWrapper (model, preprocessor, postprocessor, optimizer, scheduler, losses, metrics 소유)
├── DetWrapper       (model-specific pre/postprocessor, 기본 metric)
├── DetrWrapper
├── GCNWrapper
└── HybridWrapper

get_wrapper(model_option)  <- 사용자가 넘긴 model 이름으로 wrapper를 명시적으로 고르는 factory
```

`train_step()`은 forward, loss 계산, backward와 optimizer step을 wrapper가
전부 수행하고, `predict_step()`은 raw output을 자기 postprocessor에 넘겨
최종 결과로 바꾼다. model(`nn.Module`, forward만)과 wrapper(train_step 등)가
분리된 두 개의 파일이라는 점이 핵심이다.

## 결론 — model마다 별도 Adapter, registry가 연결한다

`roi-corner-detection-ver3`의 `BaseWrapper`/`get_wrapper()`가 하던 역할을
task-runner에서는 **model마다 독립된 Adapter 클래스 + `registry.py`**로
그대로 옮긴다. 다만 "위임만 하는 thin adapter 1개 + 실제 구현 wrapper
여러 개"라는 두 계층을 두지 않고, **model마다 하나씩 있는 Adapter
클래스가 곧 실제 구현**이다.

```text
adapters/padim.py    -> PadimAdapter(BaseAdapter)   # loss_fn 없음, optimizer 없음
adapters/draem.py    -> DraemAdapter(BaseAdapter)   # DraemLoss, augmenter, sspcab 분기
```

engine이 호출하는 고정된 hook 이름(`prepare_train`, `train_data`,
`train_step`, `prepare_evaluate`, `eval_step`, `prepare_predict`,
`predict_step`, `reset_metrics`, `update_metrics`, `compute_metrics`)을
`PadimAdapter`와 `DraemAdapter`가 각자 실제로 구현한다. `configure_optimizer`
호출도 각 클래스의 `prepare_train` 안에서 그 model에 맞는 대로(또는 `None`으로)
직접 수행한다 — 위임할 대상이 없으므로 위임 코드 자체가 없다.

**어떤 model의 Adapter를 쓸지는 Adapter 클래스 내부가 아니라 task-runner의
source 로딩 절차가 결정한다.** job의 `params.model.name`으로 `registry.py`의
`MODEL_REGISTRY`를 조회해 해당 클래스를 바로 가져와 인스턴스화하므로, 각
Adapter는 자신이 어떤 model인지 이미 알고 있고 다른 model로 분기하는 코드를
가질 필요가 없다.

```text
registry.py
    MODEL_REGISTRY = {"padim": PadimAdapter, "draem": DraemAdapter, ...}

source 로딩
    model_name = job.params.model.name
    AdapterClass = MODEL_REGISTRY[model_name]
    adapter = AdapterClass(task_dir)
```

이미 정한 원칙("실제 backward와 parameter update는 task의 train_step이
수행한다", "공통 engine은 optimizer, scheduler 객체를 생성·검사하지
않는다")은 그대로 유지된다 — engine은 여전히 어떤 Adapter가 선택됐는지,
그 안에서 optimizer가 있는지 없는지 전혀 모른다.

## 필요한 것

- `models/<model-name>.py` — 순수 `nn.Module`, forward만.
- `adapters/<model-name>.py` — 그 model 전용 `train_step`/`eval_step`/
  `predict_step`/`configure_optimizer`/loss를 구현하는 Adapter 클래스.
  `base.yaml` 병합, `resolved.json` 기록, checkpoint 경로 조합처럼 model과
  무관한 공통 로직은 task-runner가 제공하는 `BaseAdapter`를 상속해 재사용한다.
- `registry.py`의 `MODEL_REGISTRY` — `{"padim": PadimAdapter, "draem": DraemAdapter, ...}`
  매핑 하나.

model을 추가할 때는 `models/<new_model>.py`와 `adapters/<new_model>.py`를
추가하고 `MODEL_REGISTRY`에 한 줄만 등록하면 된다. `defectvad`에 model이
20개 있어도 task는 여전히 하나고, `task.toml`도 바뀌지 않는다.

## 예시 코드

공통 로직(`BaseAdapter`)은 `refs/base-adapter-sample.py`, model별 Adapter
예시는 `refs/adapter-sample.py`, registry 예시는 `refs/registry-sample.py`를
따른다.

## 주의 — `cv_boilerplate`의 권고와는 다른 방향

`03_MODEL_AND_ADAPTER.md`의 `cv_boilerplate` 권고 표는 "optimizer, AMP,
clipping, resume → 공통 Trainer"로 두라고 되어 있는데, 이는 task-runner가
택한 방향과 반대다. task-runner는 (`library-execution-patterns.md`에서
이미 명시했듯) 이 부분을 의도적으로 model별 Adapter 쪽에 남기는 manual
optimization 방식을 쓴다 — backend 중립성(PyTorch가 아닌 backend도
지원)을 위해서다. `cv_boilerplate`의 권고를 그대로 계승하지 않는다.
