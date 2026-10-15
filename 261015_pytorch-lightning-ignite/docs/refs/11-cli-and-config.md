> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# LightningCLI와 Ignite의 config 기반 실행

## 확정된 요구

Lightning은 실제 LightningCLI 기능을 그대로 사용한다. Ignite는 같은 명령·설정 파일·
명령줄 덮어쓰기와 설정 확인 방식으로 동작하게 구현한다. Python 공개 API의
fit·validate·test·predict와 native 실행 유지 요구는 [09](09-client-api-and-examples.md)를 따른다.

Lightning native 우선은 CLI뿐 아니라 Wrapper·학습·검증·평가·예측·Trainer·DataModule
전체에 적용된다. CLI는 이 native 객체를 생성하고 실행하는 진입점이며, Ignite는 같은
주요 API와 config 사용 방식으로 Engine 기반 실행을 제공한다.

## 실행 구조

v0.1은 실제 LightningCLI 경로를 구현·검증한다. Ignite CLI와 두 백엔드 선택 기능은
Lightning 검증·테스트 완료 후 v0.2 또는 그 이후 구현 대상으로 둔다.
아래 양쪽 설정 대응표는 최종 방향이며, v0.1에서 Ignite 설정 실행을 요구하지 않는다.

| 경로 | CLI 역할 | 실제 실행 |
| --- | --- | --- |
| Lightning | 공식 LightningCLI의 파싱·객체 생성·명령 실행 | native Trainer·Task·DataModule |
| Ignite | 같은 사용 방식을 제공하는 프로젝트 CLI | 프로젝트 Ignite Trainer·Engine |
| 독립 Predictor | 학습 CLI와 분리된 Python 추론 API | Lightning·Ignite 없이 실행 |

Lightning에서는 LightningModule과 LightningDataModule 클래스를 CLI에 등록한다.
기본 실행 모드는 선택한 Trainer 명령까지 실행하므로 별도로 fit를 다시 호출하지 않는다.
[공식 Intermediate 안내](https://github.com/Lightning-AI/pytorch-lightning/blob/master/docs/source-pytorch/cli/lightning_cli_intermediate.rst)

Lightning 쪽 진입점은 다음처럼 구성한다. Task와 DataModule은 구현 예정 클래스이며,
각각 native LightningModule·LightningDataModule을 기반으로 작성한다.

```python
# src/backends/lightning/cli.py: Lightning 경로 예시
from lightning.pytorch.cli import LightningCLI
from src.backends.lightning.tasks.classification import ClassificationTask
from src.backends.lightning.datamodule import ImageDataModule

def main():
    LightningCLI(ClassificationTask, ImageDataModule)

if __name__ == "__main__":
    main()
```

프로젝트 루트 main.py가 선택한 백엔드 CLI의 main을 호출하는 진입점을 유지한다.
src 아래에는 프로젝트명 패키지를 추가하지 않으며 src.backends 경로로 import한다.
위 모듈을 파일 경로로 직접 실행하는 명령을 기본 사용법으로 삼지 않는다.
상세 배치는 [전체 구조](01-architecture.md#예상-프로젝트-폴더-구조)를 따른다.

CLI 전용 대체 Trainer를 Lightning 쪽에 필수로 두지 않는다. Ignite 쪽은 프로젝트 CLI가
설정에서 Ignite Task·DataModule·Trainer를 생성하고 같은 명령을 Engine 실행에 연결한다.

IgniteTrainer의 메서드 이름이 같다고 LightningCLI의 trainer_class에 바로 넣을 수 있다고
가정하지 않는다. LightningCLI는 Lightning 객체를 생성·실행하는 도구다. Ignite용 파서와
객체 생성 연결은 별도로 구현하며, jsonargparse를 활용하는 것은 검토 후보다.

## 명령과 설정 파일

아래는 목표 사용 형태다. main.py와 config 경로는 예시이며 아직 구현 파일은 없다.
백엔드 선택은 진입점·실행 환경에서 이루어졌다고 가정하고 문법은 별도로 결정한다.

```powershell
python main.py fit --config configs/classification.yaml
python main.py validate --config configs/classification.yaml --ckpt_path model.ckpt
python main.py test --config configs/classification.yaml --ckpt_path model.ckpt
python main.py predict --config configs/classification.yaml --ckpt_path model.ckpt
```

YAML(.yaml/.yml)을 기본으로 사용하고 JSON(.json) 입력도 지원하는 방향으로 맞춘다.
config 뒤에 지정한 --xxx 값이 해당 설정을 덮어쓰도록 한다.
[공식 config 안내](https://github.com/Lightning-AI/pytorch-lightning/blob/master/docs/source-pytorch/cli/lightning_cli_advanced.rst)

```powershell
python main.py fit --config configs/classification.yaml --model.learning_rate 0.01 --trainer.max_epochs 20
python main.py fit --help
python main.py fit --config configs/classification.yaml --model.learning_rate 0.01 --print_config
```

--print_config는 기본값과 입력 설정·덮어쓰기를 반영한 설정을 출력하고 학습 등을 실행하지
않는다. 실제 적용 설정의 저장도 제공한다. 저장 위치·덮어쓰기 방지·실험 식별 정책은
미정이며 Lightning의 SaveConfigCallback 동작을 기준으로 Ignite 대응을 검토한다.
[공식 설정 출력·저장 안내](https://github.com/Lightning-AI/pytorch-lightning/blob/master/docs/source-pytorch/cli/lightning_cli_advanced.rst)

## 기본 섹션과 연결 대상

| 설정 | Lightning 대상 | Ignite 대응 방향 |
| --- | --- | --- |
| trainer | native Trainer 생성 인자 | 프로젝트 Trainer 인자와 Engine 설정 |
| model | LightningModule인 Task Wrapper | 같은 역할의 Ignite Task |
| data | LightningDataModule | Ignite용 DataModule |
| optimizer | Optimizer 클래스·인자 | 같은 PyTorch Optimizer 구성 |
| lr_scheduler | Scheduler 클래스·인자 | 같은 Scheduler 구성과 실행 주기 연결 |
| seed_everything | 객체 생성 전 시드 설정 | 객체 생성 전에 같은 목적의 시드 설정 |
| ckpt_path | 명령별 체크포인트 입력 | 해당 Ignite 저장 형식에 맞는 복원 |

optimizer·lr_scheduler는 LightningCLI 자동 구성 또는 사용자 등록 방식에 따라 달라진다.
Task의 configure_optimizers와 CLI 자동 구성이 충돌하지 않도록 역할을 하나로 정해야 한다.
GAN의 복수 Optimizer는 별도 설정·최적화 계약을 검토하며 단일 Optimizer 예제를 강제하지 않는다.
[LightningCLI 구현](https://github.com/Lightning-AI/pytorch-lightning/blob/master/src/lightning/pytorch/cli.py)

Loss·Metric·후처리는 model 아래의 Task 생성자 인자, transform·target_transform은
data 아래의 Dataset 구성에 연결한다. 실제 키와 중첩은 생성자 정의를 따른다. 이들을
자동으로 제공되는 최상위 섹션이라고 가정하지 않는다.

사용자 정의 preprocessing 함수·Preprocessor도 선택적으로 연결할 수 있다. Dataset의
transform으로 전달하거나 추가 전처리용 생성자 인자를 정의하여 config에서 구성한다.
사용자 정의 클래스는 타입이 지정된 인자와 class_path/init_args 연결을 검토하고,
임의 함수의 구성 방식과 인자 이름은 미정이다. 고정 최상위 preprocess 섹션이 자동으로
존재한다고 가정하지 않으며, 미지정 시 기본 Dataset 변환 경로를 유지한다.

## 고정 클래스를 등록한 config 예

다음은 Task가 out_dim·learning_rate, DataModule이 data_dir·batch_size를 받는 경우다.
Task가 직접 Optimizer를 구성한다고 가정하며 CLI의 별도 optimizer 설정과 중복 사용하지 않는다.

```yaml
seed_everything: 42
trainer:
  max_epochs: 10
  logger: false
model:
  out_dim: 2
  learning_rate: 0.1
data:
  data_dir: "./data"
  batch_size: 32
ckpt_path: null
```

```powershell
python main.py fit --config configs/classification.yaml --model.learning_rate 0.01 --trainer.max_epochs 20
```

이 명령의 최종 학습률은 0.01, max_epochs는 20이며 out_dim과 데이터 설정은 파일 값을
유지한다. 앞서 논의한 긴 CLI 명령의 인자도 같은 방식으로 config에 옮길 수 있다.
홈 경로 문자열을 받는 사용자 정의 DataModule은 expanduser 처리를 확인해야 한다.

## 클래스 선택과 기존 순수 모델

클래스 선택 모드에서는 class_path와 init_args를 사용한다. 바깥 model은 Task Wrapper,
그 생성자 아래 model 또는 encoder·decoder 등은 기존 순수 PyTorch 모델 구성요소다.
아래 경로와 인자는 구조를 설명하는 예시이며 실제 구현은 없다. src 구조 변경은
class_path에 반영하지만 main.py의 서브커맨드와 config 덮어쓰기 방식은 유지한다.

```yaml
model:
  class_path: src.backends.lightning.tasks.classification.ClassificationTask
  init_args:
    model:
      class_path: examples.models.my_cnn.MyCNN
      init_args:
        out_dim: 2
    loss_fn:
      class_path: torch.nn.CrossEntropyLoss
data:
  class_path: src.backends.lightning.datamodule.ImageDataModule
  init_args:
    data_dir: "./data"
    batch_size: 32
```

고정 클래스 예제와 클래스 선택 예제의 중첩을 임의로 섞지 않는다. CLI 노출 경로는 등록
방식과 생성자 타입에 따라 달라지므로 --help와 --print_config로 확인한다.
[공식 클래스 구성 안내](https://github.com/Lightning-AI/pytorch-lightning/blob/master/docs/source-pytorch/cli/lightning_cli_advanced.rst)

## Ignite 호환 범위와 오류 처리

같은 섹션·공통 옵션은 같은 목적과 우선순위로 처리한다. 클래스 경로는 백엔드별 Task와
DataModule을 가리킬 수 있으므로 설정 파일의 모든 문자열이 동일해야 한다는 뜻은 아니다.
Lightning Callback을 Ignite Handler로 자동 변환하거나 Lightning 체크포인트를 Ignite
학습 재개 파일로 그대로 읽는 기능은 확정하지 않았다.

지원하지 않는 키·클래스·옵션은 실행 전에 명확히 보고하는 방향으로 한다. 파싱할 수
있다는 이유만으로 실행 의미까지 호환된다고 취급하지 않는다. 백엔드 전용 Strategy·Plugin,
Logger·Callback 옵션은 지원표를 정하고 공통 옵션과 구분해야 한다.

## 미정

지원 라이브러리 버전, 진입점과 백엔드 선택 문법, Ignite 파서, 공통 옵션 지원표,
클래스 등록·생성 방식, Optimizer 구성 주체, 복수 Optimizer 설정, config 저장 정책과
체크포인트 복원 범위는 미정이다. CLI와 독립 Predictor 사이의 추가 CLI는 별도 요구가 없다.
독립 추론 결과물 설정은 [08](08-weights-and-checkpoints.md), 검증은 [10](10-validation.md)을 따른다.
