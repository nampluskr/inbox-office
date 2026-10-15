> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# Dataset, DataModule과 transform

## 확정된 요구

기존 Dataset와 DataLoader를 DataModule로 연결한다. Dataset의 `transform`과
`target_transform`을 재사용하며 별도 Preprocessor를 필수로 두지 않는다.
평가·추론용 변환은 native 실행과 독립 Predictor에서 재사용하고 중복 적용하지 않는다.
기본 전처리는 Dataset에서 수행하되, 필요하면 사용자 정의 preprocessing 함수나
Preprocessor를 선택적으로 연결할 수 있어야 한다.

## 검토 제안: 책임과 적용 위치

| 처리 | 기본 위치 후보 | 주의할 점 |
| --- | --- | --- |
| 샘플 로딩, 입력 변환 | Dataset | 제공받은 Dataset의 기존 동작을 확인 |
| 타깃 변환 | Dataset의 target_transform 또는 기존 코드 | 추론 시 정답이 있다고 가정하지 않음 |
| 입력·타깃의 동기화된 공간 변환 | 기존 Dataset의 공동 변환 | 무작위 파라미터를 함께 적용 |
| 배치 구성 | DataLoader·collate_fn | 가변 크기와 타깃 개수 보존 |
| 단계별 Loader 제공 | DataModule | Dataset·Loader 자체를 임의 변경하지 않음 |
| 선택적 배치 처리·GPU 증강 | 백엔드 Hook/step | Dataset 변환과 중복되지 않게 명시 |

PyTorch Dataset 전체가 transform 인자를 갖는 것은 아니다. transform과 target_transform은
기존 Dataset이 제공하는 인터페이스를 재사용한다는 의미다. 제공되지 않는 경우에도
모든 Dataset을 같은 생성자로 다시 작성하도록 강제하지 않는 방향을 제안한다.

## 선택적 사용자 정의 전처리

사용자 정의 함수나 객체를 Dataset의 transform·target_transform으로 제공하는 것이
기본 확장 경로다. 입력과 타깃을 함께 바꾸는 경우에는 공동 변환을 사용한다.

Dataset 밖의 배치 처리·GPU 처리나 원시 입력 변환이 필요한 경우에는 별도 사용자 정의
전처리를 실행 위치에 맞게 연결할 수 있다. Lightning은 native Hook/step, Ignite는
배치 준비/Engine step, 독립 Predictor는 모델 실행 전 경로에 연결하는 방안을 검토한다.
공통 변환 코드 자체는 Lightning·Ignite에 의존하지 않는다.

사용자 정의 처리가 기존 transform의 대체인지 추가 단계인지, 적용 단계와 처리한 입력
상태를 명시해야 한다. 이미 변환된 배치에는 같은 샘플 변환을 다시 적용하지 않으며,
별도로 지정한 배치 처리는 그 계약에 따라 수행한다. 사용자 정의 전처리 미지정 시에는
기존 Dataset 변환과 입력 경로만으로 실행할 수 있어야 한다.

주입 인자의 이름, callable/객체 인터페이스, 메타데이터 전달과 단계별 활성화 방식은 미정이다.
별도 Preprocessor 기반 클래스의 상속을 필수로 요구하지 않는 방향을 제안한다.

## DataModule 계약 후보

Lightning에서는 native LightningDataModule을 최대한 그대로 사용하고, Ignite에서는
같은 단계별 Loader API를 제공하는 프로젝트 클래스를 구현한다. Lightning은 prepare_data·setup과 단계별 Loader
메서드로 데이터를 구성한다. [공식 DataModule 안내](https://api.lightning.ai/docs/pytorch/stable/data/datamodule)

| 단계 | 제공할 데이터 | 논의할 정책 |
| --- | --- | --- |
| fit | train, 선택적 validation | validation 미제공 시 동작 |
| validate | validation | 공통 validate 호출로 제공하며 test 상태와 구분 |
| test | test | validation과 평가 데이터 구분 |
| predict | 정답 없이도 사용 가능한 입력 | 타깃 포함 배치도 입력만 추출 |

Dataset을 받으면 Loader를 구성하고, Loader를 받으면 기존 sampler·collate 설정을
보존하는 방안을 제안한다. 같은 단계에 Dataset과 Loader를 모두 제공했을 때 오류로
처리할지 우선순위를 둘지는 미정이다. prepare_data/setup/teardown의 반복 호출과
예외 처리, 분산 환경의 호출 정책도 구현 전에 정해야 한다.

## 독립 Predictor의 두 입력 경로

| 입력 | 처리 |
| --- | --- |
| 원시 입력 | 평가·추론용 입력 transform 적용 후 배치 구성 |
| 이미 변환된 배치 | 입력 transform 재적용 없이 모델 실행 |

Dataset에서 처리한 입력인지 Tensor 타입만 보고 추측하지 않는다. Tensor도 변환 전
입력일 수 있다. 별도 메서드나 명시적인 입력 옵션으로 경로를 구분하는 방안을 제안한다.
구체적인 API 이름은 [09](09-client-api-and-examples.md)의 후보를 검토한다.

학습용 무작위 증강을 독립 추론에 자동 적용하지 않는다. 회귀의 target_transform으로
사용한 통계·단위와 출력 역변환은 [04](04-outputs-and-postprocessing.md)의 후처리와
연결해야 한다. 역변환 함수를 일반 callable에서 자동으로 추론할 수 있다고 가정하지 않는다.

## 메타데이터

원본 크기, resize 비율, padding, 샘플 ID가 필요한 경우 Dataset/배치에서 후처리까지
전달하는 방안을 검토한다. 이를 위해 별도 Preprocessor 클래스가 반드시 필요한 것은 아니다.

## 미정

메타데이터 구조, 지원 batch 형태, 설정 저장 방식, 분산 sampler 정책은 미정이다.

근거: [데이터 초안](drafts/design-4.md), [BRIEF](../BRIEF.md).
