# 프로젝트와 anomalib의 Dataset·DataModule 비교·평가 방법

작성일: 2026-10-22.

STFPM·EfficientAD의 모델 비교에 앞서 프로젝트와 anomalib 2.0.0이 같은 이미지·라벨·마스크·split·모델 입력을 사용하는지 확인한다. MVTec AD·BTAD·VisA별 검증 근거와 결과를 이 문서에 기록하고, 통과한 데이터 검증 ID를 [모델 비교 문서](model-comparison-guide.md)에 연결한다.

이 문서는 평가 절차와 기록 양식이다. 이번 문서 작성에서는 Dataset·DataModule을 실행하거나 비교용 코드를 구현하지 않았다. `미실행`과 `—`는 평가 결과가 없다는 뜻이다. 설치 때 수행한 일부 데이터 읽기는 양쪽 구현의 동등성 검증으로 취급하지 않는다.

## 1. 비교 범위와 현재 확인한 차이

| 항목 | 프로젝트 | anomalib 2.0.0 | 확인할 내용 |
|---|---|---|---|
| 공통 Dataset | `FolderAnomalyDataset`, `VisADataset` | 데이터셋별 Dataset·DataFrame | 파일 목록·원본 ID·라벨·마스크 대응 |
| DataModule | `AnomalyLitData`를 데이터별로 연결 | `MVTecAD`, `BTech`, `Visa` | split 구성·단계별 생명주기·DataLoader |
| 반환 형식 | `(image, target)` tuple | `ImageItem`·배치 객체 | 의미가 같은 필드를 대응시켜 비교 |
| 학습 target | 현재 정상 train은 빈 dict | 라벨·경로 등의 메타데이터 제공 | 필드 유무와 학습에 필요한 값 구별 |
| 전처리 위치 | Dataset의 `AnomalyTransform` | Dataset augmentation과 모델 PreProcessor | 실제 모델 입력 직전 tensor까지 비교 |
| valid/test 기본값 | 원본 test에서 valid 40% 분리 | 기본 `SAME_AS_TEST` | 기본 분할 차이를 먼저 기록하고 공유 split으로 통제 |
| 로컬 데이터 준비 | 필요한 폴더·파일 확인, 자동 다운로드 없음 | 없으면 다운로드·준비 처리 가능 | 로컬 존재 조건과 파일 변경 여부 확인 |

위 표는 현재 소스 검토에서 확인한 구조다. 실행 검증 완료를 뜻하지 않는다. 설치 버전·WinPython 경로·환경은 [설치 가이드](anomalib-install-guide.md), 프로젝트 계약은 [SPEC](../../specs/v0.2/anomaly_detection/SPEC.md)·[DECISIONS](../../specs/v0.2/anomaly_detection/DECISIONS.md)를 따른다.

먼저 각 구현의 원래 Dataset·DataModule을 사용해 기본 동작과 차이를 기록한다. 그 뒤 공유 split·동일 전처리를 연결한 조건을 별도 검증 ID로 평가한다. 양쪽에 같은 Dataset을 주입한 결과만으로 원래 Dataset 구현이 같다고 판정하지 않는다.

## 2. 단계별 검증 절차

### 2.1 원본 파일·라벨·마스크

원본 데이터에서 독립적인 기준 목록을 만들고 각 구현이 읽은 목록을 대조한다. 한쪽 구현의 누락을 그대로 복제한 공유 목록이 되지 않도록 폴더 또는 공식 CSV 기준과도 비교한다.

| 확인 항목 | 방법·기록 기준 |
|---|---|
| 원본 ID | 데이터셋·범주·원본 split·원본 상대 경로로 식별; basename만으로 매칭하지 않음 |
| 파일 집합 | 추가·누락·중복 개수와 실제 ID 목록 |
| 라벨 | 정상=0, 이상=1 대응; train에 이상 이미지가 없는지 확인 |
| 마스크 연결 | 이미지별 마스크 대응, 정상의 zero mask, 누락·중복 매칭 확인 |
| 디코딩 | RGB 채널 순서·shape·dtype·값 범위·화소 값 |
| 이진 마스크 | 원본 크기에서 이진화 후 foreground 위치·개수·값 집합 비교 |
| 준비 단계 | 실행 전후 파일 목록·필요 시 SHA-256으로 생성·변환·삭제 확인 |

이미지 파일의 해시와 디코딩한 화소의 해시는 구분한다. BMP→PNG처럼 저장 형식이 바뀐 경우 원본 ID 대응표와 디코딩된 화소·마스크 비교 근거를 남긴다. 원본 데이터와 가중치는 수정하지 않는다. 변환이 필요하면 별도 작업용 복사본이나 원본을 읽는 연결 코드를 사용한다.

### 2.2 train·valid·test 분할

프로젝트는 데이터 seed 42, `valid_ratio=0.4`를 기본으로 원본 test를 valid/test로 나눈다. 두 라벨이 각 split에 모두 포함될 때까지 최대 100회 seed를 바꿔 재시도하므로 실제 선택된 파일 목록을 기록해야 한다. anomalib의 기본 valid/test 공유와는 다르다.

| 확인 항목 | 판정 기준 |
|---|---|
| 기본 분할 | 각 구현의 기본값·실제 파일 수·차이 기록 |
| 통제 분할 | 동일 원본 ID 목록을 train·valid·test에 적용 |
| 라벨 분포 | split별 정상·이상 수 완전 일치; valid/test 모두 두 클래스 포함 |
| 교집합 | train∩valid, train∩test, valid∩test가 비어 있음 |
| 합집합 | 의도한 전체 원본 목록과 일치; 제외 표본은 사유 기록 |
| 재현성 | 동일 설정으로 새 DataModule을 생성해도 split 목록·해시 일치 |

같은 seed·비율이어도 파일 정렬과 분할 알고리즘이 다르면 결과가 달라진다. 공유 manifest에는 `sample_id`, `category`, `source_split`, `split`, `image_relative_path`, `label`, `mask_relative_path`를 저장한다. 정상 마스크가 파일 없이 생성되면 mask 경로는 비워 두고 생성 규칙을 기록한다. CSV 자체의 SHA-256과 정렬된 sample ID 집합의 해시를 구분해 보관한다.

### 2.3 전처리·실제 모델 입력

동일 원본 ID를 기준으로 아래 네 지점을 비교한다. 데이터 로더 출력이 같아도 모델 PreProcessor가 다시 변환할 수 있으므로 마지막 지점까지 확인한다.

1. 디코딩 직후, resize·정규화 이전 이미지와 이진 마스크.
2. Dataset transform 또는 augmentation 이후 샘플.
3. collate 이후 DataLoader 배치.
4. 모델 PreProcessor·batch callback 처리 이후, 순수 모델 `forward`에 들어가기 직전 입력과 평가용 마스크.

| 입력 프로필 | 최종 모델 입력 기준 |
|---|---|
| STFPM | RGB, float32, `[3, 256, 256]`, ImageNet mean `(0.485, 0.456, 0.406)`·std `(0.229, 0.224, 0.225)` 정규화 1회 |
| EfficientAD | RGB, float32, `[3, 256, 256]`, 외부 정규화 없이 0~1 범위; 모델 내부 정규화 유지 |
| 평가 마스크 | `[256, 256]` 또는 의미상 같은 단일 채널 형식, 이진 값과 영역 위치 일치 |

프로젝트는 resize→float 변환→선택적 정규화를 적용한다. anomalib 쪽 resize·dtype 변환 순서, 보간, antialias, crop, augmentation과 PreProcessor의 중복 적용 여부를 실제 설정으로 기록한다. 정수 이미지 resize와 float 이미지 resize는 같은 크기라도 화소 차이가 날 수 있다.

raw RGB 화소·라벨·이진 마스크·파일 집합은 우선 완전 일치를 요구한다. 동일 변환 조건의 float32 입력은 `atol=1e-6`, `rtol=1e-5`를 검토 기준으로 제안하며 실행 전에 확정한다. 최대·평균 절대 오차와 불일치 sample ID를 함께 기록한다. 기본 구현 차이가 있으면 원인을 먼저 기록하고, 통제 조건에서 다시 비교한다. 허용 오차를 결과에 맞춰 사후 확대하지 않는다.

### 2.4 DataLoader와 DataModule 생명주기

| 확인 항목 | 방법·판정 기준 |
|---|---|
| 배치 필드 | 프로젝트 image·label·mask와 anomalib image·gt_label·gt_mask의 의미 대응 |
| 배치 순서 | 우선 shuffle=false로 비교; 학습 순서는 별도로 sample ID·중복·누락 확인 |
| 샘플 수 | 전체 epoch에서 의도한 sample ID가 정확히 한 번 등장; sampler/drop_last 예외는 명시 |
| 마지막 배치 | batch size·drop_last·마지막 배치 크기·배치 수 기록 |
| 실행 설정 | num_workers, pin_memory, sampler, generator·worker seed 기록 |
| 반복 호출 | 같은 인스턴스의 setup 반복 시 기존 split이 의도치 않게 바뀌지 않음 |
| 독립 평가 | 새 인스턴스의 setup(test)·setup(predict)가 저장된 test 목록을 재현 |
| 단계 전환 | fit→validate→test→predict의 파일 ID 목록 유지와 예측 대상 확인 |

첫 비교는 단일 프로세스·num_workers=0으로 수행한다. 안정화 후 실제 학습 설정에서도 재현성을 확인한다. 같은 seed라도 generator 상태·로더 생성 순서·augmentation 난수 소비가 다르면 순서가 달라질 수 있다. 완전한 학습 연산 비교가 목적이면 공유 순서 또는 같은 입력 배치를 사용한다.

### 2.5 EfficientAD의 Imagenette

이상 탐지 Dataset과 별도로 penalty 학습 데이터도 확인한다. 프로젝트는 `E:/datasets/imagenette2`를 받아 내부에서 `train`을 연결하고, anomalib 2.0.0에는 `E:/datasets/imagenette2/train`을 전달한다.

클래스 이름·클래스별 파일 수·전체 sample ID, val 제외 여부, 이미지 decode, resize·RandomGrayscale·crop·tensor 변환 순서와 순환 iterator 동작을 기록한다. 동일 seed만으로 랜덤 변환 일치를 가정하지 않는다. 개별 연산 비교에는 동일하게 변환한 penalty 입력을 공급하고, 원래 penalty 로더의 난수·반복 동작은 별도로 평가한다.

## 3. 데이터셋별 결과 기록

### MVTec AD

원본 경로: `E:/datasets/mvtec`. 프로젝트 `MVTecDataset`·`MVTecLitData`, anomalib `MVTecADDataset`·`MVTecAD`를 비교한다. 정상 폴더 `good`, 이상 이미지와 `ground_truth/<defect>/*_mask.png` 대응, 정상 zero mask를 확인한다.

| 범주 | 데이터 검증 ID | 파일·라벨·마스크 | 공유 split | STFPM 입력 | EfficientAD 입력 | Loader·stage | 모델 비교 진행 |
|---|---|---|---|---|---|---|---|
| bottle | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |
| grid | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |
| 추가 범주 | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |

기록: 원본 train/test 정상·이상 수 `—`, 양쪽 기본 split 차이 `—`, 통제 split CSV·해시 `—`, 파일 누락·중복 `—`, mask 불일치 픽셀 수 `—`, 프로필별 입력 오차 `—`, 원인·조치·재검증 ID `—`.

### BTAD

원본 경로: `E:/datasets/btad`. 프로젝트 `BTADDataset`·`BTADLitData`, anomalib `BTechDataset`·`BTech`를 비교한다. 정상 `ok`, 이상 `ko`, 마스크 접미사 없음, PNG·BMP 지원과 특히 03의 BMP 마스크를 확인한다. anomalib 준비 단계가 수행하는 변환과 기존 로컬 파일을 직접 읽는 동작은 구분한다.

| 범주 | 데이터 검증 ID | 파일·라벨·마스크 | 공유 split | STFPM 입력 | EfficientAD 입력 | Loader·stage | 모델 비교 진행 |
|---|---|---|---|---|---|---|---|
| 01 | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |
| 02 | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |
| 03 | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |

기록: 범주·확장자별 원본 수 `—`, 변환 전후 ID·화소 대응 `—`, mask 해상도·이진값 `—`, 양쪽 기본 split 차이 `—`, 공유 split 해시 `—`, 프로필별 입력 오차 `—`, 원인·조치·재검증 ID `—`.

### VisA

원본 경로: `E:/datasets/visa`. 프로젝트 `VisADataset`·`VisALitData`, anomalib `VisaDataset`·`Visa`를 비교한다. 원본 `split_csv/1cls.csv`의 object·split·label·image·mask를 기준으로 확인한다. anomalib의 `visa_pytorch` 준비 결과는 원본 CSV 행과 대응시키고, 경로 변경이나 파일명 변경이 누락·중복으로 오인되지 않도록 ID 대응표를 저장한다. 원본에서 준비 작업을 실행하지 않는다.

| 범주 | 데이터 검증 ID | CSV·파일·라벨·마스크 | 공유 split | STFPM 입력 | EfficientAD 입력 | Loader·stage | 모델 비교 진행 |
|---|---|---|---|---|---|---|---|
| candle | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |
| pcb1 | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |
| 추가 범주 | — | 미실행 | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |

전체 범주는 candle·capsules·cashew·chewinggum·fryum·macaroni1·macaroni2·pcb1·pcb2·pcb3·pcb4·pipe_fryum이다. 평가한 범주별로 행을 추가한다.

기록: CSV 경로·해시 `—`, 원본 CSV 행→각 구현의 ID 대응표 `—`, 라벨별 개수 `—`, mask 화소 비교 `—`, 공유 split 해시 `—`, 프로필별 입력 오차 `—`, 원인·조치·재검증 ID `—`.

### Imagenette penalty 데이터

| 데이터 검증 ID | train 파일·클래스 | val 제외 | 랜덤 변환·입력 | 로더·반복 | EfficientAD 진행 |
|---|---|---|---|---|---|
| — | 미실행 | 미실행 | 미실행 | 미실행 | 보류 |

기록: 루트·실제 ImageFolder 경로 `—`, 클래스별 개수·목록 해시 `—`, 고정 penalty 입력의 오차 `—`, 난수·iterator 조건 `—`, 원인·조치·재검증 ID `—`.

## 4. 실행별 상세 기록 양식

기본 동작 검토와 통제 조건 검증을 별도 ID로 기록한다. 결과 파일은 예를 들어 `outputs/anomalib-comparison/data/<검증 ID>`에 보관하고 실제 생성된 경로만 문서에 기입한다.

| 항목 | 프로젝트 | anomalib |
|---|---|---|
| 데이터 검증 ID / 일시 / 실행자 | — | — |
| 소스·라이브러리 버전 / 설정 | — | — |
| 원본 데이터셋 / 범주 / 경로 | — | — |
| 검증 조건: 기본 동작 또는 통제 조건 | — | — |
| 준비 단계의 파일 변경 여부 | — | — |
| 원본 ID 목록·대응표 경로 | — | — |
| train 정상 / 이상 수 | — | — |
| valid 정상 / 이상 수 | — | — |
| test 정상 / 이상 수 | — | — |
| 공유 manifest 경로·SHA-256 | — | — |
| 추가 / 누락 / 중복 ID 수·목록 | — | — |
| split 교집합·합집합 확인 | — | — |
| 라벨 / mask 불일치 수 | — | — |
| decode·Dataset·Loader·forward 직전 근거 | — | — |
| 모델 입력 프로필 / 전처리 설정 | — | — |
| tensor shape / dtype / min·max | — | — |
| 이미지 최대 / 평균 절대 오차 | — | — |
| mask 불일치 픽셀 수 | — | — |
| 학습 순서 / batch 수 / 마지막 batch | — | — |
| setup 반복·독립 평가의 목록 해시 | — | — |
| 실행 명령·비교 스크립트·결과 파일 | — | — |
| 판정·미해결 차이·재검증 ID | 미실행 | 미실행 |

## 5. 모델 비교로 진행하는 기준

동일 범주와 입력 프로필에 대해 파일·라벨·마스크, 공유 split, 최종 입력, 평가 Loader의 표본 대응이 확인되어야 한다. EfficientAD에는 Imagenette 검증도 필요하다. split·파일 목록은 두 모델에 재사용할 수 있지만 정규화가 다른 입력 프로필의 검증을 서로 대신하지 않는다.

판정은 `미실행`, `차이 확인`, `통제 조건 재검증 필요`, `모델 비교 진행 가능`으로 기록한다. 기본 동작에 차이가 있더라도 원인과 통제 방법을 기록하고 통제 조건 검증을 통과하면 해당 조건의 모델 비교는 진행할 수 있다. 남아 있는 차이의 영향을 분리하지 못하면 모델 결과의 직접 비교를 보류한다.

모델 비교 문서에는 데이터 검증 ID, manifest·입력 프로필 해시 또는 설정 참조, 통과 항목과 제한을 기록한다. 실제 비교 스크립트·공유 split adapter는 아직 이 문서에서 구현하지 않았으므로 실행 전에 준비하고 근거 경로를 남겨야 한다.
