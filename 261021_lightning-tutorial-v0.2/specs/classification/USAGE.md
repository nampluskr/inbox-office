# Classification 사용법

[프로젝트 안내](../../../README.md)에서 환경과 로컬 경로를 준비한다. 이하 python은 필요한 패키지가 설치된 Python 3.11 실행 파일이며 명령은 프로젝트 루트에서 실행한다. 공통 우선순위·경로 규칙은 [공통 명세](../SPEC.md), 현재 계약은 [SPEC.md](SPEC.md)를 따른다.

## 데이터와 가중치 준비

[paths.example.toml](../../../paths.example.toml)을 paths.toml로 복사하고 자신의 경로를 지정한다.

```toml
[datasets]
mnist = "E:/datasets/mnist"
cifar10 = "E:/datasets/cifar10"

[backbones]
resnet18 = "E:/backbones/resnet18-f37072fd.pth"
```

MNIST 디렉터리에는 train-images-idx3-ubyte·train-labels-idx1-ubyte·t10k-images-idx3-ubyte·t10k-labels-idx1-ubyte가 필요하다. 각각 .gz 파일도 직접 읽는다. CIFAR-10 root 아래에는 cifar-10-batches-py/data_batch_1~5와 test_batch를 준비한다. 데이터와 pretrained 파일은 자동 다운로드하지 않는다.

MLP·custom CNN은 pretrained 파일이 필요 없다. torchvision backbone에는 선택한 이름에 맞는 로컬 가중치를 등록한다. 다른 가중치를 사용하면 model.weights_path로 명시한다.

## CLI 학습

기본 선택은 MNIST·MLP다. 다음 조합을 사용할 수 있다.

```powershell
python -m src.classification.trainers.lightning_cli fit --data mnist --model mlp
python -m src.classification.trainers.lightning_cli fit --data mnist --model cnn --model.backbone custom
python -m src.classification.trainers.lightning_cli fit --data cifar10 --model cnn --model.backbone custom
python -m src.classification.trainers.lightning_cli fit --data cifar10 --model cnn --model.backbone resnet18
```

MNIST와 torchvision CNN을 선택하면 CLI가 기본 3채널 복제를 연결한다. MLP에는 backbone 옵션을 전달하지 않는다. 더 짧게 실행하려면 --trainer.max_epochs 1 --trainer.limit_train_batches 2 등을 추가한다.

배치 progress bar에는 이전 epoch의 valid 지표를 표시하지 않는다. 매 train epoch 종료 후 `Epoch ... | train_loss=... valid_loss=... valid_acc=... valid_f1=...` 한 줄을 출력한다. 검증이 없는 epoch에는 train_loss만 출력하며 지표는 계속 CSV와 best checkpoint 선택에 사용한다.

모듈 실행 외에 python src/classification/trainers/lightning_cli.py fit ... 및 trainers 디렉터리에서 직접 실행하는 방식도 지원한다. 출력 상대 경로는 실행 작업 폴더 기준이므로 재현 시 프로젝트 루트에서 실행한다.

## YAML과 인자 변경

다음 내용을 experiment.yaml로 저장할 수 있다.

```yaml
selection:
  data: cifar10
  model: cnn
model:
  backbone: resnet18
  learning_rate: 0.0005
data:
  batch_size: 32
trainer:
  max_epochs: 10
  logger:
    name: cifar10-resnet18-experiment
```

```powershell
python -m src.classification.trainers.lightning_cli fit --config experiment.yaml --trainer.max_epochs 5
python -m src.classification.trainers.lightning_cli fit --paths_file paths.toml --data.root E:/datasets/mnist
```

--data와 --model은 선택, --data.xxx·--model.xxx·--trainer.xxx는 생성자 인자 변경이다. 설정 저장 시 selection을 유지한다. logger와 callback은 클래스 경로 없이 인자만 지정한다. 이전 --data.dataset과 MLP 선택용 --model.backbone mlp는 사용하지 않는다.

## 평가·예측·재개

$run을 실제 생성된 실행 폴더로 바꾼다. Python 예제에서 생성한 config.yaml도 해당 예제의 data/model 선택값을 CLI에 명시하면 사용할 수 있다. 아래 예시는 CLI가 저장한 설정을 사용한다.

```powershell
$run = "outputs/classification-cifar10-cnn-resnet18/version_0"
python -m src.classification.trainers.lightning_cli validate --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
python -m src.classification.trainers.lightning_cli test --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
python -m src.classification.trainers.lightning_cli predict --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt" --trainer.limit_predict_batches 1
python -m src.classification.trainers.lightning_cli fit --config "$run/config.yaml" --ckpt_path "$run/checkpoints/last.ckpt" --trainer.max_epochs 10 --trainer.logger.name classification-resume
```

재개에서는 기존 로그와의 충돌을 피하도록 별도 logger 이름을 지정한다. fit은 테스트를 자동 실행하지 않으며 predict는 예측 파일을 자동 저장하지 않는다. Python API의 trainer.predict 결과는 배치별 확률·클래스 dict의 리스트다.

## Python 예제

| 예제 | 설정 차이 |
|---|---|
| [mnist-mlp.py](../../../examples/classification/mnist-mlp.py) | MNIST·MLP |
| [mnist-cnn-custom.py](../../../examples/classification/mnist-cnn-custom.py) | 1채널 custom CNN·전용 logger 이름 |
| [cifar10-cnn-custom.py](../../../examples/classification/cifar10-cnn-custom.py) | 3채널 custom CNN·전용 logger 이름 |
| [cifar10-cnn-resnet18.py](../../../examples/classification/cifar10-cnn-resnet18.py) | ResNet18·로컬 가중치·전용 logger 이름 |

```powershell
python examples/classification/mnist-mlp.py
```

예제의 main에서 YAML 병합 후 config 값을 직접 변경할 수 있다. 마지막 resolve_config_paths 호출 전에 backbone·가중치·logger 이름 등의 변경을 적용한다. 학습 후 best 테스트를 수행하며 실행 폴더에 test_metrics.json과 순수 CPU model.pt를 추가 저장한다.

## 독립 추론

다음은 Python 예제로 학습한 MNIST·MLP의 model.pt를 복원하는 예시다. 경로는 실제 실행 폴더로 바꾼다.

```python
import os

from src.classification.data.mnist.dataset import MNISTDataset, MNISTTransform
from src.classification.models.common.postprocess import ClassificationPostprocess
from src.classification.models.mlp.model import MLPModel
from src.inference.predictor import Predictor
from src.utils.config import load_yaml

run_dir = "outputs/classification-mnist-mlp/version_0"
config = load_yaml(os.path.join(run_dir, "config.yaml"))
model_config = config["model"]
model = MLPModel(
    image_size=model_config["image_size"], in_channels=model_config["in_channels"],
    hidden_dims=model_config["hidden_dims"], num_classes=model_config["num_classes"],
)
predictor = Predictor(model, postprocess=ClassificationPostprocess())
predictor.load_weights(os.path.join(run_dir, "model.pt"))
dataset = MNISTDataset(config["data"]["root"], split="test", transform=MNISTTransform(model_config["in_channels"]))
image, target = dataset[0]
outputs = predictor.predict_batch(image.unsqueeze(0))
print(outputs["predictions"], outputs["probabilities"])
```

CNN은 같은 backbone·in_channels·num_classes로 CNNModel을 생성한다. 이미 학습한 model.pt를 읽을 때는 weights_path=None으로 생성할 수 있다. 데이터에 같은 평가 Transform을 적용하고, 이미 변환한 배치에는 Predictor 전처리를 다시 적용하지 않는다.

## 문제 해결과 검증

채널·MLP 이미지 크기 불일치는 데이터·모델 설정을 함께 확인한다. pretrained 파일 누락은 paths.toml 등록 또는 명시적 경로를 확인한다. 기존 클래스 이름의 checkpoint와 노트북은 현행 코드와 호환된다고 가정하지 않는다.

검증 이력과 남은 확인 항목은 [PROGRESS.md](PROGRESS.md)에 둔다. 공통 Predictor·설정 병합 테스트는 다음 명령으로 선택할 수 있다. 이 명령을 문서 정리 과정에서 실행하지는 않았다.

```powershell
python -m pytest tests/test_examples.py -q -k "predictor_does_not_repeat_transform or config_merge_does_not_mutate_inputs"
```
