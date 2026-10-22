# v0.3 설계 결정

작성일: 2026-10-22. 상태: 문서 기획 단계.

[기획 의도](INTENT.md)와 [목표 명세](SPEC.md)를 기준으로 확정한 선택과 근거를 기록한다. 아래 구조는 앞으로 구현할 대상이며, 이번 세션에서는 문서만 작성한다.

## D01. 패키지 이름과 import 경로

사용자가 선택한 패키지 이름은 `visionlab`이다. 소스는 `src/visionlab/<task>`에 배치하고 내부 import는 `visionlab.*`를 사용한다. `src`는 소스 보관 디렉터리이며 패키지 import 이름에 포함하지 않는다.

기존 `src.anomaly_detection.*`를 새 계약으로 계속 사용하면 패키지 이름을 도입하는 의미가 약해지므로 새 구현의 공개 import는 `visionlab.anomaly_detection.*`로 정한다. 실제 패키징 방법·배포 메타데이터는 구현 단계에서 마련한다. 현재 디렉터리만 바꾸면 즉시 import된다고 가정하지 않는다.

`visionlab` 이름의 외부 배포 중복 여부는 이 결정에서 검증하지 않았다. PyPI 배포는 현재 범위에 없으며 저장소 이름 변경도 이번 요청에 포함하지 않는다.

## D02. 먼저 이전할 task와 모델

v0.3의 첫 task는 `anomaly_detection`이다. 기존 STFPM·EfficientAD와 MVTec AD·BTAD·VisA를 시작점으로 삼아 구조·입출력·검증 절차를 확인한다. 추가 anomalib image 모델은 모델별로 원본·필수 연산·자산·의존성·검증 조건을 정한 뒤 진행한다.

전체 image 모델을 한 번에 복사하거나 분류용·미구현 task 폴더를 미리 추가하지 않는다. 기존 classification 코드의 이전은 별도 범위로 남긴다.

## D03. anomalib은 참조·비교 실행에 사용

`visionlab`의 실행 의존성에서 anomalib을 제외한다. 이식된 코드, 패키지 초기화, CLI·설정 처리 모두 anomalib을 import하지 않는다. anomalib을 상속한 Wrapper나 Engine을 얇게 감싸는 방식은 이식 목표에 부합하지 않는다.

설치된 anomalib은 별도 명령·프로세스에서 데이터와 모델을 비교하는 용도로만 사용한다. 같은 WinPython에 함께 설치되어 있어도 독립성이 확인된 것은 아니다. 향후 검증에서는 anomalib import 차단 또는 anomalib이 없는 환경에서 실행 가능 여부를 확인한다. 순수 PyTorch 경로의 Lightning 독립성도 별도로 검증한다.

비교용 실행 코드가 필요하면 `visionlab` 실행 모듈과 분리한다. 비교 코드의 anomalib import를 패키지 초기화·일반 학습·추론 경로로 연결하지 않는다. 비교 스크립트의 구체적 배치는 구현 시 정한다.

## D04. 원본 버전과 비교 버전을 구별

기존 STFPM·EfficientAD의 이식 참조는 커밋 `baf5e5fe12bc73cd520523046ba1d68279462e69`이며, 별도 설치된 비교 라이브러리는 anomalib 2.0.0이다. 이 두 소스가 같다고 간주하지 않는다.

v0.3의 초기 성능 대조는 설치된 2.0.0을 기준으로 계획한다. 각 모델의 실제 이식 원본은 작업 시작 시 버전 또는 커밋과 파일 경로를 고정하고 기록한다. 기존 참조를 2.0.0 또는 최신 main으로 조용히 교체하지 않는다. 원본 변경을 채택하면 생성자·연산·통계·학습 흐름·결과에 미치는 영향을 다시 검토한다.

재사용한 원본 저작권·SPDX·라이선스는 유지한다. 전체 라이브러리 대신 해당 모델에 필요한 보조 기능만 이식하며 import 경로와 연결 계층의 조정도 기록한다.

## D05. 순수 모델과 native Lightning Wrapper

모델별 `model.py`는 순수 `nn.Module`, `lightning_model.py`는 native `LightningModule`로 정한다. 데이터 연결은 native `LightningDataModule`, 실행은 native `Trainer`와 `LightningCLI`를 사용한다.

Wrapper는 설정값을 받아 모델·loss·metric 등을 내부에서 구성한다. 순수 모델·loss·metric 객체나 전처리 함수를 생성자에 주입하는 방식을 기본 계약으로 삼지 않는다. 실제 선택지가 생긴 항목만 필요한 설정을 노출한다. 원본 전용 PreProcessor·PostProcessor·Evaluator 인자는 그대로 복사하지 않고 순수 구성요소와 Hook으로 역할을 연결한다.

원본의 생성자·forward·상태는 가능한 한 보존한다. 프로젝트 연결 때문에 달라지는 인자·기본값·출력은 모델별로 문서화한다. 모든 image 모델에 같은 학습 반환값이나 같은 학습 제약을 강요하지 않는다.

## D06. Dataset·DataModule 비교를 모델 평가의 선행 조건으로 설정

기본 데이터 처리의 차이와 통제한 비교 조건을 구분한다. 파일 수만 같거나 seed·분할 비율이 같다는 이유로 동일 Dataset으로 판정하지 않는다. 원본 ID·라벨·마스크·split·최종 모델 입력을 검증한 데이터 검증 ID를 모델 결과에 연결한다.

프로젝트의 기존 test→valid/test 분할과 anomalib 기본 `SAME_AS_TEST`는 다르다. 통제 비교에서는 실제 파일 목록을 manifest로 고정한다. 이는 기존 v0.2의 메모리 내 분할만 사용하는 계약에서 보완하는 부분이다. manifest가 지정되면 다시 무작위 분할하지 않는다.

Dataset 출력과 모델 입력을 분리해 확인한다. anomalib의 모델 PreProcessor가 개입할 수 있으므로 최종 `forward` 직전까지 확인하며, 이미 변환한 배치를 다시 정규화하지 않는다.

## D07. 로컬 경로의 단일 해석

`paths.toml`의 `[datasets]`·`[backbones]`는 이름→경로 문자열의 flat 매핑을 유지한다. `--paths_file`로 선택한 파일, 설정에서 명시한 경로, 최종 실행 구성은 실제 Dataset·특징 추출기·teacher 로더까지 일관되게 전달되어야 한다.

기존 보조 로더가 내부에서 기본 `paths.toml`을 다시 읽어 CLI 선택과 달라질 수 있는 점을 그대로 이전하지 않는다. 경로는 조립 단계에서 한 번 해석하고, 순수 모델 또는 구성요소의 로컬 자산 연결은 원본 생성자 보존과 함께 모델별로 정한다. 이를 위해 임의의 전역 설정이나 추가 registry를 도입하지 않는다.

학습된 전체 state를 복원하는 평가·독립 추론은 원본 pretrained 파일이나 학습 전용 데이터에 불필요하게 의존하지 않게 한다. 모델별 필수 자산과 예외가 있으면 사전에 명시한다.

## D08. native CLI와 파일 기반 실행 기록

task의 `trainers/lightning_cli.py`를 모듈로 실행한다. 기존 네 YAML 계층과 데이터·모델 선택의 분리를 유지하며 native fit·validate·test·predict를 사용한다. 별도 학습 루프·Engine·등록 framework는 추가하지 않는다.

logger·callback의 구체 클래스는 task의 연결 코드에서 정하고 YAML은 생성자 설정을 담는다. CSVLogger·ModelCheckpoint·필요한 출력 callback과 native 설정 저장을 사용한다. TensorBoard·W&B는 별도 요청 없이 추가하지 않는다.

## D09. 모델 상태·보정·평가를 구별

STFPM의 teacher 고정, EfficientAD의 PDN teacher·통계·quantile·Imagenette penalty 등 모델 고유 흐름을 보존한다. 데이터 의존 통계는 지정한 학습·검증 집합에서만 계산한다. 테스트 데이터로 학습 상태·보정값·임계값을 맞추지 않는다.

기존 EfficientAD의 float64 통계 누적·분모 하한·step scheduler·재개 시 상태 보존은 이미 원본 대비 차이로 기록된 선택이다. v0.3에서 유지하거나 변경할 때 원본과의 차이 및 검증 결과를 남긴다. 별도 anomalib 실행을 통한 성능 차이가 곧 이식 오류나 수치 동등성을 뜻하지 않는다.

## D10. 이전 코드와 문서의 보존

이번 세션에는 v0.3 문서 3개만 추가하고 기존 실행 코드·설정·README·AGENTS를 변경하지 않는다. v0.1·v0.2는 이력과 참조로 보존한다. 현재 실행 가능한 코드를 이미 `visionlab`으로 이전했다고 기록하지 않는다.

향후 이전 시 import·CLI·설정·예제·checkpoint·독립 추론을 함께 점검한다. 옛 import나 checkpoint에 대한 자동 호환 별칭·키 변환은 기본 제공을 약속하지 않는다. 필요한 경우 실제 호환성 요구와 검증 범위를 따로 정한다.

## D11. 네 처리 구성요소를 순수 기능으로 포함

PreProcessor·PostProcessor·Evaluator·ImageVisualizer를 STFPM·EfficientAD에 필요한 범위로 포함한다. 설치된 anomalib 2.0.0의 역할과 연산을 참조하되 `nn.Module`과 Callback을 함께 상속하는 구조는 그대로 복사하지 않는다. 전처리·후처리·평가·이미지 생성 기능은 Lightning 없이 사용하고, Wrapper가 실행 순서를 제어한다. 시각화 파일 저장만 native Callback으로 연결한다.

네 구성요소는 `anomaly_detection/common`에 `pre_processor.py`, `post_processor.py`, `evaluator.py`, `visualizer.py`로 배치한다. 초기 기능 규모에서는 구성요소별 폴더보다 task 공통 파일로 모으는 편이 역할을 찾기 쉽다. native 시각화 Callback은 `common/lightning_visualizer.py`로 분리하고 common 패키지 초기화에서 자동 import하지 않는다.

`data/common`은 데이터 읽기·공간 변환·분할, `models/components`는 기능별로 묶은 공유 모델 연산을 담당한다. task 수준 `common`은 출력 형식·metric·전처리·후처리·평가·시각화의 공통 기능을 담당한다. Evaluator는 같은 task의 순수 metric을 재사용하며 같은 지표를 중복 구현하지 않는다. 상세 배치는 D15를 따른다.

모델별로 동일 연산을 다시 구현하지 않는다. Wrapper는 객체 대신 설정을 받아 필요한 구성요소를 생성하며, 상속 framework나 네 개의 독립 처리 Callback을 추가하지 않는다. 구성요소 간 순서를 Callback 등록 순서에 의존시키지 않기 위한 선택이다.

초기 범위는 모델별 정규화, 검증 기반 정규화 통계·F1 임계값, Image·Pixel AUROC/F1, 이미지·heatmap·mask·overlay 저장이다. sensitivity·image/pixel threshold matching·export용 변환·고급 시각화 옵션은 후속 범위다. 원본 전체 기능을 이식했다고 기록하지 않는다.

## D12. Dataset과 PreProcessor가 전처리를 분담

Dataset은 RGB 변환·이미지와 mask의 resize·float 변환을 담당한다. PreProcessor는 Wrapper에서 모델별 정규화를 적용한다. 서로 다른 원본 해상도도 collate 전에 같은 크기로 만들고, 모델별 정규화는 모델 호출 경로에서 통제하려는 선택이다.

STFPM은 ImageNet 정규화를 1회 적용하고 EfficientAD는 외부 정규화를 하지 않는다. 독립 Predictor는 같은 Dataset 공간 변환과 PreProcessor를 조합해 학습·평가와 입력을 맞춘다. raw 이미지 진입점과 이미 공간 변환한 배치 진입점을 구분해 이중 resize·정규화를 막는다.

기존 v0.2의 Dataset 내 정규화는 v0.3에서 PreProcessor로 옮길 대상이다. Dataset 출력과 최종 모델 입력의 두 지점을 데이터 비교 근거에 남긴다. 시각화용 이미지는 모델 정규화 전에 확보하고 sample ID·원본 경로를 배치 메타데이터에 전달한다.

## D13. 후처리 보정과 평가 원값·상태를 분리

fit의 validation 배치에서 raw 예측·정답으로 image/pixel min·max와 F1 기반 임계값을 수집하고 epoch 종료 시 확정한다. standalone validate·test·predict는 저장한 후처리 상태를 사용한다. 테스트 정답이나 배치별 범위로 보정 상태를 다시 맞추지 않는다.

정규화는 anomalib 2.0.0의 임계값 중심 min/max 변환을 참조한다. 이를 단순한 `(score-min)/(max-min)`으로 바꾸지 않는다. raw 예측은 보존하고 후처리 예측을 별도로 제공한다. validation은 기본 raw AUROC만 기록하고 test는 raw AUROC와 저장 임계값 기반 F1을 구별한다. 같은 validation에서 임계값을 선택한 F1을 독립 평가 결과로 내지 않기 위한 선택이다.

EfficientAD 모델 내부 mean/std·quantile과 공통 후처리 상태는 별도로 저장한다. 후처리 통계와 임계값은 학습 파라미터가 아닌 영속 상태이며 checkpoint·독립 추론 산출물에서 함께 복원한다. 활성화한 처리에 필요한 상태가 없거나 유효하지 않으면 명시적으로 오류를 표시한다.

## D14. 시각화 생성과 파일 저장 분리

순수 ImageVisualizer는 정규화 전 이미지·예측·선택적 정답을 받아 그림을 생성한다. native 시각화 Callback은 Wrapper가 반환한 결과를 읽어 test·predict에서 파일을 저장한다. 모델 출력이나 Evaluator 상태를 수정하지 않는다.

시각화는 기본 비활성이고 활성화 시 로컬 실행 폴더 아래에 저장한다. 실행·단계·범주·sample ID를 구분해 같은 basename의 파일이 충돌하지 않게 한다. 정답 없는 predict와 후처리 비활성 상태에서는 제공된 필드만 표시한다. heatmap 표시용 스케일은 평가 점수와 분리한다.

## D15. 모델 구성요소를 그룹화하고 별도 models/common은 두지 않음

사용자가 선택한 모델 공통 연산의 상위 경로는 `models/components`다. 기존의 평면적인 `models/common`에 여러 종류의 알고리즘을 계속 추가하는 대신 역할별 하위 그룹으로 나눈다. 설치된 anomalib 2.0.0의 `models/components` 구조도 대응 근거로 사용하되 실행 계층까지 통째로 복사하지 않는다.

| 기존 공유 기능 | 목표 배치 |
|---|---|
| `inference_batch.py` | task `common/inference_batch.py` |
| `metric.py` | task `common/metric.py` |
| `timm.py` | `models/components/feature_extractors/timm.py` |
| 특징 크기 확인용 `utils.py` | `models/components/feature_extractors/utils.py` |
| `tiler.py` | `models/components/tiling/tiler.py` |

현재 공유 기능은 위 위치로 모두 분류할 수 있으므로 초기 목표 구조에는 별도 `models/common`이 필요하지 않다. 출력 형식과 metric은 모델 외에 Wrapper·후처리·평가·추론에서도 사용하는 task 공통 기능이다. 관련 import도 `visionlab.anomaly_detection.common.*`와 `visionlab.anomaly_detection.models.components.*`로 구별한다.

추가 모델에서 실제 필요할 때 filters·stats·sampling·dimensionality_reduction·flow·layers·buffers·classifiers·cluster 그룹을 만든다. 이 목록은 분류 기준이며 빈 폴더 생성 목록이 아니다. 각 그룹의 보조 함수는 해당 그룹 안에 두고 광범위한 utils 파일로 모으지 않는다.

모델 생성·가중치 복원·학습 연결처럼 공유되는 기능이 생겨도 실제 책임으로 배치한다. 모델 내부 연산·상태 관리는 components의 적절한 그룹, task 출력·평가는 task common, Trainer·CLI 연결은 trainers 또는 명확한 Lightning 연결 파일, 모델 전용 기능은 모델 폴더에 둔다. shared Lightning 기반 클래스는 실제 중복과 필요한 인터페이스가 확인된 뒤 검토한다.

components는 순수 기능으로 유지하고 원본 base의 학습·검증 Hook 역할은 native Wrapper로 연결한다. 패키지 초기화에서 모든 그룹이나 선택적 라이브러리를 일괄 import하지 않는다. 구현 시 각 모델이 필요한 구성요소만 명시적으로 import한다.

## 구현 전에 구체화할 항목

- 모델별 이식 원본 버전·파일과 기존 구현 대비 변경 목록.
- 공유 split manifest의 입출력 연결과 비교용 실행 코드의 구체적 배치.
- 단일 경로 해석 결과를 원본 생성자 제약과 함께 전달하는 방식.
- 패키징 설정, 개발 설치·실행 준비 절차와 이전 산출물의 호환 범위.
- 추가 모델의 필수 의존성·입력·후처리·학습 상태 및 수치·성능 허용 기준.

위 항목은 미구현 사항이다. 필요한 결정은 구현 전에 문서로 보완하며 빈 코드나 추상화 계층으로 선점하지 않는다.
