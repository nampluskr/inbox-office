# v0.2 공통 설계 결정

현재 계약은 [SPEC.md](SPEC.md), 목적은 [INTENT.md](INTENT.md)에 둔다. 이 문서는 공통 선택의 이유와 호환성 영향을 기록한다.

## Task별 실행 구성

모델별 CLI 대신 task의 trainers에 Trainer와 CLI를 둔다. 데이터·모델을 바꾸면서 같은 실행 패턴을 유지하기 위한 선택이다. 루트 진입점과 별도 engine을 추가하지 않고 native Lightning subcommand를 사용한다. 이전 모델별 CLI·공통 Lightning 연결 경로를 위한 호환 별칭은 제공하지 않는다.

## 설정값으로 Wrapper 구성

Wrapper는 모델·loss·metric 객체나 전처리·후처리 함수를 주입받는 대신 필요한 설정값을 받아 내부 생성한다. YAML과 checkpoint에 재현 가능한 생성자 설정을 저장하려는 목적이다. 단일 구현을 위한 미리 준비된 registry나 선택 인자는 추가하지 않는다. 순수 모델과 공통 Predictor는 독립적인 사용 계약을 유지한다.

## 선택 정보 분리

CLI는 data/model을 먼저 선택하고 해당 클래스와 기본 YAML을 연결한다. 선택값은 별도 selection에 저장한다. 생성자 설정에 선택용 키를 섞거나 파싱 후 삭제·복원하는 방식을 피하기 위한 결정이다. 선택 처리 후 객체 생성·설정 저장은 LightningCLI가 담당한다.

사용자 YAML의 위치와 무관하게 명령행 인자가 우선하도록 인자를 정리한다. 터미널에서 가공한 인자를 native parser에 직접 전달해 args와 sys.argv 중복 전달 경고를 방지한다. 전역 sys.argv 수정과 경고 필터로 해결하지 않는다.

## Logger와 callback 고정

클래스 선택은 Python, 인자는 trainer YAML에 둔다. 예제에서 일관된 CSV·checkpoint·지표 출력을 제공하고 동적 import 구성을 줄이려는 결정이다. CLI의 설정 저장 callback은 추가로 수용한다. task 간 차이는 각 Trainer 안에 유지하고 현재 규모에서 새 공통 실행 추상화는 만들지 않는다.

## 로컬 자산과 독립 추론

컴퓨터별 데이터·가중치 경로는 TOML에 모으고 명시적 경로를 우선한다. 자동 다운로드와 누락 가중치의 조용한 무작위 대체를 방지한다. 필요한 경로만 확인하며 실제 로컬 설정은 Git에서 제외한다.

datasets와 backbones는 같은 `이름 = 경로 문자열` 형식을 사용한다. backbone마다 weights_path 하위 테이블을 반복하지 않는다. classification의 기존 weights_path 인자는 유지하며 anomaly_detection 모델에서는 원본 생성자에 맞춰 제거하고 get_backbone_dir로 조회한다.

독립 추론용 파일은 Wrapper 전체 checkpoint 대신 순수 모델의 state_dict로 저장한다. 전처리와 Tiler 같은 파라미터 없는 설정은 함께 저장한 YAML로 재구성한다. Predictor에 task별 분기를 추가하지 않는다.

## 문서 분리

루트 README는 프로젝트 소개·준비·빠른 시작·문서 링크에 집중한다. 공통 SPEC에는 계약을, task SPEC에는 차이를, DECISIONS에는 이유를 기록한다. 구현·검증·수정 이력은 task PROGRESS, 실행 예시는 task USAGE에 둔다. 공통 진행 문서는 중복 작성하지 않는다.

[Classification 결정](classification/DECISIONS.md), [anomaly detection 결정](anomaly_detection/DECISIONS.md), [v0.1 기록](../v0.1/DECISIONS.MD)을 참조한다.
