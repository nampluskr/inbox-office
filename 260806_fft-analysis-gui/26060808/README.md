# FFT ROI Analysis GUI ver0

## 프로젝트 소개

FFT ROI Analysis GUI는 `.mim` 2D grayscale 이미지의 관심 영역(ROI)을 대상으로 가로줄과 세로줄 얼룩의 주기성을 분석하는 Windows 데스크톱 도구다.

## 현재 상태

새 구현은 `docs/README.md`의 구현 stage 목록에 따라 단계별로 진행 중이다. `src/fft.py`, `src/gui.py`, `src/gui.ui` 3파일 구조가 구현되어 있으며, 현재까지 완료된 범위는 다음과 같다.

- stage-01: `Settings`/API 골격과 GUI 창(splitter, 탐색기, Image/Analysis/Settings 탭) 골격
- stage-02: root 폴더 선택, `.mim` 파일 탐색·표시, 이미지 로딩과 Canvas 렌더링
- stage-03: 이미지 최초 로딩 시 기본 ROI(전체 이미지) 자동 생성과 Canvas 오버레이 표시

이후 stage(ROI 편집, Settings 전역 설정, profile/FFT/band-pass/peak-to-valley 분석, CSV 저장 등)는 아직 미구현이며 진행 상태는 `docs/README.md`를 참조한다.

`refs/legacy1/`과 `refs/legacy2/`에는 이전 세대 코드와 현재까지의 구현이 참고용으로 보존된다. 두 경로는 런타임에서 사용하지 않는다.

## 이전 구현 참고 기능

- synthetic `.mim` 샘플 생성 (`create_data`)
- `.mim` 파일 탐색 및 ROI 기준 데이터 로딩 (`get_paths`, `get_data`)
- ROI overlay 이미지 표시 (`show_data`)
- 가로줄(horizontal)/세로줄(vertical) 1차원 intensity profile 추출 및 표시 (`get_profile`, `show_profile`)
- profile peak/valley 탐색 및 표시 (`get_profile_peaks`, `show_profile_peaks`)
- peak-to-valley amplitude 차이 계산 (`get_peak2valley`)
- FFT amplitude spectrum 계산 및 표시 (`get_fft`, `show_fft`)
- FFT 지배 주파수 peak 탐색 및 표시 (`get_fft_peaks`, `show_fft_peaks`)
- profile, profile peaks, peak-to-valley, FFT 결과의 CSV 저장 (`save_*_csv`)
- root 하위 `.mim` 재귀 검색과 단일 파일 선택
- 이미지 위 공통 ROI 생성·이동·크기 변경
- ROI별 profile과 FFT intensity 자동 plot
- 회전, 분석 방향과 실제 이미지 크기를 관리하는 PyQt GUI (`refs/legacy2/src/gui.py`)

## 개발 환경

- 대상 플랫폼: Windows
- Python 인터프리터: WinPython, `C:\winpython\WPy64-31180\python-3.11.8.amd64\python.exe` (PyQt5 5.15.9 설치됨)
- GUI 의존성: PyQt5, matplotlib, numpy, tifffile
- WSL을 사용하지 않는다.

새 GUI는 저장소 루트에서 다음 명령으로 실행한다.

```bash
"C:\winpython\WPy64-31180\python-3.11.8.amd64\python.exe" -m src.gui
```

`-m src.gui`로 실행해야 `src` 패키지의 절대 import가 정상 동작한다. 이전 GUI의 실행 방법은 `refs/legacy2/`의 코드와 문서를 참고한다.

## 배포 형태 (계획)

최소 GUI는 PyQt5 widget 코드로 구현되어 있다. 최종 사용자가 Python을 별도로 설치하지 않도록 PyInstaller `onedir`로 exe와 runtime 파일이 포함된 전체 폴더를 전달하는 배포는 아직 계획 단계다.

## 폴더 구조

```text
.
├── AGENTS.md
├── README.md
├── docs/
├── refs/
│   ├── legacy1/
│   └── legacy2/
├── src/
│   ├── fft.py
│   ├── gui.py
│   └── gui.ui
├── data/
│   └── synthetic/
└── outputs/
```

## 문서 안내

새 구현의 문서 색인은 [docs/README.md](docs/README.md)를 참조한다. 이전 구현의 문서 색인과 작성 이력은 [refs/legacy2/docs/README.md](refs/legacy2/docs/README.md)에 보관한다.
