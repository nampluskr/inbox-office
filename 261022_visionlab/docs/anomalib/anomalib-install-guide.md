# WinPython anomalib 설치 및 로컬 경로 설정

확인 기준일: 2026-10-22.

지정된 WinPython의 PyTorch 2.2.1+cu118, torchvision 0.17.1+cu118, Lightning 2.5.5, NumPy 1.26.4를 유지하면서 anomalib 2.0.0의 설치와 로컬 데이터·가중치 연결 방법을 정리한다. 실제 설치 결과와 검증 범위는 아래에 기록한다.

## 1. 설치 위치와 버전 선택

| 구분 | 경로 |
|---|---|
| WinPython | `C:\winpython\WPy64-31180_gpu` |
| Python 실행 파일 | `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe` |
| 패키지 설치 폴더 | `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\Lib\site-packages` |
| anomalib 패키지 | 위 폴더의 `anomalib` |
| CLI 실행 파일 | `C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\Scripts\anomalib.exe` |
| 프로젝트 작업 폴더 | `D:\projects\lightning-tutorial` |
| 데이터셋 | `E:\datasets` |
| backbone·teacher 가중치 | `E:\backbones` |

실제 폴더명은 `E:\dataset`이 아닌 `E:\datasets`이다. Python 패키지와 데이터·가중치는 서로 다른 위치에 저장한다.

anomalib 2.0.0의 `core` 요구 조건은 Python ≥3.10, torch ≥2, Lightning ≥2.2, torchmetrics ≥1.3.2이다. 현재 주요 패키지를 유지하기 위해 2.0.0을 선택했다. 이는 현재 환경에 맞춘 이전 버전 선택이며, 최신 버전 권장이라는 의미는 아니다. 검토 시 최신 2.7 계열은 PyTorch 2.10 이상으로 최소 버전을 올렸으므로 무조건 `pip install -U anomalib`을 실행하지 않는다.

실제 import 확인에서 `core`만으로는 `scikit-learn`, `openvino`, `python-dotenv`, `requests`가 누락되는 것을 확인했다. 따라서 아래 설치 명령에는 보완 패키지를 명시한다. OpenVINO 2024.6.0은 이 버전이 직접 참조하는 `openvino.runtime...OVDict` API를 제공하기 위한 선택이다. python-dotenv와 requests는 공개 models import 과정의 VLM·동영상 모듈 참조에 필요하다. OpenVINO를 설치해도 PyTorch 학습은 NVIDIA CUDA를 사용할 수 있다. `full` extra 전체는 설치하지 않는다.

또한 pandas 3.0.6에서 문자열 열과 anomalib의 `Split` Enum 비교가 모두 거짓이 되어 MVTec 학습 split이 0개가 되는 문제를 재현했다. 원본 파일은 209개였으며 문자열 `"train"`과 비교하면 209개, `Split.TRAIN`과 비교하면 0개였다. 이를 피하기 위해 pandas 2.2.3을 명시적으로 고정한다.

근거: [anomalib v2.0.0 의존성](https://github.com/open-edge-platform/anomalib/blob/v2.0.0/pyproject.toml), [최신 릴리스](https://github.com/open-edge-platform/anomalib/releases), [OpenVINO 직접 import](https://github.com/open-edge-platform/anomalib/blob/v2.0.0/src/anomalib/deploy/inferencers/openvino_inferencer.py).

## 2. 확인한 하드웨어·소프트웨어 사양

| 항목 | 확인 결과 |
|---|---|
| CPU | Intel Xeon w5-2445 |
| CPU 코어 | 물리 10코어, 논리 20개 |
| OS에서 확인한 RAM | 68,146,552,832 bytes, 약 63.47 GiB |
| Windows | 64비트, 23H2, build 22631 |
| GPU | NVIDIA RTX A4000 |
| GPU 메모리 | nvidia-smi 기준 15,352 MiB, 제품 사양상 16GB급 |
| NVIDIA 드라이버 | 560.76 |
| nvidia-smi CUDA 표시 | 12.6 |
| Python | CPython 3.11.8, 64비트 |
| PyTorch | 2.2.1+cu118 |
| torchvision | 0.17.1+cu118 |
| PyTorch CUDA 런타임 | 11.8 |
| cuDNN | 8700, 즉 8.7.0 |
| Lightning / pytorch-lightning | 2.5.5 / 2.5.5 |
| NumPy | 1.26.4 |
| timm | 1.0.30 |
| torchmetrics | 1.9.0 |
| pip | 24.0 |

Windows 제품명은 레지스트리에서 `Windows 10 Enterprise`, Python platform에서도 `Windows-10`으로 출력됐다. OS 식별 기록은 함께 확인한 build 22631·23H2를 기준으로 남긴다. CUDA Toolkit의 별도 설치 여부와 `nvcc` 버전은 확인하지 않았다.

`nvidia-smi`의 CUDA 12.6은 드라이버의 지원 수준이고, PyTorch의 `torch.version.cuda` 값인 11.8은 설치된 PyTorch 빌드의 CUDA 런타임이다. 두 숫자가 다른 것은 정상이다. 현재 PyTorch가 GPU를 인식하므로 anomalib 설치를 위해 CUDA Toolkit·드라이버·PyTorch를 먼저 교체할 필요는 없다. [NVIDIA CUDA 호환성](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)

## 3. 설치 방법

아래 명령은 프로젝트 루트의 PowerShell에서 실행한다. 외부 명령은 프로젝트 지침에 따라 RTK로 실행하며, Python은 항상 지정 실행 파일을 사용한다.

```powershell
$py = 'C:\winpython\WPy64-31180_gpu\python-3.11.8.amd64\python.exe'
```

### 3.1 설치 전 확인

```powershell
rtk proxy $py -m pip check
rtk proxy $py -c "import sys, torch; print(sys.executable); print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available())"
rtk proxy nvidia-smi
```

설치 전 `pip check`는 `No broken requirements found.`를 출력했다. pip에는 사내 패키지 인덱스가 이미 설정되어 있어 이번 설치도 그 설정을 사용했다. 인덱스·인증·인증서 설정은 변경하지 않았다.

### 3.2 주요 버전을 고정한 설치 계획 확인

```powershell
rtk proxy $py -m pip install --dry-run --no-user `
    'anomalib[core]==2.0.0' `
    'torch==2.2.1+cu118' 'torchvision==0.17.1+cu118' `
    'lightning==2.5.5' 'numpy==1.26.4' `
    'timm==1.0.30' 'torchmetrics==1.9.0' `
    'opencv-python==4.11.0.86' `
    'scikit-learn==1.6.1' 'openvino==2024.6.0' `
    'python-dotenv==1.0.1' 'requests==2.32.5' 'pandas==2.2.3'
```

`--dry-run`은 설치 계획만 계산하지만 패키지·메타데이터 다운로드는 발생할 수 있다. OpenCV 4.11.0.86은 현재 NumPy 1.26.4를 유지하는 조합으로 고정했다.

### 3.3 실제 설치

```powershell
rtk proxy $py -m pip install --no-user `
    'anomalib[core]==2.0.0' `
    'torch==2.2.1+cu118' 'torchvision==0.17.1+cu118' `
    'lightning==2.5.5' 'numpy==1.26.4' `
    'timm==1.0.30' 'torchmetrics==1.9.0' `
    'opencv-python==4.11.0.86' `
    'scikit-learn==1.6.1' 'openvino==2024.6.0' `
    'python-dotenv==1.0.1' 'requests==2.32.5' 'pandas==2.2.3'
```

`--no-user`는 사용자별 `%APPDATA%\Python\Python311\site-packages`로 설치되는 것을 막는다. WinPython 폴더에 쓰기 권한이 필요하며, 접근 거부가 발생하면 해당 폴더에 쓰기 가능한 계정이나 관리자 PowerShell에서 실행한다. `--user`로 우회하면 요청한 설치 위치가 달라진다. 기존 사용자 site-packages에 있던 일부 공통 패키지는 그대로 참조할 수 있으므로, 이것이 완전히 격리된 환경을 만든다는 의미는 아니다.

이번 작업은 `core` 설치 후 import 오류를 확인하고 scikit-learn, OpenVINO, python-dotenv, requests를 순서대로 보완한 뒤 pandas를 고정했다. 위 명령은 그 절차를 하나로 합친 재설치용 명령이다. pip 자체는 업그레이드하지 않았다.

### 3.4 설치 확인과 CLI

```powershell
rtk proxy $py -m pip check
rtk proxy $py -c "import anomalib, torch; from anomalib.data import MVTecAD; from anomalib.models import Stfpm, EfficientAd; from anomalib.engine import Engine; print(anomalib.__version__); print(anomalib.__file__); print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available())"
rtk proxy $py -m anomalib.cli.cli --help
```

이번 WinPython이 생성한 `anomalib.exe`의 launcher는 `#!python.exe`를 사용한다. 실제로 실행 파일의 절대 경로만 지정하면 PATH의 다른 Python을 사용해 `No module named anomalib` 오류가 발생했다. 따라서 위처럼 지정 Python에서 `-m anomalib.cli.cli`를 호출한다. anomalib 2.0.0에는 패키지 최상위 `__main__.py`가 없으므로 `python -m anomalib`은 사용할 수 없다. `anomalib.exe`를 쓰려면 먼저 WinPython 런처 환경을 활성화하거나 해당 Python 폴더를 PATH 맨 앞에 둬야 한다.

Matplotlib 캐시 폴더 권한 오류가 있을 때는 실행 전에 쓰기 가능한 폴더를 지정한다.

```powershell
$env:MPLCONFIGDIR = "$env:TEMP\anomalib-mpl"
```

## 4. 기존 데이터셋 연결

### 4.1 확인한 로컬 데이터

| 데이터 | 경로·구조 |
|---|---|
| MVTec AD | `E:\datasets\mvtec\bottle`, `cable`, `grid` 등 |
| BTAD | `E:\datasets\btad\01`, `02`, `03` |
| VisA | `E:\datasets\visa` 및 `split_csv` |
| Imagenette | `E:\datasets\imagenette2\train`, `val` |
| 기타 | CIFAR-10/100, MNIST, Fashion-MNIST 등도 존재 |

데이터셋 경로는 각 DataModule의 `root`로 지정한다. 공통 환경변수 하나가 모든 anomalib 데이터셋의 기본값을 바꾸지는 않는다.

```python
from anomalib.data import MVTecAD

datamodule = MVTecAD(
    root="E:/datasets/mvtec",
    category="bottle",
    train_batch_size=8,
    eval_batch_size=8,
    num_workers=0,
)
```

MVTec의 `root`는 `bottle`의 상위 폴더다. 현재 `bottle/train/good`와 `bottle/ground_truth`가 존재한다. `prepare_data()`는 `root/category`가 있으면 다운로드를 생략하고, 없으면 다운로드를 시도한다. 경로 오타에 주의한다. [MVTec 구현](https://github.com/open-edge-platform/anomalib/blob/v2.0.0/src/anomalib/data/datamodules/image/mvtecad.py)

anomalib CLI용 YAML에서는 다음과 같이 지정한다. 프로젝트 자체 CLI의 YAML 계약과는 별개다.

```yaml
data:
  class_path: anomalib.data.MVTecAD
  init_args:
    root: E:/datasets/mvtec
    category: bottle
    num_workers: 0
```

BTAD·VisA도 해당 클래스의 `root`를 지정하되, 원본 파일 구조와 각 DataModule의 준비 동작을 확인한다. 특히 일부 데이터 준비 코드는 정리·복사 작업을 수행할 수 있다. 이번 설치에서는 BTAD·VisA의 준비 함수를 실행하지 않았다.

Windows에서 별도 Python 스크립트로 학습할 때는 실행부를 `if __name__ == "__main__":` 안에 두고, 처음에는 `num_workers=0`으로 시작한다.

## 5. 앞으로 다운로드할 backbone 캐시 위치

### 5.1 현재 PowerShell 세션에 적용

Python·Jupyter를 시작하기 전에 설정한다.

```powershell
$env:TORCH_HOME = 'E:\backbones\torch'
$env:HF_HOME = 'E:\backbones\huggingface'
$env:HF_HUB_CACHE = 'E:\backbones\huggingface\hub'
```

| 사용 주체 | 실제 기본 캐시 |
|---|---|
| Torch Hub·torchvision의 URL 가중치 | `E:\backbones\torch\hub\checkpoints` |
| Hugging Face를 사용하는 timm | `E:\backbones\huggingface\hub` |

이 값들은 설치 명령의 인자가 아니라 실행 시 환경변수다. 기존 Python·Jupyter 커널은 종료하고 이 환경을 상속하는 새 프로세스로 시작한다. 사용자 환경에 `HF_HUB_CACHE`가 따로 지정되어 있으면 `HF_HOME`만 바꿔서는 캐시가 이동하지 않으므로 함께 명시했다.

### 5.2 WinPython 실행 환경에 유지

확인한 설정 파일은 `C:\winpython\WPy64-31180_gpu\settings\winpython.ini`이다. WinPython 런처로 실행할 때 적용하려면 기존 `[environment]` 섹션에 다음 항목을 추가한다. 기존 섹션을 중복 생성하지 않는다.

```ini
[environment]
TORCH_HOME = E:\backbones\torch
HF_HOME = E:\backbones\huggingface
HF_HUB_CACHE = E:\backbones\huggingface\hub
```

이 설정은 WinPython 런처가 읽는 설정이다. 외부 PowerShell·IDE에서 `python.exe`를 직접 실행하는 경우에는 해당 부모 프로세스에서도 환경변수를 지정해야 한다. 이번 작업에서는 INI나 사용자·시스템 환경변수를 변경하지 않았다.

근거: [Torch Hub 캐시](https://docs.pytorch.org/docs/stable/hub.html), [Hugging Face 환경변수](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables).

## 6. 이미 보유한 backbone 파일 재사용

### 6.1 캐시 변경과 기존 파일 로딩의 차이

현재 다음 파일을 확인했다.

```text
E:\backbones\resnet18-f37072fd.pth
E:\backbones\resnet18_a1_0-d63eafa0.pth
E:\backbones\resnet50-0676ba61.pth
E:\backbones\resnet50-11ad3fa6.pth
E:\backbones\wide_resnet50_2-95faca4d.pth
E:\backbones\resnet50.tv_in1k\model.safetensors
E:\backbones\wide_resnet50_2.tv_in1k\model.safetensors
```

이 밖에 EfficientNet·MobileNet·VGG·DINOv2 등의 가중치도 존재한다. 파일 존재 여부는 모델·학습 방식·state_dict 키가 호환됨을 보장하지 않는다. 예를 들어 같은 ResNet18이라도 timm의 기본 학습 가중치와 torchvision V1 가중치는 다를 수 있다.

환경변수만 설정하면 이러한 파일을 재귀 검색해서 자동 선택하지 않는다. Torch Hub는 요청 URL의 파일명에 대응하는 캐시를 사용하고, Hugging Face는 repository·revision·snapshot 구조를 사용한다. `model.safetensors` 파일 하나가 있는 폴더는 Hugging Face 캐시 전체와 다르다.

Torch Hub 로더를 사용하는 모델이라면, 요청 URL과 파일명이 일치하는 기존 `.pth`를 `TORCH_HOME/hub/checkpoints`에 복사해 재사용할 수 있다. Hugging Face를 사용하는 timm 모델에는 이 방법만으로 충분하지 않다.

### 6.2 명시적인 timm 로컬 파일 로딩

timm을 직접 사용할 때는 다음처럼 로컬 파일을 지정할 수 있다.

```python
import timm

backbone = timm.create_model(
    "resnet18.tv_in1k",
    pretrained=True,
    pretrained_cfg_overlay={
        "file": "E:/backbones/resnet18-f37072fd.pth",
        "hf_hub_id": None,
        "url": "",
    },
    features_only=True,
    out_indices=(1, 2, 3),
)
```

파일 로딩을 명시하므로 해당 파일이 없거나 맞지 않으면 오류를 해결해야 한다. 원치 않는 무작위 초기화로 대체하지 않는다.

anomalib 2.0.0의 `Stfpm`과 공통 `TimmFeatureExtractor`는 이 `pretrained_cfg_overlay`나 `weights_path`를 생성자 인자로 노출하지 않는다. 따라서 위 인자를 그대로 `Stfpm(...)`이나 YAML에 추가할 수 없다. 별도 timm 모델 등록 또는 모델별 연결 코드가 필요하다. 아래는 기존 ResNet18 파일을 쓰는 Python 실행 예시다.

```python
from timm.models import register_model
from timm.models.resnet import resnet18
from anomalib.models import Stfpm


@register_model
def local_resnet18(pretrained=False, **kwargs):
    kwargs["pretrained_cfg_overlay"] = {
        "file": "E:/backbones/resnet18-f37072fd.pth",
        "hf_hub_id": None,
        "url": "",
    }
    return resnet18(pretrained=pretrained, **kwargs)


model = Stfpm(backbone="local_resnet18")
```

등록은 모델 생성 전에 같은 Python 프로세스에서 실행해야 한다. teacher는 로컬 pretrained 파일을 로드하고 student는 원래 STFPM 동작대로 무작위 초기화된다. 이는 필요한 teacher 가중치가 없을 때 무작위 초기화로 우회하는 동작과 다르다. 이 예시는 설치된 패키지 소스를 수정하지 않는다.

Hugging Face 다운로드만 막으려면 실행 전에 `$env:HF_HUB_OFFLINE = '1'`을 지정할 수 있다. 캐시가 없으면 오류가 발생한다. 이 변수는 anomalib 데이터 다운로드나 Torch Hub의 URL 다운로드까지 차단하지 않는다.

근거: [anomalib TimmFeatureExtractor](https://github.com/open-edge-platform/anomalib/blob/v2.0.0/src/anomalib/models/components/feature_extractors/timm.py), [timm 로컬 가중치 로딩](https://github.com/huggingface/pytorch-image-models/blob/v1.0.30/timm/models/_builder.py).

## 7. EfficientAD의 teacher·Imagenette 연결

### 7.1 Imagenette

```python
from anomalib.models import EfficientAd

model = EfficientAd(
    imagenet_dir="E:/datasets/imagenette2/train",
    model_size="small",
)
```

anomalib 2.0.0은 `ImageFolder(self.imagenet_dir)`를 직접 호출하므로 클래스 폴더가 있는 `train`을 지정한다. `model_size` 값은 `small` 또는 `medium`이다. 학습용 DataModule의 `train_batch_size`는 1이어야 하며 EfficientAD 내부 정규화와 외부 ImageNet 정규화를 중복 적용하지 않는다.

### 7.2 고정 teacher 경로를 정션으로 연결

확인한 가중치는 다음과 같다. EfficientAD teacher는 ResNet이 아닌 PDN이다.

```text
E:\backbones\efficientad_pretrained_weights\pretrained_teacher_small.pth
E:\backbones\efficientad_pretrained_weights\pretrained_teacher_medium.pth
```

anomalib 2.0.0의 `prepare_pretrained_model()`은 현재 작업 폴더 기준 `./pre_trained/efficientad_pretrained_weights`를 사용한다. 이 경로는 `TORCH_HOME`으로 바뀌지 않는다.

`D:\projects\lightning-tutorial`에서 실행하고 `pre_trained`가 아직 없을 때는 다음 정션으로 원본을 복사하지 않고 연결할 수 있다.

```powershell
rtk proxy cmd /c mklink /J "D:\projects\lightning-tutorial\pre_trained" "E:\backbones"
```

연결 결과는 `프로젝트/pre_trained/efficientad_pretrained_weights` → `E:/backbones/efficientad_pretrained_weights`이다. 기존 `pre_trained`가 있다면 위 명령을 그대로 실행하지 말고 기존 내용을 확인한다. 이번 작업에서는 정션을 만들지 않았다.

### 7.3 정션 없이 teacher 파일을 명시하는 방법

Python에서 실행할 때는 해당 로딩 메서드만 바꾸는 작은 subclass도 가능하다.

```python
import os
import torch
from anomalib.models import EfficientAd


class LocalEfficientAd(EfficientAd):
    def prepare_pretrained_model(self):
        teacher_path = os.path.join(
            "E:/backbones/efficientad_pretrained_weights",
            f"pretrained_teacher_{self.model_size.value}.pth",
        )
        state_dict = torch.load(
            teacher_path,
            map_location="cpu",
            weights_only=True,
        )
        self.model.teacher.load_state_dict(state_dict)


model = LocalEfficientAd(
    imagenet_dir="E:/datasets/imagenette2/train",
    model_size="small",
)
```

이 방식은 teacher 다운로드 처리 대신 지정한 파일을 직접 로드한다.

근거: [EfficientAD v2.0.0 구현](https://github.com/open-edge-platform/anomalib/blob/v2.0.0/src/anomalib/models/image/efficient_ad/lightning_model.py).

## 8. 이 프로젝트의 paths.toml과 구분

현재 프로젝트는 다음처럼 이름을 경로 문자열에 직접 연결한다.

```toml
[datasets]
mvtec = "E:/datasets/mvtec"
btad = "E:/datasets/btad"
visa = "E:/datasets/visa"
imagenette = "E:/datasets/imagenette2"

[backbones]
resnet18 = "E:/backbones/resnet18-f37072fd.pth"
resnet50 = "E:/backbones/resnet50-0676ba61.pth"
efficientad_small = "E:/backbones/efficientad_pretrained_weights/pretrained_teacher_small.pth"
efficientad_medium = "E:/backbones/efficientad_pretrained_weights/pretrained_teacher_medium.pth"
```

프로젝트의 `src.*` 로더는 이 파일을 사용하지만, 설치한 외부 anomalib은 자동으로 읽지 않는다. anomalib을 직접 사용할 때는 앞 절의 `root`, `imagenet_dir`, 로컬 backbone 연결을 명시한다. 프로젝트 자체 EfficientAD Wrapper는 Imagenette 루트를 받고 내부에서 `train`을 연결하는 반면, anomalib 2.0.0에는 `train` 경로를 직접 전달한다.

## 9. 실제 설치·검증 기록

2026-10-22 지정 WinPython의 `Lib/site-packages`에 anomalib 2.0.0과 보완 의존성을 설치했다. 설치 전후 패키지 목록을 비교한 결과 기존 패키지의 버전 변경·삭제는 없었으며, 최종적으로 42개 패키지가 추가됐다. 설치 중 새로 추가된 pandas 3.0.6은 호환성 확인 후 2.2.3으로 교체했다.

| 확인 항목 | 실제 결과 |
|---|---|
| 패키지 경로 | 지정 WinPython의 `Lib/site-packages/anomalib` |
| 의존성 검사 | 최종 `pip check`: `No broken requirements found.` |
| 주요 import | `MVTecAD`, `Stfpm`, `EfficientAd`, `Engine` 성공 |
| CUDA | 11.8, `torch.cuda.is_available()` → `True` |
| GPU 연산 | CUDA 텐서 덧셈 결과 `[2.0, 2.0]` 확인 |
| CLI | 지정 Python의 `-m anomalib.cli.cli --help` 종료 코드 0 |
| MVTec bottle | train 209, valid 83, test 83, 첫 이미지 `(3, 900, 900)` |
| timm 로컬 ResNet18 | 명시한 `.pth` 로딩과 특징 추출 성공 |
| STFPM 로컬 ResNet18 | 문서의 timm 등록 예시로 생성·eval forward 성공, anomaly map `(1, 1, 64, 64)` |
| EfficientAD | 문서의 subclass로 small·medium teacher state_dict 복원 성공 |
| Imagenette | 기존 `train` 이미지 9,469개 인식 |
| 문서 인코딩 | 엄격한 UTF-8 디코딩·한글 본문 확인 |

MVTec 검증은 기본 `ValSplitMode.SAME_AS_TEST` 설정이므로 valid와 test가 같은 83개다. 독립된 검증·테스트 분할 성능을 확인한 결과가 아니다. backbone·teacher·데이터 경로 확인은 소켓 연결을 차단한 프로세스에서 수행했다. STFPM forward는 합성 입력 1개로 확인했으며, 학습한 모델의 정확도를 뜻하지 않는다.

실행 중 timm의 deprecated import, torchvision `ToTensor` 폐기 예정 경고가 있었다. 제한된 실행 환경에서는 OpenVINO telemetry가 사용자 폴더를 만들지 못했다는 경고와 전송하지 않는다는 메시지도 출력됐다. CLI 모듈 실행에는 `runpy` RuntimeWarning이 있었지만 도움말은 정상 출력됐고 종료 코드는 0이었다. 패키지 소스를 수정해 경고를 숨기지는 않았다.

데이터셋과 pretrained 가중치는 다운로드하지 않았다. 데이터·가중치 원본, `paths.toml`, WinPython INI, 사용자·시스템 환경변수는 변경하지 않았다. 캐시 설정과 정션 생성은 문서의 적용 방법이며 자동 적용한 설정이 아니다. 학습·평가·성능 측정과 OpenVINO export는 이번 설치 확인 범위에 포함하지 않는다.

### 추가된 패키지의 최종 버전

아래는 이번 설치로 추가된 패키지 목록이다. 기존 패키지를 포함한 전체 환경의 lock 파일은 아니다. 재설치 명령은 주요 호환성 버전을 고정하지만 나머지 간접 의존성은 설치 시점에 다시 결정될 수 있다. 정확한 재현이 필요하면 아래 버전도 constraints로 함께 고정한다.

```text
anomalib==2.0.0
av==18.1.0
certifi==2026.10.19
charset-normalizer==3.5.2
cloudpickle==3.1.2
contourpy==1.3.3
cycler==0.12.1
einops==0.8.2
fonttools==4.67.0
freia==0.2
ftfy==6.3.1
imageio==2.38.1
joblib==1.6.0
kiwisolver==1.5.1
kornia==0.8.3
kornia-rs==0.2.0
lazy-loader==0.6
markdown-it-py==4.2.0
matplotlib==3.11.2
mdurl==0.1.2
omegaconf==2.4.0
open-clip-torch==2.24.0
opencv-python==4.11.0.86
openvino==2024.6.0
openvino-telemetry==2025.2.0
pandas==2.2.3
protobuf==7.36.2
pyparsing==3.3.3
python-dotenv==1.0.1
pytz==2026.5
regex==2026.9.29
requests==2.32.5
rich==15.0.0
rich-argparse==1.8.0
scikit-image==0.26.0
scikit-learn==1.6.1
scipy==1.17.1
sentencepiece==0.2.2
threadpoolctl==3.7.0
tifffile==2026.3.3
tzdata==2026.5
urllib3==2.8.0
```
