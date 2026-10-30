# Herdr 사용 가이드 — main·sub·local 에이전트 운영

작성일: 2026-10-29 (Asia/Seoul)

Windows PowerShell 7에서 Herdr를 실행하고, Codex 2개와 OpenCode 1개,
일반 PowerShell 1개를 함께 사용하는 가이드다. 처음에는 2~6절을 순서대로
따라 하고, 다음 프로젝트부터는 8절의 시작 요청문을 재사용한다.

명령 구문은 Herdr 0.9.5의 설치된 CLI 도움말을 기준으로 확인했다.
화면 메뉴는 버전과 사용자 설정에 따라 달라질 수 있다.
이번 문서 작성에서는 실제 pane 생성·에이전트 재실행·이름 변경을 수행하지 않았다.

## 목차

1. 도구와 역할 이해하기
2. PowerShell을 열고 Herdr 실행하기
3. 에이전트 3개와 터미널 1개 배치하기
4. 각 pane에서 에이전트 실행하기
5. Pane과 에이전트 이름 정하기
6. 구성 확인과 첫 요청 보내기
7. 세 에이전트로 실제 작업하기
8. 새 프로젝트에서 같은 구성을 반복 사용하기
9. 종료하고 다음에 다시 시작하기
10. 문제 해결
11. 자주 쓰는 명령과 확인 목록
12. 관련 문서와 확인 범위

## 1. 도구와 역할 이해하기

### 1.1 각 도구의 역할

| 도구 | 하는 일 |
| --- | --- |
| PowerShell 7 | 명령을 입력하는 셸. Herdr와 에이전트를 시작한다 |
| Herdr | 터미널을 분할하고 실행 중인 에이전트와 상태를 관리한다 |
| Codex | main·sub 역할의 대화와 도구 실행을 담당한다 |
| OpenCode | local 역할의 대화와 파일·명령 도구를 담당한다 |
| Ollama | OpenCode가 선택한 로컬 모델의 추론을 수행한다 |

Herdr가 모델을 직접 실행하는 것은 아니다. Codex 모델은 Codex에서,
Gemma·Qwen 등 로컬 모델은 OpenCode에서 선택한다.

### 1.2 이름과 역할

| 이름 | 실행 프로그램 | 담당 |
| --- | --- | --- |
| main | Codex | 요청 접수·설계·분배, 모든 문서 최초 초안, 통합·최종 보고 |
| sub | Codex | 지정된 정보 수집·반복 검증·기존 문서의 지정 범위 갱신 |
| local | OpenCode | 제한된 검토·요약·추출·불일치 후보 반환, 승인된 제한 작업 |
| terminal | PowerShell | 조사·검증용 일반 명령 실행. AI 에이전트가 아님 |

이 문서의 main·sub·local은 기존 협업 문서의 sol·luna·gemma에 대응한다.
기존 문서는 이전 이름과 과거 pane ID를 포함하므로 현재 상태로 간주하지 않는다.
역할 이름을 바꾼다고 기존 프로젝트의 지침이나 실행 중 에이전트가 자동 변경되지는 않는다.

local의 실제 모델은 Gemma 또는 Qwen 등으로 변경할 수 있다. main·sub도 모델을
바꿀 수 있다. 역할 이름과 모델 이름은 별도로 기록한다.

### 1.3 화면의 단위와 이름

```text
Herdr 서버/세션
└─ Workspace: 프로젝트 작업 공간
   └─ Tab: pane 배치를 담는 화면
      ├─ Pane: main
      ├─ Pane: sub
      ├─ Pane: local
      └─ Pane: terminal
```

| 항목 | 의미 | 예 |
| --- | --- | --- |
| Workspace 이름 | 작업 공간의 표시 이름 | my-project |
| Tab 이름 | 탭의 표시 이름 | agents |
| Pane ID | 명령 대상인 고유 핸들 | wC:p7 |
| Pane 표시 이름(label) | 분할 영역에 붙이는 이름 | sub |
| 에이전트 이름 | `agent prompt` 등에서 사용하는 등록 이름 | sub |
| 에이전트 종류 | 실행 프로그램 종류 | codex, opencode |
| 터미널 제목(title) | 실행 프로그램이 갱신하는 제목 | OpenCode, 현재 작업 제목 |
| 모델 | 실제 응답을 생성하는 모델 | OpenCode에서 선택한 Qwen |

**Rename Pane은 pane 표시 이름을 바꾼다. 에이전트 이름 등록은 별도다.**
구분하기 쉽도록 표시 이름과 에이전트 이름을 같게 맞춘다.
Pane ID는 예시를 복사해 쓰지 말고 실제 조회 결과를 사용한다.

## 2. PowerShell을 열고 Herdr 실행하기

### 2.1 터미널 열기

Windows 시작 메뉴에서 PowerShell 7을 일반 실행하거나, Windows Terminal에서
PowerShell 프로필을 선택한다. Zed에서는 프로젝트 폴더를 연 뒤 터미널 패널을
연다. Zed의 명령 팔레트에서 terminal을 검색해 새 터미널을 열 수도 있다.

AI 대화 입력란과 셸 입력란은 다르다. 셸에서는 `PS D:\...>` 같은 프롬프트가
보인다. 아래 명령은 AI 대화 입력란이 아니라 PowerShell에 입력한다.

```powershell
$PSVersionTable.PSVersion
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

PowerShell 버전의 Major가 7인지 확인한다. 두 번째 명령은 `False`이면 일반 권한,
`True`이면 관리자 권한이다. PowerShell 7 선택 자체는 관리자 실행 설정이 아니다.

### 2.2 실행 명령과 작업 폴더 확인

```powershell
Get-Command rtk, herdr, codex, opencode
Set-Location -LiteralPath 'D:\projects\my-project'
Get-Location
rtk proxy herdr --version
```

`my-project`는 실제로 존재하는 프로젝트 폴더로 바꾼다. 새 프로젝트를 만드는 절차는
project-workflow의 INIT 지침을 따른다. 이 가이드는 프로젝트 초기화를 대신하지 않는다.

Herdr를 시작한다.

```powershell
rtk proxy herdr
```

`herdr`는 서버를 시작하거나 기존 세션에 연결한다. 기존 세션이 있으면 전에 열었던
workspace와 pane이 보일 수 있다. 바깥 PowerShell에서 폴더를 바꿨다는 이유로
기존 pane의 작업 폴더까지 바뀌었다고 판단하지 않는다.

### 2.3 Herdr 내부와 프로젝트 확인

Herdr 내부의 셸 프롬프트에서 확인한다.

```powershell
$env:HERDR_ENV
$env:HERDR_WORKSPACE_ID
$env:HERDR_TAB_ID
$env:HERDR_PANE_ID
Get-Location
rtk proxy herdr workspace list
rtk proxy herdr pane list --workspace $env:HERDR_WORKSPACE_ID
```

`HERDR_ENV`는 `1`이어야 한다. 기존 workspace가 다른 프로젝트라면 해당 작업을
그대로 두고 새 workspace를 만든다. 다음은 사용자가 새 프로젝트 공간을 만들 때의 예다.

```powershell
rtk proxy herdr workspace create --cwd 'D:\projects\my-project' --label my-project --focus
```

새로 열린 workspace의 PowerShell로 이동한 뒤 다음 절을 진행한다.

## 3. 에이전트 3개와 터미널 1개 배치하기

### 3.1 완성할 배치

가로 공간이 충분한 화면에서 다음 2×2 배치를 사용한다.

```text
+----------------------+----------------------+
| main: Codex          | sub: Codex           |
+----------------------+----------------------+
| terminal: PowerShell | local: OpenCode      |
+----------------------+----------------------+
```

일반 terminal을 남겨두면 에이전트를 종료하지 않고도 설치·파일·테스트 명령을
실행할 수 있다. 에이전트 대화창에 PowerShell 명령을 셸 명령처럼 입력하지 않는다.

### 3.2 첫 셸에서 세 번 분할하기

**새 탭에 셸 pane 하나만 있을 때** 아래 블록을 한 번 실행한다.
이미 pane이 있으면 목록을 먼저 보고 기존 구성을 재사용한다.
블록은 pane을 생성하므로 반복 실행하면 중복 pane이 생긴다.

```powershell
$projectPath = (Get-Location).Path
$mainPane = $env:HERDR_PANE_ID

$splitSub = rtk proxy herdr pane split --current --direction right --cwd $projectPath --no-focus | ConvertFrom-Json
$subPane = $splitSub.result.pane.pane_id
if (!$subPane) { throw 'sub pane 생성 실패. 출력을 확인하세요.' }

$splitLocal = rtk proxy herdr pane split --pane $subPane --direction down --cwd $projectPath --no-focus | ConvertFrom-Json
$localPane = $splitLocal.result.pane.pane_id
if (!$localPane) { throw 'local pane 생성 실패. 기존 pane부터 확인하세요.' }

$splitTerminal = rtk proxy herdr pane split --pane $mainPane --direction down --cwd $projectPath --no-focus | ConvertFrom-Json
$terminalPane = $splitTerminal.result.pane.pane_id
if (!$terminalPane) { throw 'terminal pane 생성 실패. 기존 pane부터 확인하세요.' }

rtk proxy herdr pane rename $mainPane main
rtk proxy herdr pane rename $subPane sub
rtk proxy herdr pane rename $localPane local
rtk proxy herdr pane rename $terminalPane terminal
rtk proxy herdr pane list --workspace $env:HERDR_WORKSPACE_ID
```

각 명령의 생성 결과에 ID가 있는지 확인하며 순서대로 실행한다.
실패한 단계 이후의 명령은 진행하지 않는다. `--no-focus`는 원래 pane의 포커스를
유지한다. 다른 pane에서도 같은 프로젝트 폴더가 열렸는지 확인한다.

### 3.3 이동·크기 조절·탭 관리

마우스로 pane을 선택한다. 우클릭으로 Herdr 메뉴가 열리는 설정에서는 Rename Pane
등을 사용할 수 있다. 우클릭이 프로그램으로 전달되는 설정이라면 CLI를 사용한다.
CLI로 현재 pane을 확대하고 되돌리는 예다.

```powershell
rtk proxy herdr pane zoom --current --toggle
rtk proxy herdr pane resize --current --direction right --amount 0.05
rtk proxy herdr tab list --workspace $env:HERDR_WORKSPACE_ID
```

다른 프로젝트는 workspace, 같은 프로젝트의 다른 화면은 tab으로 나눌 수 있다.
추가 화면이 필요할 때만 생성한다.

```powershell
rtk proxy herdr tab create --workspace $env:HERDR_WORKSPACE_ID --cwd $projectPath --label extra --no-focus
```

## 4. 각 pane에서 에이전트 실행하기

### 4.1 main과 sub: Codex 실행

main 표시의 pane을 클릭해 셸 프롬프트에서 실행한다.

```powershell
rtk proxy codex --no-daemon --sandbox workspace-write --ask-for-approval on-request
```

sub pane에서도 같은 명령으로 별도 Codex를 실행한다. 기존 Codex가 실행 중이면
다시 실행하지 않는다. 로그인·신뢰 확인이 나오면 사용자가 내용을 확인한다.

Codex 대화 화면에서 `/model`로 사용 가능한 모델을 선택한다.
main·sub는 역할 이름이며 특정 모델을 강제하지 않는다.
`--no-daemon`은 이 환경의 기존 실행 관례를 따른 것이다.
실제 옵션은 `rtk proxy codex --help`로 확인한다.
[Codex 공식 명령 안내](https://learn.chatgpt.com/docs/cli/slash-commands)

### 4.2 local: Ollama와 OpenCode 실행

Ollama가 실행 중인지 terminal pane에서 먼저 확인한다.

```powershell
rtk proxy ollama list
rtk proxy ollama ps
rtk proxy powershell -NoProfile -Command "Invoke-RestMethod http://127.0.0.1:11434/api/version -TimeoutSec 5"
```

응답하지 않으면 시작 메뉴에서 Ollama를 실행한다. 기존 서버가 있는데
`ollama serve`를 중복 실행하지 않는다.

사용자가 정한 local 운영 목표는 Gemma 4 12B 32K와 `local-worker`다. 이는 전역 설정이나
새 세션에 자동 적용된다는 뜻이 아니다. 실행 전에 실제 선택된 모델·프로필을 화면과
설정에서 대조하고, 목표와 다르면 사용자가 정한 값을 임의로 바꾸지 말고 차이를 보고한다.

```powershell
rtk proxy opencode --model ollama/gemma4:12b-32k --agent local-worker
```

`local-worker`는 자료 조회를 허용하고 파일 변경과 셸 실행은 승인을 요청하는 프로필이다.
읽기 전용 프로필은 아니다. 요청된 입력과 작업 범위를 지키며, 사용자의 승인 없이 파일을
수정하거나 승인 대상 작업을 실행하지 않는다. 요청문에 “수정해 주세요”라고 적어도
승인 절차가 생략되지는 않는다.

Qwen 모델과 `local-reader`는 선택 가능한 읽기 전용 검토 대안이다. 읽기 전용 작업을
명시적으로 선택한 경우에만 다음 명령을 사용한다.

```powershell
rtk proxy opencode --model ollama/qwen3.5:9b-32k --agent local-reader
```

OpenCode 대화 화면의 `/models`에서 다른 모델을 선택할 수 있다. 역할 이름 local은
모델이나 프로필을 바꿔도 유지한다.
[OpenCode 공식 대화형 사용법](https://opencode.ai/docs/tui/)

| OpenCode 프로필 | 조회 | 파일 변경 | 셸 실행 |
| --- | --- | --- | --- |
| local-worker (기본) | 허용 | 승인 요청 | 승인 요청 |
| local-reader (읽기 전용 대안) | 허용 | 거부 | 거부 |

읽기 전용 검토가 목적일 때 `local-reader` 대안을 선택한다. 기본 프로필인
`local-worker`에서도 사용자가 승인하지 않은 파일 변경이나 셸 실행은 하지 않는다.
프로필과 실제 모델 선택을 확인한다. 기존 세션은 이전 설정을 유지할 수 있다.
자세한 설치·프로필 설정은 [로컬 모델 가이드](../../local-llm/docs/01-opencode-local-model-guide.md)를 따른다.

### 4.3 terminal을 공유 명령·검증 공간으로 사용하기

terminal은 main·sub·local이 필요에 따라 함께 쓰는 일반 셸 pane이다. AI 대화 내용과
셸에서 실제 실행된 명령·출력·오류는 구분한다. 폴더·파일·경로·버전의 정확한 조회,
Git 상태와 diff 확인, 프로젝트에 적용되는 테스트·빌드·오류 확인, Ollama 연결·모델
목록·적재 상태 확인, 사용자가 직접 실행하는 명령에 사용한다. 정확한 목록처럼 PowerShell로
얻을 수 있는 결과는 에이전트 모델에 통과시키지 않고 직접 조회할 수 있다.

역할은 다음처럼 나눈다. main은 목적·범위·완료 기준을 정한다. sub는 일반 terminal에서
조사·검증 명령을 실행하고 실제 출력·오류·종료 상태를 확인한다. local은 필요한 출력
일부를 받아 해석·요약·검토한다. local에게 terminal 제어나 상위 에이전트 통신을 기본
임무로 맡기지 않는다. 사용자는 terminal에서 직접 명령을 실행하고 결과를 판단할 수 있다.

동시에 명령 실행 주체는 한 명으로 제한한다. 명령을 보내기 전 현재 작업 폴더, 셸 프롬프트,
전경 프로세스와 진행 중인 작업이 없는지 확인한다. 테스트나 빌드가 실행 중일 때 다른
명령을 주입하지 않고, 사용자가 직접 terminal을 쓰고 있으면 방해하지 않는다. 담당자의
작업이 끝나 셸 프롬프트로 돌아온 뒤 다음 실행 주체가 사용한다. 자동 잠금이나 명령 중재
기능이 있다고 가정하지 않는다.

에이전트 간 메시지는 각자의 제어 도구에서 Herdr agent prompt로 직접 보낸다. terminal은
메시지 중계에 쓰지 않는다. 사람이 terminal에서 직접 Herdr 명령을 실행하는 것은 별개다.
Herdr pane run의 성공은 명령 접수일 수 있으므로, 실제 출력·오류·종료 상태 또는 셸 프롬프트
복귀를 확인한다. 결과는 필요한 범위만 읽고 상태 조회를 반복하지 않는다. 기존 pane
read/run/read 예시는 7.2절을 따른다. 자세한 명령 동작은 [Herdr Agent automation](https://herdr.dev/docs/agent-automation/)을 참조한다.

장시간 서버 실행이나 로그 감시가 terminal을 계속 점유하면 별도 pane 추가를 제안할 수
있으며, 구성은 사용자 요청 범위에서만 한다. 기본 terminal은 짧은 조회·검증용으로 둔다.
Pane ID는 현재 목록이나 생성 결과에서 확인한 값을 사용한다. 아래 예시의 $terminalPane은
실제 조회된 pane ID로 지정하며 과거 pane ID를 고정하지 않는다. 처음 셸에서 만든 변수는
다른 PowerShell에 자동 전달되지 않으므로 사용할 셸에서 다시 조회·지정한다.
## 5. Pane과 에이전트 이름 정하기

### 5.1 Rename Pane과 에이전트 이름 등록

우클릭 메뉴의 **Rename Pane**으로 main·sub·local·terminal을 지정할 수 있다.
이는 표시 이름 변경이며, 실행 프로그램·모델·pane ID를 바꾸지 않는다.

에이전트를 실행한 후 terminal pane에서 조회한다.

```powershell
rtk proxy herdr pane list --workspace $env:HERDR_WORKSPACE_ID
rtk proxy herdr agent list
```

Pane 목록의 `label`과 `pane_id`, 에이전트 종류를 대조한다.
다음 변수의 값은 **자신의 실제 ID로 바꿔서** 입력한다.
아래 `실제-...-ID` 문자열은 실행 가능한 ID가 아니다.

```powershell
$mainPane = '실제-main-pane-ID'
$subPane = '실제-sub-pane-ID'
$localPane = '실제-local-pane-ID'
$terminalPane = '실제-terminal-pane-ID'

rtk proxy herdr agent rename $mainPane main
rtk proxy herdr agent rename $subPane sub
rtk proxy herdr agent rename $localPane local
rtk proxy herdr agent get main
rtk proxy herdr agent get sub
rtk proxy herdr agent get local
```

이름은 소문자 영문으로 시작하고 소문자·숫자·`_`·`-`를 포함한 32자 이내여야 한다.
같은 서버의 실행 중 에이전트 사이에서 이름이 고유해야 한다.
terminal은 AI가 없으므로 `agent rename`하지 않는다.

### 5.2 CLI로 시작하며 이름을 붙이는 대안

수동 실행과 이름 등록 대신, terminal에서 **비어 있는 셸 pane**에 시작할 수도 있다.
아래는 방법 설명이며 이미 4절에서 실행했다면 중복 실행하지 않는다.

```powershell
rtk proxy herdr agent start main --kind codex --pane $mainPane -- --no-daemon --sandbox workspace-write --ask-for-approval on-request
rtk proxy herdr agent start sub --kind codex --pane $subPane -- --no-daemon --sandbox workspace-write --ask-for-approval on-request
rtk proxy herdr agent start local --kind opencode --pane $localPane -- --model ollama/gemma4:12b-32k --agent local-worker
```

읽기 전용 검토를 선택한 경우에만 위 local 예제의 모델과 프로필을
`ollama/qwen3.5:9b-32k`와 `local-reader`로 바꾼다.

`agent start`는 pane을 만들지 않는다. 지정한 pane의 전경에 셸 프롬프트가 있어야 한다.
로그인·승인 등으로 `agent_not_ready`가 나오면 출력을 읽고 해결한다.
시작 실패 메시지만 보고 같은 명령을 곧바로 재전송하지 않는다.

### 5.3 이름과 역할은 별도로 전달

이름 등록은 AI에게 역할을 설명하는 행위가 아니다. 각 에이전트의 첫 요청에
이 가이드의 경로와 자신이 맡을 역할을 명시한다.
에이전트가 종료·교체되면 등록 이름이 사라질 수 있으므로 다음 실행에서 다시 확인한다.

## 6. 구성 확인과 첫 요청 보내기

terminal에서 목록을 조회한다.

```powershell
rtk proxy herdr pane list --workspace $env:HERDR_WORKSPACE_ID
rtk proxy herdr agent list
```

확인할 항목은 다음과 같다.

- 대상 탭에 pane 4개, 대상 프로젝트의 에이전트 3개가 있다.
- main·sub는 codex, local은 opencode다. terminal에는 AI가 없다.
- 네 pane의 작업 폴더가 대상 프로젝트와 일치한다.
- 표시 이름과 에이전트 이름이 대응하고, 실제 모델은 각 프로그램 화면에서 확인했다.
- 로그인·신뢰·승인 대화가 남아 있지 않다.

서버에 다른 프로젝트도 있으면 `agent list`에는 그 에이전트도 포함될 수 있다.
반환된 workspace·tab·pane ID로 범위를 확인한다.

main에 직접 입력할 첫 요청 예시다.

```text
D:\projects\_docs\guides\herdr-usage-guide.md의 역할·협업 규칙을 읽어 주세요.
당신은 main입니다. 현재 프로젝트 지침을 먼저 확인하고,
프로젝트 경로·자신의 역할·현재 에이전트 구성을 보고하세요.
아직 업무 파일을 변경하지 마세요.
```

main에는 “sub와 local에도 역할 확인을 요청하고 결과를 확인해 주세요”라고 요청할 수 있다.
직접 CLI로 보내려면 terminal에서 다음과 같이 실행한다.

```powershell
rtk proxy herdr agent prompt sub '당신은 sub입니다. 현재 프로젝트 지침과 D:\projects\_docs\guides\herdr-usage-guide.md의 역할 규칙을 읽고 작업 폴더와 담당을 보고하세요. 파일은 수정하지 마세요.' --wait --timeout 60000
rtk proxy herdr agent read sub --source recent-unwrapped --lines 80
```

AI가 다른 AI에 전달할 때는 자신의 제어 도구에서 `agent prompt`를 직접 실행한다.
일반 terminal을 메시지 중계용으로 쓰지 않는다. 사람이 terminal에서 직접 제어 명령을
실행하는 것과는 구분한다.

## 7. 세 에이전트로 실제 작업하기

### 7.1 작업 지시 형식

```text
목적: 무엇을 확인하거나 완성할 것인가
입력: 읽을 파일·폴더·자료 범위
허용 작업: 조회 / 지정 파일 수정 / 지정 명령 실행
수정 가능 파일: 정확한 경로, 없으면 없음
출력 형식: 표 / 근거와 불일치 후보 / 변경 요약
완료 기준: 어떤 결과를 보면 완료로 판단할 것인가
```

짧은 일은 main만 처리한다. 추가 검토가 필요한 작업에 sub·local을 참여시킨다.
같은 파일은 동시에 수정하지 않는다. 모든 문서 최초 초안과 최종 통합은 main이 맡는다.
sub는 지정된 기존 문서를 갱신하고, local은 작은 입력 범위의 검토·추출을 우선한다.
모델 응답이 일치해도 원문·실행 결과 대조를 생략하지 않는다.

### 7.2 작업 예시

| 작업 | main | sub | local |
| --- | --- | --- | --- |
| 환경 점검 | 점검 기준·최종 판단 | 명령 실행·실제 출력 수집 | 제한된 결과의 누락 검토 |
| 문서 작성 | 최초 초안·결정·통합 | 근거 확인·지정 갱신 | 모순·누락 후보와 근거 반환 |
| 파일 정리 | 기준·변경 범위 결정 | 참조·영향 조사 | 지정 자료의 불일치 검토 |
| 분류·추출 | 필드·완료 기준 정의 | 표본 대조 | 분할한 입력 처리 |

sub의 조사·검증 명령은 프로젝트 운영 지침에 따라 일반 PowerShell pane에서 수행한다.
그때마다 해당 pane에 셸 프롬프트가 있고 다른 명령이 실행 중이지 않은지 확인한다.

```powershell
rtk proxy herdr pane read $terminalPane --source recent-unwrapped --lines 30
rtk proxy herdr pane run $terminalPane 'rtk git status --short'
rtk proxy herdr pane read $terminalPane --source recent-unwrapped --lines 80
```

이 terminal 역할 분담과 동시 사용 규칙은 4.3절을 따른다. 실제 제어는 해당 pane의 현재
ID를 사용하며, 에이전트 간 메시지를 terminal로 중계하지 않는다.
이 예시는 AI의 제어 도구 등 **다른 pane에서** terminal을 제어할 때 사용한다.
사람이 이미 terminal에 있다면 `rtk git status --short`를 직접 입력하면 된다.
`pane run` 성공은 실행 완료가 아니다. 실제 출력·오류·프롬프트 복귀를 확인한다.

### 7.3 상태와 결과 확인

| 상태 | 해석과 다음 행동 |
| --- | --- |
| working | 작업 중. 상태와 출력을 확인하며 기다린다 |
| idle / done | 입력 대기 또는 완료 표시. 성공·검증 완료를 뜻하지 않으므로 응답과 완료 기준을 대조한다 |
| blocked | 승인·질문 UI 확인. 사용자의 판단이 필요한 대화를 임의로 수락하지 않는다 |
| unknown | 상태 판별 불가. 완료로 판단하지 않고 화면과 전경 프로세스를 확인한다 |

짧은 에이전트 작업은 `agent prompt --wait`로 한 번 제출하고 도구 대기한 뒤, 응답을 필요한
범위에서 한 번 읽어 검증하는 흐름을 우선한다. 상위가 도구 대기 중 `working`으로 보일 수
있으며 그 표시만으로 지속 추론이나 추가 비용 발생을 단정하지 않는다. 이는 도구 호출 안에서
기다리는 상태이지 실제 agent `idle`과 같다는 뜻도 아니다.

```powershell
rtk proxy herdr agent prompt local '짧은 작업' --wait --timeout 60000
rtk proxy herdr agent read local --source recent-unwrapped --lines 80
```

기본 `--wait`는 `idle`, `done`, `blocked`를 반환할 수 있다. `blocked`면 승인 UI를 읽고
사용자 판단을 받는다. `idle`·`done`이나 prompt 전달 성공은 성공 검증이 아니다. 반드시 읽은
응답과 완료 기준을 대조한다. `timeout`, `agent_prompt_stalled`, `blocked`가 나오면 표시된
실제 상태·오류를 확인하고 보고하며 같은 요청을 자동 재전송하지 않는다. 공식 `agent wait`도
상태를 기다리는 도구일 뿐 개별 작업의 성공을 보장하지 않는다. 모델 기반 반복 `get`·`read`와
짧은 wait 루프는 기본 절차에서 제외한다.

#### 컨텍스트 확인과 압축

작업을 전달하기 전에 현재 컨텍스트 표시를 한 번 확인하고, 작업 중에는 반복 조회하지 않는다.
표시가 없거나 해석할 수 없으면 미확인으로 기록한다. Codex 화면의 남은 비율과 OpenCode의
사용 비율은 방향이 다를 수 있으므로 표시 라벨을 확인한다. 남은 컨텍스트가 20% 이하일 때를
압축 검토 기준으로 삼는다. 이는 공식 제한이 아니라 사용자가 채택한 운영 기준이며, 사용률
표시라면 80% 이상에 해당한다.

sub가 입력 대기 중이고 승인·질문 화면이 아닐 때 작업 경계에서 /compact를 사용할 수 있다.
실행 중인 작업은 상태만으로 중단하지 않는다. 압축은 한 번 실행하고 도구 대기 후 잔량을 한 번
확인한다. 실패하거나 승인 대기이면 자동 반복 재시도하지 않고 실제 상태를 보고한다.
[Codex의 /compact 안내](https://learn.chatgpt.com/docs/cli/slash-commands#keep-transcripts-lean-with-compact)에
따르면 압축 과정에서 세부 사항이 요약될 수 있다. 압축은 모델 최대 컨텍스트 확대와 다른
기능이며 처리 비용이 발생할 수 있다. 임의로 모델이나 컨텍스트 상한을 변경하지 않는다.

압축 전후에 역할, 현재 작업, 완료된 작업 ID, 실제 결과 위치를 확인해 끝난 작업을 다시
수행하지 않도록 한다. 새 인계 파일 체계는 만들지 않는다. local은 독립 작업을 시작할 때
기존 대화를 보존한 채 새 대화를 우선 검토할 수 있다. 이어지는 작업은 필요한 맥락을 유지하고,
새 대화를 열었다면 모델·프로필·입력 범위를 다시 확인한다. 매 요청마다 대화를 초기화하지 않는다.

**2026-10-29 과거 관측:** 대기 중인 sub에서 /compact 실행 약 19초 뒤 남은 컨텍스트가
10%에서 94%로 표시됐다. local의 약 52% 사용 표시는 별도의 당시 관측이다. 두 값은 날짜가
붙은 개별 화면 관측이며 현재 상태나 모든 실행의 결과를 뜻하지 않는다.
### 7.4 작업 범위와 결과 전달

local은 지정된 실제 작업과 간결한 결과 출력만 맡는다. 상태 대기와 상위 에이전트 메시지
전송은 local의 기본 임무가 아니다. 짧은 작업 지시 하나에 긴 통신·대기 절차까지 붙이면
업무 범위가 커지고 수행 부담이 늘 수 있다.

단순 PowerShell 명령으로 정확히 얻을 수 있는 파일 목록이나 버전 정보는 PowerShell을
우선한다. 모든 작업을 세 에이전트에 차례로 통과시키지 않는다. `main → sub → local` 분담은
검토 범위가 나뉘거나 독립 작업이 실제로 도움이 될 때만 사용한다.

결과 전달은 크기에 맞춘다. 작은 결과는 local의 작업 응답 본문에 핵심만 짧게 남기고,
상위는 단일 `agent prompt --wait`의 결과를 읽는다. local이 별도 상위 알림을 보내지 않는다.
모든 결과를 알림과 재조회 단계로 분리할 필요는 없다. 큰 결과는
사용자가 허용한 경로에 승인된 결과물로 한 번 남기고, 상위는 필요한 부분만 읽는 방식을
검토한다. 허용 경로가 정해지지 않았으면 새 파일이나 경로를 만들거나 지어내지 않는다.
이 가이드에서는 결과 저장 체계나 자동화를 구현하지 않는다.

모델이 완료 문구를 보냈다는 사실, 실제 턴 종료, 압축 종료, 결과 준비 완료는 서로 다를 수
있다. 모델이 알림 직후에도 추가 출력을 생성하며 `working`일 수 있다. Herdr 화면 알림은
상태 변화 UI이며 `agent prompt`를 자동 전달하지 않는다. 화면 알림만으로 상위에게 결과가
전달됐다고 보지 않는다.

실제 idle 대기와 자동 재개가 반드시 필요한 긴 작업만 별도 예외로 다룬다. 그 경우 모델 밖의
도구가 작업별 결과 준비와 해당 실행의 실제 종료를 확인한 뒤 상위에게 통지하는 방식을 향후
구현·검증 대상으로 둘 수 있다. 아직 미구현이며 현재 사용 가능하다고 가정하지 않는다.
프로세스 idle 표본만으로 성공을 판정하지 말고 작업 ID별 성공·실패·blocked·timeout을 나눠야
한다. 이전 작업 종료를 새 작업 완료로 오인하지 않도록 작업과 결과의 연결도 검증한다.

sub는 필요한 경우 local 원문을 `agent read`로 직접 검토하고, main은 sub의 검토로 충분하면
그 결과만 읽는다. 오류나 중요한 판단에서만 main이 local 원문을 추가 확인한다. 모든 상위가
같은 원문을 읽도록 강제하지 않는다. 사용자에게는 대화 전문 대신 최종 결과·필요한 근거·남은
한계를 보고한다. 전체 대화를 결과 저장소처럼 쓰면 이전 대화·추론·긴 출력까지 함께 읽혀
입력 토큰이 커질 수 있다. 화면에서 추론을 숨기는 것과 실제 생성량을 줄이는 것은 다르다.

출력이 잘리면 먼저 `agent read --source recent-unwrapped --lines N`으로 필요한 범위를 다시
읽는다. 회수할 수 없을 때에만 UTF-8 임시 결과 파일을 대안으로 검토하고, 허용된 실제 경로를
알린다. 중간 재작성·중복 전달·불필요한 조회를 줄이면 토큰을 아낄 수 있지만, 원문을 읽는
토큰은 남는다. 크레딧 절감률이나 사용량 0을 보장하지 않는다.

### 7.5 관측 기록과 후속 검증 제안

**2026-10-29 LIST-02 관측:** local이 짧은 완료 알림을 보낸 뒤에도 출력을 계속 생성했다.
화면에는 약 33초의 compaction과 약 15초의 추가 응답이 표시됐다. sub의 첫 원문 읽기는
`agent_not_idle`로 거부됐고, visible 조회 후 한 번 대기해 idle/done에 도달한 다음 180줄·
360줄로 읽기 범위를 늘렸다. local 결과에서 `_docs`와 `_ideas`의 선행 밑줄이 빠졌다.
main과 sub의 대기 상태 표본은 있었지만 지속 idle의 증거와 정확한 토큰·크레딧 계측은 없었다.
이는 local 알림 뒤 sub가 원문을 기다려 조회한 LIST-02 시험 흐름의 관측이다. 그 흐름을 모든
작업에 기본 강제하지 않으며, 오류와 조회 부담이 드러난 한 사례로 보존한다.

**2026-10-29 LIST-03-B 관측:** 새 OpenCode 대화에서 `agent prompt --wait`로 한 번
조회하고 70줄의 `recent-unwrapped`를 읽었다. 화면상 `Build · Gemma4 12B 16K`는 이전과
같았지만 실제 `local-worker` 프로필은 확인되지 않았고 새 대화의 초기 컨텍스트도 달랐다.
local은 `Read .`를 한 번 수행했으며 해당 출력에 반복 생성·compaction 표시는 없었다.
독립 PowerShell 대조는 폴더 17개·파일 4개였고 local은 항목을 한 목록에 섞고 `_docs`·
`_ideas`의 밑줄을 누락했다. 화면에 28초가 표시됐지만 토큰·크레딧은 미측정이다.
전달 절차는 짧아졌으나 정확성은 통과하지 못한 시험으로 기록한다.

같은 날짜 이후 local 화면은 Build / Gemma4 12B 16K였고, 관측한 사용자 전역 설정은
`model`·`small_model`이 `ollama/gemma4:12b-16k`, `default_agent`가 `local-worker`였다.
가이드의 Gemma 4 12B 32K / `local-worker`는 사용자가 정한 운영 목표로 유지한다. 화면의
실행 모델은 16K라 모델 목표와 달랐다. 전역 `default_agent` 이름은 `local-worker`였지만,
그 사실만으로 해당 실행 세션의 프로필까지 확인된 것은 아니다. compaction이 모델·프로필
차이를 일으켰다고 단정할 근거는 없다. 이는 해당 날짜의 관측 기록이지 영구 현재값이 아니다.
실행 시 목표 모델·프로필을 명시하고 실제 선택을 대조하며, 우선 짧은 새 세션에서 확인한다.
auto compaction 끄기나 컨텍스트 확대는 1차 해결책으로 삼지 않고 별도 검증 사항으로 둔다.

이전 개선 비교안은 아래에 이력으로 보존한다. 당시 제안이며 실행 결과나 현재 기본 운영
규칙으로 간주하지 않는다.

| 안 | 비교할 흐름 | 상태 |
| --- | --- | --- |
| A | 기존 모델 직접 알림과 화면 원문 조회 | 비교 기준 |
| B | local은 작업만 하고 작은 결과를 간결하게 전달 | 제안·미검증 |
| C | 결과물과 외부 실제 종료 통지 사용 | 외부 통지 도구 구현 후에만 검증 |

각 회차에서 이름의 문자 보존·누락·추가, 도구와 조회 경로 근거, 결과 후 불필요한 생성,
compaction 유무, 결과 준비·알림·최종 idle 순서, 상위 조회 횟수와 읽은 양, 경과 시간을
기록한다. 입력·출력·추론 토큰과 크레딧은 실제 계측 가능한 값만 적고 나머지는 미측정으로
표시한다. main/sub가 실제 idle인 상태와 도구의 wait 안에서 대기 중인 상태도 구분한다.
반복 생성·불필요한 재조회가 없고 결과가 정확하며 긴 결과가 재전달되지 않는지 확인한 뒤에만
운영 방식을 채택한다. 자동 재시험하거나 자동 채택하지 않는다.

현재 권장 흐름(별도 테스트 대기): 단순하고 정확한 PowerShell 조회는 셸에서 직접 한다.
에이전트 작업이 필요하면 짧게 지시하고 `agent prompt --wait` 한 번으로 기다린 뒤 필요한
출력만 읽어 검증한다. 이 문서 수정만으로 해당 흐름의 테스트가 완료된 것은 아니다.

## 8. 새 프로젝트에서 같은 구성을 반복 사용하기

### 8.1 공통 규칙과 프로젝트별 정보 분리

| 공통으로 재사용 | 실행할 때 확인·지정 |
| --- | --- |
| main·sub·local의 역할 | 프로젝트 절대 경로·프로젝트 지침 |
| 3개 에이전트와 terminal 구성 | 현재 workspace·tab·pane ID |
| 전달 형식·검증·동시 수정 방지 | 실제 모델·프로필·에이전트 상태 |
| 일반 권한·실제 출력 확인 원칙 | 기존 pane 재사용 여부·이름 충돌 |

2026-10-29에 확인한 현재 프로젝트 pane 구성은 다음과 같다. 이는 해당 날짜의 관측
기록이며, pane ID를 향후 실행에서 재사용하도록 고정하는 값이 아니다.

| 프로젝트 | 탭 | 역할 | 당시 pane ID |
| --- | --- | --- | --- |
| `D:\projects` | `wC:t1` | main | `wC:p1` |
| `D:\projects` | `wC:t1` | sub | `wC:p7` |
| `D:\projects` | `wC:t1` | local | `wC:p8` |
| `D:\projects` | `wC:t1` | terminal | `wC:p9` |

재실행 후에도 pane 표시 이름은 남을 수 있지만 에이전트 등록 이름·모델·프로필은
달라질 수 있다. 매번 실제 pane과 실행 상태를 다시 조회하고, 에이전트 등록 이름·모델·
프로필을 확인하거나 필요한 경우 다시 등록한다.

이 문서를 공통 운영 지침으로 참조하고 아래 요청문을 재사용한다.
프로젝트마다 가이드 사본을 만들지 않는다. 기존 AGENTS.md가 있으면 먼저 읽고,
필요할 때 이 가이드 참조를 추가하는 방식을 검토한다. 기존 지침을 통째로 덮어쓰지 않는다.
다른 도구가 같은 지침을 자동으로 읽는다고 가정하지 말고, 첫 역할 요청에서 경로를 알려준다.

프로젝트 지침에 남길 수 있는 참조 문구 예시다. 이 가이드 작성으로 해당 파일을
자동 생성하거나 수정하지는 않는다.

```text
Herdr로 협업할 때 D:\projects\_docs\guides\herdr-usage-guide.md를 참조한다.
역할은 main·sub·local이며, 실제 pane ID와 모델은 매 실행 시 확인한다.
프로젝트별 요구와 제약은 이 프로젝트의 지침·INTENT를 기준으로 확인한다.
```

### 8.2 매번 수행할 최소 순서

1. PowerShell에서 프로젝트 폴더로 이동하고 Herdr를 실행한다.
2. 대상 프로젝트 workspace인지 확인한다. 필요하면 새 workspace를 만든다.
3. 해당 프로젝트의 첫 pane에서 main용 Codex를 실행한다.
4. 아래 요청문을 main에 붙여 넣는다. 경로·모델·이름 접두어는 실제 값으로 바꾼다.
5. main의 구성 결과 표와 필요한 역할 확인 응답을 검토한다.

### 8.3 시작 요청문 템플릿

```text
D:\projects\_docs\guides\herdr-usage-guide.md를 읽고 다음 구성을 준비해 주세요.

프로젝트: D:\projects\my-project
이름 접두어: 없음
main 모델: 현재 제가 선택한 모델 유지
sub 모델: Codex에서 제가 선택할 수 있도록 실행 후 현재 선택을 보고
local 모델: ollama/gemma4:12b-32k
local 프로필: local-worker
위 값은 사용자가 정한 운영 목표입니다. 실행 세션과 전역 설정에 자동 적용된다고 가정하지
말고, 시작 시 실제 모델·프로필을 대조해 목표와 차이를 보고하세요. local은 지정된 작은
범위의 작업과 간결한 결과를 맡고, Herdr 상태 대기와 상위 통신 절차를 기본 지시로 받지
않습니다.

작업을 전달하기 전에 각 에이전트의 컨텍스트 표시를 한 번 확인하고, 작업 중 반복 조회하지
마세요. 화면 라벨을 확인해 남은 비율과 사용 비율을 구분하고 해석할 수 없으면 미확인으로
기록하세요. 남은 컨텍스트 20% 이하(사용률 표시라면 80% 이상)는 공식 제한이 아닌 운영상
압축 검토 기준입니다. 진행 중 작업은 상태만으로 중단하지 말고, sub가 입력 대기이며 승인·질문
화면이 아닐 때 작업 경계에서만 /compact를 검토하세요. 한 번 대기한 뒤 잔량을 한 번 확인하고,
실패·승인 대기이면 자동 재시도하지 마세요. 압축 전후 역할·현재 작업·완료 작업 ID·실제 결과
위치를 대조해 재실행을 막으세요. local은 독립 작업에 새 대화를 검토할 수 있지만 기존 기록을
삭제하거나 매 요청마다 초기화하지 마세요. 새 대화 후 모델·프로필·입력 범위를 다시 확인하세요.
압축과 모델 최대 컨텍스트 확대는 다르며 모델·상한을 임의 변경하지 마세요.
현재 Codex를 main으로 사용하고, 같은 탭에 sub(Codex), local(OpenCode),
terminal(일반 PowerShell)을 두어 총 4개 pane으로 구성해 주세요.
프로젝트의 AGENTS.md 등 적용 지침을 먼저 확인하세요.

Herdr 스킬을 적용하고 HERDR_ENV=1인지 확인하세요.
현재 workspace·작업 폴더·pane·에이전트·이름·상태부터 조회하세요.
다른 프로젝트 공간이면 기존 작업을 변경하지 말고 상황을 보고하세요.
같은 프로젝트의 적합한 pane은 재사용하고 부족한 pane만 분할하세요.
반환된 실제 ID를 사용하고 셸 프롬프트가 확인된 빈 pane에서만 시작하세요.
포커스는 main에 유지하고 표시 이름과 등록 에이전트 이름을 맞추세요.
다른 프로젝트와 이름이 충돌하면 기존 이름을 바꾸지 말고 접두어를 물어보세요.

sub와 local에 이 가이드 경로와 각자의 역할을 전달하세요. local에는 지정된 작업 범위만
요청하고 Herdr 상태 대기나 상위 통신 절차를 맡기지 마세요. 역할 확인은 필요한 경우
간결하게 한 번 받고, 추가 보고 단계를 기본으로 붙이지 마세요.
local-worker는 조회 허용, 파일 변경·셸 실행 승인 요청 프로필입니다. 작업 범위를 지키고
사용자 승인 없이 파일을 수정하거나 승인 대상 작업을 실행하지 마세요. 읽기 전용 검토를
명시적으로 선택한 경우에만 Qwen과 local-reader 대안을 사용하세요.
terminal은 AI를 실행하지 않은 셸로 남겨두세요.
접속 오류만으로 관리자 실행이라고 단정하지 말고 실제 권한을 구분하세요.
필요한 읽기 전용 조회는 실행 환경의 승인 절차에 따라 재시도하세요.
서버 재시작·프로그램 설치·전역 설정 변경·프로젝트 업무 파일 변경은 하지 마세요.
완료 시 역할·등록 이름·표시 이름·pane ID·폴더·상태·확인된 모델을 표로 보고하세요.
확인하지 못한 항목은 미확인으로 표시하세요.

단순 PowerShell 파일 목록이나 버전 조회는 셸에서 직접 처리하고, 모든 작업을 main→sub→local로
강제 분배하지 마세요. 필요한 작업에만 sub·local을 참여시키세요. local에는 지정된 작은 범위의 작업만 맡기고,
Herdr 상태 대기나 상위 통신 절차를 기본 작업으로 지시하지 마세요. 작은 결과는 검토할
local 작업 응답에 핵심만 짧게 포함하고, 큰 결과는 사용자가 허용한 실제 경로의 결과물로
분리하는 방안을 제안하되 외부 완료 통지 도구가 이미 구현됐다고 가정하지 마세요.
에이전트 작업은 짧은 prompt --wait 한 번으로 기다린 뒤 응답을 필요한 범위에서 읽고 검증하세요.
상위가 도구 대기 중 working으로 보일 수 있으며, 지속 추론이나 비용 발생으로 단정하지 마세요.
blocked·timeout·stalled는 성공이 아니므로 오류를 확인하고 중복 제출하지 마세요.
```

모델 태그가 없으면 설치부터 진행하지 않고 실제 사용 가능한 목록을 확인한다.
위 요청문은 실행을 지시하는 템플릿이며 구성 성공을 보장하는 실행 프로그램은 아니다.

### 8.4 여러 프로젝트를 함께 실행할 때

에이전트 등록 이름은 같은 서버에서 고유해야 한다. 예를 들어 두 프로젝트를 함께
실행한다면 `alpha-main / alpha-sub / alpha-local`과
`beta-main / beta-sub / beta-local`처럼 구분한다.
표시 이름도 맞추고, 명령의 대상 이름도 접두어가 포함된 실제 이름으로 바꾼다.
전체 이름은 32자 이내로 정한다. Pane 표시 이름만 바꿔서는 등록 이름 충돌이 해소되지 않는다.

Pane ID와 과거 세션 ID를 템플릿에 고정하지 않는다. 프로젝트 변경 시 모델 설치와
전역 프로필 설정을 매번 반복할 필요는 없지만, 현재 실행에 적용됐는지는 확인한다.

### 8.5 문서·스킬·스크립트 비교

| 방식 | 적합한 내용 | 현재 선택 |
| --- | --- | --- |
| 공통 지침 문서 | 역할·협업·확인 기준 | 이 문서를 참조 |
| 시작 요청문 | 경로·모델 등 실행별 입력과 구성 지시 | 위 템플릿 재사용 |
| 스킬 | 에이전트가 재사용할 설정 절차 패키지 | 별도 생성하지 않음 |
| 실행 스크립트 | pane 생성·실행·이름 등록 자동화 | 별도 생성하지 않음 |

현재는 **공통 문서와 시작 요청문**을 사용한다. 자동화가 필요해지면 별도 요청으로
검토하며, 기존 pane·이름 충돌·부분 실패 후 재실행을 다루는 검증이 필요하다.

문서 예제의 4개 pane 전체 구성은 진행 중인 작업을 바꾸지 않도록 새로 실행하지 않았다.
이 문서 외의 스킬·실행 스크립트·프로젝트 지침·전역 설정은 생성하거나 변경하지 않았다.
