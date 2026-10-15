> 버전: v0.1 · 작성일: 2026-10-15 · 상태: 사용자 확정 사항을 정리한 초안

# DECISIONS — pytorch-lightning-ignite

[INTENT](INTENT.md)와 [BRIEF](BRIEF.md)를 기준으로 사용자가 확정한 설계 방향을 기록한다.
아래의 배제한 대안은 선택한 방향과 맞지 않는 구현 방식을 설명한다.
상세 검토는 [refs](refs/README.md)에 있으며, 이 문서는 구현·검증 완료를 뜻하지 않는다.

## D-1. Lightning native를 구현 기준으로 사용

- 선택: Wrapper는 LightningModule, 실행은 native Trainer, 데이터는 LightningDataModule,
  명령줄은 실제 LightningCLI를 최대한 직접 사용한다. 학습·검증·평가·추론 전반에 적용한다.
- 근거: Lightning 기능을 최대한 활용하고 Ignite가 같은 공개 API를 제공하는 것이
  프로젝트의 큰 목적이다. 공통화를 위해 Lightning을 축소하지 않는다.
- 배제한 대안: 양쪽을 위한 별도 최소 기능 Trainer·학습 루프로 Lightning을 대체하는 방식.
  필수 공통 Task 계층 앞뒤로 모든 실행을 우회시키는 방식도 native 우선 원칙에 맞지 않는다.
- 관련 검토: [전체 구조](refs/01-architecture.md), [Lightning](refs/05-lightning-backend.md).

## D-2. v0.1은 Lightning, 검증 후 후속 버전에서 Ignite 구현

- 선택: v0.1에서 Lightning 구현과 검증·테스트를 먼저 완료한다. 그 뒤 v0.2 또는 그 이후
  사용자가 지정하는 버전에서 같은 공개 API의 Ignite를 Engine으로 구현한다.
- 근거: 먼저 실제로 검증된 Lightning API와 동작을 확보하여 후속 구현의 기준으로 사용한다.
- 배제한 대안: 두 백엔드를 동시에 구현하거나 Lightning 검증·테스트가 끝나기 전에
  Ignite 구현을 시작하는 방식. Ignite 구현 완료를 v0.1 완료 조건에 넣는 방식도 배제한다.
- 관련 검토: [v0.1 범위](BRIEF.md), [검증 순서](refs/10-validation.md).

## D-3. Ignite가 Lightning의 공개 API에 맞춤

- 선택: 후속 Ignite는 fit·validate·test·predict, 주요 Task Hook, 단계별 DataModule,
  CLI·config 사용 방식과 반환 계약을 검증된 Lightning 기준에 맞춘다. 내부는 Engine으로 구현한다.
- 근거: 백엔드를 바꿀 때 사용자가 실행 코드와 설정 방식을 다시 작성하는 부담을 줄인다.
- 배제한 대안: 사용자가 Ignite에서만 Engine.run과 State를 직접 다루어야 하는 공개 API.
  Ignite의 차이를 이유로 Lightning native API·반환·옵션을 제한하는 방식도 배제한다.
- 관련 검토: [Ignite](refs/06-ignite-backend.md), [API](refs/09-client-api-and-examples.md).

## D-4. 기존 순수 PyTorch 모델을 Wrapper에 주입

- 선택: 기존 nn.Module과 Encoder·Decoder·Generator·Discriminator를 Wrapper에 전달한다.
  기존 모델은 forward로 원시 출력을 반환하는 역할을 유지한다.
- 근거: 사용자가 이미 작성한 모델을 수정하지 않고 학습·평가·추론에 재사용하려는 요구다.
- 배제한 대안: 모델 자체를 LightningModule로 다시 작성하거나 forward에 학습 반복·
  백엔드 의존성을 넣도록 요구하는 방식. 모든 Task를 하나의 출력 형태로 억지로 맞추지 않는다.
- 관련 검토: [Task Wrapper](refs/02-task-wrappers.md).

## D-5. 기존 Dataset/DataLoader를 DataModule로 연결

- 선택: 기존 Dataset과 기존 DataLoader 입력을 재사용한다. v0.1은 native
  LightningDataModule을 사용하고 후속 Ignite가 같은 단계별 Loader API를 제공한다.
- 근거: 기존 데이터 자산을 유지하면서 학습·검증·평가·추론 단계의 데이터 제공 방식을 정리한다.
- 배제한 대안: 공통 프레임워크 사용을 위해 기존 Dataset·Loader 전체를 다시 작성하도록
  요구하는 방식. DataModule에 Task의 Loss·모델 실행 책임까지 넣는 방식도 배제한다.
- 관련 검토: [데이터와 변환](refs/03-data-and-transforms.md).

## D-6. Dataset 변환을 기본으로 하고 사용자 정의 전처리는 선택적으로 연결

- 선택: 기본 전처리는 Dataset의 transform·target_transform에 둔다. 필요 시 사용자 정의
  함수나 Preprocessor를 transform 또는 명시적인 추가 처리 위치에 연결할 수 있게 한다.
  기존 변환의 대체인지 추가 처리인지 구분하고 중복 적용하지 않는다.
- 근거: 기존 변환을 재사용하면서 Dataset 밖의 입력·배치 처리도 필요한 경우 지원한다.
- 배제한 대안: 모든 사용자에게 별도 Preprocessor 구현·상속을 요구하는 방식. 이미
  변환된 배치에 같은 샘플 변환을 다시 적용하거나 Tensor 타입만으로 변환 여부를 추측하는 방식.
- 관련 검토: [전처리 확장](refs/03-data-and-transforms.md), [독립 추론](refs/07-pure-pytorch-predictor.md).

## D-7. 후처리를 순수 PyTorch 공통 코드로 분리

- 선택: argmax·역정규화 등 필요한 출력 후처리를 Dataset·학습 백엔드와 분리하여
  native 평가·예측과 독립 Predictor에서 재사용한다. Loss·Metric에 필요한 원시 정보는 유지한다.
- 근거: 실행 경로가 달라져도 실제 예측의 해석을 일치시키고 기존 모델의 forward 역할을 유지한다.
- 배제한 대안: 후처리를 Lightning Wrapper 안에서만 사용할 수 있게 만드는 방식.
  모든 Loss·Metric 입력을 최종 클래스 ID나 표시용 이미지로 바꾸는 방식도 배제한다.
- 관련 검토: [출력과 후처리](refs/04-outputs-and-postprocessing.md).

## D-8. native 예측과 별도의 순수 PyTorch Predictor 제공

- 선택: native 평가·예측을 유지하며, 학습된 가중치를 복원해 Lightning·Ignite 없이
  실행하는 독립 Predictor를 별도로 작성한다. 평가용 transform과 공통 후처리를 재사용한다.
- 근거: 학습이 끝난 순수 모델을 사용하는 데 학습 프레임워크가 필요하지 않아야 한다.
- 배제한 대안: 추론에 학습 Wrapper·Trainer·CLI를 필수로 요구하는 방식. 독립 Predictor가
  native 평가·예측을 대체하도록 연결하는 방식도 배제한다.
- 관련 검토: [Predictor](refs/07-pure-pytorch-predictor.md), [가중치](refs/08-weights-and-checkpoints.md).

## D-9. 실제 LightningCLI와 config 기반 실행 사용

- 선택: v0.1은 실제 LightningCLI로 객체를 생성하고 명령을 실행한다. 설정 파일을 사용하고
  --xxx로 값을 덮어쓰며 --help·--print_config로 설정을 확인한다. 후속 Ignite가 같은 방식을 제공한다.
- 근거: native CLI 기능을 그대로 활용하면서 코드 수정 없이 실행 설정을 바꾸려는 요구다.
- 배제한 대안: Lightning용 자체 파서로 native CLI를 교체하는 방식. CLI 기본 실행 이후
  fit 등을 다시 호출하거나 Ignite 미지원 옵션을 조용히 무시하는 방식도 배제한다.
- 관련 검토: [CLI와 config](refs/11-cli-and-config.md).

## D-10. src 바로 아래에 기능별 모듈 배치

- 선택: src/core·src/backends·src/inference 등으로 배치하고 프로젝트명 패키지를
  중간에 추가하지 않는다. 루트 main.py를 진입점으로 유지하고 import·class_path를 맞춘다.
- 근거: 사용자가 src 아래에 별도 패키지명 없이 작성하도록 지정했다. 기존 CLI 명령 형태를 유지한다.
- 배제한 대안: src/pytorch_lightning_ignite 아래로 모듈을 한 번 더 감싸는 구조.
  폴더 변경만을 이유로 사용자에게 src 내부 파일의 직접 실행을 요구하는 방식도 배제한다.
- 관련 검토: [예상 폴더 구조](refs/01-architecture.md#예상-프로젝트-폴더-구조).
