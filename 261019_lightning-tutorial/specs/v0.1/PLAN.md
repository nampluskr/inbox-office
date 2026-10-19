# 구현 계획

## 목표와 현재 상태

순수 PyTorch와 Lightning의 분리를 유지하면서 CIFAR-10·ResNet50, MVTec·STFPM 두 예제를 구현한다. 작업 기준은 [INTENT.MD](INTENT.MD)와 [AGENTS.md](../../AGENTS.md)를 따른다.

정리 전 문서에는 2026-10-19 두 예제의 초기 구현과 짧은 실행 검증 완료가 기록되어 있었다. 사용자 수동 정리 후 모델별 CLI·공통 Lightning 연결 파일·실행 노트북과 산출물이 없는 것을 확인했다. 현재는 두 예제의 실행과 복원을 재현할 수 있는 완료 상태가 아니다. 전체 학습 성능 검증은 수행하지 않았다. 구현 결정과 참조 한계는 [DECISIONS.MD](DECISIONS.MD), 실제 파일 목록과 검증 범위는 루트 [README.md](../../README.md)에 기록한다.

아래 체크 목록에서 남아 있는 구현과 기존 확인 이력은 유지하고, 현재 없는 구성요소 및 그 구성요소가 필요한 실행 완료 항목은 미완료로 표시한다. 미완료 표시는 현재 현황을 뜻하며 삭제한 파일의 복구를 지시하는 것은 아니다. 이번 문서 갱신에서는 코드 실행과 환경 재검증을 수행하지 않았다.

## 1. 목적과 작업 기준

- [x] 사용자 의도와 PyTorch·Lightning 분리 원칙 정리
- [x] task 중심 폴더 구조와 두 예제의 참조 원본 정리
- [x] AGENTS·README·PLAN 작성
- [x] 사용자 지정 로컬 자산 위치 기록: 데이터셋 `E:\datasets`, pretrained 가중치 `E:\backbones`
- [x] Python 실행 파일 기록: `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe`

## 2. 참조 코드와 환경 확인

- [x] 기존 `dl-lightning`의 CIFAR-10·ResNet50·Wrapper·데이터 연결·CLI 코드 검토
- [x] `cv_boilerplate`의 MVTec·STFPM·loss·metric·후처리·설정 검토
- [x] anomalib STFPM의 `torch_model.py`, `lightning_model.py`, 관련 loss·anomaly map 구현과 기존 코드 비교
- [ ] 재사용할 코드의 참조 버전 또는 커밋과 라이선스 표기 기록 확인 (`references.json`·`THIRD_PARTY_NOTICES.md` 없음, 라이선스 원문은 남아 있음)
- [x] 지정 Python의 PyTorch·torchvision·Lightning·CLI 의존성과 CUDA 상태 확인
- [x] CIFAR-10·MVTec 실제 경로와 로컬 pretrained 가중치 확인

완료 기준: 재사용할 구현, 필요한 연결 변경, 사용 가능한 환경·자산을 확인하고 기록한다. 원본 알고리즘을 유지하는 부분과 프로젝트에 맞게 변경할 부분을 구분한다.

## 3. 설정과 실행 계약 구체화

- [x] `default.yaml`·데이터 YAML·모델 YAML의 내용과 결합 순서, CLI 덮어쓰기 우선순위 결정
- [x] 모델·loss·metric 주입 방식과 배치·출력 형식 결정
- [x] Dataset·DataLoader 연결과 필요한 DataModule의 배치 결정
- [x] 학습·검증 분할과 transform 적용 책임을 한 곳으로 정리
- [x] MVTec 사용 범주·분할·정상/이상 라벨·마스크 처리와 평가 지표 결정
- [x] 실행 ID, 설정·로그·metric·체크포인트·순수 모델 가중치의 저장 규칙 결정

완료 기준: 두 예제의 설정 조합과 실행 흐름을 설명할 수 있고, 데이터·모델 코드가 Lightning에 의존하지 않는 연결 방식을 정한다.

## 4. CIFAR-10 · ResNet50

- [x] `src/classification/data/cifar10/`에 기존 로컬 Dataset과 학습·평가 transform을 배치
- [x] `src/classification/models/cnn/model.py`에 순수 `ClassificationModel` 구성: custom·resnet18·resnet50·efficientnet_b0 지원, 기본값 resnet50
- [x] loss·metric·Wrapper를 `cnn/`으로 이동하고 노트북·`cnn.yaml`·기존 검증 코드 참조 갱신
- [x] 변경된 분류 노트북의 실행 횟수와 기존 출력 초기화
- [x] 필요한 loss·metric 구성과 로컬 pretrained 가중치 로딩 구현
- [x] 정리 전 ResNet50의 순수 모델 import·forward와 loss 계산 확인 이력 보존
- [ ] CNN 통합 후 모델 import·forward·가중치 복원 확인 (이번 변경에서는 실행하지 않음)
- [x] `lightning_module.py`에 학습·검증·평가·예측 Hook과 optimizer·로깅 연결
- [ ] `lightning_cli.py`와 세 종류의 YAML을 연결 (YAML만 남아 있음)
- [ ] 현재 파일 상태에서 설정 파싱·객체 생성·짧은 학습·검증·평가·예측 확인
- [ ] 현재 파일 상태에서 체크포인트 복원과 순수 모델 가중치 저장 확인

완료 기준: YAML과 CLI로 예제를 실행하고, 저장한 가중치로 결과를 복원할 수 있다. 검증 규모와 결과를 README에 기록한다.

## 5. MVTec · STFPM

- [x] `src/anomaly_detection/data/mvtec/`에 이미지·라벨·마스크 로딩과 transform 구현
- [x] `src/anomaly_detection/models/stfpm/model.py`에 순수 STFPM 모델 배치
- [x] 원본의 teacher·student 특징 추출, 학습 출력과 평가 시 anomaly map·score 계산 보존 확인
- [x] 필요한 loss·metric·후처리를 Lightning과 독립적으로 구현
- [x] teacher 고정과 student 학습 동작 확인
- [x] anomalib `lightning_model.py`를 기준으로 Wrapper의 학습·검증 흐름과 optimizer 연결
- [x] 학습·검증·평가·예측 Hook의 필요한 동작과 단계별 metric 처리 구현
- [ ] 모델별 CLI와 공통·데이터·모델 YAML 연결 (YAML만 남아 있음)
- [ ] 현재 파일 상태에서 짧은 학습·평가·예측과 가중치 복원 확인

완료 기준: 모델 알고리즘은 순수 PyTorch 파일에 유지되고 Wrapper는 Lightning 실행을 담당한다. 비교 가능한 입력과 가중치로 원본 대비 출력 형상·loss·anomaly map 동작을 확인하고, 의도적인 차이는 기록한다.

## 6. 공통 독립 추론과 유틸리티

- [x] 두 예제에서 실제로 공유하는 설정·파일 처리를 `src/utils/`로 구성
- [x] `src/inference/predictor.py`에 모델·전처리·후처리 주입 방식 구현
- [ ] Lightning 체크포인트에서 순수 모델 `state_dict`를 내보내는 연결 구현 (공통 CLI 파일 없음)
- [ ] 현재 파일 상태에서 두 모델의 순수 가중치 복원과 추론 확인 (기존 가중치 산출물 없음)
- [x] Lightning import를 차단한 별도 프로세스 등으로 순수 모델·데이터·Predictor의 독립성 확인
- [x] 원시 입력과 이미 변환된 입력에서 transform 중복 적용 여부 확인

완료 기준: 공통 Predictor가 task별 클래스·LightningModule·Trainer를 참조하지 않고 두 모델을 실행한다. 단순히 파일만 나뉜 상태를 넘어 Lightning 없이 사용할 수 있음을 확인한다.

## 7. 예제 사용 안내와 결과 기록

- [x] 검증한 환경·패키지 버전과 데이터·가중치 준비 방법 기록
- [ ] 현재 파일 상태에서 사용할 수 있는 학습·검증·평가·예측·독립 추론 명령 기록
- [ ] 현재 실행 연결에 맞는 산출물과 복원 방법 안내
- [x] 의미 있는 동작 검증을 정리하고 미검증 범위·제한 사항 기록
- [x] README·intent·AGENTS·PLAN의 구조·원칙·구현 상태 일치 확인
- [x] Markdown UTF-8과 한글 정상 저장 확인

완료 기준: 문서에 안내한 실행 방법으로 두 예제의 실행과 복원을 재현할 수 있고, 수행한 검증과 남은 제약을 확인할 수 있다.

## 정리 전 실행 확인 기록

아래는 기존 문서에 남아 있던 실행 이력이다. 현재 `notebooks/`와 `outputs/`는 비어 있어 해당 노트북·가중치·보고서로 결과를 재확인할 수 없다. 이번 수동 정리 후 실행 결과로 해석하지 않는다.

- 지정 Python·로컬 데이터·가중치와 CUDA를 확인했으며 패키지는 변경하지 않았다.
- CIFAR-10·ResNet50: batch size 2, 학습 2배치·1 epoch, 검증·평가·예측 각 2배치를 실행했다.
- MVTec bottle·STFPM: batch size 2, 학습 2배치·1 epoch, 검증 33개·평가 50개, 예측 2배치를 실행했다.
- `tests/test_examples.py`: 8개 테스트 통과. teacher 고정·student 갱신, 참조 수식, split·mask, 가중치 내보내기·복원, 독립 추론과 전처리 중복 방지를 확인했다.
- `notebooks/cifar10_resnet50.ipynb`, `notebooks/mvtec_stfpm.ipynb`: 각 7개 코드 셀을 순서대로 실행한 기록이 있었다. 당시 보고서 경로는 `outputs/notebook_verification.json`이며 현재 해당 파일들은 없다.
- 기존 학습 폴더로 fit 실행을 거부하고 설정·CSV가 유지되는 것을 확인했다.
- Markdown·노트북의 UTF-8과 한글, 문서 링크와 Python 코드 문법을 확인했다.

참조 버전은 anomalib의 확인한 `main` URL과 검토 날짜, 로컬 원본 SHA-256으로 기록한 이력이 있으나 현재 `references.json`은 없다. 원격 고정 커밋 확보와 전체 anomalib 런타임 대비 수치 동등성 검증은 수행하지 않았다. Jupyter 화면 렌더링, 다중 장치와 다른 MVTec 범주는 검증 범위 밖이다.
