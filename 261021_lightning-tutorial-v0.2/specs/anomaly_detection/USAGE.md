# Anomaly detection 사용법

## VisA 데이터셋

`paths.toml`의 `[datasets]`에서 `visa = "E:/datasets/visa"`를 지정한다. 로컬 VisA의 `split_csv/1cls.csv`를 기준으로 각 범주의 정상 train 이미지와 정상·이상 test 이미지 및 이상 마스크를 읽는다. 기본 범주는 `candle`이다. 원본 test는 기존 데이터 모듈의 `valid_ratio`와 `seed`를 사용하여 검증·테스트로 나눈다. 따라서 별도 test 결과는 VisA 전체 공식 test 지표와 직접 비교할 수 없다.

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data visa --data.category candle --model stfpm --model.backbone resnet18
python -m src.anomaly_detection.trainers.lightning_cli fit --data visa --data.category candle --model efficientad --model.model_size small
```

EfficientAD를 선택하면 기존 설정과 동일하게 `batch_size=1`, `normalize=false`가 적용된다. `candle`, `capsules`, `cashew`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb1`~`pcb4`, `pipe_fryum`을 `--data.category`로 지정할 수 있다.

[프로젝트 안내](../../../README.md)에서 환경과 로컬 경로를 준비한다. 이하 python은 필요한 패키지가 설치된 Python 3.11 실행 파일이며 명령은 프로젝트 루트에서 실행한다. 공통 규칙은 [공통 명세](../SPEC.md), 모델 계약은 [SPEC.md](SPEC.md)를 따른다.

## 데이터·가중치 준비

[paths.example.toml](../../../paths.example.toml)을 paths.toml로 복사하고 자신의 경로를 지정한다.

```toml
[datasets]
mvtec = "E:/datasets/mvtec"
btad = "E:/datasets/btad"
imagenette = "E:/datasets/imagenette2"

[backbones]
resnet18 = "E:/backbones/resnet18-f37072fd.pth"
efficientad_small = "E:/backbones/efficientad_pretrained_weights/pretrained_teacher_small.pth"
efficientad_medium = "E:/backbones/efficientad_pretrained_weights/pretrained_teacher_medium.pth"
```

root 아래 category/train/good·category/test/<defect>·category/ground_truth/<defect> 구조가 필요하다. bottle 외에 grid 등 로컬 범주를 category로 선택할 수 있다. 두 라벨을 포함하는 valid/test 분할에 필요한 평가 샘플을 준비한다. 데이터와 가중치는 다운로드하지 않는다.

STFPM은 timm이 필요하다. teacher 가중치는 backbone 이름으로 `paths.toml`의 `[backbones]`를 조회한다. 순수 모델과 Wrapper 생성자에는 `weights_path`를 전달하지 않는다.

BTAD의 root 아래에는 01·02·03 범주별 train/ok·test/ok·test/ko·ground_truth/ko가 있어야 한다. 범주명은 문자열로 지정하며 YAML에서는 "01"처럼 따옴표로 감싼다. BMP·PNG 이미지와 마스크를 지원한다.

EfficientAD는 ResNet 가중치 대신 PDN teacher 파일과 Imagenette 루트가 필요하다. `get_dataset_dir("imagenette", paths)`로 `E:/datasets/imagenette2`를 얻고, 학습에는 그 아래 train/<class> 이미지만 사용한다. val 이미지는 penalty에 포함하지 않는다. 둘 다 로컬 자산만 사용하며 자동 다운로드하지 않는다. `[backbones.resnet18]` 하위 테이블 대신 위처럼 `[backbones]`의 직접 문자열 매핑을 사용한다.

## CLI 학습

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data mvtec --data.category bottle --model stfpm --model.backbone resnet18
python -m src.anomaly_detection.trainers.lightning_cli fit --data mvtec --data.category grid --model stfpm --model.backbone resnet18
```

기본값은 MVTec·bottle·STFPM·ResNet18이다. 기본 logger 이름에 category와 backbone이 포함된다. 모듈 실행 외에 python src/anomaly_detection/trainers/lightning_cli.py fit ... 형태의 직접 실행도 지원한다.

BTAD·STFPM:

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data btad --data.category 01 --model stfpm --model.backbone resnet18
```

BTAD·EfficientAD와 MVTec·EfficientAD:

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data btad --data.category 01 --model efficientad --model.model_size small
python -m src.anomaly_detection.trainers.lightning_cli fit --data mvtec --data.category bottle --model efficientad --model.model_size small
```

EfficientAD를 선택하면 모델 YAML에서 batch_size=1·normalize=false가 적용된다. 현재 256×256·단일 장치·gradient accumulation 1을 지원한다. model_size는 small 또는 medium이고, 해당 이름의 teacher 가중치를 사용한다. 기본 logger는 예를 들어 anomaly-btad-01-efficientad-small이다. STFPM의 backbone·layers·tiler 인자를 EfficientAD에 전달하지 않는다.

EfficientAD의 연결 확인용 짧은 학습과 긴 학습 설정:

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data btad --data.category 01 --model efficientad --trainer.max_epochs 1 --trainer.limit_train_batches 2
python -m src.anomaly_detection.trainers.lightning_cli fit --data btad --data.category 01 --model efficientad --trainer.max_epochs -1 --trainer.max_steps 70000
```

짧은 학습에서도 teacher 통계는 정상 train 전체, quantile 보정은 정상 valid 전체를 읽는다. 기본값은 task 공통 10 epoch이며 긴 학습의 성능을 보장하지 않는다. fit은 보정된 valid 지표를 기록하고 best checkpoint에 통계·quantile을 함께 저장한다.

배치 progress bar에는 이전 epoch의 valid AUROC를 표시하지 않는다. 매 train epoch 종료 후 `Epoch ... | train_loss=... valid_image_auroc=... valid_pixel_auroc=...` 한 줄을 출력한다. 지표는 계속 CSV와 best checkpoint 선택에 사용한다.

EfficientAD의 `train_st`, `train_ae`, `train_stae`, `train_loss`는 CSV에 기록하되 progress bar에는 표시하지 않는다. `train_loss`는 epoch 종료 출력에 유지한다.

TOML 대신 학습 자산을 직접 지정할 수도 있다.

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data btad --data.root E:/datasets/btad --model efficientad --model.imagenet_dir E:/datasets/imagenette2
```

짧은 학습은 다음처럼 제한한다. 검증은 AUROC에 두 클래스가 필요하므로 전체 valid를 사용한다.

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --data mvtec --data.category bottle --model stfpm --data.batch_size 2 --trainer.max_epochs 1 --trainer.limit_train_batches 2
```

고정된 teacher 때문에 학습 시작 시 eval mode module 경고가 나타날 수 있다. teacher의 BatchNorm 상태를 train으로 변경하지 않는다.

## YAML과 설정 변경

다음 내용을 experiment.yaml로 저장할 수 있다.

```yaml
selection:
  data: mvtec
  model: stfpm
data:
  category: grid
  batch_size: 4
model:
  backbone: resnet18
  layers: [layer1, layer2, layer3]
trainer:
  max_epochs: 10
```

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --config experiment.yaml --data.category bottle
python -m src.anomaly_detection.trainers.lightning_cli fit --paths_file paths.toml --data.root E:/datasets/mvtec
```

선택은 --data·--model, 인자 변경은 --data.xxx·--model.xxx·--trainer.xxx를 사용한다. 사용자 YAML·명령행의 최종 category/backbone으로 기본 logger 이름을 정하고, 명시적인 trainer.logger.name을 우선한다.

EfficientAD에서는 backbone 대신 model_size를 logger 이름에 사용한다. 모델 YAML이 데이터 기본값도 변경하므로 사용자 설정에서 normalize=true나 batch_size>1로 덮어쓰면 오류다.

## 평가·예측·재개

$run은 실제 실행 폴더로 바꾼다. best는 valid_image_auroc 최대값 기준이며 마지막 epoch나 pixel AUROC 최고 epoch와 다를 수 있다.

```powershell
$run = "outputs/anomaly-mvtec-bottle-stfpm-resnet18/version_0"
python -m src.anomaly_detection.trainers.lightning_cli validate --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
python -m src.anomaly_detection.trainers.lightning_cli test --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
python -m src.anomaly_detection.trainers.lightning_cli predict --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt" --trainer.limit_predict_batches 1
python -m src.anomaly_detection.trainers.lightning_cli fit --config "$run/config.yaml" --ckpt_path "$run/checkpoints/last.ckpt" --trainer.max_epochs 20 --trainer.logger.name anomaly-resume
```

CLI fit은 학습만 수행한다. test·predict는 예제 전용 JSON·model.pt·예측 파일을 자동 저장하지 않는다. Python API의 trainer.predict 결과는 배치별 InferenceBatch의 리스트이며 텐서는 해당 장치에 남는다.

BTAD·EfficientAD도 같은 명령을 사용한다. 저장된 selection과 설정을 그대로 읽으므로 --data·--model을 반복할 필요가 없다.

```powershell
$run = "outputs/anomaly-btad-01-efficientad-small/version_0"
python -m src.anomaly_detection.trainers.lightning_cli validate --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
python -m src.anomaly_detection.trainers.lightning_cli test --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
python -m src.anomaly_detection.trainers.lightning_cli predict --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt" --trainer.limit_predict_batches 1
```

EfficientAD standalone 평가는 checkpoint의 보정값을 유지한다. checkpoint 없이 새 모델로 평가하거나 test에서 quantile을 다시 계산하지 않는다. 평가·독립 추론에는 Imagenette와 원본 teacher 파일이 필요하지 않다. 학습 재개 시에는 penalty용 Imagenette가 필요하다.

## Python 예제

[bottle 예제](../../../examples/anomaly_detection/mvtec-stfpm-bottle.py)는 병합 후 config["data"]["category"] = "bottle"로 범주를 명시한다.

```powershell
python examples/anomaly_detection/mvtec-stfpm-bottle.py
```

기본 10 epoch 학습 후 best checkpoint를 평가하고 config.yaml·CSV·checkpoint·test_metrics.json·순수 CPU model.pt를 저장한다. 변경할 값은 main의 YAML 병합 뒤에 대입하고 로컬 경로 해석 전에 반영한다. category를 바꾸는 별도 예제를 만들 때는 logger 이름도 해당 범주에 맞춰 명시한다.

추가 예제는 데이터·모델 선택과 category를 파일에 명시한다.

| 예제 | 조합 |
|---|---|
| [btad-stfpm-01.py](../../../examples/anomaly_detection/btad-stfpm-01.py) | BTAD 01·STFPM ResNet18 |
| [mvtec-efficientad-bottle.py](../../../examples/anomaly_detection/mvtec-efficientad-bottle.py) | MVTec bottle·EfficientAD small |
| [btad-efficientad-01.py](../../../examples/anomaly_detection/btad-efficientad-01.py) | BTAD 01·EfficientAD small |

```powershell
python examples/anomaly_detection/btad-stfpm-01.py
python examples/anomaly_detection/mvtec-efficientad-bottle.py
python examples/anomaly_detection/btad-efficientad-01.py
```

## Tiler 사용

STFPM 전용이다. EfficientAD에는 적용하지 않는다. 모델 생성자에는 tiler 인자를 두지 않는다. CLI의 최상위 설정으로 연결하며 기본값은 null이다. 다음 내용을 tiling.yaml로 저장한다.

```yaml
selection:
  data: mvtec
  model: stfpm
tiler:
  tile_size: 128
  stride: 128
  remove_border_count: 0
  mode: padding
```

```powershell
python -m src.anomaly_detection.trainers.lightning_cli fit --config tiling.yaml
python -m src.anomaly_detection.trainers.lightning_cli fit --tiler '{tile_size: 128, stride: 128, mode: padding}'
```

Python 예제에서는 모델 생성 후 `model.model.tiler = Tiler(tile_size=128, stride=128)`로 활성화한다. 순수 STFPMModel에서도 생성 후 `model.tiler`에 Tiler 객체를 할당한다.

tile_size·stride는 정수 또는 [높이,너비]다. stride 생략 시 tile_size를 사용한다. 타일은 전처리된 입력보다 클 수 없고 stride는 타일 이하여야 한다. border를 제거한 뒤 가장 작은 특징 타일의 내부가 남아야 한다. mode는 padding 또는 interpolation이며 interpolation은 크기 조정으로 픽셀을 바꿀 수 있다. 자세한 병합 계약은 [SPEC.md](SPEC.md)를 따른다.

## 독립 추론

Python 예제로 저장한 config.yaml과 model.pt를 사용한다. 경로는 실제 결과로 바꾼다.

```python
import os

from src.anomaly_detection.data.mvtec.dataset import MVTecDataset, MVTecTransform
from src.anomaly_detection.models.stfpm.model import STFPMModel
from src.inference.predictor import Predictor
from src.utils.config import load_yaml

run_dir = "outputs/anomaly-mvtec-bottle-stfpm-resnet18/version_0"
config = load_yaml(os.path.join(run_dir, "config.yaml"))
model_config = config["model"]
model = STFPMModel(
    backbone=model_config["backbone"], layers=model_config["layers"],
)
predictor = Predictor(model)
predictor.load_weights(os.path.join(run_dir, "model.pt"))
dataset = MVTecDataset(
    config["data"]["root"], train=False, category=config["data"]["category"],
    transform=MVTecTransform(config["data"]["image_size"]),
)
image, target = dataset[0]
outputs = predictor.predict_batch(image.unsqueeze(0))
print(outputs.pred_score, outputs.anomaly_map.shape)
```

Dataset에서 전처리한 배치는 predict_batch에 전달해 중복 적용하지 않는다. 순수 가중치만으로는 tiler 설정을 알 수 없으므로 필요한 경우 같은 설정의 Tiler 객체를 생성 후 연결한다. 기존 torchvision 기반 checkpoint의 timm 키 호환성은 보장하지 않는다.

EfficientAD는 전체 model.pt에서 teacher·student·autoencoder·통계·quantile을 복원한다. 원본 teacher 파일을 다시 로드할 필요가 없다.

```python
import os

from src.anomaly_detection.data.btad.dataset import BTADDataset, BTADTransform
from src.anomaly_detection.models.efficientad.model import EfficientAdModel
from src.inference.predictor import Predictor
from src.utils.config import load_yaml

run_dir = "outputs/anomaly-btad-01-efficientad-small/version_0"
config = load_yaml(os.path.join(run_dir, "config.yaml"))
values = config["model"]
model = EfficientAdModel(
    model_size=values["model_size"], teacher_out_channels=values["teacher_out_channels"],
    padding=values["padding"], pad_maps=values["pad_maps"],
)
predictor = Predictor(model)
predictor.load_weights(os.path.join(run_dir, "model.pt"))
dataset = BTADDataset(
    config["data"]["root"], train=False, category=config["data"]["category"],
    transform=BTADTransform(config["data"]["image_size"], normalize=False),
)
image, target = dataset[0]
outputs = predictor.predict_batch(image.unsqueeze(0))
print(outputs.pred_score, outputs.anomaly_map.shape)
```

EfficientAD 입력에 STFPM용 ImageNet 정규화 텐서를 재사용하지 않는다. 출력은 확률이 아니며 음수도 포함할 수 있는 이상 점수다.

## 사용자 검증 명령

수식·teacher 고정/student 갱신·MVTec 마스크:

```powershell
python -m pytest tests/test_examples.py -q -k "stfpm_reference_equations or teacher_frozen_student_updated or mvtec_folders_masks_and_rejection"
```

Python 예제의 model.pt를 만든 후 checkpoint 일치·Lightning import 차단 추론:

```powershell
$env:STFPM_RUN_DIR = "outputs/anomaly-mvtec-bottle-stfpm-resnet18/version_0"
python -m pytest tests/test_examples.py -q -k "stfpm or plain_import_and_inference_without_lightning"
```

기존 테스트의 실행 폴더 복원 검증은 기본 bottle·ResNet18·타일링 비활성 결과를 사용한다. 다른 폴더는 환경 변수로 지정한다. Tiler 자체와 활성 모델·설정·checkpoint 복원은 별도로 확인한다.

```powershell
python -m pytest tests/test_tiler.py -q -k "not stfpm"
python -m pytest tests/test_tiler.py -q -k stfpm
```

Tiler 테스트는 중첩·비중첩 복원, stride 생략, padding/interpolation, border, gradient, 잘못된 인자, 활성 STFPM 출력 크기·복원을 포함한다. 실행 여부와 남은 확인은 [PROGRESS.md](PROGRESS.md)에 기록한다.
