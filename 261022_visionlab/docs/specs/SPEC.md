# v0.3 목표 명세

작성일: 2026-10-22. 상태: 문서 기획 단계, 구현 미착수.

[INTENT.md](INTENT.md)와 [DECISIONS.md](DECISIONS.md)를 기준으로 향후 구현할 계약을 정의한다. 현재 실행 코드는 기존 위치에 있으며 이 문서의 경로·동작이 이미 제공된다고 해석하지 않는다. 이번 세션의 산출물은 v0.3 문서 3개뿐이다.

## 1. 패키지와 코드 배치

패키지 이름은 `visionlab`, task 이름은 `anomaly_detection`이다. `src`는 소스 루트이고 내부 import는 `visionlab.*`를 사용한다.

다음은 목표 구조다. 이번 작업에서 폴더·Python 파일·설정 파일을 생성하지 않는다.

```text
src/
  visionlab/
    anomaly_detection/
      configs/
        default.yaml
        trainer.yaml
        data/
        models/
      data/
        common/
        mvtec/
        btad/
        visa/
      models/
        components/
          feature_extractors/
            timm.py
            utils.py
          tiling/
            tiler.py
        stfpm/
        efficientad/
      trainers/
        lightning_cli.py
        lightning_trainer.py
      common/
        inference_batch.py
        metric.py
        pre_processor.py
        post_processor.py
        evaluator.py
        visualizer.py
        lightning_visualizer.py
    inference/
      predictor.py
    utils/
      config.py
      io.py
```

| 위치 | 책임 |
|---|---|
| `data/<dataset>/dataset.py` | 순수 Dataset·데이터별 Transform·원본 ID와 파일 대응 |
| `data/<dataset>/lightning_data.py` | native DataModule·표준 DataLoader·단계별 데이터 연결 |
| `data/common/` | 실제 공유하는 폴더 읽기·변환·분할·manifest 연결 |
| `models/<model>/model.py` | 순수 모델·모델별 연산·학습된 상태 |
| `models/<model>/loss.py`·`anomaly_map.py` 등 | 실제 필요한 모델별 순수 연산 |
| `models/<model>/lightning_model.py` | native Lightning Wrapper·Hook·optimizer·metric 상태 |
| `models/components/feature_extractors/` | 순수 특징 추출기와 특징 shape 확인용 보조 함수 |
| `models/components/tiling/` | 모델 입력 타일링·특징 복원과 관련 순수 보조 연산 |
| `trainers/` | native Trainer·CLI·logger·callback·설정 조립 |
| `common/inference_batch.py` | 모델·후처리·평가·추론에서 공유하는 순수 출력 형식 |
| `common/metric.py` | 순수 지표 구현, Evaluator에서 재사용 |
| `common/pre_processor.py` | 순수 PreProcessor·모델별 정규화와 입력 확인 |
| `common/post_processor.py` | 순수 PostProcessor·보정 통계·임계값·정규화·이진 예측 |
| `common/evaluator.py` | 순수 Evaluator·단계별 지표 집계; common/metric.py 재사용 |
| `common/visualizer.py` | 순수 ImageVisualizer·이미지 생성 |
| `common/lightning_visualizer.py` | native 시각화 파일 저장 Callback |
| `visionlab/inference/` | task별 Wrapper에 의존하지 않는 순수 추론 |
| `visionlab/utils/` | 순수 파일·설정 처리; 필요한 Lightning 연결은 별도 파일 |

모델에 필요하지 않은 loss·metric 파일을 관례만으로 만들지 않는다. 공통 요소는 실제 공유가 확인된 위치에 둔다. 순수 유틸리티와 패키지 초기화가 Lightning 연결 파일을 자동 import하지 않게 한다. 프로젝트 루트에 Python 진입점을 추가하지 않는다.

task의 `common`은 모델·Wrapper·후처리·평가·추론에서 공유하는 출력·metric·처리 기능을 담당한다. `data/common`의 데이터 처리와 `models/components`의 모델 연산은 역할별로 분리하고 구현을 중복하지 않는다. `common/__init__.py`는 `lightning_visualizer.py`를 자동 import하지 않는다. 순수 출력 형식·metric·네 처리 구성요소는 직접 import할 때 Lightning이 로드되지 않아야 한다.

### 모델 구성요소 그룹과 import

초기 목표 구조에는 별도 `models/common`을 두지 않는다. 기존 공유 파일의 목표 import는 다음과 같다.

| 기능 | 목표 모듈 |
|---|---|
| InferenceBatch | `visionlab.anomaly_detection.common.inference_batch` |
| 공통 metric | `visionlab.anomaly_detection.common.metric` |
| TimmFeatureExtractor | `visionlab.anomaly_detection.models.components.feature_extractors.timm` |
| 특징 shape 확인 | `visionlab.anomaly_detection.models.components.feature_extractors.utils` |
| Tiler | `visionlab.anomaly_detection.models.components.tiling.tiler` |

추가 모델을 이식할 때 필요한 경우에만 filters·stats·sampling·dimensionality_reduction·flow·layers·buffers·classifiers·cluster 등 구성요소 그룹을 추가한다. 원본 구성요소의 역할을 확인해 분류하고 실제 이식 전 빈 그룹·파일을 만들지 않는다. 특정 모델에만 종속된 연산은 해당 모델 폴더에 유지한다.

components에는 Lightning·anomalib을 참조하지 않는 순수 모델 구성요소만 둔다. 원본의 buffer·상태 관리 기능과 학습 Hook을 구분해 순수 부분만 이식하고 Hook은 Wrapper에서 연결한다. 그룹별 보조 함수는 해당 그룹 안에 배치한다. 모델 생성·복원·학습 연결의 공유 기능도 실제 책임으로 분류하고 이를 위한 models/common이나 공통 Lightning 기반 클래스를 미리 만들지 않는다.

각 구성요소는 필요한 순수 타입·연산만 import하고 task Evaluator·Visualizer·Trainer를 통해 연산을 실행하지 않는다. 패키지 초기화에서 모든 그룹·선택적 의존성·Lightning 연결을 일괄 import하지 않는다. common의 출력 형식·metric도 순수 기능의 경량 import를 유지한다.

기존 `src/anomaly_detection`·`src/inference`·`src/utils`의 필요한 기능은 구현 단계에서 이 구조로 옮긴다. classification의 이전은 현재 범위에 포함하지 않는다.

## 2. 의존성 경계

| 영역 | 허용 책임 | 참조하지 않을 실행 계층 |
|---|---|---|
| 순수 모델·Dataset·변환·loss·metric·추론·네 처리 구성요소 | PyTorch·torchvision·이미지 처리 및 모델에 필요한 독립 라이브러리 | Lightning·anomalib |
| Lightning 연결 | 순수 구성요소와 native Lightning API | anomalib |
| task CLI | 설정 해석·선택·Trainer 실행 | anomalib Engine·AnomalibModule |
| 별도 비교 실행 | 설치된 anomalib과 visionlab의 산출물을 비교 | visionlab 일반 실행 경로로의 역의존 |

순수 PyTorch 중심은 모든 보조 패키지를 재구현한다는 뜻이 아니다. timm·torchmetrics 등 모델에 실제 필요한 독립 라이브러리는 사용 이유·버전을 기록해 사용할 수 있다. anomalib에만 존재하는 기능은 필요한 범위를 이식하거나 독립 기능으로 작성한다.

`import anomalib`, 동적 import, anomalib 객체 상속·주입, 원본 소스 경로를 실행 시 찾아오는 방식은 `visionlab`에서 허용하지 않는다. anomalib이 설치된 개발 환경에서 import가 성공했다는 사실만으로 독립성을 인정하지 않는다.

## 3. 모델과 Lightning Wrapper

- `model.py`는 `nn.Module`이며 Lightning Hook·Trainer·CLI를 참조하지 않는다.
- 원본의 학습·평가 모드별 forward 입력·반환값·계산 순서를 모델별로 기록한다.
- Wrapper는 설정값으로 순수 모델·loss·metric 등을 내부 생성한다. 알고리즘을 Hook 안에 중복 작성하지 않는다.
- native `LightningModule`, `LightningDataModule`, `Trainer`, `LightningCLI`를 사용한다.
- optimizer의 대상 파라미터, scheduler interval·frequency·종료 step, 통계·보정 시점은 원본과 대조해 명시한다.
- 지표 상태는 valid/test별로 분리하고 단계 경계에서 초기화한다. 평가 시 모델 상태의 변경 여부를 명시한다.
- 모든 모델을 동일한 학습 loss 반환 형태에 억지로 맞추지 않는다. 공통 평가 출력으로의 연결은 얇은 변환으로 처리한다.
- Wrapper가 PreProcessor·모델·PostProcessor·Evaluator의 순서를 제어한다. ImageVisualizer 파일 저장 Callback은 완료된 결과만 소비한다.

모델별 이식 기록에는 원본 버전·커밋·파일, 생성자·forward·학습 상태, 필요한 자산·의존성, 변경점·이유, 정적·실행 검증 범위를 포함한다. 원본 저작권·라이선스를 유지한다.

## 4. Dataset·DataModule 계약

### 기본 샘플과 원본 식별

Dataset은 Lightning 없이 동작해야 한다. 기존 tuple 입력을 기본으로 `image, target`을 반환한다. 평가 target에는 정상=0·이상=1의 `label`과 이진 `mask`가 필요하며 정상 마스크는 0이다. 학습용 정상 Dataset의 target은 기존처럼 비어 있을 수 있다. 비교용 라벨·원본 경로·ID는 Dataset 메타데이터에서 추적할 수 있어야 한다.

| 값 | 기준 |
|---|---|
| image | Dataset 출력은 공간 변환한 RGB float32 `[3,H,W]`, 범위 `[0,1]`; 모델별 정규화는 PreProcessor 담당 |
| 평가 label | 정수 이진 라벨 |
| 평가 mask | 정수 이진 값, 최종 평가 해상도 `[H,W]` |
| sample ID | 데이터셋·범주·원본 split·원본 상대 경로를 구별할 수 있는 안정적 식별자 |

test·predict용 target 메타데이터에는 `sample_id`·`image_path`를 배치에 전달해 결과 파일과 원본을 대응시킨다. label·mask는 정답 없는 predict에서 생략할 수 있다. 표시용 이미지는 정규화 전 Dataset 이미지를 사용하고, 배치·예측과 같은 공간 좌표계를 유지한다. 학습용 target은 기존처럼 비어 있을 수 있다.

파일명 stem만으로 다른 범주나 경로의 이미지를 합치지 않는다. 누락된 마스크·지원하지 않는 범주·중복 ID는 명시적으로 오류를 보고한다. 오류 표본을 조용히 제외하지 않는다.

### 지원 데이터와 분할

| 데이터 | 초기 경로 | 기본 읽기 기준 |
|---|---|---|
| MVTec AD | `E:/datasets/mvtec` | 범주별 train/good·test·ground_truth |
| BTAD | `E:/datasets/btad` | 01·02·03의 ok/ko, BMP·PNG 마스크 지원 |
| VisA | `E:/datasets/visa` | `split_csv/1cls.csv`의 파일·라벨·마스크 |
| Imagenette | `E:/datasets/imagenette2` | EfficientAD penalty용 train만 사용 |

프로젝트 split 이름은 train·valid·test를 사용한다. 공식 Lightning API 이름은 유지한다. 기본 분할을 제공할 경우 기존 valid_ratio 0.4·seed 42·양쪽 라벨 확보 재시도 정책을 기록하고 실제 선택된 목록을 저장한다. 검증·테스트에 각각 두 클래스가 있어야 한다.

통제 비교용 manifest는 원본 ID·범주·원본 split·선택 split·이미지 상대 경로·라벨·마스크 상대 경로를 포함한다. 세부 포맷과 연결 API는 구현 전에 확정한다. 지정된 manifest는 임의로 다시 분할하지 않고 사용하며 누락·중복·split 교집합·원본과의 대응을 확인한다.

같은 설정의 새 인스턴스와 setup 반복·독립 test/predict에서도 같은 평가 집합을 복원해야 한다. 인덱스의 우연한 일치나 같은 seed만으로 동일 데이터를 보장하지 않는다. 학습 난수 seed와 데이터 분할 식별 정보를 구별한다.

### 전처리와 배치

`torchvision.transforms.v2`를 기본으로 Dataset에서 이미지·mask의 공간 변환과 이미지 float 변환을 함께 적용한다. resize·보간·antialias·crop·dtype 변환 순서를 기록하고 모델별 정규화는 Wrapper의 PreProcessor에서 적용한다. mask는 이진 영역을 보존하며 이미지용 정규화를 적용하지 않는다.

STFPM PreProcessor는 ImageNet 정규화를 1회 적용한다. EfficientAD PreProcessor는 정규화를 생략하고 `[0,1]` 입력과 모델 내부 정규화를 유지한다. v0.2 Dataset의 normalize=true를 이 흐름에 중복 적용하지 않는다. Dataset 출력·Loader 배치·최종 forward 입력을 각각 검증한다. 상세 처리 순서는 7절을 따른다.

DataLoader의 batch size·shuffle·drop_last·sampler·worker·seed를 최종 설정에 남긴다. 평가 Loader는 파일 ID별 예측을 복원할 수 있어야 한다. 학습 순서의 통제가 필요한 연산 비교는 동일 입력 배치를 사용한다. 데이터 준비가 원본 파일을 변경하거나 자동 다운로드하지 않게 한다.

## 5. 초기 모델 계약

### STFPM

순수 모델의 시작 인자는 기존 layers·backbone이며 Wrapper는 backbone·layers로 내부 구성한다. 초기 검증은 ResNet18과 layer1·layer2·layer3, 256×256 입력, Tiler 비활성으로 시작한다. teacher는 명시적인 로컬 pretrained state를 사용해 eval·gradient 고정을 유지하고 student만 학습한다.

SGD의 기존 기준은 lr 0.4·momentum 0.9·dampening 0·weight_decay 0.001이다. 원본 특징 정규화·손실·계층별 map 결합·이미지 score 계산을 대조한다. Tiler 활성화는 별도 비교 조건으로 두고 설정 저장·복원과 출력 크기를 확인한다.

### EfficientAD

PDN small/medium teacher·student·autoencoder·세 loss를 보존한다. teacher는 크기에 맞는 로컬 파일을 사용하고 teacher_out_channels=384, padding=false, pad_maps=true를 초기 기준으로 삼는다. 입력은 256×256·batch 1·단일 장치·accumulation 1을 기존 지원 기준으로 둔다. 확장은 후속 검증 후 결정한다.

정상 train에서 teacher 통계, 정상 valid에서 map quantile을 계산한다. Imagenette train만 penalty 입력에 사용한다. Adam의 기존 lr은 0.0001, weight_decay는 0.00001이다. 실제 scheduler 변경 step·epoch와 학습 예산을 기록한다. 10 epoch와 70,000 step 실행을 같은 학습 조건으로 비교하지 않는다.

standalone validate·test·predict는 fitted checkpoint의 통계·quantile을 유지한다. 재개 시 teacher·통계를 불필요하게 초기화하지 않는다. float64 누적·분모 하한·CPU quantile·step scheduler 등 기존 조정을 유지할지는 원본 대조 기록에 명시한다. 보정되지 않은 상태로 평가를 시작하면 오류를 보고한다.

## 6. 설정·CLI·로컬 경로

기본 설정은 task 아래에서 다음 네 계층으로 유지한다.

1. `configs/default.yaml`: 공통 실행 seed.
2. `configs/data/<dataset>.yaml`: 데이터·분할·로더·전처리 설정.
3. `configs/models/<model>.yaml`: Wrapper 인자와 필요한 데이터 기본값.
4. `configs/trainer.yaml`: Trainer·logger·callback 설정.

생성자 설정 우선순위는 선택 조합의 기본 계층 → 사용자 `--config` 전달 순서 → 명령행 인자다. 선택값은 별도 `selection.data`·`selection.model`에 두고 `--data`·`--model`로 지정한다. 개별 설정은 `--data.xxx`·`--model.xxx`·`--trainer.xxx`로 변경한다. 알 수 없는 선택·생성자 인자는 오류로 처리한다.

목표 CLI 모듈은 `visionlab.anomaly_detection.trainers.lightning_cli`다. 프로젝트 루트에서 지정 Python의 모듈 실행을 사용하며, `visionlab`을 import할 수 있는 패키지 준비가 선행되어야 한다. 패키징·실제 실행 명령은 구현 단계에서 검증한다.

native fit·validate·test·predict와 `ckpt_path` 복원을 사용한다. fit은 자동 test 실행을 뜻하지 않는다. 생성자에 없는 비교용·선택용 값을 모델 인자로 전달하지 않는다.

루트 `paths.toml`의 `[datasets]`·`[backbones]`는 이름→경로 문자열 매핑을 유지한다. 명시한 경로가 TOML 기본값보다 우선하며 최종 해석 결과를 저장한다. `--paths_file`로 선택한 파일이 모든 실제 자산 로더에 동일하게 적용되어야 한다. 순수 모델이 CLI와 무관한 기본 TOML을 다시 읽어 선택을 덮어쓰지 않게 한다. 실제 경로 전달 방식은 원본 모델 생성자를 검토한 후 구현 전에 결정한다.

필요한 자산이 없으면 오류를 표시한다. 무작위 초기화가 원래 알고리즘의 일부인 student 생성과 pretrained 누락의 대체 동작을 구별한다.

## 7. 전처리·후처리·평가·시각화

### 구성과 초기 범위

| 구성요소 | 순수 기능 | native Lightning 연결 |
|---|---|---|
| PreProcessor | 입력 shape·dtype 확인, 모델별 정규화 | Wrapper가 모델 forward 직전에 호출 |
| PostProcessor | 검증 통계·F1 임계값 추정, 정규화·이진 예측 | Wrapper가 fit validation에서 상태 수집·확정, 독립 평가에서 적용 |
| Evaluator | update·compute·reset, Image·Pixel AUROC/F1 | Wrapper가 valid/test 상태와 epoch 로그 관리 |
| ImageVisualizer | 표시 이미지·heatmap·mask·overlay 생성 | 별도 native Callback이 test·predict 결과를 로컬 저장 |

네 구성요소는 순수 기능과 Lightning 연결을 분리한다. 원본의 nn.Module·Callback 다중 상속이나 anomalib Batch를 요구하지 않는다. export용 변환·sensitivity·image/pixel threshold matching·고급 표시 옵션은 초기 범위에서 제외한다.

### 입력 처리와 Hook 순서

Dataset은 이미지·mask의 공간 변환과 이미지 float 변환을 완료하고 배치로 묶는다. Wrapper는 원래 이미지를 변경하지 않는 PreProcessor로 모델 입력을 만들고 순수 모델을 호출한다. STFPM의 정규화 기준은 mean `(0.485,0.456,0.406)`, std `(0.229,0.224,0.225)`이며 EfficientAD 입력에는 외부 정규화를 적용하지 않는다.

| 실행 단계 | 처리 순서 |
|---|---|
| train | Dataset 변환 → PreProcessor → 모델 학습 forward·loss → native optimizer |
| fit validation 시작 | Evaluator와 후처리 수집 상태 초기화; EfficientAD 내부 정상 valid quantile 보정은 모델별 계약대로 선행 |
| fit validation 배치 | PreProcessor → 모델 raw 예측 → raw AUROC 갱신·후처리 통계와 임계값 수집 |
| fit validation 종료 | 후처리 상태 확정 → raw AUROC 집계·로그 → 같은 epoch의 후처리 상태를 포함하는 checkpoint 저장 |
| standalone validate | PreProcessor → 모델 raw 예측 → raw AUROC; 보정 상태 변경 없음 |
| test | PreProcessor → 모델 raw 예측 → PostProcessor → raw AUROC·후처리 F1 → 결과 반환·시각화 Callback |
| predict | PreProcessor → 모델 raw 예측 → PostProcessor → 결과 반환·시각화 Callback; 정답 요구 없음 |

후처리·평가 순서를 독립 Callback의 등록 순서로 조정하지 않는다. best checkpoint의 가중치와 후처리 상태가 서로 다른 epoch에서 오지 않도록 저장 시점을 확인한다. validation 중 모델별 보정 통계와 공통 후처리 수집 순서도 검증한다.

### PostProcessor의 보정·정규화·임계값

PostProcessor는 image와 pixel 경로를 분리해 min·max·F1 기반 raw 임계값·유효 상태를 보관한다. fit validation 배치 전체를 대상으로 통계를 집계하고 epoch 종료에 확정한다. 지표와 마찬가지로 배치별 최적 임계값을 평균하지 않는다. 임계값 후보·동률 선택 규칙은 anomalib 2.0.0의 참조 구현과 대조해 구현 기록에 고정한다.

정규화는 원본의 임계값 중심 변환 `clamp((x-threshold)/(max-min)+0.5, 0, 1)`을 기준으로 한다. 정규화만 활성화하고 임계값 계산을 비활성화한 경우 중심값은 `(min+max)/2`로 둔다. 정규화가 활성화되면 이진 판정은 0.5 초과, 비활성화되면 저장된 raw 임계값 초과를 사용한다. raw 출력은 이 과정에서 수정하지 않는다.

후처리 전체와 정규화·threshold는 각각 비활성화할 수 있다. 필요한 경로의 보정 상태가 없거나 min/max·임계값에 비유한 값이 있으면 활성 처리에서 오류를 표시한다. 상수 점수로 max=min인 경로는 정규화 유효 상태를 만들지 않고 해당 정규화가 필요하면 오류를 표시한다. 이 경우 원본 대비 방어 처리 차이를 기록한다. 테스트 배치 값으로 범위를 대체하지 않는다.

라벨이나 mask가 없어 임계값을 계산할 수 없는 경로는 미보정으로 기록한다. 초기 threshold 계산은 해당 경로에 두 클래스가 있는 검증 정답을 요구한다. image 임계값을 pixel에 자동 재사용하지 않는다. 후처리를 끈 경우 raw 예측은 가능하며 이진 예측은 생성하지 않는다.

EfficientAD의 모델 내부 mean/std·quantile과 이 상태는 별개다. standalone validate·test·predict는 어느 보정값도 다시 맞추지 않는다. 후처리 상태의 유효성 확인은 활성화된 경로에 한정하며 전체 후처리가 비활성화된 raw 평가에 미보정 상태를 요구하지 않는다.

### Evaluator

기본 validation은 raw Image·Pixel AUROC, 기본 test는 raw Image·Pixel AUROC와 저장된 후처리 예측의 Image·Pixel F1을 기록한다. 후처리 threshold를 비활성화하면 F1은 계산하지 않고 사유를 기록한다. 같은 validation에서 맞춘 임계값의 F1을 독립 테스트 지표로 보고하지 않는다.

AUROC는 raw score·map에만 순위 보존 변환을 적용해 계산한다. 후처리의 clipping은 raw AUROC 입력에 적용하지 않는다. F1은 후처리된 bool 예측과 정답으로 계산하며 확률용 자동 변환을 적용하지 않는다. 단일 클래스 집합의 AUROC와 정답이 없는 metric은 계산 불가 사유를 기록하고 0으로 채우지 않는다.

Evaluator는 단계마다 상태를 초기화하고 전체 표본·픽셀을 누적해 계산한다. valid/test 상태를 분리한다. Pixel 지표는 동일 해상도·공간 좌표의 mask와 비교하고, shape·sample 대응 오류를 조용히 건너뛰지 않는다. 지표명에서 raw AUROC와 후처리 F1의 출처를 식별할 수 있어야 한다. 현재 best 기준의 valid_image_auroc 이름은 유지한다.

### 시각화·결과 전달

Wrapper의 평가·예측 결과는 `raw`, `processed` 예측을 별도 필드로 전달하고 시각화에 필요한 `sample_id`, `image_path`, 정규화 전 표시 이미지와 선택적 label·mask를 함께 제공한다. 후처리가 비활성화되면 processed는 없으며 raw는 항상 보존한다. 순수 모델의 InferenceBatch는 유지하고 이 메타데이터를 모델 forward 인자로 추가하지 않는다.

순수 ImageVisualizer는 원본 배치·예측을 수정하지 않고 입력 이미지·heatmap·정답 mask·예측 mask·overlay를 생성한다. 표시용 heatmap 스케일은 평가·후처리 상태와 별도로 취급한다. 정답·예측 mask가 없는 경우 해당 패널을 생략한다. 표시 이미지는 모델 입력 해상도와 좌표를 기준으로 하며 원본 해상도로 복원하는 기능은 후속 범위다.

native 저장 Callback은 기본 비활성이고 활성화 시 test·predict의 완료된 결과를 읽어 PNG를 저장한다. 저장 위치는 기본 실행 폴더 아래 images이며 실행·단계·범주·sample ID를 구분하고 하위 경로를 보존해 파일명 충돌을 방지한다. 출력 파일을 sample ID에 다시 대응할 수 있게 기록한다. 시각화 과정에서 정규화·임계값·metric 상태를 갱신하지 않는다.

### 구성요소 설정

PreProcessor·PostProcessor·Evaluator 설정은 Wrapper의 `model.pre_processor`, `model.post_processor`, `model.evaluator` 하위 설정으로 저장한다. 값은 생성에 필요한 설정이며 클래스 객체·함수·anomalib 객체를 받지 않는다. PreProcessor의 기본 정규화는 모델 계약으로 결정하며 잘못된 EfficientAD 외부 정규화는 오류로 처리한다.

기본 PostProcessor는 정규화·threshold를 활성화한다. 각 활성 상태와 실제 보정 상태를 구별해 저장하며 raw 비교 실행은 명시적으로 후처리를 끈다. Evaluator의 기본 metric은 앞 절의 단계별 구성을 사용한다. 시각화 설정은 task가 고정한 Callback의 `trainer.callbacks.visualizer`에 두고 enabled=false를 기본값으로 한다. 공간 변환·정규화·보정·시각화 설정을 최종 실행 설정에 모두 남긴다.

## 8. 출력·checkpoint·독립 추론

평가 결과는 공통 순수 출력 형식으로 이미지별 `pred_score`와 필요한 경우 `anomaly_map`을 제공한다. 초기 두 모델은 기존 `[B,1]` score·`[B,1,H,W]` map을 기준으로 하며 후속 모델의 형상 차이는 명시적인 연결 규칙으로 처리한다. `pred_label`·`pred_mask`는 후처리를 실제 적용했을 때만 제공한다.

raw score·map과 정규화·threshold 후 결과를 구분한다. 이상 점수는 확률로 가정하지 않으며 EfficientAD의 보정 점수는 음수일 수 있다. AUROC 계산용 순위 보존 변환이 모델 raw 출력을 바꾸면 안 된다.

Lightning checkpoint에는 학습 재개에 필요한 모델·optimizer·scheduler 상태와 하이퍼파라미터, 필요한 보정·비파라미터 설정을 저장한다. PostProcessor는 학습 파라미터가 아닌 min/max·임계값·유효 상태를 영속 상태로 저장하며 모델 상태와 같은 checkpoint에서 복원한다. Evaluator의 epoch별 누적값·임시 임계값 수집 배치는 추론용 영속 상태와 구분한다.

독립 추론용 산출물은 순수 모델의 전체 state_dict와 PostProcessor state_dict, 구조·공간 변환·PreProcessor·PostProcessor 설정을 제공한다. 모델 가중치와 후처리 상태를 각각 식별하고 묶음의 버전·무결성을 확인한다. Tiler 등 state_dict에 포함되지 않는 실행 설정도 복원 가능해야 한다.

Predictor는 Lightning Wrapper·Trainer·구체 task 모델을 참조하지 않는다. checkpoint 변환은 Lightning 연결 또는 별도 변환 경로가 담당한다. 학습된 전체 state 복원에 원본 teacher 가중치·Imagenette를 다시 요구하지 않는다. 기존 checkpoint 키·옛 import와의 자동 호환성은 보장하지 않는다.

독립 추론은 raw 이미지에 공간 변환·PreProcessor를 적용하는 진입점과 이미 공간 변환한 `[0,1]` 배치를 받는 진입점을 구분한다. 두 경로 모두 PreProcessor는 1회 적용하고, 순수 모델 raw 예측과 선택적 PostProcessor 결과를 제공한다. 이미 모델 정규화된 tensor를 같은 경로에 다시 전달하지 않는다. 후처리 활성 추론은 fitted 상태를 필수로 요구한다.

## 9. 로그와 평가 산출물

로컬 CSV·설정·checkpoint·평가 결과 파일을 사용한다. 초기 두 모델의 best 선택은 기존 valid_image_auroc 최대값을 기준으로 명시하고 선택 epoch·step을 저장한다. 마지막 epoch와 best checkpoint 결과를 구별한다. 모델별 다른 선택 기준이 필요하면 평가 전에 결정한다.

실행 기록에는 코드 버전·미커밋 변경, 패키지·장치, 최종 설정, manifest·가중치 해시, 입력 프로필, 학습 seed·step·LR 이력, checkpoint 식별 정보, metric·예측 원값 근거를 포함한다. 실행하지 않은 학습·test·export는 완료로 기록하지 않는다.

## 10. 검증 순서와 수용 기준

| 단계 | 확인 항목 | 다음 단계 조건 |
|---|---|---|
| 의존성 | anomalib 없이 import·실행, 순수 경로는 Lightning 없이 동작 | 실행 의존성 분리 확인 |
| Dataset·DataModule | 원본 파일·라벨·mask·공유 split·최종 입력·Loader·stage 재현 | 해당 범주·입력 프로필 검증 통과 |
| 순수 모델 | 같은 state·입력의 특징·loss·raw 출력·teacher 고정 | 모델별 허용 오차와 차이 근거 확인 |
| 처리 구성요소 | 정규화 1회·raw 보존·보정 상태 동결·metric 분리·이미지 대응 | 아래 수용 시나리오와 저장·복원 확인 |
| Lightning 연결 | fit·validate·test·predict·재개·설정 저장·보정 상태 | 단계별 실제 실행과 산출물 확인 |
| 독립 추론 | 전체 state·비파라미터 설정 복원, Wrapper 의존성 없음 | 입력·출력 일치 근거 확인 |
| 별도 anomalib 비교 | 같은 평가 데이터·자산·학습 예산·metric | 범주별 결과·차이 분석 기록 |

[Dataset·DataModule 비교 가이드](../../docs/anomalib/dataset-comparison-guide.md)를 먼저 적용하고, 데이터 검증 ID를 [모델 비교 가이드](../../docs/anomalib/model-comparison-guide.md)의 결과에 연결한다. 현재 가이드의 v0.2 실행 경로는 기존 구현용이며 v0.3 실행 가능 여부를 나타내지 않는다. 실제 이전 시 새 패키지 경로와 검증된 명령을 반영한다.

설치된 anomalib 2.0.0과의 비교는 별도 프로세스에서 수행한다. 기본 동작 차이와 통제한 비교 조건을 구별한다. 동일 상태 연산 비교와 독립 학습 후 성능 비교를 혼동하지 않는다. 수치 허용 오차·학습 예산·반복 seed·성능 판정 기준은 실험 전에 기록한다.

Dataset 파일 집합·라벨·mask 불일치나 미해결 입력 차이가 남으면 해당 모델 성능의 직접 비교를 보류한다. 비교 결과가 없는 모델은 이식 구현과 실행 확인까지만 기록한다. anomalib 전체 image 모델에 대해 검증 완료했다고 확대하지 않는다.

### 네 처리 구성요소의 수용 시나리오

- 같은 이미지의 Dataset→Wrapper 경로와 독립 추론 경로가 같은 최종 입력을 생성하고, STFPM 정규화가 중복되지 않으며 EfficientAD 입력이 `[0,1]`을 유지한다.
- 이미지와 mask가 같은 좌표로 변환되고, 시각화 표시 이미지가 정규화 전 입력과 sample ID에 대응한다.
- fit validation 전체 집계로 보정한 min/max·임계값이 같은 epoch checkpoint에 저장되고 복원 후 같은 후처리 결과를 생성한다.
- standalone validate·test·predict 전후 후처리 상태와 EfficientAD 내부 보정 상태가 동일하며, 테스트 정답이 상태 추정에 사용되지 않는다.
- 후처리·시각화 전후 raw tensor가 변경되지 않고 raw AUROC 입력이 clipping되지 않는다.
- valid/test metric이 반복 실행에서 누적되지 않으며 F1은 저장된 임계값과 bool 예측을 사용한다. 단일 클래스·정답 없음은 계산 불가 또는 해당 지표 생략 사유가 남는다.
- 후처리 미보정·상수 점수·비유한 값·누락 mask·미활성 경로를 각각 확인하고 잘못된 이진 예측이나 상태 대체가 발생하지 않는다.
- 시각화 활성/비활성, 정답 없는 predict, 후처리 비활성, 같은 basename의 다른 파일에서 저장 결과·파일 ID 대응을 확인한다.
- 네 순수 구성요소가 Lightning·anomalib import 차단 상태에서도 동작하고 native 시각화 Callback만 Lightning 연결에 의존한다.

위 시나리오는 향후 구현 시 수용 기준이다. 이번 문서 작업에서는 테스트 코드를 추가하거나 실행하지 않는다.

## 11. 이번 문서 작업의 완료 조건

- `specs/v0.3/INTENT.md`·`DECISIONS.md`·`SPEC.md`만 작성한다.
- 문서는 한국어·UTF-8로 저장하고 엄격한 디코딩·한글 본문·상대 링크를 확인한다.
- Python·YAML·TOML·패키징 코드, 실행 폴더·기존 모델·데이터·설정은 변경하지 않는다.
- 이식·학습·성능 비교의 현재 상태는 미착수로 유지한다.
