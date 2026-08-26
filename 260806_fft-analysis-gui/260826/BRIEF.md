# FFT ROI Analysis GUI 리팩터링 브리프

## 문서 상태

- 상태: Draft
- 적용 대상: PyQt 기반 현재 구현을 대체할 차기 구현
- 상세 기술 기준: [SPEC.md](SPEC.md)
- 기존 수치 분석 계약: [../spec/fft-spec.md](../spec/fft-spec.md)

## 사용자 의도

사용자는 `.mim` 2D grayscale 이미지에서 ROI를 지정하고, 가로줄과 세로줄 얼룩의 주기성을 profile, FFT spectrum, band-pass profile 및 peak-to-valley 값으로 확인할 수 있는 Windows 데스크톱 프로그램을 필요로 한다.

현재 PyQt 기반 구현은 파일 탐색, 이미지 표시와 기본 ROI 표시까지 진행되었다. 차기 구현은 사용자 화면을 Electron 기반으로 다시 구성하고, 검증된 Python 수치 계산 생태계는 독립 분석 엔진으로 유지한다. 최종 사용자는 Python이나 Node.js를 별도로 설치하지 않고 하나의 Windows 설치 프로그램으로 제품을 설치할 수 있어야 한다.

## 리팩터링 목적

1. Electron과 React를 사용해 파일 탐색, 탭, 설정, ROI 편집 및 분석 결과 표시를 일관된 웹 UI로 제공한다.
2. `.mim` 로딩과 FFT 계산은 Python, tifffile 및 NumPy에 유지하여 기존 분석 결과와의 동등성을 보존한다.
3. 화면용 profile과 spectrum은 Electron Renderer의 Plotly.js 대화형 차트로 표시한다.
4. 보고서용 그래프도 같은 분석 결과와 Plotly.js figure 정의로 고정 크기 PNG를 생성해 화면과 보고서의 수치·스타일 차이를 방지한다.
5. 생성된 PNG를 Python의 `python-pptx`로 템플릿 슬라이드에 삽입해 PPTX 보고서를 작성한다.
6. Electron과 Python 사이에 명시적인 요청·응답 계약을 두어 UI와 분석 로직을 분리한다.
7. Python runtime과 분석·PPTX 의존성을 Electron 설치 프로그램에 포함해 독립 실행 가능한 Windows 제품으로 배포한다.

## 제품 개요

사용자는 다음 흐름으로 프로그램을 사용한다.

1. Root Folder를 선택한다.
2. Explorer에서 `.mim` 파일을 선택한다.
3. 회전된 grayscale 이미지와 공통 ROI overlay를 확인한다.
4. ROI를 추가·삭제하거나 코너를 드래그하고 정규화 좌표를 직접 편집한다.
5. ROI와 분석 방향을 선택한다.
6. dL/L(%) profile, FFT spectrum, 주요 peak, band-pass profile 및 peak-to-valley 결과를 확인한다.
7. 필요한 분석 결과를 CSV로 저장한다.
8. 고정 크기로 내보낸 Plotly.js PNG와 PPTX 템플릿으로 보고서를 생성하고 최종 PNG를 미리 본다.

GUI의 탭, 버튼, 레이블, 상태 및 오류 메시지는 영어로 표시한다.

## 목표 아키텍처

```text
Electron main process
├── BrowserWindow와 애플리케이션 수명 주기
├── Folder Picker와 Root 경계 검증
├── 제한된 IPC handler
├── Python 분석 엔진 시작·종료
├── Plotly.js 보고서 PNG 저장
└── 설치 리소스, PPTX 템플릿 및 임시 파일 관리

Electron preload
└── Renderer에 최소 typed API만 노출

React Renderer
├── Explorer, Image, Analysis, Settings UI
├── SVG 기반 ROI overlay와 편집
├── Plotly.js 기반 profile 및 spectrum
├── 보고서 전용 고정 크기 Plotly.js figure와 PNG export
├── 최종 보고서 PNG preview
└── 비동기 요청 상태와 오류 표시

Python 분석 엔진
├── tifffile 기반 .mim 로딩
├── Pillow 기반 표시용 PNG 생성
├── NumPy 기반 ROI와 profile 처리
├── FFT, band-pass, peak 및 peak-to-valley 계산
├── CSV 저장
└── python-pptx 기반 템플릿 슬라이드 생성
```

## 핵심 기술 결정

| 영역 | 결정 |
| --- | --- |
| 대상 플랫폼 | Windows x64 |
| 데스크톱 shell | Electron |
| GUI | React + TypeScript + CSS |
| 빌드 | electron-vite |
| 화면 그래프 | Plotly.js |
| 보고서 그래프 | Plotly.js 고정 크기 PNG export |
| 이미지 ROI overlay | React SVG |
| 분석 언어 | Python |
| 이미지 로딩 | tifffile |
| 표시용 이미지 인코딩 | Pillow |
| 수치 계산 | NumPy |
| PPTX 생성 | python-pptx + PPTX 템플릿 |
| Python 패키징 | PyInstaller `onedir` |
| Windows 설치 프로그램 | electron-builder NSIS |
| 프로세스 통신 | Electron main과 지속 실행 Python worker 사이의 NDJSON 요청·응답 |

matplotlib는 화면과 보고서 렌더링에 사용하지 않으며 runtime dependency에 포함하지 않는다. 화면과 보고서는 동일한 Python 분석 결과와 공통 Plotly.js trace·style 정의를 사용한다. 보고서 PNG는 화면 크기와 무관한 전용 off-screen graph에서 `width`, `height`, `scale`을 명시해 생성한다.

## 구현 범위

### 포함 범위

- Root Folder 선택과 `.mim` 파일 탐색
- grayscale 이미지 표시와 회전
- 여러 ROI의 추가, 삭제, 선택, 색상 및 좌표 편집
- 이미지 위 ROI 코너 드래그
- horizontal 및 vertical profile 분석
- dL/L(%) 정규화
- FFT amplitude spectrum과 Top-K peak
- band-pass profile과 peak-to-valley
- Plotly.js 기반 대화형 그래프
- Plotly.js 기반 고정 크기 overview 및 ROI 분석 PNG 생성
- 최종 PNG report preview
- PPTX 템플릿의 고정 slot에 PNG를 삽입한 슬라이드 보고서
- 분석 결과 CSV 저장
- Python 분석 엔진을 포함한 Windows NSIS 설치 프로그램
- 개발·제품 환경에서 동일한 IPC 계약과 구조화된 오류 처리

### 제외 범위

- 브라우저에서 `.mim`을 직접 디코딩하는 JavaScript 구현
- JavaScript 또는 WebAssembly로 NumPy 분석식을 재작성하는 작업
- Renderer에서 Node.js 파일 시스템이나 Python 프로세스를 직접 호출하는 구조
- matplotlib PNG를 연속 갱신해 대화형 그래프를 대신하는 구조
- matplotlib로 별도의 보고서 그래프를 다시 그리는 이중 renderer 구조
- macOS와 Linux 배포
- 클라우드 처리와 외부 서버 의존성
- `refs/legacy1/` 또는 `refs/legacy2/`를 runtime dependency로 사용하는 구조

## 품질 기준

- 동일 입력과 설정에 대한 차기 Python 엔진의 수치 결과는 승인된 기존 기준 결과와 허용 오차 내에서 일치해야 한다.
- ROI 드래그 중에는 Renderer가 overlay를 즉시 갱신하며 Python 응답을 기다리지 않는다.
- 분석은 비동기로 실행하고 Renderer를 정지시키지 않는다.
- 늦게 도착한 이전 요청 결과가 최신 화면 상태를 덮어쓰지 않는다.
- 화면과 보고서 그래프는 동일한 분석 배열, peak와 공통 Plotly.js style 정의를 사용한다.
- 보고서 PNG는 figure 종류별 고정 pixel 크기와 종횡비로 생성하며 PPTX slot에서 늘어나거나 찌그러지지 않는다.
- PPTX 생성 전에 최종 삽입 PNG를 Electron에서 그대로 미리 볼 수 있어야 한다.
- Renderer는 Node.js와 파일 시스템에 직접 접근하지 않는다.
- Python 엔진 오류 또는 비정상 종료가 Electron 앱 전체의 비정상 종료로 이어지지 않는다.
- 설치된 제품은 시스템 Python과 Node.js 설치 여부에 의존하지 않는다.

## 전환 원칙

현재 PyQt 코드는 새 Electron UI의 runtime dependency로 사용하지 않는다. 기존 `src/fft.py`의 분석 계약과 레거시 검증 자료는 Python 엔진을 재구성할 때 기준으로 사용한다.

전환은 다음 순서를 따른다.

1. 대표 `.mim` 데이터와 승인된 수치 결과를 고정한다.
2. GUI와 독립적인 Python 분석 엔진을 완성한다.
3. Electron main, preload, Renderer 골격과 보안 경계를 구성한다.
4. 이미지 표시와 SVG ROI 편집을 연결한다.
5. 분석 배열을 Plotly.js 그래프에 연결한다.
6. 보고서 전용 Plotly.js figure, 고정 크기 PNG export와 preview를 구현한다.
7. python-pptx 템플릿 조립과 PPTX 검증을 구현한다.
8. CSV 저장, 오류 처리와 프로세스 복구를 구현한다.
9. Python 엔진과 Electron 앱을 함께 패키징하고 clean Windows 환경에서 검증한다.
10. 새 구현의 인수 기준이 모두 통과한 뒤 PyQt 진입점을 폐기한다.

PyQt 파일은 새 구현 검증이 끝나기 전에 삭제하지 않는다.

## 최종 산출물

최종 사용자에게는 하나의 NSIS 설치 프로그램을 제공한다. 설치 프로그램에는 Electron 애플리케이션, Plotly.js, Python 분석 엔진, Python runtime, NumPy, tifffile, Pillow, python-pptx, 기본 PPTX 템플릿 및 제품 실행에 필요한 모든 리소스가 포함된다.

제품은 분석 CSV, Plotly.js PNG와 PPTX 슬라이드 보고서를 생성한다. 보고서에 삽입되는 PNG는 Electron의 report preview와 동일한 파일이다.

설치 후 제품 디렉터리에는 Electron과 Python 엔진 파일이 함께 배치될 수 있다. 단일 설치 파일 제공은 보장하지만, 설치 후 모든 구성 요소를 단일 실행 파일 하나로 합치는 것은 목표가 아니다.
