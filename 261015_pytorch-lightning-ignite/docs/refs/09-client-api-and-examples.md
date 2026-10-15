> 대상 버전: v0.1(Lightning 기준, Ignite는 후속 검토) · 작성일: 2026-10-15 · 상태: 기술 검토 초안

# 클라이언트 API와 사용 예제

## 확정된 요구

Task와 데이터 자산을 공통된 방식으로 연결하되, Lightning·Ignite의 native 평가·예측을
유지한다. 독립 Predictor는 별도 경로이며 transform과 후처리를 재사용한다.
공개 메서드는 Lightning 형태의 fit·validate·test·predict로 맞춘다. Ignite는 프로젝트
Trainer가 내부 Engine 실행에 연결한다. 주요 Task Hook, 단계별 Loader 제공 방식과
평가·예측 반환 계약을 공통화한다. 클래스명·세부 인자·반환 스키마는 미정이다.

이 프로젝트는 Lightning의 Wrapper·Trainer·학습·평가·추론을 최대한 native로 사용하고,
Ignite가 같은 공개 API로 동작하도록 Engine 기반으로 구현한다. 공통 API를 위해
Lightning의 native 옵션·반환·확장 기능을 별도 최소 기능 계층으로 축소하지 않는다.

명령줄에서는 실제 LightningCLI를 사용하고 Ignite는 같은 설정·실행 방식을 구현한다.
config 파일과 --xxx 덮어쓰기, 설정 확인 예제는 [11](11-cli-and-config.md)에 정리한다.

## 공통화 범위

| 공통화할 내용 | native 특성을 유지할 내용 |
| --- | --- |
| Task 이름과 모델 구성요소 지정 | Trainer·Engine 실행 객체 |
| fit·validate·test·predict 호출 형태 | native 실행 루프와 최적화 기능 |
| 주요 Task step Hook | 백엔드별 최적화 API |
| Dataset/Loader를 DataModule로 연결하는 사용 방식 | lifecycle과 장치·정밀도 처리 |
| 평가용 transform·후처리와 공개 반환 계약 | 내부 native 결과·State 객체 |
| 추론용 가중치 내보내기와 복원 | Callback·Event·Handler 확장 |

공개 Trainer는 내부에서 독립 Predictor를 호출하여 native 예측을 대체하지 않는다.
검증은 validate, 테스트 평가는 test로 구분한다. Lightning 쪽은 native Trainer를 사용하고,
IgniteTrainer는 프로젝트 클래스명 후보다. Ignite에서 Lightning 전체 기능을 복제하는
것은 목표가 아니며, Lightning 쪽의 CLI 기능은 공식 구현을 그대로 사용한다.

## 주요 Hook과 반환 계약

공통 Task Hook 이름과 역할은 다음과 같이 정리한다. 아래 인자 표기는 검토 후보이며
전체 Lightning Hook 시그니처의 호환을 확정하는 것은 아니다.

| Hook 후보 | 공통 역할 | 추가로 정할 것 |
| --- | --- | --- |
| training_step(batch, batch_idx) | 학습 Loss 등 계산 | 반환 형식, backward·Optimizer 책임 |
| validation_step(batch, batch_idx) | 검증 처리 | Metric 상태 관리와 반환 규칙 |
| test_step(batch, batch_idx) | 테스트 평가 처리 | 검증 상태와 분리 방식 |
| predict_step(batch, batch_idx) | 공통 후처리를 적용한 예측 | 샘플·배치 단위와 메타데이터 |
| configure_optimizers() | Optimizer·Scheduler 구성 제공 | 복수 Optimizer·업데이트 정책 |

단일 Optimizer의 Loss 반환과 실행 계층 업데이트를 기준 후보로 검토하되 GAN의
최적화 계약은 별도로 정한다. 공통 Hook을 위해 모델 forward 자체를 변경하지 않는다.

평가 결과는 지표 이름과 값, 예측 결과는 Task별 필드·순서·배치 묶음·반환 장치를
공통 계약으로 명시해야 한다. 지원 버전의 Lightning native 반환을 기준으로 Ignite가
맞추며 정확한 스키마·옵션 대응은 미정이다. Ignite Engine State는 Ignite 연결 계층에서
해석한다. Lightning native의 반환 형식을 별도 공통 형식으로 바꾸도록 요구하지 않는다.

## 예제 표기

v0.1에서 구현·실행 검증할 예제는 Lightning과 공통 순수 PyTorch 코드·독립 Predictor
경로다. Ignite 분기와 내부 실행 예제는 v0.2 또는 그 이후의 목표 사용 형태이며
v0.1에서 실행 가능해야 하는 API로 간주하지 않는다.

아래 코드는 사용 흐름을 설명하는 의사 코드다. 모델·Dataset은 기존 사용자 자산이며,
build_task·build_datamodule·IgniteTrainer·Predictor·export_for_inference는
이 프로젝트의 API 후보다. fit·validate·test·predict 호출 형태는 반영된 사용자 방향이다.
현재 설치·실행 가능한 패키지나 확정된 시그니처가 아니다.

### 기존 데이터와 모델 연결

```python
model = MyModel(...)                         # 기존 nn.Module
eval_transform = make_eval_transform(...)    # 기존 평가용 변환
postprocess = ClassificationPostprocess(...) # 공통 후처리 후보

# test_dataset에는 이미 eval_transform이 연결되어 있다고 가정
dm = build_datamodule(
    backend=backend,
    train_dataset=train_dataset,
    val_dataset=val_dataset,
    test_dataset=test_dataset,
    predict_dataset=predict_dataset,
)
task = build_task(
    backend=backend,
    task="classification",
    model=model,
    loss_fn=loss_fn,
    optimizer_factory=optimizer_factory,
    postprocess=postprocess,
)
```

이미 DataLoader가 있다면 같은 역할의 Loader 입력 경로를 사용한다. Dataset·Loader
중복 제공과 누락 단계 정책은 [03](03-data-and-transforms.md)에서 결정해야 한다.

### 공통 공개 API

```python
# backend에 맞는 task와 dm을 위에서 구성했다고 가정
if backend == "lightning":
    from lightning.pytorch import Trainer
    trainer = Trainer(max_epochs=10)
else:
    trainer = IgniteTrainer(max_epochs=10)  # 프로젝트 클래스 후보
trainer.fit(task, datamodule=dm)
validation_metrics = trainer.validate(task, datamodule=dm)
metrics = trainer.test(task, datamodule=dm)
predictions = trainer.predict(task, datamodule=dm)
```

공통 후처리는 task.predict_step에 연결한다. 양쪽 Trainer의 공개 호출 형태를 맞추고,
Lightning 쪽은 native Trainer를 사용한다. validate는 validation 데이터를, test는
test 데이터를 사용한다. native 호출 형태는
[DataModule 공식 안내](https://api.lightning.ai/docs/pytorch/stable/data/datamodule)를 참고했다.

위 코드는 Python API 사용 흐름이다. 실제 패키지에서는 백엔드별 import를 분리한다.
LightningCLI 실행 모드에서는 CLI가 객체를 생성하고 명령까지 실행하므로 위 호출을
추가로 실행하지 않는다. Ignite CLI도 같은 사용자 흐름으로 한 번만 명령을 실행한다.

### Ignite Trainer의 내부 실행 대응

```python
# 사용자 코드가 아닌 IgniteTrainer 내부 동작을 설명하는 의사 코드
# 각 메서드는 해당 단계의 setup/teardown과 상태 초기화를 함께 관리
# fit:
task.trainer.run(dm.train_dataloader(), max_epochs=epochs)
# validate:
task.evaluator.run(dm.val_dataloader())
# test:
task.evaluator.run(dm.test_dataloader())
# predict:
task.predictor_engine.run(dm.predict_dataloader())
```

trainer/evaluator/predictor_engine 속성명은 후보이며 validate/test 상태 분리와 반환 결과
수집 방식의 세부 구현은 미정이다. 사용자에게 Engine.run 직접 호출을 필수로 요구하지 않는다.
predictor_engine은 프로젝트가 구성하는 Ignite Engine이다. 독립 PyTorch Predictor와
구분하며, Engine.run의 이벤트 실행 모델은 [공식 안내](https://docs.pytorch.org/ignite/engine.html)를 따른다.

### 저장 후 독립 추론

```python
export_for_inference(task, destination=artifact_path)  # 후보 API

# 별도 프로세스: Lightning/Ignite 없이 실행
model = MyModel(...)
model.load_state_dict(load_weights(artifact_path))    # 후보 로더
predictor = Predictor(
    model=model,
    transform=eval_transform,
    postprocess=postprocess,
)
prediction = predictor.predict(raw_input)            # transform 적용
predictions = predictor.predict_batch(prepared_x)    # transform 생략
```

Task별 모델 조합과 메타데이터 복원은 [07](07-pure-pytorch-predictor.md)·
[08](08-weights-and-checkpoints.md)에서 검토한다. 위 단일 모델 예제를 VAE/GAN의
전체 복원 계약으로 사용하지 않는다.

## 미정

Ignite 클래스명, Factory 도입 여부, native 객체 접근 경로, Ignite 대응 옵션, Hook 반환값과
최적화 책임, 평가·예측 반환 스키마, 예측 수집·장치 정책, 원시 입력과 준비된 배치 타입,
다중 모델 주입 형식은 미정이다. 세부 계약이 확정되면 이번 버전 범위에 맞는 예제를 작성한다.
