# FFT ROI Analysis GUI 제품 요구사항

| 항목 | 값 |
| --- | --- |
| 상태 | Active |
| 작성일 | 2026-07-16 |
| 적용 범위 | 사용자, 제품 범위, 기능 및 비기능 요구사항 |
| 관련 문서 | [상세 기술 문서와 문서 색인](../README.md) |

## 문서 목적

이 문서는 FFT ROI Analysis GUI의 현재 확정된 제품 기준을 정의하는 canonical 문서다. 분석 수치 규칙, 설정 JSON, 출력 file 계약, 화면 layout 및 module 구조는 이 문서의 범위가 아니다.

## 현재 확정 기준

### 제품 목적

- `260713_fft-analysis-common-ver1`의 범용 ROI 분석을 Windows GUI에서 사용할 수 있게 한다.
- 사용자가 GUI에서 ROI와 분석 조건을 설정해 선택한 MIM 파일을 즉시 분석하고, 선택 항목 또는 전체 목록을 같은 조건으로 batch 처리할 수 있게 한다.
- ROI, 이미지 실제 크기와 분석 parameter를 저장해 같은 조건을 재사용한다.
- 분석 입력, 설정과 결과를 추적 가능한 형태로 보존한다.
- 기존 분석 결과 호환성을 유지하면서 전체 배포 폴더와 ZIP 크기를 단계적으로 줄인다.

### 주요 사용자

- MIM 이미지를 검토하고 ROI별 얼룩 주기성을 확인하는 분석 담당자
- 여러 sample과 condition을 같은 설정으로 비교하는 평가 담당자
- CSV, PNG와 PPTX 결과를 이용해 분석 보고서를 작성하는 사용자

### 입력과 결과물

- 입력은 선택 root 아래에서 재귀 검색한 `.mim` 2D grayscale 이미지와 사용자가 설정한 ROI 및 분석 조건이다.
- 결과물은 화면의 분석 미리보기와 UTF-8 CSV, PNG 및 선택적 PPTX다.
- PPTX template이 선택되지 않은 경우에도 CSV와 PNG 저장은 가능해야 한다.

### 핵심 기능

- 선택 root 아래 모든 하위 폴더에서 `.mim` 파일을 재귀 검색하고 단일 또는 복수 파일을 선택한다.
- 원본 이미지와 ROI overlay를 표시하고 ROI를 추가, 삭제, 이동, 크기 변경 및 색상 지정한다.
- horizontal 및 vertical profile, Peak-to-Valley, FFT intensity와 Top-K peak를 확인하고 peak의 mm 주기를 표시한다.
- 현재 파일, 선택 항목 및 전체 목록을 분석하고 결과를 저장한다.
- 설정을 저장하고 다시 불러온다.
- 개별 파일, ROI 또는 direction 오류를 기록하되 사용자가 취소하지 않은 batch는 계속 처리한다.
- 검색 및 batch 진행률, 취소 상태와 오류 수를 사용자에게 표시한다.

### 비기능 요구사항

- 최종 사용자는 Python을 별도로 설치하지 않은 Windows 10/11 x64 환경에서 GUI를 실행할 수 있어야 한다.
- 배포물은 PyInstaller `onedir` 형태의 실행 파일과 runtime 파일이 포함된 전체 폴더다.
- 기존 분석 결과는 golden result와 허용 오차 안에서 호환성을 검증한다.
- 분석 입력, 사용한 설정과 결과는 추적할 수 있게 보존한다.
- 한 파일의 읽기 또는 분석 실패가 취소되지 않은 batch 전체를 중단시키지 않아야 한다.

## 범위 경계

- 분석 공식, ROI validation, FFT 단위와 Top-K 산정은 현재 [상세 기술 문서](../README.md)의 분석 기준을 따른다.
- 설정 JSON field와 validation은 현재 [상세 기술 문서](../README.md)의 ROI 설정 JSON 계약을 따른다.
- CSV column, PNG, PPTX template 및 오류 log의 상세 계약은 현재 [상세 기술 문서](../README.md)의 결과 저장 계약을 따른다.
- 화면 영역, interaction과 비동기 표시 규칙은 [GUI layout 명세](../design/gui-layout-spec.md)를 따른다.
- module 책임, data flow와 thread model은 [시스템 구조](../design/system-architecture.md)를 따른다.

## 향후 확정 필요

- 제품 차원의 명시적 제외 범위
- 기능별 상세 인수 조건과 우선순위
- 허용 가능한 처리 시간, 메모리 사용량, 배포 크기의 수치 목표
- 접근성, keyboard 조작과 화면 해상도별 사용성 기준

