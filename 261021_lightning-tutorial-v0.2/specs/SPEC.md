# v0.2 공통 명세

[기획 의도](INTENT.md)와 [설계 결정](DECISIONS.md)을 기준으로 현재 공통 계약을 정의한다.

## 코드 배치

```text
src/
├── classification/
│   ├── configs/
│   ├── data/
│   ├── models/
│   └── trainers/
├── anomaly_detection/
│   ├── configs/
│   ├── data/
│   ├── models/
│   └── trainers/
├── inference/predictor.py
└── utils/
    ├── config.py
    └── io.py
```

| 위치 | 책임 |
|---|---|
| task `data/<dataset>/dataset.py` | Dataset와 해당 데이터의 Transform |
| task `data/<dataset>/lightning_data.py` | DataModule·분할·표준 DataLoader |
| task `data/common/` | 실제로 공유하는 폴더 읽기·변환·데이터 연결 |
| task `models/<model>/model.py` | 순수 모델 |
| task `models/<model>/lightning_model.py` | 설정값으로 구성요소를 생성하는 Wrapper |
| task `models/common/` | 실제로 공유하는 모델 구성요소 |
| task `trainers/lightning_trainer.py` | task Trainer·logger·callback·예제 저장 함수 |
| task `trainers/lightning_cli.py` | 선택 해석·기본 설정·native CLI 연결 |

내부 import는 `src.*`를 사용한다. 순수 파일과 패키지 초기화는 Lightning을 자동 import하지 않는다. 프로젝트 루트에 Python 진입점을 추가하지 않는다.

## 설정과 선택

기본 설정 파일은 다음 순서로 병합한다.

1. task `configs/default.yaml`: 실행 시드
2. `configs/data/<dataset>.yaml`: DataModule 인자
3. `configs/models/<model>.yaml`: Wrapper 인자와 필요한 데이터 기본값 변경
4. `configs/trainer.yaml`: Trainer·logger·callback 인자

CLI의 생성자 설정 우선순위는 위 기본 설정 → 선택 조합의 기본값 → 사용자 `--config` 전달 순서 → 명령행 인자다. Python 예제는 병합 후 직접 대입한 값을 사용한다.

CLI의 선택 우선순위는 기본 선택 → 사용자 YAML의 `selection` → 명령행 `--data`·`--model`이다. 선택값은 생성자 인자와 분리한다.

```yaml
selection:
  data: <dataset>
  model: <model>
data: {}
model: {}
trainer: {}
```

`--data.xxx`·`--model.xxx`·`--trainer.xxx`로 선택 클래스의 인자를 변경한다. 저장한 CLI 설정은 같은 task의 `--config`로 재사용한다.

## 로컬 경로

루트 `paths.toml`은 로컬 파일이며 Git에서 제외한다. 공유 형식은 [paths.example.toml](../../paths.example.toml)을 따른다.

`[datasets]`와 `[backbones]`는 모두 이름을 경로 문자열에 직접 연결한다. `[backbones.resnet18]`처럼 하위 테이블에 weights_path를 두는 이전 형식은 사용하지 않는다.

- `load_paths_config(path=None)`: 기본적으로 프로젝트 루트 TOML을 읽는다.
- `get_dataset_dir(name, paths)`: 데이터 디렉터리를 반환하고 존재를 확인한다.
- `get_backbone_dir(name, paths)`: 이름과 달리 가중치 파일 경로를 반환하고 존재를 확인한다.
- `resolve_config_paths(config, dataset_name, paths_file=None)`: 복사한 최종 설정에 실제 경로를 반영한다.

명시적 `data.root`가 이름 조회보다 우선한다. classification의 `model.weights_path`도 명시할 수 있다. TOML 내부 상대 경로는 TOML 위치, 명시적 상대 경로와 출력 경로는 실행 작업 폴더 기준이다. 사용하지 않는 자산의 파일 존재는 확인하지 않는다. 데이터 YAML의 `root: null`은 이름 조회를 뜻한다. 외부 backbone은 경로가 비어 있으면 이름으로 조회하고 custom CNN·MLP는 조회를 생략한다. anomaly 모델은 생성자에서 가중치 경로를 받지 않고 get_backbone_dir로 조회한다.

EfficientAD는 task의 resolve_anomaly_config_paths로 teacher 파일의 존재와 Imagenette 경로를 확인한다. 실제 teacher 로드는 Wrapper가 get_backbone_dir로 조회하여 수행한다. 상세 규칙은 [anomaly detection 명세](anomaly_detection/SPEC.md)를 따른다.

## Trainer와 실행

CSVLogger·ModelCheckpoint·MetricsPrinter는 task Trainer에서 항상 생성한다. YAML은 logger의 생성자 인자와 역할별 callback 인자만 받는다. `class_path`·`init_args` 및 비활성화용 false는 지원하지 않는다. 생략한 항목은 Python 기본값을 사용하며 알 수 없는 callback 이름은 오류다. CLI 설정 저장 callback은 기본 callback에 추가한다.

native `fit`·`validate`·`test`·`predict`를 사용한다. CLI fit은 테스트를 자동 실행하지 않는다. Python 예제는 시드 → 객체 생성 → 설정 저장 → fit → best test → 결과 저장 흐름을 사용한다. logger는 실행 폴더에 파일을 쓰기 전에 초기화한다.

| 실행 경로 | 산출물 |
|---|---|
| CLI | native 설정 저장, CSV, best/last checkpoint, 모델 hyperparameter |
| Python 예제 | 위 산출물과 테스트 JSON·best 순수 CPU state_dict |

학습 산출물은 기본적으로 `outputs/<logger name>/version_*/`에 둔다. native 평가·예측 명령이 예제 전용 JSON·순수 가중치·예측 파일을 자동 저장한다고 가정하지 않는다.

## 독립 추론

공통 Predictor는 task 클래스나 Lightning을 참조하지 않는다. 모델·전처리·후처리 callable과 device를 받는다.

- `load_weights(path)`: 순수 state_dict를 strict 복원하고 eval 상태로 전환한다.
- `predict(image)`: 선택적 전처리를 적용한 CHW 입력을 한 배치로 처리한다.
- `predict_batch(batch)`: 이미 전처리된 float NCHW 입력을 받고 전처리를 다시 적용하지 않는다.
- 모델 출력에 선택적 후처리를 적용하며 장치 이동·배치 결과 결합은 호출 측에서 수행한다.

복원 시 학습과 같은 구조·설정·전처리를 사용한다. task별 출력·checkpoint 기준은 [classification 명세](classification/SPEC.md)와 [anomaly detection 명세](anomaly_detection/SPEC.md)를 따른다.
