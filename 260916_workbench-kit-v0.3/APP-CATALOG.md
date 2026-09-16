> 버전: v0.3 · 작성일: 2026-09-16
>
> 이 문서는 workbench-kit 위에 만들 수 있는 응용 앱 후보를 비교한 조사 자료다.
> 현재 v0.3의 `BRIEF.md`와 `DECISIONS.md`가 정한 요구·결정을 바꾸지 않는다.

# APP CATALOG — workbench-kit

## 1. 앱 MVP와 공통 껍데기의 환류

### 1.1 반복 흐름

각 응용 앱은 고정된 workbench-kit 기준 버전을 참조해 **독립 프로젝트 v0.1**으로
빠르게 구현한다. 앱은 공통 껍데기를 자동으로 따라가지 않으며, 시작에 사용한
workbench-kit의 태그 또는 커밋을 앱의 참조 자료에 기록한다. `_clones\workbench-kit`은
읽기 전용 참조본이므로 수정하거나 공통 기능의 반입 대상으로 삼지 않는다.

```text
고정된 workbench-kit 기준 버전
  → 응용 앱 v0.1 구현·검증
  → 공통화 후보 수집·검토
  → workbench-kit 다음 버전에 반영·검증
  → 응용 앱 v0.2 이행 또는 새 기준 기반 MVP 재구성
```

앱 v0.1은 단순한 일회성 결과물이 아니라, 공통 껍데기의 확장 표면이 실제 도메인에서
성립하는지 검증하는 사례다. 앱의 v0.1이 마감되기 전에는 공통화 후보를 확정하지
않는다. 전 Phase 완료만으로 마감하지 않고, 사람이 실제로 써본 검토 루프까지 끝나야
한다.

### 1.2 공통화 후보의 판정

아래 조건을 모두 만족하는 항목만 workbench-kit의 다음 버전에서 검토한다.

| 판정 기준 | 통과 조건 |
| --- | --- |
| 일반성 | 둘 이상의 앱에서 실제로 필요했거나, 리소스 종류와 무관한 명확한 확장 표면이다 |
| 경계 | PDF·LaTeX·Notebook처럼 특정 도메인 지식이나 도메인 데이터 모델을 포함하지 않는다 |
| 호스트 | 공통 기능이면 Electron과 pywebview에서 같은 계약으로 만들고 검증할 수 있다 |
| 실증 | 앱 v0.1의 실제 사용자 시나리오에서 동작과 실패 처리가 확인됐다 |
| 회귀 | 공통화해도 기존 앱의 도메인 코드가 공통 코어로 새지 않으며, 기존 껍데기 검증을 통과한다 |

실제 텍스트 읽기·쓰기 브리지, 저장 실패 처리, 바이너리 asset 전달은 공통화 후보가 될
수 있다. PDF 렌더링, LaTeX 컴파일, Jupyter kernel, 파일 관리자 충돌 정책은 각 앱의
도메인에 남긴다. 후보의 반입 여부는 workbench-kit 새 버전의 사람 작성
`DECISIONS.md`에서 결정하며, 에이전트가 자동으로 반입하지 않는다.

### 1.3 응용 앱 v0.2의 이행 판정

workbench-kit이 갱신된 뒤 각 앱은 새 껍데기로 옮긴다. 판정은 코드 줄 수가 아니라
기존 사용자 시나리오·데이터 수명과의 호환성으로 한다.

| 선택 | 적용 조건 | 처리 |
| --- | --- | --- |
| 점진 이행 | 새 공통 API를 어댑터로 연결한 뒤 v0.1 사용자 시나리오가 그대로 통과하고, 앱의 데이터 모델·사용 흐름을 바꿀 필요가 없다 | 같은 앱의 v0.2에서 공통 기능을 추가 반영한다 |
| MVP 재구성 | 탭 수명, host API, 저장 모델 또는 레이아웃 조합이 바뀌어 v0.1의 앱 코드를 유지하는 비용보다 새 기준에서 재구성하는 편이 낫다 | 같은 앱의 v0.2에서 새 껍데기 기반으로 MVP를 다시 구현한다 |

어느 경우에도 v0.1을 덮어쓰거나 지우지 않는다. v0.1의 문서·코드·검증 기록은 history로
보존하고, v0.2의 `BRIEF.md`에 이행 또는 재구성의 이유를 기록한다.

### 1.4 반입 단위

8개 앱을 모두 만든 뒤 한 번에 공통화를 시도하지 않는다. 다음처럼 검증된 범위별로
workbench-kit의 다음 버전을 시작한다.

| 묶음 | 앱 | 검증 후 검토할 공통 범위 |
| --- | --- | --- |
| 1차 | 마크다운 뷰어, 멀티 텍스트 에디터 | 읽기·쓰기 host 브리지, dirty·저장 실패·탭 수명 |
| 2차 | 코드 에디터, PDF 뷰어, 마인드맵 | 언어 등록, 바이너리 asset, 비파일 문서 수명 |
| 3차 | 2칸 파일 관리자, LaTeX, Jupyter Notebook | 파일 변경, 외부 프로세스, 장기 세션. 도메인에 남길 부분과 공통 계약을 분리 |

각 묶음의 workbench-kit 반영은 기존 껍데기 회귀 검사와 해당 앱의 최소 통합 시나리오를
모두 통과해야 한다. Electron 전용 앱에서만 확인된 기능은 Electron 앱의 host adapter에
남기며, pywebview 구현과 동등성 검증이 끝나기 전에는 공통 계약으로 승격하지 않는다.

## 2. 목적과 공통 전제

이 카탈로그는 공통 껍데기 위에서 8개 응용 앱을 만들 때 필요한 도메인 구현과 추가
의존성을 비교한다. 앱은 공통 코어가 아니라 리소스 종류 등록, 앱 조합 시작점, 호스트
브리지를 통해 붙인다. 껍데기는 파일·폴더·세션 같은 리소스 종류를 알지 않는다.

아래의 **필수 의존성**은 MVP를 만들 때 추가하는 패키지 또는 시스템 도구다. **선택
의존성**은 고급 기능을 원할 때만 넣는다. 정확한 버전은 앱을 실제로 시작할 때 해당
앱의 `package-lock.json` 또는 Python 환경 lockfile로 고정한다.

공통으로 먼저 갖춰야 하는 기능은 다음과 같다.

| 공통 기능 | 내용 | 필요한 앱 |
| --- | --- | --- |
| 리소스 종류 등록 | 파일 확장자·세션 ID를 앱의 보기로 연결하고, 탭을 닫을 때 해당 보기를 해제한다 | 전부 |
| 제한된 호스트 브리지 | 렌더러에 범용 파일시스템·IPC를 주지 않고, 목적별 파일 선택·읽기·쓰기·상태 조회 API만 노출한다 | 파일 기반 7개 |
| 저장 수명 | 실제 저장 뒤 dirty 상태를 해제하고, 저장 실패 시 탭을 계속 열어 둔다 | 편집 앱 5개 |
| 상태 표시 | 앱 작업의 진행·성공·오류를 기존 상태바에 보인다 | 전부 |
| 호스트 동등성 | 두 호스트를 요구하는 기능은 같은 사용자 동작에 같은 결과를 낸다 | pywebview 대상, 공통 기능 |

Electron 앱은 기존의 `contextIsolation: true`, `sandbox: true`, `nodeIntegration: false`
경계를 유지한다. preload에는 `readText`, `writeText`, `copy`, `move`처럼 검증 가능한
목적별 API만 둔다. Python 계산 또는 Jupyter 커널이 필요한 앱만 pywebview를 정본
호스트로 둔다.

## 3. 한눈에 보는 비교

| # | 앱 | 권장 호스트 | MVP 핵심 | 필수 추가 의존성 | 선택·후속 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | 마크다운 뷰어 | Electron | 로컬 Markdown·텍스트를 읽기 전용 탭으로 열기 | 없음. 기존 `marked`, `DOMPurify` 사용 | 없음 |
| 2 | 멀티 텍스트 에디터 | Electron | 탭별 메모·텍스트 파일 편집과 저장 | 없음. 기존 Monaco 사용 | `chokidar`, `iconv-lite` |
| 3 | 코드 에디터 | Electron | Python·Java·C++ 편집과 구문 강조 | 없음. Monaco 언어 모듈만 등록 | LSP 서버, `chokidar`, `iconv-lite` |
| 4 | PDF 뷰어 | Electron | PDF 탭·페이지·확대/축소·검색 | `pdfjs-dist` | PDF.js WASM asset 지원 |
| 5 | 마인드맵 작성 프로그램 | Electron | 트리 노드 편집·자동 배치·저장 | `d3-hierarchy`, `d3-zoom` | `d3-shape` |
| 6 | 2칸 파일 관리자 | Electron | 두 폴더, 다중 선택, 반대편 보기, 복사·이동 | 없음. Node·Electron API 사용 | `chokidar`, `pdfjs-dist`, 가상 목록 라이브러리 |
| 7 | LaTeX 뷰어·컴파일러 | Electron | `.tex` 빌드, 오류 위치, 생성 PDF 미리보기 | TeX Live, `latexmk`, `pdfjs-dist` | SyncTeX, `chokidar` |
| 8 | Jupyter Notebook 뷰어·실행기 | pywebview | 노트북 셀·출력 표시와 로컬 커널 실행 | `nbformat`, `jupyter_client`, `ipykernel` | `nbconvert`, 언어별 kernel |

## 4. 앱별 구현 범위

### 4.1 마크다운 뷰어

**MVP 구현**

- `.md`를 탭에 읽기 전용으로 열고 GitHub Flavored Markdown으로 렌더링한다.
- 상대 경로의 이미지와 루트 안 문서 링크를 앱 안에서 열며, 외부 URL만 기본 브라우저로 넘긴다.
- 코드·일반 텍스트는 줄 번호와 읽기 전용 텍스트 보기로 표시한다.
- 문서별 확대/축소, 코드 블록 복사, 두 문서의 분할 열기를 제공한다.

**범위 밖**

- 원본 편집·저장, 전문 색인·검색, 범용 파일 관리, 원격 문서 로드.

**의존성**

- 추가 패키지는 없다. 키트에 있는 `marked`, `DOMPurify`, Monaco를 사용한다.
- HTML은 정화하고, 원격 스크립트·임의 iframe을 실행하지 않는다.

### 4.2 멀티 텍스트 에디터

**MVP 구현**

- 새 메모, 열기, 저장, 다른 이름 저장, 저장하지 않은 변경 확인을 제공한다.
- 각 탭은 독립 Monaco 모델·커서·스크롤·undo/redo 상태를 가지며, 분할한 칸에서도 그대로 살아 있다.
- UTF-8 텍스트만 읽고 원자적으로 저장한다. 이진 파일·과도하게 큰 파일은 열지 않고 오류를 보인다.
- 새 메모는 임시 ID를 가진 pinned 탭으로 열며, 저장 전 종료될 때 복구할 수 있는 임시 본문을 보관한다.

**범위 밖**

- 공동 편집, 리치 텍스트, 자동 인코딩 추정.

**의존성**

- 필수 추가 패키지는 없다. Monaco가 이미 읽기/편집, 찾기·바꾸기, 변경 감지를 제공한다.
- 외부 수정 감지에는 `chokidar`, CP949·UTF-16 같은 명시적 인코딩 선택에는 `iconv-lite`를 선택한다.

### 4.3 코드 에디터

**MVP 구현**

- 텍스트 에디터의 파일 수명·저장을 재사용한다.
- 앱 시작점에서 Monaco의 Python, Java, C++ 언어 등록 모듈을 불러 구문 강조를 켠다.
- `.py`, `.pyi`는 `python`, `.java`는 `java`, `.c`·`.h`·`.cc`·`.cpp`·`.cxx`·`.hpp`·`.hxx`는 `cpp`로 판별한다.
- 상태바에 현재 언어, 줄·열, 들여쓰기, 인코딩을 표시한다.

**범위 밖**

- 자동완성, 정의 이동, 진단, 빌드, 실행, 디버그, 소스 제어.

**의존성**

- 필수 추가 패키지는 없다. 현재 Monaco 패키지의 개별 언어 모듈을 앱 조합 시작점에서 등록한다.
- 언어 서비스가 필요해질 때만 Python용 Pyright, Java용 JDT LS, C++용 clangd와 LSP 중계 계층을 추가한다. 이들은 각각 별도 시스템 도구·프로세스 수명·보안 정책이 필요하다.

### 4.4 PDF 뷰어

**MVP 구현**

- `.pdf`를 `pdf` 리소스 종류로 열고, 페이지 이동·현재/전체 페이지 표시·확대/축소·맞춤·회전·검색을 제공한다.
- 탭마다 PDF.js 문서와 worker를 소유하고, 탭이 닫힐 때 렌더 작업·이벤트·worker 참조를 해제한다.
- Electron host가 선택하거나 Explorer에서 고른 PDF 바이트만 renderer에 전달한다.

**범위 밖**

- PDF 주석·서명·양식 편집, 임의 `file://` iframe, 원격 URL 직접 로드.

**의존성**

- `pdfjs-dist`가 필수다. display API로 보기 UI를 만들고, worker를 Vite 산출물의 로컬 asset으로 배치한다.
- JPX 같은 고급 이미지가 든 PDF까지 지원하려면 PDF.js WASM asset도 배포하고 `wasmUrl`을 설정한다.

### 4.5 마인드맵 작성 프로그램

**MVP 구현**

- 제목·루트·노드 ID·부모 관계·형제 순서·색·접힘 상태를 가진 앱 전용 JSON 문서를 저장한다.
- 새 맵, 노드 추가·이름 편집·삭제·순서 변경·접기/펼치기, undo/redo를 제공한다.
- SVG 연결선과 HTML 노드 카드로 그리고, 중앙 루트 기준 자동 좌우 배치, 이동·확대/축소·화면 맞춤을 제공한다.

**범위 밖**

- 순환 그래프·자유 연결선·협업·리치 텍스트·이미지 첨부·XMind/OPML 호환·이미지/PDF 내보내기.

**의존성**

- `d3-hierarchy`로 트리 배치를 계산하고 `d3-zoom`으로 이동·확대/축소를 처리한다.
- 곡선 연결선을 원할 때만 `d3-shape`를 추가한다.

### 4.6 Total Commander 방식 2칸 파일 관리자

**MVP 구현**

- 시작 시 편집기 영역의 좌·우 칸에 독립 `CommanderFolderView`를 하나씩 열고, 각각 현재 폴더·선택·스크롤 상태를 보존한다.
- 파일 이름·크기·수정 시각 목록, 폴더 우선 정렬, 다중 선택, 상위 폴더 이동, 새로 고침을 제공한다.
- 한쪽 파일을 선택하면 반대편 칸에 임시 미리보기/편집 탭을 열되, 복사·이동 대상은 각 `FolderSession.currentPath`로 유지한다.
- 복사, 이동, 새 파일·폴더, 이름 변경, 휴지통 삭제, 덮어쓰기 충돌 확인, 권한·경로 오류 표시를 제공한다.

**범위 밖**

- Word·Excel·HWP 편집, 압축 파일 내부 조작, 원격 파일시스템, 자동 동기화.

**의존성**

- 필수 추가 패키지는 없다. Electron dialog·shell과 Node `fs/promises`로 목록·복사·이동·상태 조회를 구현한다.
- 외부 변경 감지는 `chokidar`, PDF 미리보기는 `pdfjs-dist`, 매우 큰 폴더의 목록 가상화는 전용 가상 목록 라이브러리를 선택한다.
- 파일 변경 API는 main process에서만 수행하고, renderer에는 복사·이동 같은 목적별 preload 메서드만 노출한다.

### 4.7 LaTeX 뷰어·컴파일러

**MVP 구현**

- `.tex`를 Monaco로 열고, 루트 문서를 명시적으로 고르거나 `\documentclass` 기준으로 찾는다.
- Build 명령은 고정된 `latexmk` 인자와 작업 폴더에서만 실행하고, 생성 PDF를 PDF 뷰어 탭으로 연다.
- `.log`의 파일·줄·오류를 파싱해 소스 위치로 이동한다.
- 빌드 실패 시 마지막 성공 PDF를 유지하고 상태바에 진행·오류를 표시한다.

**범위 밖**

- `-shell-escape`, 임의 셸 명령, 자동 빌드, SyncTeX, 참고문헌·패키지 자동 설치.

**의존성**

- 시스템 TeX Live와 `latexmk`, PDF 표시용 `pdfjs-dist`가 필수다.
- 파일 변경 기반 자동 빌드에는 `chokidar`, 소스/PDF 양방향 이동에는 TeX Live의 SyncTeX 도구를 후속으로 둔다.

### 4.8 Jupyter Notebook 뷰어·실행기

**MVP 구현**

- `.ipynb`를 `nbformat`으로 읽어 코드·Markdown·저장된 출력·오류 traceback을 셀 단위로 표시한다.
- Markdown은 기존 `marked`와 `DOMPurify`로 렌더링하고, 수식 표시에 MathJax를 추가한다.
- 실행형은 탭마다 로컬 kernel 세션을 소유한다. 실행 요청 뒤 busy, stream, display, error, idle 메시지를 순서대로 UI에 반영한다.
- 탭 닫기·앱 종료·kernel 재시작·중단에서 커널 수명을 명시적으로 처리한다.

**범위 밖**

- ipywidgets, 원격 Jupyter Server, 임의 JavaScript 출력, 협업, notebook 내부 편집기 다중 인스턴스.

**의존성**

- 실행형 정본은 pywebview이며, Python의 `nbformat`, `jupyter_client`, `ipykernel`이 필수다.
- HTML/PDF 같은 내보내기에만 `nbconvert`, Python 외 언어 실행에만 해당 언어 kernel을 추가한다.

## 5. 재사용성 검증 우선순위

우선순위 기준은 일상 사용 빈도가 아니라, 공통 껍데기의 확장 표면을 가장 작은 위험으로
검증하고 다음 단계의 전제 기능을 만드는 순서다.

| 순서 | 앱 | 앞 단계에서 검증하거나 새로 더하는 것 |
| --- | --- | --- |
| 1 | 마크다운 뷰어 | 파일 종류 등록, 읽기 전용 파일 로드, 탭 수명, 정화된 HTML 렌더링 |
| 2 | 멀티 텍스트 에디터 | 실제 텍스트 쓰기, dirty·저장 실패·종료 확인, 새 탭 수명 |
| 3 | 코드 에디터 | 앱별 Monaco 언어 등록과 확장자 판별. 텍스트 에디터의 저장 수명을 재사용 |
| 4 | PDF 뷰어 | 바이너리 파일 전달, worker asset, 무상태 문서 보기 수명 |
| 5 | 마인드맵 작성 프로그램 | 파일 경로가 아닌 앱 문서 ID, 살아 있는 비파일 보기, 앱 전용 저장 모델 |
| 6 | 2칸 파일 관리자 | 두 독립 폴더 보기, 파일 변경 host API, 충돌·진행·되돌릴 수 없는 작업 확인 |
| 7 | LaTeX 뷰어·컴파일러 | 허용 목록 기반 외부 프로세스 실행, 빌드 로그, PDF 파이프라인 |
| 8 | Jupyter Notebook 뷰어·실행기 | pywebview bridge, 장기 kernel 세션, 비동기 출력·오류 메시지 수명 |

## 6. 참고 근거

- 공통 껍데기: `D:\projects\_clones\workbench-kit\docs\current\INTENT.md`, `src/main.ts`, `src/core/editor.ts`, `src/core/texteditor.ts`
- 마크다운 참조 구현: `D:\projects\_clones\markdown-viewer\README.md`
- PDF.js: <https://mozilla.github.io/pdf.js/getting_started/>
- Jupyter notebook 형식과 메시징: <https://nbformat.readthedocs.io/>, <https://jupyter-client.readthedocs.io/en/stable/messaging.html>
- TeX Live: <https://tug.org/texlive/doc/texlive-en/texlive-en.html>
- D3 hierarchy와 zoom: <https://d3js.org/d3-hierarchy/hierarchy>, <https://d3js.org/d3-zoom>
- Electron 보안과 context isolation: <https://www.electronjs.org/docs/latest/tutorial/security>, <https://www.electronjs.org/docs/latest/tutorial/context-isolation>
