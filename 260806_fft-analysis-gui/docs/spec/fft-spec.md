# FFT API 명세

`src/fft.py`에 둘 공개 API와 설정 모델을 검토하기 위한 초안이다. 이 문서에는 함수의 최종 타입 힌트, 반환값, 오류 처리 및 구현 규칙을 아직 정의하지 않는다.

폴더 선택과 ROI 선택은 GUI 책임이다. API는 GUI가 전달한 폴더, 이미지, 회전값, ROI 및 방향을 분석용 데이터로 변환한다.

Settings 탭에서 관리하는 설정 모델과 ROI 딕셔너리 계약도 이 문서에서 정의한다.

## API 호출 흐름

```text
list_image_paths
    -> read_image
    -> rotate_image
    -> extract_profile
    -> compute_fft
    -> find_fft_peaks
```

## 파일 탐색

```python
list_image_paths(root, pattern="*.mim")
```

## 이미지 로딩과 회전

```python
read_image(data_path)
rotate_image(image, rotation=0)
```

이미지를 선택하면 먼저 원본 이미지를 읽고, GUI에서 회전 방향을 선택하면 회전된 이미지를 만든다.

## ROI 분석

```python
extract_profile(image, roi, direction)
compute_fft(profile)
find_fft_peaks(spectrum, top_k)
```

- `direction`은 회전된 이미지 기준의 `x` 또는 `y` 방향이다.
- `extract_profile()`은 선택 ROI와 방향의 profile 데이터를 추출한다.
- `compute_fft()`는 profile의 FFT 데이터를 계산한다.
- `find_fft_peaks()`는 FFT 데이터에서 GUI에 표시할 Top-K peak를 찾는다.

## Settings 데이터 모델

`Settings`는 Settings 탭에서 사용자가 수정하는 분석 설정을 보관하는 단일 데이터 클래스다. ROI는 기존 방식과 호환되도록 데이터 클래스가 아닌 딕셔너리로 표현한다. Python 모듈 전역 변수로 저장하지 않으며, GUI는 하나의 `Settings` 인스턴스를 `AnalysisState`에 보관해 API 호출에 사용한다.

```text
Settings
├── physical_width_mm
├── physical_height_mm
├── rotation
├── rois: list[dict]
├── averaging_band_size_px
├── low_pass_cutoff
├── high_pass_cutoff
└── top_k
```

다음 클래스는 향후 `src/fft.py`에 정의하는 GUI 독립 데이터 모델이다. 필드의 타입, 기본값, 검증 규칙 및 JSON 변환은 후속 설계 범위다.

```python
@dataclass
class Settings:
    physical_width_mm
    physical_height_mm
    rotation
    rois
    averaging_band_size_px
    low_pass_cutoff
    high_pass_cutoff
    top_k
```

각 `rois` 항목은 다음 key를 갖는 딕셔너리다.

```python
{
    "xmin": ...,
    "xmax": ...,
    "ymin": ...,
    "ymax": ...,
    "label": ...,
    "color": ...,
}
```

ROI는 여러 이미지에 공통으로 적용할 수 있도록 정규화 좌표 체계를 사용한다. `xmin`, `xmax`, `ymin`, `ymax`는 회전된 이미지의 폭과 높이에 대한 비율로 해석한다.

### 소유와 사용

- `src/fft.py`는 `Settings` 데이터 클래스를 정의하고, 분석 API는 필요한 설정과 ROI 딕셔너리를 입력으로 받는다.
- `src/gui.py`의 `AnalysisState`는 `Settings` 인스턴스를 하나만 소유한다.
- Settings 탭은 `Settings` 필드를 수정하고, `GuiController`는 수정된 값을 사용해 분석을 다시 실행한다.
- `MainWindow`, `GuiController`, `CanvasView`는 같은 설정값을 별도 속성으로 중복 보관하지 않는다.

## 후속 작성 항목

다음 항목은 API 계약을 구체화하는 후속 범위다.

- 입력값과 타입 힌트
- 반환값과 데이터 형식
- `rotation` 허용값
- 경로 처리 방식
- ROI 좌표 형식과 검증 규칙
- Settings 각 필드의 타입, 기본값, 허용 범위 및 단위
- `low_pass_cutoff`와 `high_pass_cutoff`의 기준 단위
- `averaging_band_size_px`의 정확한 계산 방향과 최소값
- JSON 저장·불러오기 형식
- 이미지별 설정과 폴더 공통 설정의 적용 범위
- 예외 처리와 검증 규칙
- CSV 저장 API
