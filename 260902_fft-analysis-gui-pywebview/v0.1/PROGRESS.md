> 버전: v0.1 · 상태: 마감

# PROGRESS

## 계획된 작업

- P1: 애플리케이션 골격, `.mim` 이미지 로드·표시·회전과 Explorer를 구현하고 검증했다.
- P2: 다중 ROI 편집, ROI 프리셋, ROI 탭 상태와 비동기 요청 보호를 구현하고 검증했다.
- P3: raw profile, 경계 0-padding 없는 정규화 profile, ROI별 분석 요청을 구현하고 검증했다.
- P4: FFT, peak 탐색, peak-to-valley, 선택 피크 주기 오버레이와 회귀 검증을 완료했다.
- P5: Settings, API 오류 형식, 디자인 토큰, 환경 설정 및 PyInstaller 패키징을 완료했다.

각 Phase의 세부 task, 검증 결과 및 적대적 검토 기록은 `backlog.json`에 보관한다. 모든 Phase는 `done` 상태다.

## 계획 외 개선

- UI 비동기 응답의 순서 역전으로 이전 분석 결과가 최신 상태를 덮어쓰지 않도록 요청 토큰 보호를 보강했다.
- 극단적인 peak period에서 오버레이 위치가 과도하게 생성되지 않도록 상한과 경계 검증을 추가했다.
- API 예외 처리와 Settings 검증을 표준 오류 envelope로 통일했다.

## 마감 요약

- 계획 대비: backlog의 P1~P5 전체가 완료됐다.
- 계획 외 개선: 비동기 상태 일관성, 오버레이 경계, 오류 처리 안정성을 보강했다.
- 남긴 것: Python이 설치되지 않은 clean Windows 환경에서의 독립 실행 파일 검증은 수행하지 않았다.
- 다음 버전으로: clean Windows 배포 검증, 보고서·CSV 저장, 테마 확장 등은 v0.2 이상의 요구가 확정될 때 검토한다.
