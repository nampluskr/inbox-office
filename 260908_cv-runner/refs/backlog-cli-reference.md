# backlog CLI 참조 분석

## 확인 대상

- 원격 저장소: `https://github.com/nampluskr/backlog.git`
- 로컬 참조: `D:\projects\_clones\backlog`
- branch: `main`
- revision: `702842736e8ae5827e20575133ae8779f354fa92`

## 확인된 구조

`backlog`는 `backlog.json`을 작업 상태의 SSOT로 사용하는 Python CLI다. `--file`로 대상 JSON을 선택하고 `validate`, `list`, `show`, `add`, `update` subcommand를 제공한다.

실제 사용에서는 사용자 요청을 받은 AI agent가 작업을 수행하고 `backlog` CLI를 호출하여 상태를 변경한다. `backlog` CLI 자체는 backlog에 기록된 작업을 실행하지 않는다.

정상 결과는 stdout, 오류는 stderr로 출력하고 오류 종류에 따라 종료 코드를 구분한다. `list`와 `show`는 사람이 읽는 출력과 JSON 출력을 제공한다.

쓰기 명령은 다음 순서를 따른다.

1. UTF-8 JSON을 읽고 parsing한다.
2. 변경 전 전체 문서를 검증한다.
3. 원본을 직접 바꾸지 않고 복제본을 변경한다.
4. 변경 후 전체 문서를 다시 검증한다.
5. 같은 폴더의 임시 파일에 직렬화한다.
6. `os.replace`로 원본을 원자적으로 교체한다.

동시 쓰기 잠금은 제공하지 않으며 단일 writer를 가정한다.

## cv-batch-runner에 적용할 원칙

다음 `backlog` 특성은 그대로 적용할 수 있다.

- JSON을 현재 상태의 SSOT로 사용한다.
- 최상위 `--file` option으로 대상 batch JSON을 지정한다.
- 검증, 목록과 상세 조회를 subcommand로 분리한다.
- 기계가 읽는 JSON 출력 형식을 제공한다.
- 모든 상태 변경에 사전 검증, 사후 검증과 원자적 저장을 적용한다.
- 하나의 runner만 batch JSON을 수정하는 단일 writer 원칙을 사용한다.
- 정상 출력, 오류 출력과 종료 코드를 구분한다.
- 임시 fixture 복사본을 사용하는 CLI와 문서 입출력 테스트를 둔다.

다음 사항은 `cv-batch-runner`가 별도로 추가해야 한다.

- 미진행 job을 정의된 순서대로 실행하는 batch 실행 명령
- 각 행을 train, evaluate 또는 predict CLI command로 변환하는 기능
- 실행 직전과 직후의 job 상태 전이
- 실패한 job을 기록하고 다음 job으로 진행하는 실행 정책
- job별 독립 결과 폴더, log와 artifact 경로 기록
- 전체 batch 종료 요약과 terminal 유지
- AI agent 없이 사용자 또는 UI의 실행 요청만으로 동작하는 결정론적 runtime

## 적용하지 않는 backlog 운영 방식

`cv-batch-runner`는 AI agent가 작업을 수행한 뒤 CLI로 상태를 갱신하는 운영 방식을 적용하지 않는다. `backlog`에서 참고하는 범위는 JSON SSOT, CLI 명령 구조, 문서 검증과 안전한 저장 방식이다.

`cv-batch-runner`의 job은 batch runner가 실제 CLI process로 실행한다. 시작 상태는 process 실행 직전에, 종료 상태와 성공 또는 실패 결과는 process 종료 직후 runner가 직접 기록한다.

## command 대응 초안

정확한 명령 이름과 option은 이후 interface 규격에서 확정한다. 현재 단계의 기능 대응은 다음과 같다.

| backlog 기능 | cv-batch-runner 대응 |
| --- | --- |
| `--file` | 대상 batch JSON 선택 |
| `validate` | batch와 모든 job 규격 및 조합 검증 |
| `list` | job 목록과 상태 조회 |
| `show` | 개별 job의 조건, 상태와 결과 경로 조회 |
| `add`, `update` | UI 또는 CLI가 job 정의를 구성하고 수정하는 안전한 변경 경로 |
| 없음 | pending job을 순차 실행하는 `run` 계열 명령 |

UI dashboard는 terminal 문자열을 분석하지 않고 CLI의 JSON 출력 또는 batch JSON을 읽어 상태를 표시한다. 실행 버튼은 terminal launcher를 통해 batch 실행 명령을 시작한다.
