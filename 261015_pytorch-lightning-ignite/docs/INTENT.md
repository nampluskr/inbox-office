# INTENT — pytorch-lightning-ignite

> 작성일: 2026-10-15 · 상태: 사용자 검토용 초안
>
> `refs/`의 요청 내용을 바탕으로 정리했다. 참고 문서의 구현 제안을 사용자 결정으로 간주하지 않는다.

## 무엇을 하는가

기존 순수 PyTorch 모델과 데이터 자산을 재사용하여, 작업 종류에 맞는 Wrapper로
학습·평가·추론을 수행할 수 있게 한다.

이 프로젝트의 큰 목적 중 하나는 Lightning을 최대한 native 그대로 사용하면서,
Ignite가 Lightning과 같은 공개 API와 사용 방식으로 동작하게 하는 것이다.
Lightning을 별도 공통 계층에 맞춰 다시 구현하는 대신 Lightning을 기준으로 Ignite를 연결한다.
이 기준은 CLI뿐 아니라 Task Wrapper, 학습·평가·추론과 Trainer·데이터 계층 전반에 적용한다.

분류, 회귀, 분할, 객체 탐지, 이상 탐지뿐 아니라 AutoEncoder, VAE, GAN처럼 여러 모델
구성요소를 조합하는 작업도 다룬다. Lightning과 Ignite를 공통된 사용 방식으로
이용하고, 기존 Dataset과 DataLoader도 DataModule을 통해 함께 사용할 수 있게 한다.

학습된 모델은 학습 프레임워크 없이도 사용할 수 있게 한다. 기존 모델의 출력과 실제
사용할 예측값 사이에 필요한 후처리를 적용하여 독립적으로 추론할 수 있게 한다.

## 왜 하는가

사용자는 이미 순전파가 정의된 순수 PyTorch 모델을 가지고 있다. 학습에 사용할 모델을
Task별 Wrapper에 전달하여 학습·평가·추론에 사용하고 싶다. Encoder, Decoder,
Generator, Discriminator도 기존 구성요소를 그대로 활용하고 싶다.

데이터 역시 이미 작성된 Dataset과 DataLoader를 활용하고 싶다. 모델을 실행하는
방식과 데이터를 제공하는 방식을 정리하여, Lightning과 Ignite를 사용할 때 반복해서
작성해야 하는 연결 코드를 줄이는 것이 목적이다.

Lightning의 기능과 사용 방식을 유지하면서 Ignite도 같은 방식으로 사용할 수 있으면,
사용자가 백엔드마다 학습·평가·예측 코드와 실행 설정을 다시 익히고 작성하는 부담을 줄일 수 있다.

## 변하지 않는 원칙

- 기존 모델의 순전파 코드를 학습 프레임워크에 맞추어 다시 작성하도록 요구하지 않는다.
- 작업별 특성을 유지하면서 학습·평가·추론을 일관된 방식으로 사용할 수 있게 한다.
- 단일 모델뿐 아니라 여러 모델 구성요소를 조합하는 작업도 다룬다.
- 기존 Dataset과 DataLoader를 재사용하며, DataModule을 공통 사용 방식에 포함한다.
- Lightning과 Ignite 양쪽에서 사용할 수 있는 것을 프로젝트의 지원 방향으로 삼는다.
- 각 학습 프레임워크가 제공하는 평가·예측 기능을 유지한다.
- Lightning의 native API·기능·실행 방식을 최대한 그대로 사용하고, Ignite의 공개 API를
  이에 맞춘다. 공통화를 위해 Lightning 기능을 축소하거나 별도 구현으로 대체하지 않는다.
- Lightning 구현과 검증·테스트를 먼저 완료하고, 검증된 동작과 공개 API를 기준으로
  Ignite를 구현한다. 두 백엔드의 구현을 병행하지 않는다.
- Wrapper와 실행 기능 전반에서 Lightning native를 기준으로 삼으며, Ignite는 같은
  공개 사용 방식을 제공하고 내부 실행은 Engine으로 구현한다.
- 백엔드를 바꾸어도 같은 사용 방식으로 학습·검증·평가·예측을 호출할 수 있게 한다.
  내부 실행과 확장 기능은 각 학습 프레임워크의 특성을 유지한다.
- 실행 설정을 파일로 관리하고 필요한 값만 명령줄에서 바꿀 수 있게 한다.
  Lightning은 공식 CLI를 그대로 활용하고 Ignite는 같은 설정·실행 방식을 제공한다.
- 학습된 모델을 독립적으로 추론하는 데 Lightning이나 Ignite를 요구하지 않는다.
- 기존 데이터 변환을 재사용하고, 실행 경로가 달라져도 평가·추론에 필요한 입력 처리와
  예측값 해석을 일관되게 유지한다. 같은 변환을 중복 적용하지 않는다.
- 전처리·후처리를 학습 백엔드에 종속시키지 않으며, 별도의 전처리 계층을 필수로 요구하지 않는다.
  기본 전처리는 기존 Dataset의 변환을 활용하고, 필요하면 사용자 정의 전처리도 선택적으로 사용할 수 있다.

## 다루지 않는 것

- 새로운 모델 구조나 학습 알고리즘을 발명하는 일. 기존 모델을 활용하는 것이 목적이다.
- 개별 프로젝트의 원천 데이터나 Dataset 구현을 대신 만드는 일. 이미 주어진 데이터
  자산을 연결하는 것을 출발점으로 한다.

## 근거

| 자료 | 의도에 반영한 내용 |
| --- | --- |
| [design-1.md](refs/drafts/design-1.md) 첫 질문 | 기존 순수 PyTorch 모델을 전달받는 Task별 Wrapper, 분류·분할·객체 탐지·이상 탐지의 학습·평가·추론 |
| [design-2.md](refs/drafts/design-2.md) 첫 질문 | AE·VAE·GAN 포함, Encoder·Decoder·Generator·Discriminator 재사용 |
| [design-3.md](refs/drafts/design-3.md) | Lightning·Ignite의 공통 클라이언트 API 검토. 내부 구조는 설계 제안으로 취급 |
| [design-4.md](refs/drafts/design-4.md) 첫 질문 | 기존 Dataset/DataLoader를 DataModule로 묶고 Ignite에도 같은 형식 적용 |
| 2026-10-15 사용자 확인 | DataModule 포함 |
| 2026-10-15 사용자 추가 요청 | Regression(회귀)을 전체 지원 대상에 포함 |
| 2026-10-15 사용자 결정 | Lightning·Ignite의 native 평가·예측 유지, 순수 PyTorch Predictor 별도 작성 |
| 2026-10-15 사용자 반영 요청 | Dataset의 transform·target_transform 재사용, 별도 Preprocessor는 선택, 후처리는 native 경로와 독립 Predictor에서 공유 |
| 2026-10-15 사용자 반영 요청 | Ignite 내부 Engine 실행을 유지하면서 Lightning과 같은 공개 호출 형태와 주요 Task Hook·데이터·반환 계약을 공통화 |
| 2026-10-15 사용자 반영 요청 | 실제 LightningCLI 사용, Ignite에서 같은 명령·config·명령줄 덮어쓰기와 설정 확인 방식 구현 |
| 2026-10-15 사용자 강조 | Lightning native 최대 활용과 Ignite의 동일 공개 API 구현은 프로젝트의 큰 목적 중 하나 |
| 2026-10-15 사용자 버전 지정 | v0.1은 Lightning 구현·검증·테스트, 완료 후 v0.2 또는 그 이후 버전에서 Ignite 구현 |
