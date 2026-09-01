# HANDOFF.md

## 1. 문서 목적

본 문서는 ChatGPT 세션에서 지금까지 검토한 OLED Mura 분석 관련 기술적 내용을 Codex 작업 환경으로 전달하기 위한 handoff 문서다.

이 문서는 **현재까지 검토한 아이디어와 분석 후보 전체를 기술적으로 정리**한다.

최종 설계가 확정되었다는 의미는 아니며, 확정된 원칙은 `DECISIONS.md`를 우선 참조한다.

---

# 2. 측정 데이터 모델

기본 측정 데이터는 2D luminance map이다.

\[
L(x,y)
\]

여러 Gray Scale 및 Target Luminance 조건을 포함하면 다음과 같이 확장할 수 있다.

\[
L(x,y,G,L_{target})
\]

여기서:

- \(x,y\): OLED panel spatial coordinate
- \(G\): Gray Scale
- \(L_{target}\): Target Luminance

데이터 특성:

- single-channel
- floating-point
- OLED display와 동일한 2D shape
- TIFF / MIM / CSV
- 향후 physical pixel pitch 또는 panel dimensions 정보 연계 가능

---

# 3. ROI / Mask

## 3.1 ROI

사용자는 복수 ROI를 상대좌표로 정의할 수 있다.

\[
ROI_i=(x_1,y_1,x_2,y_2), \qquad 0\le x,y\le1
\]

예:

```text
ROI_1 = (0.05, 0.05, 0.95, 0.95)
ROI_2 = (0.05, 0.05, 0.45, 0.95)
ROI_3 = (0.55, 0.05, 0.95, 0.95)
```

각 ROI는 독립적인 Mura 분석 단위다.

## 3.2 Mask

ROI와 Mask는 분리해서 관리하는 것이 권장된다.

Mask 대상 예:

- Camera hole
- Rounded corner
- Invalid pixel
- Measurement invalid region
- 기타 분석 제외 영역

\[
M(x,y)\in\{0,1\}
\]

Mask convention은 구현 단계에서 명확히 고정해야 한다.

---

# 4. 1D Projection

ROI를 X 또는 Y 방향으로 projection하여 1D profile을 생성한다.

## 4.1 X-profile

Y 방향 평균:

\[
P_x(x)=\frac{1}{H}\sum_yL(x,y)
\]

주요 용도:

- Vertical Band
- X Gradient
- Vertical periodic structure

## 4.2 Y-profile

X 방향 평균:

\[
P_y(y)=\frac{1}{W}\sum_xL(x,y)
\]

주요 용도:

- Horizontal Band
- Y Gradient
- Horizontal periodic structure

## 4.3 Average vs Sum

ROI 크기가 달라도 해석이 일관되도록 기본 projection은 Average가 적합하다.

## 4.4 Multi-strip Projection

전체 ROI projection에서 local band가 희석될 수 있으므로 ROI를 여러 strip으로 분할하여 local projection을 계산하는 방법을 검토하였다.

예:

```text
ROI
────────────────────
Strip 1 -> Px1
────────────────────
Strip 2 -> Px2
────────────────────
Strip 3 -> Px3
────────────────────
```

주요 용도:

- Partial vertical band
- Partial horizontal band
- Local streak

---

# 5. Transform Analysis 8개

현재 검토한 기본 transform module은 다음 8개다.

## 5.1 1D

- 1D-DCT
- 1D-FFT
- 1D-DWT
- 1D-DT-CWT

## 5.2 2D

- 2D-DCT
- 2D-FFT
- 2D-DWT
- 2D-DT-CWT

개념적 분류는 다음과 같다.

\[
1D/2D
\times
Real/Complex
\times
Fourier/Wavelet
\]

단, DCT는 FFT의 단순 real version이 아니라 Fourier-related cosine transform이라는 점에 주의한다.

---

# 6. FFT

## 6.1 1D FFT

\[
F_x(f)=FFT(P_x(x))
\]

\[
PSD_x(f)=|F_x(f)|^2
\]

주요 용도:

- Vertical Band
- Horizontal Band
- Periodic Line
- Ripple
- Dominant frequency
- Pitch

\[
\lambda=\frac1{f_0}
\]

## 6.2 2D FFT

\[
F(f_x,f_y)=FFT2(L(x,y))
\]

\[
PSD(f_x,f_y)=|F(f_x,f_y)|^2
\]

주요 용도:

- 2D periodicity
- Grid
- Checker pattern
- Diagonal pattern
- Ripple
- Directional energy
- Orientation analysis

Spatial frequency:

\[
f=\sqrt{f_x^2+f_y^2}
\]

Orientation:

\[
\theta=\tan^{-1}\left(\frac{f_y}{f_x}\right)
\]

FFT의 주요 장점은 정확한 frequency/pitch 분석이다.

주요 단점은 위치 정보의 손실이다.

---

# 7. DCT

DCT는 smooth/global variation과 frequency energy distribution 분석 후보로 검토하였다.

주요 feature:

- Low-frequency energy
- Mid-frequency energy
- High-frequency energy
- Directional energy
- Spectral centroid

주요 검출 대상:

- Gradient
- Shading
- Large-scale cloud
- Global frequency distribution
- Fine texture energy

DCT는 ROI boundary가 FFT와 다른 방식으로 처리되므로 smooth non-uniformity 분석에 유용할 수 있다.

---

# 8. DWT

Discrete Wavelet Transform은 multi-scale local structure 분석 후보로 검토하였다.

2D DWT는 일반적으로 다음 subband를 사용한다.

\[
LL,\ LH,\ HL,\ HH
\]

Multi-level decomposition을 통해 서로 다른 scale의 Mura를 분석한다.

주요 검출 대상:

- Cloud
- Blob
- Local band
- Grain
- Fine Mura
- Multi-scale texture

주요 feature:

- Level별 energy
- Directional detail energy
- Local coefficient magnitude
- High-frequency energy

---

# 9. DT-CWT

Dual-Tree Complex Wavelet Transform은 Complex Wavelet 후보 중 우선 검토 대상으로 선정하였다.

복소 coefficient:

\[
W_{s,\theta}(x,y)
=
A_{s,\theta}(x,y)e^{j\phi_{s,\theta}(x,y)}
\]

Magnitude:

\[
A=|W|
\]

Phase:

\[
\phi=\angle W
\]

주요 장점:

- approximate shift invariance
- multi-scale
- local spatial information
- improved directional selectivity
- diagonal / streak 분석

대표적으로 여러 방향 subband를 제공한다.

주요 feature:

\[
E_s
=
\sum_\theta\sum_{x,y}|W_{s,\theta}|^2
\]

\[
E_\theta
=
\sum_s\sum_{x,y}|W_{s,\theta}|^2
\]

추가 feature:

- Q95 / Q99 / Q99.5
- Active area ratio
- Local max
- Normalized scale-orientation energy

주요 대상:

- Local band
- Diagonal Mura
- Streak
- Cloud
- Blob
- Grain

---

# 10. Spatial Analysis

Transform domain으로 이동하지 않고 원래 2D luminance map에서 직접 분석하는 방법을 별도 family로 검토하였다.

## 10.1 Global Statistics

- Mean
- Standard deviation
- Coefficient of Variation
- Percentile uniformity
- Peak-to-peak

권장 예:

\[
CV=\frac{\sigma}{\mu}
\]

\[
U_P=\frac{P_{99}-P_1}{\mu}
\]

## 10.2 Relative Luminance

\[
D(x,y)=\frac{L(x,y)-\mu}{\mu}
\]

목적:

- Gray level 간 상대 Mura 비교
- Absolute luminance 영향 감소

## 10.3 Surface / Gradient

Plane:

\[
\hat L(x,y)=a_0+a_1x+a_2y
\]

2차 surface:

\[
\hat L(x,y)
=
a_0+a_1x+a_2y+a_3x^2+a_4xy+a_5y^2
\]

Residual:

\[
R(x,y)=L(x,y)-\hat L(x,y)
\]

목적:

- Global shading과 local Mura 분리
- FFT 저주파 오염 감소

## 10.4 Local Statistics

- Local mean
- Local std
- Local RMS
- Local contrast

주요 대상:

- Cloud
- Local Mura
- Grain

## 10.5 Segmentation

Threshold 기반 candidate region:

\[
M(x,y)=
\begin{cases}
1,&|D(x,y)|>T\\
0,&otherwise
\end{cases}
\]

이후 connected component 분석.

추출 가능 feature:

- centroid
- area
- bounding box
- contrast
- width
- height

## 10.6 Shape

- Area
- Perimeter
- Major axis
- Minor axis
- Aspect ratio
- Orientation
- Eccentricity
- Circularity
- Solidity

## 10.7 Gradient / Edge

\[
G_x=\frac{\partial L}{\partial x}
\]

\[
G_y=\frac{\partial L}{\partial y}
\]

\[
G=\sqrt{G_x^2+G_y^2}
\]

Sobel, Scharr, multi-scale gradient 등이 후보.

## 10.8 Structure Tensor

Local orientation과 coherence 분석.

주요 대상:

- Vertical band
- Horizontal band
- Diagonal streak
- Local directional Mura

## 10.9 Autocorrelation

\[
R(\Delta x,\Delta y)
=
E[
L(x,y)L(x+\Delta x,y+\Delta y)
]
\]

주요 목적:

- correlation length
- periodicity
- FFT peak validation
- texture scale

---

# 11. Multi-scale Spatial Filtering

Gaussian scale-space:

\[
G_\sigma=L*Gaussian(\sigma)
\]

Difference of Gaussian:

\[
DoG_{\sigma_1,\sigma_2}
=
G_{\sigma_1}-G_{\sigma_2}
\]

Laplacian of Gaussian:

\[
LoG_\sigma
=
\nabla^2(G_\sigma*L)
\]

주요 대상:

- Cloud
- Blob
- Spot
- Scale-specific local Mura

---

# 12. Morphology

검토한 주요 연산:

- Opening
- Closing
- White Top-Hat
- Black Top-Hat

White Top-Hat:

\[
T_w=L-(L\circ B)
\]

Black Top-Hat:

\[
T_b=(L\bullet B)-L
\]

주요 대상:

- Bright spot
- Dark spot
- Blob
- Local Mura

---

# 13. Gabor

Gabor filter:

\[
g(x,y;\lambda,\theta,\sigma)
\]

Filter bank를 wavelength와 orientation 기준으로 구성한다.

\[
R_{\lambda,\theta}
=
L*g_{\lambda,\theta}
\]

주요 대상:

- Vertical band
- Horizontal band
- Diagonal band
- Streak
- Directional texture
- 특정 pitch/width를 가진 pattern

장점:

- 원하는 frequency/orientation을 직접 설계하기 쉬움

---

# 14. Radon Transform

\[
R(\rho,\theta)
\]

주요 대상:

- Long line
- Vertical/Horizontal line
- Diagonal line
- Streak

Diffuse cloud에는 상대적으로 적합하지 않다.

---

# 15. PCA / SVD

2D luminance matrix:

\[
L=U\Sigma V^T
\]

배경과 residual component 분리에 활용 가능하다.

큰 singular component:

- mean
- smooth shading
- global structure

작은 component:

- local structure
- defect
- noise

---

# 16. RPCA / Low-Rank + Sparse

\[
L=B+M+N
\]

또는

\[
L=L_{low-rank}+L_{sparse}
\]

개념:

- low-rank: background
- sparse: local defect
- noise: residual

주의:

- Large cloud는 sparse assumption에 맞지 않을 수 있음

---

# 17. Golden Reference

정상 panel reference:

\[
L_{ref}(x,y,G)
=
\frac1N\sum_iL_i(x,y,G)
\]

DUT difference:

\[
D(x,y,G)
=
\frac{L_{DUT}-L_{ref}}{L_{ref}}
\]

주요 목적:

- 정상 panel 구조 제거
- 공통 pattern 제거
- abnormal pattern 강조

중요 조건:

- registration / alignment

---

# 18. Population Analysis

ROI별 feature vector:

\[
\mathbf{x}
=
[
Spatial,
FFT,
DCT,
DWT,
DT\text{-}CWT,
Gabor,\ldots
]
\]

정상 population 기반 anomaly score 후보:

- Z-score
- Mahalanobis distance
- Isolation Forest
- One-Class SVM
- Autoencoder

Mahalanobis distance:

\[
D_M=
\sqrt{
(\mathbf{x}-\mu)^T
\Sigma^{-1}
(\mathbf{x}-\mu)
}
\]

---

# 19. Gray-Level Dependency

여러 Gray 조건을 활용하는 분석은 OLED 데이터에서 중요한 확장 축이다.

\[
M(x,y,G)
=
\frac{L(x,y,G)-\mu_G}{\mu_G}
\]

불량별 Gray response:

\[
S_k(G)
\]

검토 대상:

- Worst Gray
- Low-gray-specific Mura
- Gray-dependent band
- Persistent shading
- Severity-vs-Gray trend

---

# 20. HVS / JND / SEMU

물리적인 luminance deviation과 사람이 느끼는 Mura severity는 동일하지 않을 수 있다.

최종 perceptual severity 후보:

\[
Severity=
f(
Contrast,
Size,
SpatialFrequency,
BackgroundLuminance,
Location
)
\]

검토 방법:

- Human Visual System
- Just Noticeable Difference
- SEMU

이 계층은 실제 관능평가 및 OK/NG calibration과 연결될 수 있다.

---

# 21. 검토한 Mura 종류

현재까지 검토한 대표 분류:

## Global

- Gradient
- Shading
- Edge Mura

## Directional

- Vertical Band
- Horizontal Band
- Diagonal Mura
- Streak

## Periodic

- Periodic Line
- Ripple
- Grid
- Checker Pattern

## Local

- Local Band
- Cloud
- Blob
- Spot

## Texture

- Grain
- Fine Mura
- Random Texture

---

# 22. 분석 방법별 대표 역할

| 방법 | 대표 역할 |
|---|---|
| Spatial | Contrast / Area / Location / Shape |
| 1D FFT | Directional periodicity / pitch |
| 2D FFT | 2D periodicity / orientation |
| DCT | Global LF/MF/HF energy |
| DWT | Multi-scale local structure |
| DT-CWT | Scale + orientation + location |
| Gabor | Tunable frequency + orientation |
| Radon | Long line / streak |
| Morphology | Local bright/dark region |
| LoG / DoG | Blob / cloud / spot |
| PCA / SVD | Background decomposition |
| RPCA | Low-rank + sparse decomposition |
| HVS / JND / SEMU | Perceptual severity |
| Population model | Statistical abnormality |

---

# 23. Mura별 분석 후보

| Mura | 주요 후보 |
|---|---|
| Gradient | Surface fitting, DCT |
| Shading | Surface fitting, DCT |
| Vertical Band | X-profile, 1D FFT, 2D FFT, DT-CWT, Gabor |
| Horizontal Band | Y-profile, 1D FFT, 2D FFT, DT-CWT, Gabor |
| Periodic Line | 1D/2D FFT, Autocorrelation, Gabor |
| Local Band | Spatial, Multi-strip, DWT, DT-CWT, Gabor |
| Diagonal Mura | 2D FFT, DT-CWT, Gabor, Radon |
| Streak | Spatial shape, Structure Tensor, DT-CWT, Gabor, Radon |
| Grid | 2D FFT, Gabor, Autocorrelation |
| Ripple | 1D/2D FFT, Autocorrelation |
| Cloud | Local statistics, DoG/LoG, DWT, DT-CWT |
| Blob | Segmentation, LoG, DWT, DT-CWT |
| Spot | Segmentation, Morphology, LoG |
| Grain | Local RMS, DCT HF, DWT/DT-CWT HF |
| Random Texture | Statistics, Wavelet, Autocorrelation |

---

# 24. Severity

불량 존재 여부와 Severity는 분리하여 생각하였다.

개념적 Severity:

\[
S_k
=
f(
Contrast,
Area,
Location,
Scale,
Direction,
Periodicity,
BackgroundLuminance
)
\]

추가 구분:

- Detector score
- Confidence
- Physical severity
- Perceptual severity
- ROI-level severity
- Panel-level severity

최종 threshold는 실제 OK/NG 및 관능평가 데이터로 calibration하는 것이 적합하다.

---

# 25. 최종 분석 Architecture 후보

현재까지의 논의를 종합하면 다음 family 구성이 적절하다.

1. Spatial
2. Spectral
3. Multi-resolution
4. Directional
5. Decomposition
6. Cross-condition
7. Perceptual
8. Decision

개념:

```text
ROI Luminance
      │
      ├── Spatial
      ├── Projection
      ├── FFT / DCT
      ├── DWT / DT-CWT
      ├── Gabor / Radon
      ├── PCA / RPCA
      ├── Gray / Golden / Population
      └── HVS / JND / SEMU
                  │
                  ↓
             Feature Fusion
                  │
          ┌───────┴────────┐
          ↓                ↓
      Mura Type         Severity
```

---

# 26. 중요 고려사항

- FFT 하나로 모든 Mura를 판단하지 않는다.
- Spatial feature는 필수다.
- Transform별 역할을 구분한다.
- 위치 정보가 필요한 경우 spatial/local method를 사용한다.
- 정확한 pitch는 FFT가 유리하다.
- Local scale/orientation은 DT-CWT가 유리할 수 있다.
- 특정 frequency/orientation detector는 Gabor가 유리할 수 있다.
- Physical scale은 가능한 한 mm 단위로 해석한다.
- Frequency는 가능한 한 cycle/mm로 표현한다.
- Camera hole, rounded corner, ROI edge가 artificial response를 만들 수 있다.
- Camera/sensor artifact와 panel Mura를 구분해야 한다.
- 여러 Gray condition을 적극 활용한다.
- 최종 Severity는 perception과 연결될 가능성이 높다.
