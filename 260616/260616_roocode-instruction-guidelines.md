# RooCode Instruction Guidelines

## 1. 문서 목적

이 문서는 RooCode에서 반복적으로 사용하는 지침, 규칙, mode, skill, slash command, ignore 정책, MCP 설정, auto-approve 정책을 어떤 파일과 폴더에 나누어 관리할지 설명한다.

RooCode는 Claude Code나 Codex와 유사하게 프로젝트별 지침을 둘 수 있지만, 중심 구조는 `.roo` 폴더와 mode 기반 규칙이다. 따라서 단일 지침 파일만 사용하는 방식보다 `.roo/rules`, `.roo/skills`, `.roo/commands`, `.roomodes`, `.rooignore`, `.roo/mcp.json`을 목적별로 분리하는 것이 좋다.

이 문서는 다음 구성 요소의 역할을 구분한다.

- `AGENTS.md`
- `AGENT.md`
- `.roo/rules`
- `.roo/rules-{modeSlug}`
- `.roorules`
- `.roorules-{modeSlug}`
- `.roo/skills`
- `.roo/skills-{modeSlug}`
- `.agents/skills`
- `.roo/commands`
- `.roomodes`
- `.rooignore`
- `.roo/mcp.json`
- auto-approve settings
- command allowlist and denylist

## 2. RooCode 상태와 문서 기준 시점

RooCode 관련 기능은 사용하는 배포판, 확장 버전, 문서 시점에 따라 차이가 있을 수 있다. 따라서 실제 프로젝트에 적용하기 전에는 현재 사용 중인 RooCode 환경과 공식 문서를 확인해야 한다.

공식 문서에 extension 유지보수 상태, 기능 변경, deprecation 정보가 표시될 수 있으므로 문서 작성 시 다음 정보를 함께 확인한다.

- 현재 사용 중인 RooCode 버전
- 공식 문서의 최신 업데이트 상태
- VS Code extension 설정 항목의 실제 이름
- workspace settings와 user settings의 적용 범위
- mode, skill, command 기능의 현재 지원 여부

이 문서는 특정 프로젝트에 묶이지 않는 공통 지침 관리 구조를 설명한다.

## 3. 기존 단일 AGENTS.md 또는 .roorules 방식의 한계

RooCode에서는 `AGENTS.md`, `AGENT.md`, `.roorules` 같은 파일을 통해 기본 지침을 제공할 수 있다. 단순한 프로젝트에서는 하나의 파일만으로 충분하다.

다만 다음과 같은 경우에는 단일 파일 방식이 한계에 도달한다.

- 문서 작성 규칙과 코딩 규칙이 길어지는 경우
- mode별로 서로 다른 규칙이 필요한 경우
- 반복 작업 절차를 skill로 재사용해야 하는 경우
- 자주 쓰는 prompt를 slash command로 호출해야 하는 경우
- 파일 접근 제외 패턴을 `.rooignore`로 관리해야 하는 경우
- MCP 서버 설정을 프로젝트 단위로 공유해야 하는 경우
- auto-approve 권한 정책을 세밀하게 관리해야 하는 경우

이때는 단일 지침 파일에 모든 내용을 누적하지 말고, `.roo` 폴더 아래에 기능별로 분리한다.

## 4. RooCode 지침 관리 구성 요소 개요

RooCode 지침 관리는 여러 파일과 폴더로 구성된다.

| 구성 요소 | 목적 | 대표 위치 |
|---|---|---|
| `AGENTS.md` | 공통 에이전트 지침 | repository root |
| `AGENT.md` | `AGENTS.md` fallback 또는 단일 에이전트 지침 | repository root |
| `.roo/rules` | 일반 workspace 규칙 | `.roo/rules/*.md` |
| `.roo/rules-{modeSlug}` | mode-specific 규칙 | `.roo/rules-code/*.md` |
| `.roorules` | legacy 또는 fallback 규칙 | repository root |
| `.roorules-{modeSlug}` | mode-specific fallback 규칙 | repository root |
| `.roo/skills` | workspace skill | `.roo/skills/<skill-name>/SKILL.md` |
| `.roo/skills-{modeSlug}` | mode-specific skill | `.roo/skills-code/<skill-name>/SKILL.md` |
| `.agents/skills` | agents skill standard 호환 skill | `.agents/skills/<skill-name>/SKILL.md` |
| `.roo/commands` | slash command | `.roo/commands/*.md` |
| `.roomodes` | project custom modes | repository root |
| `.rooignore` | RooCode 접근 제외 파일 패턴 | repository root |
| `.roo/mcp.json` | project MCP server 설정 | `.roo/mcp.json` |

## 5. 전역 지침과 워크스페이스 지침의 차이

RooCode 지침은 전역 수준과 워크스페이스 수준으로 나눌 수 있다.

전역 수준은 사용자 환경 전체에 적용되는 기본값이다. 워크스페이스 수준은 특정 프로젝트에만 적용된다.

일반적으로 다음 기준으로 나눈다.

| 지침 유형 | 권장 위치 |
|---|---|
| 개인 선호, 전역 작업 습관 | RooCode user settings 또는 전역 지침 위치 |
| 특정 프로젝트 규칙 | repository root `AGENTS.md`, `.roo/rules` |
| 특정 mode 전용 규칙 | `.roo/rules-{modeSlug}` |
| 프로젝트 slash command | `.roo/commands` |
| 프로젝트 MCP 설정 | `.roo/mcp.json` |
| 파일 접근 제외 | `.rooignore` |

전역 지침에는 모든 프로젝트에 적용해도 무리가 없는 내용만 둔다. 프로젝트 고유 폴더 구조, 빌드 명령, 도메인 규칙은 워크스페이스 지침에 둔다.

## 6. .roo 폴더 개요

`.roo` 폴더는 RooCode의 프로젝트별 확장 요소를 관리하는 중심 위치이다.

대표 구조:

```text
project-root/
└─ .roo/
   ├─ rules/
   ├─ rules-code/
   ├─ skills/
   ├─ skills-code/
   ├─ commands/
   └─ mcp.json
```

`.roo`는 다음 목적에 적합하다.

- 일반 규칙 관리
- mode-specific 규칙 관리
- 재사용 skill 관리
- mode-specific skill 관리
- slash command 관리
- project MCP 설정 관리

반대로 다음 내용은 `.roo`에 두는 것이 적합하지 않다.

- 일반 산출 문서
- 분석 결과물
- 빌드 산출물
- 대량 데이터
- 개인 비밀 정보

## 7. .roo/rules 구조

`.roo/rules`는 workspace 전체에 적용할 일반 규칙을 관리하는 폴더이다.

예시:

```text
.roo/
└─ rules/
   ├─ docs.md
   ├─ coding.md
   ├─ testing.md
   └─ review.md
```

규칙 파일에는 다음 내용을 담을 수 있다.

- 문서 작성 기준
- 코딩 스타일
- 테스트 작성 기준
- 리뷰 체크리스트
- 산출물 저장 규칙
- 금지 사항

좋은 규칙 파일의 특징은 다음과 같다.

- 적용 범위가 명확하다.
- 규칙이 실행 가능하다.
- 상위 지침과 중복이 적다.
- 파일 하나가 하나의 주제를 다룬다.

## 8. .roorules fallback 방식

`.roorules`는 RooCode에서 사용할 수 있는 fallback 또는 legacy 지침 파일로 볼 수 있다.

예시:

```text
project-root/
└─ .roorules
```

새 프로젝트에서는 `.roo/rules`처럼 폴더 기반 구조를 우선 사용하는 것이 관리하기 쉽다. 다만 기존 프로젝트가 `.roorules`를 사용하고 있다면 즉시 삭제하지 말고 다음 전략을 따른다.

- 기존 `.roorules`의 내용을 주제별로 분리한다.
- 공통 규칙은 `.roo/rules/*.md`로 이동한다.
- mode별 규칙은 `.roo/rules-{modeSlug}`로 이동한다.
- 마이그레이션 기간에는 `.roorules`에 새 위치를 안내한다.

## 9. Mode-specific Rules 구조

RooCode는 mode별로 서로 다른 작업 규칙을 둘 수 있다. mode-specific rules는 `.roo/rules-{modeSlug}` 형태로 관리한다.

예시:

```text
.roo/
├─ rules/
│  └─ common.md
├─ rules-code/
│  └─ coding.md
├─ rules-architect/
│  └─ design.md
└─ rules-debug/
   └─ debugging.md
```

mode-specific rules가 적합한 경우:

- code mode에서는 구현과 테스트 기준을 강조해야 하는 경우
- architect mode에서는 설계, trade-off, 구조 설명을 강조해야 하는 경우
- debug mode에서는 재현 절차, 로그 수집, 원인 분석 순서를 강조해야 하는 경우
- docs mode에서는 문서 톤과 목차 형식을 강조해야 하는 경우

## 10. .roo/rules-{modeSlug} 작성 방식

mode-specific rule은 특정 mode에서만 적용될 내용을 담는다.

예시:

```md
# Code Mode Rules

Apply these rules in code mode.

- Read existing implementation before editing.
- Keep changes scoped to the requested behavior.
- Add focused tests when behavior changes.
- Report commands used for verification.
```

좋은 mode-specific rule의 특징은 다음과 같다.

- mode 이름과 적용 범위가 분명하다.
- 일반 규칙과 중복하지 않는다.
- 해당 mode에서 필요한 판단 기준을 제공한다.
- 너무 긴 배경 설명을 포함하지 않는다.

## 11. .roorules-{modeSlug} fallback 방식

`.roorules-{modeSlug}`는 mode-specific fallback 파일로 사용할 수 있다.

예시:

```text
project-root/
├─ .roorules-code
├─ .roorules-architect
└─ .roorules-debug
```

새로 구성할 때는 `.roo/rules-{modeSlug}` 폴더 구조가 더 확장성이 좋다. 기존 `.roorules-{modeSlug}`가 있다면 다음 방식으로 정리한다.

- 파일 내용을 `.roo/rules-{modeSlug}/*.md`로 분리한다.
- 기존 파일은 임시 호환 계층으로 유지한다.
- 중복 규칙은 하나의 위치로 통합한다.
- 마이그레이션 완료 후 fallback 파일을 제거할지 결정한다.

## 12. AGENTS.md 지원 방식

RooCode는 `AGENTS.md`를 에이전트 공통 지침 파일로 사용할 수 있다. 여러 도구가 같은 프로젝트 지침을 공유해야 한다면 `AGENTS.md`를 중심 파일로 두는 방식이 유용하다.

권장 역할:

| 파일 | 역할 |
|---|---|
| `AGENTS.md` | 여러 에이전트가 공유하는 공통 프로젝트 지침 |
| `.roo/rules` | RooCode 전용 세부 규칙 |
| `.roo/rules-{modeSlug}` | RooCode mode-specific 규칙 |

`AGENTS.md`에는 모든 도구가 함께 따라도 되는 공통 원칙을 둔다. RooCode에만 해당하는 세부 규칙은 `.roo` 아래로 분리한다.

## 13. AGENT.md fallback 방식

일부 환경에서는 `AGENT.md`가 fallback 지침 파일로 사용될 수 있다.

새 프로젝트에서는 `AGENTS.md`를 우선하고, `AGENT.md`는 기존 호환이나 특수 환경이 필요한 경우에만 둔다.

권장 방식:

```text
project-root/
├─ AGENTS.md
└─ .roo/
   └─ rules/
      └─ common.md
```

피해야 할 방식:

- `AGENTS.md`와 `AGENT.md`에 같은 내용을 중복 작성한다.
- 두 파일에 서로 다른 핵심 원칙을 적어 충돌을 만든다.
- fallback 파일을 장기간 방치한다.

## 14. 지침 로딩 순서와 우선순위

RooCode의 실제 지침 로딩 순서와 우선순위는 버전과 설정에 따라 달라질 수 있다. 따라서 공식 문서를 기준으로 현재 환경에서 확인해야 한다.

일반적인 관리 원칙은 다음과 같다.

- 공통 지침은 `AGENTS.md`에 둔다.
- RooCode 전체 규칙은 `.roo/rules`에 둔다.
- mode-specific 규칙은 `.roo/rules-{modeSlug}`에 둔다.
- legacy fallback 파일은 마이그레이션 목적으로만 유지한다.
- 서로 충돌하는 규칙을 여러 위치에 중복 작성하지 않는다.

우선순위가 불명확한 경우에는 더 구체적인 위치에 있는 지침이 더 좁은 범위를 갖도록 설계한다. 예를 들어 `.roo/rules-code`에는 code mode에만 필요한 내용을 두고, `.roo/rules`에는 전체 공통 규칙만 둔다.

## 15. .roo/skills 구조

`.roo/skills`는 RooCode에서 재사용 가능한 작업 절차와 도메인 지식을 관리하는 위치이다.

예시:

```text
.roo/
└─ skills/
   ├─ write-docs/
   │  └─ SKILL.md
   ├─ code-review/
   │  └─ SKILL.md
   └─ run-analysis/
      └─ SKILL.md
```

필요하면 skill 내부에 `references`, `scripts`, `templates`, `assets` 같은 보조 폴더를 둘 수 있다.

```text
.roo/skills/write-docs/
├─ SKILL.md
├─ references/
│  └─ style-guide.md
├─ templates/
│  └─ standard-doc.md
└─ scripts/
   └─ validate-docs.ps1
```

## 16. SKILL.md 작성 방식

`SKILL.md`는 skill의 목적, 사용 시점, 수행 절차, 출력 형식을 명확히 설명한다.

예시:

```md
---
name: write-docs
description: Use when creating or revising Markdown documentation with the shared documentation rules.
---

# Write Docs Skill

## When To Use

Use this skill when the task is to create, revise, restructure, or review documentation.

## Instructions

1. Read the relevant project rules first.
2. Identify the target audience and document purpose.
3. Use the standard document structure unless the user requests otherwise.
4. Keep Markdown in UTF-8.
5. Do not add unrelated implementation details.

## Output

Return the modified file path and a concise summary.
```

좋은 `SKILL.md`의 특징은 다음과 같다.

- 이름이 짧고 명확하다.
- description이 사용 시점을 잘 설명한다.
- 수행 단계가 구체적이다.
- 출력 형식이 정해져 있다.
- 참조 자료와 스크립트 위치가 명확하다.

## 17. Mode-specific Skills 구조

Mode-specific skill은 특정 mode에서만 의미가 있는 작업 절차를 분리할 때 사용한다.

예시:

```text
.roo/
├─ skills/
│  └─ write-docs/
│     └─ SKILL.md
├─ skills-code/
│  └─ implement-feature/
│     └─ SKILL.md
└─ skills-debug/
   └─ investigate-failure/
      └─ SKILL.md
```

Mode-specific skill이 적합한 경우:

- code mode에서만 호출해야 하는 구현 절차
- debug mode에서만 필요한 장애 분석 절차
- architect mode에서만 필요한 설계 검토 절차
- docs mode에서만 필요한 문서 작성 절차

공통 skill과 mode-specific skill에 같은 내용을 반복하지 않는다. 공통 절차는 `.roo/skills`에 두고, mode별 차이만 `.roo/skills-{modeSlug}`에 둔다.

## 18. .agents/skills와의 관계

RooCode는 `.agents/skills` 같은 agent skill standard 계열 구조와 함께 사용될 수 있다.

두 위치의 권장 역할은 다음과 같다.

| 위치 | 권장 역할 |
|---|---|
| `.agents/skills` | 여러 에이전트가 공유할 수 있는 일반 skill |
| `.roo/skills` | RooCode 전용 skill |
| `.roo/skills-{modeSlug}` | RooCode mode-specific skill |

여러 도구가 함께 사용할 workflow라면 `.agents/skills`에 두는 것이 좋다. RooCode에서만 쓰는 mode-specific workflow라면 `.roo/skills-{modeSlug}`가 적합하다.

## 19. Skills, Custom Instructions, Slash Commands의 역할 구분

RooCode에서 지침과 자동화 요소는 역할이 다르다.

| 구분 | 목적 | 적합한 경우 |
|---|---|---|
| Custom Instructions 또는 Rules | 지속 지침 | 항상 적용할 원칙, 경로별 규칙 |
| Skills | 재사용 workflow | 절차, 참고자료, 템플릿, 스크립트가 필요한 작업 |
| Slash Commands | 명시 호출 prompt | 사용자가 자주 직접 호출하는 짧은 작업 |
| Custom Modes | 작업 성격 분리 | code, architect, debug 등 역할별 도구와 지침 구분 |

간단한 원칙은 rules에 둔다. 반복 절차는 skill로 둔다. 사용자가 직접 호출하는 prompt는 command로 둔다. 작업 환경 자체가 달라져야 하면 mode로 둔다.

## 20. .roo/commands 구조

`.roo/commands`는 RooCode slash command를 정의하는 위치이다.

예시:

```text
.roo/
└─ commands/
   ├─ summarize-changes.md
   ├─ review-diff.md
   └─ prepare-pr.md
```

Command가 적합한 경우:

- 사용자가 직접 자주 호출하는 작업
- 짧은 prompt 템플릿으로 충분한 작업
- 인자를 받아 prompt를 확장하는 작업
- skill보다 가벼운 반복 명령

Command보다 skill이 적합한 경우:

- 참고자료가 필요한 경우
- 템플릿이나 스크립트가 필요한 경우
- 수행 단계가 긴 경우
- mode-specific 판단 기준이 중요한 경우

## 21. Slash Command 작성 방식

Slash command 파일은 일반적으로 Markdown으로 작성하며, frontmatter와 본문 prompt로 구성할 수 있다.

예시:

```md
---
description: Prepare a concise summary from the current changes
argument-hint: [FOCUS]
---

Review the current changes and write a concise summary.
Focus on: $ARGUMENTS
```

좋은 command의 특징은 다음과 같다.

- 이름이 동사 중심이다.
- description이 짧고 명확하다.
- 인자가 필요한 경우 argument hint를 제공한다.
- 본문 prompt가 너무 길지 않다.
- 복잡한 절차는 skill로 분리한다.

## 22. Slash Command frontmatter 필드

Slash command frontmatter에는 command의 설명과 인자 힌트를 둘 수 있다.

대표 필드:

| 필드 | 목적 |
|---|---|
| `description` | command 목록에 표시할 설명 |
| `argument-hint` | 사용자가 넘길 인자 형식 안내 |

예시:

```md
---
description: Review documentation structure and consistency
argument-hint: [FILE]
---

Review the documentation file specified by the user.
Check structure, terminology, consistency, and missing sections.
Target: $ARGUMENTS
```

frontmatter는 command를 찾고 이해하는 데 도움을 준다. command 본문에는 실제로 수행할 prompt를 작성한다.

## 23. .roomodes 구조

`.roomodes`는 프로젝트 custom modes를 정의하는 파일이다.

예시:

```text
project-root/
└─ .roomodes
```

Custom mode는 작업 성격에 따라 도구 접근 권한, 지침, 역할을 다르게 가져가야 할 때 사용한다.

예시 mode:

- code
- architect
- debug
- docs
- review
- test

Mode를 나누면 같은 프로젝트에서도 구현, 설계, 디버깅, 문서 작성의 작업 방식을 구분할 수 있다.

## 24. Custom Modes 작성 방식

Custom mode는 mode 이름, slug, 역할 설명, 사용 가능한 tool group, mode-specific 지침을 포함할 수 있다.

일반적인 작성 원칙은 다음과 같다.

- mode slug는 짧고 일관되게 작성한다.
- mode 역할을 명확히 구분한다.
- 필요한 tool group만 허용한다.
- mode-specific rules와 충돌하지 않게 작성한다.
- 너무 많은 mode를 만들지 않는다.

예시 개념:

```text
mode: docs
slug: docs
purpose: documentation writing and review
tools: read, edit, search
rules: .roo/rules-docs
```

실제 `.roomodes` 문법은 현재 RooCode 공식 문서를 기준으로 작성한다.

## 25. Mode groups와 tool access 관리

Mode group은 mode에서 사용할 수 있는 도구 범위를 관리하는 개념이다.

권장 원칙:

- mode별로 필요한 도구만 허용한다.
- 문서 작성 mode에는 불필요한 실행 권한을 줄인다.
- debug mode에는 로그 확인과 테스트 실행을 허용하되 destructive command는 제한한다.
- architect mode에는 읽기와 검색 중심 권한을 우선한다.
- code mode에는 편집과 검증에 필요한 권한을 허용한다.

Tool access는 작업 효율뿐 아니라 안전성과도 관련된다. mode가 많아질수록 각 mode의 권한 범위를 명확히 관리해야 한다.

## 26. Global Modes와 Project Modes의 우선순위

RooCode에서는 전역 mode와 프로젝트 mode를 함께 사용할 수 있다.

일반적인 관리 원칙은 다음과 같다.

- 모든 프로젝트에서 재사용할 mode는 global mode로 둔다.
- 특정 프로젝트에만 맞는 mode는 `.roomodes`에 둔다.
- 같은 이름 또는 slug의 mode가 충돌하지 않도록 한다.
- 프로젝트 mode가 전역 mode를 대체하는 경우 의도를 문서화한다.

실제 우선순위와 병합 방식은 RooCode 버전과 공식 문서를 기준으로 확인한다.

## 27. .rooignore 구조와 사용 목적

`.rooignore`는 RooCode가 접근하거나 고려하지 않아야 할 파일과 폴더 패턴을 정의하는 파일이다.

예시:

```text
project-root/
└─ .rooignore
```

사용 목적:

- 빌드 산출물 제외
- 대용량 데이터 제외
- 민감 파일 제외
- generated 파일 제외
- 의존성 폴더 제외

예시 패턴:

```gitignore
node_modules/
dist/
build/
.env
*.secret
outputs/large-data/
```

`.rooignore`는 `.gitignore`와 비슷한 목적을 가지지만, Git 추적 여부가 아니라 RooCode의 접근 범위를 관리한다는 점이 다르다.

## 28. .rooignore 패턴 작성 방식

`.rooignore` 패턴은 좁고 명확하게 작성한다.

권장 패턴:

- generated output 제외
- dependency directory 제외
- credential file 제외
- 매우 큰 binary file 제외
- 분석 결과 중 재생성 가능한 파일 제외

주의사항:

- 실제 작업에 필요한 source file을 제외하지 않는다.
- 문서 작성에 필요한 reference file을 실수로 제외하지 않는다.
- 너무 넓은 wildcard를 사용하지 않는다.
- `.rooignore` 변경은 작업 영향이 크므로 리뷰한다.

예시:

```gitignore
# Dependencies
node_modules/
.venv/

# Build outputs
dist/
build/

# Secrets
.env
.env.*
*.pem

# Large generated outputs
outputs/cache/
outputs/tmp/
```

## 29. Auto-Approve와 권한 관리 방식

Auto-approve는 특정 작업이나 명령을 사용자 승인 없이 수행하도록 허용하는 설정이다.

권장 원칙:

- 최소 권한 원칙을 따른다.
- 읽기 작업과 쓰기 작업을 구분한다.
- destructive command는 자동 승인하지 않는다.
- 외부 네트워크, 패키지 설치, 파일 삭제는 신중하게 다룬다.
- 프로젝트 공유 설정과 개인 로컬 설정을 구분한다.

Auto-approve가 적합한 경우:

- 안전한 읽기 명령
- 반복적인 테스트 명령
- formatter나 linter 실행
- project-local generated file 재생성

Auto-approve가 부적합한 경우:

- 파일 삭제
- branch reset
- credential 변경
- 원격 배포
- 시스템 경로 수정

## 30. Command Allowlist와 Denylist 관리

RooCode는 명령 허용 목록과 차단 목록을 설정할 수 있다.

Allowlist는 승인 없이 실행해도 되는 안전한 명령을 좁게 정의한다. Denylist는 절대 실행하면 안 되는 명령을 명시한다.

권장 방식:

- 전체 명령을 넓게 허용하지 않는다.
- 하위 명령 prefix를 좁게 허용한다.
- destructive command는 denylist에 둔다.
- allowlist와 denylist가 충돌하지 않게 관리한다.
- 팀 공유 설정에 넣기 전 검토한다.

예시 개념:

```text
allow:
  npm test
  npm run lint
  git status
  git diff

deny:
  rm -rf
  git reset --hard
  format disk
```

실제 설정 키와 문법은 현재 RooCode 공식 문서를 기준으로 작성한다.

## 31. .roo/mcp.json 구조

`.roo/mcp.json`은 프로젝트 단위 MCP 서버 설정을 관리하는 위치이다.

예시:

```text
.roo/
└─ mcp.json
```

MCP 설정에 적합한 내용:

- 프로젝트에서 사용할 MCP 서버 정의
- 로컬 MCP command 설정
- 원격 MCP endpoint 설정
- shared tool integration 설정

주의사항:

- token, password, API key를 직접 저장하지 않는다.
- 사용자별 인증 정보는 안전한 별도 경로로 관리한다.
- 프로젝트에 체크인해도 되는 설정인지 확인한다.
- 외부 시스템 접근 권한은 최소 범위로 설정한다.

## 32. Global MCP 설정과 Project MCP 설정의 차이

MCP 설정은 global scope와 project scope로 나눌 수 있다.

| 구분 | 용도 |
|---|---|
| Global MCP | 여러 프로젝트에서 공통으로 사용하는 개인 도구 연결 |
| Project MCP | 특정 프로젝트에서 공유해야 하는 도구 연결 |

Project MCP가 적합한 경우:

- 팀 전체가 같은 MCP 서버를 사용해야 하는 경우
- 프로젝트 코드베이스와 직접 관련된 도구인 경우
- repository와 함께 설정을 공유하는 것이 유용한 경우

Global MCP가 적합한 경우:

- 개인 계정에 묶인 도구인 경우
- 여러 프로젝트에서 반복 사용하는 개인 도구인 경우
- 프로젝트에 공유하면 안 되는 연결인 경우

## 33. .roo, .agents, AGENTS.md, .roomodes, .rooignore의 역할 구분

각 구성 요소는 서로 대체 관계가 아니라 보완 관계이다.

| 구분 | 주 역할 | 넣을 내용 | 넣지 않을 내용 |
|---|---|---|---|
| `AGENTS.md` | 공통 지속 지침 | 여러 에이전트가 공유할 원칙 | RooCode mode-specific 세부 규칙 전체 |
| `.roo/rules` | RooCode 일반 규칙 | 문서, 코딩, 테스트 규칙 | 반복 workflow 전체 |
| `.roo/rules-{modeSlug}` | mode-specific 규칙 | mode별 작업 기준 | 전역 공통 지침 반복 |
| `.roo/skills` | RooCode workflow | 절차, 템플릿, 참고자료 | 단순 slash command |
| `.agents/skills` | 다중 에이전트 skill | 도구 공통 workflow | RooCode 전용 mode 의존 절차 |
| `.roo/commands` | slash command | 짧은 명시 호출 prompt | 긴 전문 workflow |
| `.roomodes` | custom mode | mode 정의와 tool access | 일반 문서 규칙 본문 전체 |
| `.rooignore` | 접근 제외 | 제외 패턴 | 프로젝트 지침 |
| `.roo/mcp.json` | MCP 연결 | MCP server 설정 | secret 값 |

## 34. 권장 공통 폴더 구조

일반적인 권장 구조는 다음과 같다.

```text
project-root/
├─ AGENTS.md
├─ AGENT.md
├─ .roorules
├─ .roorules-code
├─ .roomodes
├─ .rooignore
├─ .roo/
│  ├─ rules/
│  │  ├─ docs.md
│  │  ├─ coding.md
│  │  └─ testing.md
│  ├─ rules-code/
│  │  └─ coding-mode.md
│  ├─ rules-architect/
│  │  └─ architecture-mode.md
│  ├─ skills/
│  │  ├─ write-docs/
│  │  │  ├─ SKILL.md
│  │  │  └─ templates/
│  │  └─ code-review/
│  │     ├─ SKILL.md
│  │     └─ references/
│  ├─ skills-code/
│  │  └─ implement-feature/
│  │     └─ SKILL.md
│  ├─ commands/
│  │  ├─ summarize-changes.md
│  │  └─ prepare-pr.md
│  └─ mcp.json
├─ .agents/
│  └─ skills/
│     └─ shared-docs-workflow/
│        └─ SKILL.md
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

RooCode 전용 규칙이 필요할 때:

```text
project-root/
├─ AGENTS.md
└─ .roo/
   └─ rules/
      └─ common.md
```

Mode-specific 규칙이 필요할 때:

```text
project-root/
├─ AGENTS.md
└─ .roo/
   ├─ rules/
   │  └─ common.md
   └─ rules-code/
      └─ coding.md
```

반복 workflow가 필요할 때:

```text
project-root/
├─ AGENTS.md
└─ .roo/
   └─ skills/
      └─ write-docs/
         └─ SKILL.md
```

Slash command가 필요할 때:

```text
project-root/
├─ AGENTS.md
└─ .roo/
   └─ commands/
      └─ summarize-changes.md
```

MCP 설정이 필요할 때:

```text
project-root/
├─ AGENTS.md
└─ .roo/
   └─ mcp.json
```

## 35. 단계별 도입 전략

처음부터 모든 구조를 만들 필요는 없다. 다음 순서로 도입하는 것이 좋다.

1. `AGENTS.md` 작성

   여러 에이전트가 공유할 프로젝트 전체 지침을 작성한다.

2. RooCode 일반 규칙 분리

   RooCode에서만 필요한 세부 규칙은 `.roo/rules/*.md`로 분리한다.

3. 기존 `.roorules` 정리

   기존 `.roorules`가 있다면 주제별 파일로 나누어 `.roo/rules`로 이동한다.

4. Mode-specific rules 도입

   code, architect, debug 등 mode별 규칙이 필요하면 `.roo/rules-{modeSlug}`를 만든다.

5. 반복 workflow를 skill로 전환

   같은 절차를 반복하게 되면 `.roo/skills/<skill-name>/SKILL.md`로 만든다.

6. Mode-specific skills 도입

   특정 mode에서만 쓰는 workflow는 `.roo/skills-{modeSlug}`에 둔다.

7. 자주 쓰는 prompt를 command로 전환

   사용자가 직접 호출하는 짧은 prompt는 `.roo/commands/*.md`로 만든다.

8. Custom mode 도입

   작업 성격별 tool access와 역할을 나누어야 하면 `.roomodes`를 작성한다.

9. `.rooignore` 작성

   RooCode가 접근하지 않아야 할 파일과 폴더를 제외한다.

10. Auto-approve 정책 정리

   안전한 명령만 좁게 허용하고, 위험한 명령은 차단한다.

11. MCP 설정 도입

   프로젝트 외부 도구 연결이 필요하면 `.roo/mcp.json`을 작성한다.

## 36. 주의사항과 안티패턴

주의사항:

- 공식 문서와 현재 RooCode 버전을 확인한다.
- `AGENTS.md`에는 공통 핵심 지침만 둔다.
- RooCode 전용 세부 규칙은 `.roo/rules`로 분리한다.
- mode-specific 규칙은 일반 규칙과 중복하지 않는다.
- skill과 command의 역할을 구분한다.
- `.rooignore`로 source file을 실수로 제외하지 않는다.
- MCP 설정에 secret을 직접 저장하지 않는다.
- auto-approve는 최소 권한 원칙을 따른다.
- destructive command는 자동 승인하지 않는다.

안티패턴:

- 모든 내용을 `AGENTS.md` 또는 `.roorules` 하나에 계속 누적하는 방식
- `.roo/rules`와 `.roorules`에 같은 내용을 중복 작성하는 방식
- mode-specific 규칙을 모든 mode에 복사하는 방식
- skill 하나가 문서 작성, 코딩, 리뷰, 배포를 모두 담당하게 만드는 방식
- 모든 반복 prompt를 slash command로만 관리하는 방식
- `.roomodes`를 너무 많이 만들어 실제 작업 선택을 어렵게 하는 방식
- `.rooignore`에 너무 넓은 wildcard를 사용하는 방식
- allowlist를 너무 넓게 열어 두는 방식
- 개인 secret이나 token을 `.roo/mcp.json`에 저장하는 방식

## 37. 참고 기준

이 문서는 RooCode 공식 문서의 다음 주제를 기준으로 정리한다.

- Custom Instructions
- Rules
- Skills
- Slash Commands
- Custom Modes
- `.rooignore`
- Auto-Approving Actions
- Command Allowlist and Denylist
- MCP

공식 문서의 세부 설정명과 지원 범위는 RooCode 버전과 실행 환경에 따라 달라질 수 있으므로, 실제 설정 파일을 작성할 때는 현재 사용 중인 RooCode 환경의 최신 문서를 확인한다.
