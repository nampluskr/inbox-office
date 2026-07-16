# FFT ROI Analysis GUI layout 명세

| 항목 | 값 |
| --- | --- |
| 상태 | Active |
| 작성일 | 2026-07-16 |
| 적용 범위 | 화면 영역, 사용자 interaction 및 화면 상태 |
| 관련 문서 | [상세 기술 문서와 문서 색인](../README.md) |

## 문서 목적

이 문서는 FFT ROI Analysis GUI의 현재 확정된 화면 영역과 interaction 기준을 정의하는 canonical 문서다. 정확한 widget 종류, object name, pixel 크기, splitter 비율과 tab 내부 배치는 이 문서에서 확정하지 않는다.

## 현재 확정 기준

### 좌측 탐색 영역

- 분석 root 폴더를 선택한다.
- 선택 root의 모든 하위 폴더에서 MIM 파일을 검색한다.
- 각 항목에 상대 경로, 부모 폴더, sample ID와 파일명을 표시한다.
- 단일 또는 복수 파일을 선택한다.
- 검색 및 batch 진행률, 취소와 오류 수를 표시한다.

### 우측 분석 영역

- 원본 이미지와 ROI overlay를 표시한다.
- ROI별 profile과 FFT intensity를 표시한다.
- Top-K peak 표와 rank를 표시한다.
- 선택한 peak의 주기를 profile에 반복 간격으로 표시한다.
- 현재 파일을 분석하고 결과를 저장하는 기능을 제공한다.

### ROI 및 설정 탭

- ROI를 추가, 삭제하고 이름과 색상을 변경한다.
- 정규화 좌표와 pixel 좌표를 확인한다.
- 이미지의 실제 가로·세로 길이와 회전을 설정한다.
- horizontal 또는 vertical 방향을 활성화한다.
- 평균 filter, reference filter와 Top-K를 설정한다.
- JSON 설정을 저장하고 불러온다.
- 출력 폴더와 PPTX template을 선택한다.

### 사용자 interaction 흐름

```text
폴더 선택
    -> MIM 파일 검색 및 선택
    -> 이미지와 ROI 확인
    -> ROI 및 분석 조건 설정
    -> profile과 FFT 미리보기
    -> Top-K peak와 주기 확인
    -> 현재 파일, 선택 항목 또는 전체 목록 분석
    -> CSV, PNG 및 선택적 PPTX 저장
```

### 작업 상태와 오류 표시

- 검색과 분석의 장시간 작업은 GUI가 응답 가능한 상태에서 진행률과 취소 상태를 표시한다.
- 개별 파일, ROI 또는 direction 오류는 식별 가능한 원인과 함께 오류 목록에 표시한다.
- 사용자가 취소하지 않은 batch는 개별 오류가 발생해도 다음 항목을 계속 처리한다.
- 이전 비동기 작업의 결과는 새 화면 상태를 덮어쓰지 않아야 한다. worker와 GUI의 구현 규칙은 [시스템 구조](system-architecture.md)의 thread model을 따른다.

## 범위 경계

- 제품 기능과 배포 요구사항은 [제품 요구사항](../product/product-spec.md)을 따른다.
- module 책임과 worker 구현 경계는 [시스템 구조](system-architecture.md)를 따른다.
- ROI, 분석 parameter, JSON과 결과 file의 상세 계약은 현재 [상세 기술 문서](../README.md)에 유지한다.

## 향후 확정 필요

- widget 종류와 object name
- 창의 기본 크기, 최소 크기, splitter 비율과 탭의 정확한 내부 배치
- keyboard 조작, focus 순서, 접근성 및 화면 해상도별 동작
- 빈 목록, loading, validation 실패와 저장 완료의 세부 화면 상태
- Qt Designer 구현에 필요한 wireframe과 widget property 계약

