# FFT API 흐름·네이밍 재정의 계획

| 항목 | 값 |
| --- | --- |
| 상태 | Done |
| 작성일 | 2026-08-08 |
| 범위 | `docs/spec/fft-spec.md` API 흐름·네이밍 재정의 (문서 전용) |
| 관련 문서 | [FFT API 명세](../spec/fft-spec.md), [GUI 명세](../spec/gui-spec.md), [MATLAB 레거시 분석](../spec/matlab-legacy-analysis.md) |

## 목적

`docs/spec/fft-spec.md`의 API 호출 흐름과 함수 네이밍을 레거시 MATLAB 파이프라인(profile 추출 및 FFT 분석)을 참조해 원점에서 재정의한다. 현재 흐름(`list_image_paths → read_image → rotate_image → extract_profile → compute_fft → find_fft_peaks`)은 분석의 핵심 물리량 dL/L(%)와 필터링·band-pass·Peak-to-Valley 단계를 드러내지 못한다.

`src/fft.py`는 아직 존재하지 않으므로 이 계획은 문서만 수정한다(AGENTS.md: 정본 문서를 코드보다 먼저 변경). 레거시 코드(`refs/legacy1`, `refs/legacy2`, `refs/matlab`)의 흐름·네이밍·변수는 참조만 하며 그대로 복제하지 않는다.

## 설계 결정

1. 함수명은 동사+목적어 형태로 하고, 분석 계산은 `compute_*` 중심으로 통일한다. 시각화는 `show_*` 쌍으로 제공한다.
2. `compute_raw_profile`은 ROI·방향의 원시 평균 profile만 반환한다. 필터링과 dL/L은 raw profile 단계에 통합하지 않는다.
3. profile 단계를 두 함수로 나눈다. `compute_raw_profile`은 원시 평균만 반환하고, `compute_norm_profile`은 raw profile을 받아 내부에서 noise·background 평활 필터링을 수행한 뒤 dL/L(%)를 계산한다(평활을 이 함수에 병합, 별도 `smooth_profile` 없음).
4. 하위 함수는 `data_path` 재로딩 체인이 아니라 앞 단계 출력을 인자로 받는 데이터 파이프라인으로 정의한다. `show_*`도 동일한 데이터 인자를 받아 figure만 그린다.
5. 변수명은 `data` 대신 `image`(회전된 전체)를 쓰고, image에서 crop된 영역은 `roi`로 쓴다. image 대상과 roi 대상은 함수 이중화가 아니라 인자로 구분한다.
6. `Settings`에 background 필터 크기 `reference_band_size_px`를 추가한다(기존 `averaging_band_size_px`는 noise 필터).
7. band-pass(ifft)와 Peak-to-Valley를 흐름에 함수로 포함한다.
8. 모든 길이 단위는 mm로 고정하고 cm는 사용하지 않는다. 주파수축은 cycles/mm, 파장은 mm.
9. 시각화 책임을 두 계층으로 완전히 분리한다. `show_*(data_path, ...)`는 `ax`를 받지 않고 항상 새 Figure/Axes를 만들어 표시한 뒤 `(fig, ax)`를 반환한다(독립 창 표시용). `draw_*(ax, data_path, ...)`는 호출자가 전달한 `Axes`에 그리기만 하고 반환값이 없다(GUI Canvas 렌더링용). `show_*`는 내부에서 새 Axes를 만들고 `draw_*(ax, ...)`를 호출해 그리기 로직을 중복하지 않는다.
10. `show_*`/`draw_*`의 접미사는 처리 결과값의 종류를 따른다. `compute_*`가 profile을 반환하면 `_profile`, spectrum을 반환하면 `_spectrum`로 시각화 함수 접미사를 맞춘다(`compute_bandpass_profile` -> `show_bandpass_profile`/`draw_bandpass_profile`). `show_profile`/`draw_profile`은 raw profile과 norm(dL/L) profile을 모두 인자로 받는 범용 함수이므로 별도로 나누지 않는다. peaks·P2V처럼 profile/spectrum이 아닌 결과는 이 규칙 대상이 아니다.

## 확정 함수 세트

```python
find_image_paths(root, pattern="*.mim")
get_image(data_path, rotation=0)                  # -> image (회전된 전체)
get_roi(image, roi)                               # -> roi (crop된 영역)
compute_raw_profile(roi, direction="horizontal")  # -> 원시 평균 profile
compute_norm_profile(raw_profile, averaging_band_size_px, reference_band_size_px)  # 내부 noise/background 평활 -> dL/L(%) profile
compute_fft_spectrum(profile, px_to_mm=None)      # -> spectrum
compute_fft_peaks(spectrum, num_peaks=1)          # -> top-K peaks
compute_bandpass_profile(profile, low_pass_cutoff, high_pass_cutoff, px_to_mm=None)  # -> ifft profile
compute_peak2valley(profile)                      # -> P2V 진폭
# 시각화(독립 창): show_image, show_profile, show_fft_spectrum, show_fft_peaks, show_bandpass_profile, show_peak2valley
#   각 show_*(data_path, ...)는 새 Figure/Axes를 만들고 (fig, ax)를 반환한다. ax 인자를 받지 않는다.
# 시각화(Canvas 렌더링): draw_image, draw_profile, draw_fft_spectrum, draw_fft_peaks, draw_bandpass_profile, draw_peak2valley
#   각 draw_*(ax, data_path, ...)는 전달받은 Axes에 그리기만 하고 반환값이 없다. show_*는 내부에서 draw_*를 호출한다.
```

정확한 인자 순서·기본값, `roi`에 `list[dict]` 전달 시 리스트 반환 여부는 문서 초안에서 확정한다.

## 구현 범위 (문서 수정)

### `docs/spec/fft-spec.md`

- "## API 호출 흐름" 블록을 데이터 인자 파이프라인으로 교체한다.

  ```text
  find_image_paths(root)                       -> paths
  get_image(path, rotation)                    -> image (로딩+회전)
  get_roi(image, roi)                          -> roi
  compute_raw_profile(roi, direction)          -> raw profile (원시 평균)
  compute_norm_profile(raw_profile, ...)       -> dL/L(%) profile (내부 noise/background 평활)
  compute_fft_spectrum(dl_profile, px_to_mm)   -> spectrum
  compute_fft_peaks(spectrum, num_peaks)       -> top-K peaks
  compute_bandpass_profile(dl_profile, low, high) -> band-pass profile (ifft)
  compute_peak2valley(dl_profile)              -> P2V 진폭
  ```

- "## 이미지 로딩과 회전"과 "## ROI 분석"을 "## 분석 API 함수"로 통합하고, 위 함수 세트를 한국어 한 줄 설명 + `python` 시그니처로 나열한다. image/roi는 인자로 구분한다.
- 각 분석 함수마다 `show_*`(독립 창, `ax` 없음, `(fig, ax)` 반환)와 `draw_*(ax, ...)`(전달받은 Axes에 그리기만, 반환값 없음)를 별도 항목으로 나열하고, `show_*`가 내부에서 `draw_*`를 호출하는 관계를 설명한다.
- `Settings` 트리와 `@dataclass`에 `reference_band_size_px`를 `averaging_band_size_px` 뒤에 추가하고, 필터·dL/L·cutoff(mm)·`top_k` 매핑 설명 문단을 추가한다.
- `compute_raw_profile`(원시 평균) → `compute_norm_profile`(내부 noise/background 평활 후 dL/L%) 후처리 순서와 각 단계 입출력을 명시한다. dL/L 정의는 `matlab-legacy-analysis.md`를 참조한다.
- "후속 작성 항목"의 필터 관련 항목을 `averaging_band_size_px`·`reference_band_size_px` 기준으로 갱신한다.

### `docs/spec/gui-spec.md`

- "계획 사용자 흐름"의 옛 함수명을 새 함수 세트로 교체한다. 방향 표기 `x`/`y`를 `horizontal`/`vertical`로 바꾸고, profile이 원시 평균이며 dL/L이 후처리임을 반영한다.
- `CanvasView`/`GuiController`가 Canvas에 그릴 때는 `show_*`가 아니라 `draw_*(ax, ...)`를 호출함을 명시한다(반환값을 쓰지 않는 렌더링이므로).
- `GuiController` 설명이 새 함수 계열을 호출함을 명확히 한다(GUI 메서드명 자체는 유지).

## 제외 범위

- `src/fft.py`, `src/gui.py`, `src/gui.ui` 구현.
- 필터·band-pass·Peak-to-Valley 세부 산술 알고리즘, 최종 타입 힌트, 반환 데이터 형상, 검증 규칙, JSON 직렬화.
- `notebooks/`의 실제 코드 수정. (노트북은 옛 `get_*`/`show_*` import를 사용하므로 새 함수명과 불일치하며, 이 불일치의 처리 방침만 문서에 후속 항목으로 남길지 초안에서 판단한다.)

## 인수 기준

- fft-spec.md의 API 흐름이 데이터 인자 파이프라인으로 재정의되고, 옛 함수명이 새 `compute_*`/`show_*` 세트로 대체된다.
- `compute_raw_profile`은 원시 평균만 반환하고, `compute_norm_profile`이 내부 평활 후 dL/L(%)를 계산하는 별도 함수로 문서에 나타난다.
- 변수명이 `image`(회전 전체)와 `roi`(crop 영역)로 일관되게 사용된다.
- `Settings`에 `reference_band_size_px`가 추가되고 트리와 `@dataclass`가 일치한다.
- band-pass와 Peak-to-Valley 함수가 흐름과 함수 목록에 포함된다.
- 모든 길이 단위가 mm로 표기되고 cm 표현이 없다.
- 각 `show_*`에 대응하는 `draw_*(ax, ...)`가 문서에 존재하고, `show_*`는 반환값(`fig, ax`)을 갖는 독립 창 표시용, `draw_*`는 반환값 없는 Canvas 렌더링용으로 책임이 구분되어 있다.

## 검증

- fft-spec.md와 `docs/spec/` 전체에서 옛 이름(`list_image_paths`, `read_image`, `rotate_image`, `extract_profile`, `compute_fft`, `find_fft_peaks`) 잔존 여부를 검색한다.
- 흐름도에 `data_path` 재로딩 체인 표현이 없고 각 단계가 앞 단계 출력을 인자로 받는지 확인한다.
- `Settings` 트리와 `@dataclass` 필드 목록이 일치하고 `reference_band_size_px`를 포함하는지 확인한다.
- 수정한 Markdown 문서가 UTF-8이며 `U+FFFD` 대체 문자와 이모지를 포함하지 않는지 확인한다.
