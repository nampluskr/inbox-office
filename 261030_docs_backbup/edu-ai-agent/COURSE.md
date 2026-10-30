# Agentic AI 교육 과정 소개

## 과정 개요

본 과정은 LLM 기반 애플리케이션에서 출발하여, 스스로 추론하고 계획하며 도구를 활용하는 Agentic AI 시스템을 설계·구현·운영하는 심화 과정입니다. LangChain으로 LLM 애플리케이션과 RAG를 구성하는 기초부터, Tool Calling·ReAct, LangGraph 기반 오케스트레이션과 검증, 추론·계획(Plan-and-Execute) 및 Agent Harness 설계, MCP·A2A를 통한 외부 연동과 멀티에이전트 구조, 그리고 Agent의 배포와 개선까지 단계적으로 다룹니다. 이론과 실습을 병행하여 실제 업무에 적용 가능한 Agent 시스템 구축 역량을 확보하는 것을 목표로 합니다.

## 핵심 학습 축

- AI 기술 진화와 Agentic AI
- 추론·계획과 하네스 엔지니어링
- 오케스트레이션 설계·검증·운영
- 멀티에이전트 · MCP/A2A · 배포·개선

## 교육 목표

교육 수료 후 다음 역량을 확보할 수 있습니다.

- LangChain 주요 컴포넌트로 LLM 애플리케이션을 구성할 수 있습니다.
- 기업 내부 문서를 활용하는 RAG 시스템을 설계·구현할 수 있습니다.
- Tool Calling과 ReAct 추론으로 동작하는 Agent를 개발할 수 있습니다.
- LangGraph 오케스트레이션을 설계하고 assert·LangSmith로 검증·최적화할 수 있습니다.
- Plan-and-Execute·Replanning과 Agent Harness를 직접 구현할 수 있습니다.
- MCP·A2A로 외부 시스템 및 Agent 간 연동을 구성할 수 있습니다.
- 멀티에이전트·Deep Agent로 복합 작업 시스템을 구축할 수 있습니다.
- Agent를 프로덕션에 배포하고 지속적으로 개선하는 운영 역량을 갖출 수 있습니다.

## 날짜별 교육 내용

### 1일차

| 교시 | 주제 | 세부 내용 |
| --- | --- | --- |
| 1교시 | 과정 소개 · AI 기술 진화 | LLM·RAG·Agent·Agentic AI 관계 |
| 2교시 | LLM API 활용 | OpenAI·Gemini, Message Role |
| 3교시 | LangChain 기본 구조 | Model·Prompt·Chain |
| 4교시 | Prompt 설계 | Template·Few-shot |
| 5교시 | LCEL·Runnable | Sequence·Parallel·Stream |
| 6교시 | Structured Output | Parser, JSON·Pydantic |
| 7교시 | Memory 관리 | Message History·대화 이력 |
| 8교시 | LangChain 종합 실습 | 대화형 LLM 앱 구현 |

### 2일차

| 교시 | 주제 | 세부 내용 |
| --- | --- | --- |
| 1교시 | RAG 아키텍처 | Indexing·Retrieval·Generation |
| 2교시 | Document Loader | PDF·Word·CSV 로딩 |
| 3교시 | Document Splitter | Chunk·Overlap 설계 |
| 4교시 | Embedding | 임베딩·문장 유사도 |
| 5교시 | Vector Store | FAISS·Chroma |
| 6교시 | Retriever | Similarity·MMR·Filtering |
| 7교시 | RAG Chain | 문서 기반 QA 구성 |
| 8교시 | RAG 종합 실습 | 기업 지식 질의응답 |

### 3일차

| 교시 | 주제 | 세부 내용 |
| --- | --- | --- |
| 1교시 | Tool Calling | Function Calling·Schema |
| 2교시 | 사용자 정의 Tool | @tool·BaseTool |
| 3교시 | ReAct 추론 | Thought–Action–Observation |
| 4교시 | Agent 구현 | create_agent·복수 Tool |
| 5교시 | MCP 기반 연동 | 개요·Server·Transport·Adapter |
| 6교시 | LangGraph 기본 | StateGraph·Node·Edge |
| 7교시 | 조건 분기·반복 | Conditional Edge·Routing |
| 8교시 | 상태 제어 | Checkpointer·Interrupt·HITL |

### 4일차

| 교시 | 주제 | 세부 내용 |
| --- | --- | --- |
| 1교시 | Plan-and-Execute | Planner·Executor 구조 |
| 2교시 | Replanning | 동적 재계획·실패 대응 |
| 3교시 | 오케스트레이션 검증 | assert·LangSmith 추적 |
| 4교시 | 운영 최적화 | 비용·지연·Evaluation |
| 5교시 | 하네스 설계 실습 | 루프·컨텍스트·메모리 |
| 6교시 | Advanced RAG (1) | Multi-Query·Hybrid·Rerank |
| 7교시 | Advanced RAG (2) | Adaptive·Corrective·Self-RAG |
| 8교시 | Deep Agent | Middleware·Memory·Todo |

### 5일차

| 교시 | 주제 | 세부 내용 |
| --- | --- | --- |
| 1교시 | 멀티에이전트 구조 | Supervisor·SubAgent·핸드오프 |
| 2교시 | 하네스 엔지니어링 심화 | 가드레일·컨텍스트·에러 복구 |
| 3교시 | A2A 연동 | MCP·A2A 비교·로컬 실습 |
| 4교시 | Agent 검증 | 관찰·평가·회귀 테스트 |
| 5교시 | 배포와 개선 | 상태 영속화·배포·개선 루프 |
| 6교시 | 종합 실습 (1) 설계·구현 | RAG·Tool·MCP·멀티에이전트 통합 |
| 7교시 | 종합 실습 (2) 검증·개선 | 오케스트레이션·하네스·검증 |
| 8교시 | 종합 실습 (3) 리뷰·풀이 | 실행·리뷰·Q&A |
