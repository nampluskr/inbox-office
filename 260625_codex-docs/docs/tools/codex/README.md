# Codex CLI 매뉴얼

## 문서 목적
이 폴더는 Codex CLI를 외부 터미널에서 직접 사용하는 방법을 정리한다.

Codex 앱 대화창 또는 VS Code Extension 사용 경험이 있는 사용자가 PowerShell에서 `codex` 명령을 실행하고, 프로젝트 작업, 권한 제어, 세션 관리, Git 리뷰까지 이어갈 수 있도록 구성한다.

## 작성 예정 문서
| 순서 | 파일명 | 내용 |
|---:|---|---|
| 01 | `codex-01-setup.md` | Windows PowerShell 설치, PATH 설정, `codex --version` 확인 |
| 02 | `codex-02-quickstart.md` | 첫 실행, 로그인, 첫 요청 보내기 |
| 03 | `codex-03-interface-modes.md` | 웹 대화창, Codex 앱, 앱 내부 터미널, 외부 터미널 CLI 차이 |
| 04 | `codex-04-command-reference.md` | 자주 쓰는 Codex CLI 명령과 옵션 |
| 05 | `codex-05-project-workflow.md` | 프로젝트 폴더에서 파일 읽기, 수정 요청, 결과 확인 |
| 06 | `codex-06-permissions-sandbox.md` | approval, sandbox, read-only, workspace-write, full access |
| 07 | `codex-07-session-management.md` | 세션 저장, `resume`, 이전 작업 이어가기 |
| 08 | `codex-08-git-review-workflow.md` | Git 상태 확인, diff, review, 커밋 전 점검 |
| 09 | `codex-09-troubleshooting.md` | 설치, 로그인, 권한, 터미널, 인코딩 문제 해결 |
| 10 | `codex-10-cheatsheet.md` | 자주 쓰는 명령과 상황별 프롬프트 요약 |

## 기존 문서 정리 예정
- 기존 `docs/windows-powershell-codex-install-guide.md` 문서는 이후 `codex-01-setup.md`로 옮기고, UTF-8 인코딩과 문서 구조를 정리한다.
