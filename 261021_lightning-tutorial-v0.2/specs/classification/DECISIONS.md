# Classification 설계 결정

[공통 결정](../DECISIONS.md)을 따른다. 현재 계약은 [SPEC.md](SPEC.md), 구현·검증 이력은 [PROGRESS.md](PROGRESS.md)에 둔다.

## 분류 기준

CrossEntropyLoss와 클래스별 logits를 기준으로 통일한다. num_classes가 2인 경우도 같은 다중 클래스 인터페이스로 처리한다. 출력 하나의 BCE 분류는 별도 task로 검토해 출력 수와 클래스 수를 혼동하지 않게 한다.

## 데이터와 채널

MNIST의 원래 픽셀을 유지하기 위해 보간 확대 대신 28→32 패딩을 사용한다. torchvision backbone에는 3채널 입력이 필요하므로 CLI 조합에 따라 회색조를 복제한다. pretrained 네트워크 구조를 수정하는 방식은 사용하지 않는다. MNIST의 추가 정규화는 도입하지 않는다.

CIFAR-10은 기존 RandomCrop·HorizontalFlip·ImageNet 정규화를 유지한다. Dataset·Transform은 dataset.py에, 분할과 DataLoader는 lightning_data.py에 모아 전처리와 분할 중복을 줄인다.

## 모델 이름과 공유 구성

순수 모델은 MLPModel·CNNModel, Wrapper는 MLPLitModel·CNNLitModel로 구분한다. 과거 CNNBackboneModel·CNNModule·ClassificationModel 등의 별칭은 제공하지 않는다. 이전 이름을 저장한 설정과 오래된 노트북은 별도 이식이 필요하다.

MLP·CNN이 실제로 공유하는 metric과 예측 후처리만 models/common에 둔다. loss는 단일 CrossEntropyLoss라 별도 registry나 선택 키를 만들지 않는다.

## CNN 설정 통합

custom·ResNet18 등의 별도 YAML을 만들지 않고 cnn.yaml과 backbone 인자를 사용한다. Python 예제의 변경값을 코드에 명시해 조합 차이를 보여준다. torchvision 원본 가중치는 분류층 교체 전에 로드한다.

기존 순수 CNNModel의 직접 생성 기본값과 Wrapper 기본값은 유지하며 CLI/YAML에서 custom을 명시한다. 순수 모델은 pretrained 없이 학습 가중치를 복원하는 용도로도 사용할 수 있으므로 weights_path=None 생성을 허용한다. CLI·예제의 외부 pretrained 선택은 로컬 경로를 요구한다.

## 예측과 저장

forward의 logits 계약을 유지하고 predict_step에서만 softmax·argmax를 수행한다. Predictor도 동일한 후처리 객체를 받아 재사용한다. 매개변수나 buffer가 없는 후처리 추가로 모델 state_dict 키를 바꾸지 않는다.

예제에서는 객체 생성과 fit/test 호출을 직접 보여주고, 설정·평가 JSON·순수 가중치 저장만 작은 함수로 공유한다. 학습 전체를 감싸는 실행 계층은 추가하지 않는다. CSVLogger 초기화 후 설정을 저장해 로그 폴더 초기화 경고를 방지한다.

## Epoch 지표 출력

valid 지표는 검증 종료에 계산되므로 학습 배치가 진행되는 동안 progress bar에 남겨두지 않는다. MetricsPrinter는 epoch별 train_loss·valid 지표의 터미널 요약을 위해 유지한다. CNN의 on_step/on_epoch 동시 로그는 train_loss_epoch에서 현재 epoch 값을 읽고, MLP는 train_loss를 읽는다. 검증이 실행되지 않은 epoch에 이전 valid 값을 다시 출력하지 않는다. 지표는 CSV와 checkpoint 선택에도 계속 사용한다.

## 참조

CNN 구조와 CIFAR-10 처리는 로컬 dl-lightning의 구현을 참조한 이력을 이어간다. 과거 참조 파일·해시와 이전 실행 검증은 [v0.1 결정 기록](../../v0.1/DECISIONS.MD)에 보존한다. 현재 이름·설정 변경 후의 전체 실행 검증과 구별한다.
