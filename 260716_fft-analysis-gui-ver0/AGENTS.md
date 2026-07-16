# 프로젝트 운영 규칙

이 문서는 FFT ROI 분석 GUI 프로젝트의 운영과 변경 관리 규칙을 정의한다. 프로젝트 설명은 [README.md](README.md), 상세 기술 기준은 [docs/README.md](docs/README.md)를 참조한다.

@C:\Users\wonhee.nam\.codex\RTK.md

## 문서 작성 절대 규칙

- 이모지를 사용하지 않는다.
- Markdown 문서는 UTF-8 인코딩으로 작성하고 저장한다.
- 파일 저장 후 한글이 깨지지 않았는지 확인한다.
- 파일에 `U+FFFD` 대체 문자가 포함되지 않았는지 검사한다.
- 현재 확정된 기준과 향후 계획을 구분해서 작성한다.
- 동일한 규칙을 여러 canonical 문서에 중복 정의하지 않는다.

## 명령 실행 규칙

- `C:\Users\wonhee.nam\.codex\RTK.md`에 따라 가능한 shell 명령은 `rtk`를 prefix로 사용한다.
- RTK가 설치되지 않았거나 실행 연결 오류로 사용할 수 없으면 문제를 먼저 알리고 작업에 필요한 최소 범위에서만 기본 명령을 사용한다.
- 개발 환경, 테스트와 배포 명령은 [상세 기술 문서](docs/README.md)에 정의된 기준을 따른다.

## 변경 작업 순서

1. 작업 전에 [상세 기술 문서](docs/README.md)와 관련 plan을 확인한다.
2. 요구사항이나 설계가 바뀌면 코드보다 canonical 문서를 먼저 수정한다.
3. 구현 범위, 제외 범위와 인수 기준을 plan에 기록한다.
4. 승인된 문서와 plan을 기준으로 코드를 구현한다.
5. 관련 검증을 실행하고 기대값과 실제 결과를 확인한다.
6. 구현 결과에 맞게 문서와 plan 상태를 갱신한다.

계획 문서는 `docs/development/plans/NNNN-topic-plan.md` 형식을 사용한다. 현재 문서 구조 계획은 [0001-documentation-structure-plan.md](docs/development/plans/0001-documentation-structure-plan.md)를 참조한다.

## 변경 관리 규칙

- 사용자가 만든 파일과 변경 사항을 요청 범위 밖에서 수정하거나 삭제하지 않는다.
- 인접 프로젝트는 참고와 검증에만 사용하고 런타임 dependency로 만들지 않는다.
- 경로, 파일명, 설정 key와 CSV column 이름은 코드와 canonical 문서에서 일치시킨다.
- 구현 세부 규칙을 이 문서에 추가하지 않고 `docs/README.md`의 해당 절을 수정한다.
- 향후 상세 문서가 분리되면 `docs/README.md`를 색인으로 사용하고 세부 규칙의 canonical 위치를 하나로 유지한다.

## 문서 참조

- [프로젝트 설명](README.md)
- [상세 기술 문서와 문서 색인](docs/README.md)
- [문서 구조 및 작성 계획](docs/development/plans/0001-documentation-structure-plan.md)
