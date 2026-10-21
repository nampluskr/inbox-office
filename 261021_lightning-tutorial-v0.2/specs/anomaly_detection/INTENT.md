# Anomaly detection 기획 의도

[공통 목적·원칙](../INTENT.md)을 따른다.

## 목적과 대상

정상 데이터로 학습하고 이미지·픽셀 수준 이상 점수를 계산하는 모델을, 원본 알고리즘을 보존하면서 native Lightning으로 실행한다. MVTec·BTAD·VisA와 STFPM·EfficientAD를 같은 실행 패턴으로 조합한다.

## 범위

STFPM과 EfficientAD의 teacher/student·autoencoder·loss·anomaly map 연산을 anomalib 원본에 가깝게 유지한다. 여러 모델이 공유할 InferenceBatch·TimmFeatureExtractor·Tiler·metric·필수 유틸리티는 task의 models/common에 둔다. 데이터셋의 공통 폴더 읽기·변환·분할은 data/common에 둔다. anomalib Engine·전용 Wrapper 기반·배치 실행 계층은 도입하지 않는다.

VisA는 후속 후보다. 아직 없는 파일·폴더나 실행 가능한 것처럼 보이는 예제는 미리 작성하지 않는다.

## Task 원칙

- teacher는 로컬 pretrained 가중치로 생성해 평가 상태·고정 파라미터를 유지한다.
- student는 처음부터 학습하며 모델별 teacher 특징을 맞춘다. EfficientAD는 autoencoder와 Imagenette penalty도 사용한다.
- 모델의 raw 점수·map과 임계값 판정·정규화 후처리를 구별한다.
- 선택적 타일링도 모델 내부 알고리즘 흐름으로 연결하고 설정값을 저장한다.
- 평가 분할 정책과 원본 대비 차이, 검증 한계를 명시한다.

현재 계약은 [SPEC.md](SPEC.md), 원본과의 차이는 [DECISIONS.md](DECISIONS.md), 새 모델 이식 절차는 [ANOMALIB_PORTING_GUIDE.md](ANOMALIB_PORTING_GUIDE.md), 실행은 [USAGE.md](USAGE.md), 상태는 [PROGRESS.md](PROGRESS.md)를 따른다.
