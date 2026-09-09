# task-runner

## 무엇을 하는가

외부 프로젝트가 소유한 task별 dataset, dataloader와 model을 adapter로 연결하여, 서로 다른 task와 backend에 공통으로 적용할 수 있는 train, evaluate, predict와 batch 실행 engine을 제공한다.

## 왜 하는가

기존 `cv-batch-runner` 기획을 통해 실행 구조를 task에 의존하는 부분과 task가 달라져도 변하지 않는 부분으로 분리할 필요를 확인했다. task와 backend마다 실행 코드를 다시 만드는 대신, 공통 계약과 engine을 한 번 정의하고 외부 구현을 연결하여 재사용하고자 한다. 또한 구조를 CV와 PyTorch에 고정하지 않고 새로운 backend로 확장할 수 있게 한다.

## 변하지 않는 원칙

- task 의존 레이어와 task 불변 실행 레이어를 분리한다.
- task 프로젝트가 자신의 dataset, dataloader, model과 task별 동작을 소유한다.
- model은 공통 실행 framework에 결합되지 않은 순수 backend model로 유지한다.
- adapter가 외부 task 구현과 공통 실행 계약을 연결한다.
- backend 고유의 실행 방식은 backend 확장 지점 뒤에 격리한다.
- train, evaluate와 predict는 task와 backend에 관계없이 같은 상위 job 개념을 사용한다.
- batch의 각 job은 독립된 단일 job 실행에 대응한다.
- job 실행과 상태 관리는 AI agent의 판단이나 개입 없이 결정론적으로 동작한다.

## 다루지 않는 것

- 개별 task의 dataset 구축과 제공
- 개별 task의 model과 알고리즘 개발
- model을 특정 실행 framework의 전용 기반 클래스에 종속시키는 방식
- 모든 backend에 PyTorch의 실행 방식을 강제하는 방식
- AI agent가 job을 선택하거나 실행 결과를 판단하는 방식
- 최종 사용자 인터페이스 기술을 미리 확정하는 일
