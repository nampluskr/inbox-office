# FFT API 명세

`src/fft.py`에 둘 공개 API와 설정 모델을 검토하기 위한 초안이다. 이 문서에는 함수의 최종 타입 힌트, 반환값, 오류 처리 및 구현 규칙을 아직 정의하지 않는다.

폴더 선택과 ROI 선택은 GUI 책임이다. API는 GUI가 전달한 폴더, 이미지, 회전값, ROI 및 방향을 분석용 데이터로 변환한다.

Settings 탭에서 관리하는 설정 모델과 ROI 딕셔너리 계약도 이 문서에서 정의한다.

## 레거시 대비 설계 원칙

이 프로그램은 `refs/matlab/`의 레거시 MATLAB 코드(분석은 `docs/spec/matlab-legacy-analysis.md` 참고)를 이식하되, 하드코딩된 전역값을 파라미터로 바꾸고 길이 단위를 통일한다. 핵심 결정은 다음과 같다.

1. **ROI는 전역값이 아니라 파라미터다.** 레거시는 특정 이미지 shape을 전제로 `ROI_x`, `ROI_y`, `division_y`를 스크립트 상단에 하드코딩했다. 신규 프로그램은 ROI를 Settings 또는 API 입력값으로 받는다. GUI가 선택한 ROI를 API에 전달한다.
2. **픽셀 설정값은 이미지에서 유도하고, 물리 단위(mm)만 설정으로 보관한다.** 이미지는 패널에 대응하므로 픽셀 폭·높이는 로딩된 이미지 또는 crop된 ROI의 크기에서 계산할 수 있다. 사용자가 설정하는 값은 회전되어 고정된 패널의 가로·세로 mm 값뿐이다. 픽셀당 mm(`mmPP`)는 `panel_mm / image_pixels`로 런타임에 계산한다.
3. **레거시의 간접 영역 지정 파라미터는 제거한다.** 다음 값은 ROI 직접 지정으로 대체되어 불필요하다.
   - `ROI_x`, `ROI_y` — ROI 크기는 ROI 좌표에서 도출한다.
   - `division_x`, `division_y` — ROI를 직접 지정하므로 분할 개념이 필요 없다.
   - `crop_left`, `crop_right`, `crop_top`, `crop_bottom` — ROI 선택이 crop을 대신한다.
4. **모든 길이 단위는 mm로 고정하고 cm는 사용하지 않는다.** 레거시 GUI가 쓰던 cycles/cm와 파장 변환의 `*10`은 폐기한다. 주파수 축은 cycles/mm, 파장은 mm로 통일한다.
5. **함수명은 동사+목적어, 분석 계산은 `compute_*`로 통일한다.** 시각화는 `show_*`(독립 창)와 `draw_*`(Canvas 렌더링) 두 계층으로 분리한다. 레거시 코드(`refs/legacy1`, `refs/legacy2`, `refs/matlab`)의 흐름·네이밍·변수는 참조만 하며 그대로 옮기지 않는다.
6. **profile 계산은 원시 평균과 후처리를 분리한다.** `compute_raw_profile`은 ROI·방향의 원시 평균만 반환하고, `compute_norm_profile`이 noise·background 평활과 dL/L(%) 계산을 내부에서 수행한다.
7. **하위 함수는 앞 단계의 출력을 인자로 받는다.** 파일 경로를 다시 읽어들이는 체인이 아니라, `image → roi → profile → spectrum` 순으로 데이터를 직접 전달한다.

## API 호출 흐름

```text
find_image_paths(root)                          -> paths
get_image(path, rotation)                        -> image (로딩+회전)
get_roi(image, roi)                              -> roi
compute_raw_profile(roi, direction)              -> raw profile (원시 평균)
compute_norm_profile(raw_profile, ...)           -> dL/L(%) profile (내부 noise/background 평활)
compute_fft_spectrum(dl_profile, px_to_mm)       -> spectrum
compute_fft_peaks(spectrum, num_peaks)           -> top-K peaks
compute_bandpass_profile(dl_profile, low, high)  -> band-pass profile (ifft)
compute_peak2valley(dl_profile)                  -> P2V 진폭
```

각 단계는 앞 단계의 출력을 인자로 받는다. `find_image_paths()`를 제외한 모든 함수는 독립적으로도 호출할 수 있도록 필요한 입력을 인자로 명시한다.

## 분석 API 함수

`direction`은 회전된 이미지 기준의 `"horizontal"` 또는 `"vertical"`이다. 변수명은 회전된 이미지 전체를 `image`, `image`에서 crop한 영역을 `roi`로 쓴다. `image` 대상 함수와 `roi` 대상 함수는 별도로 이중화하지 않고 인자로 구분한다.

### 파일 탐색

```python
find_image_paths(root, pattern="*.mim")
```

### 이미지 로딩과 ROI

```python
get_image(image_path, rotation=0)
get_roi(image, roi)
```

- `get_image()`는 이미지를 읽고 `rotation`으로 회전한 `image`를 반환한다. `rotation`은 `-90`, `0`, `90`, `180` 중 하나만 허용하며, 그 외 값은 `ValueError`를 발생시킨다.
- `get_roi()`는 `image`에서 정규화 좌표 `roi`가 가리키는 영역을 crop한 배열을 반환한다.

### Profile

```python
compute_raw_profile(roi, direction="horizontal")
compute_norm_profile(raw_profile, averaging_band_size_px, reference_band_size_px)
```

- `compute_raw_profile()`은 `roi`를 `direction` 방향으로 평균한 원시 profile을 반환한다. 필터링이나 dL/L 계산을 포함하지 않는다.
- `compute_norm_profile()`은 `compute_raw_profile()`의 출력을 받아 noise 평활(`averaging_band_size_px`)과 background 평활(`reference_band_size_px`)을 각각 적용한 뒤, `100 * (smoothed - reference) / reference`로 dL/L(%) profile을 계산한다.

### FFT

```python
compute_fft_spectrum(profile, px_to_mm=None)
compute_fft_peaks(spectrum, num_peaks=1)
```

- `compute_fft_spectrum()`은 profile의 FFT 진폭 스펙트럼을 계산한다.
- `compute_fft_peaks()`는 스펙트럼에서 GUI에 표시할 상위 `num_peaks`개 peak를 찾는다.

### Band-pass와 Peak-to-Valley

```python
compute_bandpass_profile(profile, low_pass_cutoff, high_pass_cutoff, px_to_mm=None)
compute_peak2valley(profile)
```

- `compute_bandpass_profile()`은 `low_pass_cutoff`/`high_pass_cutoff`(mm) 밖의 주파수 성분을 제거한 뒤 역변환한 profile을 반환한다.
- `compute_peak2valley()`는 profile의 peak-valley 진폭을 계산한다.

### 시각화

각 분석 결과에는 `show_*`(독립 창)와 `draw_*`(Canvas 렌더링) 두 함수가 대응한다.

```python
show_image(image, roi=None)              # -> None, 새 Figure 생성 후 표시
draw_image(ax, image, roi=None)          # -> None, 전달받은 Axes에 그림

show_profiles(profiles, labels=[])
draw_profiles(ax, profiles, labels=[])

show_spectrums(spectrums, labels=[])
draw_spectrums(ax, spectrums, labels=[])

show_spectrum_peaks(spectrum, peaks)
draw_spectrum_peaks(ax, spectrum, peaks)

show_peak2valley(profile, peak2valley)
draw_peak2valley(ax, profile, peak2valley)
```

- `show_*`는 `ax`를 받지 않고 항상 새 Figure/Axes를 만들어 표시하며 반환값이 없다. 독립 창에 표시할 때 쓴다.
- `draw_*(ax, ...)`는 호출자가 전달한 `Axes`에 그리기만 하고 반환값이 없다. GUI Canvas 렌더링에 쓴다.
- `show_*`는 내부에서 새 Axes를 만들고 `draw_*(ax, ...)`를 호출해 그리기 로직을 중복하지 않는다.
- `show_profiles`/`draw_profiles`는 `profiles` 리스트에 담긴 1개 이상의 profile을 같은 Axes에 겹쳐 그린다. raw profile, norm(dL/L) profile, band-pass profile을 각각 단독으로 표시하거나(리스트 길이 1) 여러 개를 겹쳐 비교(리스트 길이 2 이상)할 때 모두 이 함수를 쓴다. `labels`는 `profiles`와 같은 길이로 전달하며 범례 레이블로 쓴다.
- `show_spectrums`/`draw_spectrums`도 동일한 규칙으로 `spectrums` 리스트를 겹쳐 그린다.
- `show_spectrum_peaks`·`show_peak2valley`처럼 profile/spectrum 자체가 아니라 peaks·P2V 같은 부가 결과를 함께 표시하는 함수는 리스트화 규칙 대상이 아니다.
- `show_image`/`draw_image`의 `roi`는 단일 ROI dict 또는 ROI dict의 list를 모두 받는다. list일 때는 각 ROI를 이미지 위에 사각형으로 겹쳐 그린다. 각 ROI의 `xmin`/`xmax`/`ymin`/`ymax`(정규화 좌표)는 이미지의 폭·높이 픽셀 크기에 곱해 실제 사각형 좌표로 변환하고, `color`로 사각형 테두리를(선 굵기 2pt), `label`로 범례 텍스트를 그린다. 전체 이미지를 덮는 ROI(`xmin=0, xmax=1, ymin=0, ymax=1`)의 테두리가 Axes 경계선(spine)에 가려 보이지 않는 문제를 피하기 위해, `draw_image()`는 ROI를 그릴 때 Axes의 spine을 숨긴다.

## Settings 데이터 모델

`Settings`는 Settings 탭에서 사용자가 수정하는 분석 설정을 보관하는 단일 데이터 클래스다. ROI는 기존 방식과 호환되도록 데이터 클래스가 아닌 딕셔너리로 표현한다. Python 모듈 전역 변수로 저장하지 않으며, GUI는 하나의 `Settings` 인스턴스를 `AnalysisState`에 보관해 API 호출에 사용한다.

```text
Settings
├── physical_width_mm
├── physical_height_mm
├── rotation
├── rois: list[dict]
├── averaging_band_size_px
├── reference_band_size_px
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
    reference_band_size_px
    low_pass_cutoff
    high_pass_cutoff
    top_k
```

`averaging_band_size_px`는 `compute_norm_profile()`의 noise 평활 필터 크기이고, `reference_band_size_px`는 같은 함수의 background 평활 필터 크기다. `low_pass_cutoff`와 `high_pass_cutoff`의 단위는 mm이며 `compute_bandpass_profile()`의 cut 경계로 쓰인다. `top_k`는 `compute_fft_peaks()`의 `num_peaks`에 대응한다.

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

`rois`가 비어 있을 때 GUI(`GuiController`)는 회전된 이미지 전체를 덮는 기본 ROI 1개(`xmin=0, xmax=1, ymin=0, ymax=1, label="Total", color="yellow"`)를 채운다. 이 기본값 채우기는 `src/fft.py` API의 책임이 아니라 GUI 책임이며, 분석 함수는 빈 `rois` 처리 로직을 갖지 않는다.

### 소유와 사용

- `src/fft.py`는 `Settings` 데이터 클래스를 정의하고, 분석 API는 필요한 설정과 ROI 딕셔너리를 입력으로 받는다.
- `src/gui.py`의 `AnalysisState`는 `Settings` 인스턴스를 하나만 소유한다.
- Settings 탭은 `Settings` 필드를 수정하고, `GuiController`는 수정된 값을 사용해 분석을 다시 실행한다.
- `MainWindow`, `GuiController`, `CanvasView`는 같은 설정값을 별도 속성으로 중복 보관하지 않는다.

## 후속 작성 항목

다음 항목은 API 계약을 구체화하는 후속 범위다.

- 입력값과 타입 힌트
- 반환값과 데이터 형식
- 경로 처리 방식
- ROI 좌표 형식과 검증 규칙
- Settings 각 필드의 타입, 기본값, 허용 범위 및 단위 (길이 단위는 mm 고정)
- `low_pass_cutoff`와 `high_pass_cutoff`의 세부 계산 규칙 (기준 단위는 mm 고정)
- `averaging_band_size_px`와 `reference_band_size_px`의 정확한 계산 방향과 최소값
- JSON 저장·불러오기 형식
- 이미지별 설정과 폴더 공통 설정의 적용 범위
- 예외 처리와 검증 규칙
- CSV 저장 API
