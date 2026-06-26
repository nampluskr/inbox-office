# docs 작성 지침

## 적용 범위
- 이 파일은 `docs` 아래의 모든 문서에 적용한다.
- 저장소 전체 규칙은 루트 `AGENTS.md`를 따른다.
- 하위 폴더에 더 구체적인 `AGENTS.md`가 있으면 해당 지침을 함께 따른다.

## 지침 계층
문서 작성 지침은 Top -> Down 순서로 적용한다.

```text
AGENTS.md
  -> docs/AGENTS.md
      -> docs/guides/AGENTS.md
      -> docs/tools/AGENTS.md
```

상위 지침은 공통 원칙을 정의하고, 하위 지침은 자기 폴더의 문서 성격과 작성 규칙만 정의한다.

## README와 AGENTS 역할 구분
- `README.md`는 사람이 읽는 안내 문서다.
- `AGENTS.md`는 AI Agent가 따르는 작성 지침이다.
- 하위 폴더의 README와 AGENTS에는 해당 폴더의 내용과 규칙만 담는다.
- `docs` 전체 구조, 하위 폴더 역할, 공통 작성 원칙은 `docs/README.md`와 `docs/AGENTS.md`에서 관리한다.

## docs 하위 폴더 역할
| 폴더 | 작성 성격 |
|---|---|
| `docs/guides` | AI Agent 작업 방식과 철학을 다루는 학습형 문서 |
| `docs/tools` | 도구별 CLI 사용법을 다루는 실전 매뉴얼 |
| `docs/plans` | 확정되었거나 저장 요청된 계획 문서 |
| `docs/templates` | 여러 문서 부류에서 공통으로 사용할 범용 템플릿 |
| `docs/refs` | 참고 자료, 외부 문서 요약, LLM wiki, 논문, 저장소 링크 |

## 공통 작성 원칙
- 문서는 UTF-8 인코딩으로 저장하고 한글 깨짐 여부를 확인한다.
- 각 문서는 자신의 폴더 역할에 맞는 범위만 다룬다.
- 상위 폴더 구조 설명을 하위 폴더 문서에 반복하지 않는다.
- 특정 도구 명령어는 `docs/tools`에 작성하고, 방법론과 철학은 `docs/guides`에 작성한다.
- 폴더 전용 문서 형식은 해당 폴더의 `TEMPLATE.md`에 둔다.
- 여러 문서 부류에서 공통으로 반복 사용할 형식은 `docs/templates`에 둔다.
- 외부 자료 요약과 원문 링크는 `docs/refs`에 정리한다.

## Obsidian 호환 작성 규칙
- `docs` 폴더는 Obsidian Vault로 열어 읽기, Graph View 확인, 검색, 백링크 확인, 직접 수정/편집에 사용할 수 있다.
- Obsidian에서 문서를 수정할 수 있으므로, AI Agent는 작업 전후에 최신 파일 내용과 변경 상태를 확인한다.
- Obsidian 전용 문법보다 GitHub와 일반 Markdown 뷰어에서도 읽히는 표준 Markdown을 우선 사용한다.
- 문서 간 링크는 기본적으로 `[문서 제목](상대/경로.md)` 형식을 사용한다.
- Obsidian 전용 `[[wikilink]]`는 필요한 경우에만 보조적으로 사용하고, 기본 링크로 사용하지 않는다.
- 각 폴더의 `README.md`는 Obsidian에서 MOC(Map of Content) 역할을 한다.
- 새 문서를 추가할 때는 관련 README에 링크를 추가할지 검토한다.
- 주요 문서에는 가능한 한 YAML frontmatter를 둔다.

권장 frontmatter 형식은 다음과 같다.

```yaml
---
type: guide
status: draft
tags: [ai-agent, guide]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

허용 태그는 필요 이상으로 늘리지 않고 다음 목록을 우선 사용한다.

- `ai-agent`
- `guide`
- `tool`
- `plan`
- `template`
- `ref`
- `llm-wiki`
- `obsidian`

## 동기화 규칙
- `docs` 전체 하위 폴더 구조가 바뀌면 `docs/README.md`를 함께 확인한다.
- `docs` 공통 작성 원칙이 바뀌면 `docs/AGENTS.md`를 업데이트한다.
- `docs/guides` 구조나 문서 목록이 바뀌면 `docs/guides/README.md`와 `docs/guides/AGENTS.md`를 확인한다.
- `docs/tools` 구조나 도구별 문서 목록이 바뀌면 `docs/tools/README.md`와 `docs/tools/AGENTS.md`를 확인한다.
- 새 계획이 승인되어 저장 요청을 받으면 루트 `AGENTS.md`의 PLAN 저장 규칙을 따른다.

## 품질 확인
- 신규 또는 수정된 Markdown 파일은 UTF-8 엄격 디코딩으로 확인한다.
- 한글 깨짐 대체 문자가 없는지 확인한다.
- README와 AGENTS의 역할이 섞이지 않았는지 확인한다.
- 링크와 상대 경로가 실제 파일 구조와 맞는지 확인한다.
- frontmatter가 있는 문서는 YAML 구문이 깨지지 않았는지 확인한다.
- Obsidian Graph View 연결을 위해 주요 문서에 관련 문서 링크가 있는지 확인한다.
