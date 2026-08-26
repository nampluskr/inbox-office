# FFT ROI Analysis GUI Electron 리팩터링 명세

## 문서 상태

- 상태: Draft
- 구현 상태: 미착수
- 상위 개요: [BRIEF.md](BRIEF.md)

## 1. 문서 목적과 적용 범위

이 문서는 PyQt 기반 GUI를 Electron 기반 GUI로 대체하고 Python 분석 계층을 독립 worker로 재구성하기 위한 기술 기준을 정의한다.

이 문서는 승인 후 다음 영역의 차기 구현 canonical 기준이 된다.

- Electron main, preload 및 React Renderer 구조
- Electron과 Python 분석 엔진 사이의 통신
- 이미지 및 ROI 표시
- 대화형 profile과 FFT 그래프
- Plotly.js 고정 크기 PNG와 python-pptx 슬라이드 보고서
- Python 엔진 포함 Windows 패키징
- 비동기 처리, 오류, 보안 및 검증 기준

[../spec/gui-spec.md](../spec/gui-spec.md)의 PyQt 화면 구조, Qt class, `gui.ui` 및 matplotlib Canvas 기준은 차기 구현에 적용하지 않는다. 분석 함수의 수학적 의미, 정규화 좌표, 단위와 설정 필드는 별도 변경이 승인되기 전까지 [../spec/fft-spec.md](../spec/fft-spec.md)를 따른다.

## 2. 확정 기술 스택

| 계층 | 기술 |
| --- | --- |
| Desktop runtime | Electron |
| Main 및 preload | TypeScript |
| Renderer | React + TypeScript + CSS |
| 개발·번들 | electron-vite |
| 화면 그래프 | Plotly.js |
| 보고서 그래프 | Plotly.js `toImage()` PNG export |
| ROI overlay | SVG |
| 분석 엔진 | Python |
| 이미지 읽기 | tifffile |
| 표시용 이미지 인코딩 | Pillow |
| 수치 계산 | NumPy |
| PPTX 생성 | python-pptx |
| Python 패키징 | PyInstaller `onedir` |
| Windows installer | electron-builder NSIS |
| 단위 테스트 | Python test runner와 Vitest |

구체적인 package version은 프로젝트 골격을 생성할 때 lock file로 고정한다. 버전 변경은 lock file과 검증 결과를 함께 갱신한다.

## 3. 시스템 구조

```text
React Renderer
    │ typed preload API
    ▼
preload
    │ allowlisted Electron IPC
    ▼
Electron main process
    ├── Windows dialog와 파일 시스템 경계
    ├── Python worker manager
    ├── Plotly.js report PNG와 저장 파일 관리
    ├── PPTX 템플릿 및 출력 경로 검증
    └── BrowserWindow 수명 주기
            │ stdin/stdout NDJSON
            ▼
       Python analysis worker
            ├── image I/O
            ├── ROI와 profile
            ├── FFT와 filtering
            ├── CSV output
            └── python-pptx slide assembly

React report renderer
    ├── 공통 Plotly.js trace와 style
    ├── 고정 크기 off-screen figure
    ├── PNG export와 preview
    └── Electron main을 통한 PNG 저장
```

### 3.1 Electron main process

main process는 다음 책임을 가진다.

- BrowserWindow 생성과 종료
- Content Security Policy 설정
- Root Folder 선택
- Root 경계 안의 `.mim` 파일 목록과 경로 검증
- Python worker 시작, 상태 확인, 요청 전달, 종료 및 1회 복구
- Renderer 요청과 Python 응답의 request ID 연결
- Python이 만든 임시 PNG 읽기와 정리
- Plotly.js data URL을 PNG bytes로 변환해 report job 임시 디렉터리에 저장
- 사용자가 선택한 CSV, PPTX와 report image 저장 위치 검증
- PPTX 템플릿 경로, 확장자와 존재 여부 검증
- 구조화된 오류를 preload에 반환

main process는 FFT 계산을 구현하지 않는다.

### 3.2 preload

preload는 `contextBridge`를 통해 Renderer에 제한된 API만 제공한다. `ipcRenderer` 객체와 임의 channel 호출 기능을 노출하지 않는다.

공개 API의 개념적 형태는 다음과 같다.

```typescript
interface FftAnalysisApi {
  selectRootFolder(): Promise<Result<RootInfo>>
  listImages(directoryPath?: string): Promise<Result<ImageEntry[]>>
  loadImage(request: LoadImageRequest): Promise<Result<ImageView>>
  analyze(request: AnalysisRequest): Promise<Result<AnalysisResult>>
  saveCsv(request: SaveCsvRequest): Promise<Result<SavedFile>>
  selectReportTemplate(): Promise<Result<SelectedFile>>
  selectReportOutputDirectory(): Promise<Result<SelectedDirectory>>
  writeReportPng(request: WriteReportPngRequest): Promise<Result<ReportAsset>>
  buildPptx(request: BuildPptxRequest): Promise<Result<ReportResult>>
  getEngineStatus(): Promise<EngineStatus>
}
```

preload는 문자열, 숫자, 배열 길이와 enum 형태를 1차 검증한다. 파일의 실제 경계와 권한 검증은 main process가 담당한다.

### 3.3 React Renderer

Renderer는 다음 책임을 가진다.

- Explorer, Image, Analysis 및 Settings 화면
- 현재 파일, ROI, 분석 방향과 설정 상태
- SVG ROI overlay 표시와 pointer interaction
- Plotly.js profile 및 spectrum 표시
- 공통 Plotly.js trace·style을 사용하는 보고서 전용 figure 생성
- 고정 `width`, `height`, `scale` PNG export와 최종 PNG preview
- report job의 PNG 생성 진행 상태 관리
- loading, empty, stale 및 error 상태 표시
- 최신 request ID 기준 응답 반영

Renderer는 다음 작업을 하지 않는다.

- Node.js `fs`, `path` 또는 `child_process` 직접 호출
- `.mim` 직접 디코딩
- NumPy 분석식의 JavaScript 재구현
- 검증되지 않은 로컬 경로를 `<img src="file://...">`로 직접 표시

### 3.4 Python 분석 엔진

Python 엔진은 GUI 없는 지속 실행 worker다. 다음 책임을 가진다.

- `.mim` 이미지 읽기와 2D grayscale 검증
- 이미지 회전
- Pillow 기반 표시용 grayscale PNG 생성
- 정규화 ROI 좌표를 pixel 범위로 변환하고 crop
- raw profile과 normalized dL/L(%) profile 계산
- FFT spectrum과 Top-K peak 계산
- band-pass profile과 peak-to-valley 계산
- profile, spectrum 및 peak CSV 생성
- 검증된 Plotly.js PNG를 PPTX 템플릿의 고정 picture slot에 삽입
- 생성된 PPTX의 slide 수, title, picture 수와 slot geometry 검증

Python 엔진은 Electron 창, dialog, 파일 탐색 UI 또는 graph를 생성하지 않는다. PyQt와 matplotlib를 runtime dependency로 사용하지 않는다. PPTX 조립은 `python-pptx`를 사용한다.

## 4. 프로세스 수명 주기

### 4.1 시작

1. Electron main process가 시작된다.
2. 개발 환경에서는 설정된 Python interpreter와 worker module을 실행한다.
3. 패키지 환경에서는 `process.resourcesPath/engine/fft-engine.exe`를 실행한다.
4. main process가 `engine.ping`을 보내고 protocol version을 확인한다.
5. handshake가 성공한 뒤 분석 관련 UI를 활성화한다.

Python worker는 분석 요청마다 새로 실행하지 않고 애플리케이션 세션 동안 유지한다.

### 4.2 종료와 복구

- 정상 종료 시 main process는 `engine.shutdown`을 요청하고 제한 시간 후 남은 프로세스를 종료한다.
- worker가 비정상 종료하면 진행 중 요청은 `ENGINE_EXITED`로 실패 처리한다.
- main process는 자동 재시작을 한 번 시도한다.
- 재시작 후에도 handshake가 실패하면 분석 UI를 비활성화하고 영어 오류 메시지를 표시한다.
- Renderer reload가 Python worker를 중복 실행하게 해서는 안 된다.

Windows에서 Python worker 창은 표시하지 않는다.

## 5. Electron과 Python 통신 계약

### 5.1 전송 형식

main process와 Python worker는 UTF-8 NDJSON을 사용한다. 한 줄은 하나의 완전한 요청 또는 응답이다.

- stdin: main process가 worker로 보내는 요청 전용
- stdout: protocol 응답 전용
- stderr: 사람이 읽는 로그 전용
- stdout에는 디버그 메시지, progress text 또는 traceback을 출력하지 않는다.
- 모든 메시지는 `protocolVersion`과 `requestId`를 포함한다.

### 5.2 요청 envelope

```json
{
  "protocolVersion": 1,
  "requestId": "request-17",
  "method": "analysis.run",
  "params": {}
}
```

### 5.3 성공 응답

```json
{
  "protocolVersion": 1,
  "requestId": "request-17",
  "ok": true,
  "result": {}
}
```

### 5.4 실패 응답

```json
{
  "protocolVersion": 1,
  "requestId": "request-17",
  "ok": false,
  "error": {
    "code": "INVALID_ROI",
    "message": "ROI bounds must be between 0 and 1.",
    "details": null
  }
}
```

Renderer에 표시하는 오류 문자열은 영어로 작성한다. traceback과 내부 경로 정보는 Renderer에 직접 노출하지 않고 로그에 기록한다.

### 5.5 worker method

| method | 입력 | 출력 |
| --- | --- | --- |
| `engine.ping` | 없음 | protocol version, engine version |
| `image.load` | 이미지 경로, 회전 | 이미지 metadata, 표시용 PNG 임시 경로 |
| `analysis.run` | 이미지 경로, 회전, ROI, 방향, 설정 | profile, spectrum, peaks, band-pass, peak-to-valley |
| `csv.save` | 저장 경로, 분석 결과 종류와 값 | 저장된 절대 경로 |
| `report.build_pptx` | 템플릿 경로, 출력 경로, slide title과 검증된 PNG asset 목록 | PPTX 경로, slide 수, picture 수 |
| `engine.shutdown` | 없음 | 종료 승인 |

`image.load`와 `analysis.run`은 동일 파일을 반복해서 디코딩하지 않도록 worker 내부에 제한된 최근 이미지 cache를 둘 수 있다. cache key는 실제 경로, 수정 시각과 회전값을 포함해야 한다.

## 6. 데이터 계약

### 6.1 ROI

```json
{
  "id": "roi-1",
  "label": "Total",
  "color": "#ffff00",
  "xmin": 0.0,
  "xmax": 1.0,
  "ymin": 0.0,
  "ymax": 1.0
}
```

- 좌표는 회전된 이미지 기준의 정규화 값이다.
- 모든 좌표는 `0.0` 이상 `1.0` 이하다.
- `xmin < xmax`, `ymin < ymax`여야 한다.
- Renderer와 Python worker가 각각 입력을 검증한다.
- 사용자 표시에는 `label`을 사용하고 내부 참조에는 변경되지 않는 `id`를 사용한다.

### 6.2 이미지 결과

```json
{
  "imageId": "image-23",
  "widthPx": 4096,
  "heightPx": 3072,
  "dtype": "uint16",
  "displayMin": 0.0,
  "displayMax": 65535.0,
  "pngPath": "controlled-temporary-path"
}
```

`pngPath`는 Python worker와 main process 사이에서만 사용한다. main process는 해당 파일이 앱 전용 임시 디렉터리 안에 있는지 검증한 후 PNG bytes를 읽어 Renderer에 전달한다. Renderer는 bytes로 Blob URL을 생성하고 교체 시 이전 URL을 해제한다.

PNG는 화면 표시용 데이터이며 수치 분석 입력으로 다시 사용하지 않는다. 분석은 원래 `.mim` 배열을 사용한다.

### 6.3 분석 요청

```json
{
  "imagePath": "D:\\data\\sample.mim",
  "rotation": 0,
  "roi": {
    "id": "roi-1",
    "label": "Total",
    "color": "#ffff00",
    "xmin": 0.0,
    "xmax": 1.0,
    "ymin": 0.0,
    "ymax": 1.0
  },
  "direction": "horizontal",
  "settings": {
    "physicalWidthMm": 0.0,
    "physicalHeightMm": 0.0,
    "averagingBandSizePx": 0,
    "referenceBandSizePx": 0,
    "lowPassCutoff": 0.0,
    "highPassCutoff": 0.0,
    "topK": 1
  }
}
```

Renderer와 TypeScript IPC에서는 camelCase를 사용한다. Python 내부 식별자는 snake_case를 사용하며 worker 경계에서 한 번만 변환한다. CSV column 이름은 별도 저장 계약에서 고정하고 임의로 변경하지 않는다.

### 6.4 분석 결과

```json
{
  "profile": {
    "positionMm": [],
    "raw": [],
    "normalizedPercent": [],
    "bandpassPercent": []
  },
  "spectrum": {
    "frequencyCyclesPerMm": [],
    "amplitude": []
  },
  "peaks": [
    {
      "index": 0,
      "frequencyCyclesPerMm": 0.0,
      "wavelengthMm": null,
      "amplitude": 0.0
    }
  ],
  "peakToValleyPercent": 0.0
}
```

- 배열 값은 JSON number 또는 `null`만 사용한다.
- NaN과 Infinity를 JSON에 기록하지 않는다.
- 값이 정의되지 않는 경우 worker는 `null` 또는 구조화된 오류를 반환한다.
- 주파수와 길이 단위는 기존 FFT API 명세와 동일하게 cycles/mm와 mm를 사용한다.
- 계산 공식과 boundary 규칙은 기존 FFT API 명세 및 승인된 baseline test를 따른다.

초기 구현은 JSON number array를 사용한다. 실제 대표 데이터에서 전송 비용이 병목으로 확인된 경우에만 binary typed-array protocol을 별도 승인 후 도입한다.

## 7. 파일 시스템과 보안 경계

### 7.1 BrowserWindow

제품 BrowserWindow는 다음 설정을 유지한다.

```typescript
webPreferences: {
  contextIsolation: true,
  nodeIntegration: false,
  sandbox: true,
  preload: preloadPath
}
```

Renderer에 필요한 script, style, image와 연결 대상만 허용하는 Content Security Policy를 설정한다.

### 7.2 Root Folder 경계

1. 사용자가 Folder Picker로 Root Folder를 선택한다.
2. main process는 Root의 절대 경로와 실제 경로를 저장한다.
3. 모든 파일 목록, 이미지 로딩 및 저장 요청은 main process에서 정규화한다.
4. 읽기 대상은 Root와 같거나 Root 하위의 기존 `.mim` 파일이어야 한다.
5. 실제 경로를 다시 확인해 symlink와 junction을 통한 Root 이탈을 거부한다.
6. 검증을 통과한 절대 경로만 Python worker에 전달한다.

CSV와 PPTX 저장은 사용자가 Save Dialog 또는 Folder Picker에서 선택한 경로에만 허용한다. Python worker가 Renderer 문자열만으로 임의 경로에 저장하게 해서는 안 된다. PPTX 템플릿은 설치본에 포함된 기본 템플릿 또는 사용자가 File Picker에서 선택한 기존 `.pptx` 파일만 허용한다.

### 7.3 임시 파일

- 표시용 이미지 PNG와 Plotly.js 보고서 PNG는 report job별 애플리케이션 전용 임시 디렉터리에 생성한다.
- 파일명은 사용자 입력을 직접 포함하지 않는 고유 ID를 사용한다.
- Renderer가 전달하는 보고서 이미지는 `data:image/png;base64,` 형식만 허용한다. main process는 형식과 설정된 최대 byte 크기를 검증한 뒤 decode한다.
- main process는 요청 응답을 전달하기 전에 실제 경계, 확장자와 PNG signature를 확인한다.
- Python worker에는 main process가 생성하고 검증한 report asset 경로만 전달한다.
- 이미지 교체, cache 제거 및 앱 종료 시 더 이상 사용하지 않는 임시 파일을 정리한다.
- 정리 실패는 로그에 남기되 정상 종료를 방해하지 않는다.

## 8. GUI와 상태

### 8.1 기본 레이아웃

```text
Application Window
├── Explorer
└── Workspace
    ├── Image tab
    ├── Analysis tab
    └── Settings tab
```

모든 탭, 버튼, 레이블, tooltip, status와 오류 메시지는 영어로 표시한다.

### 8.2 Renderer 상태

| 상태 | 설명 |
| --- | --- |
| `rootPath` | 선택된 Root Folder 또는 `null` |
| `imageEntries` | 탐색된 `.mim` 파일 목록 |
| `selectedImagePath` | 현재 이미지 또는 `null` |
| `imageView` | 표시용 image metadata와 Blob URL |
| `rois` | 공통 ROI 목록 |
| `editingRoiId` | Image 탭에서 편집 중인 ROI |
| `analysisRoiId` | Analysis 탭에서 선택한 ROI |
| `direction` | `horizontal` 또는 `vertical` |
| `settings` | 분석 설정 단일 원본 |
| `analysis` | 최신 성공 분석 결과 |
| `pendingRequestId` | 현재 유효한 분석 요청 |
| `engineStatus` | `starting`, `ready`, `failed` |
| `reportJob` | 선택한 template, output, ROI 순서와 PNG/PPTX 진행 상태 |

같은 설정이나 ROI를 여러 state에 복제하지 않는다. `editingRoiId`와 `analysisRoiId`는 서로 독립적이다.

## 9. 이미지와 ROI 상호작용

### 9.1 이미지 표시

- Python worker가 grayscale PNG를 생성한다.
- Renderer는 비율을 보존하면서 가용 영역에 맞춰 이미지를 표시한다.
- 실제 image 좌표와 화면 좌표의 transform을 한 모듈에서 관리한다.
- 창 resize와 zoom 후에도 ROI가 같은 image 위치를 가리켜야 한다.

### 9.2 SVG ROI overlay

- ROI 사각형과 네 코너 handle은 이미지 위 SVG overlay로 표시한다.
- ROI의 source of truth는 정규화 좌표다.
- pointer 이동은 화면 좌표를 image 좌표로 변환한 뒤 0~1 범위로 clamp한다.
- 코너가 반대쪽 코너를 통과하지 못하게 최소 크기를 적용한다.
- 선택 ROI는 색상 외에도 선 굵기 또는 handle로 구분한다.

ROI를 드래그하는 동안 Renderer는 overlay만 즉시 갱신한다. Python 분석 요청은 pointer 이동마다 보내지 않고 pointer 종료 시 보낸다.

Settings 입력처럼 연속 변경될 수 있는 값은 마지막 변경 이후 기본 150ms debounce 후 분석한다. 분석 실행 버튼을 별도로 두는 경우 명시적 실행은 debounce를 우회한다.

## 10. Plotly.js 그래프

### 10.1 책임 분리

Python worker는 모든 분석 값을 계산하고 Plotly.js는 전달받은 값만 시각화한다. Renderer에서 FFT, smoothing, filtering 또는 peak 탐색을 다시 계산하지 않는다.

### 10.2 Profile graph

- x축: 위치 mm
- y축: dL/L(%) 또는 해당 trace의 명시된 단위
- normalized profile과 band-pass profile을 겹쳐 표시할 수 있다.
- 각 trace에는 영어 이름과 구분 가능한 색을 사용한다.
- hover에서 x와 y 값을 표시한다.
- legend에서 trace 표시 여부를 전환할 수 있다.

### 10.3 FFT spectrum graph

- x축: cycles/mm
- y축: amplitude
- spectrum은 line trace로 표시한다.
- Top-K peak는 marker trace로 분리한다.
- peak hover에는 frequency, wavelength와 amplitude를 표시한다.

### 10.4 갱신

- 같은 graph container를 유지하고 Plotly의 갱신 API로 trace와 layout을 변경한다.
- 새 분석 결과가 도착해도 사용자가 선택한 zoom 범위 유지 여부는 데이터 범위가 동일한 경우 유지하고, 파일·ROI·방향이 바뀌면 autorange로 초기화한다.
- container resize 시 graph를 현재 영역에 맞춘다.
- 다크·라이트 테마는 CSS와 Plotly layout을 함께 변경하되 Python 재계산을 요청하지 않는다.
- graph 갱신은 Python에서 PNG를 다시 생성하지 않는다.

CSV 저장 데이터는 Plotly 내부 상태가 아니라 Python 분석 결과를 기준으로 한다.

### 10.5 공통 figure 정의

화면과 보고서는 같은 분석 결과와 공통 trace·style builder를 사용한다. 다음 항목을 공통 정의로 관리한다.

- trace 데이터와 표시 순서
- line, marker, peak 색상과 두께
- axis title, 단위와 number format
- 표시할 FFT 범위와 Top-K peak
- legend label과 순서
- NaN과 누락값 처리

화면 layout은 반응형 크기, hover, zoom과 pan을 허용한다. 보고서 layout은 같은 trace·style 위에 고정 크기, 고정 margin, 고정 font와 static export 설정을 적용한다. 화면의 현재 zoom 상태를 보고서에 복사하지 않는다.

### 10.6 보고서 PNG export

보고서 PNG는 현재 보이는 graph를 화면 크기 그대로 capture하지 않는다. report 전용 off-screen graph container를 만들고 `Plotly.toImage()`에 `format`, `width`, `height`와 `scale`을 명시한다.

기존 `260705_fft-analysis-benz-ver2` 출력 비율을 계승하는 기본 논리 크기는 다음과 같다.

| figure | `width` | `height` | `scale` | 종횡비 |
| --- | ---: | ---: | ---: | ---: |
| Overview | 1800 px | 600 px | 1 | 3:1 |
| ROI direction analysis | 600 px | 1200 px | 1 | 1:2 |

`scale`은 논리 layout과 종횡비를 유지하면서 실제 출력 해상도를 높일 때만 변경한다. 한 report job 안에서는 같은 종류의 figure에 같은 크기와 scale을 사용한다. PPTX picture slot의 종횡비는 대응 PNG와 같아야 하며 `python-pptx` 삽입 과정에서 이미지를 강제로 늘이거나 찌그러뜨리지 않는다.

Overview figure는 grayscale 이미지, 선택된 ROI 사각형, ROI label과 legend를 포함한다. ROI direction analysis figure는 기존 보고서 구성을 계승해 다음 네 행을 세로로 배치한다.

1. FFT spectrum과 Top-3 peak marker
2. profile과 Top-1 period guide line
3. profile과 Top-2 period guide line
4. profile과 Top-3 period guide line

보고서 생성 순서는 다음과 같다.

1. Python worker가 승인된 분석 결과를 반환한다.
2. report renderer가 공통 trace·style과 고정 report layout으로 off-screen figure를 생성한다.
3. `Plotly.toImage()`가 PNG data URL을 반환한다.
4. Renderer가 제한된 preload API로 PNG를 main process에 전달한다.
5. main process가 검증한 PNG를 report job 임시 디렉터리에 저장한다.
6. Renderer는 저장된 최종 PNG bytes를 report preview에 표시한다.
7. 모든 필수 PNG가 준비되면 main process가 검증된 asset 목록으로 `report.build_pptx`를 호출한다.

### 10.7 PPTX 보고서

기본 PPTX 템플릿은 한 장의 template slide와 다섯 개의 picture slot을 가진다. 사용자는 보고서에 포함할 ROI 네 개와 그 순서를 선택한다.

샘플별로 horizontal과 vertical slide를 각각 한 장 생성한다. 각 slide에는 다음 PNG를 삽입한다.

1. overview PNG 한 개
2. 선택된 ROI 네 개의 해당 방향 분석 PNG

`python-pptx` 조립 계층은 template의 text와 overlay shape를 복사하고, title을 설정하고, PNG를 template picture slot 위치와 크기에 맞춰 삽입한다. 생성 직후 다음 항목을 다시 열어 검증한다.

- 예상 slide 수
- slide title 순서
- slide당 picture 다섯 개
- template과 생성 slide의 picture slot 위치와 크기
- 모든 PNG와 PPTX 파일의 존재 및 non-zero 크기

기본 템플릿과 다른 picture slot 수를 지원하는 기능은 초기 범위에 포함하지 않는다.

## 11. 비동기 요청과 stale result

1. Renderer가 새 분석 요청마다 고유 request ID를 만든다.
2. `pendingRequestId`를 최신 ID로 교체한다.
3. main process는 같은 ID로 Python worker에 전달한다.
4. 응답 ID가 현재 `pendingRequestId`와 다르면 Renderer는 해당 결과를 폐기한다.
5. 최신 요청 실패 시 마지막 성공 그래프를 유지할지 비우는지는 오류 종류에 따라 결정한다. 입력 오류는 이전 결과를 유지하고 오류를 표시하며, 파일 변경·삭제 오류는 결과를 비운다.

Python 계산을 실제로 중단하는 cancellation은 초기 범위에 포함하지 않는다. stale result 폐기로 화면 정확성을 먼저 보장한다.

## 12. 오류 코드

| 코드 | 의미 | UI 처리 |
| --- | --- | --- |
| `ENGINE_NOT_READY` | worker handshake 전 요청 | 분석 UI 비활성화와 상태 표시 |
| `ENGINE_EXITED` | 계산 중 worker 종료 | 요청 실패와 재시작 상태 표시 |
| `PROTOCOL_MISMATCH` | Electron과 worker version 불일치 | 분석 차단과 재설치 안내 |
| `INVALID_REQUEST` | method 또는 입력 형태 오류 | 영어 입력 오류 표시 |
| `INVALID_PATH` | 빈 경로 또는 비정상 경로 | 요청 거부 |
| `OUTSIDE_ROOT` | Root 밖 읽기 요청 | 접근 거부 |
| `NOT_FOUND` | 파일이 존재하지 않음 | 목록 갱신 안내 |
| `ACCESS_DENIED` | 파일 읽기 또는 저장 권한 없음 | 영어 권한 오류 표시 |
| `UNSUPPORTED_IMAGE` | `.mim` 형식 또는 2D grayscale 조건 불일치 | 이미지 로딩 실패 표시 |
| `INVALID_ROTATION` | 허용되지 않은 회전 | 설정 오류 표시 |
| `INVALID_ROI` | ROI 좌표 또는 크기 오류 | ROI 입력 강조와 분석 중단 |
| `INVALID_SETTINGS` | 분석 설정 범위 오류 | 해당 설정 입력 강조 |
| `ANALYSIS_FAILED` | 계산 중 처리되지 않은 오류 | 이전 정상 결과 유지와 오류 표시 |
| `SAVE_FAILED` | CSV 저장 실패 | 저장 실패 상태 표시 |
| `REPORT_RENDER_FAILED` | Plotly.js PNG export 또는 PNG 검증 실패 | report job 중단과 실패 figure 표시 |
| `INVALID_TEMPLATE` | PPTX template 구조 또는 slot 수 불일치 | template 오류와 요구 조건 표시 |
| `PPTX_BUILD_FAILED` | PNG 삽입, PPTX 저장 또는 사후 검증 실패 | report job 실패와 로그 위치 표시 |

오류로 앱을 비정상 종료하지 않는다. 내부 예외와 traceback은 로그에 남기고 Renderer에는 안정된 오류 코드와 영어 메시지만 전달한다.

## 13. 소스와 빌드 구조

목표 구조는 다음과 같다.

```text
.
├── package.json
├── package-lock.json
├── electron.vite.config.ts
├── electron/
│   ├── main/
│   │   ├── index.ts
│   │   ├── engine-manager.ts
│   │   ├── report-assets.ts
│   │   └── filesystem-boundary.ts
│   ├── preload/
│   │   └── index.ts
│   ├── renderer/
│   │   ├── index.html
│   │   └── src/
│   │       ├── App.tsx
│   │       ├── components/
│   │       ├── reports/
│   │       │   ├── report-figure.tsx
│   │       │   └── report-export.ts
│   │       ├── state/
│   │       └── styles.css
│   └── shared/
│       └── contracts.ts
├── src/
│   ├── __init__.py
│   └── engine/
│       ├── __init__.py
│       ├── analysis.py
│       ├── image_io.py
│       ├── pptx_report.py
│       ├── protocol.py
│       └── worker.py
├── resources/
│   └── templates/
│       └── TEMPLATE-OUTPUT-SLIDE.pptx
├── tests/
│   ├── python/
│   └── electron/
├── build/
│   └── pyinstaller/
└── release/
```

`src/` 아래 Python 파일은 프로젝트의 Python 작성 규칙을 따른다. Electron 내부 import는 계층 경계를 명확히 유지하며 Renderer가 main 전용 module을 import하지 않는다.

## 14. 패키징

### 14.1 Python 엔진

- PyInstaller `onedir`로 `fft-engine.exe`와 runtime 파일을 생성한다.
- GUI framework와 개발·테스트 dependency는 포함하지 않는다.
- 필요한 hidden import, tifffile codec, Pillow PNG encoder와 python-pptx dependency를 명시적으로 검증한다.
- matplotlib와 PyQt는 포함하지 않는다.
- 빌드된 엔진은 Python이 설치되지 않은 clean Windows 환경에서 실행되어야 한다.

### 14.2 Electron 설치 프로그램

electron-builder는 다음 항목을 NSIS installer에 포함한다.

- Electron main, preload 및 Renderer bundle
- Plotly.js bundle
- 제품 icon과 정적 asset
- PyInstaller `onedir` 전체 폴더
- 기본 PPTX 템플릿
- 필요한 license와 제품 metadata

Python 엔진 폴더는 `extraResources`를 사용해 설치본의 `resources/engine`에 둔다. main process는 패키지 환경에서 `process.resourcesPath`를 기준으로 실행 파일을 찾는다.

사용자에게 전달하는 artifact는 단일 NSIS Setup `.exe`다. 설치 후 디렉터리가 여러 runtime 파일을 포함하는 것은 허용한다. Python worker를 PyInstaller `onefile`로 다시 감싸 단일 설치 후 실행 파일을 만드는 것은 목표가 아니다.

### 14.3 빌드 순서

```text
Python unit tests
→ PyInstaller engine build
→ packaged engine smoke test
→ Electron typecheck and unit tests
→ fixed-size Plotly PNG and PPTX integration test
→ electron-vite build
→ electron-builder NSIS package
→ clean Windows install and end-to-end smoke test
```

Windows x64 artifact는 Windows x64 build 환경에서 생성한다. Electron과 Python 엔진의 architecture는 일치해야 한다.

## 15. 로그와 진단

- main process와 Python worker 로그는 사용자 데이터 디렉터리 아래 제품 전용 log 디렉터리에 기록한다.
- 로그에는 timestamp, severity, component와 request ID를 포함한다.
- 정상 분석 배열과 전체 이미지 데이터는 기본 로그에 기록하지 않는다.
- 사용자가 선택한 경로는 진단에 필요한 범위에서만 기록한다.
- 로그 파일은 크기 또는 개수 기준으로 제한하고 무한히 증가하지 않게 한다.

## 16. 검증 기준

### 16.1 Python 분석

- 승인된 대표 `.mim` 파일을 정확한 shape와 dtype으로 읽는다.
- 허용 회전별 결과가 baseline과 일치한다.
- 정규화 ROI crop 경계가 baseline과 일치한다.
- raw, normalized, band-pass profile 결과가 허용 오차 내에서 일치한다.
- FFT frequency, amplitude, Top-K peak와 peak-to-valley가 허용 오차 내에서 일치한다.
- 잘못된 이미지, ROI와 설정이 안정된 오류 코드로 변환된다.

수치 허용 오차는 baseline test를 만들 때 dtype과 기존 기준 구현을 근거로 고정한다. 근거 없이 모든 분석에 하나의 공통 오차를 적용하지 않는다.

### 16.2 Electron 경계

- Renderer에서 Node.js API를 사용할 수 없다.
- preload는 allowlisted API만 노출한다.
- Root 밖 경로와 junction 우회가 Python worker에 전달되기 전에 거부된다.
- protocol version 불일치가 분석 실행 전에 탐지된다.
- worker 비정상 종료가 Electron 앱 비정상 종료로 이어지지 않는다.
- Renderer reload 후 worker가 중복 실행되지 않는다.

### 16.3 GUI

- Root 선택, 파일 목록, 이미지 표시와 상태표시줄이 동작한다.
- 기본 ROI가 없는 최초 이미지 로딩 시 전체 이미지 ROI가 생성된다.
- ROI drag와 Settings 좌표가 같은 정규화 좌표를 편집한다.
- ROI drag 중 overlay가 Python 응답과 독립적으로 갱신된다.
- 최신 분석 응답만 graph에 반영된다.
- profile, spectrum, peak와 band-pass trace가 올바른 축과 단위로 표시된다.
- theme와 resize는 Python 재분석 없이 graph에 반영된다.
- 화면과 보고서 figure가 같은 분석 배열, peak와 공통 trace·style 정의를 사용한다.
- Overview PNG가 기본 1800 x 600 px, ROI direction PNG가 기본 600 x 1200 px로 생성된다.
- report preview가 PPTX에 실제 삽입되는 PNG와 동일하다.
- GUI 표시 문자열은 모두 영어다.

### 16.4 보고서

- 기본 template은 한 장의 slide와 picture slot 다섯 개를 가져야 한다.
- 사용자가 선택한 ROI 네 개의 순서가 report image와 PPTX slot 순서에 반영된다.
- 샘플마다 horizontal과 vertical slide가 각각 생성된다.
- slide마다 overview 한 개와 ROI 분석 이미지 네 개가 삽입된다.
- 생성된 slide 수, title, picture 수와 slot geometry 검증이 통과한다.
- PNG export 또는 PPTX 조립 실패는 부분 성공으로 표시하지 않고 구조화된 오류를 반환한다.

### 16.5 패키지

- 시스템 Python과 Node.js가 없는 clean Windows x64 환경에서 설치, 실행 및 제거된다.
- 설치된 앱이 포함된 Python worker를 찾고 handshake를 완료한다.
- 대표 `.mim` 파일 로딩, ROI 분석, graph 표시, 고정 크기 PNG, PPTX 보고서와 CSV 저장이 설치본에서 동작한다.
- 앱 종료 후 Python worker가 남지 않는다.

## 17. 전환과 폐기 기준

현재 PyQt 구현은 다음 조건을 모두 충족하기 전까지 비교 기준으로 보존한다.

1. Python 분석 baseline test가 준비된다.
2. Electron에서 파일 선택, 이미지 표시와 ROI 편집이 동작한다.
3. Python worker 결과가 Plotly.js graph에 표시된다.
4. Plotly.js report PNG가 고정 크기로 생성되고 preview와 PPTX에 동일하게 사용된다.
5. python-pptx가 기본 template으로 horizontal·vertical slide를 생성하고 사후 검증한다.
6. CSV 저장과 구조화된 오류 처리가 동작한다.
7. NSIS 설치본의 clean Windows 검증이 통과한다.

조건을 충족한 뒤 다음 항목을 별도 승인된 변경으로 제거한다.

- PyQt GUI 진입점
- `gui.ui`
- Qt matplotlib Canvas 연결
- 사용하지 않는 PyQt와 matplotlib GUI dependency

기존 파일과 사용자 변경 사항을 새 구현 검증 전에 삭제하지 않는다.

## 18. 향후 검토 항목

다음 항목은 현재 확정 기준이 아니며 실제 요구나 측정 결과가 생길 때 별도 명세 변경으로 다룬다.

- JSON 배열 대신 binary typed-array protocol
- 진행률 event와 실제 계산 cancellation
- worker pool 또는 여러 이미지 병렬 분석
- picture slot 수가 다른 사용자 PPTX template
- session과 설정 영구 저장
- 자동 update와 code signing 운영 절차
- macOS와 Linux 패키지
