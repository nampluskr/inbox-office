> 버전: v0.2 · 작성일: 2026-09-02

# SPEC

이 문서는 [[BRIEF]] 2절의 사용자 요구와 [[DECISIONS]]의 설계 결정을 검증 가능한 요구사항으로 정의한다.

## 1. 기능 요구사항

### FR-1. MIM 이미지 로드와 표시

- 내용: 사용자는 Windows 절대 경로의 `.mim` 2차원 grayscale 이미지를 열 수 있어야 한다. 화면 표시는 8-bit로 변환할 수 있지만 Profile과 FFT 계산에는 원본 수치 배열을 사용해야 한다.
- 판정 방법:
  - 대표 `.mim` fixture를 열었을 때 원본 shape와 dtype이 기대값과 일치하고 이미지가 Setting 탭에 표시되는지 확인한다.
  - 표시용 변환 전후에도 동일 ROI의 분석 입력 배열이 원본 `.mim` 값과 일치하는지 자동 테스트로 확인한다.
  - 2차원 grayscale이 아닌 입력이 안정된 오류 응답으로 반환되고 앱이 종료되지 않는지 확인한다.

### FR-2. 이미지 회전과 ROI 관리

- 내용: 회전값 `0`, `90`, `-90`, `180`을 지원하고 모든 ROI와 분석은 회전된 이미지 기준으로 동작해야 한다. 사용자는 정규화 좌표의 사각형 ROI를 추가·삭제·이동·크기 조절·이름 변경할 수 있으며 ROI와 분석 탭은 1:1로 유지되어야 한다.
- 판정 방법:
  - 각 회전값에서 표시 크기, ROI crop과 Profile 방향이 기대 배열과 일치하는지 fixture로 확인한다.
  - 유효하지 않은 회전값과 `xmin >= xmax`, `ymin >= ymax`, 범위 밖 ROI가 오류로 처리되는지 확인한다.
  - ROI 추가·삭제·이름 변경 때 같은 ID의 탭이 생성·제거·갱신되고 다른 ROI 탭은 유지되는지 UI 테스트로 확인한다.

### FR-3. Profile 계산

- 내용: ROI에서 Horizontal 또는 Vertical raw Profile을 계산하고, AVG BAND와 REF BAND moving average를 적용해 `100 × (smoothed - reference) / reference`의 정규화 dL/L(%) Profile을 계산해야 한다. 경계에서는 0 padding 없이 실제 포함 sample 수로 평균해야 한다.
- 판정 방법:
  - 작은 고정 배열에 대해 Horizontal·Vertical raw Profile과 정규화 Profile이 수작업 기대값과 허용 오차 `1e-10` 이내인지 자동 테스트로 확인한다.
  - window가 Profile보다 크거나 경계를 넘는 fixture에서 잘린 window의 실제 sample 평균과 일치하는지 확인한다.
  - 결과에 NaN 또는 Infinity가 포함되지 않는지 확인한다.

### FR-4. FFT, TOP-K peak와 peak-to-valley 계산

- 내용: 정규화 dL/L(%) Profile에 FFT를 수행하고 local maximum만 peak 후보로 사용해야 한다. DC와 양 끝 bin을 제외하고 `min_peak_separation_bins`를 적용한 뒤 amplitude 순으로 최대 TOP-K를 반환해야 한다. 정규화 Profile의 peak-to-valley 값도 제공해야 한다.
- 판정 방법:
  - 단일·복합 주파수 합성 Profile에서 예상 FFT bin과 period가 허용 오차 내에 검출되는지 확인한다.
  - DC, 양 끝 bin과 local maximum이 아닌 bin이 반환되지 않는지 확인한다.
  - 후보 수가 TOP-K보다 적으면 실제 후보 수만 반환하고, 후보 간 bin 간격이 설정값 이상인지 확인한다.
  - peak-to-valley가 `max(normalized) - min(normalized)`와 일치하는지 확인한다.

### FR-5. 분석 상태 유지

- 내용: ROI별 분석 결과와 Direction 상태는 독립적으로 유지되어야 한다. 탭을 전환해도 마지막 결과와 그래프 zoom 상태를 유지하고, 이미지 또는 해당 ROI 분석 설정이 바뀌면 영향을 받는 결과를 갱신해야 한다.
- 판정 방법:
  - 두 ROI에 서로 다른 Direction과 zoom을 적용한 뒤 탭을 왕복해 각각 복원되는지 확인한다.
  - 파일·회전·ROI 좌표·분석 설정을 각각 변경했을 때 관련 결과가 새 입력 기준으로 갱신되는지 확인한다.

### FR-6. `setting.json` 탐색과 초기 생성

- 내용: 개발 실행에서는 `app.py`, 배포 실행에서는 실제 GUI 실행 파일과 같은 폴더의 `setting.json`을 읽어야 한다. 파일이 없으면 같은 위치에 v0.2 기본값과 `Default` 제품을 포함한 UTF-8 JSON 파일을 생성해야 한다.
- 판정 방법:
  - 임시 개발 실행 경로와 PyInstaller 실행 경로에서 각각 설정 파일 탐색 위치가 예상 절대 경로인지 확인한다.
  - 파일이 없는 쓰기 가능한 임시 폴더에서 최초 실행 후 `setting.json`이 생성되고 표준 JSON parser로 읽히는지 확인한다.
  - 생성된 파일에 전역 GUI 설정, active product `Default`와 `Default` 제품이 존재하는지 확인한다.

### FR-7. 설정 파일의 범위와 기본값

- 내용: 전역 GUI 설정에는 `theme`과 마지막 active product를 포함해야 한다. 제품 공통 설정에는 Physical Width·Height, TOP-K, `min_peak_separation_bins`, `fft_display_range_percent`와 ROI 목록을 포함해야 한다. ROI에는 ID·이름·정규화 좌표·AVG BAND·REF BAND를 포함해야 한다. 초기값은 Gray, active product `Default`, 물리 크기 0, TOP-K 5, 최소 peak 간격 2 bin, FFT 표시 범위 40%, AVG BAND 3 px, REF BAND 201 px와 중앙 90% 기본 ROI로 한다.
- 판정 방법:
  - 기본 생성 파일의 각 필드와 값이 명시된 기본값과 일치하는지 schema 테스트로 확인한다.
  - 제품 두 개와 서로 다른 ROI 설정을 저장한 fixture를 읽어 값의 소유 범위가 바뀌지 않는지 확인한다.
  - `fft_display_range_percent`가 1~100, 물리 크기가 0 이상, band가 1 이상 정수, TOP-K가 0 이상 정수, 최소 peak 간격이 1 이상 정수인지 검증한다.

### FR-8. Setting 탭과 active product 편집

- 내용: 고정 첫 탭의 이름은 Setting이어야 하고 기존 Full Panel 영역에는 active product 선택기를 표시해야 한다. 선택 제품의 설정과 ROI를 확인·수정하고 명시적으로 저장할 수 있어야 하며 기존 톱니바퀴 Settings 버튼과 modal은 없어야 한다.
- 판정 방법:
  - 시작 화면에서 첫 탭 이름, active product 선택기와 저장 동작이 보이고 톱니바퀴 및 Settings modal이 존재하지 않는지 확인한다.
  - 저장 전 편집값이 파일에 반영되지 않고 저장 후 해당 제품 JSON 값에 반영되는지 확인한다.
  - 최초 설정 파일에서는 `Default`가 선택되고 해당 설정과 ROI가 화면에 표시되는지 확인한다.

### FR-9. 제품 전환과 설정 복원

- 내용: 하나의 설정 파일에 있는 여러 제품을 선택할 수 있어야 한다. 제품을 전환하면 해당 제품의 분석 설정과 ROI를 적용하고, 앱 재실행 시 마지막 active product, 제품 설정, ROI와 테마를 복원해야 한다.
- 판정 방법:
  - 서로 다른 물리 크기, TOP-K와 ROI를 가진 두 제품을 번갈아 선택해 화면과 분석값이 각각 일치하는지 확인한다.
  - 제품 B와 Dark 테마를 저장하고 재실행했을 때 제품 B, 해당 ROI와 Dark 테마가 복원되는지 확인한다.
  - 제품 전환으로 다른 제품의 저장값이 변경되지 않는지 JSON 비교로 확인한다.

### FR-10. ROI별 분석 설정 적용

- 내용: ROI 탭은 선택 제품의 해당 ROI에 저장된 AVG BAND와 REF BAND를 표시·수정·저장해야 하며, TOP-K와 최소 peak 간격은 제품 공통 설정을 적용해야 한다.
- 판정 방법:
  - 같은 제품의 두 ROI에 서로 다른 band 값을 저장한 뒤 각 탭에서 올바르게 표시·계산되는지 확인한다.
  - 제품의 TOP-K와 최소 peak 간격을 변경했을 때 모든 ROI의 다음 분석 결과에 공통으로 적용되는지 확인한다.

### FR-11. TOP PEAKS 테이블

- 내용: 각 분석 방향의 TOP PEAKS 영역은 헤더가 있는 테이블이어야 한다. 행 수는 검출된 peak 수를 넘지 않으며 제품 TOP-K의 증가·감소에 따라 최대 행 수가 갱신되어야 한다. All에서는 Horizontal 테이블을 위, Vertical 테이블을 아래에 표시하고 방향 제목을 붙여야 한다.
- 판정 방법:
  - TOP-K를 3, 7, 2로 바꿀 때 충분한 peak fixture에서 행 수가 각각 3, 7, 2인지 확인한다.
  - peak 후보가 TOP-K보다 적을 때 빈 가짜 행 없이 후보 수만 표시되는지 확인한다.
  - All에서 방향 제목이 있는 두 테이블의 순서가 Horizontal, Vertical인지 확인한다.

### FR-12. FFT peak marker와 badge

- 내용: TOP-K peak마다 테마에서 구별되는 고유 색상의 filled circle marker와 `[순번] X축값` 형식의 작은 직사각형 badge를 표시해야 한다. 순번은 테이블 행과 같고 X축값은 현재 단위의 cycles/px 또는 cycles/mm여야 한다.
- 판정 방법:
  - K개 marker·badge·행 순번이 1:1로 대응하고 각 badge 값이 해당 peak frequency와 표시 정밀도 내에서 일치하는지 확인한다.
  - 동일 방향의 K개 peak 색상이 서로 구분되며 Dark·Gray·White에서 marker와 badge가 배경에서 식별되는지 확인한다.
  - 색상 표시를 제거한 grayscale 캡처에서도 순번으로 peak 대응을 식별할 수 있는지 확인한다.

### FR-13. Peak 선택과 Profile 오버레이 동기화

- 내용: TOP PEAKS 행 또는 FFT marker·badge를 선택하면 같은 peak가 선택되고 해당 고유 색상의 주기선을 Profile에 표시해야 한다. 여러 peak를 동시에 선택할 수 있고 다시 선택하면 해제해야 한다. All의 Horizontal·Vertical 선택 상태는 독립적이어야 한다.
- 판정 방법:
  - 테이블 행과 FFT marker를 각각 선택해 반대쪽 선택 상태, marker, badge와 Profile 선이 같은 순번·색상으로 갱신되는지 확인한다.
  - 세 peak를 선택한 뒤 하나를 해제했을 때 나머지 두 선택과 선만 유지되는지 확인한다.
  - All에서 Horizontal 선택·해제가 Vertical 선택과 선을 바꾸지 않는지 확인한다.

### FR-14. Profile 주기선 위상 정합

- 내용: 선택 peak의 frequency를 bin 해상도보다 정밀하게 보정하고, 보정된 period 간격은 유지한 채 반복 peak 또는 valley와 전체적으로 가장 잘 맞는 위상 오프셋을 적용해야 한다. 결과에는 보정 frequency·period·위상 오프셋·선택 극성과 수치형 정합 점수를 포함해야 한다.
- 판정 방법:
  - 알려진 비정수-bin frequency와 위상을 가진 합성 Profile에서 보정 frequency가 원래 FFT bin 중심보다 참값에 가깝고, 첫 overlay가 이론적 peak 또는 valley에서 1 sample 이내인지 확인한다.
  - 모든 인접 overlay 간격이 보정 period와 수치 허용 오차 `1e-6` 이내인지 확인한다.
  - 부호가 반대인 두 fixture에서 peak와 valley 극성이 각각 선택되는지 확인한다.
  - 주기 신호 fixture의 정합 점수가 noise fixture보다 높고 점수가 UI에서 확인 가능한지 검증한다.

### FR-15. Horizontal·Vertical·All 표시

- 내용: Direction은 Horizontal·Vertical·All을 제공해야 한다. All에서는 Horizontal Profile·FFT를 왼쪽 열, Vertical Profile·FFT를 오른쪽 열에 각각 위아래로 배치해야 한다.
- 판정 방법:
  - 각 Direction에서 표시되는 그래프와 테이블이 선택 방향과 일치하는지 확인한다.
  - All 화면에서 두 열의 방향과 각 열 내부의 Profile 위·FFT 아래 순서를 DOM과 화면 캡처로 확인한다.

### FR-16. px와 mm 단위 전환

- 내용: 분석 방향에 해당하는 Physical Width 또는 Height가 0보다 크면 해당 ROI의 실제 물리 span과 sample 수를 기준으로 Profile X축과 period를 mm, FFT X축을 cycles/mm로 표시해야 한다. 값이 0이면 px와 cycles/px를 사용해야 한다.
- 판정 방법:
  - 전체 폭 100 mm에서 가로 50%인 ROI fixture의 Horizontal Profile span과 FFT 단위가 ROI의 실제 50 mm sampling에 맞는지 확인한다.
  - Width만 양수이고 Height는 0인 제품에서 Horizontal은 mm, Vertical은 px 계열 단위를 사용하는지 확인한다.
  - 같은 overlay를 px와 mm로 표시했을 때 sample 좌표로 역변환한 위치가 일치하는지 확인한다.

### FR-17. FFT 기본 표시 범위

- 내용: FFT 기본 X축은 해당 ROI·방향 Nyquist 주파수의 `fft_display_range_percent`까지만 표시해야 한다. 기본값은 40%이고 Setting에서 1~100%로 수정·저장할 수 있어야 한다. 표시 범위 밖 데이터도 유지하여 zoom·pan으로 확인할 수 있어야 한다.
- 판정 방법:
  - px 단위의 기본 sampling에서 초기 범위가 `0~0.2 cycles/px`인지 확인한다.
  - 서로 다른 px/mm sampling fixture에서 X축 상한이 각각의 Nyquist × 설정 비율과 일치하는지 확인한다.
  - 20%, 100%로 변경·저장·재실행했을 때 범위가 복원되는지 확인한다.
  - 초기 범위 밖 FFT point가 trace 데이터에 남아 있고 zoom·pan으로 표시되는지 확인한다.

### FR-18. Dark·Gray·White 테마

- 내용: GUI는 Dark·Gray·White 테마를 제공하고 최초 기본값은 Gray여야 한다. 탭 오른쪽 창 제어 버튼 바로 왼쪽의 테마 버튼으로 White → Gray → Dark → White 순서로 전환하며 GUI·그래프·테이블·아이콘에 동시에 적용해야 한다.
- 판정 방법:
  - 설정 파일이 없는 최초 실행에서 Gray가 적용되는지 확인한다.
  - 각 시작 테마에서 버튼 클릭 후 지정된 다음 테마로 이동하는지 확인한다.
  - 각 테마에서 Explorer, 탭, field, button, graph, TOP PEAKS와 icon의 computed token이 해당 테마값인지 확인한다.
  - 선택 테마를 저장하고 재실행했을 때 복원되는지 확인한다.

### FR-19. Scientific 그래프 표현과 축 정렬

- 내용: Profile·FFT 그래프는 GUI 기본 글꼴, 테마 배경과 절제된 grid를 사용해야 한다. plot 내부 십자축 없이 네 변의 직사각형 frame을 표시하고 X축은 하단, Y축은 좌측에 둬야 한다. 같은 방향의 Profile과 FFT plot 시작 X좌표를 정렬해야 한다.
- 판정 방법:
  - 세 테마에서 흰색 기본 Plotly 배경이 노출되지 않고 축·눈금·tooltip·trace가 theme token을 사용하는지 확인한다.
  - 화면 캡처에서 네 frame 변이 존재하고 내부를 가로지르는 0축이 표시되지 않는지 확인한다.
  - Profile과 FFT의 좌측 plot 경계 차이가 1 CSS px 이하인지 기본 크기와 resize 후 각각 측정한다.
  - 축 제목·눈금·tooltip의 computed font family가 GUI 기본 글꼴과 일치하는지 확인한다.

### FR-20. MIM 전용 Explorer 내용 필터링

- 내용: Explorer에는 확장자 대소문자와 관계없이 `.mim` 파일과 이를 직접 또는 재귀적으로 포함하는 폴더 계층만 표시해야 한다. 다른 파일과 MIM이 없는 폴더는 표시하지 않아야 한다.
- 판정 방법:
  - `.mim`, `.MIM`, `.txt`와 빈 폴더가 섞인 fixture tree에서 기대되는 파일과 조상 폴더만 반환·표시되는지 확인한다.
  - 표시된 각 폴더 아래에 적어도 하나의 MIM 파일이 존재하는지 재귀 검증한다.
  - MIM 파일 클릭 시 해당 절대 경로의 이미지가 로드되는지 확인한다.

### FR-21. Explorer tree 상호작용과 표현

- 내용: 폴더 클릭은 경로 이동이 아니라 같은 tree 안의 펼침·접힘이어야 하며 상태를 `>`와 `v` chevron으로 표시해야 한다. 폴더는 bold, 파일은 normal weight로 표시하고 각각 folder/file icon을 사용하며 행은 compact spacing을 사용해야 한다.
- 판정 방법:
  - 폴더를 두 번 클릭해 하위 항목과 chevron이 펼침·접힘에 맞게 바뀌고 root 문맥이 유지되는지 확인한다.
  - computed font weight가 폴더와 파일에서 각각 bold와 normal인지 확인한다.
  - 각 행에 올바른 icon이 있고 기존 버전보다 상하 padding이 감소했는지 스타일 값으로 확인한다.

### FR-22. Frameless window 제어

- 내용: native title bar를 표시하지 않고 탭 영역을 창 최상단에 둬야 한다. 빈 탭 영역으로 창을 이동하고 double-click으로 최대화·복원해야 한다. 탭과 버튼은 drag 대상에서 제외하며 오른쪽 버튼으로 최소화, 최대화·복원과 닫기를 수행해야 한다.
- 판정 방법:
  - 실행 창에 native title bar가 없고 별도 제목 행 없이 탭 영역이 최상단인지 확인한다.
  - 빈 영역 drag, double-click, 세 창 제어 버튼이 Windows 창 상태를 예상대로 바꾸는지 수동 UI 검증한다.
  - 최대화 상태에서 icon이 복원 형태로 바뀌고 탭·테마 버튼 클릭이 창 drag로 처리되지 않는지 확인한다.

### FR-23. 하단 상태바

- 내용: GUI 하단 전체 폭에 theme token을 사용하는 compact 상태바를 표시해야 한다. 왼쪽에는 compact monospace 글꼴로 현재 MIM의 Windows 절대 경로 또는 미선택 상태를, 오른쪽에는 `FFT ROI Analyzer v0.2 (YY-MM-DD)`를 표시해야 한다. 긴 경로는 생략하고 tooltip으로 전체 경로를 제공해야 한다.
- 판정 방법:
  - 파일 미선택·선택 상태에서 왼쪽 문구가 각각 요구 형식인지 확인한다.
  - 200자 이상의 경로 fixture가 한 줄로 생략되고 tooltip에는 원문 전체가 있는지 확인한다.
  - 오른쪽 날짜가 build date와 `YY-MM-DD` 형식으로 일치하는지 확인한다.
  - 세 테마에서 surface·border·text token과 경로의 monospace font가 적용되는지 확인한다.

### FR-24. Setting 이미지 zoom과 pan

- 내용: Wheel pointer 중심 zoom, Space+왼쪽 drag pan, 가운데 버튼 drag pan을 지원해야 한다. `Ctrl+0`은 Fit, `Ctrl+1`은 실제 pixel 크기 100%, `+`·`-`는 화면 중심 기준 단계 zoom으로 동작해야 한다. 범위는 10~800%이며 파일 최초 로드는 Fit 상태여야 한다. Space를 누르지 않은 왼쪽 drag는 ROI 편집에 사용하고 pan 가능·진행 상태는 open-hand·closed-hand cursor로 구분해야 한다.
- 판정 방법:
  - 각 입력 방식으로 zoom·pan 값이 기대 방향으로 변하고 Wheel 전후 pointer 아래 image 좌표가 유지되는지 확인한다.
  - 단축키 결과와 10%·800% clamp를 확인한다.
  - 작은 이미지는 중앙 정렬되고 pan으로 이미지 전체가 viewport 밖으로 사라지지 않는지 확인한다.
  - 탭을 왕복해 zoom·pan 상태가 유지되고 이미지와 ROI 좌표가 일치하는지 확인한다.
  - ROI label과 handle의 화면 px 크기가 10%, 100%, 800%에서 동일한지 측정한다.
  - 일반 왼쪽 drag가 ROI 생성·이동·크기 조절을 유지하고 Space 또는 가운데 버튼 pan 전후 cursor가 지정 상태로 바뀌는지 확인한다.
  - zoom·pan 전후 ROI의 저장된 정규화 좌표가 변경되지 않는지 확인한다.

### FR-25. 이미지 grid 표시

- 내용: Setting 이미지에는 기본 감춤인 Grid toggle을 제공해야 한다. grid는 이미지와 함께 zoom·pan하고 이미지 경계 안에서 ROI보다 뒤에 표시되어야 하며 분석 입력과 결과를 바꾸지 않아야 한다.
- 판정 방법:
  - 최초 상태에서 grid가 숨겨지고 toggle 후 표시·재감춤되는지 확인한다.
  - zoom·pan 전후 grid와 image 좌표가 함께 변하고 선이 image 경계 밖에 표시되지 않는지 확인한다.
  - ROI 경계·label·handle이 grid보다 위에 그려지는지 확인한다.
  - grid toggle 전후 Profile·FFT·peak 결과가 byte-for-byte 동일한지 확인한다.

### FR-26. 프로그램과 Explorer 아이콘

- 내용: FFT·ROI 분석 도구의 성격을 나타내는 새 대표 아이콘을 실행 파일, 창과 작업 표시줄에 동일하게 적용해야 한다. Explorer folder/file icon은 같은 scientific line-icon 계열로 구성하고 세 테마에서 식별되어야 한다.
- 판정 방법:
  - PyInstaller 산출물의 executable icon과 실행 중 창·작업 표시줄 icon이 승인된 동일 원본을 사용하는지 확인한다.
  - Windows의 16, 24, 32, 48, 256 px 크기에서 대표 형태가 식별되는지 시각 검수한다.
  - 세 테마에서 folder/file icon이 배경과 구분되고 서로 혼동되지 않는지 확인한다.

## 2. 비기능 요구사항

### NFR-1. Scientific 전문 분석 도구 수준의 시각 품질

- 내용: [[BRIEF]]의 핵심 원칙을 GUI 전체의 최우선 품질 기준으로 적용해야 한다. 기본 browser control이나 Plotly 기본 스타일이 그대로 노출되지 않아야 하며 타이포그래피, spacing, grid, 색상과 icon이 하나의 체계로 보여야 한다.
- 판정 방법:
  - Dark·Gray·White 및 Horizontal·Vertical·All 화면 캡처를 SSOT 체크리스트로 검수하고 사용자 승인을 받는다.
  - 기본 흰색 Plotly surface, 기본 OS/browser button, 서로 다른 font family와 정의되지 않은 임의 색상이 남아 있지 않은지 DOM·CSS 검사로 확인한다.

### NFR-2. 테마 대비와 비색상 식별

- 내용: 세 테마에서 일반 텍스트는 배경 대비 4.5:1 이상, 큰 텍스트와 icon·graph 주요 선은 3:1 이상을 목표로 해야 한다. Peak는 색상만으로 식별하지 않아야 한다.
- 판정 방법:
  - 사용된 foreground/background token 조합을 자동 contrast 검사해 기준 충족 여부를 기록한다.
  - grayscale 화면에서도 peak 순번, 방향 label과 선택 상태를 판별할 수 있는지 확인한다.

### NFR-3. v0.1 분석 회귀 방지

- 내용: v0.2 UI·설정 변경이 기존 MIM 로드, 회전, ROI, Profile, FFT, peak와 peak-to-valley 계산 결과를 의도치 않게 변경하지 않아야 한다. D-12의 frequency·phase 보정은 기존 raw FFT 배열을 변경하지 않는 후처리여야 한다.
- 판정 방법:
  - 기존 v0.1 자동 테스트 전체와 v0.2 테스트가 모두 통과하는지 확인한다.
  - 고정 fixture의 raw Profile, normalized Profile, FFT frequency·amplitude와 peak-to-valley를 v0.1 baseline과 비교해 기존 허용 오차를 만족하는지 확인한다.

### NFR-4. Resize와 상태 일관성

- 내용: 앱이 선언한 최소 창 크기부터 최대화 상태까지 주요 control, graph, table과 상태바가 겹치거나 접근 불가능해지지 않아야 한다. Resize 후에도 축 정렬, 선택 상태와 image transform이 유지되어야 한다.
- 판정 방법:
  - 최소 크기, 기본 크기와 최대화 상태에서 세 테마·All 화면을 캡처해 overlap과 잘림을 확인한다.
  - 각 resize 전후 선택 peak, graph zoom, image zoom·pan과 plot 좌측 경계를 비교한다.

### NFR-5. 오류 격리와 데이터 유효성

- 내용: 파일 접근, 잘못된 JSON·설정·ROI와 분석 실패가 앱 프로세스의 비정상 종료로 이어지지 않아야 한다. Python API 결과는 JSON 직렬화 가능하고 NaN·Infinity를 포함하지 않아야 한다.
- 판정 방법:
  - 읽기 전용 설정 위치, 손상 JSON, 범위 밖 설정, 없는 MIM 경로와 잘못된 ROI를 각각 입력해 사용자용 오류가 표시되고 앱이 계속 동작하는지 확인한다.
  - 모든 API fixture 결과를 표준 JSON serializer로 직렬화하고 NaN·Infinity가 없는지 확인한다.

### NFR-6. 로컬 배포 산출물

- 내용: PyInstaller로 Windows 실행 파일을 빌드할 수 있어야 하며 web asset, Python dependency와 대표 아이콘을 포함해야 한다. 실행 파일은 자신의 실제 위치를 기준으로 `setting.json`을 찾아야 한다.
- 판정 방법:
  - 지정 WinPython 환경에서 빌드 명령이 성공하고 산출 실행 파일이 생성되는지 확인한다.
  - 산출물을 경로가 다른 쓰기 가능한 두 폴더에 복사해 각각 자신의 폴더에 설정 파일을 생성하고 앱 화면이 열리는지 확인한다.

## 3. 제약사항

- 대상 운영체제는 Windows이며 desktop shell은 pywebview와 WebView2를 사용한다.
- 개발·테스트 Python은 `C:\winpython\WPy64-31180_main\python-3.11.8.amd64\python.exe` 3.11.8을 사용한다.
- 수치 계산은 Python의 NumPy와 SciPy가 담당하고, `.mim` 로드는 tifffile, 표시 이미지 변환은 Pillow를 사용한다.
- UI는 HTML·CSS·JavaScript, graph는 Plotly.js를 사용한다. Electron, PyQt와 Matplotlib을 runtime dependency로 추가하지 않는다.
- Python이 Profile, FFT, peak, 단위와 위상 정합 결과를 계산하고 JavaScript는 반환 결과의 표시와 상호작용을 담당한다. JavaScript에서 분석 결과를 별도로 재계산하지 않는다.
- 수치 계산 기준은 `legacy/matlab/`을 1순위, `legacy/python/fft.py`를 2순위 참고 자료로 사용하며 legacy 코드를 runtime dependency로 사용하지 않는다.
- 설정 파일은 실행 파일과 같은 폴더에 있어야 하므로 배포 위치는 사용자에게 쓰기 권한이 있는 폴더여야 한다.
- 배포는 PyInstaller를 사용하고 프로그램 대표 icon을 빌드 산출물에 포함한다.
- Python API는 성공과 오류를 구분하는 안정된 JSON 직렬화 가능 응답만 UI에 반환해야 한다.

## 4. 미구현 대상

- PPTX 분석 보고서 생성과 저장은 v0.2에서 구현하지 않는다.
- CSV 분석 결과 저장은 v0.2에서 구현하지 않는다.
- YAML·TXT 설정 파일과 제품별 개별 설정 파일은 지원하지 않는다.
- `.mim` 이외 형식의 분석 데이터 탐색과 로드는 지원하지 않는다.
- Profile 주기선을 각 local peak에 개별적으로 snap해 선 간격을 바꾸는 기능은 구현하지 않는다.
- FFT 복소 위상만을 사용한 단독 정합 방식과 sine curve 재구성은 구현하지 않는다.
- 이미지 grid의 사용자 정의 간격·색상·선 종류 편집은 구현하지 않는다.
- Electron·PyQt 등 다른 GUI framework로의 전환은 수행하지 않는다.
- Python이 설치되지 않은 clean Windows 환경의 설치 프로그램 및 배포 검증은 별도 요구가 확정될 때 다룬다.
