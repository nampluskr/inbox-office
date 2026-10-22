# v0.3 데이터 처리 설계

## 사용자 의도

- v0.3 visionlab의 데이터 연결을 anomalib과 유사한 사용 방식으로 설계한다.
- 순수 PyTorch `MVTecDataset`을 정의하고, 이를 내부에서 생성하는 Lightning Wrapper `MVTecLitData`를 정의한다.
- `MVTecLitData`는 native `lightning.pytorch.LightningDataModule`을 직접 상속한다.
- visionlab의 Dataset·DataModule은 `anomalib.data`를 import하거나 anomalib 클래스에 의존하지 않는다.
- `MVTecLitData`의 생성자 인자 이름·순서·기본값은 anomalib 2.0.0의 `anomalib.data.MVTecAD`와 동일하게 맞춘다.
- 다른 `XXXLitData`도 대응하는 anomalib DataModule의 생성자 인자를 따르고 native Lightning으로 구현한다.
- 데이터 처리 설계는 이 독립 문서 `DATA.md` 한 개에 작성하고 다른 문서는 수정하지 않는다.
- Dataset·Transform·PreProcessor의 책임과 STFPM·EfficientAD별 처리 순서 및 차이를 설명한다.
- STFPM의 전체 입력 해상도 변경과 Tiler의 타일 분할·특징 복원을 구분하고, 설정 위치와 출력 해상도를 설명한다.
- 완전한 구현 코드 대신 클래스·생성자·주요 메서드·연결 관계를 보여주는 스켈레톤을 포함한다.
- 순수 Dataset과 native Lightning DataModule의 사용 예를 제시한다.
- 순수 PyTorch와 Lightning의 책임을 분리하고, 불필요한 공통 기반 클래스나 추상화 계층을 추가하지 않는다.
- 로컬 데이터와 가중치를 사용하고 자동 다운로드하거나 원본 자산을 수정하지 않는다.
- 문서는 한국어로 작성하고 이모지를 사용하지 않는다. 코드 설명은 간결한 영어 주석으로 작성한다.
- Markdown은 UTF-8로 저장하고 저장 후 엄격한 UTF-8 디코딩과 한글 본문을 확인한다.

작성일: 2026-10-22. 상태: 설계 제안, 구현 미착수.

이 문서는 MVTec AD를 기준으로 Dataset·Transform·native Lightning DataModule·PreProcessor와 STFPM Tiler의 역할 및 연결 구조를 정의한다. 아래 경로와 클래스는 목표 구조이며 현재 제공되는 실행 API가 아니다. 코드 블록은 책임과 연결을 설명하는 스켈레톤으로, 생략한 부분을 구현하기 전에는 실행 예제로 사용할 수 없다.

## 1. 구조와 의존성

```text
src/visionlab/anomaly_detection/data/
  mvtec/
    dataset.py          # MVTecDataset, MVTecTransform
    lightning_data.py   # MVTecLitData
  common/               # Shared pure operations when actually needed
```

| 구성요소 | 기반 클래스 | 책임 |
|---|---|---|
| `MVTecDataset` | `torch.utils.data.Dataset` | 파일 탐색, 이미지·라벨·마스크 읽기, 원본 식별 정보, 변환 호출 |
| `MVTecTransform` | 일반 Python 클래스 | 이미지·마스크의 공간 변환과 이미지 float 변환 |
| `MVTecLitData` | `lightning.pytorch.LightningDataModule` | Dataset 내부 생성, valid/test 분할, 단계별 준비, DataLoader 연결 |

`dataset.py`는 Lightning과 anomalib을 import하지 않는다. 순수 PyTorch DataLoader와 함께 독립적으로 사용할 수 있어야 한다. `lightning_data.py`는 순수 Dataset과 native Lightning API를 연결하며 anomalib을 참조하지 않는다.

`MVTecLitData`는 설정값을 받아 필요한 Dataset을 내부에서 생성한다. Dataset 상속 클래스가 아니며 Dataset 객체를 생성자에 주입하는 방식을 기본 계약으로 삼지 않는다. 모델의 Lightning Wrapper가 순수 모델을 내부 생성하는 것과 같은 구성 원칙이다.

visionlab의 `XXXLitData`는 대응하는 anomalib DataModule의 생성자 인자 이름·순서·기본값과 의미를 따른다. MVTec의 기준은 설치된 **anomalib 2.0.0의 `anomalib.data.MVTecAD`**다. 상속 대상은 native `LightningDataModule`이며 anomalib의 DataModule·Dataset·Enum을 import하거나 상속하지 않는다. 다른 데이터셋은 각자 대응하는 anomalib 클래스의 인자를 따르며 MVTec 전용 인자를 일괄 적용하지 않는다.

초기 MVTec 구현에는 공통 Lightning 기반 클래스를 추가하지 않는다. 파일 탐색·변환·분할에서 실제 공유가 확인된 순수 연산만 `data/common`에 둔다. 패키지 초기화가 `lightning_data.py`를 자동 import해 순수 Dataset 사용에 Lightning을 요구하지 않게 한다.

## 2. Dataset 입출력과 전처리

### 원본 데이터와 샘플

MVTec root는 범주 폴더의 상위 경로다. 기본 로컬 위치는 `E:/datasets/mvtec`이며 bottle 범주는 다음과 같이 읽는다.

```text
mvtec/bottle/
  train/good/
  test/good/
  test/<defect>/
  ground_truth/<defect>/<image_stem>_mask.png
```

Dataset의 `split` 인자는 원본 폴더를 선택하는 `train` 또는 `test`다. 논리적 valid/test는 DataModule의 분할 모드에 따라 연결한다. 원본에 valid 폴더가 있다고 가정하지 않는다. 기본 `same_as_test`는 같은 파일 목록을 사용하고, `from_test`를 명시하면 원본 test를 valid/test로 분리한다.

`dataset[index]`는 `(image, target)`을 반환한다.

| 값 | 계약 |
|---|---|
| `image` | RGB float32 Tensor `[3,H,W]`, 범위 `[0,1]` |
| `target["label"]` | 평가 시 정상 0·이상 1의 정수 scalar Tensor |
| `target["mask"]` | 평가 시 int64 이진 Tensor `[H,W]`, 정상 이미지는 모두 0 |
| `target["sample_id"]` | 평가·예측 결과와 원본을 대응시키는 안정적인 문자열 ID |
| `target["image_path"]` | 로컬 원본 이미지 경로 문자열 |

학습용 정상 샘플의 target은 빈 dict일 수 있다. 원본 ID·경로·라벨은 이 경우에도 Dataset의 `samples`에서 추적할 수 있어야 한다. 평가 target에는 위 네 필드를 제공한다. 정답 없는 예측을 추가할 때는 label·mask를 생략할 수 있으며, 이번 MVTec 기본 predict는 정답이 있는 test 집합을 사용한다.

`samples`에는 원본 split·이미지 상대 경로·라벨·마스크 상대 경로·sample ID를 보관한다. sample ID는 데이터셋·범주·원본 split·이미지 상대 경로를 구분한다. 예를 들면 `mvtec/bottle/test/broken_large/000.png`를 사용할 수 있다. 목록은 안정적인 경로 순서로 정렬하고, 파일명 stem만으로 샘플을 식별하지 않는다.

누락된 이미지·이상 마스크, 지원하지 않는 범주나 split, 빈 Dataset, 중복 ID는 오류로 보고한다. 데이터와 마스크를 자동 다운로드하거나 오류 샘플을 조용히 제외하지 않는다.

### 변환 책임

`MVTecTransform`은 `torchvision.transforms.v2`를 사용한다. RGB 변환 후 이미지와 마스크를 같은 공간 좌표계에서 resize하고 이미지를 float32 `[0,1]`로 변환한다. 기본 크기는 256×256이다. 이미지는 bilinear 보간과 antialias를 사용하고 마스크는 nearest 보간으로 이진 값을 보존한다.

DataModule은 단계별 `train_augmentations`·`val_augmentations`·`test_augmentations`를 Dataset 변환으로 연결한다. 단계별 값이 `None`이면 공통 `augmentations`를 사용한다. val과 test는 같은 파일 목록이어도 서로 다른 변환을 적용할 수 있도록 Dataset view와 transform 상태를 분리한다. predict는 test 변환을 사용한다.

DataModule에는 `image_size` 인자를 추가하지 않는다. 크기 변경은 augmentation의 `v2.Resize`로 표현한다. 변환 조립 시 지정한 resize를 우선하고, 없으면 기본 256×256 resize를 적용하여 중복 resize를 막는다. 이미지와 마스크를 함께 변환하며 마스크에 이미지용 색상 변환이나 정규화를 적용하지 않는다. 이 기본 공간 변환 연결은 visionlab의 Dataset·PreProcessor 분담에 따른 것으로, anomalib 모델의 PreProcessor를 탐색해 연결하는 구현을 요구하지 않는다.

모델별 정규화는 Dataset에서 수행하지 않는다. STFPM은 모델 Wrapper의 PreProcessor에서 ImageNet 정규화를 한 번 적용하며 EfficientAD는 `[0,1]` 입력을 받아 모델 내부 정규화를 사용한다. 시각화에는 모델 정규화 전 Dataset 이미지를 사용한다.

### 순수 Dataset 스켈레톤

다음 스켈레톤의 기본 transform은 Dataset이 내부 생성한다. 외부 transform을 지정하면 같은 이미지·마스크 입출력 계약을 충족해야 한다.

```python
from torch.utils.data import Dataset


class MVTecTransform:
    def __init__(self, image_size=256, augmentations=None):
        self.image_size = image_size
        self.augmentations = augmentations
        # Build v2 transforms with ToImage and paired spatial augmentations.
        # Use an explicit Resize when supplied; otherwise use image_size.
        # Use tv_tensors.Image/Mask and convert float image / integer mask.
        ...

    def __call__(self, image, target):
        # Resize image and mask together; convert image to float32 [0, 1].
        ...


class MVTecDataset(Dataset):
    def __init__(
        self,
        root,
        category="bottle",
        split="train",
        image_size=256,
        transform=None,
    ):
        self.root = root
        self.category = category
        self.split = split
        self.transform = (
            transform if transform is not None else MVTecTransform(image_size)
        )
        self.samples = self._collect_samples()

    def _collect_samples(self):
        # Validate local files and return records sorted by relative path.
        ...

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        # Read RGB image, label, mask and source metadata from samples[index].
        # Return self.transform(image, target).
        ...
```

## 3. Lightning DataModule 생명주기와 분할

### anomalib과 동일한 생성자 인자

다음 14개 인자의 이름·순서·기본값을 anomalib 2.0.0과 동일하게 유지한다. `root` 기본값과 실제 사용자 경로를 구분하며 로컬 실행 예제에서 `E:/datasets/mvtec`를 명시한다.

| 인자 | 기본값 | 의미 |
|---|---|---|
| `root` | `"./datasets/MVTecAD"` | 범주 폴더의 상위 경로 |
| `category` | `"bottle"` | MVTec 범주 |
| `train_batch_size` | `32` | 학습 batch size |
| `eval_batch_size` | `32` | 검증·평가·예측 batch size |
| `num_workers` | `8` | DataLoader worker 수 |
| `train_augmentations` | `None` | 학습 전용 변환 |
| `val_augmentations` | `None` | 검증 전용 변환 |
| `test_augmentations` | `None` | 평가·예측 전용 변환 |
| `augmentations` | `None` | 단계별 값이 없을 때 사용하는 공통 변환 |
| `test_split_mode` | `TestSplitMode.FROM_DIR` | test 구성 방식, 문자열 값 `"from_dir"` |
| `test_split_ratio` | `0.2` | test에 정상 샘플이 없을 때 train에서 확보하는 비율 |
| `val_split_mode` | `ValSplitMode.SAME_AS_TEST` | valid 구성 방식, 문자열 값 `"same_as_test"` |
| `val_split_ratio` | `0.5` | valid 분할이 필요한 모드에서 사용하는 비율 |
| `seed` | `None` | 분할 seed, 기본값은 고정 seed를 지정하지 않음 |

`image_size`·`valid_ratio`·`pin_memory`·manifest 경로 등 대응 원본에 없는 생성자 인자는 추가하지 않는다. 기존 `valid_ratio` 대신 `val_split_ratio`를 사용한다. root는 문자열과 `os.PathLike`를 받아 `os.fspath()`·`os.path`로 처리한다. pathlib 객체를 입력으로 받을 수 있지만 구현에서 `pathlib.Path`를 사용하지 않는다.

분할 Enum은 `data/common/split.py`에 순수 Python `str, Enum` 타입으로 정의한다. visionlab Enum 또는 동일한 문자열 값으로 설정하며 생성자 기본값에는 visionlab Enum을 사용한다. anomalib Enum 객체의 동일성을 요구하지 않는다. anomalib에서 타입을 가져와 주석이나 기본값에 사용하는 것도 허용하지 않는다.

| 타입 | 멤버와 문자열 값 |
|---|---|
| `TestSplitMode` | `NONE="none"`, `FROM_DIR="from_dir"`, `SYNTHETIC="synthetic"` |
| `ValSplitMode` | `NONE="none"`, `SAME_AS_TEST="same_as_test"`, `FROM_TRAIN="from_train"`, `FROM_TEST="from_test"`, `SYNTHETIC="synthetic"` |

모든 모드는 목표 지원 계약이다. 문자열을 받기만 하고 무시하거나 다른 모드로 대체하지 않는다. synthetic 등 아직 구현되지 않은 경로는 명시적인 오류를 보고하고, 구현·검증 전에는 지원 완료로 기록하지 않는다. 합성 이상 생성도 anomalib에 의존하지 않는 순수 연산으로 연결한다.

### 생명주기

root는 조립 단계에서 명시 경로 또는 `paths.toml`로 해석해 전달하며 Dataset이 기본 경로 설정을 다시 읽지 않는다. 생성자를 직접 호출할 때는 위 기본값을 사용한다.

| 메서드 또는 단계 | 역할 |
|---|---|
| `prepare_data()` | 로컬 폴더 존재 확인. 다운로드·Dataset 상태 생성·분할 수행 없음 |
| `setup("fit")` | 정상 train Dataset과 valid 집합 준비 |
| `setup("validate")` | 선택한 모드의 valid 집합 준비 |
| `setup("test")` | 선택한 모드의 test 집합 준비 |
| `setup("predict")` | 기본 예측 대상으로 test 집합 준비 |
| `setup(None)` | train·valid·test 모두 준비 |
| `train_dataloader()` | train 집합, shuffle 활성 |
| `val_dataloader()` | valid 집합, shuffle 비활성 |
| `test_dataloader()`·`predict_dataloader()` | test 집합, shuffle 비활성 |

`prepare_data()`는 분산 실행에서 모든 프로세스에 호출된다고 가정하지 않는다. Dataset과 분할 상태는 각 프로세스의 `setup()`에서 준비한다. 순수 Dataset도 파일을 검증하므로 직접 사용하는 경우에 동일한 오류를 보고할 수 있어야 한다.

분할 모드가 train에서 정상 샘플을 가져오도록 요구하면 독립 validate/test에서도 필요한 원본 train 목록을 준비한다. 이는 학습을 실행한다는 뜻이 아니다. 반복 setup은 이미 준비한 집합을 재사용한다. 기본 `same_as_test`는 valid와 test의 파일 목록이 같으므로 데이터 교집합을 무조건 오류로 처리하지 않는다.

### 모드와 재현성

기본값은 `test_split_mode="from_dir"`, `val_split_mode="same_as_test"`, `val_split_ratio=0.5`, `seed=None`다. `same_as_test`에서는 valid용으로 다시 분할하지 않으므로 `val_split_ratio`를 사용하지 않는다. 분리된 평가를 원하면 `val_split_mode="from_test"`를 명시한다. 이때 라벨별 분할과 비율 처리는 anomalib 2.0.0을 기준으로 연결하며 기존 프로젝트의 100회 재시도 정책을 기본 동작으로 가져오지 않는다.

`from_train`은 train에서 valid를 분리하고, `synthetic`은 정상 샘플을 기반으로 합성 이상을 구성한다. `none`은 원본의 해당 단계 분할 규칙을 따른다. test에 정상 이미지가 없는 경우에는 `test_split_ratio`를 적용해 train에서 정상 test 샘플을 확보한다. 각 모드는 원본 소스와 대조하여 구현·검증한다.

고정 seed를 명시하면 안정적인 원본 목록을 기반으로 새 인스턴스와 독립 평가에서도 분할을 재현한다. `seed=None`에서는 서로 다른 인스턴스의 동일 분할을 보장하지 않는다. 동일 인스턴스의 반복 setup에서는 seed와 무관하게 확정한 목록을 재사용한다. `from_train`은 정상 샘플만 포함할 수 있으므로 Dataset 계층이 모든 모드에서 두 클래스를 강제하지 않는다. AUROC나 모델 보정에 필요한 라벨 조건은 해당 평가·모델 연결에서 확인한다.

실제 선택한 ID·상대 경로 목록을 실행 기록에 저장하고 독립 평가에서 대조한다. 동일 seed만으로 데이터 동일성을 판정하지 않는다. 통제 비교용 manifest를 지정한 경우에는 해당 목록을 사용하고 재분할하지 않는다. manifest의 구체적인 파일 포맷·입출력 API는 구현 전에 확정할 항목으로 남기며 아래 스켈레톤에는 미확정 인자를 추가하지 않는다.

DataLoader의 기본 batch size는 학습·평가 각각 32, worker는 8이다. Windows의 간단한 실행 예제에서는 `num_workers=0`을 명시할 수 있다. EfficientAD는 `train_batch_size=1`을 명시한다. pin memory와 drop_last는 표준 DataLoader 기본값인 비활성을 사용하며 별도 생성자 인자로 노출하지 않는다. seed가 지정된 경우 generator·worker 난수 초기화에 연결한다. 최종 sampler·shuffle·drop_last·worker 설정은 실행 설정에 기록한다. 분산 실행에서는 프로세스마다 독립적으로 무작위 분할하지 않도록 seed 또는 확정한 파일 목록을 공유하고 native Lightning의 sampler 연결을 고려한다.

### native Lightning 스켈레톤

`_setup_datasets()`는 선택한 모드에 필요한 원본 Dataset을 내부 생성하고 분할·단계별 transform을 연결한다. `_make_loader()`는 표준 DataLoader 연결만 담당한다. 아래 Enum은 `data/common/split.py`에 별도로 정의한다. 스켈레톤에서는 해당 visionlab 타입만 import한다.

생성자 인자 목록은 anomalib 2.0.0 `data/datamodules/image/mvtecad.py`를 기준으로 작성했다. 원본의 Enum 대신 visionlab Enum을 사용하고 root의 타입은 같은 경로 입력을 수용하는 `os.PathLike`로 표기한다.

```python
# Constructor signature adapted from anomalib 2.0.0.
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import PathLike

import lightning.pytorch as pl
from torchvision.transforms.v2 import Transform

from visionlab.anomaly_detection.data.common.split import TestSplitMode, ValSplitMode
from visionlab.anomaly_detection.data.mvtec.dataset import MVTecDataset


class MVTecLitData(pl.LightningDataModule):
    def __init__(
        self,
        root: PathLike[str] | str = "./datasets/MVTecAD",
        category: str = "bottle",
        train_batch_size: int = 32,
        eval_batch_size: int = 32,
        num_workers: int = 8,
        train_augmentations: Transform | None = None,
        val_augmentations: Transform | None = None,
        test_augmentations: Transform | None = None,
        augmentations: Transform | None = None,
        test_split_mode: TestSplitMode | str = TestSplitMode.FROM_DIR,
        test_split_ratio: float = 0.2,
        val_split_mode: ValSplitMode | str = ValSplitMode.SAME_AS_TEST,
        val_split_ratio: float = 0.5,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        self.save_hyperparameters()
        self.train_dataset = None
        self.valid_dataset = None
        self.test_dataset = None
        # Validate configuration values.
        ...

    def prepare_data(self):
        # Check local folders; do not download or set per-process state.
        ...

    def setup(self, stage=None):
        if stage in (None, "fit", "validate", "test", "predict"):
            self._setup_datasets(stage)

    def _setup_datasets(self, stage):
        # Create MVTecDataset objects for the source train/test as needed.
        # Resolve test/val modes once and keep stable sample selections.
        # Select stage augmentations, falling back to self.hparams.augmentations.
        # Build MVTecTransform(augmentations=selected) per stage.
        # Pass each transform to its MVTecDataset view without sharing state.
        # Assign train_dataset, valid_dataset and test_dataset as required.
        ...

    def _make_loader(self, dataset, batch_size, shuffle):
        # Return a standard DataLoader with configured workers and RNG state.
        ...

    def train_dataloader(self):
        return self._make_loader(
            self.train_dataset, self.hparams.train_batch_size, shuffle=True,
        )

    def val_dataloader(self):
        return self._make_loader(
            self.valid_dataset, self.hparams.eval_batch_size, shuffle=False,
        )

    def test_dataloader(self):
        return self._make_loader(
            self.test_dataset, self.hparams.eval_batch_size, shuffle=False,
        )

    def predict_dataloader(self):
        return self._make_loader(
            self.test_dataset, self.hparams.eval_batch_size, shuffle=False,
        )
```

## 4. Transform·PreProcessor와 모델별 처리

### 단계별 책임과 입력

Dataset은 원본 이미지·라벨·마스크를 읽고 Transform을 호출한다. Transform은 CPU의 샘플 단위 공간 변환과 augmentation을 수행하며, DataLoader가 결과를 배치로 묶는다. PreProcessor는 모델 호출 직전에 배치의 shape·dtype·범위를 확인하고 모델별 정규화를 적용한다. PreProcessor는 resize·augmentation을 반복하지 않는다.

| 단계 | 이미지 형식 | 마스크·메타데이터 |
|---|---|---|
| 원본 읽기 | RGB 이미지, 원본 해상도 | 이상 마스크 또는 정상의 0 마스크, 원본 식별 정보 |
| Dataset Transform 출력 | float32 `[3,H,W]`, `[0,1]` | 이진 int64 마스크 `[H,W]`, ID·경로 보존 |
| DataLoader 출력 | float32 `[B,3,H,W]`, `[0,1]` | 마스크 `[B,H,W]`, 이미지별 ID·경로 |
| STFPM PreProcessor 출력 | 같은 shape, ImageNet 정규화된 값 | 정답·메타데이터 변경 없음 |
| EfficientAD PreProcessor 출력 | 같은 shape, `[0,1]` | 정답·메타데이터 변경 없음 |

`torchvision.transforms.v2`에 이미지는 `tv_tensors.Image`, 마스크는 `tv_tensors.Mask`로 전달하여 같은 무작위 공간 변환을 적용한다. 이미지의 색상 변환은 이미지에만 적용한다. dtype 변환은 이미지 float32 스케일 변환과 마스크 int64 이진 값 보존을 구분한다. 모델별 `Normalize`를 Dataset Transform이나 `*_augmentations`에 넣지 않는다.

### STFPM·EfficientAD 비교

| 항목 | STFPM | EfficientAD |
|---|---|---|
| Dataset | 공통 `MVTecDataset` | 공통 `MVTecDataset` |
| Transform | 공간 변환·단계별 augmentation·float 변환 | 같은 책임, 필요한 augmentation은 별도 설정 |
| 기본 전체 크기 | 256×256, 고해상도 타일링에서는 명시적으로 변경 | 초기 지원 기준 256×256 |
| PreProcessor | 입력 확인 후 ImageNet 정규화 | 입력 확인, 외부 정규화 생략 |
| 순수 모델 입력 | 정규화한 배치 | `[0,1]` 배치 |
| 모델 내부 정규화 | 추가 적용 없음 | 모델 내부 ImageNet 정규화 |
| Tiler | 선택적으로 사용 | 초기 설계에서 연결하지 않음 |
| 학습 batch size | 설정값 사용 | 현재 지원 기준 1 |

ImageNet 정규화 기준은 mean `(0.485, 0.456, 0.406)`, std `(0.229, 0.224, 0.225)`다. STFPM은 PreProcessor에서, EfficientAD는 순수 모델 내부에서 적용한다.

```text
STFPM:
원본 → Dataset Transform → [0,1] 배치 → PreProcessor 정규화
     → STFPMModel: 선택적 tile → 특징 추출 → 선택적 untile → 예측

EfficientAD:
원본 → Dataset Transform → [0,1] 배치 → PreProcessor 입력 확인
     → EfficientADModel 내부 정규화 → teacher/student/autoencoder 연산
```

EfficientAD의 Imagenette penalty 입력은 MVTec DataLoader와 별도로 학습 연결에서 준비한다. 이 입력에도 외부 ImageNet 정규화를 적용하지 않고 `[0,1]` 이미지를 순수 모델에 전달한다. Imagenette 경로와 teacher 가중치는 MVTecLitData 생성자에 추가하지 않는다.

### 순수 PreProcessor와 호출 스켈레톤

목표 위치는 `visionlab/anomaly_detection/common/pre_processor.py`다. PreProcessor는 순수 `nn.Module`로 정의하고 Lightning Callback이나 anomalib 클래스를 상속하지 않는다. 모델 Wrapper가 모델 설정에 맞는 PreProcessor를 내부 생성한다. 아래 예의 `mean=None, std=None`은 EfficientAD의 입력 확인 전용 구성을 뜻하며, STFPM은 두 통계값을 모두 설정한다.

```python
from torch import nn


class PreProcessor(nn.Module):
    def __init__(self, mean=None, std=None):
        super().__init__()
        # Validate paired mean/std; register normalization buffers if enabled.
        ...

    def forward(self, images):
        # Check float32 [B, 3, H, W] input in [0, 1].
        # Return normalized images or the unchanged input when disabled.
        # Never resize, augment or modify the source images in place.
        ...
```

순수 PyTorch 경로에서도 같은 PreProcessor를 직접 호출한다.

```python
# Pure PyTorch: images have already passed through Dataset Transform.
images, target = next(iter(loader))
model_inputs = pre_processor(images)
predictions = pure_model(model_inputs)
```

Lightning Wrapper는 train·validate·test·predict에서 같은 입력 경로를 호출한다. 다음은 호출 관계만 보여주는 스켈레톤이며 모델 생성과 단계별 loss·metric 처리는 생략한다.

```python
class STFPMLitModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        # Constructor settings are omitted from this call-flow skeleton.
        # Create self.model and self.pre_processor from those settings.
        ...

    def forward(self, images):
        model_inputs = self.pre_processor(images)
        return self.model(model_inputs)

    def training_step(self, batch, batch_idx):
        images, target = batch
        features = self(images)
        # Compute model-specific loss from the returned features.
        ...
```

Wrapper 예시는 호출 순서에 집중하여 생성자 설정 인자를 생략했다. 실제 구현에서는 모델 설정 인자를 명시한다. EfficientAD Wrapper도 같은 호출 순서를 사용하되 PreProcessor의 외부 정규화를 생략한다. 이미 전처리한 입력을 다시 Wrapper에 넘겨 이중 정규화하지 않는다.

시각화에는 `images`의 정규화 전 값을 사용하며 `target`의 마스크·라벨·원본 ID를 보존한다. 독립 추론도 같은 공간 변환과 PreProcessor를 재사용한다. 원본 이미지 입력 경로에서는 공간 변환 후 PreProcessor를 호출하고, 이미 공간 변환한 `[0,1]` 배치 입력 경로에서는 PreProcessor만 호출한다.

### anomalib과의 연결 방식 차이

anomalib 2.0.0은 모델 PreProcessor에 resize·정규화 등을 정의하고, PreProcessor가 `nn.Module`과 Lightning Callback을 함께 상속한다. DataModule은 모델의 resize를 Dataset augmentation에도 연결해 collate 전에 크기를 맞추며, 배치 Hook에서 PreProcessor transform을 적용한다.

현재 visionlab 설계에서는 Dataset Transform이 공간 변환을 완료하고, 순수 PreProcessor는 입력 확인·모델별 정규화를 담당한다. DataModule 생성자 인자는 anomalib과 맞추되 내부 전처리 연결은 이 문서의 분리 원칙을 따른다. anomalib의 Callback 또는 export용 전처리 구현 전체를 제공한다는 뜻은 아니다.

## 5. STFPM Tiler와 이미지 크기

### 설정 위치와 실행 위치

| 처리 | 설정·실행 위치 | 예 |
|---|---|---|
| 전체 이미지 크기 변경 | Dataset Transform의 `v2.Resize` | 원본 → 1024×1024 |
| 정규화 | Wrapper가 호출하는 PreProcessor | 전체 배치 ImageNet 정규화 |
| Tiler 생성·연결 | 모델 조립 단계, Lightning 실행에서는 모델 Wrapper | 순수 모델의 `model.tiler`에 연결 |
| 타일 분할 | 순수 `STFPMModel.forward()`의 `tiler.tile()` | 256×256 타일 생성 |
| 특징 복원 | 특징 추출 후 계층별 `tiler.untile()` | teacher/student 특징을 각각 복원 |
| anomaly map 해상도 | 모델의 anomaly map 생성 단계 | tile 이전 모델 입력의 전체 크기 |

Tiler의 목표 위치는 `visionlab/anomaly_detection/models/components/tiling/tiler.py`다. 순수 PyTorch 구성요소로 유지하며 Dataset·DataModule에서 타일별 학습 샘플이나 정답을 새로 만들지 않는다. 기본값은 Tiler 비활성이다. 순수 PyTorch 사용자는 직접 구성해 순수 모델에 연결할 수 있다.

전체 크기는 DataModule의 공통 `augmentations` 또는 단계별 augmentation으로 지정한다. 모든 단계에 같은 해상도를 적용하는 설정 형태는 다음과 같다. 단계별 값이 있으면 그 값이 우선하므로 서로 다른 해상도를 의도했는지 확인한다.

```python
from torchvision.transforms import v2


data = MVTecLitData(
    root="E:/datasets/mvtec",
    augmentations=v2.Resize((1024, 1024), antialias=True),
)
```

Tiler는 별도로 모델 조립 코드에서 연결한다. 아래 `pure_model`은 생성한 순수 STFPM 모델이며, Lightning에서는 Wrapper가 같은 연결을 내부에서 수행한다. DataModule의 14개 생성자 인자에 타일 설정을 추가하지 않는다. Wrapper의 최종 설정 인자 이름은 모델 설계에서 확정하고, tile_size·stride·mode·remove_border_count와 활성 여부는 checkpoint 및 독립 추론 설정에 보존한다.

```python
from visionlab.anomaly_detection.models.components.tiling.tiler import Tiler


pure_model.tiler = Tiler(tile_size=256, stride=256, mode="padding")
```

### 해상도 예와 특징 복원

전체 입력 1024×1024, tile 256×256, stride 256이면 이미지당 16개 타일이 생긴다. 전체 배치가 `[B,3,1024,1024]`이면 특징 추출기에 전달하는 타일 배치는 `[B*16,3,256,256]`이다. 계층별 특징은 backbone의 downsampling 비율에 따른 해상도를 가지며 untile 후에도 해당 특징 해상도를 유지한다. 최종 anomaly map을 전체 1024×1024에 맞춘다.

```text
Dataset 이미지·마스크: 1024×1024
  → PreProcessor: 전체 이미지 정규화, 마스크 유지
  → Tiler: 이미지당 256×256 타일 16개
  → teacher/student: 타일별 특징 추출
  → Untiler: 계층별 teacher/student 특징 복원
  → 학습: 복원된 특징으로 loss 계산
  → 평가: 복원된 특징으로 anomaly map 생성 → 1024×1024
```

STFPM은 타일별 anomaly map을 생성해 붙이는 구조가 아니다. 특징을 먼저 복원한 뒤 anomaly map을 생성하며, 이 순서를 학습·평가에서 보존한다. 순수 모델의 핵심 흐름은 다음과 같다.

```python
def forward(self, images):
    output_size = images.shape[-2:]
    if self.tiler is not None:
        images = self.tiler.tile(images)

    teacher_features = self.teacher_model(images)
    student_features = self.student_model(images)

    if self.tiler is not None:
        # Untile every layer of teacher_features and student_features.
        ...

    if self.training:
        return teacher_features, student_features

    # Generate the anomaly map at output_size from restored features.
    ...
```

기본 256×256 resize 후 256×256 타일을 사용하면 타일은 이미지당 하나다. 고해상도 타일링을 사용할 때는 전체 입력 해상도를 먼저 명시하고, 그보다 작은 tile_size와 적절한 stride를 설정한다. 기본 resize로 이미 잃은 세부 정보는 Tiler로 복원할 수 없다.

### 가장자리 보정과 평가 좌표

타일 격자가 입력 가장자리에 맞지 않으면 Tiler 내부에서 padding 또는 interpolation으로 작업 크기를 맞춘다. untile은 가장자리 보정을 되돌려 입력에 대응하는 전체 특징을 복원한다. 이 과정은 Dataset의 전체 resize 설정과 별개다. tile_size·stride의 유효성과 입력 크기를 확인하며 지원하지 않는 조합은 오류로 처리한다.

정답 마스크와 시각화 이미지는 Dataset 변환 후 전체 좌표계를 유지한다. 최종 anomaly map도 tile 이전 모델 입력 크기를 사용하므로 이 마스크와 직접 대응한다. 원본 파일이 2048×2048이고 Dataset이 1024×1024로 변환했다면 결과는 1024×1024다. 원본 파일 해상도로 되돌리는 기능은 별도 후속 처리로 정의해야 하며 여기서 자동 제공하지 않는다.

## 6. 연결 예와 구현 시 확인

### 순수 PyTorch 사용 형태

아래 예는 구현 완료 후의 연결 형태다. Dataset만 사용하는 경로에서는 Lightning을 import하지 않는다.

```python
from torch.utils.data import DataLoader

from visionlab.anomaly_detection.data.mvtec.dataset import MVTecDataset


dataset = MVTecDataset(
    root="E:/datasets/mvtec", category="bottle", split="train",
)
loader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=0)
```

### native Lightning 사용 형태

`model`은 별도로 생성한 native LightningModule이다. fit과 test는 각각 명시적으로 호출하며 DataModule이 학습 루프를 실행하지 않는다.

```python
from lightning.pytorch import Trainer

from visionlab.anomaly_detection.data.mvtec.lightning_data import MVTecLitData


data = MVTecLitData(
    root="E:/datasets/mvtec",
    category="bottle",
    train_batch_size=8,
    eval_batch_size=8,
    num_workers=0,
    val_split_mode="from_test",
    val_split_ratio=0.4,
    seed=42,
)
trainer = Trainer(max_epochs=10, devices=1)
trainer.fit(model, datamodule=data)
trainer.test(model, datamodule=data)
```

이 예제는 로컬 실행 편의와 valid/test 분리를 위해 기본값을 명시적으로 덮어쓴다. 인자 없는 `MVTecLitData()`는 anomalib과 동일한 기본값을 사용한다.

### 향후 구현 검증 기준

- 생성자의 14개 인자 이름·순서·기본값을 기준 anomalib 버전과 대조한다. 타입은 visionlab Enum과 표준 경로 타입으로 독립적으로 정의했는지 확인한다.
- 순수 Dataset import·샘플 읽기에 Lightning·anomalib이 필요하지 않은지 확인한다.
- 정상·이상 샘플의 이미지 shape·dtype·범위, 라벨·이진 마스크·원본 식별 정보와 기본 collate 결과를 확인한다.
- 이미지·마스크 공간 대응, 정상의 0 마스크, 모델별 정규화가 한 번만 적용되는지 확인한다.
- Dataset 출력·배치·모델 입력의 shape·dtype·범위를 구분해 확인하고, resize·정규화의 중복과 시각화용 원본 배치 변경이 없는지 확인한다.
- EfficientAD의 MVTec·Imagenette 입력이 외부 정규화 없이 모델에 전달되는지 확인한다.
- Tiler 비활성·활성 경로를 구분하고, 1024×1024 입력과 256 타일·stride에서 이미지당 16개 타일이 생성되는지 확인한다.
- 계층별 특징 복원, 겹치는 타일과 가장자리 보정, 입력 전체 크기의 anomaly map과 정답 마스크 대응을 확인한다. Tiler 설정 저장·복원과 독립 추론의 동일성도 확인한다.
- 기본 `same_as_test`에서는 valid/test 파일 목록이 같고, 명시한 `from_test`에서는 겹치지 않는지 확인한다. 고정 seed에서 새 인스턴스·독립 평가의 목록을 대조하고 반복 setup의 목록 보존을 확인한다.
- 단계별 augmentation 우선순위, 공통 fallback, val/test transform 상태 분리와 지정한 resize 반영을 확인한다.
- 누락 파일·마스크·중복 ID·잘못된 분할 인자·라벨 수 부족을 오류로 처리하는지 확인한다.
- native Trainer가 DataModule을 통해 단계를 실행하고 EfficientAD의 학습 batch 1 설정이 적용되는지 확인한다.

이번 문서는 설계와 스켈레톤만 제공한다. Dataset·DataModule 구현, import·학습·평가·성능 검증 결과는 포함하지 않는다.

### 참조

- anomalib 2.0.0 설치 소스: `anomalib/data/datamodules/image/mvtecad.py`, `anomalib/data/datamodules/base/image.py`, `anomalib/data/utils/split.py`.
- [anomalib MVTecAD 공식 API](https://anomalib.readthedocs.io/en/latest/markdown/guides/reference/data/datamodules/image/mvtecad.html). 웹 문서는 변경될 수 있으므로 이 문서의 인자 기준은 위 2.0.0 설치 소스다.
- [anomalib 2.0.0 augmentation 안내](https://anomalib.readthedocs.io/en/v2.0.0/markdown/guides/how_to/data/transforms.html).
