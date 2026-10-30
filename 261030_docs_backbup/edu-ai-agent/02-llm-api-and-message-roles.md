# LLM API와 메시지 역할 실습

## 학습 목표와 범위

[교육과정](../COURSE.md)의 1일차 2교시인 LLM API 활용과 Message Role을 실습합니다. 각 Python 코드 블록을 Jupyter Notebook의 독립된 Code 셀에 복사하고 위에서 아래로 실행합니다. 코드 앞의 목적과 내용은 Markdown 셀로, 코드 뒤의 결과 설명은 관찰 기록의 기준으로 사용할 수 있습니다.

이 실습에서는 로컬 Ollama와 OpenAI API를 선택하여 동일한 기본 호출 구조를 사용합니다. 원래 교육과정에 포함된 Gemini의 개별 SDK 연동은 이번 문서의 범위에 포함하지 않습니다. LangChain, 구조화 출력, 장기 메모리는 후속 교시에서 다룹니다.

실습을 마치면 다음을 설명할 수 있어야 합니다.

- API 클라이언트, 서버 주소, 모델 이름의 관계
- `system`, `user`, `assistant` 메시지의 역할
- 단일 요청과 대화 이력을 포함한 요청의 차이
- 일반 응답과 스트리밍 응답의 처리 방식
- 인증 오류, 연결 오류, 모델 오류, 호출 제한의 구분

## 실행 환경과 준비사항

| 항목 | Ollama | OpenAI API |
| --- | --- | --- |
| 모델 실행 위치 | 로컬 PC | OpenAI 서버 |
| 준비 | Ollama 실행, 대화용 모델 다운로드 | API 키와 해당 모델 사용 권한·크레딧 |
| 호출 주소 | `http://localhost:11434/v1/` | `https://api.openai.com/v1/` |
| 인증 | 기본 로컬 서버는 실제 API 키 불필요 | 실제 API 키 필요 |
| 실행 비용 | 외부 모델 API 이용료 없이 로컬 자원 사용 | 모델·사용량에 따른 API 비용 |
| 권장 노트북 환경 | Ollama와 같은 PC의 Jupyter 커널 | 로컬 Jupyter 또는 Colab |

일반적인 Colab 원격 런타임의 `localhost`는 Colab 서버입니다. PC에 설치한 Ollama에 연결하려면 같은 PC의 Jupyter 커널 또는 별도로 구성한 로컬 런타임을 사용합니다.

Ollama에서는 텍스트 대화와 시스템 지시를 지원하는 모델을 준비합니다. 임베딩 전용 모델은 이 실습의 채팅 모델로 선택하지 않습니다. OpenAI에서는 Chat Completions와 아래 메시지 역할을 지원하는 모델을 선택합니다. 제공자와 모델에 따라 지원하는 역할·매개변수·컨텍스트 길이가 다르며, 일부 OpenAI 모델에서는 `developer` 역할을 사용하도록 안내할 수 있습니다.

여기서는 두 환경을 비교하기 위해 Chat Completions를 사용합니다. OpenAI의 Responses API와 Ollama의 모든 기능이 동일하다는 의미는 아닙니다. Ollama는 OpenAI API의 일부를 호환합니다. [Ollama 호환 API 안내](https://docs.ollama.com/api/openai-compatibility)

아래 결과 설명은 예상 동작과 관찰 기준입니다. 실제 답변은 모델과 실행 시점에 따라 달라집니다. 문서 작성 과정에서는 유료 API 호출이나 로컬 모델 추론을 실행하지 않았습니다. OpenAI 모드에서는 모델 호출 셀을 실행할 때마다 사용량이 발생하며, 반복 실행도 추가 호출입니다.

## 1. 실습 환경 설정

### 1.1 실습 패키지 설치

- 현재 노트북 커널이 사용하는 Python에 OpenAI SDK와 HTTP 요청 라이브러리를 설치합니다.
- 같은 SDK로 OpenAI와 Ollama의 호환 API에 접속합니다.

```python
import subprocess
import sys

subprocess.check_call([
    sys.executable,
    "-m",
    "pip",
    "install",
    "openai",
    "requests",
])
```

**결과:**

- 설치 로그와 종료 코드 `0`이 나타나면 설치가 완료된 것입니다.
- 이미 설치되어 있으면 기존 설치 정보가 출력될 수 있습니다.
- 환경에서 커널 재시작을 안내하면 재시작한 뒤 1.2 절부터 진행합니다.
- 이후 셀에서 import 오류가 나면 설치 대상 Python과 커널의 경로를 확인합니다.

### 1.2 라이브러리와 버전 확인

- 필요한 라이브러리를 불러오고 환경 정보를 확인합니다.
- 실습 중 문제가 발생했을 때 Python·패키지 버전을 함께 기록합니다.

```python
import json
import os
import time
from getpass import getpass
from importlib.metadata import version

import requests
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)

print("Python:", sys.version.split()[0])
print("openai:", version("openai"))
print("requests:", version("requests"))
```

**결과:**

- Python과 두 패키지의 버전이 출력됩니다.
- `sys`는 1.1 절에서 불러오므로 셀을 순서대로 실행해야 합니다.
- 버전 정보는 실행 환경 정보이며 모델의 버전이나 성능을 나타내지는 않습니다.

### 1.3 제공자와 모델 선택

- 기본값인 Ollama 또는 OpenAI를 선택합니다.
- Ollama는 설치된 모델 목록을 조회한 뒤 사용할 대화용 모델 이름을 입력합니다.
- OpenAI는 사용할 모델 이름과 API 키를 준비합니다.
- 키는 코드나 출력에 표시하지 않습니다.

```python
PROVIDER = "ollama"  # "ollama" 또는 "openai"
OLLAMA_HOST = "http://localhost:11434"
OPENAI_BASE_URL = "https://api.openai.com/v1/"

if PROVIDER == "ollama":
    try:
        model_response = requests.get(
            f"{OLLAMA_HOST}/api/tags",
            timeout=10,
        )
        model_response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Ollama 연결에 실패했습니다. 서버 실행 상태와 커널 위치를 확인하세요."
        ) from exc

    installed_models = [
        item["name"]
        for item in model_response.json().get("models", [])
    ]
    if not installed_models:
        raise RuntimeError("Ollama에 대화용 모델을 먼저 다운로드하세요.")

    print("설치된 모델:", installed_models)
    MODEL = input("사용할 대화용 모델 이름을 정확히 입력하세요: ").strip()
    if MODEL not in installed_models:
        raise ValueError("설치된 모델 목록에 있는 이름을 입력하세요.")

    api_key = "ollama"  # SDK 입력용 값. 로컬 Ollama는 이 값을 무시합니다.
    base_url = f"{OLLAMA_HOST}/v1/"

elif PROVIDER == "openai":
    MODEL = input("사용 가능한 OpenAI 채팅 모델 이름을 입력하세요: ").strip()
    if not MODEL:
        raise ValueError("모델 이름이 필요합니다.")

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        api_key = getpass("OpenAI API 키를 입력하세요: ").strip()
    if not api_key:
        raise ValueError("OpenAI API 키가 필요합니다.")
    base_url = OPENAI_BASE_URL

else:
    raise ValueError("PROVIDER는 'ollama' 또는 'openai'여야 합니다.")

print("선택한 제공자:", PROVIDER)
print("선택한 모델:", MODEL)
print("호출 주소:", base_url)
```

**결과:**

- Ollama에서는 실제 설치된 모델 목록과 선택 결과가 출력됩니다.
- 목록에 있다는 사실만으로 채팅 기능 지원이 보장되는 것은 아니므로 대화용 모델을 선택합니다.
- OpenAI에서는 모델의 실제 접근 권한이 첫 호출 때 확인됩니다.
- `getpass` 입력은 보통 화면에 표시되지 않으며, 입력한 키는 현재 커널 메모리에 존재합니다.
- 커널 변수나 인증 정보를 출력하지 않습니다.

Ollama 모델 목록은 공식 `/api/tags` 엔드포인트로 조회합니다. [Ollama 모델 목록 API](https://docs.ollama.com/api/tags)

### 1.4 API 클라이언트 생성

- 선택한 서버에 요청할 클라이언트를 생성합니다.
- 오류를 관찰하기 쉽도록 SDK 자동 재시도를 끄고, 로컬 모델의 첫 로딩을 고려해 요청 제한 시간을 설정합니다.

```python
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=300.0,
    max_retries=0,
)

print("클라이언트 생성 완료:", PROVIDER, MODEL)
```

**결과:**

- 클라이언트 생성 완료 메시지가 출력됩니다.
- 이 단계는 호출 설정을 준비하는 단계이므로 서버 연결·인증·모델 실행이 성공했다는 뜻은 아닙니다.
- 실제 요청은 다음 셀부터 발생합니다.
- `300.0`은 클라이언트의 타임아웃 설정이며, 실제 처리 시간이나 엄격한 전체 실행 시간 보장은 아닙니다.

## 2. API 기본 호출과 응답

### 2.1 첫 번째 질문 전송

- `user` 메시지 하나를 전달하고 응답 텍스트를 추출합니다.
- 요청 직전부터 응답 수신까지 걸린 시간도 측정합니다.

```python
messages = [
    {
        "role": "user",
        "content": "Python 리스트와 튜플의 차이를 간단히 설명해 주세요.",
    }
]

started_at = time.perf_counter()
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
)
elapsed_seconds = time.perf_counter() - started_at

answer = response.choices[0].message.content or ""
print(answer)
print(f"\n요청부터 응답 수신까지: {elapsed_seconds:.2f}초")
```

**결과:**

- 리스트와 튜플의 변경 가능 여부나 사용 예시 등에 대한 설명이 출력됩니다.
- 답변 내용이 정확한지 사람이 확인합니다.
- Ollama의 첫 요청은 모델 로딩 때문에 후속 요청보다 오래 걸릴 수 있습니다.
- 이 시간에는 네트워크·대기·로딩·생성 등이 포함되므로 순수한 모델 생성 속도로 해석하지 않습니다.

### 2.2 응답 구조와 사용량 확인

- SDK 응답에서 모델, 역할, 종료 사유, 토큰 사용량을 확인합니다.
- 전체 응답 객체 대신 학습에 필요한 필드만 출력합니다.

```python
choice = response.choices[0]

print("응답 모델:", response.model)
print("메시지 역할:", choice.message.role)
print("종료 사유:", choice.finish_reason)
print("텍스트 응답 존재:", bool(choice.message.content))

if response.usage is not None:
    print(json.dumps(
        response.usage.model_dump(),
        ensure_ascii=False,
        indent=2,
    ))
else:
    print("이 응답에는 사용량 정보가 없습니다.")
```

**결과:**

- 역할은 일반적으로 `assistant`입니다.
- 종료 사유가 `stop`이면 보통 정상적인 종료를 뜻하고, `length`이면 출력 또는 컨텍스트 한도 등을 확인합니다.
- 토큰 수는 글자 수와 다르며, 같은 문장도 모델의 토크나이저에 따라 다르게 계산됩니다.
- 제공자별 사용량 필드는 다를 수 있고, 토큰 수만으로 정확한 청구 금액을 확정할 수는 없습니다.
- 응답이 비어 있으면 종료 사유와 모델의 추론·출력 설정을 먼저 확인합니다.

## 3. 메시지 역할과 지시 비교

### 3.1 메시지 역할을 적용한 요청

- `system`에 응답 기준을 넣고 `user`에는 질문을 넣습니다.
- 메시지 역할은 단순한 텍스트 제목이 아니라 API 요청의 구조라는 점을 확인합니다.

| 역할 | 이 실습에서의 용도 |
| --- | --- |
| system | 기본 행동, 대상 독자, 답변 형식 지정 |
| user | 질문과 추가 요청 전달 |
| assistant | 앞선 모델 답변을 대화 이력으로 전달 |

```python
role_messages = [
    {
        "role": "system",
        "content": (
            "당신은 Python 교육 도우미입니다. "
            "입문자에게 설명하며, 답변은 한국어 세 문장으로 작성하세요."
        ),
    },
    {
        "role": "user",
        "content": "Python 리스트와 튜플의 차이를 설명해 주세요.",
    },
]

role_response = client.chat.completions.create(
    model=MODEL,
    messages=role_messages,
)
print(role_response.choices[0].message.content or "")
```

**결과:**

- 입문자에게 맞춘 한국어 세 문장 답변이 기대됩니다.
- 문장 수나 난이도를 지키지 않았다면 모델의 지시 준수 결과로 기록합니다.
- 프롬프트의 형식 지시는 코드 검증처럼 강제되는 조건이 아닙니다.
- `system` 사용 오류가 발생하면 선택 모델의 지원 역할을 확인합니다.
- 다른 역할로 변경해 비교할 때는 변경 내용을 기록합니다.

### 3.2 같은 질문에 서로 다른 지시 적용

- 질문과 모델을 고정하고 시스템 지시만 바꿉니다.
- 입력 변수 하나를 바꾸어 답변의 난이도와 형식 변화를 관찰합니다.
- 이 셀은 모델 요청을 두 번 실행합니다.

```python
question = "Python 리스트와 튜플은 어떻게 다른가요?"
instructions = {
    "입문자 설명": (
        "Python 입문자에게 설명하세요. 일상적인 비유를 하나 포함하고 "
        "한국어 세 문장으로 답하세요."
    ),
    "개발자 설명": (
        "Python 개발자에게 설명하세요. 변경 가능성, 해시 가능성의 조건, "
        "선택 기준을 포함하여 한국어 세 문장으로 답하세요."
    ),
}

comparison_results = {}
for label, instruction in instructions.items():
    current_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": question},
        ],
    )
    comparison_results[label] = current_response.choices[0].message.content or ""
    print(f"\n[{label}]")
    print(comparison_results[label])
```

**결과:**

- 입문자 답변에는 비유가, 개발자 답변에는 기술적인 조건과 선택 기준이 포함되는지 확인합니다.
- 튜플은 원소가 모두 해시 가능할 때 해시 가능하므로, 모든 튜플이 무조건 해시 가능하다고 설명하면 오류입니다.
- 생성 결과에는 변동성이 있으므로 두 답변의 차이가 모두 시스템 지시 때문이라고 단정하지 않습니다.
- 필요하면 같은 조건으로 반복해 경향을 확인합니다.

## 4. 대화 이력 관리

### 4.1 대화 이력 없이 후속 질문

- 이전 셀의 주제를 전달하지 않고 후속 질문만 요청합니다.
- 커널에 응답 변수가 남아 있어도 요청 메시지에 넣지 않으면 모델이 자동으로 읽지 못한다는 점을 확인합니다.

```python
followup_question = "앞서 비교한 두 자료형의 사용 예시를 각각 보여주세요."

without_history = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": "Python 교육 도우미입니다. 비교 대상이 불명확하면 질문하세요.",
        },
        {"role": "user", "content": followup_question},
    ],
)
print(without_history.choices[0].message.content or "")
```

**결과:**

- 비교 대상이 무엇인지 되묻는 답변이 기대됩니다.
- 모델이 리스트와 튜플 등을 추측할 수도 있지만, 그것이 이전 요청을 기억했다는 증거는 아닙니다.
- 이 실습의 독립적인 Chat Completions 요청에는 이전 메시지를 명시적으로 전달하지 않았습니다.

### 4.2 대화 이력을 포함한 후속 질문

- 3.1 절의 사용자 질문과 실제 모델 답변을 이력으로 전달하고 같은 후속 질문을 요청합니다.
- `assistant`는 이전 모델 답변을 표현하는 역할입니다.

```python
previous_answer = role_response.choices[0].message.content
if not previous_answer:
    raise RuntimeError("3.1 절의 응답을 먼저 확인하세요. 텍스트 답변이 필요합니다.")

conversation = [
    {
        "role": "system",
        "content": "Python 교육 도우미입니다. 비교 대상이 불명확하면 질문하세요.",
    },
    dict(role_messages[1]),
    {"role": "assistant", "content": previous_answer},
    {"role": "user", "content": followup_question},
]

with_history = client.chat.completions.create(
    model=MODEL,
    messages=conversation,
)
followup_answer = with_history.choices[0].message.content or ""
print(followup_answer)
print("\n이번 전달한 메시지 수:", len(conversation))
```

**결과:**

- 리스트와 튜플 각각의 사용 예시를 제공하는지 확인합니다.
- 4.1 절와 다른 점은 이전 질문·답변을 입력에 포함했다는 것입니다.
- 메시지는 네 개이며, 현재 응답을 저장하려면 별도로 이력에 추가해야 합니다.
- 대화가 길어지면 입력 토큰과 처리 부담도 증가하므로 무제한 누적하지 않습니다.
- 장기 메모리와 이력 축약은 후속 교시에서 다룹니다.

## 5. 스트리밍 응답

### 5.1 스트리밍 응답 받기

- 전체 답변이 완성될 때까지 기다리는 대신 텍스트 조각을 받을 때마다 출력합니다.
- 사용자에게 처음 텍스트가 보이는 시간과 전체 완료 시간을 구분합니다.

```python
stream_started_at = time.perf_counter()
first_text_seconds = None
text_parts = []

stream = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Python 학습을 시작하는 방법을 세 단계로 설명하세요."}
    ],
    stream=True,
)

try:
    for chunk in stream:
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content
        if text:
            if first_text_seconds is None:
                first_text_seconds = time.perf_counter() - stream_started_at
            text_parts.append(text)
            print(text, end="", flush=True)
finally:
    stream.close()

streamed_answer = "".join(text_parts)
print()
if first_text_seconds is not None:
    print(f"첫 텍스트 수신: {first_text_seconds:.2f}초")
else:
    print("텍스트 조각을 수신하지 못했습니다.")
print(f"전체 완료: {time.perf_counter() - stream_started_at:.2f}초")
```

**결과:**

- 답변이 여러 조각으로 이어서 출력되고, 완성된 텍스트는 `streamed_answer`에 저장됩니다.
- 조각 하나가 한 글자나 한 토큰에 반드시 대응하지는 않습니다.
- 측정한 첫 텍스트 수신 시간에는 연결·대기·모델 처리 시간이 포함됩니다.
- 추론 모델이 내부 처리 후 텍스트를 내보내는 경우 처음 보이는 답변까지 오래 걸릴 수 있습니다.
- 스트리밍은 표시 방식을 바꾸는 것이며 전체 계산 시간이나 비용을 자동으로 줄이지 않습니다.

## 6. 입력 검증과 오류 처리

### 6.1 오류를 분류하는 호출 함수

- API 호출 오류를 종류별로 처리하는 함수를 만듭니다.
- 이 셀은 함수를 정의할 뿐 모델을 호출하지 않습니다.
- 인증 정보나 전체 요청을 출력하지 않고, 학습자가 확인할 항목을 반환합니다.

```python
def ask_safely(user_text):
    if not isinstance(user_text, str) or not user_text.strip():
        return {"ok": False, "error": "질문을 입력하세요."}

    try:
        result = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": user_text}],
        )
        text = result.choices[0].message.content
        if not text:
            return {"ok": False, "error": "텍스트 응답이 없습니다. 종료 사유를 확인하세요."}
        return {"ok": True, "answer": text}
    except AuthenticationError:
        return {"ok": False, "error": "인증 정보와 API 프로젝트를 확인하세요."}
    except RateLimitError:
        return {"ok": False, "error": "호출 제한 또는 크레딧·할당량을 확인하세요."}
    except APITimeoutError:
        return {"ok": False, "error": "요청 시간이 초과되었습니다. 서버·모델 상태를 확인하세요."}
    except APIConnectionError:
        return {"ok": False, "error": "서버 주소, 네트워크, Ollama 실행 상태를 확인하세요."}
    except NotFoundError:
        return {"ok": False, "error": "모델 이름, 접근 권한, API 경로를 확인하세요."}
    except BadRequestError:
        return {"ok": False, "error": "메시지 역할, 모델 기능, 요청 형식을 확인하세요."}
    except APIStatusError as exc:
        return {"ok": False, "error": f"API 상태 오류: HTTP {exc.status_code}"}

print("오류 분류 함수 정의 완료")
```

**결과:**

- 함수 정의 완료 메시지만 출력됩니다.
- 실패 응답의 HTTP 상태와 의미는 제공자별로 다를 수 있습니다.
- 예를 들어 존재하지 않는 모델과 접근 권한 문제는 동일한 종류의 오류로 전달될 수 있으므로 상태 코드만으로 원인을 확정하지 않습니다.
- 재시도는 원인을 확인한 뒤 수행합니다.

### 6.2 입력 검증과 정상 호출 확인

- 비어 있는 질문은 서버에 보내기 전에 거부하고, 정상 질문은 6.1 절의 함수로 처리합니다.
- 빈 질문 검사에는 API 호출이 없고, 두 번째 검사에서 한 번 호출합니다.

```python
print("빈 질문 검사:", ask_safely("   "))

safe_result = ask_safely("Python에서 변수란 무엇인가요? 한 문장으로 설명하세요.")
if safe_result["ok"]:
    print("정상 응답:", safe_result["answer"])
else:
    print("확인할 사항:", safe_result["error"])
```

**결과:**

- 빈 질문은 `ok=False`와 입력 안내를 반환합니다.
- 정상 질문은 답변 또는 오류별 안내를 반환합니다.
- 오류를 재현하려고 실제 API 키를 화면에 출력하거나 서버를 변경할 필요는 없습니다.
- 이 함수는 대표적인 API 오류를 다루는 교육용 예시이며 모든 종류의 애플리케이션 오류를 처리하지는 않습니다.

## 7. 과정 안내 도우미 종합 실습

### 7.1 마무리 과제 과정 안내 도우미

- 역할·참고 정보·질문·대화 이력을 결합합니다.
- 실제 과정에 명시된 정보만 안내하고, 제공되지 않은 내용은 확인이 필요하다고 답하도록 지시합니다.
- 입력을 통해 여러 차례 질문할 수 있으며 질문 한 번마다 API 호출이 발생합니다.

```python
course_context = """
과정: 생성형 AI RAG·Agent 구현 과정
1일차: LLM API, 메시지 역할, LangChain, 프롬프트, LCEL,
       구조화 출력, 대화 이력, 챗봇 실습
2일차: 문서 로딩, 분할, 임베딩, 벡터 저장소, 검색, RAG
3일차: Tool Calling, 사용자 정의 도구, ReAct, MCP, LangGraph
4일차: 계획·재계획, 검증, 최적화, 하네스, Advanced RAG, Deep Agent
5일차: 멀티에이전트, 하네스 심화, A2A, 검증, 배포, 종합 실습
""".strip()

course_history = [{
    "role": "system",
    "content": (
        "당신은 교육 과정 안내 도우미입니다. 아래 참고 정보에 근거해 "
        "한국어로 간단히 답하세요. 정보에 없는 내용은 확인이 필요하다고 "
        "답하세요.\n\n" + course_context
    ),
}]

def ask_course(question):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("질문을 입력하세요.")

    user_message = {"role": "user", "content": question.strip()}
    candidate_history = course_history + [user_message]
    result = client.chat.completions.create(
        model=MODEL,
        messages=candidate_history,
    )
    answer = result.choices[0].message.content
    if not answer:
        raise RuntimeError("텍스트 응답이 없습니다. 요청 결과를 확인하세요.")

    # 성공한 질문과 답변만 보관합니다.
    course_history.extend([
        user_message,
        {"role": "assistant", "content": answer},
    ])
    return answer

while True:
    question = input("과정 질문을 입력하세요. 종료하려면 엔터: ").strip()
    if not question:
        break
    try:
        print(ask_course(question))
    except (APIConnectionError, APIStatusError, RuntimeError) as exc:
        print("요청 실패:", type(exc).__name__)
        print("서버·모델·인증·사용량을 확인한 뒤 다시 질문하세요.")
    print("현재 저장된 메시지 수:", len(course_history))
```

**결과:**

- 먼저 “2일차에는 무엇을 배우나요?”를 입력한 다음 “그 내용을 배우려면 1일차에 무엇을 익혀야 하나요?”라고 질문해 문맥이 유지되는지 확인합니다.
- “교육비는 얼마인가요?”처럼 참고 정보에 없는 질문에는 확인이 필요하다고 답하는지 확인합니다.
- 지시가 있어도 모델이 잘못된 내용을 생성할 수 있으므로 실제 답변을 검토합니다.
- 이 예제는 전체 참고 정보를 프롬프트에 넣는 방식이며, 문서를 검색하는 RAG는 아닙니다.
- 셀을 다시 실행하면 과제의 대화 이력이 초기화됩니다.

### 7.2 대화 초기화와 클라이언트 정리

- 커널에서 관리하는 대화 이력을 초기화하고 HTTP 클라이언트를 닫습니다.
- 실습 종료 후에는 커널도 종료합니다.

```python
course_history[:] = course_history[:1]
client.close()
api_key = None

print("대화 초기화 완료. 남은 메시지 수:", len(course_history))
print("API 클라이언트를 닫았습니다. 다시 호출하려면 설정 셀부터 실행하세요.")
```

**결과:**

- 시스템 메시지 한 개만 남고 클라이언트가 닫힙니다.
- 다른 변수에 저장한 응답·이력까지 모두 지워지는 것은 아니며, 클라이언트 내부나 환경 변수에 남은 인증 정보의 완전 삭제를 보장하지도 않습니다.
- 전체 실행 상태는 커널 종료로 정리합니다.
- 로컬 대화 초기화는 외부 서비스의 보관 데이터 삭제 요청과도 다릅니다.

## 8. 학습 확인과 제공자 비교

| 확인 항목 | 완료 기준 |
| --- | --- |
| 기본 호출 | 선택한 모델에 질문을 보내고 텍스트를 수신 |
| 역할 이해 | system·user·assistant가 각각 어디에 쓰이는지 설명 |
| 지시 비교 | 같은 질문에 지시만 바꾼 답변을 비교하고 사실 오류 확인 |
| 대화 이력 | 이력을 전달한 요청과 전달하지 않은 요청의 차이 설명 |
| 스트리밍 | 텍스트 조각을 출력하고 완성된 문자열로 저장 |
| 오류 처리 | 인증·연결·모델·호출 제한별 확인 항목 설명 |
| 도우미 과제 | 후속 질문 처리와 미제공 정보에 대한 응답 확인 |

두 제공자를 비교하려면 첫 실행의 모델 이름·버전·실행 환경·답변·처리 시간을 기록한 뒤 커널을 재시작하고 제공자를 바꾸어 동일한 질문으로 진행합니다. OpenAI 모델과 로컬 모델은 서로 다른 모델이므로 결과 차이를 서버 위치만의 영향으로 해석하지 않습니다. 모델 크기, 하드웨어, 컨텍스트, 로딩 여부도 함께 기록합니다. 이 실습은 비용이나 성능을 정밀 측정하는 벤치마크가 아닙니다.

## 9. 참고 문서

- [OpenAI Chat Completions Python API](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create): 메시지와 응답 객체, 호출 매개변수의 공식 정의
- [OpenAI API 시작하기](https://developers.openai.com/api/docs/quickstart): API 키와 SDK의 기본 사용
- [Ollama OpenAI 호환 API](https://docs.ollama.com/api/openai-compatibility): 로컬 서버 연결과 기능 호환 범위
- [Ollama 모델 목록 API](https://docs.ollama.com/api/tags): 설치된 모델 조회
