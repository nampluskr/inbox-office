# FFT ROI Analysis GUI ver0

## 프로젝트 소개

FFT ROI Analysis GUI는 `.mim` 2D grayscale 이미지의 관심 영역을 대상으로 가로줄과 세로줄 얼룩의 주기성을 분석하는 Windows 데스크톱 도구다.

기존 `260713_fft-analysis-common-ver1`의 MIM 로딩, ROI, profile과 FFT 분석 결과를 기준으로 삼고, 사용자가 GUI에서 ROI와 분석 조건을 설정해 단일 파일 또는 여러 파일을 일관된 방식으로 분석할 수 있게 하는 것이 목적이다.

## 주요 사용자

- MIM 이미지를 검토하고 ROI별 얼룩 주기성을 확인하는 분석 담당자
- 여러 sample과 condition을 같은 설정으로 비교하는 평가 담당자
- CSV, PNG와 PPTX 결과를 이용해 분석 보고서를 작성하는 사용자

## 핵심 기능

- 선택한 폴더의 모든 하위 폴더에서 MIM 파일 검색
- MIM 이미지와 ROI overlay 표시
- ROI 생성, 이동, 크기 변경 및 설정 저장·로딩
- horizontal 및 vertical profile 분석
- FFT intensity와 Top-K peak 탐색
- peak 주기의 profile 표시
- 선택 파일과 전체 목록의 batch 분석
- CSV와 PNG 저장 및 template 기반 PPTX 생성
- 개별 파일 오류 기록과 batch 처리 계속

## 사용자 흐름

```text
폴더 선택
    -> MIM 파일 검색 및 선택
    -> 이미지와 ROI 확인
    -> ROI 및 분석 조건 설정
    -> profile과 FFT 미리보기
    -> Top-K peak와 주기 확인
    -> 단일 또는 batch 분석
    -> CSV, PNG 및 선택적 PPTX 저장
```

## 배포 형태

GUI는 PyQt5와 Qt Designer를 기반으로 개발한다. 최종 사용자는 Python을 별도로 설치하지 않으며, PyInstaller `onedir`로 생성된 `fft-analysis-gui.exe`와 runtime 파일이 포함된 전체 폴더를 전달받는다.

## 문서 안내

분석 정의, GUI 구조, 설정과 출력 계약, 개발 환경, 배포 및 검증 기준은 [상세 기술 문서와 문서 색인](docs/README.md)을 참조한다.

문서 수정, 코드 구현과 결과 확인의 반복 절차 및 향후 문서 분리 계획은 [문서 구조 및 작성 계획](docs/development/plans/0001-documentation-structure-plan.md)을 참조한다.
