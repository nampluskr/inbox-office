# PLAN.md

## 1. 문서 목적

본 문서는 현재 ChatGPT 세션 이후 Codex에서 이어서 수행할 작업 순서를 제안한다.

첫 목표는 바로 코드를 많이 작성하는 것이 아니라, **현재 handoff 내용을 기반으로 프로젝트 구조와 분석 specification을 안정적으로 정리하는 것**이다.

---

# 2. Codex 작업 시작 시 우선 읽을 문서

Codex는 다음 순서로 handoff 문서를 읽는 것을 권장한다.

1. `BRIEF.md`
2. `DECISIONS.md`
3. `HANDOFF.md`
4. `QUESTIONS.md`
5. `PLAN.md`

의미:

- `BRIEF.md`: 사용자가 무엇을 원하는가
- `DECISIONS.md`: 무엇이 이미 결정되었는가
- `HANDOFF.md`: 어떤 기술을 검토했는가
- `QUESTIONS.md`: 무엇이 아직 미정인가
- `PLAN.md`: 다음에 무엇을 할 것인가

---

# 3. Codex 첫 작업 제안

Codex에서 첫 요청은 다음 목적을 갖는 것이 적절하다.

> 현재 handoff 문서 5개를 먼저 읽고, 코드 작성 전에 OLED Mura Analysis 프로젝트의 최종 문서 구조와 개발 구조를 제안한다. 기존 결정사항은 유지하고, 미정 항목은 임의로 확정하지 않는다.

---

# 4. Phase 0 — Handoff Review

목표:

- 5개 문서의 상호 모순 확인
- 누락된 요구사항 확인
- 용어 정규화
- 미정 사항 분리

출력 후보:

- handoff review
- terminology proposal
- documentation architecture proposal

완료 조건:

- 사용자 의도와 기술 검토 내용이 손실 없이 정리됨
- Decision과 Open Question이 명확히 분리됨

---

# 5. Phase 1 — 프로젝트 문서 구조 설계

최종 프로젝트에서 필요한 문서 hierarchy를 설계한다.

예상 category:

```text
docs/
  domain/
  data/
  preprocessing/
  spatial/
  spectral/
  wavelet/
  directional/
  decomposition/
  perceptual/
  validation/
  development/
```

이 단계에서는 실제 상세 문서를 모두 작성하지 않아도 된다.

먼저:

- 문서명
- 역할
- dependency
- source of truth

를 정한다.

---

# 6. Phase 2 — OLED Mura Taxonomy 상세화

현재 defect 후보를 공식 taxonomy로 정리한다.

각 Mura에 대해 최소한 다음 항목을 정의한다.

- Name
- Definition
- Visual appearance
- Bright/Dark polarity
- Global/Local
- Directionality
- Periodicity
- Typical scale
- Gray dependency possibility
- Similar defects
- Measurement artifact confusion

목표:

- 현업 naming과 분석 algorithm naming의 일관성 확보

---

# 7. Phase 3 — Data Specification

입력 데이터의 formal specification을 작성한다.

포함 항목:

- TIFF
- MIM
- CSV
- dtype
- shape
- axis convention
- coordinate system
- luminance unit
- Gray metadata
- Target Luminance metadata
- physical pixel pitch
- invalid pixel

추가:

\[
L(x,y,G,L_{target})
\]

의 데이터 model 정의.

---

# 8. Phase 4 — ROI / Mask Specification

정의할 내용:

- relative ROI
- pixel conversion
- rounding
- clipping
- multiple ROI
- overlap
- naming
- camera hole mask
- corner mask
- valid area ratio
- invalid ROI policy

완료 조건:

- 어떤 데이터 shape에서도 동일한 ROI recipe를 적용 가능

---

# 9. Phase 5 — Common Preprocessing Specification

Transform별로 중복되지 않도록 공통 preprocessing을 정의한다.

후보:

- invalid data handling
- NaN
- outlier
- normalization
- relative luminance
- detrending
- surface fitting
- windowing
- mask-aware smoothing
- edge handling
- camera artifact compensation
- registration

주의:

- 모든 analysis가 동일한 preprocessing을 쓰는 것은 아닐 수 있음
- method별 mandatory / optional preprocessing을 구분

---

# 10. Phase 6 — Synthetic Mura Generator 설계

실제 defect label이 부족한 경우 detector 검증용 synthetic data를 설계한다.

생성 후보:

- X/Y gradient
- shading
- vertical band
- horizontal band
- periodic line
- local band
- diagonal band
- ripple
- grid
- cloud
- Gaussian blob
- bright/dark spot
- grain
- random texture
- streak

각 synthetic defect의 parameter:

- amplitude
- width
- position
- frequency
- phase
- orientation
- scale
- active area

목적:

- 분석 방법별 sensitivity 확인
- feature behavior 확인
- unit test 생성

---

# 11. Phase 7 — Spatial Baseline

가장 먼저 구현할 baseline analysis.

후보:

- Global statistics
- Relative luminance
- Surface fitting
- Gradient
- Local mean/std/RMS
- Local contrast
- Segmentation
- Blob
- Shape
- Structure Tensor

목표:

- 위치
- 면적
- contrast
- shape
- orientation

을 직접 얻는 baseline 확보.

---

# 12. Phase 8 — 1D Projection Analysis

구현:

\[
P_x(x)=mean_y(L)
\]

\[
P_y(y)=mean_x(L)
\]

추가:

- X-profile
- Y-profile
- Multi-strip
- mask-aware mean

추출 feature:

- slope
- peak-to-valley
- RMS
- local contrast
- peak location
- band width

---

# 13. Phase 9 — 1D Spectral / Wavelet

분석:

- 1D-DCT
- 1D-FFT
- 1D-DWT
- 1D-DT-CWT

목적:

- directional band
- periodicity
- local scale
- profile anomaly

각 method별:

- input
- preprocessing
- output
- feature
- artifact
- physical interpretation
- runtime

를 문서화한다.

---

# 14. Phase 10 — 2D Spectral / Wavelet

분석:

- 2D-DCT
- 2D-FFT
- 2D-DWT
- 2D-DT-CWT

목적:

- 2D periodicity
- direction
- scale
- local structure

2D FFT에서는:

- radial PSD
- angular PSD
- dominant peak
- anisotropy
- entropy

등을 검토한다.

DT-CWT에서는:

- scale energy
- orientation energy
- active area
- percentile coefficient

등을 검토한다.

---

# 15. Phase 11 — Directional Analysis

구현 후보:

- Gabor
- Radon
- Structure Tensor

목적:

- vertical/horizontal/diagonal line
- streak
- directional local pattern

특히 DT-CWT와 Gabor의 성능 중복을 비교한다.

---

# 16. Phase 12 — Blob / Scale-specific Analysis

후보:

- LoG
- DoG
- Morphology
- Multi-scale local contrast

목적:

- cloud
- blob
- spot
- bright/dark local Mura

---

# 17. Phase 13 — Decomposition Analysis

후보:

- PCA
- SVD
- RPCA
- Low-rank + Sparse

목적:

- background
- smooth structure
- local defect
- noise

분리 가능성 검토.

실제 OLED data에서 assumption이 맞는지 benchmark한다.

---

# 18. Phase 14 — Mura-to-Method Mapping

각 Mura마다 primary / secondary detector를 정의한다.

예:

| Mura | Primary | Secondary |
|---|---|---|
| Gradient | Surface | DCT |
| Vertical Band | X-profile + 1D FFT | 2D FFT, DT-CWT, Gabor |
| Horizontal Band | Y-profile + 1D FFT | 2D FFT, DT-CWT, Gabor |
| Cloud | Spatial / Multi-scale | DWT, DT-CWT |
| Spot | Spatial / Morphology | LoG |
| Diagonal | DT-CWT / Gabor | 2D FFT, Radon |
| Grid | 2D FFT | Gabor, Autocorrelation |

이 문서는 최종 defect classifier 설계의 기반이 된다.

---

# 19. Phase 15 — Feature Specification

각 feature를 formal하게 정의한다.

예:

```text
feature_name
definition
formula
unit
input
parameter
expected_range
normalization
defect sensitivity
artifact sensitivity
```

Feature family:

- Spatial
- Projection
- FFT
- DCT
- DWT
- DT-CWT
- Gabor
- Population
- Perceptual

목표:

- feature 이름과 수식이 코드/문서에서 일치

---

# 20. Phase 16 — Feature Fusion / Classification

초기에는 rule-based 또는 score-based 접근 권장.

예:

```text
Vertical Band Score
  = profile evidence
  + FFT evidence
  + directional evidence
  + spatial evidence
```

Multi-label output 허용.

향후:

- Random Forest
- XGBoost
- SVM
- Neural network

으로 확장 가능.

---

# 21. Phase 17 — Severity Specification

Detection과 Severity를 분리한다.

Physical Severity 후보:

\[
S_{physical}
=
f(
Contrast,
Area,
Scale,
Location,
Direction,
Periodicity
)
\]

Perceptual Severity 후보:

\[
S_{perceptual}
=
f(
S_{physical},
BackgroundLuminance,
SpatialFrequency,
HVS/JND
)
\]

실제 threshold는 data calibration 이후 확정.

---

# 22. Phase 18 — Gray Dependency

각 defect type에 대해:

\[
S_k(G)
\]

를 분석한다.

추출 후보:

- Worst Gray
- max severity
- Gray slope
- low-gray sensitivity
- persistence
- peak Gray

---

# 23. Phase 19 — Golden / Population

가능한 경우:

## Golden

\[
D=
\frac{L_{DUT}-L_{ref}}{L_{ref}}
\]

## Population

- mean
- covariance
- Mahalanobis
- anomaly score

목표:

- 정상 공통 pattern 제거
- abnormality detection

---

# 24. Phase 20 — HVS / JND / SEMU

실제 perceptual severity와 연결한다.

필요 데이터:

- panel luminance
- Mura contrast
- Mura size
- spatial frequency
- location
- human rating

목표:

- "물리적 defect strength"와 "보이는 정도"를 분리

---

# 25. Phase 21 — Validation / Benchmark

필수 benchmark 항목:

- Detection Rate
- False Positive Rate
- Classification accuracy
- Severity correlation
- Repeatability
- Shift robustness
- ROI dependency
- Gray dependency
- Camera dependency
- Runtime

Synthetic + Real data를 함께 사용한다.

---

# 26. Phase 22 — ML / DL Extension

Classical baseline과 feature system이 구축된 이후 진행한다.

후보:

- Random Forest
- XGBoost
- One-Class SVM
- Isolation Forest
- Autoencoder
- CNN
- U-Net
- Vision Transformer

원칙:

- black-box score만 출력하지 않는다.
- 가능한 경우 classical feature와 함께 explainable result 제공.

---

# 27. Codex 작업 원칙 제안

Codex에서 이후 작업 시 다음을 권장한다.

1. `DECISIONS.md`를 설계 기준으로 사용
2. `QUESTIONS.md`의 미정 사항을 임의로 확정하지 않음
3. 문서와 코드의 terminology를 통일
4. 각 분석법마다 장점뿐 아니라 failure mode 기록
5. Mura와 camera artifact를 구분
6. pixel 단위를 가능한 한 physical unit으로 변환
7. feature 정의와 code naming을 일치
8. 새로운 방법 추가 시 기존 방법 대비 장점 명시
9. feature redundancy를 지속적으로 평가
10. 최종 목표는 Explainable Mura Analysis System

---

# 28. 가장 먼저 구현할 Minimum Viable Analysis

실제 코딩을 시작할 경우 다음 최소 세트를 권장한다.

```text
Data Loader
    ↓
ROI / Mask
    ↓
Relative Luminance
    ↓
Surface Detrending
    ↓
Spatial Statistics
    ↓
X/Y Projection
    ↓
1D FFT
    ↓
2D FFT / PSD
    ↓
Local Contrast / Segmentation
    ↓
Basic Mura Report
```

이 baseline을 먼저 검증한 뒤:

```text
DCT
DWT
DT-CWT
Gabor
HVS
Population
```

순으로 확장하는 것이 효율적이다.
