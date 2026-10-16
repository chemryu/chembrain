# GPT 전용 개발·검수

이 저장소에서 API 키 없이 Codex의 GPT 에이전트들을 나누어 개발과 검수를 진행합니다. 별도의 유료 API 컨트롤러나 Claude 연결을 사용하지 않습니다. 기존 `workflowkit/`은 이전 API 방식의 도구이며 현재 흐름에서는 실행할 필요가 없습니다.

## 역할과 기록

`Planning → Development → Independent QA → Revision → Wiki → Planning`

- [룰북](RULEBOOK.md): 권한과 회차·종료 기준
- [진행 위키](wiki.md): 현재 상태, 회차별 변경과 검수 결과
- [현재 요청](requests/current.md): 요구사항과 재개 조건
- [역할 지침](agents/): 다섯 GPT 역할 정의
- [초기 검수 인계](reviews/baseline-doi-finding.md): 재개 후 해결할 DOI 문제
- [진행 상태 JSON](progress.json): 구조화된 상태

Revision이 검수 결과를 대조한 뒤 Wiki가 이를 저장합니다. 남은 지적은 다음 Planning에 전달하고, 지적 0건과 필수 검사 통과가 확인되면 최종 파일·소스 SHA·파일 해시·검사 범위를 사용자에게 제시합니다. 실제 회차별 원문은 runs/<실행ID>/round-NN/에 남깁니다.

## 현재 대기 상태

요청한 룰북과 진행 기록만 저장했습니다. 다섯 역할의 새 개발·검수 회차와 프로그램 수정은 시작하지 않았습니다. 오늘 7:43pm CST 초기화 이후 사용자가 이 채팅에서 재개를 요청해야 시작합니다. 예약 실행 기능은 없습니다.

GitHub를 공용 기록 원본으로 사용합니다. 현재 세션은 Windows Box 폴더를 직접 갱신하거나 GitHub와 Box를 자동 동기화하지 않습니다. 사용자가 두 채팅 사이에 검수 결과를 옮길 필요는 없지만, GPT 역할들은 활성 Codex 작업 안에서만 실행됩니다. GitHub 파일 자체가 GPT를 상시 실행시키지는 않습니다.
