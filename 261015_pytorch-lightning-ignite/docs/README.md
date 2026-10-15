# pytorch-lightning-ignite

## 개요

기존 순수 PyTorch 모델과 Dataset/DataLoader를 재사용하여, Task별 학습·평가·추론을
Lightning과 Ignite에서 수행하는 프레임워크 또는 boilerplate를 기획한다.
지원 방향은 분류, 회귀, 분할, 객체 탐지, 이상 탐지, AE, VAE, GAN이다.

큰 목적 중 하나는 **Lightning을 최대한 native 그대로 사용하고, Ignite가 Lightning과
같은 공개 API와 사용 방식으로 동작하게 하는 것**이다. Lightning의 native 기능을 기준으로
삼고 Ignite의 연결 계층을 구현한다.

이 원칙은 CLI뿐 아니라 Wrapper·학습·평가·추론·Trainer에도 적용한다. Lightning은
LightningModule·Trainer·LightningDataModule을 최대한 직접 사용하며, Ignite는 같은
주요 API를 제공하는 Wrapper·Trainer를 Engine으로 구현한다.

각 백엔드의 native 평가·예측을 유지하며, 학습된 가중치를 복원하여 백엔드 없이 추론하는
순수 PyTorch Predictor도 별도로 다룬다. 기존 데이터 transform과 공통 후처리를 재사용한다.

공개 API는 Lightning 형태의 fit·validate·test·predict로 맞추며, Ignite는 프로젝트
Trainer 내부에서 Factory·Engine으로 실행한다. 주요 Task Hook과 데이터·반환 계약을
공통화하고 백엔드별 확장 기능은 유지한다.

Lightning은 공식 LightningCLI를 그대로 사용하고, Ignite는 같은 서브커맨드와 config
기반 실행을 제공한다. 설정 파일의 값을 --xxx 인자로 덮어쓰고 최종 설정을 확인할 수
있는 사용 방식을 목표로 한다.

## 현재 상태

기획 문서 작성 단계다. v0.1은 Lightning 구현·검증·테스트를 진행한다.
완료 후 v0.2 또는 그 이후 버전에서 같은 API의 Ignite를 Engine으로 구현한다.
Ignite의 정확한 착수 버전과 v0.1 Task 세부 범위는 미정이다. 두 백엔드를 동시에 구현하지 않는다.
구현 패키지, 설치 방법, 검증된 실행 예제는 아직 없다.

## 문서 안내

| 문서 | 역할 |
| --- | --- |
| [INTENT.md](INTENT.md) | 목적과 변하지 않는 원칙. 프로젝트 SSOT |
| [BRIEF.md](BRIEF.md) | 이번 범위, 제외 대상, 검토용 완료 조건 |
| [DECISIONS.md](DECISIONS.md) | v0.1의 확정된 설계 방향, 근거와 배제한 대안 |
| [refs/README.md](refs/README.md) | 주제별 기술 검토 문서와 읽기 순서 |
| [예상 프로젝트 폴더 구조](refs/01-architecture.md#예상-프로젝트-폴더-구조) | 코드·config·테스트·초기화 후 문서의 전체 배치 제안 |
| [refs/drafts/](refs/drafts/) | 기존 design-1~4 원문 보관 |

먼저 INTENT와 BRIEF를 읽고 refs의 공통 계약, 백엔드 연결, 독립 추론 순서로 검토한다.
refs의 제안은 사용자 확정 전까지 요구나 구현 결정으로 간주하지 않는다.

## 기획 구조

아래는 현재 기획 문서의 구조다. 구현 프로젝트의 전체 예상 구조와 폴더별 책임은
[전체 구조 문서](refs/01-architecture.md#예상-프로젝트-폴더-구조)에 정리했다.
구현 코드는 src 바로 아래에 기능별 모듈을 두며 별도의 프로젝트명 패키지를 추가하지 않는다.
실행 진입점은 루트 main.py를 유지한다.

```text
pytorch-lightning-ignite/
├── README.md
├── INTENT.md
├── BRIEF.md
├── DECISIONS.md
└── refs/
    ├── README.md
    ├── 01-architecture.md
    ├── 02-task-wrappers.md
    ├── 03-data-and-transforms.md
    ├── 04-outputs-and-postprocessing.md
    ├── 05-lightning-backend.md
    ├── 06-ignite-backend.md
    ├── 07-pure-pytorch-predictor.md
    ├── 08-weights-and-checkpoints.md
    ├── 09-client-api-and-examples.md
    ├── 10-validation.md
    ├── 11-cli-and-config.md
    └── drafts/
        ├── design-1.md
        ├── design-2.md
        ├── design-3.md
        └── design-4.md
```

작업 기준은 `D:\projects\_clones\project-workflow\WORKFLOW.md`와
`docs/DOC-SCHEMA.md`다. 현재 버전은 v0.1이며 확정한 설계는 DECISIONS에 기록했다.
Task 세부 범위와 완료 조건이 정해지면 PLAN을 작성하고 필요하면 SPEC을 추가한다.
PROGRESS는 구현 시작 후 작성한다.
프로젝트 초기화와 활성 위치 이동은 별도 요청 시 진행한다.
