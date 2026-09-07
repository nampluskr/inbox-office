# UI - VS Code 요소 매핑

> 참조 메모 · 작성일: 2026-09-07
>
> 이 문서는 스키마 문서(`docs/`)가 아니라 `refs/`의 참조 자료다. 현재 껍데기
> (`tab-explorer-templates` 기반, `markdown-viewer`로 촬영)의 화면 요소가 VS Code의
> 어느 요소에 대응하는지를 짝지어 둔다. VS Code 요소 자체의 설명은
> [`vscode-ui-reference.md`](vscode-ui-reference.md)에 있다.
>
> 대상 스크린샷: `tab-explorer-dark.png` · `tab-explorer-gray.png` ·
> `tab-explorer-white.png` (같은 화면의 세 테마).

---

## 0. 화면의 큰 골격

VS Code는 화면을 몇 개의 "파트(Part)"로 나눈다. 이 껍데기는 그 구성을 따르되 필요
없는 파트를 뺐다.

```
┌───────────────────────────────────────────────────────────┐
│ [메뉴바] File View Help              [타이틀바 창 버튼들]   │  ← Title Bar
├──┬──────────────┬────────────────────┬────────────────────┤
│  │ EXPLORER  ···│ tab tab tab    ⊟   │ tab             ⊟  │  ← Tab Bar
│활│              ├────────────────────┼────────────────────┤
│동│  파일 트리    │                    │                    │
│바│  (탐색기 뷰)  │   편집기 그룹 1     │    편집기 그룹 2    │  ← Editor Groups
│  │              │                    │                    │
├──┴──────────────┴────────────────────┴────────────────────┤
│ 경로…                            Markdown Viewer · Electron │  ← Status Bar
└───────────────────────────────────────────────────────────┘
   ↑Activity  ↑Side Bar (Explorer)
```

| 스크린샷에서 | VS Code 용어(영문) | 한글 통용어 | 이 프로젝트 문서 표현 |
| --- | --- | --- | --- |
| 맨 윗줄 `File View Help` | Menu Bar | 메뉴 바 | 메뉴 줄 |
| 맨 윗줄 전체 + 우측 창 버튼(전체화면·테마·최소화·최대화·닫기) | Title Bar | 제목 표시줄 | (창 상단) |
| 맨 왼쪽 좁은 세로 띠 | Activity Bar | 활동 표시줄 | 세로 띠 |
| `EXPLORER`가 든 세로 패널 | Primary Side Bar | 기본 사이드 바 | 탐색기 사이드바 |
| 가운데·오른쪽 문서가 열린 넓은 영역 | Editor Area | 편집기 영역 | 보기 영역 |
| 맨 아랫줄(경로 / 앱 이름) | Status Bar | 상태 표시줄 | 상태 표시줄 |

VS Code에는 하단 가로 영역 Panel과 오른쪽 Secondary Side Bar도 있으나 이 껍데기에는
둘 다 없다 (5절).

---

## 1. Activity Bar (맨 왼쪽 세로 띠)

VS Code에서 이 띠는 뷰 전환 버튼(탐색기·검색·소스제어·실행·확장)이 위에, 계정·설정이
아래에 놓인다.

이 껍데기는 그 전환 버튼을 거의 다 뺐다.

- 위쪽 아이콘: 사이드바 접기/펼치기 = VS Code의 Toggle Side Bar (`Ctrl+B`).
- 아래쪽 아이콘: 테마를 순환시키는 테마 버튼 (White → Gray → Dark) = VS Code의
  색 테마 전환(Color Theme).

---

## 2. Side Bar 안의 탐색기

| 스크린샷에서 | VS Code 용어 | 한글 | 설명·예시 |
| --- | --- | --- | --- |
| `EXPLORER` 글자 | Explorer (View) | 탐색기 뷰 | 사이드 바에 들어가는 하나의 "뷰". 여기선 Explorer 하나만 있음 |
| `EXPLORER` 오른쪽 아이콘들(새 파일·새로고침·모두 접기) | View Actions | 뷰 액션(툴바) | VS Code Explorer의 New File, Refresh, Collapse Folders에 해당 |
| `projects`·`_clones`·`markdown-viewer` … 목록 | File Tree | 파일 트리 | 폴더/파일을 계층으로 보여주는 트리 |
| 폴더 앞 `▾`/`▸` | Twistie (chevron) | 펼침 화살표 | 눌러서 폴더를 펼치고 접음 |
| 트리 맨 위 `projects` | Root Folder | 루트 폴더 | 사용자가 연 최상위 폴더 |
| 들여쓴 세로선 | Indent Guides | 들여쓰기 안내선 | 깊이를 표시하는 세로선 |

---

## 3. 편집기 영역 (가운데 + 오른쪽)

이 프로젝트에서 가장 중요한 부분이다. 화면이 좌우 두 칸으로 갈려 있고, VS Code에서
이 한 칸을 Editor Group(편집기 그룹)이라 부른다.

| 스크린샷에서 | VS Code 용어 | 한글 | 설명·예시 |
| --- | --- | --- | --- |
| 가운데 칸 / 오른쪽 칸 | Editor Group | 편집기 그룹 | 왼쪽엔 `AGENTS.md`·`CLAUDE.md`, 오른쪽엔 `INIT.md`가 열림 |
| 좌우로 가르는 동작·결과 | Split Editor | 편집기 분할 | VS Code `Ctrl+\`. 문서 표현으로는 "좌우 가르기" |
| `AGENTS.md`, `CLAUDE.md ✕` 낱개 | Tab | 탭 | 열린 문서 하나 = 탭 하나 |
| 탭이 늘어선 가로 줄 | Editor Tab Bar | 탭 바 | 그룹 맨 위 탭 줄 |
| 진하게 강조된 `CLAUDE.md` | Active Tab | 활성 탭 | 지금 보는 탭 |
| 탭 오른쪽 `✕` | Tab Close Button | 닫기 버튼 | |
| 각 그룹 오른쪽 위 아이콘 | Editor Actions (Split Editor) | 편집기 액션 | 그 그룹을 또 나눔 |
| 탭 아래 렌더된 본문 | Editor (여기선 읽기 전용 보기) | 편집기 본문 | 이 자리에 무엇을 그릴지가 갈아끼우는 부분 |

**용어 주의 — VS Code의 "Panel"과 헷갈리기 쉬움.** VS Code에서 터미널은 화면 아래
가로 영역인 Panel에 뜬다. 그러나 workbench-kit의 폴더 탐색기는 "탭 영역(= Editor
Group)에 터미널을 연다". 즉 이 프로젝트는 하단 Panel을 쓰지 않고 터미널도 하나의
탭으로 편집기 그룹 안에 넣는다. 이는 INTENT의 "탭은 파일 경로가 아니다"와 직접
연결된다.

---

## 4. 상태 표시줄 (맨 아래)

- 왼쪽: 지금 파일의 경로 (`D:\projects\_clones\markdown-viewer\CLAUDE.md`).
- 오른쪽: `Markdown Viewer v0.1 (2026-09-07) · Electron`.
- VS Code의 Status Bar와 같은 자리이며, 언어 모드·줄/열·인코딩 같은 항목은 넣지
  않고 최소한만 둔다.

---

## 5. VS Code엔 있지만 일부러 뺀 것 (제1원칙과 직결)

"기능 최소·인터페이스 단순"은 무엇을 뺐는지가 가장 잘 보여준다.

- Activity Bar의 뷰 전환 버튼(검색 / 소스 제어 / 실행·디버그 / 확장) — 없음. 탐색기 하나만.
- 하단 Panel(통합 터미널 / 문제 / 출력 / 디버그 콘솔) — 없음. 터미널은 3절대로 탭으로.
- Command Palette(`Ctrl+Shift+P`) — 없음.
- Breadcrumbs(탭 아래 경로 이동줄) — 없음.
- Minimap(편집기 오른쪽 축소 지도) — 없음.
- Secondary Side Bar(오른쪽 보조 사이드 바) — 없음.
- 설정/계정(Activity Bar 하단 아이콘) — 없음. 자리엔 테마 버튼만.

---

## 6. 정리 — "VS Code OSS를 참조한다"의 실제 대상

| 구분 | 요소 |
| --- | --- |
| 참조 O | Title Bar / Menu Bar · Activity Bar(축소형) · Primary Side Bar + Explorer 트리 · Editor Group과 Split Editor · Tab / Tab Bar · Status Bar · Color Theme |
| 참조 X (범위 밖) | Panel · Command Palette · Breadcrumbs · Minimap · Secondary Side Bar · SCM / 검색 / 디버그 / 확장 뷰 |

이 매핑은 BRIEF 완료 조건이 요구하는 "VS Code 동작과 채택 동작을 사람이 대조할 수
있는 기준 문서"의 재료다. 정식 기준 문서로 승격할 때 이 표가 뼈대가 될 수 있다.
