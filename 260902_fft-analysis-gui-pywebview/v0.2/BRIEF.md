> 버전: v0.2 · 작성일: 2026-09-02

# BRIEF

- 상세 요구사항과 판정 기준은 [[SPEC]] 1~4절을 따른다.

## 1. 배경

- v0.1에서 ROI 기반 FFT 분석의 핵심 파이프라인과 Windows GUI를 완성했다.
- v0.2에서는 세션마다 다시 입력해야 했던 분석 설정과 ROI를 파일에 저장한다.
- 서로 다른 제품의 분석 조건을 하나의 GUI에서 선택하고 관리할 수 있게 한다.
- GUI와 그래프의 시각 체계를 통합해 scientific 전문 분석 도구 수준으로 개선한다.

## 핵심 원칙 (SSOT)

- **FFT 분석용 GUI는 scientific/전문 분석 툴 수준의 디자인으로 작성되어야 한다.**
- 이 원칙은 v0.1에서 승계하며, v0.2의 기능·폰트·레이아웃·간격·색상·테마·그래프 표현에 관한 다른 모든 결정보다 우선한다.
- ROI FFT 분석 기능 구현에 그치지 않고 디자인 완성도를 프로젝트의 핵심 가치로 둔다.
- 기본 GUI 위젯이나 Plotly 기본 스타일을 그대로 노출해 단순하거나 부실하게 보이지 않게 한다.
- 타이포그래피, spacing, grid, 색상 팔레트와 테마를 전문 과학 분석 도구 수준으로 일관되게 설계한다.
- GUI 프레임워크는 pywebview를 유지하고, HTML·CSS 기반 디자인 시스템으로 시각 품질을 확보한다.
- Dark·Gray·White 테마는 공통 디자인 token으로 관리해 GUI와 그래프에 동일하게 적용한다.

## 2. 이번 버전에서 풀고 싶은 문제

### 2.1 설정 파일과 초기값

- 설정 파일 형식은 JSON을 사용한다.
- 설정 파일 이름은 `setting.json`으로 한다.
- 배포된 GUI 실행 파일과 같은 폴더에서 `setting.json`을 읽는다.
- `setting.json`이 없으면 현재 프로그램의 기본값으로 같은 폴더에 새 파일을 만든다.
- 하나의 `setting.json` 안에 여러 제품의 설정을 함께 저장한다.
- 처음 생성되는 파일에는 `Default` 제품을 포함한다.
- 맨 처음 실행할 때 `Default`를 active product로 선택한다.
- 제품과 무관한 GUI 설정과 제품별 분석 설정을 구분해 저장한다.

### 2.2 제품별 저장 항목

- 제품별 물리 크기와 프로그램에 정의된 분석 설정값을 저장한다.
- 각 제품에 ROI 목록을 포함한다.
- 각 ROI의 이름과 정규화 좌표를 저장한다.
- TOP-K는 선택 제품의 공통 분석 설정으로 저장한다.
- FFT 기본 표시 범위 비율은 선택 제품의 공통 분석 설정으로 저장한다.
- AVG BAND와 REF BAND는 각 ROI의 분석 설정으로 저장한다.
- ROI 탭에서 사용하는 나머지 분석 설정값도 유실되지 않도록 `setting.json`에 포함한다.
- 제품을 다시 선택하거나 앱을 다시 실행하면 저장된 설정과 ROI를 복원한다.

### 2.3 Setting 탭과 active product

- 기존 고정 탭 이름을 `Overview`에서 `Setting`으로 변경한다.
- 기존 Overview 탭 우측의 `Full Panel` 영역을 active product 선택 영역으로 교체한다.
- 맨 처음 실행할 때 `Default`가 선택되고, 해당 제품의 JSON 설정 내용이 화면에 표시된다.
- Setting 탭에서 active product를 선택할 수 있다.
- Setting 탭에서 선택 제품의 설정과 ROI를 확인하고 수정할 수 있다.
- 수정한 내용을 명시적으로 저장할 수 있다.
- 제품을 전환하면 해당 제품의 설정과 ROI를 GUI에 적용한다.
- 기존 탭 영역 오른쪽의 톱니바퀴 Settings 아이콘과 Settings 모달은 제거한다.

### 2.4 ROI 탭 분석 설정

- ROI 탭의 AVG BAND와 REF BAND는 선택 제품의 해당 ROI 설정을 표시한다.
- ROI 탭에서 AVG BAND와 REF BAND를 수정할 수 있다.
- ROI 탭에서 수정한 분석 설정은 선택 제품의 ROI 설정으로 저장한다.
- ROI 분석에는 Setting 탭에서 지정한 선택 제품의 TOP-K를 적용한다.

### 2.5 TOP PEAKS 테이블

- 각 ROI 탭의 TOP PEAKS 영역을 테이블 형태로 변경한다.
- TOP PEAKS 테이블에는 헤더를 표시한다.
- Setting 탭에서 TOP-K 값을 늘리면 TOP PEAKS 테이블의 행도 늘어난다.
- Setting 탭에서 TOP-K 값을 줄이면 TOP PEAKS 테이블의 행도 줄어든다.
- 피크 선택 기능과 선택 피크의 profile 주기 오버레이 기능은 유지한다.
- FFT Intensity 그래프에서 모든 TOP-K peak를 동일한 노란색 `x`로 표시하지 않는다.
- TOP-K peak마다 서로 다른 구별 가능한 색상을 적용한다.
- 각 peak 위치에는 해당 색상의 작은 filled circle marker를 표시한다.
- peak 순번은 TOP PEAKS 테이블의 행 순번과 동일하게 `1~K`로 표시한다.
- 각 peak 위에는 `[순번] X축값` 형식의 작은 직사각형 badge를 표시한다.
- X축값은 현재 그래프 단위에 따라 frequency를 cycles/px 또는 cycles/mm로 표시한다.
- marker, badge와 TOP PEAKS 테이블의 순번 표시에는 같은 peak 색상을 사용한다.
- 선택한 peak의 profile 주기 오버레이에도 해당 peak 색상을 사용한다.
- 선택한 peak의 Profile 주기선은 고정된 0 위치에서 시작하지 않고, 실제 Profile의 반복 peak 또는 valley와 전체적으로 가장 잘 맞는 위치에 표시한다.
- Profile 주기선은 FFT에서 찾은 주기 간격을 동일하게 유지하면서 전체 위치 오차를 최소화한다.
- 밝고 어두운 반복 패턴을 모두 다룰 수 있도록 Profile의 peak와 valley 중 정합도가 높은 극성을 사용한다.
- 정합도가 낮은 경우에도 실제 데이터보다 정확한 것처럼 오인되지 않도록 정합 결과의 신뢰도를 구분할 수 있어야 한다.
- TOP PEAKS 테이블의 행을 선택하면 해당 peak의 주기선을 위쪽 Profile 그래프에 표시한다.
- FFT Intensity 그래프의 peak marker 또는 badge를 선택해도 TOP PEAKS 행 선택과 동일하게 동작한다.
- TOP PEAKS 테이블과 FFT Intensity 그래프는 같은 peak 선택 상태를 공유하고 선택 표시를 양방향으로 동기화한다.
- 선택된 peak의 marker, badge, TOP PEAKS 행과 Profile 주기선은 모두 해당 peak의 고유 색상을 사용한다.
- 여러 peak를 선택하면 각 peak의 고유 색상으로 Profile 주기선을 함께 표시한다.
- 선택된 TOP PEAKS 행이나 FFT peak를 다시 선택하면 해당 peak 선택과 Profile 주기선을 해제한다.
- All 보기에서는 Horizontal과 Vertical peak 선택 상태 및 Profile 주기선을 서로 독립적으로 관리한다.
- 색상만으로 peak를 구분하지 않고 순번을 항상 함께 표시한다.
- peak 색상은 Dark·Gray·White 테마에서 모두 배경과 구별되는 대비를 유지한다.

### 2.6 ROI 그래프 글꼴과 축 정렬

- ROI 탭의 Profile 그래프와 FFT 그래프에 GUI 기본 글꼴을 적용한다.
- 그래프의 축 제목, 눈금, tooltip 등 내부 글꼴을 GUI와 일관되게 표시한다.
- 위쪽 Profile 그래프와 아래쪽 FFT 그래프의 y축 기준선을 같은 가로 위치에 정렬한다.
- 창 크기가 바뀌어도 두 그래프의 plot 영역 시작 위치가 서로 어긋나지 않게 한다.

### 2.7 Scientific 그래프 스타일

- GUI 테마와 그래프 영역의 배경색을 일관되게 적용한다.
- 다크 테마에서 Plotly 기본 흰색 배경을 사용하지 않는다.
- X축과 Y축이 plot 내부에서 교차하는 십자 형태를 사용하지 않는다.
- Matplotlib 기본 축 형태와 유사하게 plot 영역의 네 변을 감싸는 직사각형 frame을 표시한다.
- X축은 직사각형 하단, Y축은 직사각형 좌측을 기준으로 표시한다.
- 그래프의 배경, 축, 눈금, grid line, tooltip 색상을 전체 테마에 맞게 조정한다.
- Profile 신호선, FFT 신호선, peak marker, 선택 주기 오버레이를 서로 구별되는 색으로 표시한다.
- grid line은 분석 신호보다 두드러지지 않는 절제된 스타일로 표시한다.
- 배경 장식보다 분석 신호와 선택 피크가 먼저 읽히는 scientific 전문 분석 도구 스타일을 적용한다.

### 2.8 Dark·Gray·White 테마

- `markdown_browser` 프로젝트의 테마 전환 방식을 참고한다.
- GUI에 Dark, Gray, White 세 가지 테마를 제공한다.
- Gray를 GUI 기본 테마로 사용한다.
- 테마 변경 아이콘을 탭 영역 오른쪽의 창 제어 버튼 바로 왼쪽에 배치한다.
- 테마 아이콘을 누르면 White → Gray → Dark → White 순서로 전환한다.
- GUI의 Explorer, 탭, 입력 필드, 버튼, 경계선과 텍스트에 선택 테마를 일관되게 적용한다.
- Profile·FFT 그래프와 TOP PEAKS 테이블에도 같은 테마를 적용한다.
- 마지막으로 선택한 테마를 제품과 무관한 GUI 설정으로 저장하고 다음 실행 때 복원한다.

### 2.9 그래프의 물리 단위

- 선택 제품의 Physical Width 또는 Physical Height가 0이 아니면 분석 방향에 대응하는 물리 길이를 그래프에 적용한다.
- 물리 길이가 설정된 방향의 Profile 그래프 X축은 px 대신 mm 단위로 표시한다.
- 물리 길이가 설정된 방향의 FFT 그래프 X축은 cycles/px 대신 cycles/mm 단위로 표시한다.
- TOP PEAKS 테이블의 period도 px 대신 mm 단위로 표시한다.
- 분석 방향에 대응하는 Physical Width 또는 Physical Height가 0이면 기존 px와 cycles/px 단위를 유지한다.

### 2.10 Horizontal·Vertical·All 분석 보기

- ROI 탭의 DIRECTION 선택 항목을 `Horizontal | Vertical | All`로 구성한다.
- Horizontal을 선택하면 해당 ROI의 Horizontal Profile·FFT 그래프와 TOP PEAKS 테이블을 표시한다.
- Vertical을 선택하면 해당 ROI의 Vertical Profile·FFT 그래프와 TOP PEAKS 테이블을 표시한다.
- All을 선택하면 그래프 영역을 2열로 나눈다.
- All 그래프 영역의 왼쪽 열에는 Horizontal Profile·FFT 그래프를 표시한다.
- All 그래프 영역의 오른쪽 열에는 Vertical Profile·FFT 그래프를 표시한다.
- All에서도 각 열의 Profile 그래프와 FFT 그래프는 위아래로 배치한다.
- All을 선택하면 TOP PEAKS 영역에 테이블 두 개를 위아래로 표시한다.
- All TOP PEAKS 영역의 위쪽 테이블은 Horizontal 결과, 아래쪽 테이블은 Vertical 결과를 표시한다.
- 각 TOP PEAKS 테이블에 Horizontal 또는 Vertical 방향을 구분할 수 있는 제목을 표시한다.
- 각 방향의 피크 선택과 Profile 주기 오버레이는 서로 독립적으로 동작한다.

### 2.11 FFT 그래프의 기본 주파수 표시 범위

- FFT Intensity 그래프의 신호가 왼쪽에 지나치게 몰려 보이지 않도록 기본 X축 표시 범위를 제한한다.
- 표시 단위와 관계없이 Nyquist 주파수 대비 비율로 기본 X축 범위를 정한다.
- 기본 비율은 40%로 하며, px 단위에서는 `0~0.2 cycles/px`에 해당한다.
- 사용자가 Setting 탭에서 FFT 표시 범위 비율을 더 좁히거나 넓힐 수 있게 한다.
- 설정 이름은 `fft_display_range_percent`로 하고 선택 제품의 공통 설정으로 `setting.json`에 저장한다.
- `fft_display_range_percent` 기본값은 40이고, 1보다 크거나 같고 100보다 작거나 같은 값을 허용한다.
- mm 단위에서는 고정된 주파수 값을 사용하지 않고, 해당 ROI의 Nyquist 주파수에 설정 비율을 적용한다.
- mm 주파수 변환에는 전체 제품 길이가 아니라 실제 profile에 대응하는 ROI의 물리 길이와 sample 수를 사용한다.
- Horizontal은 ROI의 Physical Width 방향 길이, Vertical은 ROI의 Physical Height 방향 길이를 사용한다.
- X축 표시 범위를 제한해도 FFT 계산 데이터 자체는 전체 Nyquist 범위까지 유지한다.
- 사용자는 Plotly의 zoom과 pan으로 기본 표시 범위 밖의 FFT 데이터도 확인할 수 있다.

### 2.12 MIM 전용 트리 Explorer

- 좌측 Explorer를 GitHub 좌측 파일 탐색기와 같은 계층형 tree 형태로 표시한다.
- 폴더를 클릭해도 현재 경로를 해당 폴더로 이동하지 않는다.
- 접힌 폴더 앞에는 `>` 형태의 chevron을 표시한다.
- 접힌 폴더를 클릭하면 같은 Explorer 안에서 하위 항목을 펼치고 chevron을 `v` 형태로 바꾼다.
- 펼쳐진 폴더를 다시 클릭하면 하위 항목을 접는다.
- 폴더에는 folder icon, `.mim` 파일에는 file icon을 표시한다.
- 폴더 이름은 bold로 표시한다.
- 파일 이름은 bold를 사용하지 않고 normal weight로 표시한다.
- 폴더·파일 행의 상하 padding을 줄여 현재보다 compact하고 촘촘하게 표시한다.
- Explorer에는 `.mim` 파일만 표시하고 다른 확장자의 파일은 표시하지 않는다.
- 직접 또는 하위 폴더에 `.mim` 파일이 하나 이상 있는 폴더만 표시한다.
- `.mim` 파일이 전혀 없는 폴더와 그 하위 tree는 Explorer에서 숨긴다.
- 확장자는 대소문자를 구분하지 않고 `.mim`으로 판정한다.
- `.mim` 파일을 클릭하면 기존과 같이 해당 이미지를 로드한다.

### 2.13 프로그램 브랜딩과 상태바

- 현재 프로그램 대표 아이콘을 SSOT에 맞는 scientific 전문 분석 도구형 아이콘으로 교체한다.
- 대표 아이콘은 단순하고 현대적인 형태로 제작하고, 촌스럽거나 장식적인 표현을 사용하지 않는다.
- Windows 실행 파일, 작업 표시줄과 프로그램 창에서 같은 대표 아이콘을 사용한다.
- 작은 Windows 아이콘 크기에서도 형태와 FFT/ROI 분석 도구의 성격을 식별할 수 있어야 한다.
- Explorer의 folder/file icon도 대표 아이콘과 조화를 이루는 심플하고 고급스러운 line icon으로 적용한다.
- Explorer icon은 Dark·Gray·White 테마에서 모두 명확하게 보여야 한다.
- pywebview의 native title bar와 native window chrome을 제거한다.
- 별도의 프로그램 제목 영역을 만들지 않고 탭 영역을 GUI의 최상단으로 배치한다.
- 탭 영역의 빈 공간은 창을 이동할 수 있는 drag region으로 사용한다.
- 탭과 버튼은 drag region에서 제외해 기존 클릭 동작을 유지한다.
- 창 최소화, 최대화·복원, 닫기 아이콘을 탭 영역 오른쪽에 배치한다.
- 창이 최대화되면 최대화 아이콘을 복원 아이콘으로 변경한다.
- 탭 영역의 빈 공간을 double-click하면 최대화와 복원을 전환한다.
- GUI 전체 하단에 `markdown_browser`를 참고한 compact 상태바를 추가한다.
- 상태바 왼쪽에는 현재 선택해 로드한 `.mim` 파일의 전체 경로를 Windows 형식으로 표시한다.
- 파일 경로는 `D:\folder\subfolder\file.mim`과 같이 drive letter와 backslash를 포함한 절대 경로로 표시한다.
- 아직 파일을 선택하지 않은 상태에는 파일이 선택되지 않았음을 표시한다.
- 긴 파일 경로는 상태바 폭을 넘지 않게 생략 표시하고, tooltip으로 전체 경로를 확인할 수 있게 한다.
- 상태바 오른쪽에는 `FFT ROI Analyzer v0.2 (YY-MM-DD)` 형식으로 프로그램명, 버전과 날짜를 표시한다.
- 상태바의 날짜는 해당 배포본의 build date를 `YY-MM-DD` 형식으로 표시한다.
- 상태바는 선택 테마의 surface·border·text token을 사용하고 경로는 compact monospace 글꼴로 표시한다.

### 2.14 Setting 이미지 Zoom·Pan

- Setting 탭의 이미지 영역에서 확대, 축소와 이동을 지원한다.
- 이미지 위 grid line을 보이거나 감출 수 있는 Grid toggle을 제공한다.
- Grid toggle의 기본 상태는 감춤으로 한다.
- Grid line은 이미지 영역 안에만 표시하고 이미지 밖으로 그리지 않는다.
- Grid line은 이미지와 동일한 좌표 변환을 사용해 zoom·pan에 맞춰 함께 이동하고 확대·축소한다.
- Grid line은 ROI overlay보다 뒤에 표시해 ROI 경계, label과 resize handle을 가리지 않는다.
- Grid 표시 상태는 화면 표시만 바꾸며 원본 이미지, ROI 좌표와 분석 결과에는 영향을 주지 않는다.
- 마우스 휠을 사용하면 별도 modifier key 없이 포인터 위치를 중심으로 확대·축소한다.
- `Space + 왼쪽 마우스 drag`로 이미지를 이동한다.
- 마우스 가운데 버튼 drag도 이미지 이동에 사용한다.
- `Ctrl + 0`으로 이미지를 현재 표시 영역에 맞춘다.
- `Ctrl + 1`로 이미지를 100% 실제 pixel 크기로 표시한다.
- `+`와 `-` key로 화면 중심 기준 단계별 확대·축소를 수행한다.
- 확대 비율은 10%에서 800% 범위로 제한한다.
- 파일을 처음 열면 Fit to View 상태로 표시한다.
- 이미지가 표시 영역보다 작으면 중앙에 정렬한다.
- Pan으로 이미지 전체가 표시 영역 밖으로 사라지지 않게 이동 범위를 제한한다.
- Setting 탭을 벗어났다가 돌아와도 현재 zoom과 pan 위치를 유지한다.
- 이미지와 ROI overlay는 동일한 좌표 변환으로 함께 확대·이동한다.
- ROI의 정규화 좌표는 zoom·pan으로 변경하지 않는다.
- ROI 이름 label과 resize handle은 zoom 비율과 관계없이 화면상 고정 크기를 유지한다.
- `Space`를 누르지 않은 왼쪽 drag는 기존 ROI 생성·이동·크기 조절에 사용한다.
- Pan 가능 상태와 Pan 중 상태를 open-hand·closed-hand cursor로 구분한다.

## 3. 이전 버전에서 아쉬웠던 것

- 분석 Settings와 ROI가 세션 종료 후 유지되지 않았다.
- 같은 제품을 다시 분석할 때 사용자가 설정값을 다시 입력해야 했다.
- 제품별 분석 조건을 선택하고 관리하는 화면이 없었다.
- Overview 탭과 톱니바퀴 Settings 모달로 설정 기능이 나뉘어 있었다.
- TOP PEAKS 결과가 헤더가 있는 표 형태로 정리되지 않았다.
- Plotly 그래프에 GUI 기본 글꼴이 적용되지 않았다.
- 위아래 그래프의 y축 위치가 시각적으로 정렬되지 않았다.
- Plotly 기본 흰색 배경과 기본 grid line이 다크 GUI와 어울리지 않았다.
- 단일 다크 테마만 제공되어 화면 명도를 선택할 수 없었다.
- 프로그램 대표 아이콘과 Explorer 아이콘이 SSOT 수준의 전문성과 시각적 완성도를 충족하지 못했다.
- native title bar가 GUI 디자인 시스템과 분리되어 전체 화면의 완성도를 떨어뜨렸다.
- 프로그램명·버전·build date를 일관된 형식으로 확인할 수 있는 표시가 없었다.
- 현재 선택한 `.mim` 파일의 전체 Windows 경로를 지속적으로 보여주는 하단 상태바가 없었다.
- Setting 이미지에서 세부 영역을 확대하고 이동하며 ROI를 확인하기 어려웠다.

## 4. 하지 않을 것

- 제품별 설정을 여러 개의 설정 파일로 나누지 않는다.
- 설정 파일에 YAML 또는 TXT 형식을 사용하지 않는다.
- 분석 결과의 PPTX 보고서 저장 기능을 이번 버전에 포함하지 않는다.
- 분석 결과의 CSV 저장 기능을 이번 버전에 포함하지 않는다.
- clean Windows 환경의 배포 검증은 별도 요구가 확정될 때 다룬다.

## 5. 완료 조건

- 실행 파일과 같은 폴더에서 `setting.json`을 읽을 수 있다.
- 파일이 없으면 `Default` 제품과 현재 기본값을 포함한 `setting.json`이 자동 생성된다.
- 최초 실행 시 `Default`가 선택되고, 해당 설정과 ROI가 Setting 탭에 표시된다.
- 하나의 파일에서 여러 제품을 선택하고 제품별 설정과 ROI를 수정·저장·복원할 수 있다.
- 고정 탭 이름이 `Setting`이고, 기존 `Full Panel` 영역에서 active product를 선택할 수 있다.
- 기존 톱니바퀴 Settings 아이콘과 Settings 모달이 제거된다.
- TOP-K 변경에 따라 TOP PEAKS 테이블 행이 증가하거나 감소한다.
- TOP PEAKS 테이블에 헤더가 표시되고 기존 피크 선택 기능이 유지된다.
- FFT Intensity 그래프의 TOP-K peak가 서로 다른 색상과 `[순번] X축값` badge로 표시된다.
- FFT marker·badge·TOP PEAKS 행·선택 주기 오버레이가 peak별 동일 색상을 사용한다.
- TOP PEAKS 행과 FFT peak 중 어느 쪽을 선택해도 같은 peak가 선택되고 Profile에 동일 색상의 주기선이 표시된다.
- 선택한 peak의 Profile 주기선이 0 기준의 고정 위치가 아니라 반복 peak 또는 valley와의 전체 위치 오차가 최소가 되는 위치에 표시된다.
- 정합 후에도 인접한 Profile 주기선 사이의 간격이 선택한 FFT peak의 보정된 주기와 동일하다.
- 정합도가 낮은 결과는 높은 결과와 구분할 수 있다.
- 여러 peak의 선택·해제와 색상별 Profile 주기선이 함께 동작하며 All의 두 방향은 독립적이다.
- ROI별 AVG BAND와 REF BAND가 파일에 저장되고 ROI 탭에서 복원된다.
- Profile·FFT 그래프 내부 글꼴이 GUI 기본 글꼴과 일치한다.
- 위아래 그래프의 y축 기준선이 같은 가로 위치에 정렬된다.
- 그래프가 선택 테마에 맞는 배경, grid line, 신호선, marker와 tooltip 색상을 사용한다.
- Profile·FFT 그래프가 내부 십자축 없이 네 변이 보이는 직사각형 frame으로 표시된다.
- 탭 영역 오른쪽의 창 제어 버튼 바로 왼쪽 아이콘으로 Dark·Gray·White 테마를 전환할 수 있다.
- 앱을 처음 실행하면 Gray 테마가 적용된다.
- GUI, 그래프와 TOP PEAKS 테이블에 선택 테마가 함께 적용된다.
- Physical Width 또는 Physical Height가 0이 아닌 방향은 Profile·FFT 그래프와 TOP PEAKS period에 mm 기반 단위를 사용한다.
- 분석 방향에 대응하는 물리 길이가 0이면 px 기반 단위를 유지한다.
- ROI 탭의 DIRECTION에서 Horizontal, Vertical과 All을 선택할 수 있다.
- All에서는 그래프 영역이 Horizontal 좌측 열과 Vertical 우측 열로 나뉘고, 각 열에 Profile·FFT 그래프가 표시된다.
- All에서는 Horizontal·Vertical TOP PEAKS 테이블 두 개가 위아래로 표시되고 각각 독립적으로 피크를 선택할 수 있다.
- FFT 그래프는 단위와 관계없이 `fft_display_range_percent`에 지정된 Nyquist 대비 비율을 기본 표시 범위로 사용한다.
- `fft_display_range_percent`의 초기값은 40%이며 Setting 탭에서 1~100% 범위로 수정·저장할 수 있다.
- 기본 표시 범위 밖의 FFT 데이터가 제거되지 않고 zoom 또는 pan으로 확인 가능하다.
- Explorer에서 폴더는 bold, 파일은 normal weight이고 각 항목에 folder/file icon이 표시된다.
- Explorer 행의 상하 간격이 줄어 compact한 tree 목록으로 표시된다.
- 폴더 클릭 시 경로 이동 없이 `>`와 `v` chevron으로 하위 tree를 펼치거나 접을 수 있다.
- Explorer에는 `.mim` 파일과 `.mim` 파일을 포함하는 폴더 계층만 표시된다.
- Windows 실행 파일·작업 표시줄·프로그램 창에 새 대표 아이콘이 일관되게 적용된다.
- Explorer의 folder/file icon이 세 가지 테마에서 심플하고 선명하게 표시된다.
- native title bar 없이 탭 영역이 GUI 최상단에 표시되고 빈 영역으로 창을 이동할 수 있다.
- 탭 영역 오른쪽의 아이콘으로 창 최소화, 최대화·복원과 닫기를 수행할 수 있다.
- GUI 하단 상태바 왼쪽에 선택한 `.mim` 파일의 Windows 절대 경로가 표시된다.
- GUI 하단 상태바 오른쪽에 `FFT ROI Analyzer v0.2 (YY-MM-DD)`가 표시된다.
- 긴 경로는 상태바에서 생략되지만 tooltip으로 전체 경로를 확인할 수 있다.
- Setting 이미지에서 Wheel zoom, Space+왼쪽 drag와 가운데 버튼 drag pan이 동작한다.
- `Ctrl+0`, `Ctrl+1`, `+`, `-` 단축키로 Fit·100%·단계별 zoom을 실행할 수 있다.
- Setting 이미지의 Grid toggle로 grid line을 보이거나 감출 수 있고 초기 상태는 감춤이다.
- zoom·pan 중에도 이미지와 ROI overlay가 일치하고 ROI 좌표와 handle 화면 크기가 유지된다.
- 앱을 다시 실행하면 마지막 active product, 제품 설정, ROI와 테마가 복원된다.
