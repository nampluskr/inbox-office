# v0.2 공통 기획 의도

## 목적

모델 알고리즘·데이터 처리·독립 추론을 순수 PyTorch로 유지하면서, 학습 실행은 native Lightning으로 구성한다. 데이터셋과 모델이 달라도 같은 위치에서 설정과 실행 코드를 찾을 수 있게 한다.

## 설계 원칙

- 순수 모델은 구조·연산·입출력을 담당하고 Lightning Wrapper는 Hook·optimizer·단계별 지표를 연결한다.
- Wrapper는 설정값을 받아 필요한 객체를 내부 생성한다. 실제 선택지가 생겼을 때 문자열 선택 인자를 추가한다.
- Dataset·Transform·loss·metric·Predictor는 Lightning 없이 사용할 수 있게 한다.
- 학습 루프와 subcommand는 Lightning의 기본 동작을 사용한다. 불필요한 engine·registry·factory를 추가하지 않는다.
- 공통 구현은 실제로 공유하는 범위에만 둔다.
- 데이터·pretrained 가중치는 로컬 자산을 사용하며 자동 다운로드하지 않는다.
- 구현 여부와 실행 검증 여부를 구별한다. 이전 결과를 변경된 코드의 검증 결과로 간주하지 않는다.

## 범위

v0.2는 task별 `configs/data/models/trainers` 구조와 설정·실행 흐름을 통일한다. 모델별 연산의 세부 계약은 task 명세가 담당한다.

[Classification 목적](classification/INTENT.md), [anomaly detection 목적](anomaly_detection/INTENT.md)을 따른다. 별도 binary classification task와 추가 데이터셋·모델은 후속 요청에서 구체화한다.

## 문서 역할

| 문서 | 책임 |
|---|---|
| 루트 README | 외부 사용자에게 프로젝트 소개·준비·빠른 시작 제공 |
| INTENT | 목적·범위·설계 원칙 |
| SPEC | 현재 구조·설정·입출력 계약 |
| DECISIONS | 선택 이유·대안·호환성·참조 근거 |
| task PROGRESS | 구현 상태·검증 근거·미검증 범위·남은 작업 |
| task USAGE | 데이터 준비·실행·설정·복원·문제 해결 |

공통 규칙은 [SPEC.md](SPEC.md), 공통 결정은 [DECISIONS.md](DECISIONS.md)에 기록한다. task 문서는 공통 규칙을 링크하고 차이를 기술한다. 진행 상태는 task별로만 관리한다. v0.1 기록은 [이전 문서](../v0.1/DECISIONS.MD)에 남긴다.
