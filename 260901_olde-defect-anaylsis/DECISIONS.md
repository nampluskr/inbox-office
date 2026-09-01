# DECISIONS.md

## 1. 문서 목적

본 문서는 현재 세션에서 논의된 내용 중 **현 시점에서 프로젝트의 기본 원칙으로 채택할 항목**을 정리한다.

Codex에서 이후 문서 또는 코드를 작성할 때 이 문서를 우선적인 설계 기준으로 사용한다.

새로운 검토 결과로 변경이 필요한 경우, 기존 결정을 임의로 덮어쓰지 말고 변경 이유와 영향을 기록한 뒤 갱신한다.

---

# 2. 입력 데이터 관련 결정

## D-001. 기본 분석 입력은 2D Luminance Map이다.

기본 입력:

\[
L(x,y)
\]

조건 확장:

\[
L(x,y,G,L_{target})
\]

입력은 single-channel floating-point luminance data를 기본으로 한다.

---

## D-002. Gray Scale과 Target Luminance는 분석 조건으로 관리한다.

동일 panel에 여러 Gray / Target Luminance 조건이 존재할 수 있다.

단일 image 분석과 multi-condition 분석을 모두 고려한다.

---

## D-003. 분석 결과는 가능한 한 실제 물리 단위와 연결한다.

가능한 경우 다음 단위를 사용한다.

- Luminance: nit 또는 측정 장비 기준 단위
- Length: mm
- Area: mm²
- Spatial frequency: cycle/mm

Pixel 또는 cycle/pixel은 내부 표현으로 사용할 수 있으나, 사용자-facing 결과는 가능하면 physical unit으로 변환한다.

---

# 3. ROI / Mask 관련 결정

## D-004. 분석 단위는 ROI다.

전체 panel 분석뿐 아니라 사용자가 정의한 복수 ROI를 독립적으로 분석할 수 있어야 한다.

---

## D-005. ROI는 상대좌표를 사용한다.

ROI:

\[
(x_1,y_1,x_2,y_2)
\]

좌표는 0~1 범위의 relative coordinate를 기본으로 한다.

---

## D-006. ROI와 Mask는 별도 개념으로 관리한다.

ROI:
- 분석하고 싶은 공간 범위

Mask:
- ROI 내부에서 분석에서 제외할 pixel

Mask 대상:

- Camera hole
- Rounded corner
- Invalid pixel
- Measurement invalid region

---

# 4. 1D Projection 관련 결정

## D-007. 기본 projection은 Average를 사용한다.

X-profile:

\[
P_x(x)=mean_y(L(x,y))
\]

Y-profile:

\[
P_y(y)=mean_x(L(x,y))
\]

Sum은 옵션으로 둘 수 있으나 기본값으로 사용하지 않는다.

---

## D-008. X-profile / Y-profile 명칭을 사용한다.

모호한 "horizontal projection", "vertical projection" 표현보다 다음 용어를 우선한다.

- X-profile: Y 방향 평균 후 X축 함수
- Y-profile: X 방향 평균 후 Y축 함수

---

## D-009. Local band 대응을 위해 Multi-strip Projection을 검토한다.

전체 ROI projection에서 local defect가 평균으로 희석될 수 있으므로 strip-based projection을 확장 옵션으로 유지한다.

---

# 5. Transform 관련 결정

## D-010. 기본 transform analysis module은 8개로 관리한다.

### 1D

- 1D-DCT
- 1D-FFT
- 1D-DWT
- 1D-DT-CWT

### 2D

- 2D-DCT
- 2D-FFT
- 2D-DWT
- 2D-DT-CWT

---

## D-011. DCT를 FFT의 단순 real version으로 취급하지 않는다.

문서에서는 DCT를 Fourier-related cosine transform으로 설명한다.

---

## D-012. Complex Wavelet의 우선 후보는 DT-CWT다.

Complex wavelet 관련 상세 검토에서는 Dual-Tree Complex Wavelet Transform을 primary candidate로 사용한다.

필요 시 다른 complex wavelet 계열을 비교한다.

---

# 6. 분석 Architecture 관련 결정

## D-013. Transform만으로 Mura analysis system을 구성하지 않는다.

전체 분석은 최소한 다음 family를 구분한다.

1. Spatial
2. Spectral
3. Multi-resolution
4. Directional
5. Decomposition
6. Cross-condition
7. Perceptual
8. Decision

---

## D-014. 분석 방법별 역할을 명확히 구분한다.

기본 역할:

### Spatial

- Contrast
- Area
- Location
- Shape
- Local structure

### FFT

- Frequency
- Pitch
- Periodicity
- Global orientation

### DCT

- Global LF/MF/HF energy
- Smooth non-uniformity representation

### DWT

- Multi-scale local structure

### DT-CWT

- Scale
- Orientation
- Location
- Shift-robust local structure

### Gabor

- Tunable frequency
- Tunable orientation

### Radon

- Long line / streak

### PCA/SVD/RPCA

- Background / residual decomposition

### HVS/JND/SEMU

- Perceptual severity

---

# 7. Spatial Analysis 관련 결정

## D-015. Spatial Analysis는 필수 계층이다.

FFT 또는 Wavelet 결과만으로 최종 Mura 판단을 하지 않는다.

Spatial domain에서 최소한 다음 feature를 검토한다.

- Global statistics
- Relative luminance
- Surface / Gradient
- Local statistics
- Local contrast
- Segmentation
- Area / Location
- Shape
- Orientation

---

## D-016. Camera hole / ROI boundary가 분석 결과를 오염시키지 않도록 한다.

Mask boundary, ROI crop boundary, corner geometry 등에서 발생하는 artificial frequency/edge response를 고려해야 한다.

---

# 8. Severity 관련 결정

## D-017. Detection score와 Severity를 구분한다.

예:

- Detection score: 해당 Mura detector가 얼마나 강하게 반응했는지
- Severity: 실제 화질 불량 수준

둘은 동일한 값으로 취급하지 않는다.

---

## D-018. Physical Severity와 Perceptual Severity를 구분한다.

Physical Severity 후보:

- Contrast
- Area
- Scale
- Periodicity
- Direction
- Location

Perceptual Severity 후보:

- Background luminance
- Spatial frequency sensitivity
- Mura size
- JND/HVS/SEMU
- Human rating

---

## D-019. Severity threshold는 초기부터 임의로 고정하지 않는다.

최종 threshold는 다음 데이터와 calibration하는 것을 원칙으로 한다.

- OK/NG
- Human rating
- Expert visual inspection
- Production data

---

# 9. Gray / Population 관련 결정

## D-020. Gray dimension은 적극 활용한다.

단일 image보다 다음을 분석 대상으로 유지한다.

\[
S_k(G)
\]

예:

- Worst Gray
- Gray response curve
- Low-gray-specific Mura
- Persistent Mura

---

## D-021. Golden reference와 Population analysis는 별도 확장 축으로 유지한다.

가능한 경우 다음을 검토한다.

- Golden panel difference
- Normal population statistics
- Mahalanobis distance
- One-class anomaly
- Unsupervised model

---

# 10. 불량 분류 관련 결정

## D-022. 현재 불량 taxonomy는 고정된 최종 목록이 아니다.

현재 기본 후보:

- Gradient
- Shading
- Edge Mura
- Vertical Band
- Horizontal Band
- Periodic Line
- Local Band
- Diagonal Mura
- Streak
- Ripple
- Grid
- Checker
- Cloud
- Blob
- Spot
- Grain
- Fine Mura
- Random Texture

실제 데이터와 현업 naming convention에 맞추어 변경 가능하다.

---

## D-023. Multi-label defect를 허용한다.

한 ROI에 여러 Mura가 동시에 존재할 수 있다.

예:

```text
Vertical Banding : strong
Cloud Mura       : weak
Gradient         : weak
```

단일 class만 강제하지 않는다.

---

# 11. Explainability 관련 결정

## D-024. 최종 분석 결과는 설명 가능해야 한다.

가능한 결과 예:

```text
Primary Defect : Vertical Banding
Severity       : 78

Evidence
  Contrast          2.8 %
  Pitch            11.7 mm
  FFT Peak          0.085 cycle/mm
  Orientation       Vertical
  Active Area       43 %
  Worst Gray        G16
```

"왜 해당 불량으로 판단되었는가"를 확인할 수 있어야 한다.

---

# 12. 개발 관련 결정

## D-025. 바로 ML/DL로 시작하지 않는다.

먼저 해석 가능한 classical feature와 detector를 구축한다.

이후 충분한 label/data 확보 시 다음으로 확장한다.

- Random Forest
- XGBoost
- SVM
- Autoencoder
- CNN
- Segmentation network
- Transformer

---

## D-026. 분석 방법은 실제 데이터로 benchmark 후 유지 여부를 판단한다.

모든 방법을 최종 시스템에 반드시 포함하지 않는다.

예:

- DWT vs DT-CWT
- DT-CWT vs Gabor
- FFT vs Autocorrelation
- Spatial filter vs Wavelet

성능, 해석성, 계산비용을 비교하여 최종 feature redundancy를 줄인다.
