# 에이전트 작업 지침

- 프로젝트 전체 기준은 [INTENT.md](INTENT.md)다. 현재 버전은 `v0.1`이며 [PLAN](specs/v0.1/PLAN.md)을 진입점으로 사용한다.
- 공통 절차는 [WORKFLOW](../project-workflow-compact/WORKFLOW.md), 문서 기준은 [DOCUMENTS](../project-workflow-compact/docs/DOCUMENTS.md), 협업 기준은 [MULTI-AGENT](../project-workflow-compact/docs/MULTI-AGENT.md)를 따른다. 가이드 사본을 만들지 않는다.
- 현재 요청은 GPUI Kit으로 빠른 앱 생성이 가능한지 검증하는 Markdown Editor MVP 구현이다. 문서 작성에 한정했던 이전 범위는 사용자 최신 요청으로 대체되었다. PLAN의 P-5~P-15를 순서대로 구현·빌드·검증한다.
- 사용자가 지정한 에이전트는 Codex Sol과 Terra다. 같은 프로젝트에서는 Herdr의 `specs-v0.1` 탭을 사용한다. Sol은 왼쪽, Terra는 오른쪽 패널이며 작업 경로는 모두 `D:\projects\rust-test`다.
- Sol(`specs-sol`)은 구현 리드다. PLAN을 따라 작업을 실행하고 Terra에게 독립 작업과 검토를 위임하며 앱·문서·PROGRESS를 통합한다. Terra(`specs-terra`)는 Sol이 배정한 파일의 편집·렌더링 구현과 검토를 맡는다. 파일별 수정 경계와 공유 인터페이스는 구현 전에 Sol이 기록한다. 같은 파일을 동시에 수정하지 않는다.
- 현재 main 에이전트는 결정권자다. 사용자가 기술·MVP 정책 판단을 위임했으므로 필요한 판단을 하고 근거를 DECISIONS에 기록한 뒤 Sol에게 지시한다. Sol은 확정 결정 범위에서 구현하며 새로운 제품 범위 변경·기술 대체가 필요하면 근거와 대안을 main에 보고한다. 단순 구현 세부사항 때문에 진행을 중단하지 않는다.
- `specs-checks` 탭은 PowerShell 검사·빌드 로그 확인용으로 사용한다. Sol은 Herdr 스킬과 현재 권한 절차에 따라 Terra에게 작업을 전달하고 결과를 회수할 수 있다. 기존 사용자 탭·패널을 종료하거나 서버를 재시작하지 않는다. 구체적 배치와 운영 절차는 PLAN에 기록한다.
- 사용자 요구를 임의로 확대하지 않는다. 기존 U-1~U-10은 main이 확정한 MVP 결정에 따라 수행한다. 판단 근거와 관찰 증거를 구분하고 미검증 동작을 완료로 표시하지 않는다.
- 최종 레이아웃 참고는 사용자가 마지막에 첨부한 `zed-screenshot.png`다. 이전 `workbench-kit-ui-screenshot.png`를 대체한다. Sidebar는 폴더 목록, Leftbar는 파일 트리다.
- 문서와 사용자 요청의 조치·검증 결과는 해당 버전 PROGRESS에 기록한다. 앱 구현·실행을 하지 않은 경우 완료로 표시하지 않는다.
- 사용자 최신 요청에 따라 이전 비버전 specs와 Rust 학습 문서는 삭제했다. 현재 제품 문서의 링크는 루트 및 `specs/v0.1/`을 기준으로 유지한다. 문서 검사는 `rtk proxy python scripts/check_docs.py`로 수행한다.
- Markdown은 UTF-8로 저장하고 다시 읽어 한글 손상을 확인한다. 이모지는 사용하지 않는다.
- 모든 외부 명령은 RTK를 경유한다. PowerShell cmdlet은 `rtk proxy powershell -NoProfile -Command ...`로 실행한다. 상세 규칙은 [RTK.md](C:/Users/wonhee.nam/.codex/RTK.md)를 따른다.
