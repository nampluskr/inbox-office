# batch runner

## 목적

task와 backend에 독립적인 상위 batch runner의 책임과 실행 상태를 정의한다. 하위 adapter의 step 반환값과 checkpoint 계약은 이 문서의 범위에 포함하지 않는다.

## 책임 경계

batch runner는 batch 문서를 읽고 검증한 뒤 정의된 순서에 따라 각 job을 독립된 child process로 실행한다. process 생성 여부와 종료 code를 기준으로 상태를 변경하며 task log의 문장을 해석하여 성공 여부를 판단하지 않는다.

batch runner가 담당하는 일은 다음과 같다.

- batch 문서 검증
- 다음 `pending` job 선택
- job별 child process 생성
- process ID와 실행 시각 기록
- child process 종료 code 확인
- job status와 결과 경로 기록
- 실패한 job 이후의 다음 job 계속 실행
- 전체 job 종료 후 batch 상태와 요약 기록

batch runner는 다음 내용을 알지 않는다.

- dataset과 batch 내부 구조
- model과 algorithm 종류
- backend의 연산 방식
- adapter lifecycle의 내부 동작
- optimizer, scheduler와 metrics

## process 구조

```text
batch runner parent process
    -> job-001 child process
    -> job-001 종료 후 job-002 child process
    -> job-002 종료 후 job-003 child process
```

각 job은 하나의 `train`, `evaluate` 또는 `predict` CLI 실행에 대응한다. `validate`는 독립 batch job으로 두지 않고 `train` lifecycle 안에서 실행한다.

## batch 실행 폴더

batch 하나는 `batches` 아래의 timestamp 기반 폴더 하나로 저장한다.

```text
batches/
└── batch-YYMMDD-hhmmss/
    ├── batch.json
    ├── batch.log
    └── jobs/
        ├── <job-id>/
        │   ├── job.log
        │   ├── resolved.json
        │   └── artifacts/
        └── <job-id>/
            ├── job.log
            ├── resolved.json
            └── artifacts/
```

예를 들어 2026년 9월 9일 14시 30분 25초에 생성한 batch 폴더는 다음과 같다.

```text
batches/batch-260909-143025/
```

directory 이름을 batch ID로 사용한다. `batch.json`에는 전체 job 정의, 실행 순서와 status를 기록하고 `batch.log`에는 batch runner의 실행 기록을 남긴다. 각 job의 log, resolved 실행 입력과 artifact는 `jobs/<job-id>/` 아래에 격리한다.

별도의 최상위 `results` 폴더는 두지 않는다. batch 정의와 해당 실행에서 생성된 log와 artifact를 하나의 batch 폴더 안에 함께 보관한다.

## status

batch와 job의 실행 상태는 `status` field 하나로 표현한다.

| status | 의미 |
| --- | --- |
| `pending` | 아직 실행을 시작하지 않음 |
| `running` | 실행을 시작했고 아직 종료되지 않음 |
| `succeeded` | 실행이 성공적으로 종료됨 |
| `failed` | 실행이 실패로 종료되었거나 process 실행에 실패함 |

기존 기획처럼 진행 상태를 `state`, 실행 결과를 `result`로 분리하지 않는다. 단일 status를 사용하여 서로 모순되는 field 조합이 생기지 않도록 한다.

정상적인 job 상태 전이는 다음과 같다.

```text
pending -> running -> succeeded
                   -> failed
```

child process가 exit code `0`으로 종료되면 `succeeded`, 그 밖의 exit code 또는 process 생성 예외는 `failed`로 기록한다. 한 job이 `failed`가 되어도 runner는 다음 `pending` job을 계속 실행한다.

## 아직 정하지 않은 것

- batch status를 job status로부터 계산하는 정확한 규칙
- runner 중단 뒤 `running`으로 남은 job의 복구 방식
- 완료 또는 실패한 job의 명시적 재실행 방식
- batch JSON의 전체 field와 경로 표현
- 같은 초에 생성되는 batch directory 이름의 충돌 처리
- 동시에 같은 batch를 실행하지 못하게 하는 잠금 방식
- batch CLI의 subcommand와 option
