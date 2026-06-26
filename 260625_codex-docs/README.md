# AI Agent 작업 워크스페이스

## 목적
이 워크스페이스는 AI Agent를 활용한 개발 작업 방식, 도구 사용법, 계획 기록, 템플릿, 참고 자료를 관리하기 위한 공간이다.

루트 README는 워크스페이스 전체의 첫 진입 문서로 사용한다. 문서 체계의 세부 구조와 하위 폴더별 설명은 `docs/README.md`에서 확인한다.

## 현재 구조
```text
.
├── README.md
├── AGENTS.md
└── docs/
```

- `README.md`: 워크스페이스 전체의 사용자용 입구 문서
- `AGENTS.md`: 워크스페이스 전체에 적용되는 AI Agent 지침
- `docs/`: AI Agent 작업 방식, 도구 매뉴얼, 계획 기록, 템플릿, 참고 자료를 관리하는 문서 폴더

## 먼저 볼 문서
| 목적 | 문서 |
|---|---|
| 문서 전체 목차 | `docs/README.md` |
| 전체 작성 지침 | `AGENTS.md` |
| docs 작성 지침 | `docs/AGENTS.md` |
| AI Agent 방법론 | `docs/guides/README.md` |
| 도구별 CLI 매뉴얼 | `docs/tools/README.md` |

## 지침 적용 순서
AI Agent가 문서를 작성하거나 수정할 때는 Top -> Down 순서로 지침을 적용한다.

```text
AGENTS.md
  -> docs/AGENTS.md
      -> docs/guides/AGENTS.md
      -> docs/tools/AGENTS.md
```

상위 지침은 공통 원칙을 정의하고, 하위 지침은 자기 폴더의 작성 규칙만 담당한다.

## 작업 원칙
- 문서는 UTF-8 인코딩으로 저장하고 한글 깨짐 여부를 확인한다.
- 계획은 사용자가 요청하거나 최종 승인 후 확인한 경우 `docs/plans`에 저장한다.
- AI Agent 사용 방법론과 철학은 `docs/guides`에 둔다.
- Codex CLI, Claude Code CLI 같은 도구별 사용법은 `docs/tools`에 둔다.
- 여러 문서 부류에서 공통으로 반복 사용할 문서 형식은 `docs/templates`에 둔다.
- 공식 문서, 외부 자료, LLM wiki, 논문, GitHub 저장소 참고 자료는 `docs/refs`에 둔다.

## 현재 상태
- `docs` 문서 체계는 초기 구성 중이다.
- 기존 설치 문서 `docs/windows-powershell-codex-install-guide.md`는 아직 정리 전 상태로 남아 있다.
