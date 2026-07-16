# FFT ROI Analysis GUI 시스템 구조

| 항목 | 값 |
| --- | --- |
| 상태 | Active |
| 작성일 | 2026-07-16 |
| 적용 범위 | 프로젝트 구조, module 책임, data flow 및 thread model |
| 관련 문서 | [상세 기술 문서와 문서 색인](../README.md) |

## 문서 목적

이 문서는 FFT ROI Analysis GUI의 현재 확정된 시스템 구조 기준을 정의하는 canonical 문서다. 분석 수식, 설정 schema와 출력 column은 이 문서에서 확정하지 않는다. data·ROI·profile의 초기 공개 API는 아래 API 우선 구현 기준을 따른다.

## 현재 확정 기준

### 목표 프로젝트 구조

```text
.
├── AGENTS.md
├── README.md
├── run_gui.py
├── docs/
├── requirements/
│   ├── runtime.txt
│   ├── development.txt
│   └── build.txt
├── ui/
│   └── main_window.ui
├── src/
│   ├── gui/
│   ├── config/
│   ├── io/
│   ├── analysis/
│   ├── outputs/
│   └── workflows/
├── configs/
├── templates/
│   └── slides/
├── packaging/
│   └── fft_analysis_gui.spec
├── scripts/
│   └── build_exe.ps1
├── tests/
└── outputs/
```

### Module 책임

| 경로 | 책임 |
| --- | --- |
| `run_gui.py` | GUI application entry point |
| `ui/main_window.ui` | Qt Designer UI 원본 |
| `src/gui` | window, widget, signal/slot과 worker 제어 |
| `src/config` | ROI 및 분석 설정 schema, validation과 JSON |
| `src/io` | MIM 재귀 탐색, metadata와 image loading |
| `src/analysis` | 회전, ROI, profile, P2V, FFT와 Top-K 계산 |
| `src/outputs` | CSV, PNG와 PPTX 생성 |
| `src/workflows` | 단일 및 batch 처리, 진행률, 취소와 오류 수집 |
| `packaging` | PyInstaller onedir build 설정 |
| `tests` | 수치, GUI와 배포 smoke test |

### API 우선 구현

GUI 구현 전에 합성 data, ROI와 profile API를 검증한다. 초기 구현에서는 `src/api.py` 한 파일만 생성하며, 이 파일은 `create_data`, `load_data`, `show_data`, `load_roi`, `show_roi`, `load_profile`, `show_profile` 공개 함수를 제공한다.

- 모든 개별 API는 `data_path`와 `rotation`을 직접 받는다.
- `create_data`는 runtime 또는 인접 프로젝트 dependency 없이 TIFF 형식의 `.mim` 합성 이미지를 생성한다. 생성 이미지는 data·ROI·profile 검증 전용이며 실제 분석 결과의 golden reference는 아니다.
- 현재 검증 단계의 API는 dataclass나 타입힌트 대신 명시된 dictionary key를 반환한다.
- `show_*`는 blocking UI를 열지 않고 Matplotlib figure를 반환한다.
- notebook은 `from src.api import ...`만 사용해 API를 셀 단위로 검증한다.
- data, ROI와 profile API는 기능 검증이 완료될 때까지 `src/api.py` 한 파일에 유지한다.
- `src` 하위 folder와 기능별 source file 분리는 별도 계획과 검증을 승인한 후에만 수행한다.
- FFT, 저장, batch, PPTX와 GUI는 이 초기 API 확정 범위에 포함하지 않는다.

### 책임 경계와 data flow

GUI는 사용자 입력과 화면 상태를 관리하고 workflow에 작업을 요청한다. workflow는 파일 탐색 또는 분석 실행을 조정하며 I/O, 설정, 분석 및 출력 역할을 연결한다. I/O는 MIM 탐색, 식별 정보와 image loading을 맡고, analysis는 이미지와 ROI를 분석한다. outputs는 workflow가 전달한 결과를 CSV, PNG 및 PPTX로 저장한다.

```text
사용자 입력
    -> GUI
    -> workflow
    -> config, I/O, analysis, outputs
    -> 결과·진행률·오류
    -> GUI 표시 또는 파일 저장
```

- 파일 검색은 선택 root에서 MIM 항목과 식별 정보를 수집해 GUI 목록에 제공한다.
- 미리보기와 현재 파일 분석은 선택 파일, 현재 설정과 ROI를 사용해 분석 결과를 GUI에 제공한다.
- batch 분석은 선택 항목 또는 전체 목록을 순차 처리하고, 파일·ROI·direction 단위 오류를 수집하면서 취소되지 않은 항목을 계속 처리한다.
- 결과 저장은 workflow의 단일 경로 생성 계층에서 관리한다. GUI widget과 분석 함수는 출력 경로를 직접 조합하지 않는다.

### thread model

- GUI binding은 PyQt5를 사용한다.
- `ui/main_window.ui`를 Qt Designer UI의 원본으로 관리하며 `pyuic5` 생성 파일은 직접 수정하지 않는다.
- GUI thread에서 폴더 검색, MIM loading, batch FFT나 다수 파일 저장을 수행하지 않는다.
- 장시간 작업은 `QThread` worker에서 수행하고 signal/slot으로 결과, 진행률, 오류와 취소 상태를 전달한다.
- worker는 QWidget을 직접 변경하지 않는다.
- 작업 ID 또는 취소 상태를 검사해 이전 비동기 결과가 새 화면 상태를 덮어쓰지 않게 한다.

### 외부 경계

- `260713_fft-analysis-common-ver1`은 분석 결과의 golden result 참고 대상이다.
- 인접 프로젝트의 코드를 runtime에 import하거나 해당 프로젝트의 절대 경로에 의존하지 않는다.
- 필요한 기능은 이 저장소의 역할별 module로 이관한다.

## 범위 경계

- 화면 layout과 사용자의 interaction은 [GUI layout 명세](gui-layout-spec.md)에서 정의한다.
- 제품 기능과 비기능 요구사항은 [제품 요구사항](../product/product-spec.md)에서 정의한다.
- 분석, 설정, 출력의 세부 계약은 현재 [상세 기술 문서](../README.md)에 유지하며 후속 spec 문서로 분리한다.

## 향후 확정 필요

- module 간 허용 import 방향과 dependency 검증 방법
- worker의 lifecycle, queue 정책과 상세 error type
- 결과 object 및 cancellation 상태의 구체적인 data contract
