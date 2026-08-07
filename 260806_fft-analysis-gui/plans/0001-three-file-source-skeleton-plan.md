# 3파일 소스 스켈레톤 구현 계획

| 항목 | 값 |
| --- | --- |
| 상태 | Draft |
| 작성일 | 2026-08-07 |
| 범위 | `src/`의 초기 소스 스켈레톤 |
| 관련 문서 | [FFT API 명세](../spec/fft-spec.md), [GUI 명세](../spec/gui-spec.md) |

## 목적

현재 설계 문서에 정의한 초기 `src/fft.py`, `src/gui.py`, `src/gui.ui` 소스 스켈레톤을 작성한다. 파일 탐색, 이미지 로딩, ROI 분석 또는 FFT 처리는 구현하지 않고, import 가능한 API 이름과 실행 가능한 빈 GUI만 만든다.

## 구현 범위

### `src/fft.py`

- GUI와 독립적인 데이터 클래스 `Settings`를 정의한다. ROI는 기존 방식과 호환되는 딕셔너리로 표현한다.
- 최종 타입 힌트와 반환값 계약 없이 다음 공개 API 스켈레톤을 정의한다.

  ```python
  list_image_paths(root, pattern="*.mim")
  read_image(data_path)
  rotate_image(image, rotation=0)
  extract_profile(image, roi, direction)
  compute_fft(profile)
  find_fft_peaks(spectrum, top_k)
  ```

- 모든 API 스켈레톤은 영문 메시지와 함께 `NotImplementedError`를 발생시킨다.
- PyQt 또는 `gui.py`의 심볼을 import하지 않는다.

### `src/gui.py`

- GUI 구조 문서에 따라 `AnalysisState`, `MainWindow`, `GuiController`, `CanvasView`, `main()`을 정의한다.
- 실행 시 `src/gui.ui`를 로드한다.
- 수평 splitter, 탐색기 widget 참조, `CanvasView`, controller와 빈 상태를 생성한다.
- 탐색기 조작 요소는 비활성화하고 `src.fft` API를 호출하지 않는다.
- GUI 표시 문자열과 API 스켈레톤 미구현 상태 메시지는 영문으로 작성한다.

### `src/gui.ui`

- Qt Designer용 `QMainWindow` 레이아웃 원본을 정의한다.
- 문서화된 `objectName`을 사용해 `mainSplitter`, 탐색기 조작 요소, `analysisTabs`, 하나의 `canvasTab`, `canvasPlaceholder`, 상태 표시줄을 추가한다.
- 좌측 탐색기와 우측 단일 `Canvas` 탭을 수평 splitter로 배치한다.

## 제외 범위

- 파일 대화상자, 디렉터리 탐색, 이미지 로딩, 회전, Canvas 이미지 렌더링 및 ROI 상호작용
- profile, FFT, 필터링, Top-K peak 계산, CSV 내보내기 및 설정 저장
- 최종 타입 힌트, 반환 데이터 형상, 검증 규칙, 필터 단위 및 JSON 직렬화
- `fft.py`, `gui.py`, `gui.ui` 외의 새 소스 모듈

## 인수 기준

- `src/`에는 구현 파일로 `fft.py`, `gui.py`, `gui.ui`만 존재한다.
- `src.fft`는 PyQt를 import하지 않고, `Settings` 데이터 클래스와 6개 API 함수를 공개한다.
- 모든 API 스켈레톤은 호출 시 `NotImplementedError`를 발생시킨다.
- `python -m src.gui`는 `gui.ui`를 로드하고 문서화된 splitter와 `Canvas` 탭을 포함한 빈 GUI를 시작한다.
- 탐색기 조작 요소는 비활성화되어 있으며, GUI 시작 시 미구현 API를 호출하지 않는다.
- offscreen Qt 실행 점검에서 GUI가 실행된다.

## 검증

- `python -m compileall src`를 실행한다.
- `src.fft`를 import하고 공개 데이터 클래스와 API 심볼을 확인한다.
- 각 API 스켈레톤을 호출해 `NotImplementedError` 발생을 확인한다.
- offscreen 환경에서 GUI를 실행하고 필수 `objectName`, 비활성 탐색기 조작 요소, `Canvas` 탭 및 빈 상태 메시지를 확인한다.
- 수정한 Markdown 문서가 UTF-8이며 `U+FFFD` 대체 문자를 포함하지 않는지 확인한다.
