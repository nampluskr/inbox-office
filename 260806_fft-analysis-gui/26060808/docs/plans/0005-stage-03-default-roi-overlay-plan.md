# stage-03: 기본 ROI 오버레이 표시 구현 계획

| 항목 | 값 |
| --- | --- |
| 상태 | Done |
| 작성일 | 2026-08-08 |
| 범위 | `src/fft.py`의 `draw_image` ROI 오버레이 지원, `src/gui.py`의 기본 ROI 자동 생성 및 Canvas 표시 연결 |
| 관련 문서 | [FFT API 명세](../spec/fft-spec.md), [GUI 명세](../spec/gui-spec.md), [구현 stage 목록](../README.md#구현-stage-목록), [stage-02 계획](0004-stage-02-explorer-image-display-plan.md) |

## 목적

stage-02(탐색기 연결 + 이미지 표시)까지 구현된 상태 위에, 이미지 최초 로딩 시 `Settings.rois`가 비어 있으면 전체 이미지를 덮는 기본 ROI 1개를 자동으로 채우고 Canvas에 사각형으로 표시한다. 이 단계는 표시만 하며, 코너 드래그를 통한 편집이나 `Add ROI`/`Delete ROI` 버튼 연결은 stage-04 범위다.

## 사전 확인 사항

- `AnalysisState.settings`(`src/gui.py`)는 현재 `None`으로 초기화되어 있다. 이 stage에서 `fft.Settings()` 인스턴스로 바꿔 실제 `Settings` 객체를 항상 보유하게 한다.
- `fft-spec.md`의 `draw_image(ax, image, roi=None)`은 `roi`를 단일 dict로만 정의하지만 `Settings.rois`는 `list[dict]`다. 이 계획에서 `draw_image()`가 단일 dict와 dict list를 모두 받아들이도록 확장한다(AGENTS.md 규칙에 따라 `fft-spec.md`를 먼저 갱신).
- 기본 ROI의 `label`/`color`는 문서에 정의되어 있지 않았다. `label="Total"`, `color="yellow"`로 확정한다(사용자 확인).

## 구현 범위

### `docs/spec/fft-spec.md`

- `draw_image(ax, image, roi=None)` 설명에 `roi`가 단일 ROI dict 또는 ROI dict list를 받을 수 있음을 명시한다. list일 때는 각 항목을 사각형으로 겹쳐 그린다. 각 ROI dict의 `xmin`/`xmax`/`ymin`/`ymax`(정규화 좌표)를 이미지 픽셀 크기에 곱해 실제 사각형 좌표로 변환하고, `color`(matplotlib 색상 문자열)로 테두리를, `label`로 범례 텍스트를 그린다.
- "Settings 데이터 모델" 절에 GUI가 자동으로 채우는 기본 ROI의 `label`/`color` 기본값(`"Total"`/`"yellow"`)을 명시한다.

### `docs/spec/gui-spec.md`

- "계획 사용자 흐름" 2번 항목에 기본 ROI의 `label`/`color` 기본값(`"Total"`/`"yellow"`)을 명시한다.
- "Image 탭" 절에 이 단계에서는 ROI 사각형이 표시만 되고 코너 드래그 편집은 stage-04 범위임을 보강한다.

### `src/fft.py`

- `draw_image(ax, image, roi=None)`을 구현한다. `ax.clear()` + `ax.imshow(image, cmap="gray")`는 유지한다. `roi`가 `None`이면 오버레이 없음. `roi`가 dict면 `[roi]`로 감싸 리스트로 통일 처리한다. 각 ROI dict에 대해 `image.shape`(높이, 폭)를 이용해 정규화 좌표를 픽셀 좌표로 변환하고, `matplotlib.patches.Rectangle`을 `ax.add_patch()`로 추가한다(`fill=False`, `edgecolor=color`). `label`은 ROI dict의 `label` 값을 사용한다.

### `src/gui.py`

- `AnalysisState.__init__()`에서 `self.settings = None` 대신 `self.settings = fft.Settings()`로 초기화한다.
- `GuiController.select_image(image_path)`에 다음을 추가한다: `fft.get_image()` 호출 후 `self.state.settings.rois`가 비어 있으면 기본 ROI(`{"xmin": 0, "xmax": 1, "ymin": 0, "ymax": 1, "label": "Total", "color": "yellow"}`)를 추가한다. 이후 `self.canvas_view.show_image(image, self.state.settings.rois)`를 호출한다.
- `CanvasView.show_image(image, rois=None)`을 갱신해 `fft.draw_image(self.ax, image, roi=rois)`를 호출한다.

## 제외 범위

- ROI 코너 드래그를 통한 마우스 편집(`drag_roi_corner`)
- Settings 탭 `Add ROI`/`Delete ROI` 버튼 및 좌표 입력 필드 연결
- ROI 선택 상태(`AnalysisState.selected_roi`)와 Analysis 탭 연동

## 인수 기준

- 이미지 최초 로딩 시 `Settings.rois`가 자동으로 `label="Total"`, `color="yellow"`, 전체 좌표(`xmin=0,xmax=1,ymin=0,ymax=1`) ROI 1개로 채워진다.
- 이미 `rois`가 채워진 상태에서 다른 이미지를 선택해도 ROI가 중복 추가되지 않는다.
- Canvas에 해당 ROI가 사각형 오버레이로 표시되고, 이 단계에서는 마우스로 편집할 수 없다.
- `fft.draw_image()`가 단일 ROI dict와 ROI dict list를 모두 지원한다.

## 검증

- offscreen 환경에서 `data/synthetic/`의 파일을 선택한 뒤 `controller.state.settings.rois`에 기본 ROI 1개가 채워졌는지 확인한다.
- `canvas_view.ax.patches`에 `Rectangle`이 1개 추가되었는지 확인한다.
- 같은 세션에서 다른 이미지를 다시 선택했을 때 `rois` 길이가 여전히 1인지(중복 추가 없음) 확인한다.
- `fft.draw_image(ax, image, roi=[dict, dict])`처럼 dict 2개 리스트를 직접 호출해 사각형 2개가 추가되는지 별도로 확인한다.
- `python -m compileall src` 실행.
- 수정한 Markdown 파일이 UTF-8이며 `U+FFFD` 대체 문자와 이모지를 포함하지 않는지 확인한다.
