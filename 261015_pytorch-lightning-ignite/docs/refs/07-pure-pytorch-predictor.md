> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# 독립 순수 PyTorch Predictor

## 확정된 요구

학습된 가중치를 복원하여 Lightning·Ignite와 학습 Wrapper 없이 추론하는 Predictor를
별도로 작성한다. 기존 모델은 forward 역할을 유지한다. 기존 평가·추론용 transform과
native 경로에서 사용하는 공통 후처리를 재사용한다. native 평가·예측도 계속 제공한다.

## 검토 제안: 사용 흐름

```text
모델 생성 설정 → 기존 모델 구성 → 가중치 복원 → eval 모드
                                              ↓
원시 입력 → 평가용 transform → 배치 구성 ────────┤
이미 변환된 배치 ──────────────────────────────┤
                                              ↓
                                  장치 이동 → 모델 실행
                                              ↓
                                      공통 후처리 → 예측값
```

DataModule을 독립 추론의 필수 입력으로 요구하지 않는다. Dataset/DataLoader로 준비한
입력도 받을 수 있지만 LightningDataModule을 생성해야만 추론할 수 있게 만들지 않는다.

## 입력 경로 후보

| 경로 | 사용 예 | 입력 처리 |
| --- | --- | --- |
| 원시 입력 예측 | 이미지 한 장, 변환 전 Tensor | 같은 평가용 transform 적용, 배치 차원 구성 |
| 준비된 배치 예측 | Dataset/DataLoader에서 나온 입력 | 샘플 transform 생략, Task별 입력 구조 유지 |

predict/predict_batch 같은 별도 메서드 이름은 후보이며 확정 API가 아니다.
Tensor라는 이유만으로 이미 정규화됐다고 판단하지 않는다. GAN의 잠재벡터 입력과
AE/VAE의 이미지 입력도 같은 이미지 transform으로 일괄 처리하지 않는다.

필요하면 사용자 정의 preprocessing 함수나 Preprocessor를 선택적으로 주입할 수 있다.
이는 기존 평가용 transform을 대체하거나 별도 필요한 처리를 추가하는 용도이며,
어느 경우인지와 입력 상태를 명시해야 한다. 준비된 배치 경로에서는 같은 샘플 변환을
반복하지 않고, 명시한 추가 배치 처리만 계약에 따라 수행한다. 구체적인 주입 인자는 미정이다.

## 실행과 후처리

일반적인 추론에서는 model.eval과 inference_mode 또는 no_grad 사용을 검토한다.
inference_mode는 모델을 자동으로 eval 모드로 바꾸지 않으므로 둘을 구분해야 한다.
[PyTorch inference_mode](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html)

Task별 입력과 모델 구성에 맞게 forward를 실행하고 [공통 후처리](04-outputs-and-postprocessing.md)를
호출한다. 회귀 역변환 통계, 이미지 복원 메타데이터와 임계값도 동일하게 제공해야 한다.
반환 Tensor의 CPU 이동이나 NumPy 변환은 사용자 목적에 따른 옵션 후보로 남긴다.

## 복수 모델 구성요소

AE는 Encoder→Decoder, VAE는 잠재분포 해석과 샘플링 정책, GAN은 Generator 등
추론에 필요한 구성요소를 명시하는 방향을 제안한다. 학습 Wrapper 없이 필요한 조합을
재현할 수 있어야 하며, 단일 model 가중치만으로 모든 Task를 복원한다고 가정하지 않는다.
생성 전용 GAN 추론에 Discriminator까지 필수로 복원할지는 사용 목적별로 정한다.

## 의존성과 검증

공통 모델·transform·후처리·가중치 로더 경로에서 백엔드 import가 발생하지 않아야 한다.
패키지 최상위 import와 Factory에서도 이 경계를 지키는 방안을 검토한다.
PyTorch 외 이미지 입출력 등의 보조 의존성은 필요성과 지원 범위를 따로 정한다.

검증 시 Lightning·Ignite가 없는 환경에서 저장 결과물을 복원하고 native 예측과
샘플별 결과를 비교하는 것을 제안한다. 학습을 다시 실행해 양쪽 백엔드의 가중치가
동일해져야 한다는 의미는 아니다. [검증 문서](10-validation.md)

## 미정

구체적인 입력 타입, 배치 구성 규칙, context 전달, 모델 생성 함수·등록 방식,
VAE/GAN 확률 입력 정책, 반환 타입·장치와 Predictor의 클래스 분할은 미정이다.
가중치 형식은 [08](08-weights-and-checkpoints.md), 호출 예는 [09](09-client-api-and-examples.md)를 참조한다.
