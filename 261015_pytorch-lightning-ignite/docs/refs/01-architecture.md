> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# 전체 구조와 책임 경계

## 확정된 요구

Lightning을 최대한 native 그대로 사용하고 Ignite가 같은 공개 API로 동작하게 하는 것이
프로젝트의 큰 목적 중 하나다. 공통 API의 기준은 Lightning이며, 양쪽을 위해 Lightning을
별도 최소 기능 계층으로 대체하거나 축소하지 않는다.

적용 범위는 Wrapper·학습·평가·추론·Trainer·데이터·CLI 전반이다. Lightning Wrapper는
LightningModule로 작성하고 실행은 native Trainer에 맡긴다. Ignite Wrapper·Trainer는
같은 주요 Hook과 공개 API를 제공하며, 내부 반복 실행은 Engine에 맡긴다.

[INTENT](../INTENT.md)와 [BRIEF](../BRIEF.md)를 기준으로 기존 순수 PyTorch 모델을
수정하지 않고 Task별 학습·평가·추론에 사용한다. Lightning·Ignite의 native 평가·예측을
유지하고 별도의 순수 PyTorch Predictor를 제공한다. DataModule을 포함하며 기존
transform과 백엔드에 독립적인 후처리를 재사용한다.

공개 호출은 Lightning 형태의 fit·validate·test·predict로 맞춘다. Ignite용 프로젝트
Trainer는 내부에서 Factory·Engine을 실행한다. 주요 Task Hook, DataModule의 단계별
Loader와 평가·예측 반환 계약을 공통화하며, 백엔드별 확장 기능은 유지한다.

명령줄에서는 LightningCLI를 그대로 사용하고 Ignite는 같은 config·서브커맨드·덮어쓰기
방식을 구현한다. CLI는 객체 구성과 명령 전달을 맡고 실제 학습은 각 native 실행에 연결한다.
자세한 설정 계약은 [11](11-cli-and-config.md)을 따른다.

## 검토 제안: 책임 분리

### 구현 순서와 버전 경계

v0.1에서는 Lightning 기준 구현과 검증·테스트를 먼저 완료한다. 그 결과로 확인한
Wrapper Hook·Trainer·DataModule·CLI·출력 계약을 기준으로 v0.2 또는 그 이후에
Ignite를 Engine 기반으로 구현한다. Ignite의 정확한 착수 버전은 아직 정하지 않았다.
두 백엔드를 동시에 구현하지 않는다.

아래의 양쪽 실행 경로와 전체 폴더 구조는 최종 지원 방향을 함께 보여준다. v0.1에는
Ignite 코드·설정·테스트를 생성하거나 구현하지 않으며, 이에 대한 문서는 후속 검토로 보관한다.

| 구성요소 | 담당 | 담당하지 않는 것 |
| --- | --- | --- |
| Model | 기존 forward 연산 | Trainer·Engine, 데이터 로딩 |
| Dataset·transform | 샘플 로딩, 입력·타깃 변환 | 출력 후처리, 학습 반복 |
| DataModule | 단계별 Dataset/DataLoader 제공과 수명 관리 | 모델 Loss와 후처리 정의 |
| Task Wrapper | 구성요소 조합, 배치 해석, Loss·Metric 연결 | 원천 데이터 구현 |
| Postprocess | 원시 출력의 의미를 실제 예측값으로 변환 | 학습 반복·Optimizer 실행 |
| Native 실행 계층 | 학습·평가·예측 반복과 백엔드 기능 | 공통 변환의 재구현 |
| 공개 Trainer API | 같은 호출 형태를 각 native 실행에 연결 | Lightning 전체 기능의 호환 구현 |
| CLI·config | 설정 해석, 객체 생성, 명령 전달과 적용 설정 기록 | 독립 추론에 학습 백엔드 의존성 추가 |
| 독립 Predictor | 가중치 복원 후 입력 준비·모델 실행·후처리 | 학습 재개, native 실행 대체 |

이 표는 책임 후보이며 필수 클래스나 패키지 개수를 정하지 않는다.

## 두 실행 경로

```text
Dataset → transform → DataLoader/DataModule
                          ↓
              Lightning / Ignite native 실행
                          ↓
                     Model 원시 출력
                    ↙             ↘
             Loss·Metric       공통 후처리 → 예측

원시 입력 → 같은 평가용 transform ─┐
이미 변환된 배치 ─────────────────┤
                               ↓
                      독립 Predictor → Model → 같은 후처리
```

독립 Predictor가 의존하는 모델·변환·후처리·복원 코드는 Lightning·Ignite를 import하지
않는 방향을 제안한다. 패키지 초기화가 백엔드를 자동 import하는 경우도 피해야 한다.
transform은 적용된 위치를 구분하고 같은 입력에 두 번 적용하지 않는다.

## 공개 API와 내부 실행

사용자는 양쪽 Trainer에 같은 형태로 Task와 DataModule을 전달한다. Lightning은 native
Trainer에 연결하고, Ignite는 프로젝트 Trainer가 Engine 실행과 수명 관리를 연결한다.
Ignite 예측 Engine은 독립 PyTorch Predictor와 구분한다. 사용자에게 Engine.run 호출을
필수로 노출하지 않으며 native 객체를 직접 확장하는 경로는 따로 검토한다.

API 형태와 주요 Hook 공통화가 내부 상속 구조나 모든 백엔드 옵션의 호환을 의미하지는 않는다.
반환 계약과 Hook 의미는 [09](09-client-api-and-examples.md)에서 구체화한다.

Lightning의 native 반환과 설정을 기준으로 Ignite의 대응을 설계한다. 차이가 생기면
Ignite 연결 계층과 지원표에서 다루고, 이를 이유로 Lightning의 기본 동작을 바꾸지 않는다.

## 기존 후보와 현재 방향

| 기존 후보 | 장점 | 현재 취급 |
| --- | --- | --- |
| 공통 PyTorch Task + 백엔드 Adapter | 모델 조합·Loss 코드 재사용 | Lightning 앞에 필수 중간 계층으로 도입하지 않음 |
| 백엔드별 Native Task Wrapper | native 기능에 직접 연결 | Lightning native를 기준으로 Ignite가 공개 API를 맞추는 방향 채택 |

후보는 기존 [design-1](drafts/design-1.md)과 [design-3](drafts/design-3.md)에서 서로
다르게 제안되었다. 후속 사용자 요청으로 native Wrapper와 native 실행을 기준으로 하는
방향을 정했다. 세부 상속과 공통 코드의 재사용은 미정이며, 모델 조합·Loss 계산·변환·
후처리 같은 순수 코드의 공유는 가능하다. 독립 Predictor를 학습 Wrapper 복원에 종속시키지 않는다.

## 예상 프로젝트 폴더 구조

다음은 프로젝트 초기화 이후 구현을 진행할 때의 전체 구조 제안이다. 현재 기획 폴더에
아래 코드·config·테스트 파일을 생성한 것은 아니다. src 바로 아래에 기능별 모듈을 두고
프로젝트명 패키지를 중간에 추가하지 않는다. 구체적인 파일명은 후보이며,
여덟 Task는 전체 지원 방향을 보여준다. 첫 버전의 구현 범위를 확정하는 목록은 아니다.
폴더와 파일은 실제 필요 시점에 만들고 빈 구조를 미리 생성하지 않는다.

```text
pytorch-lightning-ignite/
├── README.md
├── pyproject.toml
├── .gitignore
├── main.py                           # 백엔드별 CLI 진입 연결 후보
├── docs/
│   ├── current/
│   │   ├── INTENT.md                  # 프로젝트 SSOT, 버전 간 유지
│   │   ├── BRIEF.md
│   │   ├── DECISIONS.md               # 설계 확정 후 작성
│   │   ├── PLAN.md                    # 구현 범위·Phase 확정 후 작성
│   │   ├── SPEC.md                    # 필요한 경우
│   │   └── PROGRESS.md                # 구현 시작 후 작성
│   ├── refs/                         # 현재 refs/ 문서와 drafts/ 보관
│   └── history/                      # 버전 마감 후 생성, INTENT 제외
├── configs/
│   ├── shared/                       # 양쪽에서 의미가 같은 설정 조각
│   ├── lightning/                    # native 클래스·옵션을 사용하는 설정
│   │   ├── classification.yaml
│   │   └── regression.yaml
│   └── ignite/                       # Ignite 대응 클래스·옵션 설정
│       ├── classification.yaml
│       └── regression.yaml
├── src/
│   ├── __init__.py                   # src를 import 기준으로 사용, 백엔드 자동 import 없음
│   ├── core/                         # 순수 PyTorch 공통 코드
│   │   ├── batch.py                   # 입력·타깃·메타데이터 해석 보조
│   │   ├── outputs.py                 # Task별 출력 계약 보조
│   │   └── composition.py             # AE/VAE 등 추론에도 필요한 모델 조합
│   ├── transforms/                   # 기존 transform 재사용, 선택적 사용자 정의 전처리
│   ├── postprocessing/               # native 예측·독립 Predictor가 공유
│   │   ├── classification.py
│   │   ├── regression.py
│   │   ├── segmentation.py
│   │   ├── detection.py
│   │   ├── anomaly.py
│   │   └── image.py                   # 복원·생성 이미지 출력 변환
│   ├── artifacts/                    # 추론용 결과물 저장·복원
│   │   ├── weights.py
│   │   └── metadata.py
│   ├── inference/
│   │   └── predictor.py               # 백엔드 없는 독립 추론
│   └── backends/
│       ├── lightning/
│       │   ├── cli.py                 # 실제 LightningCLI 구성
│       │   ├── datamodule.py          # native LightningDataModule 기반
│       │   └── tasks/                 # native LightningModule 기반 Wrapper
│       │       ├── base.py
│       │       ├── classification.py
│       │       ├── regression.py
│       │       ├── segmentation.py
│       │       ├── detection.py
│       │       ├── anomaly.py
│       │       ├── autoencoder.py
│       │       ├── vae.py
│       │       └── gan.py
│       └── ignite/
│           ├── cli.py                 # 같은 CLI·config 사용 방식
│           ├── trainer.py             # fit/validate/test/predict 공개 API
│           ├── datamodule.py          # 같은 단계별 Loader API
│           ├── engines/               # Ignite의 실제 반복 실행
│           │   ├── supervised.py
│           │   ├── evaluation.py
│           │   ├── prediction.py
│           │   └── adversarial.py
│           └── tasks/                 # 같은 주요 Hook을 제공하는 Wrapper
│               ├── base.py
│               ├── classification.py
│               ├── regression.py
│               ├── segmentation.py
│               ├── detection.py
│               ├── anomaly.py
│               ├── autoencoder.py
│               ├── vae.py
│               └── gan.py
├── examples/
│   ├── models/                       # 기존 순수 nn.Module 연결 예
│   ├── datasets/                     # 기존 Dataset·transform 연결 예
│   ├── python_api.py                 # Trainer API 사용 예
│   └── predict_pytorch.py            # 독립 Predictor 사용 예
└── tests/
    ├── core/
    ├── postprocessing/
    ├── artifacts/
    ├── lightning/
    ├── ignite/
    ├── inference/
    └── cli/
```

config의 분류·회귀 파일은 설정 배치 예시다. 나머지 Task의 설정도 지원 범위에 포함될 때
추가한다. 학습 결과·로그·체크포인트·추론용 결과물은 실행 시 지정한 출력 위치에 저장하며
소스 코드와 구분한다. 출력 경로 기본값과 Git 제외 정책은 구현 시 확정한다.

### 폴더별 역할과 의존 경계

| 위치 | 역할과 기준 | 상세 검토 |
| --- | --- | --- |
| backends/lightning | LightningModule·DataModule·CLI 연결만 작성하고 학습·평가·예측 반복과 Trainer는 native 사용 | [05](05-lightning-backend.md) |
| backends/ignite | Lightning 형태의 Wrapper·Trainer·DataModule·CLI를 제공하고 내부 Engine으로 실행 | [06](06-ignite-backend.md) |
| core | 모델 조합과 배치·출력 계약의 순수 공통 코드. 필수 공통 학습 Task 계층을 뜻하지 않음 | [02](02-task-wrappers.md) |
| transforms | Dataset 변환 재사용과 선택적 사용자 정의 전처리 연결. 별도 Preprocessor를 필수로 두지 않음 | [03](03-data-and-transforms.md) |
| postprocessing | 모델의 원시 출력을 실제 예측값으로 변환하는 공통 코드 | [04](04-outputs-and-postprocessing.md) |
| inference | 원시 입력·준비된 배치를 구분하는 독립 Predictor | [07](07-pure-pytorch-predictor.md) |
| artifacts | 순수 모델 가중치와 복원 설정. 학습 재개용 native 체크포인트 처리와 구분 | [08](08-weights-and-checkpoints.md) |
| configs | 파일 설정과 명령줄 덮어쓰기. 공통 설정과 백엔드 전용 설정 구분 | [11](11-cli-and-config.md) |
| examples | 기존 모델·Dataset을 전달하는 예시. 사용자 모델을 이곳으로 옮길 의무는 없음 | [09](09-client-api-and-examples.md) |
| tests | 공통 계약, native 실행, Ignite 대응, 독립 추론과 CLI 검증 | [10](10-validation.md) |

Lightning 쪽에는 대체 Trainer나 별도 학습 루프 파일을 필수로 두지 않는다.
native Trainer·Callback·Logger 등은 코드에서 가져오거나 config의 class_path로 지정한다.
Ignite 쪽 trainer.py와 engines/가 같은 공개 사용 방식을 실제 Engine 실행에 연결한다.

core·transforms·postprocessing·artifacts·inference는 Lightning·Ignite를 import하지 않는다.
백엔드 계층은 공통 코드를 참조할 수 있지만, 공통 코드나 패키지 초기화가 백엔드를
역으로 불러오지 않도록 한다. 기존 모델·Dataset은 사용자 모듈 경로에서 주입할 수 있다.

main.py는 CLI 진입점 후보이며 백엔드 선택 문법은 미정이다. Lightning 경로에 진입하면
실제 LightningCLI가 native 객체를 생성하고 명령을 실행한다. 공통 진입점이 있다고 해서
Lightning 설정을 별도 최소 기능 파서로 교체하지 않는다.

### src 배치와 실행 명령

src 아래에는 별도의 프로젝트명 패키지 없이 core·backends·inference 등을 직접 둔다.
프로젝트 루트의 main.py가 src.backends 경로로 선택한 CLI를 import하는 구성을 제안한다.
이 방식에서는 src 자체를 import 기준으로 사용하고 추가 패키지 폴더를 두지 않는다.
src/__init__.py와 하위 패키지 초기화 코드는 필요한 백엔드를 자동으로 불러오지 않는다.

루트에서 main.py를 실행하는 명령 형태는 유지한다. src 이동은 Python import와 config의
class_path에 반영하며, 같은 생성자 계약을 유지하면 --model.out_dim 등 옵션은 바뀌지 않는다.
Lightning 예시는 다음과 같다. 코드와 config는 아직 구현되지 않았다.

```powershell
python main.py fit --config configs/lightning/classification.yaml --model.out_dim 2 --trainer.max_epochs 20
```

예를 들어 Task의 class_path는 src.backends.lightning.tasks.classification.ClassificationTask,
독립 Predictor import는 src.inference.predictor 경로가 된다. config의 사용자 모델은
실제 사용자 모듈 경로를 그대로 사용한다. src 파일을 직접 실행하는 방식과 혼용하거나
실행 위치에 따라 sys.path를 임의 변경하는 방식은 기본 실행 계약으로 삼지 않는다.

프로젝트 초기화 시 문서는 workflow에 따라 배치한다. 현재 INTENT·BRIEF는 기획 폴더에
유지하고, 실제 초기화 요청 전까지 docs/current 생성·문서 이동·코드 폴더 생성은 수행하지 않는다.

## 미정

- native Wrapper의 세부 상속과 순수 공통 코드의 재사용 단위.
- 공개 Trainer의 클래스명·구성 방식, Factory 도입 여부와 native 객체 노출 방식.
- 모델 구성요소 조합을 어느 공통 모듈에 둘지.
- 위 예상 구조의 세부 파일 분할·설정 조합 방식과 첫 버전에서 실제 생성할 파일 범위.

데이터 계약은 [03](03-data-and-transforms.md), 출력 계약은
[04](04-outputs-and-postprocessing.md), 사용자 호출은 [09](09-client-api-and-examples.md)에서 검토한다.
