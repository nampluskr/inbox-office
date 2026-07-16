# FFT ROI Analysis GUI 상세 기술 문서

| 항목 | 값 |
| --- | --- |
| 상태 | Active |
| 최종 수정일 | 2026-07-16 |
| 적용 범위 | 문서 색인, 분석, 설정, 출력, 개발, 배포와 검증 |
| 관련 계획 | [0001-documentation-structure-plan.md](development/plans/0001-documentation-structure-plan.md), [0002-product-and-design-documents-plan.md](development/plans/0002-product-and-design-documents-plan.md), [0003-single-api-data-roi-profile-plan.md](development/plans/0003-single-api-data-roi-profile-plan.md), [0004-single-api-consolidation-plan.md](development/plans/0004-single-api-consolidation-plan.md), [0005-apply-python-writing-rules-plan.md](development/plans/0005-apply-python-writing-rules-plan.md), [0006-public-function-only-api-plan.md](development/plans/0006-public-function-only-api-plan.md), [0007-api-contract-repair-plan.md](development/plans/0007-api-contract-repair-plan.md), [0008-synthetic-mim-data-plan.md](development/plans/0008-synthetic-mim-data-plan.md) |

## 문서 목적

이 문서는 FFT ROI Analysis GUI의 문서 색인이며, 아직 역할별 문서로 분리되지 않은 상세 기준의 canonical 기술 문서다. 루트 [README.md](../README.md)는 프로젝트를 요약하고, 루트 [AGENTS.md](../AGENTS.md)는 운영과 변경 관리 규칙만 정의한다.

제품, 시스템 구조와 GUI 기준은 역할별 문서로 분리됐으며 이 문서에는 같은 상세 내용을 반복하지 않는다. 분석, 설정, 출력, 개발, 배포와 검증 기준은 후속 상세 문서가 생성될 때까지 이 문서에서 관리한다.

## 문서 읽기 순서

1. [제품 요구사항](product/product-spec.md)
2. [시스템 구조](design/system-architecture.md)
3. [GUI layout 명세](design/gui-layout-spec.md)
4. 이 문서의 분석, 설정, 출력, 개발, 배포와 검증 기준

## Canonical 문서 책임

| 문서 | 책임 |
| --- | --- |
| [제품 요구사항](product/product-spec.md) | 사용자, 제품 범위, 기능 및 비기능 요구사항 |
| [시스템 구조](design/system-architecture.md) | 프로젝트 구조, module 책임, data flow 및 thread model |
| [GUI layout 명세](design/gui-layout-spec.md) | 화면 영역, interaction과 화면 상태 |
| 이 문서 | 분석, 설정, 출력, 개발, 배포와 검증 기준 |

## 현재 이 문서가 유지하는 상세 기준

## Python 코드 기준

- Python 파일의 첫 줄은 `# 파일경로: 1줄 영어 설명` 형식의 주석으로 시작하고 둘째 줄은 빈 줄로 둔다.
- Python 코드에는 타입힌트를 사용하지 않는다. API 반환값과 필수 key는 canonical 문서와 notebook assert로 확인한다.
- 경로 처리는 `pathlib.Path`보다 `os.path`를 우선 사용한다.
- Notebook 전역변수는 `SNAKE_CASE`로 작성하고, 입력·출력·보고 경로와 batch 식별자는 `DATA_ROOT`, `OUTPUT_ROOT`, `REPORT_ROOT`, `BATCH_NAME`으로 관리한다.
- Notebook에는 설정 선언, 공개 API 호출과 결과 확인만 두며 재사용 목적의 함수를 정의하지 않는다.
- 현재 data·ROI·profile API는 `src/api.py`에서 제공한다. 기능별 source file 분리는 해당 API 검증 후 별도 계획에서 수행한다.
- `create_data(output_dir, num_data=1, seed=42)`는 외부 MIM 데이터가 없는 환경에서 검증할 수 있도록 TIFF 형식의 `.mim` 합성 이미지를 생성한다. 생성 데이터는 가로·세로 방향의 주기성 얼룩을 함께 포함하며, 같은 seed와 출력 경로에서는 기존 파일을 재사용한다.
- GUI, 설정, MIM I/O, 분석, 출력과 workflow의 책임을 분리한다.
- GUI widget과 분석 함수에서 출력 경로를 직접 조합하지 않는다.
- 파일명과 출력 경로는 workflow의 단일 경로 생성 계층에서 관리한다.
- 사용자 오류에는 가능한 경우 입력 파일, ROI key, direction과 실패 원인을 포함한다.
- 기존 분석을 최적화하거나 재작성할 때는 golden result가 허용 오차 안에서 일치해야 한다.
- horizontal lines 분석은 ROI의 x축 평균 투영으로 y축 profile과 y축 mm scale을 사용하고, vertical lines 분석은 ROI의 y축 평균 투영으로 x축 profile과 x축 mm scale을 사용한다.
- pixel-mm 변환값은 각 입력 이미지의 해상도와 사용자가 지정한 실제 이미지 가로·세로 길이로 계산한다.

## MIM 탐색과 식별

- 선택 root 아래 모든 하위 폴더에서 확장자가 `.mim`인 파일을 재귀적으로 수집한다.
- 탐색 결과를 정렬하고 절대 경로만으로 화면 label을 구성하지 않는다.
- 각 항목에는 상대 경로, 부모 폴더, 원본 파일명, sample ID와 절대 경로를 유지한다.
- `sample_id`는 기존 분석 호환을 위해 기본적으로 파일명 앞 16자를 사용한다.
- 동일한 sample ID가 여러 경로에 있을 수 있으므로 내부 식별에는 정규화된 원본 경로를 함께 사용한다.
- 읽을 수 없거나 2D grayscale이 아닌 MIM 파일은 원인과 함께 오류 목록에 기록한다.

| field | 설명 |
| --- | --- |
| `relative_path` | 선택 root 기준 상대 경로 |
| `parent_name` | 파일의 직접 부모 폴더 |
| `sample_id` | 기본적으로 파일명 앞 16자 |
| `source_filename` | 확장자를 포함한 원본 파일명 |
| `source_path` | 정규화된 절대 경로 |

## ROI와 분석 스펙

### ROI 규칙

- ROI 좌표는 전체 이미지에 대한 `[0, 1]` 범위의 `xmin`, `xmax`, `ymin`, `ymax`로 저장한다.
- ROI key는 설정 내에서 유일하며 결과 파일명과 CSV 식별자에 사용한다.
- `0 <= xmin < xmax <= 1`, `0 <= ymin < ymax <= 1`을 만족해야 한다.
- pixel 좌표로 변환한 ROI는 이미지 범위 안에 있고 profile과 FFT에 필요한 최소 크기를 만족해야 한다.
- batch 실행 시 사용한 설정을 결과 폴더의 `config_snapshot.json`으로 저장한다.

### 분석 방향

방향 이름은 선 얼룩의 방향을 의미하며 profile의 위치 축과 구분한다.

| 분석 방향 | ROI 투영 | 생성 profile | mm scale |
| --- | --- | --- | --- |
| `horizontal` | x축 평균 `mean(axis=1)` | y축 profile | y축 pixel-mm scale |
| `vertical` | y축 평균 `mean(axis=0)` | x축 profile | x축 pixel-mm scale |

- 회전이 활성화되면 회전된 이미지의 해상도와 실제 가로·세로 길이를 기준으로 ROI와 pixel-mm scale을 계산한다.
- FFT 결과에는 pixel 및 mm 기준 frequency와 period를 구분되는 column 이름으로 저장한다.
- Top-K peak는 intensity 내림차순 rank, frequency와 period를 포함한다.
- profile이 너무 짧거나 non-finite 값을 포함하면 FFT를 실행하지 않고 식별 가능한 오류로 처리한다.

## ROI 설정 JSON 계약

설정은 UTF-8 JSON으로 저장하며 schema version, 이미지, 분석 parameter와 ROI 목록을 포함한다.

```json
{
  "schema_version": 1,
  "image": {
    "rotation_angle": 0,
    "width_mm": 100.0,
    "height_mm": 50.0
  },
  "analysis": {
    "directions": ["horizontal", "vertical"],
    "average_filter_size": 3,
    "reference_filter_size": 101,
    "top_k": 10
  },
  "rois": [
    {
      "key": "roi_1",
      "name": "ROI 1",
      "color": "#ff0000",
      "xmin": 0.1,
      "xmax": 0.4,
      "ymin": 0.2,
      "ymax": 0.8
    }
  ]
}
```

설정 로딩 시 schema version, 필수 field, ROI key 중복, 좌표 순서와 범위를 검증한다.

## 결과 저장 계약

```text
outputs/{batch_name}/
├── log/
│   ├── data_summary.csv
│   └── analysis_errors.csv
├── config_snapshot.json
├── {condition}/
│   └── {sample_id}/
│       ├── {sample_id}-{condition}-overview.png
│       ├── {sample_id}-{condition}-overview-roi.png
│       ├── {sample_id}-{condition}-profiles.csv
│       ├── {sample_id}-{condition}-peak-to-valley.csv
│       ├── {sample_id}-{condition}-fft-intensity.csv
│       ├── {sample_id}-{condition}-top{K}-peaks.csv
│       └── {sample_id}-{condition}-{roi_key}-{direction}.png
└── {batch_name}-{condition}.pptx
```

### CSV

- CSV는 UTF-8, comma delimiter와 header 포함 형식으로 저장한다.
- 공통 식별 column은 `condition`, `sample_id`, `source_filename`, `roi_key`, `direction`이다.
- profile 결과에는 위치 축, pixel과 mm 위치, blur, reference와 profile percent를 포함한다.
- FFT 결과에는 FFT bin, pixel 및 mm 기준 frequency와 period, intensity를 포함한다.
- Top-K 결과에는 rank를 추가한다.

### PPTX template

- template이 선택되지 않으면 PPTX 기능만 비활성화한다.
- CSV와 PNG 저장은 template과 관계없이 동작한다.
- template은 한 장의 기준 slide를 사용한다.
- 기준 slide에는 하나의 overview picture slot과 선택된 ROI 결과 수에 맞는 slot이 있어야 한다.
- 가장 넓은 picture slot을 overview 위치로 판단한다.
- 나머지 ROI slot은 좌측에서 우측, 위에서 아래 순서로 적용한다.
- slot 수가 필요한 이미지 수와 다르면 저장을 시작하기 전에 오류를 표시한다.
- 사용자 template은 외부 파일로 선택하고 EXE에 내장하지 않는다.

### Batch 오류

개별 파일, ROI 또는 direction 분석이 실패해도 사용자가 취소하지 않은 경우 다음 항목을 계속 처리한다. `analysis_errors.csv`에는 다음 정보를 기록한다.

```text
source_path, sample_id, roi_key, direction, stage, error_type, message
```

## 개발 환경

### 표준 Python

```text
WinPython root: C:\winpython\WPy64-31180
Python: C:\winpython\WPy64-31180\python-3.11.8.amd64\python.exe
Python version: 3.11.8, 64-bit
```

개발과 테스트는 `.venv-dev`, Windows 배포는 `.venv-build`를 사용한다. `.venv-build`에는 runtime과 build package만 설치하고 test package는 설치하지 않는다.

| package | 초기 역할 | 최적화 방향 |
| --- | --- | --- |
| `PyQt5` | Windows GUI와 Qt widget | 유지 |
| `numpy` | 배열, projection과 FFT | 유지 |
| `scipy` | filter와 peak 탐색 | golden test 이후 NumPy 대체 검토 |
| `pandas` | 초기 CSV table 호환 | 표준 `csv`와 내부 record로 대체 검토 |
| `matplotlib` | 초기 분석 plot 호환 | Qt 기반 plot으로 대체 검토 |
| `tifffile` | MIM/TIFF loading | 유지 |
| `python-pptx` | template 기반 PPTX | 유지 |
| `PyInstaller` | Windows onedir 배포 | build 환경에서만 사용 |
| `pytest`, `pytest-qt` | 수치와 GUI 검증 | 개발 환경에서만 사용 |

PyQt5, PyInstaller, pytest와 pytest-qt는 현재 표준 WinPython 환경에 설치되어 있지 않으므로 별도 환경에 추가해야 한다.

### 환경 생성

```powershell
$PYTHON = "C:\winpython\WPy64-31180\python-3.11.8.amd64\python.exe"
& $PYTHON -m venv .venv-dev
& $PYTHON -m venv .venv-build
& .\.venv-dev\Scripts\python.exe -m pip install --upgrade pip
& .\.venv-build\Scripts\python.exe -m pip install --upgrade pip
& .\.venv-dev\Scripts\python.exe -m pip install -r requirements\runtime.txt
& .\.venv-dev\Scripts\python.exe -m pip install -r requirements\development.txt
& .\.venv-build\Scripts\python.exe -m pip install -r requirements\runtime.txt
& .\.venv-build\Scripts\python.exe -m pip install -r requirements\build.txt
```

requirements 파일이 생성되기 전에는 runtime에 PyQt5, NumPy, SciPy, Pandas, Matplotlib, tifffile과 python-pptx를 사용한다. development에는 pytest와 pytest-qt, build에는 PyInstaller를 추가한다.

### Qt Designer와 실행

```powershell
& .\.venv-dev\Scripts\pyuic5.exe ui\main_window.ui -o src\gui\generated\ui_main_window.py
& .\.venv-dev\Scripts\python.exe run_gui.py
```

최종 EXE에는 `.ui`, Qt Designer와 `pyuic5`를 포함하지 않는다.

## Windows 배포

PyInstaller `onedir`를 기본 mode로 사용한다. 대상 PC에는 Python을 설치하지 않으며 다음 폴더 전체를 배포한다.

```text
dist/fft-analysis-gui/
├── fft-analysis-gui.exe
├── _internal/
└── LICENSES/
```

```powershell
& .\.venv-build\Scripts\pyuic5.exe ui\main_window.ui -o src\gui\generated\ui_main_window.py
& .\.venv-build\Scripts\pyinstaller.exe --clean packaging\fft_analysis_gui.spec
```

- `packaging/fft_analysis_gui.spec`를 build 설정의 단일 기준으로 사용한다.
- test, Notebook, IPython, Tkinter, 예제, translation과 미사용 Qt module은 import 분석과 smoke test 후 제외한다.
- 필요한 Qt DLL이나 platform plugin을 크기만을 이유로 임의 삭제하지 않는다.
- UPX는 별도 실험 build에서 Qt plugin, 실행 안정성과 보안 제품 오탐을 확인한 뒤 적용한다.
- PyQt5 배포는 GPL 호환 조건 또는 유효한 상용 license가 확인된 경우에만 수행한다.

참고 문서:

- [Riverbank License FAQ](https://www.riverbankcomputing.com/commercial/license-faq)
- [PyInstaller Operating Mode](https://pyinstaller.org/en/latest/operating-mode.html)
- [PyInstaller Usage](https://pyinstaller.org/en/stable/usage.html)
- [Nuitka PyQt5 Support](https://nuitka.net/info/pyqt5.html)

## 배포 크기 최적화

EXE 단독 크기가 아니라 전체 `dist/fft-analysis-gui` 폴더와 ZIP 크기를 평가한다. 각 build에서 EXE, 전체 폴더, ZIP, cold start 시간과 포함 파일 목록을 기록한다.

현재 WinPython 설치 기준 source package 크기는 SciPy 약 113 MiB, Pandas 약 64 MiB, NumPy 약 33 MiB, Matplotlib 약 28 MiB다. 실제 배포 크기는 baseline build에서 다시 측정한다.

1. 기존 NumPy, SciPy, Pandas와 Matplotlib 분석으로 기준 결과와 baseline을 확보한다.
2. Pandas를 dataclass, NumPy 배열과 표준 `csv`로 교체하고 CSV를 비교한다.
3. Matplotlib을 Qt 기반 plot 계층으로 교체하고 축, peak와 주기 표시를 비교한다.
4. SciPy `uniform_filter`와 `find_peaks`를 NumPy 기반 구현으로 교체하고 수치 결과를 비교한다.
5. golden test를 통과하고 실제 배포 크기가 감소한 단계만 유지한다.

## 검증 기준

- unit, integration, GUI와 packaging smoke test를 역할별로 분리한다.
- common-ver1 결과를 golden result로 사용해 horizontal과 vertical profile, FFT와 Top-K를 비교한다.
- 한글과 공백이 포함된 경로에서 폴더 검색, 설정, CSV, PNG와 PPTX 출력을 확인한다.
- 읽을 수 없는 파일이 있어도 검색과 batch 전체가 중단되지 않는지 확인한다.
- ROI 저장과 재로딩 후 좌표가 일치하는지 확인한다.
- template이 없을 때 PPTX만 비활성화되는지 확인한다.
- 진행률과 취소가 동작하고 분석 중 GUI가 응답하는지 확인한다.
- clean Windows 10/11 x64에서 Python 설치 없이 실행되는지 확인한다.
- baseline과 각 최적화 단계의 EXE, 전체 폴더, ZIP 크기와 시작 시간을 기록한다.
- Markdown과 JSON의 UTF-8, 한글, 대체 문자와 이모지 포함 여부를 확인한다.

## 향후 상세 문서 분리 계획

생성된 문서는 실제 link로, 아직 생성하지 않은 문서는 code 형식의 예정 경로로 표시한다.

| 우선순위 | 예정 경로 | 역할 |
| ---: | --- | --- |
| 1 | [docs/product/product-spec.md](product/product-spec.md) | 사용자, 범위, 기능과 비기능 요구사항 |
| 2 | [docs/design/system-architecture.md](design/system-architecture.md) | module, dependency, data flow와 thread model |
| 3 | [docs/design/gui-layout-spec.md](design/gui-layout-spec.md) | 화면 layout, widget, 상태와 interaction |
| 4 | `docs/specs/analysis-spec.md` | ROI, profile, FFT, Top-K와 수치 규칙 |
| 5 | `docs/specs/configuration-spec.md` | JSON schema, 기본값과 validation |
| 6 | `docs/specs/output-spec.md` | CSV, PNG, PPTX, 경로와 오류 log |
| 7 | `docs/development/development-workflow.md` | 문서, 구현과 검증 반복 절차 |
| 8 | `docs/development/environment.md` | Python, dependency와 UI 생성 |
| 9 | `docs/development/coding-guidelines.md` | Python과 PyQt5 구현 규칙 |
| 10 | `docs/development/packaging.md` | PyInstaller와 크기 최적화 |
| 11 | `docs/verification/test-strategy.md` | test 계층, golden data와 인수 기준 |
| 12 | `docs/verification/reports/NNNN-topic-report.md` | 작업별 실제 검증 결과 |
| 13 | `docs/decisions/NNNN-decision-name.md` | 중요한 결정과 근거 |

문서 구조의 기본 원칙은 [문서 구조 및 작성 계획](development/plans/0001-documentation-structure-plan.md)을, 이번 분리 작업의 범위와 완료 기준은 [0002 제품 및 설계 문서 분리 계획](development/plans/0002-product-and-design-documents-plan.md)을 따른다.
