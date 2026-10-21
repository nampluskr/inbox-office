# Classification 명세

[공통 명세](../SPEC.md)를 따른다. 이 문서는 현재 classification의 구조·입출력·설정을 정의한다. 실행 예시는 [USAGE.md](USAGE.md)에 둔다.

## 구조

```text
src/classification/
├── configs/
│   ├── default.yaml
│   ├── trainer.yaml
│   ├── data/{mnist,cifar10}.yaml
│   └── models/{mlp,cnn}.yaml
├── data/
│   ├── mnist/{dataset.py,lightning_data.py}
│   └── cifar10/{dataset.py,lightning_data.py}
├── models/
│   ├── common/{metric.py,postprocess.py}
│   ├── mlp/{model.py,lightning_model.py}
│   └── cnn/{model.py,lightning_model.py}
└── trainers/{lightning_trainer.py,lightning_cli.py}
```

## 데이터

| 구분 | MNIST | CIFAR-10 |
|---|---|---|
| 순수 구성 | MNISTDataset·MNISTTransform | CIFAR10Dataset·CIFAR10Transform |
| DataModule | MNISTLitData | CIFAR10LitData |
| 로컬 원본 | train/t10k 이미지·라벨 IDX 또는 gzip | cifar-10-batches-py의 Python batch |
| 기본 분할 | train 55,000·valid 5,000·test 10,000 | train 45,000·valid 5,000·test 10,000 |
| 기본 batch size | 64 | 16 |
| 분할 설정 | valid_size=5000·seed=42 | valid_size=5000·seed=42 |

MNIST는 28×28 각 변에 2픽셀의 0 패딩을 적용하고 float32 0~1로 변환한다. 기본 출력은 1×32×32이며 in_channels=3이면 회색조를 복제한다. 추가 정규화·학습 증강은 없다. NumPy 입력은 채널 축을 확장해 torchvision 0.17의 ToImage와 연결한다.

CIFAR-10은 기본 3×32×32다. 학습에 RandomCrop(32, padding=4)·RandomHorizontalFlip을 적용하고 이후 Resize·float32 0~1 변환·ImageNet 정규화를 적용한다. valid/test는 증강을 제외한다. 분할 seed를 공유해 train/valid 인덱스가 겹치지 않도록 구성한다.

DataModule은 root를 명시적으로 전달받으며 DataLoader의 기본 num_workers는 0, pin_memory는 true다. 배치는 images [B,C,H,W]와 정수 targets [B]의 tuple이다.

## 모델과 Wrapper

| 구성 | 설정값 | 내부 구성 |
|---|---|---|
| MLPModel·MLPLitModel | image_size·in_channels·hidden_dims·num_classes | flatten·Linear/ReLU·분류층 |
| CNNModel·CNNLitModel | backbone·in_channels·num_classes·weights_path | custom CNN 또는 torchvision backbone |
| 두 Wrapper 공통 | learning_rate·weight_decay | CrossEntropyLoss·단계별 ClassificationMetric·ClassificationPostprocess |

MLP 기본 구조는 32×32×1 → 1024 → 256 → 128 → 10이다. CNN은 custom·resnet18·resnet50·efficientnet_b0를 지원한다. custom은 다섯 ConvBlock과 pooling·분류층을 사용한다.

CLI/YAML의 CNN 기본 backbone은 custom이다. 직접 생성할 때 순수 CNNModel의 기본값은 resnet50, CNNLitModel의 기본값은 resnet18이므로 명시적 backbone을 사용하는 것이 재현에 필요하다. custom만 1채널을 지원하며 torchvision backbone은 3채널을 요구한다.

torchvision 모델은 weights=None으로 생성하고 지정된 로컬 ImageNet state_dict를 strict 로드한 뒤 분류층을 교체한다. CLI·예제는 외부 backbone의 로컬 경로를 먼저 해석한다. 순수 CNNModel을 weights_path=None으로 직접 생성하면 무작위 초기화하며, 학습한 순수 가중치 복원에도 이 경로를 사용할 수 있다. custom은 backbone 가중치 인자를 받지 않는다.

## 학습·평가·예측

forward는 [B,num_classes] logits를 반환한다. Wrapper는 train/valid/test마다 별도 metric 상태를 관리하고 AdamW를 사용한다.

| 단계 | 로그·출력 |
|---|---|
| train/valid/test | stage_loss·stage_acc·stage_f1 |
| accuracy | micro accuracy |
| F1 | macro F1 |
| predict_step | probabilities [B,num_classes]·predictions [B]의 dict |

ClassificationPostprocess는 softmax와 argmax를 계산한다. predict 결과는 원래 장치에 남고 trainer.predict는 배치 결과의 리스트를 반환한다. 학습·검증·테스트의 loss·metric에는 logits를 직접 전달한다.

ClassificationLitTrainer는 valid_loss의 최솟값을 best 기준으로 사용한다. 기본 5 epoch, sanity validation 2단계, 진행 표시 활성화, 모델 요약 비활성화다. valid loss·accuracy·F1은 progress bar에서 제외하고 CSV·checkpoint 지표로 유지한다. MetricsPrinter는 각 train epoch 종료 후 현재 train_loss와 그 epoch의 valid_loss·valid_acc·valid_f1을 한 줄로 출력한다. CNN의 train_loss_epoch 키도 train_loss로 표시한다. standalone validate에서는 valid 지표만 출력한다.

## 선택·조합 기본값

ClassificationLitCLI는 data=mnist, model=mlp를 기본 선택한다. --data는 mnist·cifar10, --model은 mlp·cnn을 선택한다.

| 조합 | 기본 입력 채널 |
|---|---|
| MNIST·MLP/custom CNN | 1 |
| MNIST·torchvision CNN | 3 |
| CIFAR-10·MLP/CNN | 3 |

최종 backbone을 기준으로 조합별 기본값을 정하고 명시적인 사용자 채널을 우선한다. 데이터·모델 채널 불일치와 MLP 이미지 크기 불일치는 객체 생성 전에 오류다. MLP에는 backbone 인자가 없다.

기본 logger 이름은 classification-{dataset}-mlp 또는 classification-{dataset}-cnn-{backbone}이다. 공통 cnn.yaml을 병합한 Python 예제는 MNIST 입력 채널·예제별 logger 이름·ResNet18 backbone을 직접 덮어쓴다.

## 예제와 복원

네 Python 예제는 YAML 병합·설정 변경·경로 해석·시드·data/model/Trainer 생성·fit·best test를 명시한다. save_run_config와 save_run_results는 task Trainer 파일에서 공유한다.

model.pt는 best 평가 후 순수 모델의 CPU state_dict다. 복원할 때 모델 종류·입력 크기·채널·hidden_dims·클래스 수·backbone을 일치시키고 같은 평가 전처리를 사용한다. 순수 가중치는 Wrapper metric이나 후처리 객체를 포함하지 않는다.
