# Anomaly detection 진행 상태

EfficientAD의 `train_st`·`train_ae`·`train_stae`·`train_loss`를 progress bar에서 제외하고 epoch별 `train_loss` 출력과 CSV 기록을 유지했다. 변경 후 학습 출력은 아직 실행 확인하지 않았다.

[ANOMALIB_PORTING_GUIDE.md](ANOMALIB_PORTING_GUIDE.md)에 anomalib 모델 이식 절차와 현재 생성자·경로·Tiler·검증 기록 규칙을 정리했다. 문서 작성이며 모델 실행 결과는 추가하지 않았다.

STFPM·EfficientAD의 순수 모델 및 native Lightning Wrapper 생성자 인자를 anomalib 원본과 맞췄다. 공통 TimmFeatureExtractor와 EfficientAD Wrapper는 `get_backbone_dir`로 로컬 가중치를 조회한다. STFPM Tiler 설정을 생성자에서 CLI 최상위 설정으로 옮기고 체크포인트의 별도 항목에 저장한다. 관련 문법·문서 인코딩만 정적으로 확인했으며 변경 후 학습·평가는 실행하지 않았다.

VisA 데이터셋을 `split_csv/1cls.csv` 기반으로 추가하고 `VisALitData`, 데이터 설정, CLI 선택에 연결했다. 로컬 경로 `E:/datasets/visa`와 CSV 형식을 확인했다. VisA 학습·평가 및 모델 실행은 아직 확인하지 않았다.

문서 정리 기준일은 2026-10-21이다. 현재 계약은 [SPEC.md](SPEC.md), 사용법·검증 명령은 [USAGE.md](USAGE.md)를 따른다.

## 현재 구현

| 항목 | 구현 상태 | 확인 범위 |
|---|---|---|
| MVTec Dataset·Transform·LitData | 구현 | 이전 bottle 사용자 fit 실행, 공통 데이터 처리 분리 후 실행 미확인 |
| 원본 기반 STFPM·loss·anomaly map | 구현 | 원본 AST 비교, bottle 사용자 fit 실행 |
| native Wrapper·Trainer·CLI·YAML | 구현 | bottle GPU 10 epoch 완료 |
| InferenceBatch·TimmFeatureExtractor·공통 metric | 구현 | 정적 확인, 기본 ResNet18 경로 사용자 실행 |
| 선택적 Tiler·설정·checkpoint 연결 | 구현 | 문법·설정·원본 메서드 정적 비교, 실행 미검증 |
| bottle Python 예제·저장 함수 | 구현 | 정적 확인, 최신 예제의 전체 실행 미확인 |
| MetricsPrinter epoch 출력 | 구현 | BTAD·EfficientAD medium 사용자 10 epoch 로그 확인, progress bar 변경 후 실행 미확인 |
| BTAD Dataset·Transform·LitData | 구현 | 로컬 파일 구조·마스크 경로 확인, 01 사용자 fit 완료 |
| EfficientAD 순수 모델·native Wrapper·CLI·설정 | 구현 | 원본 AST·설정 확인, BTAD 01·medium 사용자 fit 10 epoch 완료 |
| BTAD·EfficientAD Python 예제 3개 | 구현 | 문법·설정 정적 확인, 실행 미확인 |
| VisA Dataset·Transform·LitData·CLI | 구현 | 로컬 CSV 형식 확인, 학습·평가 실행 미확인 |
| 기존 노트북 이식 | 미완료 | 이전 import가 남아 있음 |

## 사용자 실행 확인

### MVTec bottle·ResNet18

사용자 터미널에서 GPU를 사용한 CLI fit이 10 epoch 완료됐다. 근거 파일은 outputs/anomaly-mvtec-bottle-stfpm-resnet18/version_1/metrics.csv와 config.yaml이다.

| 지표 | 값 |
|---|---|
| epoch 1 train loss | 6.9693 |
| epoch 10 train loss | 0.6259 |
| 마지막 valid image AUROC | 0.9889 |
| 마지막 valid pixel AUROC | 0.9561 |

중간 epoch의 image AUROC는 1.0이었다. best 저장 기준은 image AUROC이므로 마지막 epoch·pixel 최고 epoch와 다를 수 있다. 이 결과는 fit·validation 확인이며 test·predict·순수 가중치 복원 완료를 의미하지 않는다.

### MVTec grid

사용자가 category=grid로 실행한 시작 로그에서 seed 설정·CUDA 사용과 eval mode 경고를 보고했다. epoch 완료·성능·평가 결과는 아직 확인되지 않았다.

## 수정·정적 확인 이력

- anomalib 참조를 baf5e5fe12bc73cd520523046ba1d68279462e69로 고정했다. 원본 경로·변경점은 [DECISIONS.md](DECISIONS.md)에 기록한다.
- docstring 제거 후 loss.py·anomaly_map.py·STFPMModel.forward의 AST가 원본과 같은 것을 확인했다. 특징 추출기도 로컬 가중치 연결 생성자 외 원본 메서드 보존을 확인했다.
- MVTec 로컬 디렉터리와 ResNet18 가중치 파일 존재를 확인했다. 데이터·가중치 다운로드는 하지 않았다.
- 사용자 fit 로그와 CSV를 비교해 터미널 train_loss가 한 epoch 늦게 출력되는 것을 확인했다. CSV는 올바른 epoch에 기록됐다. 출력 시점을 train epoch 종료로 변경했으며 재실행은 하지 않았다.
- teacher의 eval mode는 의도된 동작으로 유지했다. 경고를 없애려고 teacher를 학습 상태로 바꾸지 않았다.
- Python 예제를 mvtec-stfpm-bottle.py로 변경하고 병합 후 bottle을 명시했다. 문법·인코딩·참조를 확인했으며 학습은 실행하지 않았다.
- Tiler·필수 enum/예외/보조 함수를 common에 이식하고 stride 생략 기본값과 인자 검사를 보완했다. tile/untile/unfold/random crop의 AST를 스타일 변경을 반영해 원본과 비교했다.
- tests/test_tiler.py에 타일 복원·gradient·오류 조건·활성 STFPM·checkpoint 복원 테스트를 작성했다. 테스트는 실행하지 않았다.

## 패키지·환경 기록

### BTAD·EfficientAD 추가

BTAD와 EfficientAD를 추가하면서 모델·학습·CLI·pytest는 실행하지 않았고 패키지도 추가 설치하지 않았다. 기존 실행 결과를 이번 변경의 검증 결과로 취급하지 않는다.

- BTAD 로컬 경로 E:/datasets/btad의 01·02·03과 전체 이상 마스크 연결을 파일 목록으로 확인했다.
- train 정상 수는 01=400·02=399·03=1000, test 정상/이상 수는 01=21/49·02=30/200·03=400/41이다. 프로젝트 valid/test 분할 전 개수다.
- E:/backbones/efficientad_pretrained_weights의 small·medium teacher 파일과 E:/datasets/imagenette2/train의 클래스 폴더 10개 존재를 확인했다. 가중치 텐서 로드·모델 forward 검증은 하지 않았다.
- Imagenette 설정을 E:/datasets/imagenette2 루트로 변경했다. 경로 해석은 기존 get_dataset_dir를 사용하고 ImageFolder에는 루트/train을 전달한다. 변경 후 학습 실행은 아직 확인하지 않았다.
- common 데이터 구현을 분리하고 기존 MVTec import를 유지했다. BTAD 03의 BMP 마스크를 지원한다.
- EfficientAD는 STFPM과 같은 고정 anomalib 커밋에서 이식하고 native Lightning으로 연결했다. 상세 차이는 [DECISIONS.md](DECISIONS.md)를 따른다.
- paths.toml·paths.example.toml의 backbones를 datasets와 같은 flat 문자열 매핑으로 변경하고 공통 로더·조회 함수·사용 문서를 수정했다. 기존 하위 테이블 형식은 더 이상 사용하지 않는다.
- 데이터·가중치·Imagenette 다운로드와 참조 원본·데이터 수정은 하지 않았다.
- 정적 확인: 관련 Python 32개 문법, anomaly YAML 6개, TOML 두 파일의 flat 문자열 형식·신규 로컬 경로, BTAD 이상 이미지/마스크 290쌍을 확인했다. 원본과 PDN·encoder/decoder·autoencoder 5개 클래스 및 손실·특징 거리·map 연결 등 5개 메서드의 AST가 같은 것을 확인했다.
- 문서 15개의 엄격한 UTF-8·한글 본문과 로컬 링크·코드 블록을 확인했다. 문법 확인은 실행 검증을 의미하지 않는다.
- BTAD 01·EfficientAD medium 사용자 CLI fit이 GPU에서 10 epoch 완료됐다. 보고된 마지막 valid_image_auroc=0.8713, valid_pixel_auroc=0.6598이며 약 4,000 step이다. 이는 현행 코드의 이전 출력 방식으로 실행된 결과다. 현재 출력 방식 변경 후 재실행은 하지 않았다.
- STFPM·EfficientAD의 valid AUROC를 progress bar에서 제외했다. MetricsPrinter의 epoch별 train_loss·valid 지표 출력은 유지한다. CSV 기록·best checkpoint 기준은 변경하지 않았다.

지정 Python은 C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe다. 작업 명령은 [루트 지침](../../../AGENTS.md)의 RTK 규칙을 따른다. 로컬 데이터 위치는 E:\datasets, pretrained 위치는 E:\backbones이며 실제 연결은 paths.toml을 사용한다.

2026-10-21 지정 Python의 metadata 확인과 timm 설치에서 다음 버전을 기록했다. 이번 문서 정리 시 다시 설치·실행 확인한 결과는 아니다.

| 패키지 | 기록된 버전 |
|---|---|
| torch | 2.2.1+cu118 |
| torchvision | 0.17.1+cu118 |
| lightning | 2.5.5 |
| torchmetrics | 1.9.0 |
| timm | 1.0.30 |
| huggingface_hub | 2.2.0 |
| safetensors | 0.8.0 |

timm 설치에서 누락된 의존성 anyio 4.15.1·click 8.5.0·h11 0.16.0·hf-xet 1.7.0·httpcore2 2.15.1·httpx2 2.15.1·truststore 0.10.5도 추가됐다. 기존 torch·torchvision·Lightning 버전은 유지했다. Tiler 추가와 문서 분리에서는 새 패키지를 설치하지 않았다. jsonargparse 4.40.2·PyYAML 6.0.3·GPU 모델 등 이전 확인 이력은 [v0.1 결정 기록](../../v0.1/DECISIONS.MD)을 참조한다.

## 남은 확인과 제한

- [ ] 최신 출력 callback의 첫 epoch loss·검증 생략 epoch·standalone validate 확인
- [ ] 기본 bottle의 native test·predict·best checkpoint 복원 확인
- [ ] bottle Python 예제의 JSON·순수 가중치 저장·독립 Predictor 출력 일치 확인
- [ ] tests/test_examples.py의 최신 STFPM·마스크·독립성 테스트 실행
- [ ] Tiler 자체·활성 학습·평가·checkpoint·CLI 설정 저장 테스트 실행
- [ ] grid 완료 결과·다른 MVTec 범주·추가 backbone·ViT 실행 확인
- [ ] 다중 장치와 anomalib 전체 런타임 대비 수치 동등성 확인
- [ ] 기존 노트북 이식
- [ ] 공통 데이터 처리 분리 후 MVTec·STFPM 실행 회귀 확인
- [ ] BTAD 01·02·03의 STFPM 학습·평가·마스크 정렬 확인
- [ ] BTAD·MVTec EfficientAD fit·validate·test·predict 확인
- [ ] EfficientAD small/medium teacher 로드·세 loss·통계·quantile 확인
- [ ] EfficientAD checkpoint 재개와 독립 model.pt 출력 일치 확인
- [ ] native step scheduler·긴 학습 설정·평가 시 보정값 유지 확인
- [ ] flat TOML 변경 후 classification·STFPM 가중치 로드 실행 확인

기존 torchvision STFPM checkpoint를 새 timm 구조로 직접 복원할 수 있다고 보장하지 않는다. Tiler는 현재 구현되어 있지만 위 bottle 사용자 실행은 Tiler 활성화 검증이 아니다. 이전 v0.1 smoke test·8개 테스트 통과·노트북 실행 이력은 [이전 기록](../../v0.1/PLAN.MD)으로만 보존한다.

이번 문서 정리에서는 문서 링크·UTF-8·한글 본문·코드 예시 문법을 정적으로 확인하며 모델·학습·평가·추론을 실행하지 않는다.
