# FFT ROI Analysis GUI 문서

이 디렉터리는 새 구현의 설계 기준을 관리한다. 현재 단계에서는 API 계약과 GUI 골격 구조만 정의하며, 구현 코드는 포함하지 않는다.

## 문서 색인

| 문서 | 상태 | 책임 |
| --- | --- | --- |
| [spec/fft-spec.md](spec/fft-spec.md) | 검토 중 | `src/fft.py` 초기 공개 API, `Settings` 데이터 클래스 및 ROI 딕셔너리 계약 |
| [spec/gui-spec.md](spec/gui-spec.md) | 현재 기준 | 좌측 탐색기와 우측 Canvas 탭을 포함하는 GUI 골격 구조 |
| [plans/](plans/) | 이력 | 구현 계획과 실행 기록 |

## 참고 자료

`refs/legacy1/`과 `refs/legacy2/`는 이전 구현의 참고 자료다. 새 구현은 이 경로를 import하거나 runtime dependency로 사용하지 않는다.

## 문서 원칙

- API 계약은 분석 계층의 공개 입력과 출력을 정의한다.
- GUI 구조 문서는 화면 계층, 모듈 책임 및 사용자 표시 규칙을 정의한다.
- 구현 범위가 확정되면 현재 기준 문서를 먼저 갱신한 뒤 코드를 작성한다.

## 구현 stage 목록

`docs/spec/gui-spec.md`와 `docs/spec/fft-spec.md`를 기준으로 실제 구현을 `stage-xx` 순서로 나눈다. 각 stage는 착수 시점에 `docs/plans/NNNN-stage-xx-topic-plan.md` 형식의 개별 계획 문서를 만들어 세부 구현 범위, 제외 범위, 인수 기준을 기록한다. 아래 표는 stage 순서와 개략 범위만 유지하는 로드맵이다.

| stage | 제목 | 범위 |
| --- | --- | --- |
| stage-01 | 3파일 소스 골격 구현 | `src/fft.py`(`Settings` + API 스텁 `NotImplementedError`), `src/gui.py`(`AnalysisState`/`MainWindow`/`GuiController`/`CanvasView` 골격), `src/gui.ui`(splitter, 탐색기, Canvas/Analysis/Settings 탭 골격). |
| stage-02 | 탐색기 연결 + 이미지 표시 | `Browse`/`Refresh`/`fileList` 활성화, `find_image_paths()`로 목록 갱신, 이미지 선택 시 `get_image()`(`rotation=0` 고정) -> `draw_image()`로 Canvas 표시. Canvas 탭에 matplotlib `FigureCanvasQTAgg` 추가. |
| stage-03 | 기본 ROI 오버레이 표시 | 이미지 최초 로딩 시 `Settings.rois`가 비어 있으면 전체 이미지 ROI(`xmin=0,xmax=1,ymin=0,ymax=1`) 1개를 자동 추가하고 Canvas에 사각형으로 표시(편집 불가, 표시만). |
| stage-04 | ROI 추가/삭제 및 좌표 편집 동기화 | Settings 탭 `Add ROI`/`Delete ROI`, `roiNameEdit`/`roiColorButton`/`xminEdit`~`ymaxEdit` 입력, Canvas 코너 드래그(`drag_roi_corner`)와 Settings 좌표 입력 간 양방향 동기화. 삭제된 ROI가 `selected_roi`였을 때 초기화 처리 포함. |
| stage-05 | Settings 전역 분석 설정 | `physical_width_mm`, `physical_height_mm`, `rotation`, `averaging_band_size_px`, `reference_band_size_px`, `low_pass_cutoff`, `high_pass_cutoff`, `top_k` 입력 필드 연결. `rotation` 변경 시 `get_image()` 재호출과 Canvas 재표시 포함. |
| stage-06 | Analysis 탭 profile 분석 | `roiSelector`/`directionCombo` 연결, `get_roi()` -> `compute_raw_profile()` -> `compute_norm_profile()` 호출, `draw_profiles([norm_profile])`로 dL/L(%) profile 표시. |
| stage-07 | FFT spectrum 분석 | `compute_fft_spectrum()` 호출과 `draw_spectrums([spectrum])` 표시. |
| stage-08 | FFT peaks 분석 | `compute_fft_peaks()` 호출과 `draw_spectrum_peaks()` 표시. |
| stage-09 | Band-pass profile 분석 | `compute_bandpass_profile()` 호출과 `draw_profiles([norm_profile, bandpass_profile], labels=[...])`로 원본과 겹쳐 표시. |
| stage-10 | Peak-to-Valley 분석 | `compute_peak2valley()` 호출과 `draw_peak2valley()` 표시. |
| stage-11 | 저장 기능 (profile/spectrum/peaks) | CSV 저장 API 구현과 GUI 저장 버튼 연결. |

## Plan 문서

- 구현 계획은 `docs/plans/NNNN-topic-plan.md` 형식으로 작성한다.
- 번호는 4자리 0-padding 순번이며 삭제하거나 재사용하지 않는다.
- 상태는 `Draft`, `Approved`, `Done` 중 하나를 사용한다.
- 구현 전 계획은 `Draft`로 작성하고, 승인 후 `Approved`, 완료 후 `Done`으로 갱신한다.
