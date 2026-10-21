# Anomaly detection 설계 결정

[공통 결정](../DECISIONS.md)을 따른다. 현재 계약은 [SPEC.md](SPEC.md), 검증 범위는 [PROGRESS.md](PROGRESS.md)에 둔다.

## 원본 고정과 보존

참조 커밋은 anomalib의 [baf5e5fe12bc73cd520523046ba1d68279462e69](https://github.com/open-edge-platform/anomalib/tree/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/models/image/stfpm)이다. 재사용 코드의 저작권·SPDX를 유지하고 [Apache-2.0 원문](../../v0.1/licenses/Apache-2.0.txt)을 보관한다.

| 원본 | 현재 배치·변경 |
|---|---|
| stfpm/torch_model.py | model.py, 공통 import·로컬 get_backbone_dir 조회·선택적 tiler 속성 연결 |
| stfpm/anomaly_map.py·loss.py | 별도 파일과 원본 연산·메서드 유지 |
| stfpm/lightning_model.py | STFPMLitModel, native Lightning·tuple 배치·task metric |
| data/dataclasses/torch/base.py의 InferenceBatch | common/inference_batch.py, 네 필드의 NamedTuple 유지 |
| models/components/feature_extractors/timm.py·utils.py | common/timm.py·utils.py, 원본 기능과 필수 보조 함수 이식 |
| data/utils/tiler.py | common/tiler.py, Tiler·enum·예외·필수 보조 함수 이식 |
| efficient_ad/torch_model.py | efficientad/model.py, PDN·autoencoder·loss·map 유지, 공통 출력·로컬 로드 |
| efficient_ad/lightning_model.py | efficientad/lightning_model.py, native Hook·tuple 배치·보정·optimizer 연결 |

STFPM·EfficientAD 순수 모델 생성자에서 `weights_path`를 제거하고 각 anomalib `torch_model.py`의 생성자 인자와 맞췄다. native Lightning Wrapper도 `pre_processor`, `post_processor`, `evaluator`, `predictor`, `visualizer`를 제외한 원본 `lightning_model.py` 인자를 사용한다. STFPM의 optimizer 값은 원본처럼 고정하고 EfficientAD의 학습률 인자는 `lr`이다. 로컬 가중치는 모델 생성자 인자 대신 `get_backbone_dir`로 찾는다. Tiler는 STFPM 모델의 속성 및 CLI 최상위 설정으로 연결한다.

원본 docstring은 프로젝트 규칙에 따라 제거한다. 외부 알고리즘을 wrapper에 중복 구현하지 않는다.

## Native Lightning 연결

anomalib의 AnomalibModule·Batch·Evaluator·PreProcessor·PostProcessor·Visualizer·Engine은 도입하지 않는다. 프로젝트의 Dataset tuple과 native Hook을 연결한다. 모델·loss·metric은 Wrapper 내부에서 생성한다. STFPM optimizer는 원본 상수를 사용하고 EfficientAD는 lr·weight_decay를 인자로 받는다. 원본 권고인 sanity validation·gradient clipping 비활성 기본값을 trainer.yaml에 둔다.

raw score/map과 임계값 후처리를 구별하기 위해 원본 InferenceBatch를 사용한다. 기존 dict 소비자는 속성 또는 _asdict()로 변경해야 한다. 자동 threshold·label·mask 생성은 이번 범위에서 제외한다.

## 로컬 특징 추출과 teacher 고정

원본의 자동 pretrained 조회를 로컬 file 설정으로 변경한다. timm의 모델별 필터를 유지하면서 가중치 다운로드를 방지하려는 선택이다. get_backbone_dir로 paths.toml의 backbone 이름을 조회한다. 새 경로 registry는 만들지 않는다.

상위 train() 호출 후에도 teacher.eval()을 유지한다. teacher의 BatchNorm 통계를 고정하기 위한 동작이며 Lightning의 eval module 경고를 없애려고 teacher를 train 상태로 바꾸지 않는다. SGD는 student만 갱신한다.

## Tiler 이식

원본의 입력 타일링·특징 복원 연결을 사용한다. Tiler 객체는 STFPM 생성 후 모델 속성에 연결하며 CLI에서는 최상위 `tiler` 설정으로 생성한다. 기본 학습과 bottle 예제는 비활성으로 유지한다.

원본 stride=None의 미초기화 문제를 보완해 tile_size를 기본값으로 사용한다. 잘못된 크기·stride·border는 오류로 처리한다. private 메서드는 단일 밑줄, RandomCrop은 transforms.v2로 바꾼다. 원본의 중첩 평균·padding/interpolation·border 병합 동작은 유지한다. 파라미터 없는 Tiler는 state_dict 대신 저장 설정으로 복원한다.

## MVTec 분할

정상 train에는 이상 라벨이 없으므로 AUROC 기반 검증을 위해 공식 test에서 valid를 분리한다. 이는 공식 validation split이 아닌 프로젝트 정책이다. 기존 seed·최대 100회 재시도·valid_ratio를 유지하고 한 DataModule 안에서 한 번만 결정한다. 실제 클래스별 비율을 고정하는 계층 분할로 설명하지 않는다.

Dataset·Transform을 dataset.py에 모으고 표준 DataLoader를 DataModule에서 생성한다. 외부 DataLoader 상속·별도 transform.py·이전 lightning_datamodule.py 경로는 대체한다.

## 호환성과 출력

기존 torchvision 기반 STFPM checkpoint는 timm 특징 추출기 구조와 키 호환성을 보장하지 않는다. 기존 산출물은 보존하고 새 구조로 재학습한다. 이전 객체 주입형 STFPMModule에 호환 별칭을 만들지 않는다.

예제는 학습 후 best 평가·JSON·순수 모델 저장을 수행하고 CLI fit은 학습만 수행한다. Predictor는 task 의존성을 추가하지 않고 InferenceBatch를 그대로 반환한다.

## 지표 출력 시점

validation 종료에서는 현재 train epoch의 loss가 아직 집계되지 않아 이전 loss가 출력됐다. MetricsPrinter를 on_train_epoch_end로 옮겨 현재 loss를 읽도록 했다. 검증하지 않은 epoch에는 이전 valid 값을 다시 출력하지 않는다. 변경의 실행 확인 여부는 진행 문서에서 구분한다.

valid 지표는 검증 종료에만 갱신되므로 학습 배치 동안 이전 값을 보여주는 progress bar 표시를 제거한다. 사용자가 요구한 epoch별 train_loss·valid 지표 한 줄 출력에는 MetricsPrinter를 유지한다. prog_bar=False는 CSVLogger 기록과 checkpoint monitor 지표를 끄지 않는다.

## BTAD와 공통 데이터 처리

BTAD는 [anomalib BTech 데이터 처리](https://github.com/open-edge-platform/anomalib/blob/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/data/datasets/image/btech.py)의 라벨·파일 구조를 참조하고 프로젝트의 tuple Dataset으로 연결했다. 원본 DataFrame·자동 다운로드·anomalib 배치 계층은 도입하지 않는다. 실제 로컬 파일에서 01·03 이미지는 BMP, 02 이미지는 PNG, 03 마스크는 BMP인 것을 확인했다.

MVTec과 BTAD가 실제로 공유하는 폴더 파싱·변환·DataModule을 data/common으로 옮겼다. 데이터별 클래스는 정상 폴더명·이미지/마스크 확장자·마스크 접미사를 정한다. 기존 MVTec import와 기본 전처리·분할은 유지한다. BTAD에도 프로젝트의 test→valid/test 정책을 적용하며 공식 전체 test 성능과 직접 비교하지 않는다.

## EfficientAD 이식과 원본 차이

[고정 커밋의 EfficientAD](https://github.com/open-edge-platform/anomalib/tree/baf5e5fe12bc73cd520523046ba1d68279462e69/src/anomalib/models/image/efficient_ad)를 사용한다. 원본 torch_model.py를 model.py로 바꾸고 PDN small/medium·encoder/decoder·손실·map 연산을 유지한다. 원본에 별도 loss.py가 없으므로 손실을 억지로 분리하지 않는다. 원본 설명 일부의 EfficientNet 표현 대신 실제 구현인 PDN으로 기술한다.

native Wrapper는 원본 teacher 통계·Imagenette penalty·정상 valid quantile 계산 흐름을 연결한다. 가중치·Imagenette 자동 다운로드를 제거하고 teacher 파일은 TOML의 backbone 이름으로 조회한다. Imagenette는 명시적 `imagenet_dir` 또는 TOML의 루트 경로를 사용하고 그 아래 train 클래스 폴더만 읽어 val 이미지 혼입을 피한다. transforms는 v2로 통일하며 외부 정규화는 끈다.

원본 대비 다음을 조정했다.

- teacher와 통계·quantile ParameterDict의 gradient를 끈다. 파라미터 키는 유지한다.
- 재개 시 checkpoint의 teacher·통계를 보존하고 standalone 평가에서 quantile을 다시 맞추지 않는다.
- 채널 통계는 float64로 누적하고 분산·보정 분모의 0을 방지한다. quantile 계산용 map은 CPU에 모은다.
- scheduler는 native estimated_stepping_batches를 사용하고 interval=step을 명시한다. 원본 Wrapper의 StepLR 반환 형태를 그대로 복사하지 않는다.
- 기본 학습 길이는 프로젝트 공통 10 epoch로 유지하고, 긴 학습은 명시적 Trainer 설정으로 선택한다.
- 현재 256×256·배치 1·gradient accumulation 1·단일 장치를 명시적으로 요구한다. 미검증 분산 보정을 자동 허용하지 않는다.
- 순수 모델 전체 가중치 복원은 pretrained 파일 없이 가능하다. Wrapper의 새 학습은 로컬 pretrained teacher를 필수로 요구한다.
- 보정 점수는 음수가 가능하므로 공통 metric에 signed_scores 경로를 추가했다. 순위 보존 변환은 지표 계산에만 적용하고 raw 출력은 유지한다.

EfficientAD에는 STFPM용 Tiler를 자동 적용하지 않는다. mean/std·quantile·autoencoder의 원본 동작을 유지한 기본 경로부터 확인한다. 원본 anomalib 런타임과의 수치 동등성·논문 성능 재현을 완료로 기록하지 않는다.
