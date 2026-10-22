# STFPM·EfficientAD 프로젝트 구현과 anomalib 구현의 실행 결과 비교·평가 방법

작성일: 2026-10-22.

프로젝트의 STFPM·EfficientAD 구현을 설치된 anomalib 2.0.0과 비교한다. 모델별로 MVTec AD·BTAD·VisA 평가 조건, 실행 근거, 정량 결과와 차이의 원인을 누적 기록한다. 이 문서 작성에서는 학습·평가를 실행하지 않았으며, 아래 결과 표의 `미실행`과 `—`는 측정값이 없다는 뜻이다. 0이나 실패 결과로 해석하지 않는다.

## 공통 평가 기준

### 비교 대상과 환경

| 구분 | 기준 |
|---|---|
| 프로젝트 구현 | `src/anomaly_detection/models/stfpm`, `src/anomaly_detection/models/efficientad` |
| 프로젝트 이식 참조 | anomalib 커밋 `baf5e5fe12bc73cd520523046ba1d68279462e69` |
| 비교할 설치 라이브러리 | anomalib 2.0.0 |
| Python | `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe` |
| 주요 환경 | torch 2.2.1+cu118, torchvision 0.17.1+cu118, Lightning 2.5.5, pandas 2.2.3 |
| GPU | NVIDIA RTX A4000, 드라이버 560.76, PyTorch CUDA 11.8 |
| 데이터·가중치 | `E:\datasets`, `E:\backbones` |

실험마다 실제 버전·GPU·프로젝트 커밋과 미커밋 변경 내역을 기록한다. 이식 참조 커밋과 설치 라이브러리 버전은 구별하며, 두 소스가 같다고 가정하지 않는다. 상세 환경·누락 의존성 보완·로컬 가중치 연결은 [설치 가이드](anomalib-install-guide.md), 현재 프로젝트 계약·차이는 [SPEC](../../specs/v0.2/anomaly_detection/SPEC.md)·[DECISIONS](../../specs/v0.2/anomaly_detection/DECISIONS.md)를 따른다.

### 비교를 진행하는 순서

1. [Dataset·DataModule 비교 가이드](dataset-comparison-guide.md)에 따라 기본 동작의 차이를 기록하고 공유 split·모델 입력·DataLoader를 검증한다. 해당 범주·입력 프로필이 `모델 비교 진행 가능`으로 판정되면 데이터 검증 ID를 연결한다.
2. 동일한 모델 가중치·상태에서 raw score와 anomaly map을 비교한다.
3. 동일한 split·학습 예산으로 각 구현을 학습하고 검증·테스트 성능을 비교한다.
4. 같은 범주·모델 크기·평가 집합끼리 결과를 묶고 차이의 원인을 기록한다.

2단계는 연산 및 복원 일치 확인이고 3단계는 학습 흐름을 포함한 비교다. 서로 다른 학습 가중치의 출력을 비교해 연산이 일치하지 않는다고 판정하지 않는다. 같은 seed라도 생성 순서·배치 순서·난수 소비가 다르면 초기화와 학습 경로가 달라질 수 있다.

### 데이터 검증 결과 연결

파일·라벨·마스크·분할·전처리·DataLoader의 상세 평가와 데이터셋별 결과는 [dataset-comparison-guide.md](dataset-comparison-guide.md)에 기록한다. 이 문서의 모델별 결과에는 해당 데이터 검증 ID와 공유 manifest·입력 프로필을 참조한다. 기본 데이터 구성 차이를 통제하지 않은 모델 수치는 직접 비교를 보류한다.

같은 범주의 STFPM·EfficientAD는 검증된 split을 재사용하되 정규화가 다른 입력 프로필은 각각 확인한다. 반복 seed 실험에서는 split을 고정하고 모델 학습 seed만 바꾼다. EfficientAD는 Imagenette penalty 데이터의 검증 ID도 연결한다.

공식 전체 test 성능도 필요하면 별도의 평가로 기록한다. 이 경우 모델 선택·임계값·EfficientAD 보정에 사용한 valid와 겹치는지 명시하며, 겹치면 독립 테스트라고 보고하지 않는다. 프로젝트의 일부 test 결과와 공식 전체 test 결과를 같은 표의 직접 비교값으로 사용하지 않는다.

### 지표와 판정

| 항목 | 기록·계산 기준 |
|---|---|
| Image AUROC | 같은 이미지 라벨과 이미지별 이상 점수로 계산, 범위 0~1 |
| Pixel AUROC | 같은 해상도의 이진 마스크와 anomaly map 전체 픽셀로 계산, 범위 0~1 |
| AUROC 차이 | 프로젝트 − anomalib, 예: 0.002는 0.2 percentage point |
| raw 출력 차이 | score·map 각각 최대 절대 오차, 평균 절대 오차, allclose 결과 |
| 학습 loss | 같은 단계·집계 방식에서 기록; STFPM과 EfficientAD의 loss 크기끼리는 비교하지 않음 |
| 추론 속도 | batch size·입력 크기·precision·측정 범위를 함께 기록 |
| 메모리 | 동일한 측정 구간의 GPU 최대 할당 메모리 MiB |
| 반복 실행 | 가능하면 학습 seed 42·43·44, seed별 원값과 평균±표준편차 |

AUROC는 배치별 AUROC의 평균 대신 전체 평가 표본을 모아 같은 metric 코드로 다시 계산한다. 프로젝트는 AUROC 계산 시 점수에 순위 보존 변환을 적용한다. raw 출력 비교에는 이 변환을 적용하지 않는다. anomalib 기본 PostProcessor의 정규화·clipping·threshold 적용 여부를 기록하고, 공통 AUROC 비교에는 같은 단계의 score·map을 사용한다. EfficientAD 모델 내부 quantile 보정과 외부 PostProcessor는 별개다.

F1·precision·recall·예측 mask가 필요하면 추가 행을 만들고 임계값 선택 방법과 valid 근거를 기록한다. 테스트 정답으로 임계값을 선택하지 않는다. 한 클래스만 있는 집합의 AUROC는 `계산 불가`로 기록하고 0으로 채우지 않는다.

동일 state의 FP32 출력 비교는 우선 `atol=1e-5`, `rtol=1e-4`를 검토 기준으로 제안한다. 이 값은 확인된 오차나 성능 보장값이 아니다. 실행 전에 허용 오차를 확정하고, EfficientAD 통계 누적 등 의도된 차이는 해당 상태와 오차를 함께 제시한다. 학습 후 AUROC 차이의 허용 범위도 결과를 보기 전에 정하며 반복 실행의 분산을 함께 평가한다.

추론 시간은 예를 들어 warm-up 20회 후 100회를 측정하고 median·p95를 기록한다. CUDA는 측정 전후 동기화하며, 파일 읽기·전처리·후처리 포함 여부와 model.eval·inference_mode 사용 여부를 맞춘다. 전체 데이터셋 AUROC 평가와 속도 측정용 고정 배치는 별도로 식별한다.

### 실행·산출물 기록 방법

명령은 프로젝트 루트의 PowerShell에서 실행한다.

```powershell
$py = 'C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe'
```

각 비교 실행에 `모델-데이터셋-범주-크기-seed-날짜` 등의 고유 ID를 부여한다. 산출물은 예를 들어 `outputs/anomalib-comparison/<실행 ID>/project`와 `anomalib`에 구분해 보관하고, 문서에는 실제 생성된 경로를 기입한다. 빈 산출물 폴더를 미리 만들 필요는 없다.

| 보관 항목 | 내용 |
|---|---|
| 실행 설정 | 최종 병합 설정, 실행 명령, 패키지 버전, 코드 상태 |
| 데이터 근거 | 공유 split CSV·해시, train/valid/test의 정상·이상 개수 |
| 가중치 근거 | 원본 pretrained 경로·SHA-256, 초기 state 또는 초기화 근거 |
| 학습 기록 | CSV·로그, 실제 epoch·optimizer step, 시간, 선택 checkpoint·해시 |
| 예측 원값 | 상대 경로에 대응하는 라벨·raw score·map·마스크 또는 재현 가능한 참조 |
| 평가 기록 | 공통 metric 결과 JSON/CSV, 속도·메모리 측정 조건 |
| 차이 분석 | 조건 차이, 실패 로그, 의도된 구현 차이, 재실행 ID |

프로젝트의 fit·test 명령은 아래 각 모델 섹션에 제시한다. `fit`은 테스트를 자동 수행하지 않는다. `best`는 프로젝트 기본 `valid_image_auroc` 최대값 기준이다. anomalib에서도 같은 valid와 선택 기준을 명시하고, 실제 선택 epoch·step을 확인한다. 저장된 checkpoint로 평가하고 동일한 파일의 해시를 기록한다.

anomalib 실행에는 [설치 가이드의 로컬 backbone 등록·EfficientAD subclass](anomalib-install-guide.md)를 사용할 수 있다. 다만 공유 split 연결, 공통 전처리·metric, 예측 원값 저장은 비교 실행 전에 추가로 연결해야 한다. 현재 프로젝트 CLI나 anomalib 기본 CLI만으로 이 비교 계약이 자동 충족되지는 않는다. 이 문서는 비교용 실행 스크립트나 어댑터를 구현하지 않는다. 실제 준비한 anomalib 실행 명령·스크립트 경로는 실행 기록 표에 남긴다.

[MVTec anomalib 평가 예제](../../examples/anomalib/README.md)는 STFPM·EfficientAD를 로컬 자산으로 실행하고 실제 split·설정·지표를 저장한다. 이 예제는 anomalib의 FROM_TEST 분할과 native 후처리 지표를 사용하며, 이 문서의 공유 split·공통 raw metric 비교 어댑터는 아직 제공하지 않는다.

## STFPM

### 모델별 고정 조건과 실행

| 항목 | 1차 비교 기준 |
|---|---|
| backbone | ResNet18, 양쪽 모두 `resnet18-f37072fd.pth`와 동일한 state |
| 특징 계층 | `layer1`, `layer2`, `layer3` |
| 입력 | 256×256, RGB, ImageNet mean/std 정규화 1회 |
| teacher/student | teacher eval·gradient 고정, student만 optimizer 갱신 |
| optimizer | SGD lr 0.4, momentum 0.9, dampening 0, weight_decay 0.001 |
| 학습 예산 | 1차 10 epoch, batch size 8, precision 32-true, 단일 GPU |
| seed | 첫 실행 42; 반복 시 split은 고정하고 학습 seed 변경 |
| Tiler | 첫 비교는 비활성; 활성 비교는 tile size·stride·mode·border를 별도로 고정 |

두 teacher의 state_dict 키·shape·값과 초기 student state를 먼저 확인한다. 독립적인 모델 생성이 동일 초기 student를 보장하지 않으므로 연산 비교에는 같은 state를 명시적으로 연결한다. checkpoint 키 변환이 필요하면 대응표·누락 키·초과 키를 기록하고 검토한다. 현재 변환 도구가 구현되어 있다고 가정하지 않는다.

특징 계층별 tensor, loss, raw anomaly map, 이미지 score 순서로 비교하면 차이가 시작되는 지점을 찾을 수 있다. raw map의 보간·결합과 teacher BatchNorm 상태도 확인한다.

프로젝트 학습 예시:

```powershell
rtk proxy $py -m src.anomaly_detection.trainers.lightning_cli fit --data mvtec --data.category bottle --model stfpm --model.backbone resnet18 --seed_everything 42 --data.seed 42 --data.batch_size 8 --trainer.accelerator gpu --trainer.devices 1 --trainer.max_epochs 10 --trainer.precision 32-true --trainer.logger.name compare-stfpm-mvtec-bottle-seed42
```

데이터셋·범주는 아래 표를 참고해 변경한다. 다음 `$run`은 실제 생성된 version 폴더로 바꾼다.

```powershell
$run = 'outputs/compare-stfpm-mvtec-bottle-seed42/version_0'
rtk proxy $py -m src.anomaly_detection.trainers.lightning_cli test --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
```

이 명령만으로 anomalib과 공유 split이 연결되지는 않는다. 비교 실행 전 공통 조건을 충족해야 하며 자세한 프로젝트 인자는 [사용법](../../specs/v0.2/anomaly_detection/USAGE.md)을 따른다.

### MVTec AD

경로는 `E:/datasets/mvtec`, CLI 선택은 `--data mvtec`이다. bottle로 시작한 뒤 grid와 나머지 범주를 추가한다. 범주별 결과를 남기고 전체 범주 평균을 계산할 때는 평가한 범주 목록·누락 범주를 명시한다.

| 범주 | 비교 ID / seed | 공유 split·checkpoint 근거 | 프로젝트 Image / Pixel AUROC | anomalib Image / Pixel AUROC | 차이 Image / Pixel | 상태·판정 |
|---|---|---|---|---|---|---|
| bottle | — / 42 | — | — / — | — / — | — / — | 미실행 |
| grid | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 추가 범주 | — | — | — / — | — / — | — / — | 미실행 |
| 범주별 macro 평균 | 범주 목록: — | 완료 범주 수: — | — / — | — / — | — / — | 집계 전 |

기록: train/valid/test 정상·이상 수 `—`, teacher SHA-256 `—`, 최종 설정·실행 명령 경로 `—`, 선택 epoch·step `—`, 공통 metric 파일 `—`, 특징·score·map 오차 `—`, 추론 median/p95·GPU 메모리 `—`, 차이 원인·다음 조치 `—`.

### BTAD

경로는 `E:/datasets/btad`, CLI 선택은 `--data btad`이며 범주 01·02·03을 각각 평가한다. 정상 폴더명은 `ok`, 이상은 `ko`이다. BMP·PNG 지원과 특히 03의 BMP 마스크를 확인한다. anomalib이 기존 폴더를 읽는 방식과 준비 단계의 이미지 변환 여부를 확인하며 원본 데이터는 수정하지 않는다.

| 범주 | 비교 ID / seed | 공유 split·checkpoint 근거 | 프로젝트 Image / Pixel AUROC | anomalib Image / Pixel AUROC | 차이 Image / Pixel | 상태·판정 |
|---|---|---|---|---|---|---|
| 01 | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 02 | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 03 | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 3범주 macro 평균 | — | 완료 범주 수: — | — / — | — / — | — / — | 집계 전 |

기록: train/valid/test 정상·이상 수 `—`, BMP·PNG 및 마스크 대응 확인 `—`, teacher SHA-256 `—`, 설정·명령·checkpoint 경로 `—`, 선택 epoch·step `—`, 특징·score·map 오차 `—`, 속도·메모리 `—`, 차이 원인·다음 조치 `—`.

### VisA

경로는 `E:/datasets/visa`, CLI 선택은 `--data visa`이다. 프로젝트는 원본 `split_csv/1cls.csv`를 읽는다. anomalib 2.0.0의 Visa는 준비 단계에서 `visa_pytorch` 구조를 생성할 수 있으므로 원본 폴더에서 바로 준비 작업을 실행하지 않는다. 필요하면 별도 작업용 복사본 또는 원본을 읽는 연결 코드를 사용하고, CSV 기준 파일 ID·라벨·마스크 값이 동일한지 확인한다.

| 범주 | 비교 ID / seed | 공유 split·checkpoint 근거 | 프로젝트 Image / Pixel AUROC | anomalib Image / Pixel AUROC | 차이 Image / Pixel | 상태·판정 |
|---|---|---|---|---|---|---|
| candle | — / 42 | — | — / — | — / — | — / — | 미실행 |
| pcb1 | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 추가 범주 | — | — | — / — | — / — | — / — | 미실행 |
| 범주별 macro 평균 | 범주 목록: — | 완료 범주 수: — | — / — | — / — | — / — | 집계 전 |

기록: 사용 CSV·공유 split 해시 `—`, 원본→평가 파일 ID 대응 `—`, 정상·이상 수 `—`, 전처리·마스크 검증 `—`, 설정·명령·checkpoint 경로 `—`, 특징·score·map 오차 `—`, 속도·메모리 `—`, 차이 원인·다음 조치 `—`.

전체 범주는 candle·capsules·cashew·chewinggum·fryum·macaroni1·macaroni2·pcb1·pcb2·pcb3·pcb4·pipe_fryum이다. 추가 실행 시 범주별 행을 늘린다.

## EfficientAD

### 모델별 고정 조건과 실행

| 항목 | 1차 비교 기준 |
|---|---|
| 모델 크기 | small부터 시작, medium은 별도 실험·행으로 기록 |
| teacher | 크기에 맞는 PDN teacher 파일, 경로·SHA-256·state 일치 |
| teacher 출력 채널 | 384 |
| 입력 | 256×256, 외부 정규화 비활성, 모델 내부 정규화만 사용 |
| penalty 데이터 | `E:/datasets/imagenette2/train`, 클래스·파일 목록 일치 |
| 학습 | batch size 1, 단일 GPU, accumulation 1, precision 32-true |
| optimizer | Adam lr 0.0001, weight_decay 0.00001 |
| 모델 인자 | padding=false, pad_maps=true |
| 1차 학습 예산 | 10 epoch; 실제 optimizer step 수·배치 수도 기록 |
| 긴 학습 | 별도 실험으로 70,000 step 검토; 양쪽 max_steps·종료 epoch·LR 이력 확인 |

프로젝트는 `imagenet_dir`에 `E:/datasets/imagenette2` 루트를 받으며 내부에서 `train`을 연결한다. anomalib 2.0.0에는 `E:/datasets/imagenette2/train`을 직접 지정한다. Imagenette val은 penalty 학습에서 제외한다.

동일 PDN teacher만으로 모델 전체가 같아지지는 않는다. student·autoencoder 초기 state와 teacher mean/std·두 map의 quantile을 함께 확인한다. 연산 비교에는 통계·보정 상태까지 같게 하고, 학습 비교에서는 각 상태의 계산 시점·대상 목록·누적 정밀도를 기록한다.

프로젝트의 통계 float64 누적·0 분모 방지, CPU quantile 수집, 재개 시 teacher·통계 보존, standalone 평가 시 보정값 유지, step 단위 scheduler는 [구현 차이](../../specs/v0.2/anomaly_detection/DECISIONS.md)에 기록된 조정이다. anomalib 2.0.0은 validation 시작 시 quantile을 계산한다. 독립 validate 실행이 보정 상태를 바꾸는지 확인하고, 최종 test에서 테스트 정답·테스트 데이터로 통계나 quantile을 다시 맞추지 않는다.

학습 비교에서는 실제 LR 변경 step·epoch를 대조한다. 원본 흐름을 유지한 비교와 scheduler 등의 조건을 통일한 비교를 실행 ID로 구분한다. 각 구현의 기본값을 바꿨으면 변경 내용과 이유를 남긴다. 성능 차이가 생겼다는 이유만으로 이식 오류로 결론 내리지 않는다.

연산 비교는 teacher 특징, student·autoencoder 출력, `train_st`·`train_ae`·`train_stae`와 합계, mean/std, quantile, 보정 전후 map·score 순서로 기록한다. Imagenette의 랜덤 변환도 동일 입력 텐서를 공급해 비교한다.

프로젝트 학습 예시:

```powershell
rtk proxy $py -m src.anomaly_detection.trainers.lightning_cli fit --data btad --data.category 01 --model efficientad --model.model_size small --seed_everything 42 --data.seed 42 --trainer.accelerator gpu --trainer.devices 1 --trainer.max_epochs 10 --trainer.precision 32-true --trainer.logger.name compare-efficientad-btad-01-small-seed42
```

프로젝트 모델 YAML이 `batch_size=1`, `normalize=false`를 적용한다. 긴 학습은 양쪽 조건을 별도로 합의한 뒤 `--trainer.max_epochs -1 --trainer.max_steps 70000`처럼 지정한다. 10 epoch 결과와 70,000 step 결과를 직접 비교하지 않는다.

```powershell
$run = 'outputs/compare-efficientad-btad-01-small-seed42/version_0'
rtk proxy $py -m src.anomaly_detection.trainers.lightning_cli test --config "$run/config.yaml" --ckpt_path "$run/checkpoints/best.ckpt"
```

평가에는 저장된 fitted checkpoint의 teacher·student·autoencoder·통계·quantile을 모두 복원한다. standalone test 직전에 새 teacher 파일로 덮어쓰거나 quantile을 재계산하지 않는다. 비교용 adapter는 준비·미구현 상태를 실행 기록에 명시한다.

### MVTec AD

경로는 `E:/datasets/mvtec`, CLI 선택은 `--data mvtec`이다. STFPM과 같은 공유 split을 사용하되 EfficientAD용 비정규화 입력을 별도로 준비한다.

| 범주 / 크기 | 비교 ID / seed | 공유 split·checkpoint 근거 | 프로젝트 Image / Pixel AUROC | anomalib Image / Pixel AUROC | 차이 Image / Pixel | 상태·판정 |
|---|---|---|---|---|---|---|
| bottle / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| bottle / medium | — / 42 | — | — / — | — / — | — / — | 미실행 |
| grid / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 추가 범주 / 크기 | — | — | — / — | — / — | — / — | 미실행 |

기록: 라벨별 split 개수·해시 `—`, PDN teacher·Imagenette 목록 해시 `—`, 통계·quantile 오차 `—`, LR 변경 위치 `—`, 실제 optimizer step `—`, checkpoint 선택 기준·경로 `—`, 세 loss·map·score 오차 `—`, 속도·메모리 `—`, 차이 원인·다음 조치 `—`.

### BTAD

경로는 `E:/datasets/btad`, CLI 선택은 `--data btad`이다. 01·02·03별 BMP·PNG 마스크와 정상 valid 표본 수를 확인한다. 정상 valid가 부족하거나 보정 범위가 매우 좁으면 quantile 값과 분모를 함께 기록한다.

| 범주 / 크기 | 비교 ID / seed | 공유 split·checkpoint 근거 | 프로젝트 Image / Pixel AUROC | anomalib Image / Pixel AUROC | 차이 Image / Pixel | 상태·판정 |
|---|---|---|---|---|---|---|
| 01 / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 01 / medium | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 02 / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 03 / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 추가 범주 / 크기 | — | — | — / — | — / — | — / — | 미실행 |

기록: 라벨별 split 개수·해시 `—`, teacher·Imagenette 목록 해시 `—`, 정상 valid 개수 `—`, mean/std·quantile·분모 `—`, LR 이력·실제 step `—`, 설정·명령·checkpoint 경로 `—`, 세 loss·출력 오차 `—`, 속도·메모리 `—`, 차이 원인·다음 조치 `—`.

### VisA

경로는 `E:/datasets/visa`, CLI 선택은 `--data visa`이다. STFPM의 VisA 절과 동일한 원본 CSV·파일 ID·마스크 검증 절차를 적용하고, 원본을 수정하는 준비 작업을 피한다. Imagenette는 VisA가 아닌 별도 penalty 데이터로 유지한다.

| 범주 / 크기 | 비교 ID / seed | 공유 split·checkpoint 근거 | 프로젝트 Image / Pixel AUROC | anomalib Image / Pixel AUROC | 차이 Image / Pixel | 상태·판정 |
|---|---|---|---|---|---|---|
| candle / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| candle / medium | — / 42 | — | — / — | — / — | — / — | 미실행 |
| pcb1 / small | — / 42 | — | — / — | — / — | — / — | 미실행 |
| 추가 범주 / 크기 | — | — | — / — | — / — | — / — | 미실행 |

기록: CSV·공유 split 해시 `—`, 라벨별 개수·파일 ID 대응 `—`, teacher·Imagenette 목록 해시 `—`, 통계·quantile·LR 이력 `—`, 설정·명령·checkpoint 경로 `—`, 세 loss·출력 오차 `—`, 속도·메모리 `—`, 차이 원인·다음 조치 `—`.

EfficientAD의 데이터셋별 전체 평균은 small·medium을 구분해 작성한다. 모든 데이터셋에서 범주별 AUROC의 macro 평균과 범주를 합친 pooled AUROC는 다른 지표이므로 집계 방식을 명시한다.

## 실행별 상세 기록 양식

각 결과 행의 비교 ID에 대해 아래 양식을 복사해 추가한다. 반복 seed는 기존 결과를 덮어쓰지 않고 새 행과 상세 기록으로 남긴다.

| 항목 | 프로젝트 | anomalib |
|---|---|---|
| 비교 ID / 실행일 / 실행자 | — | — |
| 모델 / 데이터셋 / 범주 / 크기 | — | — |
| 소스 버전·변경 사항 | — | — |
| 환경·패키지 기록 파일 | — | — |
| 공유 split 경로·SHA-256 | — | — |
| Dataset·DataModule 검증 ID / 입력 프로필 | — | — |
| EfficientAD Imagenette 검증 ID | — | — |
| train / valid / test 정상·이상 수 | — | — |
| 전처리·mask 변환·입력 tensor 근거 | — | — |
| pretrained / 초기 state 해시 | — | — |
| 최종 설정 / 실행 명령·스크립트 | — | — |
| 학습 seed / 데이터 seed | — | — |
| 학습 epoch / optimizer step / LR 이력 | — | — |
| checkpoint 선택 기준 / epoch / step | — | — |
| checkpoint 경로·SHA-256 | — | — |
| EfficientAD 통계·quantile 근거 | — | — |
| 예측 원값 / 공통 metric 파일 | — | — |
| test Image / Pixel AUROC | — | — |
| raw score·map 최대 / 평균 절대 오차 | — | — |
| allclose 조건·결과 | — | — |
| 추론 batch·측정 범위·반복 수 | — | — |
| 추론 median / p95 ms·GPU 최대 MiB | — | — |
| 상태·실패 로그·제한 | 미실행 | 미실행 |

평가 의견: 조건 일치 여부 `—`, 차이의 재현성 `—`, 의도된 차이와 미해결 차이 `—`, 추가 조치·재실행 ID `—`.

판정은 `비교 준비 중`, `실행 실패`, `조건 불일치로 직접 비교 보류`, `동일 조건 결과 기록 완료`, `차이 분석 중`처럼 근거와 함께 적는다. 허용 오차·성능 기준을 충족했다고 판정할 때는 해당 수치·실행 ID·산출물을 함께 인용한다.

## 기존 기록과 이번 비교의 경계

[진행 기록](../../specs/v0.2/anomaly_detection/PROGRESS.md)에 있는 STFPM MVTec bottle의 마지막 valid Image/Pixel AUROC 0.9889/0.9561, EfficientAD BTAD 01 medium의 0.8713/0.6598은 과거 사용자 fit·validation 기록이다. 같은 split·checkpoint의 anomalib 대조 결과가 없으므로 위 비교 표에는 옮기지 않았다.

[설치 확인](anomalib-install-guide.md)에서 수행한 MVTec 읽기, 합성 입력 STFPM forward, EfficientAD teacher 복원은 환경·로컬 경로 확인이다. 학습 성능·test AUROC·두 구현의 수치 동등성 검증 결과가 아니다. 현재 여섯 모델·데이터셋 조합의 비교 결과는 모두 미실행이다.
