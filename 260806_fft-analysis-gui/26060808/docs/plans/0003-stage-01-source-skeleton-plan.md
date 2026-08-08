# stage-01: 3파일 소스 골격 구현 계획

| 항목 | 값 |
| --- | --- |
| 상태 | Done |
| 작성일 | 2026-08-08 |
| 범위 | `src/`의 초기 소스 골격 (`fft.py`, `gui.py`, `gui.ui`) |
| 관련 문서 | [FFT API 명세](../spec/fft-spec.md), [GUI 명세](../spec/gui-spec.md), [구현 stage 목록](../README.md#구현-stage-목록) |

## 목적

`docs/spec/fft-spec.md`와 `docs/spec/gui-spec.md`에 정의된 초기 `src/fft.py`, `src/gui.py`, `src/gui.ui` 소스 골격을 작성한다. 파일 탐색, 이미지 로딩, ROI 분석 또는 FFT 처리는 구현하지 않고, import 가능한 API 이름과 실행 가능한 빈 GUI 골격만 만든다.

이 계획은 이전 [0001 계획](0001-three-file-source-skeleton-plan.md)을 대체한다. 0001은 [0002 계획](0002-fft-api-flow-naming-redefine-plan.md)의 API 재정의 이전 함수명(`list_image_paths`, `read_image`, `rotate_image`, `extract_profile`, `compute_fft`, `find_fft_peaks`)을 사용하고 있어 현재 `fft-spec.md` 기준과 불일치한다. 0001은 `Superseded` 상태로 갱신하고, 이후 구현은 이 문서를 따른다.

## 구현 범위

### `src/fft.py`

- GUI와 독립적인 데이터 클래스 `Settings`를 `fft-spec.md`의 "Settings 데이터 모델"에 정의된 필드 순서(`physical_width_mm`, `physical_height_mm`, `rotation`, `rois`, `averaging_band_size_px`, `reference_band_size_px`, `low_pass_cutoff`, `high_pass_cutoff`, `top_k`)로 정의한다. ROI는 데이터 클래스가 아닌 `dict`(`xmin`, `xmax`, `ymin`, `ymax`, `label`, `color`)로 표현한다.
- 최종 타입 힌트와 반환값 계약 없이 `fft-spec.md` "API 호출 흐름"에 정의된 다음 공개 API 골격을 정의한다.

  ```python
  find_image_paths(root, pattern="*.mim")
  get_image(image_path, rotation=0)
  get_roi(image, roi)
  compute_raw_profile(roi, direction="horizontal")
  compute_norm_profile(raw_profile, averaging_band_size_px, reference_band_size_px)
  compute_fft_spectrum(profile, px_to_mm=None)
  compute_fft_peaks(spectrum, num_peaks=1)
  compute_bandpass_profile(profile, low_pass_cutoff, high_pass_cutoff, px_to_mm=None)
  compute_peak2valley(profile)
  show_image(image, roi=None)
  draw_image(ax, image, roi=None)
  show_profiles(profiles, labels=[])
  draw_profiles(ax, profiles, labels=[])
  show_spectrums(spectrums, labels=[])
  draw_spectrums(ax, spectrums, labels=[])
  show_spectrum_peaks(spectrum, peaks)
  draw_spectrum_peaks(ax, spectrum, peaks)
  show_peak2valley(profile, peak2valley)
  draw_peak2valley(ax, profile, peak2valley)
  ```

- `compute_*`/`get_*`/`find_*` 계열은 영문 메시지와 함께 `NotImplementedError`를 발생시킨다.
- `show_*`/`draw_*` 계열도 동일하게 `NotImplementedError`를 발생시킨다. 이 단계에서는 matplotlib 렌더링 로직을 구현하지 않는다.
- PyQt 또는 `gui.py`의 심볼을 import하지 않는다.

### `src/gui.py`

- `gui-spec.md` "계획 클래스 구조"에 따라 `AnalysisState`, `MainWindow`, `GuiController`, `CanvasView`, `main()`을 정의한다.
- 실행 시 `src/gui.ui`를 로드한다.
- 수평 `QSplitter`(`mainSplitter`), 탐색기 widget 참조, `CanvasView`, controller와 각 탭의 빈 상태를 생성한다.
- 탐색기 조작 요소(`browseButton`, `refreshButton`, `fileList`)는 비활성화하고 `src.fft` API를 호출하지 않는다.
- Analysis 탭(`roiSelector`, `directionCombo`)과 Settings 탭(`addRoiButton`, `deleteRoiButton`, `roiNameEdit`, `roiColorButton`, `xminEdit`~`ymaxEdit`)의 위젯 참조는 보관하되 이벤트 연결과 활성화는 후속 stage 범위다.
- GUI 표시 문자열과 API 골격 미구현 상태 메시지는 영문으로 작성한다.

### `src/gui.ui`

- Qt Designer용 `QMainWindow` 레이아웃 원본을 정의한다.
- `gui-spec.md` "UI 계약" 표에 정의된 `objectName`을 모두 사용해 `mainSplitter`, 탐색기 조작 요소(`dataRootEdit`, `browseButton`, `refreshButton`, `fileCountLabel`, `fileList`), `analysisTabs`와 `canvasTab`/`canvasPlaceholder`/`analysisTab`/`roiSelector`/`directionCombo`/`settingsTab`/`roiList`/`addRoiButton`/`deleteRoiButton`/`roiNameEdit`/`roiColorButton`/`xminEdit`/`xmaxEdit`/`yminEdit`/`ymaxEdit`, `QStatusBar`를 추가한다.
- 좌측 탐색기와 우측 `Canvas`/`Analysis`/`Settings` 세 탭을 수평 splitter로 배치한다.
- Canvas 탭에는 빈 상태 안내 `canvasPlaceholder`만 표시한다.

## 제외 범위

- 파일 대화상자, 디렉터리 탐색, 이미지 로딩, 회전, Canvas 이미지 렌더링 및 ROI 상호작용(코너 드래그 포함)
- profile, FFT, band-pass, peak-to-valley, Top-K peak 계산의 실제 알고리즘, CSV 내보내기 및 설정 저장
- Analysis/Settings 탭 위젯의 이벤트 연결(선택 반영, 좌표 편집 동기화 등)
- 최종 타입 힌트, 반환 데이터 형상, 검증 규칙, 필터 단위 및 JSON 직렬화
- `fft.py`, `gui.py`, `gui.ui` 외의 새 소스 모듈

## 인수 기준

- `src/`에는 구현 파일로 `fft.py`, `gui.py`, `gui.ui`만 존재한다.
- `src.fft`는 PyQt를 import하지 않고, `Settings` 데이터 클래스와 `fft-spec.md`에 정의된 전체 API 함수(`find_image_paths`부터 `draw_peak2valley`까지)를 공개한다.
- 모든 API 골격은 호출 시 `NotImplementedError`를 발생시킨다.
- `python -m src.gui`는 `gui.ui`를 로드하고 문서화된 splitter와 `Canvas`/`Analysis`/`Settings` 탭을 포함한 빈 GUI를 시작한다.
- 탐색기 조작 요소는 비활성화되어 있으며, GUI 시작 시 미구현 API를 호출하지 않는다.
- offscreen Qt 실행 점검에서 GUI가 실행된다.

## 검증

- `python -m compileall src`를 실행한다.
- `src.fft`를 import하고 공개 데이터 클래스와 API 심볼을 확인한다.
- 각 API 골격을 호출해 `NotImplementedError` 발생을 확인한다.
- offscreen 환경(`QT_QPA_PLATFORM=offscreen`)에서 GUI를 실행하고 필수 `objectName`, 비활성 탐색기 조작 요소, `Canvas`/`Analysis`/`Settings` 탭 및 빈 상태 메시지를 확인한다.
- 수정한 Markdown 문서가 UTF-8이며 `U+FFFD` 대체 문자와 이모지를 포함하지 않는지 확인한다.
