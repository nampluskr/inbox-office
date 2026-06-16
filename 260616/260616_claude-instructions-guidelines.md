# Claude Instruction Guidelines

## 1. 문서 목적

이 문서는 Claude Code에서 반복적으로 사용하는 지침, 규칙, 재사용 워크플로우, 명령, subagent, 설정, 권한 정책을 어떤 파일과 폴더에 나누어 관리할지 설명한다.

기존에는 `CLAUDE.md` 파일 하나에 모든 지침을 작성하는 방식으로 시작할 수 있다. 그러나 프로젝트 수가 늘어나거나, 문서 작성 규칙, 코딩 규칙, 검증 절차, 반복 명령, subagent, hook, MCP 설정이 많아지면 단일 파일만으로는 관리가 어려워진다.

이 문서는 다음 구성 요소의 역할을 구분한다.

- `CLAUDE.md`
- `CLAUDE.local.md`
- `.claude/CLAUDE.md`
- `.claude/rules`
- `.claude/skills`
- `.claude/commands`
- `.claude/agents`
- `.claude/settings.json`
- `.claude/settings.local.json`
- `.mcp.json`
- hooks
- permissions

## 2. 기존 단일 CLAUDE.md 방식의 한계

`CLAUDE.md` 하나만 사용하는 방식은 단순하고 시작하기 쉽다. 프로젝트 전체에서 Claude Code가 항상 참고해야 하는 지침을 한 곳에 작성할 수 있다.

다만 다음과 같은 경우에는 단일 파일 방식이 한계에 도달한다.

- 문서 작성 규칙과 코딩 규칙이 길어지는 경우
- 특정 작업 절차를 반복적으로 호출해야 하는 경우
- 하위 폴더별로 서로 다른 규칙이 필요한 경우
- 사용자 개인 지침과 팀 공유 지침이 섞이는 경우
- slash command, skill, subagent를 함께 관리해야 하는 경우
- hook, permission, MCP 설정까지 같은 파일에서 설명하려는 경우
- 프로젝트별 설정과 일반 작업 지침이 구분되지 않는 경우

이때는 `CLAUDE.md`를 최상위 지침으로 유지하되, 세부 규칙은 `.claude/rules`, 반복 워크플로우는 `.claude/skills` 또는 `.claude/commands`, 전문 역할은 `.claude/agents`, 실행 설정은 `.claude/settings.json`으로 분리하는 것이 좋다.

## 3. Claude Code 지침 관리 구성 요소 개요

Claude Code 지침 관리는 하나의 파일이 아니라 여러 계층으로 구성된다.

| 구성 요소 | 목적 | 대표 위치 |
|---|---|---|
| `CLAUDE.md` | 프로젝트 또는 폴더 단위의 지속 지침 | repository root 또는 하위 폴더 |
| `CLAUDE.local.md` | 개인 로컬 지침 | repository root 또는 하위 폴더 |
| `.claude/CLAUDE.md` | 프로젝트 내부 Claude 전용 지침 | `.claude/CLAUDE.md` |
| `.claude/rules` | 경로별 또는 주제별 규칙 | `.claude/rules/*.md` |
| `.claude/skills` | 재사용 가능한 작업 절차 | `.claude/skills/<skill-name>/SKILL.md` |
| `.claude/commands` | slash command 정의 | `.claude/commands/*.md` |
| `.claude/agents` | subagent 정의 | `.claude/agents/*.md` |
| `.claude/settings.json` | 프로젝트 공유 설정 | `.claude/settings.json` |
| `.claude/settings.local.json` | 개인 로컬 설정 | `.claude/settings.local.json` |
| `.mcp.json` | 프로젝트 MCP 서버 설정 | `.mcp.json` |

중요한 구분은 다음과 같다.

- 항상 적용할 지침은 `CLAUDE.md`에 둔다.
- 경로별 세부 규칙은 `.claude/rules`에 둔다.
- 반복 작업 절차는 `.claude/skills` 또는 `.claude/commands`에 둔다.
- 전문 역할 위임은 `.claude/agents`에 둔다.
- Claude Code 실행 설정은 `.claude/settings.json`에 둔다.
- 사용자 개인 설정은 `.claude/settings.local.json`에 둔다.
- 외부 도구 연결은 `.mcp.json`에 둔다.

## 4. CLAUDE.md 기본 구조와 사용 범위

`CLAUDE.md`는 Claude Code가 프로젝트 작업 시 참고하는 기본 지침 파일이다.

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
# CLAUDE.md

## Project Overview

이 저장소의 목적과 주요 산출물을 설명한다.

## Working Principles

- 변경 범위를 작게 유지한다.
- 기존 구조와 스타일을 우선 따른다.
- 불확실한 외부 정보는 확인 후 사용한다.

## Coding Guidelines

- 공통 유틸리티는 중복 구현하지 않는다.
- 테스트 가능한 단위로 작성한다.

## Documentation Guidelines

- Markdown 문서는 UTF-8로 작성한다.
- 산출물과 참고 문서를 구분한다.

## Verification

- 변경 후 필요한 테스트 또는 확인 명령을 실행한다.
```

`CLAUDE.md`에는 항상 적용해야 하는 핵심 지침을 둔다. 너무 긴 세부 절차를 모두 넣기보다, 필요한 경우 `.claude/rules`, `.claude/skills`, `.claude/commands`로 분리한다.

## 5. CLAUDE.local.md의 역할과 사용 시점

`CLAUDE.local.md`는 개인 로컬 환경에만 적용할 지침을 둘 때 사용한다.

적합한 내용은 다음과 같다.

- 개인 개발 환경 경로
- 개인이 선호하는 로컬 실행 명령
- 팀에 공유하지 않을 임시 메모
- 특정 사용자의 도구 설정 설명

주의할 점은 다음과 같다.

- 팀 전체에 필요한 지침은 `CLAUDE.md`에 둔다.
- 민감 정보는 `CLAUDE.local.md`에도 저장하지 않는다.
- 공유되어야 하는 빌드, 테스트, 배포 절차를 local 파일에만 두지 않는다.

일반적으로 `CLAUDE.local.md`는 Git에 커밋하지 않는 개인 파일로 관리하는 것이 좋다.

## 6. 전역 지침과 프로젝트 지침의 차이

Claude Code 지침은 전역 지침과 프로젝트 지침으로 나눌 수 있다.

전역 지침은 사용자 환경 전체에 적용되는 개인 기본값이다.

```text
~/.claude/CLAUDE.md
```

프로젝트 지침은 특정 저장소 또는 폴더에 적용된다.

```text
project-root/CLAUDE.md
project-root/subdir/CLAUDE.md
```

일반적으로 다음 기준으로 나눈다.

| 지침 유형 | 권장 위치 |
|---|---|
| 개인 응답 선호, 항상 지킬 작업 습관 | `~/.claude/CLAUDE.md` |
| 특정 저장소의 빌드, 테스트, 문서 규칙 | project `CLAUDE.md` |
| 특정 모듈 또는 하위 서비스 전용 규칙 | 하위 폴더 `CLAUDE.md` |
| 개인 로컬 환경 지침 | `CLAUDE.local.md` |

전역 지침에는 모든 프로젝트에 공통으로 적용해도 무리가 없는 내용만 둔다. 프로젝트 고유의 빌드 명령, 폴더 구조, 도메인 규칙은 프로젝트 `CLAUDE.md`에 둔다.

## 7. 하위 폴더별 CLAUDE.md 구성 방식

하위 폴더별로 성격이 다른 작업 규칙이 필요하면 해당 폴더에 `CLAUDE.md`를 둘 수 있다.

예시:

```text
project-root/
├─ CLAUDE.md
├─ docs/
│  └─ CLAUDE.md
├─ src/
│  └─ CLAUDE.md
└─ tests/
   └─ CLAUDE.md
```

하위 폴더별 지침 예시는 다음과 같다.

- `docs/CLAUDE.md`: 문서 톤, 파일명 규칙, 목차 형식, 그림 저장 방식
- `src/CLAUDE.md`: 코드 스타일, 모듈 분리 방식, 타입 힌트, 테스트 기준
- `tests/CLAUDE.md`: 테스트 파일명, fixture 관리, 실행 명령

하위 지침은 상위 지침을 반복해서 복사하지 않는다. 상위 지침과 달라지는 내용 또는 더 구체적인 내용만 작성한다.

## 8. AGENTS.md와 CLAUDE.md 연동 방식

이미 `AGENTS.md`를 사용하는 저장소에서는 같은 내용을 `CLAUDE.md`에 중복 작성하지 않는 것이 좋다.

권장 방식은 `CLAUDE.md`에서 `AGENTS.md`를 import하거나, 두 파일의 역할을 명확히 나누는 것이다.

예시:

```md
# CLAUDE.md

공통 에이전트 지침은 다음 문서를 우선 참고한다.

@AGENTS.md
```

역할 분리 예시는 다음과 같다.

| 파일 | 역할 |
|---|---|
| `AGENTS.md` | 여러 에이전트가 공유하는 공통 프로젝트 지침 |
| `CLAUDE.md` | Claude Code에 특화된 추가 지침 또는 `AGENTS.md` import |

중복 작성은 피한다. 같은 규칙이 두 파일에 다르게 적히면 유지보수가 어려워지고, 실제 작업 시 충돌이 발생할 수 있다.

## 9. .claude 폴더 개요

`.claude` 폴더는 Claude Code 관련 프로젝트 설정과 확장 요소를 관리하는 위치이다.

대표 구조:

```text
project-root/
└─ .claude/
   ├─ CLAUDE.md
   ├─ rules/
   ├─ skills/
   ├─ commands/
   ├─ agents/
   ├─ settings.json
   └─ settings.local.json
```

`.claude`는 다음 목적에 적합하다.

- Claude 전용 지침 관리
- 경로별 규칙 관리
- 재사용 skill 관리
- slash command 관리
- subagent 관리
- Claude Code 실행 설정 관리
- hooks와 permissions 관리

반대로 다음 내용은 `.claude`에 두는 것이 적합하지 않다.

- 일반 산출 문서
- 실행 결과물
- 데이터 파일
- 도메인 참고자료 전체
- 단순 개인 메모

## 10. .claude/rules 구조

`.claude/rules`는 프로젝트 내 경로별 또는 주제별 규칙을 분리해 관리할 때 사용할 수 있다.

예시 구조:

```text
.claude/
└─ rules/
   ├─ docs.md
   ├─ python.md
   ├─ testing.md
   └─ frontend.md
```

규칙 파일에는 다음 내용을 담을 수 있다.

- 특정 파일 유형별 작성 규칙
- 특정 폴더별 작업 원칙
- 테스트 작성 기준
- 문서 작성 기준
- 리뷰 체크리스트

예시:

```md
# Documentation Rules

Apply these rules when editing files under `docs/`.

- Use Markdown headings in a consistent hierarchy.
- Keep generated documents in UTF-8.
- Separate reference material from final deliverables.
```

`.claude/rules`는 사람이 읽는 작업 규칙을 분리하는 용도이다. 실행 권한 정책과 혼동하지 않도록 주의한다.

## 11. Path-specific Rules 작성 방식

Path-specific rule은 특정 경로나 파일 유형에만 적용되는 규칙이다.

예시:

```md
# Python Rules

Apply when editing:

- `src/**/*.py`
- `tests/**/*.py`

Rules:

- Prefer small pure functions for reusable logic.
- Keep IO code separate from computation code.
- Add focused tests for behavior changes.
```

좋은 path-specific rule의 특징은 다음과 같다.

- 적용 범위가 명확하다.
- 규칙이 짧고 실행 가능하다.
- 상위 `CLAUDE.md`와 중복이 적다.
- 예외 상황이 필요한 경우 함께 적는다.

피해야 할 방식은 다음과 같다.

- 모든 규칙 파일에 같은 공통 지침을 반복하는 방식
- 경로 조건 없이 너무 넓은 규칙을 여러 파일에 흩어 두는 방식
- 실제로 적용할 수 없는 추상적인 원칙만 나열하는 방식

## 12. .claude/skills 구조

Skill은 반복 가능한 작업 절차와 도메인 지식을 패키징하는 방식이다.

기본 구조:

```text
.claude/
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
.claude/skills/write-docs/
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

## 13. SKILL.md 작성 방식

`SKILL.md`는 일반적으로 metadata와 본문 지침으로 구성한다.

예시:

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

`name`은 짧고 명확해야 한다. `description`은 언제 이 skill을 사용할지 판단하는 핵심 기준이므로 구체적으로 작성한다.

좋은 description의 특징은 다음과 같다.

- 어떤 요청에서 사용해야 하는지 분명하다.
- 사용하지 말아야 할 범위가 암시되거나 명시되어 있다.
- 핵심 키워드가 앞쪽에 있다.
- 너무 포괄적이지 않다.

## 14. Skills 호출 방식과 기존 Commands와의 관계

Skill과 command는 모두 반복 작업을 돕지만 역할이 다르다.

| 구분 | 목적 | 적합한 경우 |
|---|---|---|
| Skill | 작업 절차와 도메인 지식 패키징 | 반복 workflow, 전문 작업 방식 |
| Command | 사용자가 직접 호출하는 짧은 slash command | 자주 실행하는 명령형 prompt |

Skill은 작업 방식 자체를 정의하는 데 적합하다. Command는 사용자가 `/command-name`처럼 직접 호출하는 작업 진입점에 적합하다.

예를 들어 문서 작성 workflow가 복잡하다면 skill로 만든다.

```text
.claude/skills/write-docs/SKILL.md
```

반면 “현재 변경사항 요약 작성”처럼 짧고 명령형인 작업은 command로 만들 수 있다.

```text
.claude/commands/summarize-changes.md
```

## 15. .claude/commands 구조와 사용 시점

`.claude/commands`는 slash command를 정의하는 위치이다.

예시 구조:

```text
.claude/
└─ commands/
   ├─ write-doc.md
   ├─ review-diff.md
   └─ prepare-pr.md
```

command 파일은 사용자가 자주 반복하는 prompt를 짧은 명령으로 호출하기 위해 사용한다.

예시:

```md
---
description: Prepare a concise pull request summary from the current diff
argument-hint: [FOCUS]
---

Review the current git diff and write a concise PR summary.
Focus on: $ARGUMENTS
```

Command가 적합한 경우:

- 사용자가 직접 자주 호출하는 작업
- 입력 인자를 받아 prompt를 확장하는 작업
- skill보다 가볍고 짧은 절차

Command보다 skill이 적합한 경우:

- 참고자료, 템플릿, 스크립트가 함께 필요한 경우
- 작업 절차가 길고 판단 기준이 많은 경우
- 암시적으로도 선택되기를 원하는 경우

## 16. .claude/agents 구조

`.claude/agents`는 subagent를 정의하는 위치이다.

예시 구조:

```text
.claude/
└─ agents/
   ├─ code-reviewer.md
   ├─ docs-writer.md
   └─ test-runner.md
```

Subagent는 특정 역할을 가진 보조 에이전트로, 복잡한 작업을 역할별로 나누는 데 유용하다.

적합한 사용 예시는 다음과 같다.

- 코드 리뷰 전담
- 문서 리뷰 전담
- 테스트 실패 분석 전담
- 보안 관점 검토
- 대규모 리팩터링 영향 분석

Subagent는 역할이 명확해야 한다. 너무 넓은 역할을 가진 subagent는 실제 작업에서 일관성이 떨어진다.

## 17. Subagents 작성 방식

Subagent 파일은 역할, 사용 시점, 수행 방식, 출력 형식을 명확히 적는다.

예시:

```md
---
name: code-reviewer
description: Use for reviewing code changes and identifying bugs, regressions, and missing tests.
---

# Code Reviewer

## Role

Review code changes with emphasis on correctness, maintainability, and regression risk.

## Instructions

- Prioritize findings over summaries.
- Reference exact files and lines when possible.
- Do not rewrite code unless explicitly asked.
- Call out missing tests when behavior changes.

## Output

Return findings ordered by severity, followed by open questions and a short summary.
```

좋은 subagent의 특징은 다음과 같다.

- 역할이 좁고 명확하다.
- 언제 사용해야 하는지 분명하다.
- 출력 형식이 정해져 있다.
- 일반 지침과 중복이 적다.

## 18. .claude/settings.json 구조

`.claude/settings.json`은 프로젝트에서 공유할 Claude Code 설정을 관리하는 파일이다.

예시:

```json
{
  "permissions": {
    "allow": [],
    "deny": []
  },
  "hooks": {}
}
```

설정 파일에는 환경에 따라 다음 성격의 내용을 둘 수 있다.

- 권한 정책
- hook 설정
- 도구 사용 관련 설정
- 프로젝트 공유 기본값

실제 설정 키는 Claude Code 버전과 실행 환경에 따라 달라질 수 있다. 따라서 작성 시에는 현재 공식 문서와 현재 환경의 설정 예시를 확인해야 한다.

## 19. .claude/settings.local.json 사용 방식

`.claude/settings.local.json`은 개인 로컬 설정을 둘 때 사용한다.

적합한 내용:

- 개인 환경에서만 필요한 권한 허용
- 로컬 도구 경로
- 개인 hook 설정
- 팀에 공유하지 않을 실험 설정

주의사항:

- 민감 정보는 저장하지 않는다.
- 팀 전체에 필요한 설정은 `settings.json`에 둔다.
- repository에 커밋하지 않는 것을 기본으로 한다.
- 개인 설정이 팀 설정을 우회하지 않도록 주의한다.

## 20. Permissions와 Hooks 관리 방식

Permissions는 Claude Code가 어떤 도구나 명령을 사용할 수 있는지 제어하는 설정이다. Hooks는 특정 이벤트 전후에 명령이나 검증 절차를 실행하는 방식이다.

권장 원칙은 다음과 같다.

- 필요한 권한만 좁게 허용한다.
- 위험한 명령은 기본적으로 허용하지 않는다.
- hook은 빠르고 예측 가능해야 한다.
- hook 실패 시 사용자가 원인을 이해할 수 있어야 한다.
- destructive command를 자동화하지 않는다.

예시 사용 시점:

- 파일 수정 후 formatter 실행
- commit 전 테스트 실행
- 특정 명령 실행 전 승인 요구
- 금지된 파일 수정 감지

Hooks와 permissions는 작업 지침이 아니라 실행 제어 장치이다. 문서 작성 방식이나 코드 스타일 설명은 `CLAUDE.md`, `.claude/rules`, `.claude/skills`에 둔다.

## 21. MCP 설정 관리 방식

MCP는 Claude Code가 외부 도구, 데이터, 시스템에 접근할 수 있도록 하는 연결 방식이다.

프로젝트 단위 MCP 설정은 일반적으로 `.mcp.json`에 둘 수 있다.

예시:

```text
project-root/
└─ .mcp.json
```

MCP 설정에 적합한 내용:

- 외부 도구 서버 정의
- 프로젝트에서 공유할 MCP 연결 정보
- 로컬 또는 원격 MCP endpoint 설정

주의사항:

- 토큰이나 비밀번호 같은 민감 정보를 직접 저장하지 않는다.
- 사용자별 인증 정보는 안전한 별도 경로로 관리한다.
- 프로젝트에 체크인해도 되는 설정인지 확인한다.
- 외부 시스템 접근 권한은 최소 범위로 설정한다.

## 22. CLAUDE.md, rules, skills, agents, settings의 역할 구분

각 구성 요소는 서로 대체 관계가 아니라 보완 관계이다.

| 구분 | 주 역할 | 넣을 내용 | 넣지 않을 내용 |
|---|---|---|---|
| `CLAUDE.md` | 지속 지침 | 프로젝트 원칙, 작업 규칙, 검증 기준 | 긴 반복 workflow 전체 |
| `.claude/rules` | 세부 규칙 | 경로별 문서/코딩/테스트 규칙 | 실행 권한 정책 전체 |
| `.claude/skills` | 재사용 workflow | 특정 작업 절차, 도메인별 수행 방법 | 단순 slash command만 필요한 prompt |
| `.claude/commands` | 명시 호출 명령 | 자주 쓰는 짧은 prompt | 복잡한 workflow 전체 |
| `.claude/agents` | 전문 역할 | 리뷰어, 문서 작성자, 테스트 분석가 | 일반 프로젝트 지침 |
| `.claude/settings.json` | 실행 설정 | permissions, hooks 등 | 문서 스타일 가이드 본문 |
| `.mcp.json` | 외부 도구 연결 | MCP 서버 설정 | 민감 인증 정보 |

간단히 정리하면 다음과 같다.

- “항상 이렇게 행동하라”는 `CLAUDE.md`
- “이 경로에서는 이렇게 작성하라”는 `.claude/rules`
- “이 작업을 반복 가능하게 수행하라”는 `.claude/skills`
- “이 명령을 사용자가 직접 호출하게 하라”는 `.claude/commands`
- “이 역할로 별도 검토하라”는 `.claude/agents`
- “Claude Code 실행 환경을 이렇게 설정하라”는 `.claude/settings.json`
- “외부 시스템을 이렇게 연결하라”는 `.mcp.json`

## 23. 권장 공통 폴더 구조

일반적인 권장 구조는 다음과 같다.

```text
project-root/
├─ CLAUDE.md
├─ CLAUDE.local.md
├─ AGENTS.md
├─ .claude/
│  ├─ CLAUDE.md
│  ├─ rules/
│  │  ├─ docs.md
│  │  ├─ coding.md
│  │  └─ testing.md
│  ├─ skills/
│  │  ├─ write-docs/
│  │  │  ├─ SKILL.md
│  │  │  └─ templates/
│  │  └─ code-review/
│  │     ├─ SKILL.md
│  │     └─ references/
│  ├─ commands/
│  │  ├─ summarize-changes.md
│  │  └─ prepare-pr.md
│  ├─ agents/
│  │  ├─ code-reviewer.md
│  │  └─ docs-writer.md
│  ├─ settings.json
│  └─ settings.local.json
├─ .mcp.json
├─ docs/
├─ src/
├─ tests/
└─ references/
```

모든 프로젝트가 이 구조를 전부 가질 필요는 없다. 필요한 구성 요소만 단계적으로 도입한다.

최소 구조:

```text
project-root/
└─ CLAUDE.md
```

기존 `AGENTS.md`와 연동하는 최소 구조:

```text
project-root/
├─ AGENTS.md
└─ CLAUDE.md
```

반복 workflow가 생겼을 때:

```text
project-root/
├─ CLAUDE.md
└─ .claude/
   └─ skills/
      └─ write-docs/
         └─ SKILL.md
```

명시 호출 command가 필요할 때:

```text
project-root/
├─ CLAUDE.md
└─ .claude/
   └─ commands/
      └─ prepare-pr.md
```

Subagent가 필요할 때:

```text
project-root/
├─ CLAUDE.md
└─ .claude/
   └─ agents/
      └─ code-reviewer.md
```

프로젝트 설정까지 필요할 때:

```text
project-root/
├─ CLAUDE.md
└─ .claude/
   ├─ settings.json
   └─ settings.local.json
```

MCP 연결이 필요할 때:

```text
project-root/
├─ CLAUDE.md
└─ .mcp.json
```

## 24. 단계별 도입 전략

처음부터 모든 구조를 만들 필요는 없다. 다음 순서로 도입하는 것이 좋다.

1. `CLAUDE.md` 작성

   프로젝트 전체에서 항상 지킬 최소 지침을 작성한다.

2. 기존 `AGENTS.md` 연동

   이미 `AGENTS.md`를 사용 중이라면 `CLAUDE.md`에서 import하거나 역할을 분리한다.

3. 세부 규칙 분리

   문서 작성 규칙, 코딩 규칙, 테스트 규칙이 길어지면 `.claude/rules` 또는 별도 reference 문서로 분리한다.

4. 반복 작업을 skill로 전환

   같은 작업 절차를 여러 번 수행하게 되면 `.claude/skills/<skill-name>/SKILL.md`로 만든다.

5. 자주 쓰는 명령을 command로 전환

   사용자가 직접 호출하는 짧은 prompt는 `.claude/commands/*.md`로 만든다.

6. 전문 역할을 subagent로 분리

   리뷰어, 문서 작성자, 테스트 분석가처럼 역할이 분명한 작업은 `.claude/agents/*.md`로 만든다.

7. Claude Code 실행 설정 도입

   프로젝트별 permissions, hooks, 도구 설정이 필요할 때 `.claude/settings.json`을 추가한다.

8. 개인 로컬 설정 분리

   팀에 공유하지 않을 개인 설정은 `.claude/settings.local.json`에 둔다.

9. MCP 설정 도입

   외부 도구나 데이터 연결이 필요할 때 `.mcp.json`을 추가한다.

## 25. 주의사항과 안티패턴

주의사항:

- `CLAUDE.md`는 핵심 지침이므로 너무 장황하게 만들지 않는다.
- 세부 설명은 `.claude/rules`, skill references, 일반 references 문서로 분리한다.
- `CLAUDE.local.md`와 `settings.local.json`에는 민감 정보를 저장하지 않는다.
- skill과 command의 역할을 구분한다.
- subagent는 역할을 좁고 명확하게 정의한다.
- hooks는 빠르고 예측 가능하게 유지한다.
- permissions는 최소 권한 원칙을 따른다.
- `.mcp.json`에 secret을 직접 저장하지 않는다.

안티패턴:

- 모든 내용을 `CLAUDE.md` 하나에 계속 누적하는 방식
- `AGENTS.md`와 `CLAUDE.md`에 같은 규칙을 중복 작성하는 방식
- skill 하나가 문서 작성, 코딩, 리뷰, 배포를 모두 담당하게 만드는 방식
- 모든 반복 prompt를 command로만 관리하는 방식
- subagent를 너무 포괄적인 범용 assistant로 만드는 방식
- settings 파일에 문서 스타일 가이드를 본문으로 작성하는 방식
- 개인 로컬 경로나 실험 설정을 팀 공유 설정에 넣는 방식
- hook에서 오래 걸리거나 파괴적인 작업을 자동 실행하는 방식

## 26. 참고 기준

이 문서는 Claude Code 공식 문서의 다음 주제를 기준으로 정리한다.

- Memory and `CLAUDE.md`
- Settings
- Slash commands
- Skills
- Subagents
- Hooks
- Permissions
- Model Context Protocol

공식 문서의 세부 설정명과 지원 범위는 Claude Code 버전과 실행 환경에 따라 달라질 수 있으므로, 실제 설정 파일을 작성할 때는 현재 사용 중인 Claude Code 환경의 최신 문서를 확인한다.
