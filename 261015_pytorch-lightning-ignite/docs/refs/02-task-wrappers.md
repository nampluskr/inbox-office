> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# Task별 Wrapper 검토

## 확정된 요구

전체 지원 방향은 Classification, Regression, Segmentation, Object Detection,
Anomaly Detection, AutoEncoder, VAE, GAN이다. 첫 버전에 포함할 Task는 미정이다.
기존 모델 또는 Encoder·Decoder·Generator·Discriminator를 받아 학습·평가·추론에
사용한다. 기존 모델의 forward를 백엔드에 맞추어 다시 작성하도록 요구하지 않는다.

양쪽 Task는 training_step·validation_step·test_step·predict_step·configure_optimizers의
주요 Hook을 공통화하는 방향이다. 세부 인자와 반환값, 최적화 책임은
[공통 API](09-client-api-and-examples.md)에서 정하며 Task별 특성을 유지한다.

Lightning Wrapper는 native LightningModule와 Hook을 최대한 직접 사용한다. Ignite
Wrapper는 같은 주요 Hook을 제공하고 Engine에서 호출한다. Lightning을 순수 공통
Task의 실행 Adapter로만 제한하는 구조는 필수로 두지 않는다. 모델 구성요소와 Loss·
후처리 등 백엔드에 독립적인 코드는 별도로 공유할 수 있다.

## 검토 제안: Task별 계약

다음은 대표적인 계약 후보이며 모든 변형을 지원한다는 약속이 아니다.

| Task | 모델 구성 | 입력·타깃의 대표 예 | 원시 출력·예측의 대표 예 |
| --- | --- | --- | --- |
| Classification | model | 입력, 클래스 정답 | logits → 확률·클래스 ID |
| Regression | model | 입력, 연속값 정답 | 예측 Tensor → 원래 단위의 값 |
| Segmentation | model | 이미지, 마스크 | 픽셀별 출력 → 마스크 |
| Object Detection | model | 이미지 목록, 박스·라벨 | 모델별 출력 → 박스·점수·라벨 |
| Anomaly Detection | model 또는 구성요소 | 이미지, 선택적인 이상 라벨·마스크 | 알고리즘별 출력 → 점수·맵·판정 |
| AutoEncoder | encoder, decoder | 입력, 복원 대상 | 복원 Tensor → 복원 이미지 |
| VAE | encoder, decoder | 입력, 복원 대상 | 복원값 및 잠재분포 정보 → 복원·생성 결과 |
| GAN | generator, discriminator | 실제 데이터, 잠재 입력 | 생성 Tensor → 생성 결과 |

사용자가 가진 Tensor 출력 모델을 출발점으로 삼되, Detection·VAE 등의 복수 정보는
Wrapper나 작은 모델 조합 구성요소에서 해석하는 방안을 검토한다. 모든 모델에 동일한
출력 Tensor 형태를 강제하지 않는다. 구체적인 지원 모델을 정한 뒤 호환 범위를 명시한다.

## 학습과 추론의 차이

Classification·Regression·Segmentation은 단일 Loss 기반 경로를 먼저 검토할 수 있다.
분류도 이진·다중 클래스·다중 라벨에 따라 타깃, Loss와 후처리가 달라진다.
회귀에서는 타깃 변환과 출력 역변환의 단위가 일치해야 한다.

AE는 입력 자체가 복원 대상인 예를 다룰 수 있지만, 손상 입력에서 원본을 복원하는 경우는
입력과 타깃이 다르다. VAE는 Encoder 출력 해석, 재매개화, 복원 Loss와 KL 항의
스케일을 정해야 한다. GAN은 생성기·판별기 Loss와 업데이트 순서를 별도로 다뤄야 한다.

Detection은 입력 크기·가변 개수 타깃과 학습/평가 시 forward 계약을 확인해야 한다.
이미지와 타깃을 함께 전달하거나 학습 시 Loss 딕셔너리를 반환하는 모델은 Tensor 출력
모델과 다른 연결이 필요하다. Anomaly는 재구성 방식의 예제 하나로 전체 알고리즘을
일반화하지 않고, 지원 방식과 점수·임계값 의미를 먼저 정한다.

## Wrapper 책임 후보

- 배치에서 모델 입력·타깃·복원용 메타데이터를 분리한다.
- 모델 구성요소를 조합하고 Loss·Metric에 필요한 값을 제공한다.
- 학습 실행은 백엔드 기능에 연결한다. 공유 후처리에 backward나 optimizer.step을 넣지 않는다.
- 추론에 필요한 조합 로직은 독립 Predictor에서도 사용할 수 있게 검토한다.

## 미정

세부 Task 변형, 지원 모델, 기본 Loss·Metric, VAE 추론의 샘플링 정책, GAN 최적화 정책,
이상 탐지 학습·임계값 보정 방식은 미정이다. 단일/복수 Optimizer 여부를 Task 전체의
고정 상속 기준으로 삼을지도 아직 정하지 않았다.

근거는 [기존 Task 초안](drafts/design-1.md), [생성 모델 초안](drafts/design-2.md),
[BRIEF](../BRIEF.md)다. 출력 해석은 [04](04-outputs-and-postprocessing.md)에서 검토한다.
