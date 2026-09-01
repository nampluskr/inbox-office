# QUESTIONS.md

## 1. 문서 목적

본 문서는 현재 세션에서 아직 결정되지 않았거나, 실제 데이터/현업 조건 확인이 필요한 항목을 기록한다.

Codex에서 작업할 때 이 항목들을 임의로 확정하지 않는다.

필요한 경우 provisional assumption을 둘 수 있으나 반드시 명시하고, 이후 실제 조건 확인 시 갱신한다.

---

# 2. 데이터 포맷

## Q-001. MIM 파일 포맷의 정확한 specification은 무엇인가?

확인 필요:

- binary / text 여부
- header 구조
- width / height 정보
- dtype
- endian
- luminance unit
- metadata
- Gray / Target Luminance 포함 여부

---

## Q-002. TIFF 데이터의 dtype과 metadata 구조는 무엇인가?

확인 필요:

- float32 / float64 / integer
- single-page / multi-page
- embedded metadata
- image orientation
- scaling factor

---

## Q-003. CSV의 layout은 무엇인가?

가능한 형태:

- pure 2D numeric matrix
- header 포함
- metadata + matrix
- row/column coordinate 포함

---

# 3. Physical Geometry

## Q-004. 측정 pixel과 실제 OLED panel의 physical coordinate 관계를 알 수 있는가?

필요 정보:

- mm/pixel
- panel width / height
- display resolution
- measurement resolution
- optical magnification

이 정보가 있어야 정확한 cycle/mm, mm, mm² 계산이 가능하다.

---

## Q-005. X/Y sampling pitch가 동일한가?

\[
\Delta x = \Delta y
\]

인지 확인 필요.

다를 경우 frequency/scale 계산을 별도 처리해야 한다.

---

# 4. ROI / Mask

## Q-006. ROI relative coordinate의 endpoint convention은 어떻게 할 것인가?

예:

- [x1, x2)
- inclusive/inclusive

Pixel rounding 규칙도 필요하다.

---

## Q-007. Camera hole / rounded corner mask 정보는 어떻게 제공되는가?

가능한 방법:

- 사용자 polygon
- binary mask
- predefined device geometry
- threshold 기반 자동 생성

---

## Q-008. ROI가 Mask와 겹쳐 유효 pixel 비율이 너무 낮은 경우의 정책은?

필요 정책:

- 최소 valid area
- warning
- analysis skip
- partial analysis

---

# 5. 측정 조건

## Q-009. 사용되는 Gray Scale 목록은 무엇인가?

예:

- G2
- G4
- G8
- G16
- G32
- G64
- G128
- G255

실제 조건 확인 필요.

---

## Q-010. Target Luminance 조건은 몇 개인가?

Target Luminance가 Gray와 독립적으로 설정되는지 확인 필요.

---

## Q-011. 동일 panel에서 반복 측정 데이터가 존재하는가?

Repeatability 평가를 위해 중요하다.

---

# 6. 측정 장비 / Artifact

## Q-012. 2D 촬상기의 sensor fixed pattern noise 특성을 알고 있는가?

확인 후보:

- row noise
- column noise
- PRNU
- DSNU
- lens shading
- dark frame
- calibration map

---

## Q-013. Camera calibration 또는 flat-field correction이 이미 적용되는가?

적용 여부에 따라 preprocessing이 달라진다.

---

## Q-014. Moiré 또는 pixel/subpixel sampling alias가 실제 데이터에 존재하는가?

패널 pixel 구조와 camera sampling 관계 확인 필요.

---

## Q-015. Defocus / MTF 조건은 고정되어 있는가?

Fine Mura 및 Grain 분석에 큰 영향을 줄 수 있다.

---

# 7. 불량 Taxonomy

## Q-016. 현업에서 실제 사용하는 OLED Mura 명칭과 현재 taxonomy가 동일한가?

현재 후보:

- Gradient
- Shading
- Vertical Band
- Horizontal Band
- Periodic Line
- Local Band
- Diagonal
- Streak
- Ripple
- Grid
- Cloud
- Blob
- Spot
- Grain
- Random Texture

실제 검사/분석 조직의 naming convention 확인 필요.

---

## Q-017. Bright Mura와 Dark Mura를 별도 class로 둘 것인가?

예:

- Bright Spot / Dark Spot
- Bright Cloud / Dark Cloud

또는 polarity feature로만 관리할지 결정 필요.

---

## Q-018. Edge Mura를 독립 class로 둘 것인가?

Shading 또는 local non-uniformity와 통합할지 결정 필요.

---

# 8. 분석 방법

## Q-019. DWT와 DT-CWT를 모두 최종 시스템에 유지할 것인가?

초기에는 모두 benchmark 가능.

최종적으로 feature redundancy와 성능 비교 필요.

---

## Q-020. Gabor와 DT-CWT의 역할 중복을 어떻게 정리할 것인가?

비교 항목:

- directional detection
- local scale
- shift robustness
- runtime
- explainability

---

## Q-021. DCT가 실질적으로 추가 가치가 있는가?

FFT/Spatial/Wavelet 대비 feature gain을 benchmark해야 한다.

---

## Q-022. Radon Transform을 필수 모듈로 둘 것인가?

Long line / streak 빈도에 따라 결정.

---

## Q-023. RPCA의 low-rank/sparse assumption이 실제 OLED Mura 데이터에 적절한가?

특히 Large Cloud는 sparse하지 않을 가능성이 있다.

---

# 9. Severity

## Q-024. 현재 사용 중인 OK/NG 기준이 존재하는가?

있다면 확보 필요:

- defect type
- threshold
- Gray dependency
- ROI dependency
- customer criterion

---

## Q-025. 관능평가 데이터가 존재하는가?

가능한 label:

- 5-point rating
- 10-point rating
- pairwise comparison
- visible / not visible
- expert score

---

## Q-026. Severity를 0~100으로 표현할 것인가?

대안:

- continuous raw score
- normalized 0~1
- 0~100
- L0~L4
- OK/NG + confidence

---

## Q-027. ROI 위치에 따라 Severity weight를 다르게 할 것인가?

예:

- Center > Edge
- Camera hole 주변 별도 기준

실제 perceptual/customer 기준 확인 필요.

---

# 10. HVS / JND / SEMU

## Q-028. 최종 perceptual metric은 무엇으로 할 것인가?

후보:

- JND 기반
- SEMU
- CSF/HVS model
- empirical human rating model

---

## Q-029. Viewing condition 정보가 존재하는가?

필요 가능 정보:

- viewing distance
- ambient illuminance
- panel luminance
- visual angle

HVS 기반 모델에 영향을 줄 수 있다.

---

# 11. Golden / Population

## Q-030. Golden sample이 존재하는가?

확인 필요:

- 단일 golden panel
- golden image
- Gray별 golden
- ROI별 golden

---

## Q-031. 정상 population 데이터를 얼마나 확보할 수 있는가?

Population anomaly model 가능성을 결정한다.

---

## Q-032. 정상 panel 간 alignment 수준은 어느 정도인가?

Golden/population comparison의 핵심 조건이다.

---

# 12. ML / DL

## Q-033. Labelled defect data가 존재하는가?

확인:

- defect type label
- severity label
- segmentation mask
- OK/NG
- human rating

---

## Q-034. 데이터 규모는 어느 정도인가?

ML/DL strategy 결정에 필요하다.

---

# 13. Validation

## Q-035. 알고리즘 성능의 최우선 평가 지표는 무엇인가?

후보:

- Detection Rate
- False Positive Rate
- Classification Accuracy
- Severity correlation
- Repeatability
- Runtime

---

## Q-036. 실시간 또는 처리시간 요구사항이 있는가?

Offline 분석인지 production inspection인지에 따라 architecture가 달라진다.

---

# 14. 구현 환경

## Q-037. Python 환경과 주요 library 제약이 있는가?

후보:

- NumPy
- SciPy
- OpenCV
- PyWavelets
- dtcwt
- scikit-image
- scikit-learn
- PyTorch

---

## Q-038. Windows/Linux 환경 중 어디에서 실행할 것인가?

MIM reader 및 deployment에 영향 가능.

---

# 15. 우선 확인 권장 순서

다음 항목을 먼저 확인하면 이후 설계 효율이 높다.

1. 실제 sample data
2. MIM specification
3. physical pixel pitch
4. Gray / Target Luminance conditions
5. 현업 Mura taxonomy
6. OK/NG / human rating 존재 여부
7. Camera calibration status
8. Golden / population data 존재 여부
9. Runtime requirement
