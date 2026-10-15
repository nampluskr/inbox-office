# 기술 검토 문서 안내

> 작성일: 2026-10-15 · 상태: 재작성 초안 · 기준 버전: v0.1 · Ignite: v0.2 또는 그 이후

## 문서의 기준

의도는 [INTENT](../INTENT.md), 이번 범위는 [BRIEF](../BRIEF.md)를 따른다.
이 폴더는 기술 검토 근거를 담으며 요구사항 명세나 구현 계획을 대신하지 않는다.

프로젝트의 큰 목적 중 하나는 Lightning의 Wrapper·학습·평가·추론·Trainer·DataModule·
CLI를 최대한 native 그대로 사용하고, Ignite가 같은 공개 API를 Engine으로 구현하는 것이다.
모든 검토 문서는 이 기준을 따르며, Lightning 쪽을 공통 최소 기능 계층으로 축소하지 않는다.

각 문서의 상태 표기는 다음과 같다.

| 표기 | 의미 |
| --- | --- |
| 확정된 요구 | 사용자 요청 또는 확인으로 INTENT·BRIEF에 반영된 내용 |
| 검토 제안 | 요구를 실현하기 위한 후보. 구현 결정으로 확정되지 않음 |
| 미정 | 사용자 판단이나 구체적인 검증 대상이 더 필요한 항목 |

fit·validate·test·predict의 공개 호출 형태와 주요 Task Hook·데이터·반환 계약 공통화는
사용자가 반영을 요청한 방향이다. 구체적인 클래스명·인자·반환 스키마는 미정이며,
문서의 구현 예시는 실행 검증되지 않았다.
LightningCLI 직접 사용과 Ignite의 같은 CLI·config 사용 방식도 사용자 확인 사항이다.
현재 프로젝트 버전은 v0.1이다. Ignite 착수 버전, 지원 라이브러리 버전과 실행 환경은 미정이다.
공식 문서 링크는 확인일 기준 API 근거이며 지원 버전 확정을 의미하지 않는다.

## 문서 목록과 읽기 순서

구현 순서는 v0.1 Lightning → 검증·테스트 완료 → v0.2 또는 그 이후 Ignite다.
Ignite 착수 버전은 미정이며 두 백엔드를 병행 구현하지 않는다. 아래 6번 문서와 다른
문서의 Ignite 대응·양쪽 비교 부분은 후속 검토다. 폴더 구조에 Ignite가 표시되어 있어도
v0.1에서 코드·설정·테스트를 생성한다는 뜻은 아니다.

| 순서 | 문서 | 주제 | 검토 상태 |
| --- | --- | --- | --- |
| 1 | [전체 구조](01-architecture.md) | 책임, 의존 방향, 두 추론 경로 | 사용자 검토 전 |
| 2 | [Task Wrapper](02-task-wrappers.md) | 여덟 Task의 모델·학습 특성 | 사용자 검토 전 |
| 3 | [데이터와 변환](03-data-and-transforms.md) | DataModule, transform, 입력 경로 | 사용자 검토 전 |
| 4 | [출력과 후처리](04-outputs-and-postprocessing.md) | 원시 출력, Loss·Metric, 실제 예측값 | 사용자 검토 전 |
| 5 | [Lightning](05-lightning-backend.md) | native 실행 연결 | 사용자 검토 전 |
| 6 | [Ignite](06-ignite-backend.md) | Lightning 형태의 공개 Trainer와 내부 Engine 연결 | v0.2 또는 그 이후 후속 검토 |
| 7 | [독립 Predictor](07-pure-pytorch-predictor.md) | 백엔드 없는 추론 | 사용자 검토 전 |
| 8 | [가중치와 체크포인트](08-weights-and-checkpoints.md) | 추론용 저장·복원과 학습 재개 구분 | 사용자 검토 전 |
| 9 | [클라이언트 API](09-client-api-and-examples.md) | 공통 호출·Hook·반환 계약과 사용 흐름 | 공통 API 방향 반영, 세부 검토 전 |
| 10 | [검증](10-validation.md) | 검증 시나리오와 판정 항목 | 사용자 검토 전 |
| 11 | [CLI와 config](11-cli-and-config.md) | 실제 LightningCLI, Ignite 대응, YAML과 명령줄 덮어쓰기 | CLI 방향 반영, 세부 검토 전 |

1~4가 공통 계약의 검토 위치다. 5~6은 백엔드 연결 방법을 다루고 공통 계약을
재정의하지 않는다. 7~8은 독립 추론과 복원, 9~10은 사용성과 검증을 다룬다.
11은 CLI에서 공통 API를 구성·실행하는 방법을 다룬다.

## 기존 초안의 취급

[drafts/](drafts/)에 옮긴 원문은 과거 검토 자료로 보관한다. 서로 충돌하는 제안이나
실행되지 않은 코드가 있으며 현재 설계 결정으로 사용하지 않는다.

| 원문 | 새 문서에서 검토한 내용 |
| --- | --- |
| [design-1.md](drafts/design-1.md) | 최초 Task 요구, 공통 Task 계층 후보 → 1·2·4·5·6 |
| [design-2.md](drafts/design-2.md) | AE·VAE·GAN, 복수 구성요소와 최적화 → 2·5·6·8 |
| [design-3.md](drafts/design-3.md) | Native Wrapper 후보, 공통 API → 1·5·6·9 |
| [design-4.md](drafts/design-4.md) | Dataset/DataLoader, DataModule → 3·5·6 |

회귀, 독립 Predictor, native 평가·예측 유지, transform 재사용과 후처리 공유는
원문 이후의 사용자 요청을 기준 문서에서 확인하여 반영했다.
Lightning 형태의 공통 공개 API와 Ignite 내부 Engine 실행도 후속 사용자 요청으로 반영했다.
실제 LightningCLI 사용과 Ignite에서 같은 config 기반 CLI 동작을 구현하는 요구도 반영했다.

## 다음 검토에서 정할 것

v0.1 Task 세부 범위, 내부 Task 구조, 데이터·예측 계약, 추론용 저장 형식과 검증 환경이
남아 있다. Ignite 착수 버전도 별도 결정한다. 확정된 설계는 [DECISIONS](../DECISIONS.md)에 기록했다.
이 문서 묶음을 작성한 것으로 구현 착수나 해당 항목의 승인이 이루어진 것은 아니다.
