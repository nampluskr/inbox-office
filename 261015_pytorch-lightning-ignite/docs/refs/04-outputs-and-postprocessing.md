> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# 원시 출력, 평가 입력과 공통 후처리

## 확정된 요구

기존 모델의 forward는 원시 출력을 반환한다. 후처리는 Dataset과 분리하고 순수
PyTorch 기반으로 작성하여 Lightning·Ignite의 native 경로와 독립 Predictor에서
재사용한다. Loss·Metric에 필요한 원시 출력과 점수 정보를 유지한다.

## 검토 제안: 출력의 소비자 구분

```text
model(inputs) → raw_outputs
                  ├→ Loss용 값 → Loss
                  ├→ 지표별 변환 → Metric
                  └→ postprocess → 사용자 예측값
```

후처리를 모델 출력 변수에 덮어쓴 뒤 Loss를 계산하지 않는다. 지표에 맞는 변환과 최종
예측 후처리가 같을 때는 함수를 공유하되, 항상 같은 변환이어야 한다고 가정하지 않는다.

| Task 예 | 원시 출력 | 실제 예측 후처리 후보 | 평가 시 고려 |
| --- | --- | --- | --- |
| 다중 클래스 분류 | logits | softmax, argmax, 클래스 이름 매핑 | Loss·확률 기반 지표·클래스 기반 지표 구분 |
| 회귀 | 연속값 Tensor | 타깃 역정규화, 단위 복원 | 예측과 정답의 평가 단위 일치 |
| 분할 | 픽셀별 logits | 마스크, 원본 크기 복원 | 보간·임계값·argmax 적용 순서 |
| 객체 탐지 | 모델별 출력 | 박스 복호화, NMS, 좌표 복원 | 모델이 이미 수행한 NMS 중복 방지 |
| 이상 탐지 | 점수·특징·복원값 등 | 이상 점수·맵·임계값 판정 | 연속 점수와 이진 판정 구분 |
| AE·VAE·GAN | 복원·생성 Tensor | 출력 범위 변환, 필요한 경우 역정규화 | 학습 출력 공간과 표시용 공간 구분 |

모델 입력에 정규화를 적용했다는 이유만으로 출력에 역정규화를 적용하지 않는다.
정규화된 이미지를 복원하도록 학습한 출력에는 적용할 수 있지만, logits·잠재벡터에는
그대로 적용할 수 없다. 역정규화와 화면 표시용 clamp/정수 변환도 구분하는 것을 제안한다.

## 공통 후처리 계약 후보

개념적으로 `postprocess(raw_outputs, context)`를 검토한다. context는 원본 크기나
좌표 복원 정보가 필요한 경우만 사용한다. callable, nn.Module 또는 데이터 클래스 중
구체적인 형식은 미정이다.

- Lightning·Ignite 객체를 인자로 요구하지 않는다.
- 원시 출력과 전달받은 설정을 제자리에서 변경하지 않는 방향을 제안한다.
- CPU 이동·NumPy 변환은 필수로 하지 않는다. 반환 장치 정책을 별도로 정한다.
- 클래스 순서, 임계값, 정규화 통계처럼 결과를 바꾸는 설정을 복원할 수 있게 한다.
- Tensor 하나로 합치기 어려운 결과는 샘플 단위 구조를 보존한다.

검토할 반환 정보는 분류의 확률·클래스 ID, 탐지의 박스·점수·라벨, 이상 탐지의 점수·맵,
회귀의 값·단위 등이다. 공통 결과 클래스나 필드명을 이 문서에서 확정하지 않는다.

## native 경로와의 관계

native 평가에서는 Metric이 필요한 표현을 선택한다. native 예측에서는 공통 후처리를
호출한다. 공개 Trainer API의 평가·예측 결과는 Lightning native의 반환 방식을 기준으로
Ignite가 맞추는 방향으로 정리한다. Ignite Engine State는 Ignite 연결 계층에서 해석하며,
사용자가 Engine State를 직접 읽어야 하는 형태를 공통 API로 삼지 않는다.
공통화를 위해 Lightning의 native 반환을 별도 형식으로 바꾸도록 요구하지 않는다.
공통 컨테이너와 필드, 배치·샘플 단위 규칙은 [09](09-client-api-and-examples.md)에서 확정해야 한다.

## 미정

Task별 결과 형식, Metric 입력 변환 인터페이스, 후처리의 장치·dtype 정책, context 형식,
원시 출력 동시 반환 옵션과 설정 직렬화 방식은 미정이다.

근거: [INTENT](../INTENT.md), [BRIEF](../BRIEF.md),
[기존 API·출력 검토](drafts/design-3.md). 백엔드 연결은 [05](05-lightning-backend.md)와
[06](06-ignite-backend.md), 독립 추론은 [07](07-pure-pytorch-predictor.md)을 참조한다.
