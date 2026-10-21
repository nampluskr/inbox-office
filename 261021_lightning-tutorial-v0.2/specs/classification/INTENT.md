# Classification 기획 의도

[공통 목적·원칙](../INTENT.md)을 따른다.

## 목적과 대상

MNIST·MLP와 CIFAR-10·CNN을 통해 데이터와 모델을 바꿔도 같은 설정·학습·평가·독립 추론 흐름을 사용할 수 있게 한다. 순수 모델 구조와 Lightning 실행 책임을 구분하는 학습 예제를 제공한다.

## 범위

MNIST·CIFAR-10과 MLP·custom CNN·torchvision backbone을 다룬다. 분류는 num_classes가 2 이상인 다중 클래스 출력과 CrossEntropyLoss를 기준으로 한다. 출력 클래스가 2개인 분류도 같은 방식으로 표현한다.

출력 하나와 BCEWithLogitsLoss를 사용하는 별도 binary classification task는 현재 구현 범위에 포함하지 않는다. 양성 라벨·임계값·데이터셋은 후속 기획에서 정한다.

## Task 원칙

- 데이터 전처리는 Dataset·Transform에서 한 번 적용한다.
- 모델과 Wrapper의 forward는 logits를 반환한다.
- 확률·클래스 변환은 predict 단계의 공통 후처리로 분리한다.
- 실제 성능 확인과 짧은 실행 확인을 구별한다.

현재 계약은 [SPEC.md](SPEC.md), 실행은 [USAGE.md](USAGE.md), 확인된 상태는 [PROGRESS.md](PROGRESS.md)를 따른다.
