# docs 문서 체계

## 문서 목적
이 폴더는 AI Agent를 활용한 개발 작업, 도구 사용법, 계획 기록, 템플릿, 참고 자료를 체계적으로 관리한다.

`docs`는 단순한 설명 문서 모음이 아니라, AI Agent와 함께 작업하기 위한 개인 작업 매뉴얼이자 지식 베이스다.

## 하위 폴더 구조
```text
docs/
  README.md
  AGENTS.md

  guides/
  tools/
  plans/
  templates/
  refs/
```

## 하위 폴더 역할
| 폴더 | 역할 |
|---|---|
| `docs/guides` | AI Agent 작업 방식, 철학, 방법론을 설명하는 학습형 가이드 |
| `docs/tools` | Codex CLI, Claude Code CLI 같은 도구별 실전 매뉴얼 |
| `docs/plans` | 승인되었거나 저장 요청된 계획 문서 |
| `docs/templates` | 여러 문서 부류에서 공통으로 사용할 범용 템플릿 |
| `docs/refs` | 공식 문서, 외부 자료, 논문, LLM wiki, GitHub 저장소 참고 자료 |

## 현재 단일 문서
| 문서 | 상태 |
|---|---|
| `docs/windows-powershell-codex-install-guide.md` | 기존 Codex 설치 문서. 이번 구조 정리에서는 이동하거나 수정하지 않는다. |

## 읽는 순서
1. AI Agent와 함께 일하는 사고방식을 익히려면 `docs/guides`를 읽는다.
2. 특정 도구를 실제로 사용할 때는 `docs/tools`를 참고한다.
3. 저장된 작업 계획과 의사결정 기록은 `docs/plans`에서 확인한다.
4. 새 가이드나 도구 매뉴얼을 작성할 때는 해당 폴더의 `TEMPLATE.md`를 참고한다.
5. 여러 문서 부류에서 공통으로 쓰는 템플릿은 `docs/templates`에서 확인한다.
6. 외부 자료와 개인 지식 베이스는 `docs/refs`에 정리한다.

## Obsidian 사용
`docs` 폴더는 Obsidian Vault로 열어 읽고 관리할 수 있다. 기존 Vault 안에서 `docs` 폴더를 관리해도 되고, `docs` 폴더 자체를 Vault로 열어도 된다.

Obsidian에서는 다음 용도로 이 문서 체계를 활용한다.

- 읽기 모드로 가이드와 매뉴얼을 확인한다.
- Graph View로 문서 간 연결을 확인한다.
- 검색과 백링크로 관련 문서를 찾아본다.
- 문서를 직접 수정하거나 편집한다.
- Obsidian에서 수정한 뒤 Git diff로 변경 내용을 확인한다.

각 폴더의 `README.md`는 Obsidian에서 MOC(Map of Content) 역할을 한다. 새 문서를 추가할 때는 관련 README에 링크를 추가할지 함께 검토한다.

## README와 AGENTS의 역할
| 파일 | 역할 |
|---|---|
| `README.md` | 사람이 읽는 안내 문서 |
| `AGENTS.md` | AI Agent가 따라야 할 작성 지침 |

각 하위 폴더의 README와 AGENTS는 해당 폴더 안의 내용만 설명한다. `docs` 전체 구조와 공통 원칙은 이 폴더의 `README.md`와 `AGENTS.md`에서 관리한다.

## 관련 지침
- 루트 지침: `AGENTS.md`
- docs 공통 지침: `docs/AGENTS.md`
- guides 작성 지침: `docs/guides/AGENTS.md`
- tools 작성 지침: `docs/tools/AGENTS.md`
