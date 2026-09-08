# cv-batch-runner 전체 구조

## 문서 목적

이 문서는 현재까지 확인된 사용자 흐름을 기준으로 UI dashboard, batch JSON, terminal launcher, batch runner, 개별 CLI job과 결과 폴더의 관계를 나타낸다. 세부 interface와 JSON field는 이후 `SPEC.md`에서 확정한다.

AI agent는 이 구조에 포함되지 않는다. 사용자 또는 UI가 실행을 시작하면 runner가 JSON과 CLI process 결과만으로 전체 batch를 진행한다.

## 전체 구조

```mermaid
flowchart TB
    subgraph UI["UI 계층"]
        CatalogView["구성요소 catalog 조회<br/>dataset, task, model, backbone, parameter"]
        Dashboard["테이블 dashboard<br/>조건 필터링 및 행 선택"]
        RunButton["실행 버튼"]
        StatusView["상태 표시<br/>미진행, 진행 중, 완료, 실패"]

        CatalogView --> Dashboard
        Dashboard --> RunButton
    end

    subgraph Contract["공유 계약"]
        Catalog["구성요소 metadata와<br/>호환성 정보"]
        BatchJson["batch.json<br/>job 정의, 순서, 진행 상태,<br/>결과와 log 경로"]
        JobSpec["공통 JobSpec<br/>한 job은 한 CLI command"]
    end

    subgraph Execution["실행 계층"]
        Launcher["terminal launcher"]
        Terminal["사용자에게 보이는<br/>하나의 terminal"]
        Cli["cv-batch-runner CLI<br/>검증, 조회, 실행"]
        Runner["batch runner"]
        Queue["순차 job executor"]
        Command["개별 CLI command<br/>train, evaluate, predict"]

        Launcher --> Terminal
        Terminal --> Cli
        Cli --> Runner
        Runner --> Queue
        Queue --> Command
        Command -->|"종료 상태 반환"| Runner
        Runner -->|"다음 job"| Queue
    end

    subgraph Results["job별 결과 저장"]
        JobDir["results / batch-id / job-id"]
        LogFile["job log"]
        Artifacts["학습, 평가, 추론 결과물"]
        Resolved["실행에 사용한 resolved 설정"]

        JobDir --> LogFile
        JobDir --> Artifacts
        JobDir --> Resolved
    end

    Catalog --> CatalogView
    Dashboard -->|"선택한 행 저장"| BatchJson
    RunButton -->|"batch.json 경로 전달"| Launcher
    BatchJson -->|"읽기 및 검증"| Cli
    BatchJson -->|"현재 상태 읽기"| StatusView
    Runner -->|"검증 후 안전한 상태 갱신"| BatchJson
    Queue --> JobSpec
    JobSpec --> Command
    Command --> JobDir
    JobDir -->|"결과와 log 경로"| BatchJson
    Runner -->|"전체 실행 요약 출력"| Terminal
    Terminal --> KeepOpen["사용자가 확인할 때까지 유지"]
    KeepOpen --> UserClose["사용자가 terminal 종료"]
```

## batch 실행 흐름

```mermaid
flowchart TD
    Start["UI에서 실행 선택"] --> Save["선택한 행을 batch.json으로 저장"]
    Save --> Launch["보이는 terminal 실행"]
    Launch --> Validate["batch.json 검증"]
    Validate --> Next{"미진행 job이 있는가"}
    Next -->|"예"| Running["해당 job을 진행 중으로 기록"]
    Running --> Execute["한 개의 CLI command 실행"]
    Execute --> Result{"CLI 실행 결과"}
    Result -->|"성공"| Success["결과 폴더 저장 및 완료 기록"]
    Result -->|"실패"| Failure["오류 log 저장 및 실패 기록"]
    Success --> Persist["batch.json 갱신"]
    Failure --> Persist
    Persist --> Next
    Next -->|"아니요"| Summary["전체 batch 완료 상태 출력"]
    Summary --> Wait["terminal 열린 상태 유지"]
    Wait --> Close["사용자가 확인 후 terminal 종료"]
```

## job과 결과의 대응

```mermaid
flowchart LR
    Row["dashboard의 선택 행"] --> JsonJob["batch.json의 job 한 건"]
    JsonJob --> Cli["CLI command 한 건"]
    Cli --> ResultDir["job 결과 폴더 한 개"]
    ResultDir --> Log["log 파일"]
    ResultDir --> Output["action별 결과물"]
```

하나의 조건에서 train, evaluate, predict를 모두 실행하면 세 개의 job 행과 세 개의 CLI command로 표현한다. 각 job은 다른 job의 성공 여부와 관계없이 자신의 상태와 결과 폴더를 가진다.

## 상태 정보의 소유권

권장 구조에서는 batch runner만 `batch.json`의 진행 상태를 변경하고 UI dashboard는 이를 읽어 표시한다. 같은 파일을 동시에 읽는 동안 불완전한 JSON이 노출되지 않도록 실제 구현에서는 안전한 파일 갱신 방법을 정해야 한다.

terminal 출력은 사용자가 실시간으로 진행 상황을 확인하는 수단이다. dashboard의 상태는 terminal 문자열을 분석하지 않고 `batch.json`에 기록된 job 상태를 기준으로 표시한다.

## 참조 근거

기존 프로젝트의 train, evaluate, predict, batch와 logging 구조에서 확인한 내용은 [previous-project-execution.md](previous-project-execution.md)에 기록했다.

terminal 하나에서 parent runner와 child job을 실행하고 JSON 상태를 기록하는 주체는 [process-and-state-ownership.md](process-and-state-ownership.md)에 정리했다.
