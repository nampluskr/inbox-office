# 실행 framework 구조 비교

## 목적

`cv_boilerplate`와 대표적인 학습 framework의 data source, parameter 갱신과 hook 책임을 비교하여 공통 engine과 task adapter의 경계를 정하는 근거로 사용한다.

## cv_boilerplate

`cv_boilerplate`는 CLI가 model, adapter, dataset, dataloader, optimizer와 scheduler를 생성하여 `Trainer.fit`에 전달한다. Trainer는 dataloader 순회뿐 아니라 device 이동, AMP, backward, gradient clipping, optimizer와 scheduler step, checkpoint 저장까지 수행한다. adapter의 `train_step`은 forward와 loss 계산 결과를 반환한다.

이 구조는 task별 batch 처리 차이를 adapter로 분리하지만 engine이 PyTorch 학습 protocol과 optimizer를 직접 아는 구조다. 따라서 새 프로젝트에서는 참고 구현으로 사용하되 engine과 task의 책임 경계는 그대로 계승하지 않는다.

## Lightning

Lightning은 task 또는 DataModule이 `train_dataloader`, `val_dataloader`, `test_dataloader`, `predict_dataloader`를 정의하고 Trainer가 반환된 iterable을 순회한다. task가 `configure_optimizers`에서 optimizer를 정의하지만 automatic optimization에서는 Trainer가 backward와 optimizer step을 실행한다. manual optimization에서는 task의 `training_step`이 갱신을 직접 수행할 수 있다.

- [LightningDataModule](https://lightning.ai/docs/pytorch/stable/data/datamodule.html)
- [Trainer](https://api.lightning.ai/docs/pytorch/stable/common/trainer.html)
- [Manual Optimization](https://lightning.ai/docs/pytorch/stable/model/manual_optimization.html)

새 프로젝트는 lifecycle과 data 제공 방식은 Lightning을 참고하고, parameter 갱신 책임은 manual optimization 방식에 가깝게 둔다. 다만 model에 framework 전용 기반 클래스 상속을 요구하지 않고 별도 adapter가 계약을 구현한다.

## Keras

Keras `fit`은 array, backend tensor, Dataset, DataLoader와 generator 같은 data source를 받아 순회한다. custom `train_step`에서는 forward, gradient 계산, optimizer 적용과 metric 갱신을 직접 구현할 수 있으며 evaluation은 `test_step`으로 확장한다.

- [Model training APIs](https://keras.io/api/models/model_training_apis/)
- [Customizing fit with train_step](https://keras.io/guides/custom_train_step_in_tensorflow/)

parameter 갱신을 step 구현이 소유한다는 점은 새 프로젝트와 유사하다. Keras는 이 계약을 `keras.Model` subclass에 두지만 새 프로젝트는 순수 backend model과 adapter를 분리한다.

## Hugging Face Trainer

Hugging Face Trainer는 dataset으로부터 dataloader를 구성하고 optimizer, scheduler, device 배치와 분산 실행을 강하게 관리한다. 확장 method를 제공하지만 PyTorch와 Transformers에 최적화된 engine 중심 구조다.

- [Hugging Face Trainer](https://huggingface.co/docs/transformers/main_classes/trainer)

backend 중립성과 task의 parameter 갱신 소유권을 우선하는 새 프로젝트에는 직접적인 구조 기준으로 사용하지 않는다.

## Ignite

Ignite Engine은 `run`에 전달된 iterable을 순회하고 각 batch를 사용자 `process_function`에 전달한다. forward, backward와 optimizer step은 process function이 결정할 수 있으며 lifecycle 확장은 event handler로 연결한다.

- [PyTorch-Ignite Engine](https://docs.pytorch.org/ignite/generated/ignite.engine.engine.Engine.html)

engine이 iterable 순회와 lifecycle을 관리하고 task 함수가 실제 step 동작을 담당한다는 책임 경계가 새 프로젝트와 가장 가깝다.

## 적용 결론

- task가 data(dataset과 dataloader를 포함한 구체 data source)를 생성하고 소유한다.
- adapter는 `train`, `validate`, `evaluate`, `predict`의 data source를 반환한다.
- engine은 data source를 iterable로만 순회하고 batch 내부 구조를 해석하지 않는다.
- engine은 공통 lifecycle과 hook 호출 순서를 관리한다.
- task의 `train_step`은 parameter 갱신까지 완료한다.
- model은 framework 전용 기반 클래스를 상속하지 않는다.
- iterable 계약은 우선 v0.1 PyTorch backend에 적용하고, one-shot `fit` backend에는 별도 capability를 정의한다.
- `validate`와 `evaluate`는 같은 평가 loop를 사용하되 각각 `valid`와 `test` split으로 분리한다.
