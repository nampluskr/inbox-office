# Codex Instruction Management Structure

## 1. 문서 목적

이 문서는 Codex에서 반복적으로 사용하는 지침, 재사용 워크플로우, 실행 정책을 어떤 파일과 폴더에 나누어 관리할지 설명한다.

기존에는 `AGENTS.md` 파일 하나에 모든 지침을 작성하는 방식으로 시작할 수 있다. 그러나 프로젝트 수가 늘어나거나, 문서 작성 규칙, 코딩 규칙, 검증 절차, 반복 명령, 도구 사용 방식이 많아지면 단일 파일만으로는 관리가 어려워진다.

이 문서는 다음 구성 요소의 역할을 구분한다.

- `AGENTS.md`
- `AGENTS.override.md`
- `.agents/skills`
- `.codex/config.toml`
- `.codex/rules`
- deprecated custom prompts

## 2. 기존 AGENTS.md 단일 파일 방식의 한계

`AGENTS.md` 하나만 사용하는 방식은 단순하고 시작하기 쉽다. 프로젝트 전체에 항상 적용할 규칙을 적어 두면 Codex가 작업 시작 시 해당 내용을 읽고 따를 수 있다.

다만 다음과 같은 경우에는 단일 파일 방식이 한계에 도달한다.

- 문서 작성 규칙과 코딩 규칙이 길어지는 경우
- 특정 작업 절차를 반복적으로 호출해야 하는 경우
- 하위 폴더별로 서로 다른 규칙이 필요한 경우
- Codex 실행 설정과 작업 지침이 한 파일에 섞이는 경우
- 샌드박스 밖 명령 승인 정책까지 함께 관리하려는 경우
- 여러 프로젝트에서 공통 워크플로우를 재사용해야 하는 경우

이때는 `AGENTS.md`를 최상위 지침으로 유지하되, 세부 작업 절차는 `.agents/skills`, 실행 설정은 `.codex`, 참고 문서는 별도 references 폴더로 분리하는 것이 좋다.

## 3. Codex 지침 관리 구성 요소 개요

Codex 지침 관리는 하나의 파일이 아니라 여러 계층으로 구성된다.

| 구성 요소 | 목적 | 대표 위치 |
|---|---|---|
| `AGENTS.md` | 프로젝트 또는 폴더 단위의 지속 지침 | repository root 또는 하위 폴더 |
| `AGENTS.override.md` | 같은 위치의 `AGENTS.md`보다 우선하는 override 지침 | repository root 또는 하위 폴더 |
| `.agents/skills` | 재사용 가능한 작업 절차와 도메인 지식 | project `.agents/skills` |
| `.codex/config.toml` | Codex 실행 설정 | project `.codex/config.toml` 또는 user config |
| `.codex/rules/*.rules` | 샌드박스 밖 명령 실행 승인 정책 | project `.codex/rules` 또는 user rules |
| `~/.codex/prompts` | deprecated custom prompts | user Codex home |

중요한 구분은 다음과 같다.

- 행동 지침은 `AGENTS.md`에 둔다.
- 반복 작업 절차는 skill로 둔다.
- Codex 실행 설정은 `.codex/config.toml`에 둔다.
- 명령 실행 승인 정책은 `.codex/rules`에 둔다.
- 일반 문서 작성 규칙 파일을 `.codex/rules`에 두지 않는다.

## 4. AGENTS.md 기본 구조와 사용 범위

`AGENTS.md`는 Codex가 작업 시작 시 읽는 기본 프로젝트 지침 파일이다.

주로 다음 내용을 작성한다.

- 프로젝트 목적
- 작업 방식
- 코딩 스타일
- 문서 작성 원칙
- 테스트 및 검증 명령
- 금지 사항
- 산출물 저장 위치
- 사용자와의 협업 방식

예시 구조는 다음과 같다.

```md
# AGENTS.md

## 프로젝트 목적

이 저장소의 목적과 주요 산출물을 설명한다.

## 작업 원칙

- 변경 범위를 작게 유지한다.
- 기존 구조와 스타일을 우선 따른다.
- 불확실한 외부 정보는 확인 후 사용한다.

## 코딩 규칙

- 공통 유틸리티는 중복 구현하지 않는다.
- 테스트 가능한 단위로 작성한다.

## 문서 규칙

- Markdown 문서는 UTF-8로 작성한다.
- 산출물과 참고 문서를 구분한다.

## 검증

- 변경 후 필요한 테스트 또는 확인 명령을 실행한다.
```

`AGENTS.md`는 일반적으로 짧고 핵심적인 내용을 담는 것이 좋다. 너무 많은 세부 절차를 넣으면 Codex가 매번 불필요한 지침을 읽게 되고, 파일 유지보수도 어려워진다.

## 5. AGENTS.override.md의 역할과 사용 시점

`AGENTS.override.md`는 같은 디렉터리의 `AGENTS.md`보다 우선 적용되는 지침 파일이다.

사용 시점은 제한적으로 잡는 것이 좋다.

- 임시로 기존 지침을 대체해야 하는 경우
- 특정 하위 폴더에서 상위 규칙을 강하게 덮어써야 하는 경우
- 실험 브랜치나 특수 작업에서 다른 검증 명령을 사용해야 하는 경우

일반적인 프로젝트 지침은 `AGENTS.md`에 두고, `AGENTS.override.md`는 특별한 상황에서만 사용한다.

권장하지 않는 사용 방식은 다음과 같다.

- 루트에 항상 `AGENTS.override.md`만 두고 `AGENTS.md`를 비워 두는 방식
- 임시 지침을 제거하지 않고 장기간 방치하는 방식
- override 파일에 프로젝트 전체 지침과 개인 작업 메모를 섞는 방식

## 6. 전역 지침과 프로젝트 지침의 차이

Codex 지침은 전역 지침과 프로젝트 지침으로 나뉜다.

전역 지침은 사용자 환경 전체에 적용된다.

```text
~/.codex/AGENTS.md
~/.codex/AGENTS.override.md
```

프로젝트 지침은 특정 저장소 또는 폴더에 적용된다.

```text
project-root/AGENTS.md
project-root/subdir/AGENTS.md
```

일반적으로 다음 기준으로 나눈다.

| 지침 유형 | 권장 위치 |
|---|---|
| 개인 응답 선호, 항상 지킬 작업 습관 | `~/.codex/AGENTS.md` |
| 특정 저장소의 빌드, 테스트, 문서 규칙 | project `AGENTS.md` |
| 특정 모듈 또는 하위 서비스 전용 규칙 | 하위 폴더 `AGENTS.md` |
| 임시 override | `AGENTS.override.md` |

전역 지침에는 모든 프로젝트에 공통으로 적용해도 무리가 없는 내용만 둔다. 프로젝트 고유의 빌드 명령, 폴더 구조, 도메인 규칙은 프로젝트 `AGENTS.md`에 둔다.

## 7. 하위 폴더별 AGENTS.md 구성 방식

Codex는 프로젝트 루트에서 현재 작업 디렉터리까지의 지침 파일을 계층적으로 읽는다. 따라서 하위 폴더에 `AGENTS.md`를 두면 해당 폴더에서 작업할 때 더 구체적인 지침을 줄 수 있다.

예시:

```text
project-root/
├─ AGENTS.md
├─ docs/
│  └─ AGENTS.md
├─ src/
│  └─ AGENTS.md
└─ tests/
   └─ AGENTS.md
```

하위 폴더별 지침 예시는 다음과 같다.

- `docs/AGENTS.md`: 문서 톤, 파일명 규칙, 목차 형식, 그림 저장 방식
- `src/AGENTS.md`: 코드 스타일, 모듈 분리 방식, 타입 힌트, 테스트 기준
- `tests/AGENTS.md`: 테스트 파일명, fixture 관리, 실행 명령

하위 지침은 상위 지침을 반복해서 복사하지 않는다. 상위 지침과 달라지는 내용 또는 더 구체적인 내용만 작성한다.

## 8. .agents 폴더 개요

`.agents` 폴더는 Codex가 사용할 수 있는 repo-scoped agent assets를 두는 위치로 사용할 수 있다. 특히 공식적으로 중요한 하위 구조는 `.agents/skills`이다.

```text
project-root/
└─ .agents/
   └─ skills/
      └─ skill-name/
         └─ SKILL.md
```

`.agents`는 다음 목적에 적합하다.

- 반복 작업 절차 정의
- 특정 도메인 작업 방식 패키징
- 문서 작성, 코드 구현, 리뷰, 분석 등 재사용 workflow 구성
- 프로젝트 내부에서 공유할 Codex skill 관리

반대로 다음 내용은 `.agents`에 두는 것이 적합하지 않다.

- 일반 산출 문서
- 실행 결과물
- 데이터 파일
- Codex 실행 권한 정책
- 단순 개인 메모

## 9. .agents/skills 구조

Skill은 하나의 디렉터리이며, 그 안에 `SKILL.md`가 있어야 한다.

기본 구조:

```text
.agents/
└─ skills/
   ├─ write-docs/
   │  └─ SKILL.md
   ├─ implement-feature/
   │  └─ SKILL.md
   └─ review-changes/
      └─ SKILL.md
```

필요하면 skill 내부에 `references`, `scripts`, `templates`, `assets` 같은 보조 폴더를 둘 수 있다.

```text
.agents/skills/write-docs/
├─ SKILL.md
├─ references/
│  └─ style-guide.md
├─ templates/
│  └─ design-doc-template.md
└─ scripts/
   └─ validate-docs.ps1
```

Skill은 다음과 같은 반복 작업에 적합하다.

- 특정 형식의 문서 작성
- 리뷰 체크리스트 수행
- 릴리스 노트 생성
- 데이터 분석 절차 실행
- 코드 마이그레이션 절차
- 특정 프레임워크 사용 방식

## 10. SKILL.md 작성 방식

`SKILL.md`는 YAML front matter와 본문 지침으로 구성한다.

기본 예시:

```md
---
name: write-docs
description: Use when creating or revising project documentation with the shared documentation rules.
---

# Write Docs Skill

## When To Use

Use this skill when the user asks to create, revise, restructure, or review documentation.

## Instructions

1. Read the relevant project guidance first.
2. Identify the target audience and document purpose.
3. Use the standard document structure unless the user requests otherwise.
4. Keep generated Markdown in UTF-8.
5. Do not add unrelated implementation details.

## Output

Return the created or modified document path and a concise summary of changes.
```

`name`은 짧고 명확해야 한다. `description`은 Codex가 언제 이 skill을 사용할지 판단하는 핵심 기준이므로 구체적으로 작성한다.

좋은 description의 특징은 다음과 같다.

- 어떤 요청에서 사용해야 하는지 분명하다.
- 사용하지 말아야 할 범위가 암시되거나 명시되어 있다.
- 핵심 키워드가 앞쪽에 있다.
- 너무 포괄적이지 않다.

좋지 않은 예:

```text
Helps with work.
```

좋은 예:

```text
Use when writing Markdown documentation that must follow the shared project documentation rules and template structure.
```

## 11. Skills 호출 방식

Skill은 명시적으로 호출하거나, Codex가 설명을 보고 암시적으로 선택할 수 있다.

명시 호출은 사용자가 skill 이름을 직접 언급하는 방식이다.

```text
$write-docs를 사용해서 문서 초안을 작성해 주세요.
```

암시 호출은 사용자 요청이 skill의 `description`과 맞을 때 Codex가 스스로 선택하는 방식이다.

예를 들어 `write-docs` skill의 description이 문서 작성 요청에 맞게 작성되어 있다면, 사용자가 단순히 “이 주제로 문서를 작성해 주세요”라고 말해도 Codex가 해당 skill을 사용할 수 있다.

명시 호출이 필요한 경우:

- 비슷한 skill이 여러 개 있는 경우
- 특정 workflow를 반드시 적용해야 하는 경우
- 사용자 또는 팀이 표준 작업 절차를 강제하고 싶은 경우

암시 호출이 유용한 경우:

- 반복 작업을 자연스럽게 자동화하고 싶은 경우
- 사용자가 매번 skill 이름을 기억하지 않아도 되게 하고 싶은 경우

## 12. .agents 폴더 사용 시 권장 패턴

`.agents`는 재사용 workflow를 담는 위치로 유지한다.

권장 패턴:

- skill 하나는 하나의 명확한 작업 목적만 가진다.
- 긴 참고 내용은 `SKILL.md`에 모두 넣지 말고 `references`로 분리한다.
- 반복 가능한 검증은 `scripts`로 분리한다.
- 문서나 코드 템플릿은 `templates`에 둔다.
- 프로젝트 전체 지침은 skill에 중복하지 않고 `AGENTS.md`를 참조한다.

예시:

```text
.agents/
└─ skills/
   ├─ write-docs/
   │  ├─ SKILL.md
   │  └─ templates/
   │     └─ standard-doc.md
   ├─ code-review/
   │  ├─ SKILL.md
   │  └─ references/
   │     └─ review-checklist.md
   └─ run-analysis/
      ├─ SKILL.md
      └─ scripts/
         └─ run-analysis.ps1
```

피해야 할 패턴:

- 모든 규칙을 하나의 거대한 skill에 넣는 방식
- `AGENTS.md`와 skill에 같은 내용을 반복해서 쓰는 방식
- 사용자 개인 메모를 repo skill에 넣는 방식
- 실행 결과물을 `.agents` 아래에 저장하는 방식

## 13. .codex 폴더 개요

`.codex` 폴더는 Codex 실행 설정과 권한 정책을 프로젝트 단위로 관리할 때 사용한다.

대표 구조:

```text
project-root/
└─ .codex/
   ├─ config.toml
   └─ rules/
      └─ default.rules
```

`.codex`는 다음 목적에 적합하다.

- 프로젝트별 Codex 설정 관리
- sandbox, model, approval 관련 설정 관리
- MCP 서버 설정 관리
- hooks 설정 관리
- 명령 실행 승인 정책 관리

일반 문서 작성 규칙이나 코딩 스타일 문서를 `.codex`에 두는 것은 권장하지 않는다. 그런 내용은 `AGENTS.md`, `.agents/skills`, 또는 별도 references 문서에 둔다.

## 14. .codex/config.toml 구조

`config.toml`은 Codex의 실행 설정을 관리하는 파일이다.

예시:

```toml
# .codex/config.toml

model = "gpt-5-codex"
reasoning_effort = "medium"

[tools]
web_search = true

[sandbox]
mode = "workspace-write"
```

실제 설정 키는 사용하는 Codex 버전과 환경에 따라 달라질 수 있다. 따라서 `config.toml`을 작성할 때는 현재 Codex 공식 문서 또는 현재 환경의 예시를 확인해야 한다.

`config.toml`에 둘 수 있는 성격의 내용:

- 모델 기본값
- reasoning 관련 기본값
- sandbox 설정
- approval 설정
- MCP 서버 설정
- hooks 설정
- 프로젝트 instruction discovery 관련 설정

`config.toml`에 두지 말아야 할 내용:

- 문서 작성 스타일 가이드 본문
- 코딩 컨벤션 설명문
- 프로젝트 도메인 지식
- 분석 절차 설명
- 대량의 Markdown 문서

이런 내용은 `AGENTS.md` 또는 skill/reference 문서에 둔다.

## 15. .codex/rules 구조

`.codex/rules`는 Codex가 샌드박스 밖에서 명령을 실행할 때 어떤 명령을 허용, 차단, 승인 요청할지 정의하는 위치이다.

예시 구조:

```text
.codex/
└─ rules/
   └─ default.rules
```

`.rules` 파일은 일반 Markdown이 아니라 Starlark 형식의 정책 파일이다.

예시:

```python
prefix_rule(
    pattern = ["gh", "pr", "view"],
    decision = "prompt",
    justification = "Viewing PRs is allowed with approval",
    match = [
        "gh pr view 123",
    ],
    not_match = [
        "gh pr list",
    ],
)
```

`decision`은 보통 다음 중 하나를 사용한다.

| decision | 의미 |
|---|---|
| `allow` | 일치하는 명령을 승인 없이 허용 |
| `prompt` | 실행 전 사용자 승인 요청 |
| `forbidden` | 실행 차단 |

중요한 점은 `.codex/rules`가 문서 규칙 폴더가 아니라는 것이다. `docs-rules.md`, `coding-rules.md` 같은 파일은 이 위치에 두지 않는다.

## 16. .codex 폴더 사용 시 권장 패턴

권장 패턴:

- `.codex/config.toml`에는 실행 설정만 둔다.
- `.codex/rules/*.rules`에는 명령 승인 정책만 둔다.
- 민감 정보나 토큰을 저장하지 않는다.
- 프로젝트에 체크인해도 되는 설정인지 확인한다.
- 팀 전체에 영향을 주는 설정은 변경 전 합의한다.

피해야 할 패턴:

- `.codex`에 일반 문서나 산출물을 저장하는 방식
- `.codex/rules`를 문서 규칙 저장소처럼 사용하는 방식
- 너무 넓은 명령 허용 규칙을 추가하는 방식
- destructive command를 쉽게 허용하는 방식
- 개인 로컬 환경에만 맞는 설정을 프로젝트에 커밋하는 방식

명령 승인 규칙은 최소 권한 원칙에 맞게 작성한다. 예를 들어 `git` 전체를 허용하기보다 필요한 하위 명령 prefix만 좁게 허용한다.

## 17. AGENTS.md, .agents, .codex의 역할 구분

세 구성 요소는 서로 대체 관계가 아니라 보완 관계이다.

| 구분 | 주 역할 | 넣을 내용 | 넣지 않을 내용 |
|---|---|---|---|
| `AGENTS.md` | 지속 지침 | 프로젝트 원칙, 작업 규칙, 검증 기준 | 긴 반복 workflow 전체 |
| `.agents/skills` | 재사용 workflow | 특정 작업 절차, 도메인별 수행 방법 | 일반 실행 권한 정책 |
| `.codex/config.toml` | Codex 실행 설정 | 모델, sandbox, MCP, hooks 설정 | 문서 스타일 가이드 |
| `.codex/rules` | 명령 승인 정책 | allow, prompt, forbidden command rules | Markdown 작성 규칙 |
| references 문서 | 사람이 읽는 설명 | 상세 가이드, 배경 지식, 표준 문서 | Codex가 자동 적용해야 할 핵심 지침 |

간단히 정리하면 다음과 같다.

- “항상 이렇게 행동하라”는 `AGENTS.md`
- “이 작업을 반복 가능하게 수행하라”는 `.agents/skills`
- “Codex 실행 환경을 이렇게 설정하라”는 `.codex/config.toml`
- “이 명령은 승인 없이 실행해도 되는가”는 `.codex/rules`
- “자세한 설명과 참고 자료”는 references 문서

## 18. 권장 공통 폴더 구조

일반적인 권장 구조는 다음과 같다.

```text
project-root/
├─ AGENTS.md
├─ .agents/
│  └─ skills/
│     ├─ write-docs/
│     │  ├─ SKILL.md
│     │  └─ templates/
│     └─ code-review/
│        ├─ SKILL.md
│        └─ references/
├─ .codex/
│  ├─ config.toml
│  └─ rules/
│     └─ default.rules
├─ docs/
├─ src/
├─ tests/
└─ references/
```

모든 프로젝트가 이 구조를 전부 가질 필요는 없다. 필요한 구성 요소만 단계적으로 도입한다.

최소 구조:

```text
project-root/
└─ AGENTS.md
```

반복 workflow가 생겼을 때:

```text
project-root/
├─ AGENTS.md
└─ .agents/
   └─ skills/
      └─ write-docs/
         └─ SKILL.md
```

Codex 실행 설정까지 필요할 때:

```text
project-root/
├─ AGENTS.md
├─ .agents/
│  └─ skills/
└─ .codex/
   └─ config.toml
```

명령 승인 정책까지 필요할 때:

```text
project-root/
├─ AGENTS.md
├─ .agents/
│  └─ skills/
└─ .codex/
   ├─ config.toml
   └─ rules/
      └─ default.rules
```

## 19. 단계별 도입 전략

처음부터 모든 구조를 만들 필요는 없다. 다음 순서로 도입하는 것이 좋다.

1. `AGENTS.md` 작성

   프로젝트 전체에서 항상 지킬 최소 지침을 작성한다.

2. 세부 규칙 분리

   문서 작성 규칙, 코딩 규칙, 리뷰 체크리스트가 길어지면 별도 reference 문서로 분리하고 `AGENTS.md`에서 참조한다.

3. 반복 작업을 skill로 전환

   같은 작업 절차를 여러 번 수행하게 되면 `.agents/skills/<skill-name>/SKILL.md`로 만든다.

4. 하위 폴더별 지침 추가

   `docs`, `src`, `tests`처럼 성격이 다른 폴더에 별도 규칙이 필요하면 하위 `AGENTS.md`를 둔다.

5. Codex 실행 설정 도입

   프로젝트별 모델, sandbox, MCP, hooks 설정이 필요할 때 `.codex/config.toml`을 추가한다.

6. 명령 승인 정책 도입

   반복적으로 승인하는 안전한 명령이 있거나, 반드시 금지해야 할 명령이 있으면 `.codex/rules/*.rules`를 추가한다.

## 20. 주의사항과 안티패턴

주의사항:

- `AGENTS.md`는 Codex가 자동으로 읽는 핵심 지침이므로 너무 장황하게 만들지 않는다.
- 세부 설명은 references 문서나 skill references로 분리한다.
- skill description은 Codex가 선택할 수 있도록 구체적으로 작성한다.
- `.codex/rules`는 Markdown 규칙 문서 위치가 아니다.
- project `.codex` 설정은 해당 프로젝트에서 신뢰 가능한 설정인지 확인한다.
- token, password, API key 같은 민감 정보는 지침 파일이나 설정 파일에 저장하지 않는다.

안티패턴:

- 모든 내용을 `AGENTS.md` 하나에 계속 누적하는 방식
- 모든 반복 작업을 custom prompt로만 관리하는 방식
- `.codex/rules`에 문서 작성 규칙을 저장하는 방식
- 너무 넓은 command allow rule을 추가하는 방식
- skill 하나가 문서 작성, 코딩, 리뷰, 배포를 모두 담당하게 만드는 방식
- 전역 지침에 특정 프로젝트 고유 규칙을 넣는 방식

## 21. Deprecated Custom Prompts

Codex에는 과거 custom prompts 기능이 있었다. Markdown 파일을 `~/.codex/prompts`에 두고 slash command처럼 호출하는 방식이다.

예시:

```text
~/.codex/prompts/draftpr.md
```

하지만 공식적으로 custom prompts는 deprecated로 안내된다. 새로 만드는 반복 workflow는 custom prompt보다 skill로 작성하는 것이 좋다.

custom prompts를 계속 사용할 수 있는 경우:

- 기존 개인 환경에 이미 있는 간단한 slash command를 유지하는 경우
- repo에 공유할 필요가 없는 개인용 짧은 prompt인 경우
- skill로 이전하기 전 임시로 사용하는 경우

새로 작성하는 표준 workflow라면 다음을 우선한다.

```text
.agents/skills/<skill-name>/SKILL.md
```

## 22. 참고 기준

이 문서는 Codex 공식 매뉴얼의 다음 주제를 기준으로 정리한다.

- Custom instructions with `AGENTS.md`
- Agent Skills
- Customization
- Rules
- Custom Prompts
- Configuration Reference
- Advanced Configuration

공식 문서의 세부 설정명과 지원 범위는 Codex 버전과 실행 환경에 따라 달라질 수 있으므로, 실제 설정 파일을 작성할 때는 현재 사용 중인 Codex 환경의 최신 문서를 확인한다.
