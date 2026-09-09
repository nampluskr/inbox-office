# 기획 출발점

## 참조 대상

- `D:\projects\_ideas\cv-batch-runner`: 이전 CV batch runner 기획. 변경하지 않고 참고한다.
- `D:\projects\_clones\cv_boilerplate`: 공통 engine과 task adapter 구조의 주요 코드 참조.

## 현재까지 사용자가 확정한 방향

- 이 프로젝트는 task별 구현을 저장소 안에 포함하지 않는 공통 실행 framework다.
- task 프로젝트는 자신의 data(dataset과 dataloader를 포함)와 model을 소유한다.
- model은 특정 실행 framework에 결합되지 않은 순수 backend model이어야 한다.
- adapter가 외부 task 구현과 공통 engine을 연결한다.
- 공통 engine은 train, evaluate와 predict lifecycle을 제공한다.
- batch runner는 독립된 CLI job을 순서대로 실행한다.
- backend는 PyTorch, JAX, NumPy, CuPy와 scikit-learn으로 확장할 수 있어야 한다.
- AI agent는 runtime의 실행과 상태 판단에 관여하지 않는다.
- 최초 구현과 검증 대상 backend는 `cv_boilerplate`를 기반으로 한 PyTorch로 한정한다.
- v0.1에서는 task 폴더 구조와 공통 engine 연결 interface를 검증하기 위해 task 구현을 mock으로 정의한다.
- v0.1 mock task는 `classification`, `segmentation`, `detection`, `anomaly_detection`으로 한정한다.
- mock task는 실제 알고리즘 성능이 아니라 공통 구조와 interface 연결을 검증한다.
- 실제 사용에서는 각 task가 로컬의 독립된 `<task-name>` 프로젝트 디렉터리에 존재한다고 가정한다.
- 공통 engine은 사용자가 지정한 `<task-name>` 디렉터리 경로를 통해 task 프로젝트를 연결한다.
- v0.1에서는 이 경계를 검증하기 위해 `tasks/<task-name>` 아래에 정해진 공통 규칙을 따르는 mock task 프로젝트를 둔다.
- `tasks/<task-name>`의 mock은 제품에 내장된 task catalog가 아니라 외부 task 연결을 검증하는 fixture다.
- 현재 프로젝트명은 프로젝트 외부 식별에만 사용하고 내부 폴더, 파일, 설정 key, package, module, class와 함수 이름에는 사용하지 않는다.
- 내부 식별자는 프로젝트명이 바뀌어도 유지할 수 있는 중립적인 이름을 사용한다.
- CLI는 `--task_dir <task-project-path>`로 로컬 task 프로젝트 경로를 받는다.
- task 프로젝트를 package 또는 editable mode로 별도 설치하지 않는다.
- 공통 engine은 `--task_dir` 아래의 정해진 폴더 구조와 adapter 진입 규칙을 사용해 소스를 직접 불러온다.
- task 프로젝트는 root의 `task.toml`과 `src/<task_package>/` 구조를 따른다.
- `task.toml`은 source package와 adapter import 경로를 선언한다.
- 실행 process는 `<task_dir>/src`를 해당 process의 import 경로에 추가한 뒤 adapter를 불러온다.
- `task.toml`에는 schema version, task 종류, backend, source package와 adapter import 경로만 기록한다.
- dataset, model과 parameter catalog는 `task.toml`에 나열하지 않고 adapter가 제공한다.
- 하나의 task 프로젝트와 adapter는 정확히 하나의 backend에만 연결한다.
- 같은 task를 다른 backend로 구현할 때는 별도의 task 프로젝트로 분리한다.
- optimizer와 scheduler는 task가 정하며 공통 backend engine은 종류, 생성 방법과 설정을 알지 않는다.
- backend engine에서 optimizer와 scheduler의 기본값은 각각 `None`이다.
- 학습 준비는 공통 engine이 `prepare_train` hook을 호출하면서 시작한다.
- 평가는 `prepare_evaluate`, 예측은 `prepare_predict` hook을 호출하면서 시작한다.
- 각 준비 hook에서 model, data source, checkpoint와 task state를 어떻게 준비할지는 task adapter가 정한다.
- optimizer가 필요한 task는 자신의 `prepare_train` 구현에서 `configure_optimizer`를 호출하고, 생성한 optimizer와 scheduler를 task 내부 state에 보관한다.
- 실제 backward와 parameter update는 task의 `train_step`이 수행한다.
- 공통 engine은 optimizer와 scheduler 객체를 받거나 읽거나 호출하지 않는다.
- 공통 engine은 lifecycle에 따른 공통 hook의 호출 시점과 순서만 정의하고 실행한다.
- 각 hook의 실제 구현과 task 전용 hook 조합은 task adapter가 소유한다.
- data(dataset과 dataloader를 포함한 구체 data source)는 task가 생성하고 소유한다.
- adapter는 `train_data`, `validate_data`, `evaluate_data`, `predict_data`를 통해 실행 모드별 data source를 제공한다.
- 공통 engine은 반환된 data source를 iterable로만 순회하고 batch 내부 구조를 해석하지 않는다.
- `iter_train_batches`처럼 순회 자체를 task hook으로 감싸지 않는다.
- batch 실행이 가능한 v0.1 PyTorch backend에는 iterable 계약을 적용한다.
- 향후 전체 dataset에 한 번의 `fit`을 수행하는 backend에는 별도의 실행 capability를 정의하며 batch iterable을 강제하지 않는다.
- `validate`는 `valid` split을 사용하고 `evaluate`는 `test` split을 사용한다.
- `validate`와 `evaluate`는 동일한 평가 loop와 `eval_step` 계약을 사용하며 context의 stage로 구분한다.
- `test` split은 학습 중 validation, model 선택, early stopping과 scheduler 판단에 사용하지 않는다.
- metrics의 종류, 생성, 상태와 계산 방법은 task adapter가 정의하고 소유한다.
- metrics는 validation과 evaluation에서만 사용한다.
- 공통 engine은 validation과 evaluation에서 `reset_metrics`, `update_metrics`, `compute_metrics` hook을 순서대로 호출할 뿐 metric 객체와 task별 입력 형식을 알지 않는다.
- validation과 evaluation은 metric state를 각각 초기화하며 `valid`와 `test` 결과를 누적하거나 섞지 않는다.
- 학습 loss와 진행 log는 평가 metrics와 구분하고 predict에서는 metric lifecycle을 사용하지 않는다.
- 상위 batch runner는 task, adapter와 backend의 내부 동작을 알지 않고 독립된 CLI job process를 순서대로 실행한다.
- batch와 job의 실행 상태는 `status` 하나로 표현하며 `pending`, `running`, `succeeded`, `failed` 네 값만 사용한다.
- 정상적인 job 상태 전이는 `pending`에서 `running`을 거쳐 `succeeded` 또는 `failed`로 끝난다.
- 기존 `cv-batch-runner` 기획의 분리된 `state`와 `result` field는 사용하지 않는다.
- batch 하나는 `batches/batch-YYMMDD-hhmmss/` directory 하나에 보관하고 directory 이름을 batch ID로 사용한다.
- batch directory에는 `batch.json`, `batch.log`와 job별 log, resolved 실행 입력, artifact를 모두 저장한다.
- job별 결과는 batch directory 아래의 `jobs/<job-id>/`에 격리한다.
- 별도의 최상위 `results` directory는 두지 않는다.

## 이후 확정한 방향 (batch 정의 모사)

- UI/대시보드가 할 일은 `batch.csv`(대시보드 표 모사)와 그 위의 sweep-spec으로
  대신하고, python 스크립트가 이를 `batch.json`으로 변환한다. 자세한 스키마와
  전개 규칙은 `refs/batch-definition-mock.md`를 따른다.
- `epochs`와 `validate`는 adapter가 아니라 공통 engine이 소유하는 값이며,
  job 정의의 고정 열이다.
- `data`/`preprocessor`/`model`/`loss`/`trainer`/`metric`/`postprocessor`
  세부 값은 `params`라는 자유 형식(JSON) 값 하나에 담고, engine은 이 내부
  구조를 해석하지 않는다. `data`는 dataset과 dataloader를 나누지 않는다.
  섹션은 mode 이름이 아니라 pipeline 단계(입력/전처리/모델/손실/학습/평가/
  후처리) 기준으로 나눈다.
- job 결과에는 별도의 `output_dir` 선택을 두지 않고 `jobs/<job-id>/artifacts/`
  고정 경로만 쓴다.
- early stopping도 `epochs`/`validate`와 같은 자리(job 정의, `params` 밖)에
  두는 engine 소유 값이다. `early_stop: {enabled, patience, monitor, mode}`
  dict 하나로 묶고, engine은 `monitor`로 지정한 key 하나만 `compute_metrics`
  결과에서 꺼내 숫자로 비교할 뿐 metric의 의미는 해석하지 않는다.
- task 프로젝트 루트에 `base.yaml` 하나를 두어 그 task의 모든 섹션 기본값을
  담는다. adapter가 실행 시점에 `base.yaml` 위에 job의 `params`를 덮어써
  최종 설정을 만들고, 그 결과를 `resolved.json`에 기록한다. model별 별도
  기본값 파일은 두지 않는다.
- 하나의 task 안에 model이 여러 개이고 학습 절차가 서로 크게 달라도, model
  개수만큼 task를 쪼개지 않는다. task 루트에 고정된 `adapter.py` 진입점을
  두지 않고, model마다 `models/<model-name>.py`(순수 forward)와
  `adapters/<model-name>.py`(그 model 전용 Adapter 클래스, 실제
  train_step/eval_step/predict_step/configure_optimizer/loss 구현)를 둔다.
- `task.toml`은 `task.adapter` 대신 `task.registry`(`module:object` 형식,
  `registry.py`의 `MODEL_REGISTRY`를 가리킴)를 선언한다. task-runner의
  source 로딩 절차가 job의 `params.model.name`으로 이 registry를 조회해
  해당 model의 Adapter 클래스를 가져와 사용한다 — 어떤 model을 쓸지는
  Adapter 내부가 아니라 로딩 절차가 결정한다.
- `base.yaml` 병합, `resolved.json` 기록, checkpoint 경로 조합처럼 model과
  무관한 공통 로직은 task-runner 저장소 자신이 `BaseAdapter`로 제공한다.
  각 `adapters/<model-name>.py`는 `BaseAdapter`를 상속하고 그 model에서
  실제로 다른 hook만 구현한다. model에는 공통 engine import를 허용하지
  않지만 adapter에는 허용한다 — adapter 자체가 engine과 연결되는 자리이기
  때문이다. `registry.py`는 위치를 task 루트로 옮기지 않고 `src/<task_package>/`
  안에 유지한다. 근거와 예시는 `refs/model-wrapper-pattern.md`,
  `refs/base-adapter-sample.py`, `refs/adapter-sample.py`,
  `refs/registry-sample.py`.
- 여러 조건을 비교하는 sweep은 격자(grid) 조합이 아니라 `base` + 명시적
  `variants` 목록(방식 B)으로 표현하고, batch.csv 전개 단계에서 완전히
  펼쳐진 행으로 만든다.
- checkpoint 저장 경로는 `task_dir` 고정 경로가 기본이지만, sweep으로 같은
  `task_dir`에 여러 variant가 학습되면 `params._variant`로 경로를 분리한다.

## 아직 확정하지 않은 것

- backend별 adapter contract
- 단일 job과 batch의 JSON 규격 중 `params` 내부 구조를 넘어선 나머지 필드
  (예: batch 전체 요약 field)
- 중단된 `running` job의 복구와 재실행 정책
- `resolved.json`이 `batch.json`의 `params`를 그대로 복사한 것인지, adapter가
  기본값을 채운 뒤의 최종본인지
