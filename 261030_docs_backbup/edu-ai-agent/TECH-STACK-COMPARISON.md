# Agentic AI 교육 기술 스택과 CLI 에이전트 비교 분석

이 교육과정은 Python으로 RAG와 업무용 에이전트를 만들고, 실행 흐름·상태·평가·배포까지 직접 설계하는 과정입니다. Claude Code·Codex CLI 사용과 비교하면, 가장 큰 차이는 에이전트의 실행 구조를 어디까지 직접 만들고 통제하느냐에 있습니다.

CLI 에이전트도 자동화와 서비스 통합에 사용할 수 있으므로, 교육과정은 서비스 개발용이고 CLI는 개인 코딩용이라는 구분만으로는 충분하지 않습니다.

교육 범위는 [COURSE.md](COURSE.md)를 기준으로, 제품 기능은 공식 문서를 기준으로 설명합니다. 구체적인 구현 예시는 교육 내용을 기술적으로 풀어 설명한 것입니다. 제품 기능은 2026년 10월 27일 확인 기준입니다.

## 1. 교육과정의 기술 스택

| 계층 | 과정에 명시된 기술 | 실제로 배우는 구현 내용 |
| --- | --- | --- |
| 모델 연결 | OpenAI·Gemini API, Message Role | 모델 호출, 시스템·사용자 메시지 구성, 응답 처리 |
| 애플리케이션 조합 | LangChain, Prompt, LCEL·Runnable | 프롬프트·모델·후처리를 연결하고 순차·병렬·스트리밍 실행 구성 |
| 출력 계약 | Structured Output, JSON, Pydantic | 자연어 응답을 프로그램이 처리할 수 있는 구조로 변환·검증 |
| 지식 검색 | Loader, Splitter, Embedding, FAISS·Chroma, Retriever | 문서를 색인하고 질문에 필요한 근거를 검색하는 RAG 구축 |
| 도구 실행 | Tool Calling, @tool, BaseTool, ReAct | 모델이 도구를 선택하도록 하고 실제 함수 실행 결과를 다시 모델에 전달 |
| 실행 흐름 | LangGraph, StateGraph, Node·Edge | 상태, 분기, 반복, 중단, 재개를 코드로 정의 |
| 계획과 실행 | Plan-and-Execute, Replanning | 계획 생성과 작업 수행을 분리하고 결과에 따라 재계획 |
| 에이전트 하네스 | 컨텍스트, 메모리, Middleware, Deep Agent | 장기 작업에 필요한 실행 루프와 컨텍스트 관리 구성 |
| 시스템 연결 | MCP, A2A, Supervisor·SubAgent | 외부 도구·데이터 연결과 에이전트 간 협업 구성 |
| 검증과 운영 | assert, LangSmith, Evaluation, 상태 영속화 | 실행 추적, 품질 평가, 회귀 확인, 비용·지연 개선, 배포 |

LangChain 공식 문서에서는 LangChain을 모델·도구·에이전트 구성 요소, LangGraph를 상태를 가진 실행 흐름, Deep Agents를 그 위의 하네스, LangSmith를 추적·평가·배포 플랫폼으로 구분합니다. 이들은 각각 역할이 다른 구성 요소입니다. [LangGraph 공식 개요](https://docs.langchain.com/oss/python/langgraph/overview)

## 2. 날짜별 기술 역량

### 1일차 모델 호출을 애플리케이션으로 구성

핵심은 모델 API의 응답을 받아 출력하는 수준에서, 입력과 출력을 명확하게 관리하는 프로그램으로 발전시키는 것입니다.

- **Prompt·Message Role:** 시스템 지시, 사용자 요청, 이전 대화를 구분합니다.
- **LCEL·Runnable:** 검색·프롬프트·모델·출력 변환을 조합하고 순차 또는 병렬로 실행합니다.
- **Structured Output·Pydantic:** 응답을 답변, 근거 문서, 추가 확인 필요 여부 같은 필드로 받도록 설계합니다.
- **Memory:** 이전 메시지를 다음 호출에 어떻게 반영할지 관리합니다.

대화 이력을 저장하는 것과 모델 자체를 학습시키는 것은 다릅니다. 이 과정의 Memory는 주로 애플리케이션이 보관하고 다시 제공하는 정보에 해당합니다.

### 2일차 사내 지식 검색 시스템 구축

RAG는 크게 색인과 질의 처리로 나뉩니다.

```text
색인:
PDF·Word·CSV → 로딩 → 청크 분할 → 임베딩 → 벡터 저장

질의:
질문 → 검색 → 근거 문서 선택 → 프롬프트 구성 → 답변
```

| 기술 | 구현할 때 판단해야 할 것 |
| --- | --- |
| Document Loader | 본문·표·메타데이터를 얼마나 정확히 추출하는가 |
| Document Splitter | 문맥이 끊기지 않으면서 검색하기 좋은 크기로 나누는가 |
| Embedding | 질문과 문서의 의미를 검색 가능한 벡터로 표현하는가 |
| FAISS·Chroma | 벡터 색인을 어떻게 저장·조회·갱신하는가 |
| Similarity·MMR·Filtering | 유사성, 결과 다양성, 메타데이터 조건을 어떻게 조합하는가 |
| RAG Chain | 검색 결과와 답변을 연결하고 근거를 어떻게 제공하는가 |

FAISS와 Chroma는 선택 가능한 저장·검색 구성 요소이며, 둘을 반드시 동시에 사용하는 구조는 아닙니다.

4일차의 Advanced RAG는 검색 품질을 개선합니다. Multi-Query는 질문을 여러 관점으로 확장하고, Hybrid는 서로 다른 검색 방식을 결합하며, Rerank는 검색 후보의 순서를 다시 평가하는 접근입니다. Adaptive·Corrective·Self-RAG는 검색 필요성이나 결과 품질을 판단하고 후속 검색·생성을 조정하는 패턴으로 이해할 수 있습니다. 실제 알고리즘과 평가 방식은 강의 구현을 확인해야 합니다.

### 3일차 도구 실행과 상태 제어

Tool Calling에서는 모델이 도구 이름과 인자를 제안하고, 실제 실행은 애플리케이션이 담당합니다.

```text
사용자 요청 → 모델의 도구 호출 제안
           → 인자·권한 검증 → 함수 실행
           → 실행 결과 전달 → 다음 행동 또는 최종 응답
```

`@tool`·BaseTool은 함수의 입력 형식과 설명을 모델에 제공하는 수단입니다. ReAct는 행동과 관찰을 반복하는 에이전트 패턴이며, 모델 내부의 상세 추론을 출력받아야 구현되는 것은 아닙니다. LangChain의 `create_agent`는 이러한 모델·도구 반복 구조를 제공합니다. [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)

LangGraph에서는 흐름을 더 구체적으로 정의합니다.

- **State:** 현재 요청, 검색 결과, 작업 결과, 승인 상태 등
- **Node:** 검색, 검증, 실행, 응답 같은 작업 단위
- **Edge:** 다음 작업으로 이동하는 경로
- **Conditional Edge:** 상태에 따른 분기
- **Checkpointer:** 실행 상태 저장
- **Interrupt·HITL:** 실행을 멈추고 사람의 입력이나 승인을 기다리는 구조

체크포인트가 있다고 외부 업무가 자동으로 안전하게 재개되는 것은 아닙니다. 예를 들어 결재 등록 후 재시도할 수 있다면, 중복 등록을 방지하는 설계도 필요합니다. LangGraph의 영속화는 이런 재개 구조의 기반입니다. [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

### 4일차와 5일차 실행 환경과 운영 품질

Plan-and-Execute는 계획 수립과 작업 수행을 분리하고, Replanning은 실행 결과에 따라 계획을 조정합니다. 하네스는 이 과정을 둘러싼 컨텍스트 관리, 도구 실행, 제한 조건, 오류 복구, 승인, 상태 관리를 뜻합니다.

Deep Agents는 파일 시스템을 통한 컨텍스트 관리, 하위 에이전트 위임, 메모리 등의 기능을 제공하는 하네스입니다. 따라서 이 교육도 모든 실행 구조를 처음부터 작성하는 방식만 다루는 것은 아닙니다. [Deep Agents 공식 개요](https://docs.langchain.com/oss/python/deepagents/overview)

MCP와 A2A는 연결 대상이 다릅니다.

| 구분 | 주된 목적 | 예시 |
| --- | --- | --- |
| MCP | 에이전트에 도구와 데이터를 제공 | 문서 검색, DB 조회, 업무 API 실행 |
| A2A | 독립적인 에이전트 간 작업 협업 | 조사 에이전트가 별도 분석 에이전트에 작업 의뢰 |

하위 에이전트를 호출한다고 반드시 A2A를 사용하는 것은 아닙니다. 같은 프로그램 안에서 함수를 통해 위임할 수도 있습니다. [MCP 공식 소개](https://modelcontextprotocol.io/docs/getting-started/intro), [A2A 공식 소개](https://a2a-protocol.org/latest/topics/what-is-a2a/)

`assert`는 출력 형식이나 실행 조건을 확인하는 데 유용하지만, 답변의 사실성이나 업무 적합성 전체를 보장하지는 않습니다. 운영 단계에서는 검색 품질, 근거 정확성, 작업 성공률, 비용, 지연을 별도로 평가해야 합니다.

## 3. Claude Code 및 Codex CLI와의 비교

Claude Code와 Codex CLI는 파일·명령 실행 도구와 반복 실행 구조를 갖춘 에이전트입니다. Claude Code는 문맥 수집·행동·검증의 반복을, Codex CLI는 코드 조사·수정·명령 실행과 반복 업무 자동화를 공식적으로 지원합니다. [Claude Code 실행 구조](https://code.claude.com/docs/en/how-claude-code-works), [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)

| 비교 항목 | 교육과정 기반 직접 구성 | Claude Code·Codex CLI 활용 |
| --- | --- | --- |
| 출발점 | Python 코드와 프레임워크 구성 요소 | 이미 구성된 에이전트 실행 환경 |
| 기본 작업 환경 | 직접 연결한 데이터·도구·업무 상태 | 작업 디렉터리, 파일, 터미널 중심 |
| 실행 흐름 | 그래프와 코드로 분기·전이를 명시 | 제공되는 에이전트 루프와 설정을 활용 |
| 검색 | 청크·임베딩·검색·재정렬을 직접 구성 | 파일 검색이나 연결 도구를 활용하고 필요하면 RAG 추가 |
| 도구 | 함수·스키마·실행 정책을 직접 정의 | 내장 도구와 확장 기능을 활용 |
| 상태 | 업무별 상태와 저장 구조를 설계 | 제공되는 세션·스레드 기능을 활용하고 업무 상태는 별도 관리 |
| 모델 선택 | 제공자 연동 범위에서 구성 | 각 제품이 지원하는 모델·연결 방식에 따름 |
| 검증 | 업무별 평가 데이터와 기준을 구성 | 실행 결과·테스트·로그를 활용하고 업무 평가는 추가 구성 |
| 초기 구축 부담 | 필요한 구성 요소가 많음 | 기본 하네스를 빠르게 활용 가능 |
| 세부 통제 | 업무 단계와 데이터 구조를 명시하기 쉬움 | 제품의 확장·설정 범위에 영향을 받음 |
| 운영 책임 | 실행·저장·배포·관측을 직접 설계 | 하네스를 재사용해도 서비스 운영 책임은 남음 |

차이를 가능 여부보다 기본 제공 범위와 직접 구현할 범위로 보는 것이 정확합니다.

CLI 에이전트가 파일을 찾아 읽는 것과, 사내 문서를 임베딩하여 검색하는 RAG는 구현 방식이 다릅니다. CLI 에이전트에 RAG 검색 도구를 연결하면 함께 사용할 수 있습니다.

프롬프트에 승인 후 실행이라고 적는 것과 프로그램이 승인 상태를 검사하여 실행을 차단하는 것은 보장 수준이 다릅니다. 어느 접근이든 반드시 지켜야 하는 업무 규칙은 코드·권한·실행 정책으로 강제해야 합니다.

## 4. CLI 에이전트의 서비스 통합

CLI 직접 사용, 기존 하네스의 서비스 통합, 프레임워크 기반 실행 흐름 구성은 구분해서 비교해야 합니다.

| 방식 | 구성 | 주된 판단 |
| --- | --- | --- |
| CLI 직접 사용 | 사람이 터미널에서 작업 요청 | 개인·팀 작업의 효율 |
| CLI·SDK를 서비스에 통합 | 애플리케이션이 기존 하네스에 작업 전달 | 제공되는 실행 구조가 업무에 맞는가 |
| 프레임워크로 실행 흐름 구성 | LangChain·LangGraph 등으로 직접 조립 | 필요한 업무 상태와 제어를 구현할 수 있는가 |

Claude Code는 `claude -p`를 통한 비대화형 실행과 Python·TypeScript Agent SDK를 제공합니다. Codex도 `codex exec`, SDK, app-server를 통해 자동화나 애플리케이션 통합에 사용할 수 있습니다. 따라서 두 제품의 하네스를 재사용해 업무용 에이전트를 만드는 접근도 가능합니다. [Claude Code 프로그램 실행](https://code.claude.com/docs/en/headless), [Codex 비대화형 실행](https://learn.chatgpt.com/docs/non-interactive-mode), [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)

서비스를 구성하면 어느 방식이든 사용자 인증, 데이터 접근 권한, 요청 간 격리, 동시 실행, 작업 시간 제한, 업무 감사 기록 등을 설계해야 합니다. CLI 호출을 API로 감싸는 것만으로 이러한 운영 요건이 충족되지는 않습니다.

## 5. 동일 업무의 구현 방식 비교

사내 규정을 검색하고 구매 요청서를 작성한 뒤 승인받아 등록하는 업무를 예로 들 수 있습니다.

| 단계 | 교육과정 방식 | CLI 하네스 활용 방식 |
| --- | --- | --- |
| 규정 검색 | RAG 검색 파이프라인 구현 | 파일 검색 또는 RAG 도구 연결 |
| 요청서 작성 | 모델 호출과 구조화 출력 구성 | 에이전트에 작성 작업을 맡기고 결과 검증 |
| 필수 항목 확인 | Pydantic·업무 검증 코드 적용 | 하네스 외부 검증 코드 또는 도구로 적용 |
| 승인 대기 | 그래프 상태·Interrupt로 표현 | 승인 기능과 애플리케이션의 업무 승인 연계 |
| 시스템 등록 | 승인 상태를 검사하는 업무 도구 실행 | 동일한 업무 도구를 연결하여 실행 |
| 실패 후 재개 | 체크포인트와 재시도 경로 설계 | 세션 기능과 별도의 업무 상태 저장 연계 |

업무 검증과 실제 시스템 등록 도구는 양쪽에서 재사용할 수 있습니다. 달라지는 것은 그 사이를 조율하는 실행 구조입니다.

## 6. CLI 에이전트 사용자에게 추가되는 학습 가치

교육 구성상, 현재 CLI 에이전트를 활용하는 사람에게 추가 가치가 큰 부분은 다음과 같습니다.

- **RAG:** 문서를 읽히는 수준에서 검색 품질을 직접 설계·평가하는 수준으로 확장합니다.
- **LangGraph:** 자연어 지시를 상태·분기·중단·재개가 있는 실행 구조로 구체화합니다.
- **하네스:** 도구 사용과 컨텍스트 관리가 결과에 미치는 영향을 이해합니다.
- **평가·운영:** 결과의 업무 성공률과 회귀를 측정합니다.
- **MCP·A2A:** 외부 도구 연결과 에이전트 간 협업을 구분하여 설계합니다.

실무에서는 Claude Code·Codex로 구현과 검증을 돕고, 업무에 필요한 RAG·도구·상태를 교육과정의 기술로 구성하는 조합이 가능합니다. 에이전트 루프 자체가 업무에 잘 맞으면 CLI 제품의 SDK·하네스를 재사용하고, 업무 단계의 명시적 제어가 중요하면 LangGraph 같은 실행 구조를 검토할 수 있습니다.

`COURSE.md`에는 배포와 운영이 주제로 들어 있지만, 인증·동시성·컨테이너·운영 인프라의 구체적인 스택은 명시되어 있지 않습니다. 이 과정은 업무용 에이전트의 구성 원리와 구현 기반을 배우는 과정으로 볼 수 있으며, 실제 운영 수준까지 다루는 깊이는 실습 코드와 평가 기준을 확인해야 판단할 수 있습니다.

## 7. 교육용 Jupyter 노트북 구성안

각 일차의 8교시에 맞춰 노트북을 나눈 구성안입니다. 총 5개 일차 폴더, 40개 교육용 노트북이며, 아래 목록은 생성 예정 경로를 나타냅니다.

```text
edu-ai-agent/
└── notebooks/
    ├── day-01-langchain/
    │   ├── 01-ai-evolution-and-course-overview.ipynb
    │   ├── 02-llm-api-and-message-roles.ipynb
    │   ├── 03-langchain-model-prompt-chain.ipynb
    │   ├── 04-prompt-template-and-few-shot.ipynb
    │   ├── 05-lcel-and-runnable.ipynb
    │   ├── 06-structured-output-and-pydantic.ipynb
    │   ├── 07-conversation-memory.ipynb
    │   └── 08-langchain-chatbot-project.ipynb
    ├── day-02-rag/
    │   ├── 01-rag-architecture.ipynb
    │   ├── 02-document-loaders.ipynb
    │   ├── 03-document-splitting.ipynb
    │   ├── 04-embeddings-and-similarity.ipynb
    │   ├── 05-vector-stores-faiss-chroma.ipynb
    │   ├── 06-retrievers-mmr-and-filtering.ipynb
    │   ├── 07-document-qa-rag-chain.ipynb
    │   └── 08-enterprise-knowledge-rag-project.ipynb
    ├── day-03-tools-and-langgraph/
    │   ├── 01-tool-calling-and-schemas.ipynb
    │   ├── 02-custom-tools.ipynb
    │   ├── 03-react-agent-loop.ipynb
    │   ├── 04-create-agent-and-multiple-tools.ipynb
    │   ├── 05-mcp-server-and-client.ipynb
    │   ├── 06-langgraph-state-nodes-and-edges.ipynb
    │   ├── 07-conditional-routing-and-loops.ipynb
    │   └── 08-checkpoints-interrupts-and-hitl.ipynb
    ├── day-04-planning-and-harness/
    │   ├── 01-plan-and-execute.ipynb
    │   ├── 02-replanning-and-failure-handling.ipynb
    │   ├── 03-assertions-and-langsmith-tracing.ipynb
    │   ├── 04-cost-latency-and-evaluation.ipynb
    │   ├── 05-agent-harness-project.ipynb
    │   ├── 06-advanced-rag-query-hybrid-rerank.ipynb
    │   ├── 07-adaptive-corrective-and-self-rag.ipynb
    │   └── 08-deep-agents-middleware-memory-todos.ipynb
    └── day-05-multi-agent-and-deployment/
        ├── 01-supervisor-subagents-and-handoffs.ipynb
        ├── 02-guardrails-context-and-recovery.ipynb
        ├── 03-a2a-and-mcp-comparison.ipynb
        ├── 04-agent-evaluation-and-regression.ipynb
        ├── 05-persistence-deployment-and-improvement.ipynb
        ├── 06-capstone-design-and-implementation.ipynb
        ├── 07-capstone-validation-and-improvement.ipynb
        └── 08-capstone-review-and-solutions.ipynb
```
