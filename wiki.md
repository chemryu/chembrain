# ChemBrain 진행 위키

## 현재 상태

**PAUSED — 사용자가 지정한 초기화 시각 이후 재개 요청 대기**

- 준비 기록 날짜: 2026-10-16
- 사용자 지정 시각 원문: 오늘 `7:43pm CST`
- 작업 방식: API 없이 Codex 안의 개별 GPT 에이전트
- 작업 원본: GitHub `chemryu/chembrain` / `codex/gpt-agent-workflow`
- 현재 소스 SHA: `5c1c15a920a6f50dc330366507597902c8a0ef64`
- 본 작업 재개: NOT RUN
- 새 다섯 역할 생성·가동: NOT RUN — 역할 지침만 준비
- 새 흐름의 최종 검수·승인: NOT RUN
- Windows Box 폴더: 사용하지 않음 — 자동 동기화 미구성
- 전달 가능 여부: **아니오 — 새 검수에서 발견한 미해결 문제가 있음**

## 2026-10-16 · 준비 기록

### 요청과 결정

사용자가 GitHub를 공용 작업 공간으로 제안하여 룰북·위키·역할 지침·검수 인계를 이 저장소에 저장합니다. Windows Box 경로에 직접 저장했다고 표현하지 않습니다.

기존의 OpenAI·Anthropic 외부 API 컨트롤러 대신, Planning / Development / Independent QA / Wiki / Revision의 GPT 역할을 사용합니다. Revision 결과를 Wiki가 회차별로 저장하고 Planning에 넘깁니다. 지적 0건과 필수 검사 통과가 함께 확인되면 사용자에게 결과를 전달합니다.

사용자 지정 시각 이전에는 새 프로그램 구현·추가 검수를 시작하지 않습니다. 이번 준비에서는 룰북·역할 지침·현재 상태만 작성했습니다. 앱 소스는 변경하지 않았습니다.

### 재개 전 확인된 문제

기존 GPT 검수 에이전트가 중단 전에 DOI 참조 편집 문제를 재현했습니다. DOI 전용 참조의 DOI를 빈 값으로 저장할 수 있어, 검토된 반응에 연결된 유일한 논문 링크가 사라질 수 있습니다. 아직 수정하지 않았습니다.

- 근거와 후속 작업: [초기 검수 인계](reviews/baseline-doi-finding.md)
- 관련 경로: `server/app.py`의 source metadata 갱신, `src/SourceMetadata.tsx`의 DOI 입력
- 다음 Planning 작업: DOI 필수 조건과 기존 인용의 일관성을 정하고, 수정·회귀 검사·독립 재검수를 계획

### 기존 증거의 범위

현재 SHA의 이전 Windows CI는 빌드·EXE 일반 실행·주요 UI·재실행 데이터 보존·런타임 PATH 분리를 통과했습니다. 이 결과는 위 DOI 문제 해결이나 새 Revision 승인 근거가 아닙니다. 깨끗한 Windows PC 검사와 사용자 기본 브라우저 연동 검사는 별도 미실행 항목입니다.

### 다음 순서

1. 사용자가 초기화 시각 이후 이 채팅에서 재개를 요청합니다.
2. Planning이 현재 요청과 위 미해결 문제를 읽습니다.
3. Development → Independent QA → Revision → Wiki → Planning의 회차를 실행합니다.
4. 종료 기준을 만족한 정확한 커밋과 검증 파일만 전달합니다.

## 기록 준비 변경

- `RULEBOOK.md`: 다섯 역할, 반복 순서, 종료 조건과 권한
- `agents/`: Planning / Development / Independent QA / Revision / Wiki 지침
- `requests/current.md`: 프로그램 요구사항과 재개 조건
- `reviews/baseline-doi-finding.md`: 중단 전에 재현된 DOI 문제
- `progress.json`: 기계가 읽을 수 있는 대기 상태
- 앱 코드 변경: 없음
