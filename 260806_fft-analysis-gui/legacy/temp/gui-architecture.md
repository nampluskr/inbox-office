# GUI 구조

## 화면 구성

메인 창은 수평 splitter로 좌측 파일 탐색 영역과 우측 탭 영역을 나눕니다.

- 좌측 파일 탐색: root 선택, 새로고침, 검색 결과 수와 단일 선택 `.mim` 상대 경로 목록
- `Canvas` 탭: 회전된 grayscale 이미지, ROI overlay와 마우스 생성·이동·크기 변경
- `Analysis` 탭: 선택 ROI의 crop 이미지, profile과 Top-K FFT peak marker가 있는 FFT intensity
- `Profile` 탭: 선택 방향의 ROI별 mean intensity 곡선
- `FFT Intensity` 탭: 선택 방향의 ROI별 FFT amplitude 곡선
- `Settings` 탭: 회전, 분석 대상 선 방향, 실제 크기, FFT Top-K peak 수, pixel 정보, ROI 목록·이름·색상·좌표와 추가·삭제
- 상태 영역: 현재 파일 로드, 분석 완료 또는 오류 메시지
- GUI의 사용자 표시 문자열은 영어로만 작성

## 사용자 흐름

1. 시작 시 기본 root를 검색하거나 사용자가 다른 root를 선택합니다.
2. 좌측 목록에서 `.mim` 파일 하나를 선택합니다.
3. GUI가 회전된 이미지와 공통 ROI를 표시하고 모든 ROI의 profile과 FFT를 계산합니다.
4. 사용자가 공통 설정을 확정하거나 ROI 조작을 마치면 현재 파일 결과를 자동 갱신합니다.
5. 사용자는 Analysis 탭에서 선택 ROI의 상세 결과를 확인하거나 Profile과 FFT Intensity 탭에서 ROI 색상별 곡선을 비교합니다.

## 책임 경계

```text
PyQt view and state
    -> GUI controller
        -> src.fft public functions
            -> image and plot data
```

- view는 파일 목록, 사용자 입력, ROI 상호작용과 plot rendering을 담당합니다.
- state는 root, 검색 파일, 현재 파일, 공통 설정과 API 호환 ROI를 검증하고 보관합니다.
- controller는 파일 검색, 방향별 단위 계산, API 호출, 선택 ROI Top-K peak 계산, 자동 갱신과 오류 변환을 담당합니다.
- `src.fft`는 이미지 로드와 profile·FFT 계산을 담당하며 GUI를 import하지 않습니다.
- GUI는 FFT·profile 공식을 재구현하지 않습니다.

## 소스 구조

```text
src/
├── fft.py
├── gui.py
└── gui.ui
```

- `fft.py`는 GUI와 독립적인 이미지 로드, profile·FFT 계산, 시각화와 CSV 저장 공개 함수를 제공합니다.
- `gui.py`는 상태, PyQt widget, ROI interaction, controller와 애플리케이션 진입점을 통합합니다.
- `gui.ui`는 Qt Designer에서 편집하는 화면 레이아웃 자산입니다.
- `gui.py`의 controller 책임만 `src.fft` 공개 함수를 호출합니다.
- 기능 구현이 안정된 뒤 `gui.py`의 책임을 별도 모듈로 리팩터링합니다.

## Qt Designer 레이아웃

`src/gui.ui`는 현재 화면 계층을 Qt Designer에서 편집하는 runtime 레이아웃 소스입니다. `src/gui.py`는 시작 시 `uic.loadUi()`로 같은 폴더의 이 파일을 로드합니다.

- `QGraphicsView` placeholder는 실행 시 `ImageView`가 표시되는 Canvas와 선택 ROI crop 영역으로 교체됩니다.
- 일반 `QWidget` placeholder는 실행 시 Matplotlib `AnalysisPlot`이 표시되는 Profile과 FFT 영역으로 교체됩니다.
- `gui.ui`에서 widget의 `objectName`은 `gui.py`의 signal·상태 연결 계약입니다. 레이아웃을 변경할 때 기존 object name을 변경하거나 삭제하면 해당 코드를 함께 변경해야 합니다.
- Qt Designer에서 레이아웃을 수정하고 저장하면 다음 `python -m src.gui` 실행에 반영됩니다.

## 상태와 갱신

- 실제 Width/Height는 회전 후 화면 이미지의 물리 길이입니다.
- 가로줄 분석인 horizontal은 회전 후 높이, 세로줄 분석인 vertical은 회전 후 너비를 이용해 `px_to_mm`을 계산합니다.
- ROI 이동과 크기 변경 중에는 분석하지 않고 mouse release 뒤 한 번 갱신합니다.
- ROI 이름이나 색상 변경은 overlay와 plot legend를 갱신합니다.
- 파일이 없거나 설정이 유효하지 않으면 image 또는 stale plot을 비우고 원인을 표시합니다.
- 초기 범위는 단일 선택 파일의 동기 처리입니다.

## 구현 경계

`legacy/`는 참고 전용이며 import하거나 runtime dependency로 사용하지 않습니다. CSV 저장 공개 API는 유지하지만 이번 GUI에서는 호출하지 않습니다. batch, worker, configuration과 output 계층은 포함하지 않습니다.
