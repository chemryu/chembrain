# ChemBrain 진행 위키

## 현재 상태

**CHANGES_REQUESTED — 20261017-gpt-02 / round-01, 미해결 4건·round-02 Planning 인계**

- 날짜/시간대: 2026-10-17 (America/Chicago)
- 확정 범위: JACS 전체 논문, 주제 필터 없음, **서지정보 + OA PDF만**
- 추가 요구: 본문·SI 참조 카드를 정규화 논문 DOI별 하나로 묶고 locator·원래 evidence 보존
- 역할: round-01 Planning·Development·Independent QA·Revision·Wiki 기록 완료, 다음 round-02 Planning 대기
- 고정된 새 소스 SHA: `36fde22d2791475062565161bf986b88f035b2da` — 소스 브랜치에 푸시됨
- 회차 시작 기준 SHA: `3f102821649ff13b5581ebdff18274ef46602322` — 이전 승인은 신규 변경에 승계하지 않음
- 기록 원본: GitHub `codex/gpt-workflow-records`; 실행 소스 `codex/gpt-agent-workflow`
- 새 기능 QA·Revision 최종 결과: 둘 다 **CHANGES REQUESTED / 미해결 4건 / 전달 승인 없음**
- 정확한 SHA의 Windows CI: PENDING — 성공해도 이 소스의 검수 거절은 해소되지 않음
- 다음 Planning: [round-01 인계](runs/20261017-gpt-02/round-01/handoff.md)를 읽고 round-02 계획 작성
- 로컬 검사: Python 210 PASS / Windows 전용 DPAPI 1 SKIP, 프런트엔드·실제 브라우저·소스 시작/재실행 PASS
- 클라우드 공개 공급자 관찰: **UNAVAILABLE** (네트워크/DNS 제한) — 실제 다운로드 PASS가 아님
- 새 기능 전달 여부: **아니오**. 사용자 PC 예약 작업 설치: **아직 없음**
- Box 직접 저장·자동 동기화: 미구성. 기관 인증의 클라우드 이전·개인 외부 AI API 호출: 없음
- 이전 검수 후보 승인은 아래 기록과 기존 회차 보고서에 보존하며 신규 변경에 승계하지 않음

## 이전 실행 완료 상태 — 20261016-gpt-01

**READY_REVIEWED_CANDIDATE — 다섯 역할 완료, 남은 지적 0건**

- 실행 ID / 회차: `20261016-gpt-01` / `round-01`
- 기록 날짜: 2026-10-16 (America/Chicago)
- 최신 사용자 요청 원문: **“지금 바로 시작해줘”** — 이전 `7:43pm CST` 대기 해제
- 작업 방식: API 없이 현재 Codex 작업 안의 개별 GPT 에이전트
- 실행 소스 원본: GitHub `chemryu/chembrain` / `codex/gpt-agent-workflow`
- 진행 기록 원본: `codex/gpt-workflow-records` — 최초 게시 완료 (`4224102580de88e3d10fa679c2457502044a8434`)
- 고정된 검토 대상 소스 SHA: `3f102821649ff13b5581ebdff18274ef46602322`
- 역할 실행: Planning·Development·Independent QA·Revision·Wiki 모두 COMPLETE
- Independent QA / Revision: 동일 소스에 대해 각각 PASS, 남은 지적 **0건**
- 기존 DOI 지적: 독립 검증과 Revision에서 RESOLVED
- 필수 자동 검사: PASS — 로컬 Python 153 PASS / Windows 전용 1 SKIP, Windows Python 154 PASS / 0 SKIP, 프런트엔드·실제 UI·일반 시작·재실행·런타임 PATH 분리
- Windows 증거 원본: 불변 영수증 커밋 `0c6df260af7ef7a340cd2aff80415d4577c63bbf`
- 전달 가능 여부: **예 — 검수된 후보 파일에 한함**, 공개 Release 승인은 아님
- 다음 Planning 인계: **CLOSE / 추가 회차 없음** — [완료 인계](runs/20261016-gpt-01/round-01/handoff.md)
- 깨끗한 Windows PC / 사용자 기본 브라우저 통합: **NOT RUN** — 수동 확인 범위
- Windows Box 폴더: 직접 저장·자동 동기화 미구성

## round-01 · 검수 완료 및 사용자 전달

[Independent QA 전체 보고서](runs/20261016-gpt-01/round-01/qa.md)와 [Revision 전체 보고서](runs/20261016-gpt-01/round-01/revision.md)를 원문 그대로 보존했습니다. 두 역할은 위 고정 SHA에 대해 필수 자동 검사 PASS와 남은 지적 0건을 확인했습니다. Revision의 독립 추가 DOI 행렬 검사도 PASS입니다. 따라서 Wiki는 다음 Planning에 빈 수정 목록을 돌리지 않고 회차를 종료합니다.

| 전달 근거 | 내용 |
| --- | --- |
| Windows 후보 파일 | [GitHub Actions 다운로드](https://github.com/chemryu/chembrain/actions/runs/38978428660/artifacts/12080600552) |
| 내부 ZIP | `Chembrain-Windows-x64.zip` |
| 내부 ZIP SHA-256 | `ceacbc857ec919b45687f4108fe1394d8a4405643e592358e75cf942ba06b9c0` |
| 원본 영수증·검사 로그 | [windows/](runs/20261016-gpt-01/round-01/windows/) |
| 최종 인계 | [handoff.md](runs/20261016-gpt-01/round-01/handoff.md) |
| 기계 판독 전달 기록 | [delivery.json](runs/20261016-gpt-01/round-01/delivery.json) |

다운로드한 GitHub artifact ZIP을 풀고, 그 안의 `Chembrain-Windows-x64.zip`도 풉니다. `Chembrain.exe`를 더블클릭하면 됩니다. Python·Node.js 설치와 API 키가 필요하지 않으며, 앱 사용 중 실행 콘솔을 열어 둡니다. 사용자 데이터는 `%LOCALAPPDATA%\Chembrain`에 저장합니다.

SHA-256은 CI가 테스트한 EXE 패키지에 대해 생성하고 같은 artifact에 업로드한 값입니다. 이 세션은 불변 영수증·로그·체크섬을 확인했으며, 인증이 필요한 artifact를 별도로 내려받아 바이트를 재계산하지는 않았습니다. 전달은 위 artifact를 그대로 사용하며 다른 파일로 대체하거나 재압축하지 않습니다.

깨끗한 Windows VM 및 사용자의 실제 기본 브라우저 연동은 NOT RUN입니다. PATH 분리와 브라우저 요청 프로브/Chromium 렌더링 검사를 그 수동 검사 대신 통과했다고 표현하지 않습니다. 공개 Release·배포·권한 변경·Box 동기화·영구 실행 GPT·예약 실행을 수행하지 않았습니다. 이후 실행 소스가 바뀌면 새 SHA에 대해 필요한 검사와 두 독립 검토를 다시 수행합니다.

아래 내용은 각 단계 당시의 진행 기록으로 보존합니다.

## round-01 · 소스 고정 및 독립 검수 시작

Development가 실행 소스를 `3f102821649ff13b5581ebdff18274ef46602322`로 고정하고 `codex/gpt-agent-workflow`에 푸시했습니다. [Development 보고서](runs/20261016-gpt-01/round-01/development.md)에 변경 파일·이유·실행 명령을 보관합니다.

- Python 전체 로컬 검사: 153 PASS, 1 SKIP (Windows 전용 DPAPI)
- 프런트엔드 빌드: PASS
- 실제 Chromium UI: PASS — DOI 삭제 시도·거절·링크 유지 포함
- 소스 일반 시작 및 실제 재실행 데이터 보존: PASS
- 고정 SHA Windows CI: PENDING
- Independent QA: RUNNING, 최종 승인 없음
- Revision: NOT RUN

기존 DOI 문제는 **수정 구현 완료·독립 검증 대기**이며, Wiki가 해결을 대신 승인하지 않습니다. 이전 Windows SHA의 증거는 이번 커밋 통과 근거가 아닙니다. 깨끗한 Windows PC와 사용자 기본 브라우저 통합 검사는 여전히 NOT RUN입니다. 진행 기록 브랜치의 최초 게시도 아직 대기 중입니다.

## round-01 · 계획 확정 및 기록 분리

[Planning 보고서](runs/20261016-gpt-01/round-01/planning.md)가 작성되었으며 Development가 DOI 삭제 방지·UI 안내·회귀 검사를 구현하고 있습니다. 현재 소스 기준 SHA는 새 커밋이 확정되기 전의 시작 기준이며, 구현이 통과했다는 뜻이 아닙니다.

검토 대상 실행 소스는 `codex/gpt-agent-workflow`에 고정합니다. 최종 Independent QA·Revision·위키·진행 상태 기록은 별도 `codex/gpt-workflow-records` 브랜치에 저장해 동일한 전체 소스 SHA를 참조합니다. 아직 기록 브랜치의 최초 게시가 완료되지는 않았습니다. 앱이나 실행·빌드 입력이 바뀌면 새 SHA로 검수와 관련 검사를 반복하며, 문서 분리로 통과 기준을 낮추지 않습니다.

## 2026-10-16 · round-01 시작 기록

사용자가 **“지금 바로 시작해줘”**라고 명시해 이전 사용량 초기화 대기 요청을 해제했습니다. 이는 사용자 요청에 따른 즉시 재개이며 예약 실행이 아닙니다. 이전 요청과 준비 기록은 아래에 유지합니다.

`Planning → Development → Independent QA → Revision → Wiki → Planning` 흐름을 현재 Codex 작업 안에서 실행합니다. Planning과 Wiki는 별도 GPT 역할로 시작했으며, 주 에이전트가 Development와 조정을 담당합니다. Independent QA와 Revision은 구현·검사 증거가 준비된 뒤 각각 분리해서 실행합니다. 외부 개인 AI API 키나 API 호출을 사용하지 않습니다.

첫 계획의 입력은 [초기 DOI 검수 인계](reviews/baseline-doi-finding.md)입니다. 기록 시작 시점에는 앱 소스 변경·새 검수 승인·전달 파일이 없습니다. Wiki는 실제 보고서가 도착한 뒤 회차별 원문과 인계 내용을 저장하며, 실행하지 않은 검사를 통과로 기록하지 않습니다.

다음 작업: Planning 완료 기준 확정 → Development 수정·검사 → 정확한 커밋에 대한 Independent QA → Revision → Wiki 기록 및 다음 Planning 인계 또는 종료 판단.

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

## 2026-10-17 · 주간 논문 수집 기능 요청

**새 기능: PRELIMINARY / AWAITING_INPUT — NOT IMPLEMENTED**

사용자는 구독 접근권이 있는 PC에서 선택한 저널의 새 논문을 매주 내려받아 ChemBrain DB에 반영하는 기능을 요청했습니다. 저널명·관심 주제와 교내망/VPN·프록시·기관 로그인 등 접근 경로에 대한 답변을 기다립니다. 구독권만으로 모든 출판사의 무인 다운로드가 가능하다고 가정하지 않습니다.

[새 회차 Planning 초안](runs/20261017-gpt-02/round-01/planning.md)에 ISSN/Crossref·RSS 메타데이터 탐색과 DOI 중복 제거, source ID·사용자 편집을 보존하는 원자적 PDF 첨부, EXE `--sync-once`와 현재 사용자 Windows 작업 스케줄러, `NEEDS_LOGIN` 상태를 포함한 예비 구성을 기록했습니다. PDF는 로컬 보관하고 UI는 DOI 중심으로 유지하며, 일반 텍스트 후보에서 검수 완료 반응을 자동 생성하지 않습니다.

이전 앱의 **READY_REVIEWED_CANDIDATE**와 소스 `3f102821649ff13b5581ebdff18274ef46602322`에 대한 검수는 그대로 유지됩니다. 그 승인은 새 주간 수집 기능의 구현·인증·예약 실행을 포함하지 않습니다. 이번 요청으로 코드를 변경하거나 논문을 다운로드하거나 PC에 예약 작업을 설치하지 않았으며, 기관 인증을 클라우드에 이전하지 않았습니다. 확정 구현 계획은 사용자 입력과 지원 접근 경로 확인 이후 작성합니다.

## 2026-10-17 · 입력 확정 및 구현 착수

사용자가 **JACS 전체 논문, 주제 제한 없음, 서지정보와 OA PDF만**으로 범위를 확정했습니다. 캠퍼스 네트워크/VPN 구독 접근권이 있더라도 비공개 PDF 수집으로 범위를 확장하지 않습니다. 본문·SI가 같은 논문이면 반응 참조 카드를 정규화 DOI별 하나로 묶되, underlying evidence와 모든 locator를 보존하는 요구도 추가되었습니다.

Planning이 최종 계획을 작성하고 Development가 수집기·UI 보조 에이전트와 구현을 시작합니다. 보조 에이전트는 Development 역할이며 독립 QA를 대신하지 않습니다. 별도 Independent QA와 Revision은 구현·정확한 SHA의 증거 준비 후 수행합니다. 현재 새 기능은 미검증·미전달이며 사용자 PC에 스케줄을 설치하거나 Box에 직접 기록하지 않았습니다. 이전 실행의 승인·SHA·영수증은 역사로 보존합니다.

## 2026-10-17 · gpt-02 소스 고정 및 독립 검수 시작

Development가 새 실행 소스를 `36fde22d2791475062565161bf986b88f035b2da`로 고정·푸시했습니다. [Development 원문](runs/20261017-gpt-02/round-01/development.md)에 구현·명령·검사·제한을 보존합니다. Planning과 구현·로컬 검사는 완료했으며 Independent QA 및 Revision의 사전 검토가 진행 중입니다. Windows CI는 이 정확한 SHA의 결과를 기다리고 있습니다.

로컬 전체 Python 검사는 210 PASS와 Windows 전용 DPAPI 1 SKIP, 프런트엔드 빌드·실제 Chromium·일반 시작과 실제 재실행 저장 유지는 PASS입니다. 이는 Windows 결과나 두 독립 최종 승인을 대신하지 않습니다. 공개 공급자 직접 관찰은 네트워크/DNS 제한으로 **UNAVAILABLE**이며 실제 공개 PDF 수집 성공으로 기록하지 않습니다. Windows 관찰과 원본 증거는 별도로 확인합니다.

새 기능은 아직 검수 완료·전달 상태가 아닙니다. 사용자 PC의 수집/예약 작업 설치·기관 인증 이전·Box 직접 기록·개인 외부 AI API 호출을 수행하지 않았습니다. 깨끗한 Windows VM·실제 기본 브라우저 검사는 계속 NOT RUN입니다. 기존 검수 회차의 승인과 모든 SHA/영수증은 보존하지만 새 소스 검수에 전용하지 않습니다.

## 2026-10-17 · gpt-02 round-01 검수 거절 및 Planning 환류

[QA 원문](runs/20261017-gpt-02/round-01/qa.md)과 [Revision 원문](runs/20261017-gpt-02/round-01/revision.md)은 모두 소스 `36fde22d2791475062565161bf986b88f035b2da`에 대해 **CHANGES REQUESTED**, 미해결 **4건**을 기록했습니다. Wiki는 두 원문을 그대로 보존하고 [수정 작업 인계](runs/20261017-gpt-02/round-01/handoff.md)를 작성해 **round-02 Planning**으로 넘깁니다.

1. **HIGH:** 같은 출판사 리다이렉트가 다른 논문/경로로 이동해도 원래 DOI와 라이선스로 PDF가 첨부될 수 있음.
2. **MEDIUM:** 검증에 사용한 라이선스 유효일·버전·제공 PDF 링크 및 Crossref type이 provenance에서 누락됨.
3. **MEDIUM:** PDF 바이트 제한 외 최대 페이지 수가 없어 매우 큰 페이지 문서를 허용함.
4. **MEDIUM:** 기존 DOI 중복 기록을 보존하지만 중복 개수·source ID를 사용자 상태에 알리지 않음.

이 후보의 전달 승인은 없습니다. 기존 검사 PASS나 이후 Windows CI 성공은 네 지적의 수정을 대신하지 않습니다. 다음 회차에서는 수정된 새 SHA에 대해 필수 검사와 QA·Revision을 다시 수행하며, OA 한정·기존 데이터 보존·실제 공급자 UNAVAILABLE 등 범위와 한계를 유지합니다.
