# v0.3 기획 의도

작성일: 2026-10-22. 상태: 문서 기획 단계.

## 목적

`visionlab` 패키지에 anomalib의 이미지 이상 탐지 모델을 이식한다. 기존 `src/anomaly_detection`의 구현과 분리 원칙을 바탕으로 모델·데이터 처리·독립 추론은 순수 PyTorch 중심으로 구성하고, 학습 실행에는 native Lightning의 DataModule·LightningModule·Trainer·LightningCLI를 사용한다.

이식한 모델은 anomalib을 설치하거나 import하지 않아도 실행할 수 있어야 한다. 별도로 설치된 anomalib은 동일한 로컬 데이터에서 데이터 처리와 모델 성능을 비교·검증하는 참조 구현으로 사용한다.

## 패키지와 작업 범위

- 패키지 이름은 `visionlab`으로 확정한다.
- 소스 배치는 `src/{package_name}/{task_name}`이며 첫 대상은 `src/visionlab/anomaly_detection`이다.
- 초기 이식·검증 대상은 기존 STFPM·EfficientAD, MVTec AD·BTAD·VisA다. EfficientAD의 Imagenette penalty 데이터도 검증 범위에 포함한다.
- PreProcessor·PostProcessor·Evaluator·ImageVisualizer도 초기 두 모델에 필요한 범위로 포함하고 `anomaly_detection/common`에 배치한다. 순수 처리 기능은 Lightning 없이 사용하고 Wrapper와 native Callback이 실행에 연결한다.
- 장기 범위는 anomalib의 image 모델이다. 추가 모델은 원본 분석과 필요한 의존성·데이터·검증 조건을 정리한 뒤 하나씩 이식한다.
- classification 등 다른 task의 이전과 새 task 추가는 후속 작업에서 정한다. 현재 범위만을 위해 빈 task 폴더나 미구현 모델을 만들지 않는다.

이번 세션은 이 문서와 [DECISIONS.md](DECISIONS.md)·[SPEC.md](SPEC.md) 작성에 한정한다. 코드 이동·수정, 패키지 설정 파일 작성, 설치, 데이터 처리, 모델 실행은 수행하지 않는다. v0.3 명세는 목표 계약이며 구현 완료 상태를 나타내지 않는다.

## 설계 원칙

### 실행 의존성의 독립성

원본의 알고리즘과 필요한 자료구조·보조 연산을 프로젝트 안에서 구현한다. anomalib의 기반 클래스·Engine·Batch·전용 callback을 실행 시 참조하지 않는다. import 별칭, 동적 import, 원본 패키지 객체를 주입하는 방식으로 의존성 경계를 우회하지 않는다.

### PyTorch와 Lightning의 책임 분리

순수 모델은 구조·연산·입출력과 학습된 모델 상태를 담당한다. Dataset·DataLoader·변환·loss·metric·후처리·Predictor는 Lightning 없이 사용할 수 있게 한다. Lightning Wrapper는 모델 알고리즘을 중복 작성하지 않고 Hook·optimizer·지표 상태·로깅·보정 실행 시점을 연결한다.

### 전처리·후처리·평가·시각화

Dataset은 RGB 변환·이미지와 마스크의 공간 변환·float 변환을 담당하고, Wrapper의 PreProcessor는 모델별 정규화를 담당한다. 독립 추론은 같은 두 단계를 조합한다. 이미 정규화한 입력을 다시 처리하지 않는다.

PostProcessor의 정규화 통계·임계값은 fit의 validation에서만 추정하고 저장한다. standalone 평가·예측은 저장 상태를 사용한다. raw 출력과 후처리 결과를 분리하고, Evaluator는 raw AUROC와 후처리 예측의 F1을 구별해 계산한다. EfficientAD의 모델 내부 quantile 보정과 공통 후처리 상태도 분리한다.

Wrapper가 전처리·모델 연산·후처리·평가 순서를 명시한다. 시각화는 순수 이미지 생성 기능과 native Callback의 파일 저장을 나누고, 정규화 전 표시 이미지·안정적인 sample ID를 사용한다. 원본의 nn.Module·Callback 다중 상속과 전용 Batch를 그대로 도입하지 않는다.

초기 시각화는 입력 이미지·heatmap·정답 및 예측 마스크·overlay의 로컬 저장을 지원하며 기본 비활성이다. sensitivity·threshold matching·export용 전처리와 고급 시각화 옵션은 후속 범위로 둔다.

### 모델별 알고리즘 보존

원본의 학습·평가 흐름, 특징 추출, 손실, 통계·보정, 학습 대상 파라미터를 먼저 분석한다. 참조 버전·커밋·원본 파일·라이선스를 기록하고 필요한 변경은 이유와 검증 영향을 남긴다. 여러 모델을 하나의 학습 방식에 맞추기 위한 불필요한 추상화는 추가하지 않는다.

### 공통 기능의 배치

모델 내부의 공유 연산은 `models/components` 아래에 특징 추출·타일링·통계·샘플링 등 구성요소별로 묶는다. task 전체가 사용하는 출력 형식·metric·전처리·후처리·평가·시각화는 task `common`, 데이터 읽기·공간 변환·분할은 `data/common`에 둔다.

초기 구조에는 별도 `models/common`을 두지 않는다. 기능별 책임이 명확한 위치를 먼저 선택하고, 추가 모델에서 실제로 필요해질 때 해당 구성요소 그룹을 만든다. 공유 Lightning 기반 클래스나 빈 그룹 폴더를 미리 추가하지 않는다.

### 데이터 검증의 선행

모델 성능을 비교하기 전에 Dataset·DataModule의 파일 목록·라벨·마스크·분할·전처리·배치·최종 모델 입력을 비교한다. 양쪽 기본 동작의 차이를 먼저 기록하고, 비교 조건을 통제한 뒤 모델의 연산·학습·성능을 평가한다.

### 로컬 자산과 재현 근거

`E:/datasets`와 `E:/backbones`의 기존 자산을 사용한다. 자동 다운로드·원본 데이터 변경·가중치 누락 시 임의 대체를 하지 않는다. 최종 설정, 데이터 분할, 가중치 식별 정보, checkpoint, 지표·로그를 저장해 결과의 근거를 추적할 수 있게 한다.

## 검증 순서와 완료 의미

1. 원본 Dataset·DataModule의 차이와 통제한 데이터 입력을 검증한다.
2. 동일 입력·가중치·모델 상태에서 특징·loss·raw 출력과 복원 동작을 비교한다.
3. 전처리 중복 방지·후처리 상태 복원·지표 상태 초기화·시각화 파일 대응과 native Lightning의 학습·검증·테스트·예측·재개·독립 추론을 각각 확인한다.
4. 동일 데이터와 학습 예산으로 별도 anomalib 실행 결과와 비교한다.

코드 이식, 정적 확인, 실행 확인, 성능 비교 완료는 구별한다. 과거 v0.2 결과나 설치 확인을 v0.3의 검증 결과로 옮기지 않는다. 다른 split이나 checkpoint에서 얻은 수치를 동일 조건의 성능 비교로 보고하지 않는다.

## 문서 역할

| 문서 | 역할 |
|---|---|
| [INTENT.md](INTENT.md) | 목적·범위·성공 기준 |
| [DECISIONS.md](DECISIONS.md) | 확정한 선택·근거·대안·이전 시 주의점 |
| [SPEC.md](SPEC.md) | 목표 폴더 구조·의존성·설정·데이터·실행·검증 계약 |
| [데이터 비교 가이드](../../docs/anomalib/dataset-comparison-guide.md) | Dataset·DataModule 선행 평가 절차·결과 양식 |
| [모델 비교 가이드](../../docs/anomalib/model-comparison-guide.md) | STFPM·EfficientAD별 비교 조건·결과 양식 |

v0.1·v0.2 문서는 기존 이력과 구현 참조로 보존한다. 향후 실제 v0.3 구현·검증 결과는 실행한 버전과 근거를 명시해 기록하며, 문서 기획만으로 완료 처리하지 않는다.
