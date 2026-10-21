# Classification 진행 상태

공통 경로 설정의 backbones를 datasets와 같은 flat 문자열 매핑으로 변경했다. paths.example.toml·공통 조회 함수·사용 문서를 함께 반영했다. TOML 문법·문자열 형식은 정적으로 확인했으며 변경 후 classification 가중치 로드·학습은 실행하지 않았다.

문서 정리 기준일은 2026-10-21이다. 구현 계약은 [SPEC.md](SPEC.md), 실행 명령은 [USAGE.md](USAGE.md)를 따른다. 구현 완료와 실행 확인을 구별하며 아래 이력을 최신 변경 전체의 검증 결과로 확대하지 않는다.

## 현재 구현

| 항목 | 구현 상태 | 확인 범위 |
|---|---|---|
| MNIST Dataset·Transform·MLP 경로 | 구현 | 초기 경로 사용자 학습·best 테스트 확인 |
| CIFAR-10 Dataset·Transform·CNN 경로 | 구현 | 이전 구조 실행 이력·산출물 존재 확인, 최신 변경 전체 재실행 미확인 |
| task Trainer·CLI·네 YAML | 구현 | 명세·코드 정리와 정적 확인, 최신 모든 조합 실행 미확인 |
| Wrapper 내부 객체 생성·공통 metric/후처리 | 구현 | 정적 확인, 변경 후 전체 실행·복원 미확인 |
| 저장 함수 공유·Trainer YAML 중복 제거 | 구현 | 문법·설정·호출 순서 정적 확인 |
| 순수 가중치·공통 Predictor 연결 | 구현 | 예제 저장 코드·출력 계약 확인, 최신 조합별 추론 미검증 |
| 기존 노트북 이식 | 미완료 | 이전 import가 남아 있음 |

## 확인된 실행 근거

### MNIST·MLP 사용자 실행

초기 MNIST 경로의 사용자 터미널 실행에서 5 epoch 학습과 best checkpoint 테스트 완료가 보고됐다.

| 지표 | 보고된 값 |
|---|---|
| test loss | 0.0799202 |
| test accuracy | 0.9767000 |
| test macro F1 | 0.9766263 |

에이전트가 별도로 실행한 결과가 아니다. 이후 Wrapper 생성자·CLI·후처리·저장 함수 변경 전체를 재검증한 결과로 간주하지 않는다.

### 산출물 확인

기존 outputs에서 MNIST·MLP, MNIST·custom CNN, CIFAR-10·ResNet18의 test_metrics.json이 확인된 이력이 있다. 산출물 존재는 현재 코드로 모든 조합을 재실행했다는 뜻이 아니다. 과거 출력의 test_accuracy 키와 현재 test_acc 키도 구별한다.

## 변경·수정 이력

- MNIST NumPy 이미지에 채널 축을 추가해 torchvision 0.17 ToImage의 축 변환 오류를 수정했다.
- CSVLogger를 먼저 초기화한 뒤 config.yaml을 저장하도록 순서를 변경했다. 사용자 재실행에서 로그 폴더 경고와 Tensor Cores 안내가 사라지고 학습·테스트가 완료된 것이 보고됐다.
- 예제·CLI에서 float32 matmul precision을 high로 지정했다. 내부 정밀도·성능에 영향을 주므로 이전 실행과 동일한 수치를 보장하지 않는다.
- worker 부족 성능 경고 필터와 tqdm 재활성화는 후속 변경 시 실행 검증하지 않았다.
- CIFAR-10 Dataset·Transform을 dataset.py에 모으고 DataModule·Wrapper 이름을 v0.2 규칙으로 변경했다. 과거 클래스 별칭과 노트북은 이식하지 않았다.
- CNN YAML을 cnn.yaml 하나로 모으고 예제별 입력 채널·backbone·logger를 직접 변경하도록 정리했다.
- task CLI에 data/model 선택·selection 저장·조합별 기본값·입력 검사를 추가했다.
- 가공한 터미널 args의 native 파싱으로 args/sys.argv 중복 전달 경고를 수정했다. 전역 argv 변경·경고 필터는 추가하지 않았고 당시 실행 테스트는 하지 않았다.
- Wrapper는 설정값으로 내부 객체를 생성하며 predict_step에서 공통 후처리를 적용하도록 변경했다.
- 예제의 설정·평가 JSON·순수 가중치 저장을 함수 두 개로 공유하고 Trainer YAML 중복을 제거했다. 당시 문법·설정·인코딩 정적 확인을 수행했다.
- MLP·CNN의 valid loss·acc·F1을 progress bar에서 제외했다. MetricsPrinter를 train epoch 종료 시 현재 train_loss와 실행된 valid 지표를 출력하도록 변경했다. 변경 후 학습은 실행하지 않았다.

## 실행 환경과 이전 기록

프로젝트 작업 시 지정 Python은 C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe, 작업 폴더는 D:\projects\lightning-tutorial이다. 로컬 데이터·가중치는 paths.toml로 연결한다. 실행·패키지 명령은 [루트 작업 지침](../../../AGENTS.md)의 RTK 규칙을 따른다.

공유 Python 환경의 2026-10-21 패키지 확인·timm 설치 기록은 [anomaly 진행 상태](../anomaly_detection/PROGRESS.md)에 둔다. 과거 Python 3.11.8·CUDA 환경의 CIFAR-10 제한 배치 학습, YAML 객체 주입·노트북 검증은 [v0.1 PLAN](../../v0.1/PLAN.MD)·[결정 기록](../../v0.1/DECISIONS.MD)에 보존한다.

## 남은 확인

- [ ] 현재 CLI의 모든 data/model 조합·YAML/명령행 우선순위·저장 설정 재사용 확인
- [ ] 최신 Wrapper의 import·forward·제한 배치 fit/validate/test/predict 확인
- [ ] best checkpoint·순수 model.pt 복원과 예측 일치 확인
- [ ] Lightning import 차단 상태의 최신 순수 모델·데이터·독립 추론 확인
- [ ] MNIST torchvision backbone의 3채널 복제와 입력 검사 실행 확인
- [ ] 문서 명령의 사용자 환경 재현과 기존 노트북 이식
- [ ] epoch별 train_loss·valid 지표 출력과 CSV·checkpoint 기준 유지 확인

이번 문서 재구성에서는 코드·패키지를 변경하거나 모델·학습·평가 테스트를 실행하지 않는다. 문서 링크·UTF-8·한글 본문·코드 예시 문법을 정적으로 확인한다.
