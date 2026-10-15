> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# Lightning native 실행 연결

## 확정된 요구

이 문서는 v0.1의 구현 대상이다. Lightning 구현과 검증·테스트를 먼저 완료하고,
실제로 검증된 API와 동작을 후속 Ignite 구현의 기준으로 남긴다. Ignite를 병행 구현하지 않는다.

Lightning의 native 학습·평가·예측을 사용한다. 기존 순수 모델과 데이터 변환을 유지하고,
공통 후처리를 연결한다. 독립 Predictor는 이 경로와 별도로 제공한다.

Lightning을 최대한 native 그대로 사용하는 것이 기준이다. Ignite가 Lightning의 공개
API와 사용 방식에 맞추며, Lightning 쪽에 Ignite 호환을 위한 별도 Trainer를 필수로 두지 않는다.

이 기준은 Wrapper·학습·검증·평가·추론 전반에 적용한다. Task별 LightningModule의
training_step·validation_step·test_step·predict_step과 configure_optimizers를 구현하고,
반복 실행·최적화·수명 관리는 가능한 한 native Trainer 기능을 활용한다.

fit·validate·test·predict의 공개 호출 형태는 Ignite용 Trainer와 맞춘다. 주요 Task Hook,
DataModule의 단계별 Loader와 평가·예측 반환 계약도 공통화 대상으로 삼는다.

## 검토 제안: native 구성

| 역할 | 연결 후보 |
| --- | --- |
| 모델과 학습 처리 | LightningModule 기반 Task Wrapper |
| 학습 | Trainer.fit와 training_step |
| 검증·평가 | Trainer.validate/test와 validation_step/test_step |
| 예측 | Trainer.predict와 predict_step |
| 단계별 데이터 | LightningDataModule |
| 사용자 후처리 | predict_step에서 공통 callable 호출 |

Lightning 쪽 공개 Trainer는 native Trainer를 사용한다. native 반환을 공통 계약의
기준으로 삼으며, 학습·평가·예측 루프를 독립 Predictor로 교체하지 않는다.
Callback·정밀도·분산 실행 등은 native 기능을 활용한다.

LightningModule의 step Hook에 작업별 처리를 연결하는 방식은
[공식 API](https://lightning.ai/docs/pytorch/2.2.2/optional-api/api/lightning.pytorch.core.LightningModule)를
참고했다. 이 링크의 버전을 프로젝트 지원 버전으로 지정한 것은 아니다.

## 데이터와 출력 연결

Dataset/DataModule을 통과한 입력에는 transform을 다시 적용하지 않는다. 배치에서
입력·타깃·메타데이터를 분리하는 코드는 Task별 계약에 따른다. 추가 배치 처리가 필요하면
전송 전후 Hook 또는 step 연결을 검토하되 처리 소유자를 하나로 정한다.

training_step은 원시 출력으로 Loss를 계산한다. validation/test는 필요한 Loss와
Metric을 계산하고, predict_step은 원시 출력에 공통 후처리를 적용한다. 정답이 없는
예측 배치를 지원하며, tuple/list 형태만으로 입력·정답 여부를 추측하지 않는다.
상세 규칙은 [데이터](03-data-and-transforms.md)와 [출력](04-outputs-and-postprocessing.md)을 따른다.

## 생성 모델과 특수 학습

AE·VAE의 구성요소 조합은 Task별로 검토한다. GAN은 복수 Optimizer의 업데이트 순서와
gradient 제어가 필요하다. Lightning의 manual optimization API를 사용하여 연결하는
방안을 제안한다. `manual_backward`와 optimizer toggle 기능은
[공식 API](https://lightning.ai/docs/pytorch/2.2.2/optional-api/api/lightning.pytorch.core.LightningModule)에서
확인할 수 있다. 일반 PyTorch backward를 공유 후처리에 넣지 않는다.

## DataModule과 가중치

데이터 수명 관리는 Trainer와 native DataModule에 맡긴다. Wrapper가 prepare_data나
setup을 다시 호출하여 수명 관리를 중복하지 않도록 검토한다.
[공식 DataModule 사용법](https://api.lightning.ai/docs/pytorch/stable/data/datamodule)

추론용 저장은 학습 Wrapper 전체와 구분하여 실제 모델 구성요소의 가중치를 내보내는
방향을 검토한다. 복원 시 LightningModule이 반드시 필요해지는 형태는 독립 Predictor의
요구와 맞지 않는다. 형식은 [08](08-weights-and-checkpoints.md)에서 검토한다.

## LightningCLI 직접 사용

명령줄 진입점은 실제 LightningCLI를 사용한다. Task는 LightningModule, 데이터 계층은
LightningDataModule로 등록하고 native Trainer를 생성한다. Lightning 동작을 제한하는
별도 공통 파서로 교체하지 않는다. 프로젝트 확장이 필요하면 공식 확장 지점을 사용한다.

기본 실행 모드에서는 CLI가 선택한 명령을 실행하므로 사용자 진입점에서 fit 등을 다시
호출하지 않는다. Python 공개 API의 추가 계층도 LightningCLI의 native 객체 생성을
방해하지 않도록 한다. config 구조·우선순위·예시는 [11](11-cli-and-config.md)을 참조한다.

## 미정

- native Task Wrapper의 내부 상속과 순수 공통 코드 재사용 단위.
- Metric 구현, 로깅, 체크포인트, AMP·분산학습의 이번 버전 지원 범위.
- 공통 평가·예측 반환 구조, 공개 Trainer의 클래스명과 native 객체를 노출하는 방법.
- 지원 Lightning·PyTorch 버전과 반복 실행 검증 환경.

구현 예시는 [09](09-client-api-and-examples.md)의 검토용 호출 흐름을 참조한다.
기존 근거는 [Native Wrapper 초안](drafts/design-3.md)과 [DataModule 초안](drafts/design-4.md)이다.
