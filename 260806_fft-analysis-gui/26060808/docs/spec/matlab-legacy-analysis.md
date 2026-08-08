# MATLAB 레거시 코드 분석

`refs/matlab/`에 있는 원본 MATLAB 코드를 역공학해 정리한 참조 문서다. 얇은 가로줄(Thin Horizontal Line) mura를 profile 추출과 FFT로 분석하는 알고리즘의 작동 순서, 핵심 수식, 파라미터 매핑을 기록한다. 이 문서는 구현 스펙이 아니라 원본 동작을 이해하기 위한 근거 자료다.

분석 대상은 다음 두 파일이다.

- `refs/matlab/fft_analyzer-legacy.m` — 배치 스크립트. 최초 원형이자 최소 코드다.
- `refs/matlab/ThinHorLineAnalysis.txt` — MATLAB App Designer GUI 앱(v3.1). 스크립트 로직을 GUI화하고 crop, 영역 분할, 주파수 대역통과, Excel 저장을 추가한 확장판이다.

두 파일은 같은 알고리즘의 서로 다른 형태이며, 핵심 물리량은 **배경 대비 profile의 상대 변화율 `dL/L(%)`**이다. 이 값의 FFT로 가로줄 mura의 주기 성분을 찾는다.

## 1. 공통 분석 파이프라인

두 버전이 공유하는 핵심 흐름은 다음과 같다.

```text
이미지 로드
    -> 회전(imrotate 90도)
    -> (영역 분할)
    -> Noise 제거 평균 필터  -> ActiveImage_avg
    -> Background 평균 필터   -> ActiveImage_ref
    -> 중심 기준 ROI 설정
    -> ROI 열 방향 평균       -> profile, profile_ref
    -> dL/L(%) 계산           -> Dprofile
    -> FFT(abs)               -> profile_fft
    -> findpeaks 정렬          -> 상위 peak 파장/강도
```

## 2. Legacy 스크립트 (`fft_analyzer-legacy.m`)

### 작동 순서

파일당 처리 순서는 다음과 같다.

1. **파일 목록 수집** — 현재 폴더의 `*.mim` (`dir('*.mim')`).
2. **이미지 로드** — `importdata(fileName)`.
3. **회전** — `imrotate(double(ActiveImage), 90)` (반시계 90도). `_rotated.mim`으로 저장.
4. **세로 등분** — `division_y`개로 분할(기본 1 = 분할 없음). `_j.mim`으로 저장.
5. **Noise 제거** — `avgFiltSize`(=10) 평균 필터 → `ActiveImage_avg`. `_avg10.mim`으로 저장.
6. **Background 생성** — `avgRefFiltSize`(=48) 평균 필터 → `ActiveImage_ref`. `_BG.mim`으로 저장.
7. **ROI 설정** — 이미지 중심 기준 `ROI_x` × `ROI_y` 영역의 start/end 좌표 계산.
8. **Profile 추출** — ROI를 열 방향 `mean`으로 평균해 1D profile 생성.
   - `profile` — noise 제거 이미지 기준.
   - `profile_ref` — background 이미지 기준.
9. **dL/L(%) 계산** — `Dprofile = 100*(profile - profile_ref)./profile_ref`.
10. **FFT** — `abs(fft(Dprofile))`, DC 성분 제외 후 `2:floor(ROI_x/2)` 구간만 사용.
11. **주파수 축** — `mmPP = panel_long_mm / resize_H` 기반 `x_cpmm` (cycles/mm).
12. **피크 검출** — `findpeaks` → 내림차순 정렬 → **상위 5개** 파장(mm, `1./loc`)과 강도 저장.
13. 결과를 `data` 행렬에 열 단위로 누적(start/end 좌표, profile, ref, Dprofile, FFT, peak 5개).

### 알려진 문제

49행의 `ROI_X`(대문자 X)는 정의되지 않은 변수다. MATLAB 변수명은 대소문자를 구분하므로 이 스크립트는 그대로 실행하면 오류가 난다. 원본이 미완성 또는 오타 상태임을 의미한다. 올바른 이름은 `ROI_x`다.

### 파라미터 (스크립트 상단 하드코딩)

| 변수 | 값 | 의미 |
|---|---|---|
| `avgFiltSize` | 10 | Noise 제거 필터 크기 (px) |
| `avgRefFiltSize` | 48 | Background 생성 필터 크기 (px) |
| `ROI_x` | 1170 | ROI 가로 (px) |
| `ROI_y` | 474 | ROI 세로 (px) |
| `panel_long_mm` | 149.1 | Panel 장축 실측 크기 (mm) |
| `division_y` | 1 | 세로 등분 개수 |

### 환경 요구

- MATLAB 본체.
- Image Processing Toolbox — `fspecial`, `imfilter`, `imrotate`, `imresize`.
- Signal Processing Toolbox — `findpeaks`.
- 외부 함수 `saveastiff` (중간 결과 저장).
- 입력 파일 `*.mim`.

## 3. GUI 앱 (`ThinHorLineAnalysis.txt`)

### 사용 흐름

1. **startupFcn** — 파라미터 18개 테이블을 기본값으로 초기화하고 기본 이미지를 세팅한다.
2. **OPEN 버튼** (`Button_openPushed`) — 폴더를 선택하면 `*_Y.tif`, `*_Y_Active.tif`, `*.mim` 파일 목록을 만든다.
3. **행 더블클릭** (`UITable_resultDoubleClicked`) — 파일 하나를 분석한다.
   - 파라미터 18개 로드.
   - (선택) `angleNameOrder`/`timeNameOrder` 파일명 규칙으로 0도 기준 이미지를 찾아 resize 정보를 산출한다.
   - 이미지 로드 → mim이면 90도 회전, Rotation 체크 시 추가 90도 회전.
   - `getActiveImage5`로 Threshold 크롭(외부 함수).
   - `division_x` × `division_y` 영역으로 분할하고, 각 영역마다 `showData`를 호출한다.
4. **`showData`** — 핵심 분석 함수. resize → 4방향 crop → 평균/ref 필터 → ROI → `Dprofile` → peak/valley 및 FFT → band-pass.
5. **RUN 버튼** (`Button_runPushed`) — 모든 파일을 일괄 처리하고 Excel(.xlsx) 3시트로 저장한다(결과값 / band-pass profile / 이미지). Excel COM 자동화를 쓴다.
6. **STOP 버튼** (`Button_stopPushed`) — `app.stop` 플래그로 RUN 루프를 중단한다.

### `showData` 세부 동작

1. `imresize`로 `[resize_V, resize_H]` 크기로 맞춘 뒤 4방향 crop 적용.
2. `avgFiltSize` 평균 필터로 `ActiveImage_avg`, `avgRefFiltSize` 평균 필터로 `ActiveImage_ref` 생성.
3. 크롭된 이미지 중심 기준으로 `ROI_x` × `ROI_y` ROI 좌표 계산.
4. `profile`, `profile_ref` 추출 후 `Dprofile` 계산.
5. `findpeaks`로 peak와 valley를 각각 검출한다. `MinPeakWidth 0.1`(mm)로 0.1mm 미만 잡음 피크를 배제한다.
6. 각 peak 기준 `scanWidth_mm` 이내에서 가까운 valley를 찾아 **Peak-to-Valley** 값을 구한다. 가장 큰 값이 `maxPeak2Valley`, 평균이 `avgPeak2Valley`다.
7. peak2valley를 내림차순 정렬해 상위 5/10/15/20% 평균(`peak2valley5p` 등)을 계산한다.
8. FFT를 계산한다. 주파수 축은 `x_cpcm` (cycles/cm)로 legacy의 cycles/mm과 단위가 다르다.
9. 주파수 대역통과(band-pass) 적용 후 `ifft`로 `Dprofile_cut`을 만든다(아래 5절).
10. FFT peak를 내림차순 정렬해 상위 파장(mm)과 최고 peak 대비 비율(%)을 저장한다.

### 파라미터 (18개, `startupFcn`의 `inputPara` 기본값)

| # | 이름 | 기본값 | 코드 변수 | 의미 |
|---|---|---|---|---|
| 1 | Crop Th.(%) | 50 | `th = 값/100` | Active 영역 임계값 |
| 2 | Median Filter(pixels) | 0 | `medFiltSize` | 미디언 필터 크기 |
| 3 | Avg. Filter(pixels) | 28 | `avgFiltSize` | Noise 제거 필터 |
| 4 | Avg. Ref. Filter(pixels) | 140 | `avgRefFiltSize` | Background 필터 |
| 5 | ROI x(pixels) | 2000 | `ROI_x` | ROI 가로 |
| 6 | ROI y(pixels) | 1000 | `ROI_y` | ROI 세로 |
| 7 | Panel Hor. Side(mm) | 158.8 | `panel_long_mm` | 패널 가로 실측 (mm) |
| 8 | Scan Width(mm) | 2 | `scanWidth_mm` | Peak-Valley 탐색 폭 (mm) |
| 9 | Angle Name Order | 11 | `angleNameOrder` | 파일명 내 각도 토큰 위치 |
| 10 | Time Name Order | 1 | `timeNameOrder` | 파일명 내 시간 토큰 위치 |
| 11 | Division x | 1 | `division_x` | 가로 분할 수 |
| 12 | Division y | 1 | `division_y` | 세로 분할 수 |
| 13 | Fq. cut Short(mm) | 3.4 | `cut_mmLow` | 대역통과 단파장 컷 |
| 14 | Fq. cut Long(mm) | 3.6 | `cut_mmHigh` | 대역통과 장파장 컷 |
| 15 | Crop Left(pixels) | 0 | `crop_left` | 좌측 crop |
| 16 | Crop Right(pixels) | 0 | `crop_right` | 우측 crop |
| 17 | Crop Top(pixels) | 0 | `crop_top` | 상단 crop |
| 18 | Crop Bottom(pixels) | 0 | `crop_bottom` | 하단 crop |

> `inputPara`의 실제 나열 순서는 `[50;0;28;140;2000;1000;158.8;2;11;1;1;1;3.4;3.6;0;0;0;0]`이다.

### mim(Telecentric) 권장값

`mimFileTelecentricCheckBox`를 켜면 mim 파일 전용 권장 파라미터를 안내한다. 이 값들은 legacy 스크립트의 하드코딩 값과 계열이 같다.

| 파라미터 | 권장값 |
|---|---|
| Crop Th.(%) | 0 |
| Median Filter(pixels) | 0 |
| Avg. Filter(pixels) | 10 |
| Avg. Ref. Filter(pixels) | 48 |
| ROI x(pixels) | 1300 |
| ROI y(pixels) | 175 |
| Panel Hor. Side(mm) | 158.8 |
| Scan Width(mm) | 3 |
| Angle Name Order | 0 |
| Time Name Order | 1 |
| Division x | 1 |
| Division y | 1 |

### 환경 요구

- MATLAB + App Designer.
- Image Processing Toolbox, Signal Processing Toolbox.
- 외부 함수 `getActiveImage5`(Threshold 크롭), `saveastiff`, `dec2base27`(Excel 열 인덱스 변환), `fn_PasteImageToExcel2`(이미지 삽입).
- **Excel COM 자동화** (`actxserver('Excel.Application')`) — Windows + Excel 설치가 필수다.

## 4. dL/L(%) 정의

`dL/L(%)`는 background 대비 신호 profile의 상대 변화율이다. 절대 밝기 편차가 아니라 배경 대비 비율로 정규화한 값이므로, 밝기 수준이 다른 이미지 사이에서도 비교할 수 있다.

```matlab
Dprofile = 100 * (profile - profile_ref) ./ profile_ref;
```

- `profile` — noise 제거 필터(`avgFiltSize`)를 거친 이미지의 ROI 열 방향 평균. 신호 성분이다.
- `profile_ref` — 더 큰 필터(`avgRefFiltSize`)로 강하게 평활화한 background. 저주파 조명/밝기 성분이다.
- 큰 필터일수록 세밀한 가로줄 성분이 지워지므로, `profile - profile_ref`는 background에서 제거된 고주파 성분(=가로줄 mura)만 남긴다.
- `./ profile_ref`로 나누고 `100`을 곱해 백분율 상대 변화율로 만든다.

이후 모든 정량 지표(Peak-to-Valley, FFT peak)는 이 `Dprofile`을 입력으로 한다.

## 5. Band-pass 로직 (GUI 전용)

GUI의 `showData`는 FFT 도메인에서 특정 파장 대역만 남기고 나머지를 0으로 만든 뒤 역변환해 `Dprofile_cut`을 만든다. 특정 주기의 가로줄 성분만 분리해 보기 위한 처리다.

```matlab
interval_cpcm = x_cpcm(1);

% 장파장(저주파)쪽 컷: cut_mmHigh보다 긴 주기 성분 제거
profile_fft_temp0(2:round(10/(cut_mmHigh*interval_cpcm))) = 0;
profile_fft_temp0(end-round(10/(cut_mmHigh*interval_cpcm))+2:end) = 0;

% 단파장(고주파)쪽 컷: cut_mmLow보다 짧은 주기 성분 제거
profile_fft_temp0(round(10/(cut_mmLow*interval_cpcm))+2:end-round(10/(cut_mmLow*interval_cpcm))) = 0;

Dprofile_cut = ifft(profile_fft_temp0);
```

- 주파수 축이 cycles/cm이므로 파장(mm)을 주파수 인덱스로 바꿀 때 `10/(cut_mm * interval_cpcm)` 형태(cm↔mm 환산 10)를 쓴다.
- FFT는 켤레 대칭이므로 앞쪽 인덱스와 `end` 근처 인덱스를 동시에 0으로 만들어 실수 신호 대칭을 유지한다.
- 결과적으로 `[cut_mmLow, cut_mmHigh]` 범위 밖 파장 성분이 제거된 대역통과 profile이 된다. 기본값 3.4~3.6mm는 좁은 대역만 통과시킨다.
- `Dprofile_cut`은 RUN 시 Excel 두 번째 시트에 "dL/L(%) Band Pass"로 저장된다.

## 6. 주파수 축 계산

profile은 픽셀 단위지만 결과는 물리 단위(파장 mm, 주파수 cycles/cm)로 변환한다. 기준은 픽셀당 실제 거리 `mmPP`다.

```matlab
mmPP = panel_long_mm / resize_H;   % 픽셀당 mm
```

| 항목 | Legacy | GUI |
|---|---|---|
| 주파수 축 수식 | `x_cpmm = (1:floor(ROI_x/2)-1)/(mmPP*ROI_x)` | `x_cpcm = (1:floor(ROI_x/2)-1)/(mmPP*ROI_x)*10` |
| 단위 | cycles/mm | cycles/cm |
| Peak 파장 변환 | `1./loc` (mm) | `10./loc` (mm) |

GUI는 cm 기준이라 `*10`이 붙는다는 점을 제외하면 계산 구조는 동일하다.

## 7. 두 버전 비교 요약

| 항목 | Legacy 스크립트 | GUI 앱 |
|---|---|---|
| 파라미터 | 6개 하드코딩 | 18개 (GUI 테이블 편집) |
| Crop / Threshold | 없음 | Crop Th. + Median + 4방향 crop |
| 영역 분할 | 세로만 (`division_y`) | 가로·세로 (`division_x` / `division_y`) |
| 정량 지표 | FFT 상위 5개 peak | Peak-to-Valley (max/avg/5·10·15·20%) + FFT peak |
| 주파수 축 | cycles/mm | cycles/cm |
| Band-pass (ifft) | 없음 | 있음 (`cut_mmLow` / `cut_mmHigh`) |
| 출력 | `data` 행렬 (메모리) | Excel 3시트 + GUI 시각화 |
| 실행 환경 | MATLAB 스크립트 | MATLAB App + Excel COM (Windows) |

## 8. Python 이식 시 참고

`docs/spec/fft-spec.md`의 API 흐름(`get_image → get_roi → compute_raw_profile → compute_norm_profile → compute_fft_spectrum → compute_fft_peaks`)은 이 레거시 파이프라인의 공통 부분과 대응한다. 이식 시 주의할 점은 다음과 같다.

- `dL/L(%)`는 profile 그 자체가 아니라 noise/background 두 필터 결과의 상대 변화율이다. 단순 ROI 평균 profile과 다르다.
- 필터는 MATLAB `fspecial('average')` + `imfilter(..., 'symmetric')` 조합이다. 경계 처리가 symmetric이라는 점을 맞춰야 결과가 일치한다.
- 주파수 축 단위(cycles/mm vs cycles/cm)와 DC 제외 구간(`2:floor(ROI_x/2)`)을 정확히 옮겨야 peak 파장이 맞는다.
- band-pass는 FFT 켤레 대칭을 유지하며 양끝 인덱스를 동시에 0으로 만드는 방식이라는 점을 유지해야 한다.
- 49행 `ROI_X` 오타는 legacy 스크립트의 버그이며, 올바른 동작은 GUI `showData`를 기준으로 판단한다.
