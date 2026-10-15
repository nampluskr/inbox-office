> 대상 버전: v0.2 또는 그 이후(착수 버전 미정) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# Ignite native 실행 연결

## 확정된 요구

Ignite는 v0.1 구현 범위 밖이다. Lightning 구현과 검증·테스트가 완료된 뒤 v0.2 또는
그 이후 버전에서 착수한다. 정확한 버전은 사용자가 지정하며 이 문서는 후속 검토 자료다.
아래 API·구성 후보는 검증된 Lightning 구현을 기준으로 상세화한다.

Ignite 기능을 활용하는 학습·평가·예측 경로를 유지한다. DataModule과 같은 형식으로
데이터를 제공하고 공통 후처리를 연결한다. 별도 순수 PyTorch Predictor가 native
경로를 대체하지 않는다.

공개 API의 기준은 Lightning native다. CLI뿐 아니라 Task Wrapper·Trainer·학습·검증·
평가·예측의 주요 API를 맞추고, Ignite는 내부 Engine 구현으로 연결한다. 이를 위해
Lightning 쪽에 공통 최소 기능 Wrapper나 별도 Trainer를 강제하지 않는다.

Lightning과 같은 형태의 fit·validate·test·predict를 제공하는 프로젝트 Trainer를
작성한다. 주요 Task Hook, DataModule의 단계별 Loader와 평가·예측 반환 계약을
공통화하고, 내부에서는 Ignite Factory·Engine·Event·Handler를 활용한다.

## 공개 Trainer와 native 실행

IgniteTrainer라는 클래스명은 후보이며, 같은 공개 호출 형태를 제공하는 방향은 확정이다.
아래는 호출과 내부 실행의 대응이다.

| 공개 호출 | 내부 실행 | 데이터 |
| --- | --- | --- |
| fit(task, datamodule=dm) | 학습 Engine과 선택적 validation 연결 | train, 선택적 validation |
| validate(task, datamodule=dm) | 검증 evaluator 실행 | validation |
| test(task, datamodule=dm) | 테스트 evaluator 실행 | test |
| predict(task, datamodule=dm) | 예측 Engine과 공통 후처리 | predict |

validate와 test는 데이터와 Metric 상태를 구분한다. evaluator 인스턴스를 분리할지,
설정·상태를 초기화하여 재사용할지는 미정이다. 프로젝트 Trainer가 DataModule 수명 관리와
native 결과의 공통 반환 계약 연결을 담당한다. Lightning을 import하는 계층으로 만들지 않는다.

## 검토 제안: Engine 기반 구성

Ignite의 Engine은 배치별 process_function을 실행하고 이벤트를 발생시킨다.
평가에는 supervised evaluator를 활용할 수 있다. 예측은 이 프로젝트가 Engine에
예측 step을 연결한다. 공개 predict 메서드는 프로젝트 Trainer가 제공하고 Engine.run으로
실행한다. [Ignite Engine 안내](https://docs.pytorch.org/ignite/engine.html)

| 기능 | 연결 후보 | 공통 코드와의 경계 |
| --- | --- | --- |
| 표준 지도학습 | create_supervised_trainer | 입력·Loss 계약이 맞는 Task에 사용 |
| 표준 평가 | create_supervised_evaluator | Metric별 입력 표현 보존 |
| 특수 학습 | Custom Engine | Task별 모델 조합·최적화 정책 연결 |
| 예측 | 예측용 Engine | eval 모드·gradient 비활성화·공통 후처리 |
| DataModule | 프로젝트의 일반 Python 클래스 | 단계별 Loader 추출과 수명 관리 |

## Factory 변환 인자의 역할

Trainer의 prepare_batch는 입력 준비, model_transform은 Loss에 필요한 모델 출력 변환,
output_transform은 Engine State에 노출할 step 결과 구성을 담당한다.
[공식 trainer API](https://docs.pytorch.org/ignite/generated/ignite.engine.create_supervised_trainer.html)

Evaluator에도 모델·출력 변환 지점이 있다. 최종 클래스 ID만 공통 출력으로 내보내면
Loss나 확률 기반 Metric에 필요한 정보가 사라질 수 있으므로, 필요한 원시 출력과 타깃을
함께 보존하고 Metric별로 선택하는 구성을 검토한다.
[공식 evaluator API](https://docs.pytorch.org/ignite/generated/ignite.engine.create_supervised_evaluator.html)

이미 Dataset이 transform을 적용한 배치에 prepare_batch가 같은 transform을 다시
적용하지 않게 한다. 장치 이동, 입력 분리와 실제 데이터 변환은 개념적으로 구분한다.

## 공통 Task Hook과 최적화 계약

주요 Hook은 training_step·validation_step·test_step·predict_step·configure_optimizers로
맞추는 방향이다. 구체적인 인자와 반환값은 [09](09-client-api-and-examples.md)에서 검토한다.
Engine의 process_function이 해당 Hook을 호출하도록 연결한다.

단일 Optimizer에서는 training_step이 Loss를 반환하고 실행 계층이 backward와 step을
처리하는 방안을 제안한다. GAN 같은 복수 Optimizer 작업은 업데이트 순서, gradient 제어와
백엔드별 최적화 API 연결 계약을 별도로 정해야 한다. Hook 이름만으로 Lightning과 같은
전체 동작이 보장된다고 가정하지 않는다.

## Task와 수명 관리

AE는 입력과 복원 타깃을 준비하여 표준 Factory에 연결할 수 있는지 검토한다.
VAE는 복원값과 잠재분포 정보를 Loss까지 전달해야 한다. GAN은 생성기·판별기 업데이트를
위한 전용 step 후보를 검토한다. 모든 Task를 supervised Factory에 억지로 맞추지 않는다.

Ignite용 DataModule은 Lightning을 상속하거나 import하지 않는 방향을 제안한다.
실행 계층이 setup과 단계별 Loader를 연결하고 종료·예외 시 정리를 담당한다.
정확한 수명 계약은 [03](03-data-and-transforms.md)에서 확정해야 한다.

fit/validate/test/predict를 반복 호출할 때 handler 중복 등록, Metric 누적 상태, 예측 결과
보관 상태와 Engine 재실행 의미를 검증해야 한다. 예측 결과를 모으는 구체적인 Handler나
반환 형식의 세부 스키마는 아직 정하지 않았다. 공개 API는 공통 반환 계약에 맞추고,
내부 Engine State와 Handler는 백엔드 확장 경로에서 접근하는 방안을 검토한다.

각 백엔드 확장 기능은 유지하며 Ignite가 지원하는 옵션과 백엔드 전용 옵션의 경계를
명시한다. Ignite의 미지원 옵션을 이유로 Lightning native 기능을 제한하지 않는다.

## LightningCLI와 같은 명령줄 사용 방식

프로젝트 CLI는 fit·validate·test·predict, YAML/JSON config, --xxx 덮어쓰기,
--help·--print_config와 적용 설정 기록을 제공한다. trainer·model·data와 최적화 설정을
해석하여 Ignite 객체를 생성하고 프로젝트 Trainer의 같은 명령으로 전달한다.

실제 LightningCLI에 IgniteTrainer를 그대로 전달해 동작한다고 가정하지 않는다.
Ignite용 파서와 객체 생성 연결을 별도로 작성하며 jsonargparse는 구현 후보로 검토한다.
지원하지 않는 Lightning 전용 옵션을 조용히 무시하지 않고 명확히 보고한다.
config와 클래스 경로, 백엔드별 옵션 의미는 [11](11-cli-and-config.md)을 따른다.

## 미정

공개 Trainer의 클래스명·세부 인자, Wrapper 구성과 Factory 적용 Task, 공통 Hook의
반환값·최적화 책임, 공개 반환 스키마, Engine별 출력 형식, handler 연결·해제 정책,
validation 미제공 처리, 지원 버전, AMP·분산학습·학습 재개 지원 범위가 남아 있다.
CLI 파서·지원 옵션 대응표·config 기록 정책과 백엔드 선택 문법도 미정이다.
평가·예측의 공유 후처리는 [04](04-outputs-and-postprocessing.md),
가중치 저장은 [08](08-weights-and-checkpoints.md)를 기준으로 검토한다.

기존 근거: [Native Wrapper 초안](drafts/design-3.md), [데이터 초안](drafts/design-4.md).
