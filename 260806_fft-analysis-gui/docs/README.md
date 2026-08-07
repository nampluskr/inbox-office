# FFT ROI Analysis GUI 문서

이 디렉터리는 새 구현의 설계 기준을 관리한다. 현재 단계에서는 API 계약과 GUI 골격 구조만 정의하며, 구현 코드는 포함하지 않는다.

## 문서 색인

| 문서 | 상태 | 책임 |
| --- | --- | --- |
| [spec/fft-spec.md](spec/fft-spec.md) | 검토 중 | `src/fft.py` 초기 공개 API, `Settings` 데이터 클래스 및 ROI 딕셔너리 계약 |
| [spec/gui-spec.md](spec/gui-spec.md) | 현재 기준 | 좌측 탐색기와 우측 Canvas 탭을 포함하는 GUI 골격 구조 |
| [plans/](plans/) | 이력 | 구현 계획과 실행 기록 |

## 참고 자료

`refs/legacy1/`과 `refs/legacy2/`는 이전 구현의 참고 자료다. 새 구현은 이 경로를 import하거나 runtime dependency로 사용하지 않는다.

## 문서 원칙

- API 계약은 분석 계층의 공개 입력과 출력을 정의한다.
- GUI 구조 문서는 화면 계층, 모듈 책임 및 사용자 표시 규칙을 정의한다.
- 구현 범위가 확정되면 현재 기준 문서를 먼저 갱신한 뒤 코드를 작성한다.

## Plan 문서

- 구현 계획은 `docs/plans/NNNN-topic-plan.md` 형식으로 작성한다.
- 번호는 4자리 0-padding 순번이며 삭제하거나 재사용하지 않는다.
- 상태는 `Draft`, `Approved`, `Done` 중 하나를 사용한다.
- 구현 전 계획은 `Draft`로 작성하고, 승인 후 `Approved`, 완료 후 `Done`으로 갱신한다.
