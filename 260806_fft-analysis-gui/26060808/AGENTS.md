# 프로젝트 운영 규칙

이 문서는 FFT ROI Analysis GUI 프로젝트의 운영과 변경 관리 규칙을 정의한다. 프로젝트 설명은 [README.md](README.md), 새 구현의 상세 기술 기준과 문서 색인은 [docs/README.md](docs/README.md)를 참조한다. 이전 구현 문서는 [refs/legacy2/docs/README.md](refs/legacy2/docs/README.md)에 보관한다.

## 문서 작성 규칙

- 이모지를 사용하지 않는다.
- Markdown 문서는 UTF-8 인코딩으로 작성하고 저장한다.
- 파일 저장 후 한글이 깨지지 않았는지 확인한다.
- 파일에 `U+FFFD` 대체 문자가 포함되지 않았는지 검사한다.
- 현재 확정된 기준과 향후 계획을 구분해서 작성한다.
- 동일한 규칙을 여러 canonical 문서에 중복 정의하지 않는다.

## 변경 작업 순서

1. 작업 전에 [README.md](README.md), [docs/README.md](docs/README.md)와 관련 설계 문서를 확인한다. 이전 구현과 관련되면 [refs/legacy2/docs/README.md](refs/legacy2/docs/README.md)를 추가로 확인한다.
2. 요구사항이나 설계가 바뀌면 코드보다 canonical 문서를 먼저 수정한다.
3. 구현 범위, 제외 범위와 인수 기준을 필요할 때 별도 plan에 기록한다.
4. 승인된 문서와 plan이 있으면 이를 기준으로 코드를 구현한다.
5. 관련 검증을 실행하고 기대값과 실제 결과를 확인한다.
6. 구현 결과에 맞게 문서와 plan 상태를 갱신한다.

## plan 문서 규칙

현재 새 구현에는 plan 문서를 두지 않는다. 구현 계획 문서가 필요해지면 경로, 번호, 상태와 구성 규칙을 새 `docs/README.md`에 먼저 정의한다.

## 변경 관리 규칙

- 사용자가 만든 파일과 변경 사항을 요청 범위 밖에서 수정하거나 삭제하지 않는다.
- `refs/legacy1/`과 `refs/legacy2/`는 참고 전용이며 런타임 dependency로 만들지 않는다.
- 경로, 파일명, 설정 key와 CSV column 이름은 코드와 canonical 문서에서 일치시킨다.
- GUI에서 사용자에게 표시하는 탭, 레이블, 버튼, 상태 및 오류 메시지는 영어로만 작성한다.
- 구현 세부 규칙을 이 문서에 추가하지 않고 `docs/README.md`의 해당 절을 수정한다.

## Python 코드 작성 규칙

`src/` 아래 모든 Python 코드는 다음 규칙을 따른다.

- 식별자, 주석, docstring, 문자열에 한국어를 사용하지 않는다.
- 세로 정렬을 위한 불필요한 공백을 넣지 않는다.
- 경로 처리는 `pathlib.Path` 대신 `os.path`를 사용한다.
- type hint를 사용하지 않는다.
- 모든 파일의 첫 줄은 `# path/from/project/root.py: one-line description` 형식으로 작성한다.
- 첫 줄 header 다음에 빈 줄 하나를 두고 import를 작성한다.
- class와 top-level function은 한 줄 docstring을 작성한다.
- method에는 docstring을 작성하지 않는다.
- 주석은 필요한 경우에만 최소한으로 작성한다.
- `src/` 아래 모든 폴더에는 빈 `__init__.py`를 둔다.
- `src/` 내부 import는 `src.xxx` 형식의 absolute import를 사용한다.

## 문서 참조

- [프로젝트 설명](README.md)
- [새 구현의 상세 기술 문서와 문서 색인](docs/README.md)
- [이전 구현의 상세 기술 문서와 문서 색인](refs/legacy2/docs/README.md)
