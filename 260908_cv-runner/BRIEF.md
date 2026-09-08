> 버전: v0.1 · 작성일: 2026-09-08

# BRIEF

## 배경

사용자는 `cv_boilerplate`, `defectvad-refactoring`, `roi-corner-detection-ver3`에서 다양한 데이터셋, task와 model을 통합하여 학습하는 구조를 만들어 왔다. 그러나 데이터셋과 model을 먼저 구현하고 CLI와 batch 실행을 뒤에 추가하는 bottom-up 방식으로 진행하면서, 새로운 task나 model을 추가할 때마다 실행 방법과 option 구성이 달라졌다.

## 이번 버전에서 풀고 싶은 문제

- 실제 데이터셋과 model은 구현되어 있다고 가정하고 mock으로 대체한다.
- 데이터셋, task, model, backbone과 model parameter를 표현하는 데 필요한 인터페이스 규격을 먼저 정한다.
- 사용자가 선택할 수 있는 구성요소와 가능한 조합을 확인하는 공통 방식을 정한다.
- 학습, 평가, 추론 job이 공유하는 실행 규격을 정한다.
- 단일 job을 실행하는 CLI 형식을 정한다.
- 전체 batch, 그 안의 job과 각 job의 진행 상태를 함께 기록하는 JSON 형식을 정한다.
- `backlog`처럼 JSON을 검증, 조회하고 안전하게 변경하는 전용 CLI 형식을 정한다.
- batch의 각 행과 하나의 CLI 명령이 일대일로 대응하게 한다.
- 사용자가 볼 수 있는 하나의 터미널을 열고 batch의 job을 JSON에 정의된 순서대로 실행한다.
- 한 job이 실패해도 실패를 기록하고 다음 job을 실행한다.
- 각 job이 독립된 결과 폴더에 결과물과 `logging` 기반 로그를 기록하게 한다.
- 사용자가 실행을 시작하면 AI agent 개입 없이 runner가 JSON과 CLI 종료 결과에 따라 job을 실행하고 상태를 변경하게 한다.
- 모든 job의 실행이 끝난 뒤에도 터미널을 열어 두어 사용자가 최종 상태를 확인하고 직접 닫을 수 있게 한다.
- 향후 Electron 기반 앱이나 웹 애플리케이션이 같은 실행 규격을 사용할 수 있게 한다.

## 하지 않을 것

- 실제 데이터셋 구축과 제공
- 실제 model과 backbone 알고리즘 구현
- 실제 학습 성능과 정확도 비교
- Electron 기반 앱 또는 웹 애플리케이션 구현
- 최종 사용자 인터페이스 기술 확정
- AI agent를 batch runtime의 구성요소로 사용하거나 AI agent가 job 상태를 판단하게 하는 기능

## 완료 조건

- mock 데이터셋과 mock model을 사용해 학습, 평가, 추론 CLI job을 각각 실행할 수 있다.
- 데이터셋, task, model, backbone과 model parameter의 선택 가능 여부를 실행 전에 검증할 수 있다.
- batch 전체 정의, 실행할 job 목록과 각 job의 진행 상태를 하나의 JSON 파일로 저장하고 다시 읽을 수 있다.
- CLI로 batch JSON 전체를 검증하고 job 목록과 개별 job을 조회할 수 있다.
- runner의 상태 변경 전후에 batch JSON 전체가 유효한지 검사하고 안전하게 저장할 수 있다.
- batch의 각 행을 하나의 독립된 CLI 명령으로 변환할 수 있다.
- 사용자가 볼 수 있는 하나의 터미널에서 JSON에 정의된 순서대로 여러 job을 실행할 수 있다.
- 중간 job이 실패해도 뒤의 job이 실행되며, 각 job의 성공과 실패 결과를 구분할 수 있다.
- job 실행 전후에 해당 job의 진행 상태가 JSON 파일에 반영된다.
- 학습, 평가, 추론 job마다 독립된 결과 폴더가 생성되고 해당 폴더에 결과물과 `logging` 기반 로그 파일이 기록된다.
- 사용자 또는 UI가 실행을 시작한 뒤 AI agent 호출 없이 전체 batch가 진행된다.
- 모든 job이 끝난 뒤 terminal에 최종 완료 상태가 표시되고, terminal은 사용자가 닫기 전까지 열린 상태로 남는다.
- 추가 완료 조건은 이후 대화에서 확정한다.
