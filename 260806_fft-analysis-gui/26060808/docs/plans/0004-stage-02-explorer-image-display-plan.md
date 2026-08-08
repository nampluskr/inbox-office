# stage-02: 탐색기 연결 + 이미지 표시 구현 계획

| 항목 | 값 |
| --- | --- |
| 상태 | Done |
| 작성일 | 2026-08-08 |
| 범위 | `src/fft.py`의 `find_image_paths`/`get_image`/`draw_image` 구현, `src/gui.py`/`src/gui.ui`의 탐색기 활성화 및 Canvas 이미지 표시 연결 |
| 관련 문서 | [FFT API 명세](../spec/fft-spec.md), [GUI 명세](../spec/gui-spec.md), [구현 stage 목록](../README.md#구현-stage-목록), [stage-01 계획](0003-stage-01-source-skeleton-plan.md) |

## 목적

stage-01에서 만든 골격 위에 실제 폴더 탐색과 이미지 표시를 연결한다. 사용자가 root 폴더를 선택하면 `.mim` 파일 목록을 갱신하고, 파일을 선택하면 `get_image()`로 로딩한 이미지를 Canvas에 표시한다. 이 stage에서 `rotation`은 `0`으로 고정한다. `Settings.rotation` 변경에 따른 재호출과 회전 UI는 stage-05(Settings 전역 분석 설정)에서 다룬다. ROI 오버레이 표시는 stage-03 범위이며, 이 stage에서는 그리지 않는다.

## 사전 확인 사항

- `.mim` 파일은 실제로는 TIFF 포맷(`uint16` 2D grayscale)이며 `tifffile.imread()`로 읽을 수 있다. `data/synthetic/`에 800x400 `uint16` 샘플 10개가 있어 검증에 사용한다.
- `fft-spec.md`에 `rotation` 허용값을 `-90`, `0`, `90`, `180` 4가지로 확정했다(이 계획 착수 전 문서 갱신, AGENTS.md 변경 순서 규칙에 따름). 이 stage는 `0`만 사용하지만 `get_image()` 구현 자체는 4가지 값을 모두 검증한다.
- Canvas 탭은 현재 `canvasPlaceholder` `QLabel`만 있고 실제 이미지를 그릴 matplotlib `Axes`가 없다. 이 stage에서 `gui.py`가 `FigureCanvasQTAgg`를 `canvasTab` 레이아웃에 동적으로 추가하고, 이미지가 없을 때는 `canvasPlaceholder`를 보이고 있을 때는 `FigureCanvasQTAgg`를 보이는 방식으로 전환한다(`gui.ui`는 수정하지 않음, `canvasPlaceholder`는 stage-01 골격 그대로 유지).

## 구현 범위

### `src/fft.py`

- `find_image_paths(root, pattern="*.mim")`을 구현한다. `os.path.join(root, "**", pattern)`에 `glob.glob(..., recursive=True)`를 적용해 하위 폴더까지 재귀 탐색하고, 정렬된 경로 리스트를 반환한다.
- `get_image(image_path, rotation=0)`을 구현한다. `tifffile.imread(image_path)`로 읽고 `np.asarray(...)`로 변환한다. 2차원이 아니면 `ValueError`를 발생시킨다. `rotation`이 `-90`/`0`/`90`/`180`이 아니면 `ValueError`를 발생시킨다. `0`이 아니면 `np.rot90`(90 배수 회전)으로 회전한다.
- `draw_image(ax, image, roi=None)`을 구현한다. `ax.clear()` 후 `ax.imshow(image, cmap="gray")`로 표시한다. `roi`가 `None`이면 오버레이를 그리지 않는다(이 stage에서는 항상 `None`으로 호출됨. ROI 사각형 렌더링은 stage-03에서 구현).
- `os.path` 기반 경로 처리를 사용하고 `pathlib.Path`는 쓰지 않는다(AGENTS.md 규칙).

### `src/gui.py`

- `MainWindow.load_ui()` 이후 `canvasTab`의 레이아웃에 matplotlib `Figure`/`Axes`를 소유한 `FigureCanvasQTAgg`를 추가하고 `CanvasView`에 전달한다.
- `CanvasView`에 `figure_canvas`, `ax` 속성을 추가한다. `show_empty_state(message)`는 `canvasPlaceholder`를 표시하고 `figure_canvas`를 숨긴다. 이미지가 있을 때는 반대로 전환하는 헬퍼(`show_image(image)` 등 내부 메서드, 공개 계약은 GUI 구조 문서의 표에 없으므로 이름은 구현 시 정하되 `draw_*`와 혼동되지 않게 한다)를 추가한다.
- `MainWindow`에서 `browseButton`, `refreshButton`, `fileList`를 활성화한다.
- `GuiController.refresh_image_list()`를 구현한다. `AnalysisState.root_path`가 설정되어 있으면 `fft.find_image_paths(root_path)`를 호출해 `AnalysisState.image_paths`를 갱신하고, `MainWindow`가 `fileList`와 `fileCountLabel`을 갱신하도록 콜백 또는 반환값을 전달한다.
- `GuiController.select_image(image_path)`를 구현한다. `fft.get_image(image_path, rotation=0)`을 호출해 `self.rotated_image`(및 `self.source_image`)에 저장하고, `AnalysisState.selected_image_path`를 갱신한 뒤 `CanvasView`가 `fft.draw_image(ax, image)`를 호출하도록 연결한다.
- `browseButton.clicked`는 `QFileDialog.getExistingDirectory`로 폴더를 선택하고 `AnalysisState.root_path`를 설정한 뒤 `refresh_image_list()`를 호출한다.
- `refreshButton.clicked`는 `refresh_image_list()`를 다시 호출한다.
- `fileList.currentItemChanged`(또는 `itemClicked`)는 선택된 항목의 경로로 `select_image()`를 호출한다.
- `find_image_paths`/`get_image` 호출 중 예외가 발생하면 `MainWindow.set_status(message)`로 영문 오류 메시지를 표시하고 Canvas는 빈 상태를 유지한다.
- rotation을 다루는 UI나 `set_rotation()` 호출 연결은 이 stage에서 만들지 않는다(스텁 유지, stage-05 범위).

### `src/gui.ui`

- 이 stage에서는 수정하지 않는다. `canvasTab`에 `FigureCanvasQTAgg`를 넣는 작업은 `gui.py`에서 동적으로 처리한다(Qt Designer `.ui`는 matplotlib 위젯을 직접 표현할 UI 요소가 없으므로).

## 제외 범위

- ROI 오버레이 표시 및 상호작용(stage-03, stage-04)
- `Settings.rotation` 변경 UI와 그에 따른 `get_image()` 재호출(stage-05)
- Analysis/Settings 탭의 나머지 위젯 이벤트 연결
- profile/FFT/band-pass/peak-to-valley 분석(stage-06 이후)
- 이미지 캐싱 전략, 대용량 이미지 성능 최적화

## 인수 기준

- `fft.find_image_paths(root)`가 하위 폴더를 포함해 `*.mim` 파일을 재귀적으로 찾아 정렬된 리스트를 반환한다.
- `fft.get_image(path, rotation)`이 `-90`/`0`/`90`/`180`에서 각각 올바르게 회전된 2차원 배열을 반환하고, 그 외 값에는 `ValueError`를 발생시킨다.
- `fft.draw_image(ax, image, roi=None)`이 전달된 `Axes`에 grayscale 이미지를 그리고 반환값이 없다.
- GUI에서 `Browse`로 `data/synthetic/`를 선택하면 `fileList`에 10개 파일이 나열되고 `fileCountLabel`이 개수를 표시한다.
- `fileList`에서 파일을 선택하면 Canvas에 해당 이미지가 표시되고 `canvasPlaceholder`는 숨겨진다.
- 존재하지 않는 root 또는 로딩 실패 시 상태바에 영문 오류 메시지가 표시되고 앱이 중단되지 않는다.

## 검증

- `python -m compileall src`를 실행한다.
- `C:\winpython\WPy64-31180\python-3.11.8.amd64\python.exe`로 `fft.find_image_paths`, `fft.get_image`, `fft.draw_image`를 `data/synthetic/`에 대해 직접 호출해 반환값과 shape/dtype을 확인한다.
- `get_image`에 허용되지 않는 `rotation`(예: `45`)을 전달해 `ValueError`가 발생하는지 확인한다.
- offscreen 환경(`QT_QPA_PLATFORM=offscreen`)에서 GUI를 실행하고, `AnalysisState.root_path`를 `data/synthetic/`로 설정한 뒤 `refresh_image_list()`와 `select_image()`를 코드로 직접 호출해 `fileList` 항목 수와 Canvas의 `ax`에 이미지가 그려졌는지(`ax.images`) 확인한다.
- 수정한 Markdown 문서가 UTF-8이며 `U+FFFD` 대체 문자와 이모지를 포함하지 않는지 확인한다.
