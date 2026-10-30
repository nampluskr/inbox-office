# Markdown Editor 실행 계획

## INTENT

확정된 요구를 문서 작성·협업 구성과 향후 앱 구현·검증 작업으로 연결한다. 최신 사용자 요청은 GPUI Kit 기반 실행 가능한 MVP 구현·빌드·검증이다. main의 D-8/D-10/D-11 및 확정 U-1~U-10을 적용하여 Sol이 P-5~P-15를 순서대로 통합하고 Terra가 독립 구현·검토한다. 실제 상태와 결과는 [PROGRESS](PROGRESS.md)에 기록한다.

기준 문서는 [프로젝트 INTENT](../../INTENT.md), [버전 INTENT](INTENT.md), [DECISIONS](DECISIONS.md), [SPEC](SPEC.md)이다. U-1~U-10은 main이 확정한 구현 기준이다. 요구 변경이나 주요 기술 대체는 증거·대안과 함께 main에 보고한다. 기존 작업 표의 정책 확정 조건은 해당 결정으로 충족되었으며 매번 사용자 승인을 기다리지 않는다.

## 에이전트 구성과 수정 경계

사용자가 지정한 Codex Sol·Terra 구성이다. 아래 배치는 호출·통합 담당이 현재 프로젝트의 Herdr CLI에서 생성하고 모델·작업 경로·좌우 분할을 확인했다. 실제 실행 내역은 PROGRESS에 기록한다.

| 담당 | 역할과 수정 범위 |
| --- | --- |
| 호출·통합 담당 | 사용자 응답, Herdr 구성·상태 확인, 결과 회수와 최종 통합·검증. 담당 파일 수정은 해당 담당의 작업 종료 확인 후 수행 |
| Sol `specs-sol` | 구현 리드. Cargo·작업 공간·파일 I/O·세션 및 README·PLAN·PROGRESS 최종 통합 책임. 기술 결정과 AGENTS는 main 담당 |
| Terra `specs-terra` | Sol이 배정한 원문 편집·강조 및 Preview·렌더링 모듈 구현·검토. 저장 I/O와 PLAN 통합은 Sol 담당 |
| 검사 패널 | PowerShell 문서 검사·빌드 로그 확인. Sol이 결과 회수 |

## MVP 파일 소유권과 인터페이스

| 담당 | 수정 파일 | 책임 |
| --- | --- | --- |
| Sol | Cargo.toml, Cargo.lock, src/main.rs, src/workspace.rs, src/files.rs, src/session.rs, README, 버전 INTENT·SPEC·PLAN·PROGRESS | 창·폴더·트리·탭·저장·충돌·복원·메뉴·최종 빌드 통합 |
| Terra | src/editor.rs, src/preview.rs, scripts/mathjax.cjs, package.json, package-lock.json, samples/preview.md 및 로컬 이미지 | Kit EditorState 원문 편집·강조, TextView Preview, 수식 helper와 렌더링 샘플 |
| main | AGENTS, 루트 INTENT, DECISIONS | 정책 판단과 근거 기록 |

Terra는 Cargo를 동시에 실행하지 않고 의존성 추가를 Sol에게 보고한다. 편집기는 EditorPane이 Entity<EditorState>를 소유하며 text/set_text/view를 제공한다. PreviewPane은 new/update/view를 제공하고 정확한 Kit 생성 인자는 Terra가 registry 소스로 확인하여 전달한다. 문서 ID·generation·150ms 지연·Preview 탭/분할 배치와 저장 I/O는 Sol 책임이다. 공유 API 변경은 먼저 전달하며 소유자 작업 종료 확인 전 다른 담당 파일을 수정하지 않는다. 조사·모듈 작성은 병렬 가능하나 실행 검증과 기능 통합은 P-ID 의존 순서를 따른다.

## 실제 Herdr 배치와 운영

| 위치 | 용도 | 대상 | 작업 경로 |
| --- | --- | --- | --- |
| `wH:t1` | 기존 호출 탭 | 기존 구성 보존 | 기존 환경 보존 |
| `wH:t2` / `specs-v0.1` 왼쪽 | Sol | `wH:p2`, `specs-sol`, `gpt-6.1-sol` | `D:/projects/rust-test` |
| `wH:t2` / `specs-v0.1` 오른쪽 | Terra | `wH:p3`, `specs-terra`, `gpt-6.1-terra` | `D:/projects/rust-test` |
| `wH:t3` / `specs-checks` | PowerShell 문서 검사 | `wH:p4` | `D:/projects/rust-test` |

위 ID는 이번 실행에서 CLI 응답으로 확인한 값이며 세션이 바뀌면 다시 조회한다. 명령 전에 `HERDR_ENV=1`을 확인하고 아니면 Herdr 제어를 중단한다. 실제 목록과 패널의 cwd·프로세스를 확인하고 명시 ID 또는 고유 이름을 사용한다. 사용자 포커스를 바꾸지 않는 백그라운드 운영을 유지하며, 승인된 배치를 재구성할 때는 기존 전용 탭·에이전트를 먼저 찾아 재사용하고 생성 시 `--no-focus`와 동일 cwd를 지정한다. 기존 사용자 탭·패널을 종료하거나 서버를 재시작하지 않는다.

Bun이 없어 래퍼 대신 설치된 Herdr CLI를 사용했다. 관리자 서버 조회는 호출 담당의 승인된 승격 명령으로 정상 접근을 확인했다. 실제 호출 시 권한과 결과를 확인하며 승격은 호출 환경의 승인 절차를 따른다. 아래는 재조회·작업 전달·검사를 위한 예시다. `HERDR_ENV` 조회값이 `1`이 아니면 이후 Herdr 명령을 실행하지 않는다. 모든 외부 명령은 RTK를 경유한다.

```powershell
rtk proxy powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('HERDR_ENV')"
rtk proxy herdr workspace list
rtk proxy herdr tab list --workspace wH
rtk proxy herdr pane list --workspace wH
rtk proxy herdr pane process-info --pane wH:p2
rtk proxy herdr agent list
rtk proxy herdr agent get specs-sol
rtk proxy herdr agent read specs-sol --source recent-unwrapped --lines 120
rtk proxy herdr agent prompt specs-sol "담당 작업과 수정 경계를 확인하고 결과와 미해결 사항을 보고하세요." --wait --timeout 45000
rtk proxy herdr pane run wH:p4 "rtk proxy python scripts/check_docs.py"
rtk proxy herdr pane read wH:p4 --source recent-unwrapped --lines 120
```

작업 전달에는 문서 경로, 작업 ID, 수정 범위, 선행 조건과 완료 기준을 포함한다. 전달 성공은 작업 시작이나 완료의 증거가 아니며 검사 명령 접수도 실행 완료를 뜻하지 않는다. 호출 담당은 출력과 산출물, 검증 결과 및 미해결 사항을 회수하고 실제 파일 상태와 대조한다. `idle` 또는 `done`만으로 완료를 판정하지 않는다. `blocked`, 시간 초과, stalled 또는 오류 시 대상 상태와 출력을 먼저 확인한다. 명령이 이미 전달됐을 수 있으므로 무조건 재전송하지 않는다. 승인이나 질문 화면은 내용을 확인하고 필요한 사용자 판단을 받는다.

작업 탭은 두 에이전트를 좌우 50:50으로 분할한다. 초기 구성 시 탭 생성 응답의 root pane ID를 Sol에 배정하고, 해당 패널을 오른쪽으로 분할한 응답 ID를 Terra에 배정한다. `agent start`의 `--kind codex` 뒤에 네이티브 인수 `-- --model gpt-6.1-sol --approve-for-me -C D:\projects\rust-test` 또는 Terra 모델 인수를 전달한다. `--approve-for-me`가 workspace-write를 선택하므로 `--sandbox workspace-write`를 함께 지정하지 않는다. 검사 탭은 에이전트 없이 PowerShell 하나만 유지한다. 생성과 시작 성공 응답의 ID·모델 인수·cwd를 확인하고 PROGRESS에 기록한다. 작업 후 전용 탭과 에이전트는 유지한다.

## Phase 1: 문서와 협업 구성

목적: 승인된 범위의 문서와 기존 협업 배치를 정리하고 정합성을 확인한다. 완료 기준: 담당 결과와 미결 사항을 회수하고 요구·계획·진행 기록 및 링크, UTF-8과 한글을 확인하여 실제 결과를 PROGRESS에 기록한다. 앱 기능 완료를 뜻하지 않는다.

| 작업 | 내용 | 대응 요구 | 선행 작업·조건 | 담당 | 검증 방법 |
| --- | --- | --- | --- | --- | --- |
| P-1 | 의도·결정·요구와 신규 문서 안내 작성 | R-1, R-2, R-3, R-4, R-5, R-6, R-7, R-8, R-9, R-10, R-11, R-12, R-13, R-14 | 사용자 확정 범위와 기존 지침 확인 | Sol | 문서 재읽기, 요구·제외 범위 및 미결 구분 확인 |
| P-2 | 신규 명세 검토와 PLAN 작성 | R-1, R-2, R-3, R-4, R-5, R-6, R-7, R-8, R-9, R-10, R-11, R-12, R-13, R-14 | P-1의 검토 대상 문서 제공; Sol 담당 파일 동시 수정 금지 | Terra | R-ID 전수 대조, U-ID 의존 조건과 Phase·작업·담당·검증 확인 |
| P-3 | 사용자 지정 Herdr 배치와 운영 상태 확인 및 결과 회수 | 해당 없음 | 사용자 승인 범위, HERDR_ENV와 접근 권한 확인 | 호출·통합 담당 | 명시 ID의 상태·cwd·출력과 산출물 확인; 기존 탭 보존 확인 |
| P-4 | 과거 문서와 임시 파일 정리, 신규 문서 링크 통합 검토와 진행 기록 | R-1, R-2, R-3, R-4, R-5, R-6, R-7, R-8, R-9, R-10, R-11, R-12, R-13, R-14 | P-1~P-3 결과 회수 및 담당 작업 종료 확인 | 호출·통합 담당; PROGRESS는 Sol과 순차 조정 | 호출 담당이 과거 `specs` 직하 3개 문서와 `docs/RUST-INTRO.md`, `docs/RUST-GUI.md`, 임시 `.d1` PowerShell 파일을 정리하고 검사 도구는 유지. 신규 문서 링크 정합성 및 `rtk proxy python scripts/check_docs.py` 결과 확인, UTF-8 재읽기·한글 손상 확인; 실제 조치·결과·미결 사항을 PROGRESS에 기록 |

## Phase 2: Windows 기반과 렌더링 검증 — 대기

목적: 후속 구현을 위한 Windows 환경과 화면·입력·렌더링 조합의 실현 가능성을 확인한다. 완료 기준: 합의 환경과 샘플의 결과, 한계 및 선택 근거를 기록하고 다음 단계의 기술 조건을 충족한다.

| 작업 | 내용 | 대응 요구 | 선행 작업·조건 | 담당 | 검증 방법 |
| --- | --- | --- | --- | --- | --- |
| P-5 | Windows 기본 창과 한글 표시·입력 검증 | R-1 | P-4, 최신 구현 요청 적용, 대상 Windows 환경과 U-9 버전 조합·호환성 검증 계획 확정 | Sol | 합의 환경에서 창 시작과 한글 표시·입력 확인, 환경과 결과 기록 |
| P-6 | 편집·Markdown·수식 렌더링 후보 검증 및 조합 결정 지원 | R-4, R-7 | P-5, U-9 검증 계획; 기능별 구현 전 U-1·U-4·U-9와 샘플은 main 확정 정책 적용 | Terra | 합의 샘플과 Windows 호환성·리소스·라이선스 조건 대조; 후보 결과와 기술 대체 필요 여부를 main에 전달 |

## Phase 3: 폴더·트리·탭 — 대기

목적: 폴더 선택과 파일 탐색, 탭의 작업 공간을 연결한다. 완료 기준: 두 폴더와 중첩 트리의 전환·열기 및 등록 해제를 요구 기준으로 확인한다.

| 작업 | 내용 | 대응 요구 | 선행 작업·조건 | 담당 | 검증 방법 |
| --- | --- | --- | --- | --- | --- |
| P-7 | Sidebar 폴더 등록·선택·등록 해제와 Leftbar 트리 | R-2, R-3, R-12 | P-5~P-6, U-8 확정; 파일 오류 경로는 U-6·U-7 확정 후 착수 | Sol | 두 폴더 전환, 중첩 파일 열기와 등록 해제 후 디스크 보존 확인; 확정 오류 시나리오 대조 |
| P-8 | 오른쪽 원문 탭과 폴더별 탭·선택 상태 연결 | R-3, R-8 | P-7, U-1·U-2 파일 열기 정책과 U-3·U-7·U-8 상태·문서 수명 확정 | Sol; 편집 연결은 Terra와 경계 합의 | A→B→A 전환 후 탭·선택·미저장 상태를 확정 정책과 대조 |

## Phase 4: 편집과 저장 — 대기

목적: 원문을 바로 편집하고 안전하게 저장한다. 완료 기준: 합의 샘플의 편집·강조·저장과 확정된 오류 처리를 확인한다.

| 작업 | 내용 | 대응 요구 | 선행 작업·조건 | 담당 | 검증 방법 |
| --- | --- | --- | --- | --- | --- |
| P-9 | Markdown·코드 원문 편집과 구문 강조 | R-4 | P-6·P-8, U-1·U-2·U-9 확정 | Terra | 확정 언어와 Markdown 샘플에서 강조 및 한글·코드 입력 확인 |
| P-10 | 저장과 외부 변경·충돌 처리 | R-5, R-12 | P-9, U-2·U-6 확정; 관련 문서 수명·실패 처리는 U-8 확정 후 착수 | Terra | 저장 후 재열기·내용과 변경 상태 대조; 접근 거부·저장 실패·외부 변경 충돌을 확정 정책과 대조 |

## Phase 5: Preview와 수식 — 대기

목적: 미저장 원문에 연결된 Preview와 확정 문법을 제공한다. 완료 기준: 두 표시 방식과 최신 버퍼, 문법·리소스·수식 샘플이 요구대로 동작한다.

| 작업 | 내용 | 대응 요구 | 선행 작업·조건 | 담당 | 검증 방법 |
| --- | --- | --- | --- | --- | --- |
| P-11 | Preview 연결·탭 및 오른쪽 분할·갱신 | R-6, R-8 | P-8~P-10, U-3 확정; 폴더별 상태는 U-7·U-8 확정 | Terra; 탭·분할 연결은 Sol과 경계 합의 | 두 표시 방식에서 미저장 수정 반영 시간과 원문 연결, 폴더 전환 상태 확인 |
| P-12 | Markdown·코드 강조·상대 리소스·수식 렌더링 | R-7, R-12 | P-6·P-11, U-1·U-4·U-5·U-9 및 샘플 확정 | Terra | 기본 문법·표·작업 목록·코드·상대 이미지/링크·인라인/블록 수식 및 리소스 오류를 확정 결과와 대조 |

## Phase 6: 복원·메뉴·통합 — 대기

목적: 세션과 패널 복원, 종료 처리, 메뉴 및 전체 범위를 완성하고 검증한다. 완료 기준: 전체 R-1~R-14의 실제 검증 결과와 미해결 사항이 기록되고 사용자에게 전달된다. 버전 종료는 사용자가 판단한다.

| 작업 | 내용 | 대응 요구 | 선행 작업·조건 | 담당 | 검증 방법 |
| --- | --- | --- | --- | --- | --- |
| P-13 | 패널 독립 토글·크기와 폴더별 세션 지속화·복원 | R-8, R-9, R-10, R-12 | P-7~P-12, U-7·U-10 확정; 복원 오류 경로는 U-7 확정 | Sol | 두 패널 독립 조작, 크기·표시 및 폴더·파일 탭 재시작 복원과 누락·손상 상태 처리 확인 |
| P-14 | 미저장 종료와 문서 수명 처리 | R-2, R-8, R-11, R-12 | P-10·P-13, U-8 확정 | Sol; 저장 연결은 Terra와 경계 합의 | 저장·버리기·취소와 다중 문서·저장 실패를 각각 확정 정책과 대조 |
| P-15 | 구현 기능만 메뉴에 연결하고 레이아웃·제외 범위 통합 검증 | R-1, R-2, R-3, R-4, R-5, R-6, R-7, R-8, R-9, R-10, R-11, R-12, R-13, R-14 | P-13·P-14 및 모든 의존 정책 확정 | Sol·Terra 각 책임 영역; 호출·통합 담당 최종 검증 | 메뉴 항목 실행, 참조 이미지 영역 대조, 제외 기능 확인 및 SPEC 전 요구 시나리오 수행·기록 |

## 진행 기록

[PROGRESS](PROGRESS.md)는 위 Phase와 P-ID를 참조하여 상태를 대기·진행·완료·보류로 관리한다. Phase 착수, 상태 변경, 완료와 문제 발생 시 일자·수행 내용·실제 검증·남은 문제를 기록하고 사용자 요청 이력을 보존한다. 문서 검사와 앱 기능 검증을 구분하며 수행하지 않은 작업은 완료로 표시하지 않는다.
