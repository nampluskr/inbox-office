> 버전: v0.1 · 상태: 마감

# DECISIONS

## D-1. Python 단일 런타임과 pywebview를 사용한다

- 선택: pywebview와 Windows WebView2를 데스크톱 shell로 사용한다.
- 근거: NumPy와 SciPy가 필수이므로 Python 런타임은 이미 필요하다. HTML/CSS와 Plotly.js를 사용해 전문 분석 도구 수준의 UI를 구현할 수 있다.
- 배제한 대안: Electron과 Python subprocess 조합은 Node.js와 Python의 이중 런타임 및 별도 IPC 설계가 필요하므로 배제했다. PyQt는 기본 위젯 스타일의 한계와 사용자 요구에 따라 배제했다.

## D-2. 계산은 Python, 표시는 JavaScript가 담당한다

- 선택: 이미지 처리, profile, FFT, peak 탐색과 오류 변환은 Python API가 수행하고 JavaScript는 반환 데이터를 표시·상호작용 처리만 한다.
- 근거: 수치 계산의 단일 기준을 유지하고 JS와 Python 사이의 계산 불일치를 방지한다.
- 배제한 대안: JavaScript에서 FFT 또는 peak를 재계산하는 방식은 계산 기준이 분산되므로 배제했다.

## D-3. 분석 기준은 MATLAB 원본을 우선한다

- 선택: 수치 계산의 참조 우선순위를 `legacy/matlab/` 1순위, `legacy/python/fft.py` 2순위로 둔다.
- 근거: MATLAB 자료가 원본 분석 로직이며 Python ver1 구현은 교차 검증용이다.
- 배제한 대안: legacy 코드를 런타임 의존성으로 직접 사용하는 방식은 새 구현의 독립성과 유지보수를 해치므로 배제했다.

## D-4. 배포는 PyInstaller를 사용한다

- 선택: PyInstaller onefile 또는 onedir 빌드로 Windows 실행 파일을 만든다.
- 근거: Python 런타임과 필요한 웹 자산을 함께 패키징할 수 있고 별도 Node.js 배포 체인이 필요 없다.
- 배제한 대안: Electron 또는 별도 설치 도구 중심 패키징은 v0.1 핵심 파이프라인에 불필요한 배포 복잡도를 추가하므로 배제했다.
