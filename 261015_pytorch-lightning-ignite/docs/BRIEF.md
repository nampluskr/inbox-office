> 버전: v0.1 · 작성일: 2026-10-15 · 상태: 사용자 검토용 초안

# BRIEF — pytorch-lightning-ignite

이 문서는 [INTENT.md](INTENT.md)를 기준으로 한 v0.1 기획이다. 사용자가 v0.1은
Lightning 구현으로 지정했다. 먼저 Lightning 구현과 검증·테스트를 완료한 뒤,
v0.2 또는 그 이후 버전에서 같은 공개 API의 Ignite 구현을 진행한다.
Ignite의 정확한 착수 버전과 v0.1에 포함할 Task 세부 범위는 미정이다.

v0.1에서는 native Wrapper·Trainer·DataModule·LightningCLI와 학습·평가·추론을
구현·검증한다. 기존 요구인 공통 변환·후처리와 독립 순수 PyTorch Predictor도 유지한다.
Ignite 관련 내용은 후속 방향을 설명하는 것이며 v0.1 완료 조건에 포함하지 않는다.

Lightning을 최대한 native 그대로 사용하고 Ignite가 같은 공개 API로 동작하게 하는 것은
프로젝트의 큰 목적 중 하나다. 공통화를 위해 Lightning을 별도 최소 기능 API로 교체하거나
축소하지 않고, Lightning의 API와 동작을 기준으로 Ignite를 연결한다.

이 기준은 CLI에 한정되지 않는다. Lightning의 Task Wrapper는 LightningModule로
작성하고, Trainer·LightningDataModule 및 native 학습·검증·평가·예측 기능을 최대한
직접 사용한다. Ignite는 같은 주요 Wrapper Hook·Trainer API·데이터 제공 방식으로
사용할 수 있게 작성하고, 내부 학습·평가·예측은 Ignite Engine으로 실행한다.

## 배경

사용자는 `nn.Module`의 `forward()`만 정의된 순수 PyTorch 모델을 가지고 있다.
분류·회귀·분할·객체 탐지·이상 탐지에 대해 모델을 인자로 받는 Base Wrapper를 만들고,
각 Wrapper로 학습·평가·추론을 수행하고 싶다.
회귀(Regression)는 참고 자료 검토 이후 사용자의 추가 요청으로 지원 대상에 포함했다.

지원 대상에는 AE·VAE·GAN도 포함하고 싶다. 이 경우 기존 모델은 하나의 완성된 모델일
수도 있고, Encoder·Decoder·Generator·Discriminator 같은 개별 구성요소일 수도 있다.

데이터는 이미 구현된 PyTorch Dataset 또는 DataLoader로 주어진다. Lightning의
DataModule을 공통 API에 사용하고, Ignite에서도 같은 형식으로 데이터를 제공하는
방식을 원한다. 사용자는 이번 문서 작성 중 DataModule 포함을 확인했다.

참고 자료는 공통 Task 계층을 두는 초기 제안에서 백엔드별 Native Wrapper와 공통
클라이언트 API를 두는 후속 제안으로 전개된다. 두 안을 동시에 확정 설계로 채택하지
않는다. 후속 사용자 요청에 따라 Lightning native Wrapper·실행을 기준으로 Ignite가
맞추는 방향은 확정했다. 상세 상속 구조와 공통 유틸리티의 재사용 단위는 미정이다.

## 이번 버전에서 풀고 싶은 문제

### 버전별 구현 순서

| 구간 | 범위 | 다음 단계와의 관계 |
| --- | --- | --- |
| v0.1 | Lightning 기준 구현, 검증·테스트 | native 동작과 실제 공개 API·config·반환 계약을 검증한다 |
| v0.2 또는 그 이후 | 같은 API의 Ignite Wrapper·Trainer·DataModule·CLI와 Engine 구현 | Lightning 검증·테스트 완료 후 착수한다. 정확한 버전은 사용자가 지정한다 |

두 백엔드를 동시에 구현하지 않는다. 후속 Ignite는 v0.1에서 실제로 검증한 Lightning
구현·호출 예·테스트를 기준으로 작성한다. 이 표는 세부 Phase나 후속 버전 계획을 대신하지 않는다.

### 모델과 Task의 연결

기존 모델을 수정하지 않고 작업에 맞는 Wrapper에 전달하여 학습·평가·추론에 사용한다.
전체 지원 대상과 사용자가 제시한 모델 입력은 다음과 같다. 이 표는 첫 버전 전체 구현을
확정하는 목록이 아니다.

| 전체 지원 대상 | 기존 모델 입력 |
| --- | --- |
| Classification | 순수 PyTorch 모델 |
| Regression | 순수 PyTorch 모델 |
| Segmentation | 순수 PyTorch 모델 |
| Object Detection | 순수 PyTorch 모델 |
| Anomaly Detection | 순수 PyTorch 모델 |
| AutoEncoder | Encoder, Decoder |
| VAE | Encoder, Decoder |
| GAN | Generator, Discriminator |

### Lightning의 기준 API 구현

v0.1에서는 Lightning native 학습·검증·평가·예측을 구현하고 실제 동작을 검증한다.
독립 순수 PyTorch Predictor가 native 기능을 대체하지 않는다.
공개 호출은 Lightning과 같은 `fit()`·`validate()`·`test()`·`predict()` 형태로 맞춘다.
검증과 테스트 평가를 각각 validate와 test로 구분한다. 같은 공개 API를 제공하는 Ignite
Trainer·Factory·Engine 구현은 v0.2 또는 그 이후의 범위로 남긴다.

Task의 주요 step Hook, DataModule의 단계별 Loader 제공 방식과 평가·예측 반환 계약은
먼저 Lightning에서 검증하여 후속 Ignite의 기준으로 남긴다. 세부 반환 스키마와 복수 Optimizer 처리
규칙은 미정이다. Lightning 쪽은 native 기능을 유지하며, Ignite 쪽 Callback·Event·
분산 실행 옵션의 대응 범위는 별도로 명시한다. 독립적인 공통 Task 계층을 Lightning
Wrapper 앞에 필수로 두어 native 기능을 우회하지 않는다.

### LightningCLI와 같은 config 기반 실행

코드는 src 바로 아래에 기능별 모듈을 두며 별도의 프로젝트명 패키지를 중간에 추가하지
않는다. 루트 main.py 진입점과 기존 CLI 명령 형태는 유지하고 import·class_path를 맞춘다.

Lightning은 공식 LightningCLI의 인자 파싱·객체 생성·서브커맨드 실행 기능을 그대로
사용한다. 같은 fit·validate·test·predict 명령과 config·덮어쓰기 방식을 제공하는
Ignite CLI는 후속 버전에서 구현한다.

설정은 YAML을 기본으로 관리하고 JSON 입력도 지원하는 방향으로 맞춘다.
trainer·model·data와 optimizer·lr_scheduler, seed_everything 및 명령별 실행 인자를
설정할 수 있게 한다. Loss·Metric·transform·postprocess는 Task·DataModule 생성자 아래에
연결하며 LightningCLI에 없는 고정 최상위 섹션으로 간주하지 않는다.

config 뒤에 --model.out_dim 같은 인자를 지정하여 값을 덮어쓸 수 있고, --help와
--print_config로 허용 인자와 최종 설정을 확인할 수 있게 한다. 실제 적용 설정을 기록하여
재사용할 수 있게 한다. config의 기본값·명령줄 우선순위와 클래스 선택 방식을 Lightning에서
검증하고 후속 Ignite가 따를 기준으로 기록한다.

Ignite에서 지원하는 옵션과 native 기능의 대응은 명시한다. 공통 옵션의 의미를 유지하고
지원하지 않는 옵션은 조용히 무시하지 않는다. Lightning 전용 Callback·Strategy 객체나
체크포인트 파일이 Ignite에서 그대로 동작한다는 의미는 아니다. 구체적인 지원표와
백엔드 선택 문법, 파서 구현은 미정이다.

### 별도 순수 PyTorch Predictor

학습이 끝난 모델의 가중치를 불러와 추론하는 Predictor를 별도로 작성한다.
이 경로는 Lightning·Ignite와 해당 Task Wrapper 없이 사용할 수 있어야 한다.

기존 모델은 `forward()`로 원시 출력을 반환하는 역할을 유지한다. Predictor는 입력의
전처리, 모델 실행, 필요한 후처리를 연결하여 실제 사용할 예측값을 제공한다.
`argmax`, 이미지 역정규화 등의 처리는 모델 출력의 의미와 사용 목적에 맞게 적용한다.

native 평가·예측과 독립 Predictor는 별도의 실행 경로이며, 아래의 데이터 변환 및
후처리를 재사용한다. 구체적인 클래스명과 메서드 시그니처는 추후 설계에서 정한다.

### 기존 데이터 변환 재사용과 공통 후처리

별도의 Preprocessor를 필수로 두지 않는다. 기존 Dataset의 `transform`과
`target_transform`으로 필요한 입력·타깃 처리가 끝난다면 이를 그대로 사용한다.
Lightning·Ignite는 Dataset/DataModule을 통해 변환된 데이터를 사용한다.

필요하면 사용자가 정의한 preprocessing 함수나 Preprocessor를 선택적으로 사용할 수 있다.
Dataset의 transform·target_transform에 연결하거나, Dataset 밖의 입력·배치 처리가
필요한 위치에 연결한다. 사용자 정의 전처리를 사용하지 않는 기본 경로도 유지한다.
추가 처리인지 기존 transform을 대신하는 처리인지 명시하여 중복 적용을 방지한다.
구체적인 주입 인자와 단계별 호출 계약은 세부 설계에서 정한다.

독립 Predictor는 원시 입력을 직접 받는 경우 같은 평가·추론용 transform을 적용하고,
Dataset에서 이미 변환된 배치를 받는 경우에는 해당 변환을 다시 적용하지 않는다.
두 입력 경로를 구분하여 정규화 등의 중복 적용을 방지한다.

학습용 무작위 증강과 평가·추론용 변환은 구분한다. 이미지와 마스크·박스에 같은 공간
변환이 필요한 작업에서는 입력과 타깃을 함께 변환한다. 배치 단위 처리나 GPU 증강이
필요한 경우의 추가 처리는 선택 사항이며, 별도 전처리 계층의 필수 도입 근거로 삼지 않는다.

후처리는 Dataset과 분리하고, Lightning·Ignite의 native 평가·예측 경로와 독립
Predictor에서 재사용할 수 있는 순수 PyTorch 기반 구성요소로 둔다. 입력 transform과
후처리는 Lightning·Ignite에 의존하지 않아야 한다.

모델의 원시 출력은 유지한다. Loss에는 원시 출력 또는 Loss가 요구하는 값을 전달하고,
Metric에는 해당 지표에 필요한 변환을 적용한다. 최종 예측값을 만드는 `argmax`나
역정규화를 모든 Loss·Metric에 일괄 적용하지 않는다. 이미지 역정규화는 모델 출력이
정규화된 이미지 공간의 값인 경우처럼 출력 의미에 맞을 때 적용한다.

### DataModule 포함

v0.1에서는 기존 Dataset과 기존 DataLoader를 native LightningDataModule을 통해
연결한다. 후속 Ignite는 검증된 단계별 데이터 제공 방식을 따른다. Task를 바꾸거나
나중에 백엔드를 선택할 때 기존 데이터 구현을 다시 작성해야 하는 문제를 줄인다.

DataModule은 이번 범위에 포함한다. 단계별 데이터 제공 규칙, Dataset과 DataLoader의
입력 우선순위, 선택적인 검증 데이터 처리 등 세부 계약은 아직 확정하지 않았다.

## 이전 버전에서 아쉬웠던 것

해당 없음. v0.1이 첫 버전이며 이전 버전의 구현·검증 기록은 없다.

## 하지 않을 것

- v0.1에서는 Ignite Wrapper·Trainer·Engine·DataModule·CLI를 구현하거나 실행 검증하지 않는다.
- Lightning 검증·테스트 완료 전에 Ignite 구현을 병행하지 않는다.
- 기존 모델 및 Dataset 자체의 신규 개발은 현재 요청 범위에 포함하지 않는다.
- 참고 코드의 모든 기능을 이번 버전 필수 기능으로 확대하지 않는다. AMP, 분산학습,
  로깅, Early Stopping, 학습 재개용 체크포인트 등은 참고 자료의 제안이며 포함 여부는 미정이다.
  독립 Predictor에서 사용할 학습된 모델 가중치의 저장·복원은 포함한다.
- 독립 Predictor로 Lightning·Ignite의 native 평가·예측 기능을 대체하지 않는다.
- Ignite에서 아직 대응하지 않은 옵션이나 기능을 지원한 것처럼 처리하지 않는다.
- 공통화를 이유로 Lightning native API·CLI를 재구현하거나 지원 기능을 축소하지 않는다.
- 기존 Dataset의 변환으로 처리가 끝나는 경우에도 별도 Preprocessor 작성을 요구하지 않는다.
- 특정 객체 탐지 모델이나 이상 탐지 알고리즘을 모두 지원한다고 약속하지 않는다.
  구체적인 지원 모델과 변형 범위는 미정이다.
- 이번 문서 작성으로 프로젝트 초기화나 구현 착수를 확정하지 않는다.

## 완료 조건

다음은 v0.1 Lightning 구현의 검토용 조건이다. Task 범위와 실행 환경에 따른 상세 판정은
추가 확정해야 하며, 현재 실행 검증을 완료했다는 뜻은 아니다. Ignite의 구현·비교 검증은
후속 버전에서 수행한다.

- 이번 버전에 포함하기로 정한 Task 각각에서, 기존 모델 구성요소의 코드를 수정하지
  않고 Wrapper에 전달하여 학습·평가·추론을 실행할 수 있다.
- Lightning에서 fit·validate·test·predict를 사용할 수 있다. validate와 test의 데이터 및
  평가 상태를 구분하며 Task Hook·DataModule·반환 계약과 실행 예제를 기록한다.
- 실제 LightningCLI로 서브커맨드·config·명령줄 덮어쓰기를 실행하고 최종 설정을 확인할 수 있다.
- --help·--print_config 및 적용 설정 기록을 사용할 수 있고, 설정 출력만 요청했을 때
  학습·평가·예측이 실행되지 않는다. 지원하지 않는 옵션은 명확하게 보고된다.
- 기존 Dataset을 전달하는 경우와 기존 DataLoader를 전달하는 경우 모두 DataModule을
  통해 사용할 수 있다. Lightning의 학습·평가·추론 예제로 확인할 수 있다.
- Lightning native 평가·예측 경로를 계속 사용할 수 있다.
- Lightning 경로는 native Trainer·LightningModule·LightningDataModule·LightningCLI를
  최대한 직접 사용하고, Ignite 호환을 이유로 native 기능을 제한하지 않는다.
- 학습된 가중치를 복원한 뒤 Lightning·Ignite를 불러오지 않고 별도 Predictor로
  추론할 수 있다. 후처리가 필요한 예제로 실제 사용할 예측값이 반환되는지 확인할 수 있다.
- 기존 Dataset의 평가·추론용 transform을 독립 Predictor에서도 재사용할 수 있다.
  원시 입력 경로와 변환된 배치 경로에서 정규화 등이 중복 적용되지 않는지 확인할 수 있다.
- 같은 가중치·입력·평가용 변환·후처리 설정으로 native 예측과 독립 Predictor의 결과를
  비교할 수 있다. 확률적 동작과 수치 오차를 고려한 판정 기준은 검증 대상 확정 시 정한다.
- 후처리를 공유하면서도 Loss·Metric에 필요한 원시 출력 또는 점수 정보가 유지되는지
  확인할 수 있다.
- 위 예제에서 입력으로 사용한 기존 모델과 데이터 자산, 실행 결과를 확인할 수 있다.
- 확정한 v0.1 검증·테스트를 완료하고 결과를 기록한다. 해당 결과와 실제 API·config·
  반환 계약을 후속 Ignite 구현의 기준으로 사용할 수 있어야 한다.

## 확정이 필요한 사항

| 항목 | 현재 상태 |
| --- | --- |
| 현재 버전 | 사용자 지정 완료: v0.1, Lightning 구현·검증·테스트 |
| Ignite 착수 | 사용자 방향 확정: Lightning 검증·테스트 완료 후 v0.2 또는 그 이후. 정확한 버전은 미정 |
| 이번 버전의 Task 범위 | 미정. 전체 지원 방향은 여덟 Task이며 첫 구현 묶음은 별도 결정한다 |
| DataModule 포함 | 사용자 확인 완료 |
| native 평가·예측 유지 | 사용자 확인 완료. Lightning·Ignite의 기능을 그대로 사용한다 |
| 별도 순수 PyTorch Predictor | 사용자 확인 완료. 학습된 가중치 복원과 필요한 전처리·후처리를 연결하며 Lightning·Ignite 없이 사용한다 |
| 전처리 재사용·확장 | 기본은 Dataset의 transform·target_transform이다. 필요 시 사용자 정의 함수·Preprocessor를 선택적으로 연결할 수 있으며, 적용 위치·대체 여부를 명시해 중복을 방지한다 |
| 후처리 공유 | 순수 PyTorch 기반 후처리를 native 평가·예측과 독립 Predictor에서 재사용한다. Loss·Metric에 필요한 출력은 보존한다 |
| Wrapper·실행 기준 | 사용자 확인 완료. LightningModule·Trainer·DataModule·CLI와 학습·평가·추론을 최대한 native로 사용하고 Ignite는 같은 공개 API를 Engine으로 구현한다 |
| 내부 구조의 세부 사항 | 미정. native Wrapper 내부 상속, 공유 유틸리티와 Ignite Engine·Hook의 연결 단위를 확정해야 한다 |
| 공통 공개 API | 사용자 확인 완료. Lightning 형태의 fit·validate·test·predict, 주요 Task Hook, 단계별 Loader 및 반환 계약을 공통화한다 |
| API의 기준 | 사용자 강조 사항. Lightning native를 최대한 유지하고 Ignite가 이에 맞춘다. Lightning을 별도 공통 계층에 맞춰 축소하지 않는다 |
| Ignite 실행 계층 | 사용자 확인 완료. 프로젝트 Trainer가 내부 Factory·Engine 실행에 연결하며, 백엔드별 확장 기능을 유지한다 |
| CLI 실행 방식 | 사용자 확인 완료. Lightning은 실제 LightningCLI 사용, Ignite는 같은 config·서브커맨드·명령줄 덮어쓰기·설정 확인 방식을 구현한다 |
| CLI 세부 계약 | 미정. 파서, 진입점·백엔드 선택, 지원 옵션 대응, 클래스 선택·생성 방식, 설정 저장 위치·정책과 체크포인트 처리를 확정해야 한다 |
| 공통 API의 세부 계약 | 미정. 클래스명, 인자, Hook 반환값, 평가·예측 반환 스키마와 복수 Optimizer 처리 규칙을 확정해야 한다 |
| 독립 Predictor의 세부 계약 | 미정. 가중치 저장 형식, 모델 생성 설정, 원시 입력·변환된 배치의 API 구분, 변환 설정 및 백엔드별 연결 위치를 확정해야 한다 |
| 구체적인 지원 모델·데이터 및 실행 환경 | 미정. 검증 대상과 환경을 확정해야 한다 |
| 완료 조건 | 위 검토용 조건을 실제 버전 범위에 맞추어 확정해야 한다 |

## 참고 자료

- [주제별 기술 검토 목록](refs/README.md): 현재 요구를 기준으로 재작성한 검토 문서.
- [design-1.md](refs/drafts/design-1.md): 최초 Task Wrapper 요청과 공통 Task 계층 제안 원문.
- [design-2.md](refs/drafts/design-2.md): AE·VAE·GAN 추가 요청과 복수 모델·최적화 처리 제안 원문.
- [design-3.md](refs/drafts/design-3.md): 백엔드별 Native Wrapper와 공통 API 제안 원문.
- [design-4.md](refs/drafts/design-4.md): DataModule 추가 요청과 Dataset/DataLoader 연결 제안 원문.

기존 초안의 예제는 실행 검증하지 않았다. 주제별 문서의 공식 문서 참조는 API 검토
근거이며, 지원 버전 확정이나 구현 검증을 의미하지 않는다.
