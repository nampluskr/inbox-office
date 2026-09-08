# 이전 프로젝트 실행 구조 확인

## 확인 범위

다음 프로젝트의 학습, 평가, 추론, batch와 logging 관련 코드를 읽기 전용으로 확인했다.

- `D:\projects\_clones\cv_boilerplate`
- `D:\projects\_clones\defectvad-refactoring`
- `D:\projects\_clones\roi-corner-detection-ver3`

`defectvad-refactoring`에는 제품 코드가 없으므로 해당 문서가 분석 대상으로 삼은 `D:\projects\_clones\defectvad`의 실행 코드도 확인했다.

## 확인된 사실

### cv_boilerplate

- `src/cli/commands.py`의 `train`, `evaluate`, `predict`가 공통 config 해석과 component 조립 흐름을 사용한다.
- 세 command 모두 job별 run directory를 만들고 `setup_logger`를 호출한다.
- `setup_logger`는 console handler와 file handler를 함께 구성하지만, 세 action 모두 파일명이 `train.log`로 고정된다.
- benchmark runner는 case를 순서대로 실행하고 예외를 failed row로 기록한 뒤 다음 case를 계속 실행한다.
- benchmark 실행은 독립 CLI subprocess의 나열이 아니라 Python 함수 호출 중심이다.

### defectvad와 defectvad-refactoring

- `experiments/train.py`, `evaluate.py`, `predict.py`가 서로 다른 CLI entry point로 존재한다.
- `experiments/run_training.py`, `run_evaluation.py`, `run_prediction.py`는 조합마다 subprocess를 순서대로 실행한다.
- 기존 runner는 subprocess가 실패하면 즉시 `return`하여 뒤의 조합을 실행하지 않는다.
- 각 action은 Python `logging`을 사용하지만 파일 이름과 config 탐색 로직이 중복되어 있다.
- `evaluate.py`와 `predict.py`의 timestamp 지정 분기에는 `config_file`을 log 파일명으로 다시 대입하고 `log_file`을 설정하지 않는 동일한 불일치가 있다.
- `defectvad-refactoring` 문서는 이 중복과 fail-fast 동작을 대체하고, 공통 lifecycle과 선언적 manifest를 사용하는 방향을 제안한다.

### roi-corner-detection-ver3

- `scripts/train.py`, `evaluate.py`, `predict.py`가 같은 parser와 model 조립 option을 사용한다.
- `scripts/batch_run.py`는 config 순서대로 subprocess를 하나씩 실행한다.
- 한 subprocess가 실패해도 결과를 failed record로 남기고 다음 config를 계속 실행한다.
- 모든 job을 실행한 뒤 실패가 하나라도 있으면 batch process는 exit code 1로 종료한다.
- train은 `Trainer`의 logger를 통해 `run.log`를 남긴다.
- evaluate와 predict는 결과 파일을 저장하고 `print`로 경로를 알리지만, 자체 logger를 구성하지 않는다.

## 새 프로젝트에 주는 근거

- 순차 실행과 실패 후 계속 실행하는 동작은 `roi-corner-detection-ver3`에서 확인된 방식과 맞는다.
- 모든 action에 동일한 logging 계약을 적용해야 기존 프로젝트의 train, evaluate, predict 간 차이를 반복하지 않는다.
- job마다 독립된 log identity와 경로를 가져야 batch 안에서 실패 원인을 구분할 수 있다.
- batch 행과 실제 CLI command를 일대일로 유지해야 개별 job을 batch 밖에서 그대로 재실행할 수 있다.
