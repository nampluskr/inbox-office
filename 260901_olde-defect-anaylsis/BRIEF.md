# BRIEF.md

## 1. 목적

본 프로젝트의 목적은 **2D 촬상기로 측정한 OLED 디스플레이의 휘도(Luminance) 데이터를 이용하여 화질 불량 또는 얼룩(Mura)을 분석하는 시스템을 개발하는 것**이다.

이 문서는 사용자의 순수한 의도와 요구사항만 정의한다.  
특정 알고리즘, 수학적 변환, 구현 방법은 본 문서의 범위에서 제외한다.

---

## 2. 측정 대상

분석 대상은 스마트폰용 OLED 디스플레이와 같은 평판 디스플레이이다.

예시:

- Galaxy S26급 OLED 디스플레이
- Camera hole이 존재하는 OLED
- Corner rounding이 적용된 OLED
- 비직사각형 유효 표시영역을 갖는 OLED

---

## 3. 입력 데이터

OLED 디스플레이에 White image를 표시하고, 특정 Gray Scale 및 특정 목표 휘도 조건에서 2D 촬상기로 휘도를 측정한다.

입력 데이터의 특성은 다음과 같다.

- 2D luminance map
- 1-channel
- floating-point
- OLED display와 동일한 spatial shape
- 파일 형식:
  - TIFF
  - MIM
  - CSV
  - 향후 추가 포맷 가능
- 측정 조건 정보:
  - Gray Scale
  - Target Luminance
  - 필요 시 패널/측정 메타데이터

---

## 4. ROI 요구사항

OLED 디스플레이에는 Camera hole, rounded corner 등 분석에서 제외해야 하는 영역이 존재할 수 있다.

따라서 사용자는 분석할 ROI를 직접 지정할 수 있어야 한다.

ROI 요구사항:

- 복수 ROI 지원
- ROI는 상대 좌표 기반
- 좌측 상단과 우측 하단 좌표로 정의
- 좌표 범위는 정규화된 상대 비율 사용
- ROI별 독립적인 얼룩 분석
- Camera hole과 corner 영역은 필요 시 분석 대상에서 제외
- ROI별 결과 비교 가능

---

## 5. 분석 목적

각 ROI에 대해 OLED 화질 불량 또는 얼룩을 검출하고 특성을 정량화하고자 한다.

주요 분석 결과는 다음을 포함해야 한다.

- Mura 존재 여부
- Mura 종류
- Mura 위치
- Mura 방향
- Mura 크기
- Mura 폭
- Mura 면적
- Mura contrast
- Mura 주기
- 대표 spatial scale
- 계조별 특성
- Worst Gray
- Severity
- ROI별 결과
- Panel-level summary

---

## 6. 불량 종류

최종 시스템은 다양한 OLED 화질 얼룩을 구분할 수 있어야 한다.

대표 대상:

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
- Grid / Checker pattern
- Cloud
- Blob
- Spot
- Grain
- Fine Mura
- Random Texture

불량 종류는 프로젝트 진행 중 실제 데이터와 현업 정의에 맞추어 확장 또는 통합할 수 있다.

---

## 7. Gray Scale / 휘도 조건

동일한 패널을 여러 Gray Scale 또는 Target Luminance 조건에서 측정할 수 있다.

따라서 시스템은 단일 2D image 분석뿐 아니라 다음과 같은 조건 의존성을 분석할 수 있어야 한다.

- Gray별 Mura 변화
- Target Luminance별 Mura 변화
- 저계조에서 악화되는 Mura
- 특정 계조에서만 나타나는 Mura
- 전 계조에 걸쳐 유지되는 Mura
- Worst Gray / Worst Condition

---

## 8. 결과의 성격

최종 시스템은 단순한 OK/NG 판정만을 목표로 하지 않는다.

가능하면 다음과 같이 **설명 가능한 결과**를 제공해야 한다.

예:

```text
Primary Defect : Vertical Banding
Severity       : 78

Location       : Right-Center
Contrast       : 2.8 %
Pitch          : 11.7 mm
Active Area    : 43 %
Worst Gray     : G16
```

사용자가 왜 해당 불량으로 판정되었는지 해석할 수 있어야 한다.

---

## 9. 장기 목표

장기적으로 다음을 지원할 수 있는 OLED 화질 분석 시스템을 구축하는 것이 목표다.

- 자동 Mura 검출
- 자동 Mura 분류
- 정량적 Severity
- ROI별 분석
- Gray dependency 분석
- Panel comparison
- Golden reference comparison
- Population-based abnormality detection
- Explainable decision
- 향후 Machine Learning / Deep Learning 확장
- 실제 OK/NG 및 관능평가와의 calibration

---

## 10. 본 프로젝트의 핵심 원칙

- 실제 OLED 화질 분석에 사용 가능한 결과를 제공한다.
- 분석 결과는 가능한 한 물리적으로 해석 가능해야 한다.
- ROI별 독립 분석을 지원한다.
- 위치, 크기, 방향, 주기, contrast 등 정량적 특성을 유지한다.
- 측정 artifact와 실제 panel Mura를 구분할 수 있는 구조를 고려한다.
- 향후 실제 데이터와 관능평가를 이용하여 판정 기준을 개선할 수 있어야 한다.
