# 사선 및 큰 동심원 주기성 얼룩 분석 방법 검토

> 작성일: 2026-09-10  
> 상태: 기획 참고 자료. 요구사항 또는 확정 설계가 아니다.

## 1. 검토 목적

현재 방식은 ROI를 X축 또는 Y축 방향으로 projection하여 1차원 profile을 만들고 FFT로
주기성을 분석한다. 이 문서는 다음 두 형태를 분석하기 위한 후보 방법을 정리한다.

- 임의 각도의 평행한 사선 주기 패턴
- 반경이 커서 제한된 ROI 안에서는 사선처럼 보이는 동심원 주기 패턴

특히 두 형태가 국소적으로 거의 같아 보일 때, 같은 ROI에 두 모델을 적용하여 결과를
비교하는 방법을 검토한다.

## 2. 핵심 결론

- 사선 패턴은 현재 1차원 FFT 구조를 임의 각도의 방향성 projection으로 확장하여
  분석할 수 있다.
- 일반적인 동심원 패턴은 중심을 기준으로 극좌표 변환한 뒤 반지름 방향 profile을
  분석하는 방법이 적합하다.
- 그러나 반경이 매우 큰 동심원은 짧은 원호만 관측되므로 중심과 반경을 직접 추정하면
  수치적으로 불안정하다.
- 큰 동심원은 먼저 ROI 안에서 관측되는 국소 곡률을 추정하고, 곡률이 충분히 확인될
  때만 중심과 반경을 파생하는 접근이 적합하다.
- 동일 ROI에 직선 주기 모델과 원호 주기 모델을 모두 적용하고, 적합도와 불확실성을
  비교해야 한다.
- 분석 결과는 `사선형`, `원호형`, `판별 불가`를 모두 표현할 수 있어야 한다.

## 3. 두 형태가 구분되지 않는 이유

반경이 `R`인 원에서 ROI가 관측하는 호의 길이를 `L`이라고 하면, 해당 원호가 접선에서
최대로 벌어지는 높이 `s`는 큰 반경에서 다음과 같이 근사할 수 있다.

```text
s ≈ L² / (8R)
```

ROI 양 끝에서 라인 방향이 변하는 정도는 다음과 같이 근사할 수 있다.

```text
Δθ ≈ L / R
```

`s`가 영상의 공간 해상도, 보간 오차, 패턴 폭 또는 노이즈보다 작으면 원호와 직선을
영상만으로 구분하기 어렵다. `Δθ`가 국소 방향 측정 오차보다 작을 때도 마찬가지다.

따라서 큰 동심원에서 중심을 찾지 못하는 것은 단순히 알고리즘이 부족해서가 아닐 수
있다. 관측한 호의 범위가 작으면 중심과 반경을 결정할 정보 자체가 부족해진다. 짧은
원호의 circle fitting에서 중심과 반경의 불확실성이 커지는 현상은 알려진 문제다.

## 4. 사선 주기 패턴 분석

### 4.1 신호 모델

평행한 사선 주기 패턴은 다음과 같이 나타낼 수 있다.

```text
I(x, y) = A cos(2π(fx·x + fy·y) + φ)
```

주파수 벡터 `(fx, fy)`는 라인과 나란한 방향이 아니라 밝기가 반복되는 법선 방향을
가리킨다.

```text
frequency = sqrt(fx² + fy²)
period = 1 / frequency
line angle = atan2(fy, fx) + 90°
```

현재처럼 X 또는 Y 방향으로만 평균하면 평균 방향을 따라서도 위상이 변하므로 신호가
서로 상쇄될 수 있다. ROI 크기와 사선 각도에 따라 FFT peak가 약해지거나 사라지는
문제가 생긴다.

### 4.2 후보 방법

#### 2D FFT

ROI 전체에 2D FFT를 적용하면 평행한 주기 패턴은 원점을 기준으로 대칭인 주파수 peak
쌍으로 나타난다. peak의 위치로 라인의 법선 방향과 주기를 함께 추정할 수 있다.

장점:

- 여러 방향의 후보를 한 번에 탐색할 수 있다.
- 방향과 주기를 동시에 초기 추정할 수 있다.
- 계산이 빠르다.

한계:

- 결과만으로 현재 GUI와 같은 1차원 profile을 바로 제공하기 어렵다.
- ROI 경계와 저주파 배경이 강한 성분으로 나타날 수 있다.
- 공간 내 어느 위치에서 패턴이 강한지는 전체 spectrum만으로 알기 어렵다.

#### Radon transform과 1D FFT

Radon transform은 임의 각도의 평행선을 따라 영상을 적분하여 각도별 1차원
projection을 만든다. 각 projection에 1D FFT를 적용하면 해당 방향의 주기성을 비교할
수 있다.

Fourier slice theorem에 따르면 한 각도의 Radon projection을 1D Fourier transform한
결과는 원본 영상의 2D Fourier transform에서 같은 방향의 단면과 대응한다.

장점:

- 현재의 profile, 정규화, 1D FFT, peak 분석 구조를 재사용하기 쉽다.
- 각도별 주기 강도를 직접 비교할 수 있다.
- 선택한 방향의 profile과 공간 오버레이를 구성하기 쉽다.

한계:

- 탐색 각도 간격에 따라 계산량과 각도 정밀도가 달라진다.
- 라이브러리마다 projection 각도와 line 각도의 정의가 다를 수 있다.
- 영상을 회전하거나 보간하는 구현에서는 경계와 보간 오차를 관리해야 한다.

### 4.3 검토상 권장 흐름

```text
ROI 전처리
→ 2D FFT로 주요 방향과 주기 후보 탐색
→ 후보 각도 주변에서 Radon projection을 정밀 탐색
→ 방향성 1D profile 생성
→ 기존 정규화·FFT·peak·위상 정합 적용
→ ROI 위에 임의 각도의 평행 주기선 표시
```

2D FFT는 후보 탐색에 사용하고, Radon projection은 사용자에게 보여줄 profile과 정밀
분석에 사용하는 결합 방식이다.

## 5. 일반적인 동심원 주기 패턴 분석

### 5.1 신호 모델

중심이 `(cx, cy)`인 동심원 패턴은 중심에서의 거리 `r`에 따라 밝기가 반복된다.

```text
r = sqrt((x - cx)² + (y - cy)²)
I(x, y) = A cos(2πr/P + φ)
```

중심이 알려져 있으면 영상을 Cartesian 좌표에서 polar 좌표 `(r, θ)`로 변환할 수 있다.
동심원은 polar 영상에서 반지름 축을 따라 반복되는 평행한 띠가 된다. 각도 방향으로
평균하면 방사형 1차원 profile을 만들 수 있다.

```text
중심 지정
→ polar 변환
→ 유효한 각도 방향으로 평균
→ radial profile
→ 정규화·1D FFT
→ 반지름 방향 주기 검출
→ 원본 ROI에 동심원 오버레이
```

### 5.2 한계

- 중심 오차가 있으면 같은 원이 polar 영상에서 굽은 선으로 나타난다.
- 각도 평균 과정에서 주기 신호가 퍼져 FFT peak가 넓어질 수 있다.
- 완전한 원이 ROI에 포함되지 않으면 반지름마다 사용할 수 있는 각도 범위가 달라진다.
- 중심이 ROI에서 매우 멀면 직접적인 중심 좌표 탐색 범위가 지나치게 커진다.

## 6. 큰 동심원에 대한 국소 곡률 분석

### 6.1 중심보다 곡률을 먼저 추정하는 이유

큰 원의 작은 일부는 직선에 가까우므로 중심 좌표와 반경을 직접 최적화하면 서로 매우
다른 중심과 반경이 비슷한 원호를 만들 수 있다. 이때 해가 불안정하고 ROI가 조금만
바뀌어도 중심이 크게 이동할 수 있다.

큰 동심원은 ROI 안에서 관측되는 방향과 곡률을 먼저 추정하는 것이 적합하다.

### 6.2 국소 원호 모델

ROI 기준점 주변에서 다음 좌표를 둔다.

- `u`: 패턴의 법선 방향 좌표
- `v`: 패턴과 나란한 접선 방향 좌표
- `κ`: 곡률, `κ = 1/R`

큰 원호는 국소적으로 다음과 같이 근사할 수 있다.

```text
u_arc ≈ u + (κ / 2)·v²
```

- `κ = 0`이면 평행한 사선 모델과 같다.
- `κ ≠ 0`이면 곡률이 있는 원호 후보가 된다.
- 곡률이 안정적으로 추정되면 `R = 1 / |κ|`로 반경을 계산할 수 있다.

이 모델은 사선 모델에 곡률 파라미터 하나를 추가한 중첩 모델이다. 따라서 같은 ROI와
같은 전처리 결과를 사용해 두 모델을 직접 비교하기 쉽다.

### 6.3 국소 방향장 이용

ROI를 여러 tile로 나누고 각 tile에서 국소 패턴 방향을 추정할 수 있다.

```text
사선 패턴
→ tile별 방향이 거의 동일
→ 법선들이 거의 평행

동심원 패턴
→ 위치에 따라 tile별 방향이 점진적으로 변함
→ 법선들을 연장하면 공통 중심 방향으로 모임
```

국소 방향 후보는 windowed 2D FFT, 국소 Radon transform, structure tensor 또는
방향성 filter bank로 구할 수 있다.

각 tile 위치를 `pi`, 법선 단위 벡터를 `ni`, 신뢰도 가중치를 `wi`라고 할 때 중심
후보 `C`는 다음 법선 교차 오차를 최소화하여 추정할 수 있다.

```text
E(C) = Σ wi · ||(I - ni·niᵀ)(C - pi)||²
```

법선들이 거의 평행하면 중심 해의 불확실성이 커진다. 이 상태는 알고리즘 오류로
숨기지 않고 현재 ROI에서 원호 여부를 판별하기 어렵다는 근거로 사용할 수 있다.

### 6.4 중심과 반경의 파생

곡률이 충분히 안정적으로 검출된 경우에만 ROI 기준점 `P0`와 법선 `n`으로부터 중심을
파생한다.

```text
C ≈ P0 ± n / κ
```

중심이 영상 밖에 있어도 좌표 계산은 가능하지만, 중심의 점 추정값만 표시하면 실제보다
정확해 보일 수 있다. 다음 정보를 함께 제시할 필요가 있다.

- 중심이 있을 것으로 추정되는 방향
- 곡률과 곡률의 불확실성
- 반경 추정 범위
- ROI 안에서 예상되는 최대 휨
- ROI 변경에 대한 추정값의 안정성

## 7. 사선 모델과 원호 모델 비교

### 7.1 비교 원칙

원호 모델은 사선 모델보다 파라미터가 많으므로 같은 데이터에서는 보통 조금 더 잘
맞는다. 단순히 원호 모델의 오차가 더 작다는 이유만으로 동심원이라고 판정하면 안 된다.

두 모델은 같은 ROI, 같은 mask, 같은 전처리, 같은 주파수 범위에서 비교해야 한다.

### 7.2 후보 비교 지표

#### Spectral concentration

좌표 변환 후 FFT 에너지가 하나의 주기 peak 주변에 얼마나 집중되는지 비교한다. 모델이
패턴 방향 또는 곡률을 잘 설명하면 projection 과정의 위상 상쇄가 줄어들어 peak가 더
좁고 뚜렷해질 가능성이 있다.

#### 위상 정합 residual

각 모델이 예측한 주기선과 실제 profile의 peak 또는 valley 위치 차이를 비교한다.

#### 국소 방향 residual

tile별로 관측한 방향과 각 모델이 예측한 방향의 차이를 비교한다.

- 사선 모델은 모든 tile에 하나의 방향을 예측한다.
- 원호 모델은 위치에 따라 조금씩 달라지는 방향을 예측한다.

#### Hold-out 검증

ROI의 일부 tile로 파라미터를 추정하고 나머지 tile에서 오차를 측정한다. 원호 모델의
추가 자유도가 학습 데이터에만 맞는 것을 줄이는 방법이다.

#### 모델 복잡도 보정

AIC, BIC 또는 별도로 정한 개선 임계값을 사용해 원호 모델의 추가 파라미터를 보정할 수
있다. 어떤 기준과 임계값을 사용할지는 후속 실험으로 결정해야 한다.

## 8. 결과 분류 후보

### 8.1 사선형

- 원호 모델을 적용해도 hold-out 오차가 의미 있게 개선되지 않는다.
- 곡률의 신뢰 범위에 0이 포함된다.
- tile별 방향 변화가 방향 측정 오차 이내다.
- ROI를 조금 변경했을 때 원 중심과 반경이 크게 변한다.

### 8.2 원호형

- 원호 모델이 사용하지 않은 tile에서도 일관되게 더 잘 맞는다.
- 곡률의 신뢰 범위가 0을 포함하지 않는다.
- tile별 법선이 공통 중심 방향으로 수렴한다.
- ROI를 이동하거나 크기를 바꿔도 곡률과 중심 방향이 유지된다.
- 중심을 이용한 radial profile의 FFT peak가 사선 projection보다 더 집중된다.

### 8.3 판별 불가

- 두 모델의 점수 차이가 비교 임계값보다 작다.
- 예상되는 원호의 휨이 영상 해상도 또는 정합 오차보다 작다.
- 중심과 반경의 신뢰 범위가 지나치게 크다.
- 원호 모델의 개선이 ROI 일부에만 나타난다.
- ROI를 약간 변경했을 때 분류가 뒤집힌다.

## 9. 전처리와 데이터 조건

### 9.1 ROI 경계

직사각형 crop의 경계는 2D FFT에서 강한 수평·수직 주파수 성분을 만든다. 2D Hann
window 등으로 경계의 불연속을 완화하는 방법을 검토해야 한다. 다만 window가 profile
진폭과 정량 지표에 미치는 영향도 함께 검증해야 한다.

### 9.2 배경 추세

완만한 밝기 gradient와 panel 전체의 명도 변화는 주파수 원점 주변의 저주파 에너지를
키운다. 방향과 주기 검출 전에 평균, 평면 또는 제한된 저차 추세 제거를 검토한다.

### 9.3 복수 방향

두 개 이상의 주기 패턴이 겹치면 structure tensor는 실제 어느 방향도 아닌 혼합 방향을
반환할 수 있다. 복수 방향 가능성이 있으면 2D FFT peak 후보 또는 방향성 filter bank로
여러 방향을 유지해야 한다.

### 9.4 물리 좌표

X축과 Y축의 pixel당 물리 길이가 다르면 pixel 좌표에서 원인 패턴이 물리 공간에서는
타원이거나 그 반대일 수 있다. 실제 panel 얼룩을 평가한다면 다음 물리 반지름을 사용할
가능성을 검토해야 한다.

```text
r_mm = sqrt(((x - cx)·dx_mm)² + ((y - cy)·dy_mm)²)
```

원형의 기준을 pixel 좌표로 할지 panel 물리 좌표로 할지는 아직 결정되지 않았다.

## 10. 결과 표시 후보

### 공통 분석 결과와 Top-K peak 연동

다음 항목은 사용자 요구로 확인된 공통 분석 흐름이다.

```text
ROI 주기성 profile
→ FFT Spectrum
→ Top-K peak
→ 사용자가 peak 선택
→ Profile 그래프에 해당 주기의 주기선 표시
→ ROI 이미지에도 같은 주기의 공간 주기선 표시
```

- 기존에 구현된 Profile 주기선 표시에 ROI 이미지 오버레이를 추가한다.
- Profile, FFT Spectrum, Top-K 목록과 ROI 이미지가 같은 peak 선택 상태를 공유한다.
- Peak 선택을 해제하면 해당 주기선이 Profile과 ROI 이미지에서 함께 제거된다.
- 같은 peak는 모든 표시 위치에서 같은 순번과 색상 등 일관된 식별 수단을 사용한다.
- 여러 peak를 선택할 수 있다면 각 peak의 오버레이를 서로 구분할 수 있어야 한다.
- ROI 이미지 주기선의 간격은 선택한 FFT peak의 주파수에서 계산된 주기를 유지한다.
- ROI 이미지 주기선의 시작 위치는 Profile 그래프에 적용한 위상 정합 결과와 일치해야
  한다.
- 사선 모델은 검출한 방향을 따르는 평행선으로 표시한다.
- 원호 모델은 추정한 곡률과 중심 방향을 따르는 원호 묶음으로 표시한다.
- 두 모델을 비교할 때 각각의 오버레이를 독립적으로 표시하거나 전환하여 영상과의
  정합 정도를 비교할 수 있어야 한다.

ROI 이미지 위의 주기선은 새로운 분석 결과를 만드는 것이 아니라, FFT와 Profile에서
선택한 주기가 실제 영상의 어느 반복 위치를 설명하는지 확인하기 위한 공간 표현이다.

### 사선 분석

- 라인 방향과 법선 방향
- 주기와 주파수
- 방향성 profile과 FFT
- 방향성 강도와 신뢰도
- ROI 위 평행 주기선 오버레이

### 큰 동심원 분석

- 국소 접선 방향
- 곡률과 곡률 신뢰 범위
- 추정 반경 또는 반경 범위
- 중심 예상 방향과 중심 불확실성
- radial profile과 FFT를 계산할 수 있는지 여부
- ROI 위 원호 주기선 오버레이

### 비교 결과

- 사선 모델 점수
- 원호 모델 점수
- 원호 모델의 추가 개선량
- ROI 안에서 예상되는 휨
- `사선형`, `원호형`, `판별 불가` 중 하나의 결과와 그 근거

공통 분석 결과와 Top-K peak 연동은 사용자 요구다. 그 밖의 세부 지표와 구체적인 화면
배치는 검토 후보이며 최종 UI 요구가 아니다.

## 11. 단계적 실험 후보

1. 합성 사선 패턴에서 각도와 주기 추정 오차를 확인한다.
2. 반경과 ROI 크기를 바꾼 합성 원호 패턴에서 곡률 검출 한계를 확인한다.
3. 동일한 국소 방향과 주기를 가진 사선·원호 pair를 만들어 두 모델의 점수를 비교한다.
4. 노이즈, 명도 gradient, ROI 경계, 부분 mask 조건을 추가한다.
5. ROI를 이동하거나 크기를 바꿨을 때 분류와 파라미터가 유지되는지 확인한다.
6. 실제 OLED 영상에서 합성 실험의 판별 기준이 유지되는지 확인한다.

실험을 통해 정해야 할 주요 값은 다음과 같다.

- 방향 탐색 간격과 정밀화 범위
- tile 크기와 중첩 비율
- 최소 검출 주기와 최대 검출 주기
- 곡률 검출 최소 한계
- line과 arc 모델의 최소 점수 차이
- `판별 불가`로 처리할 불확실성 범위

## 12. 열린 결정

- 사선과 원호 분석을 항상 함께 실행할지, 개별 모드도 제공할지
- 2D FFT와 Radon transform의 역할 분담
- 큰 동심원을 국소 곡률까지만 분석할지, 중심과 반경까지 제공할지
- 중심을 사용자가 지정하거나 보정할 수 있게 할지
- pixel 좌표와 panel 물리 좌표 중 어느 좌표계에서 원형을 정의할지
- 일정하지 않은 radial period를 이번 범위에서 다룰지
- 복수 방향 패턴을 이번 범위에서 다룰지
- 모델 비교 지표와 판정 임계값
- 사선·원호 비교 화면의 구체적인 배치와 오버레이 전환 방식

## 13. 참고 자료

- SciPy, `fft2`: 2차원 discrete Fourier transform API.
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft2.html>
- SciPy, Spectral Analysis: window에 따른 spectral leakage 설명.
  <https://docs.scipy.org/doc/scipy/tutorial/signal.html>
- scikit-image, Radon transform 예제: 각도별 1차원 projection과 sinogram.
  <https://scikit-image.org/docs/0.23.x/auto_examples/transform/plot_radon_transform.html>
- Kingston and Svalbe, Generalised finite Radon transform: Fourier slice theorem과
  projection의 관계.
  <https://www.sciencedirect.com/science/article/abs/pii/S0262885606001119>
- scikit-image, `warp_polar`: Cartesian 영상을 polar 또는 log-polar 좌표로 변환하는
  API.
  <https://scikit-image.org/docs/stable/api/skimage.transform.html>
- Liu et al., An Improved Circular Fringe Fourier Transform Profilometry: 닫힌 원형
  fringe에 대한 Cartesian-to-polar 변환 기반 Fourier 분석.
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC9416724/>
- Hopp, The Sensitivity of Three-Point Circle Fitting: 관측 arc angle과 중심·반경 추정
  불확실성의 관계.
  <https://www.nist.gov/publications/sensitivity-three-point-circle-fitting>
- Silveira, An Algorithm for the Detection of Multiple Concentric Circles: 중심 검출과
  반경 검출을 분리한 concentric circle 검출 방법.
  <https://researchportal.ulisboa.pt/en/publications/an-algorithm-for-the-detection-of-multiple-concentric-circles/>
- Kanatani, Uncertainty Modeling and Model Selection for Geometric Inference: line,
  circle 등 복잡도가 다른 기하 모델의 정보 기준 비교.
  <https://iim.cs.tut.ac.jp/member/kanatani/papers/pamodel2.pdf>
- Michelet et al., Estimating Local Multiple Orientations: 복수 방향이 있을 때 단일
  structure tensor 방향 추정이 혼합될 수 있는 문제.
  <https://www.sciencedirect.com/science/article/abs/pii/S0165168407000187>
