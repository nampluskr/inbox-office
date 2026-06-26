# AI Agent 도구별 CLI 매뉴얼

## 문서 목적
이 폴더는 Codex CLI, Claude Code CLI 같은 AI Agent 도구를 실제 작업 중 수시로 참고하기 위한 매뉴얼을 모은다.

이 폴더는 명령어, 설정, 상황별 절차, 문제 해결을 빠르게 확인하는 실전 참고 문서에 집중한다.

## 대상 독자
- VS Code Extension 또는 Codex 앱 대화창을 사용해 본 경험이 있는 사용자
- 외부 터미널에서 AI Agent CLI를 직접 실행하려는 사용자
- Python 수치해석, 딥러닝, C++ 알고리즘 작업에 AI Agent CLI를 활용하려는 사용자

## 폴더 구조
```text
docs/tools/
  README.md
  AGENTS.md

  codex/
    README.md

  claude/
    README.md
```

## 도구별 문서 위치
| 위치 | 역할 |
|---|---|
| `docs/tools/codex` | Codex CLI 설치, 실행, 권한, 세션, Git 리뷰, 문제 해결 매뉴얼 |
| `docs/tools/claude` | Claude Code CLI 설치, 실행, 권한, 세션, Git 리뷰, 문제 해결 매뉴얼 |
| `docs/tools/TEMPLATE.md` | 도구별 매뉴얼 문서 작성 템플릿 |

## 권장 문서 구성
도구별 폴더는 다음 문서 흐름을 기본으로 한다.

| 순서 | 문서 주제 | 내용 |
|---:|---|---|
| 01 | setup | 설치, PATH, 버전 확인 |
| 02 | quickstart | 첫 실행, 로그인, 첫 작업 |
| 03 | interface-modes | 웹, 앱, IDE, 앱 내부 터미널, 외부 터미널 CLI 차이 |
| 04 | command-reference | 자주 쓰는 명령과 옵션 |
| 05 | project-workflow | 프로젝트 폴더에서 실제 작업하는 기본 흐름 |
| 06 | permissions-safety | 권한, 승인, sandbox, 위험 작업 제어 |
| 07 | session-management | 세션, resume, memory, context 관리 |
| 08 | git-review-workflow | Git 상태 확인, diff, review, 커밋 전 점검 |
| 09 | troubleshooting | 설치, 로그인, 권한, 터미널, 인코딩 문제 해결 |
| 10 | cheatsheet | 자주 쓰는 명령과 상황별 요청 예시 |

## 작성 원칙
- 개념 설명은 짧게 쓰고, 실제 명령과 절차를 먼저 보여준다.
- Windows PowerShell 사용자를 기본 독자로 가정하되, 필요하면 macOS/Linux 차이를 별도 항목으로 둔다.
- 문서마다 "언제 보는 문서인가"와 "빠른 결론"을 앞부분에 둔다.
- 문제 해결 문서는 증상, 원인, 해결 방법을 표로 정리한다.
- 도구별 차이가 중요한 경우, 해당 도구 폴더 안에서 차이를 설명한다.
