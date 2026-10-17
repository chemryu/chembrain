# Wiki → Planning 인계 — 20261017-web-03 / round-02

- 소스: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`.
- 최종 QA·Revision: **CHANGES REQUESTED / 신규 MEDIUM 1건 WEB-QA-05 / WEB-REV-05**.
- 이전 네 지적: 두 독립 역할에서 **모두 RESOLVED**. 다시 열지 않습니다.
- 별도 hosting: **BLOCKED_EXTERNAL_PAGES_CONFIGURATION**, 실제 새 Pages 403. 전달 승인·검증된 URL 없음.
- 다음 단계: **round-03 Planning**, metadata output/progress 및 CI feed/state의 내구성 순서만 보완합니다.
- [QA 원문](qa.md)과 [Revision 원문](revision.md)을 그대로 보존했습니다. root가 이 인계를 records 브랜치에 게시합니다; 현재 최종 게시 SHA는 아직 미확정입니다.

## 신규 한 문제: bibliography보다 진행 상태가 먼저 durable해짐

`weekly`가 최종 normalized output 전에 `last_success`와 모든 page resume cursor를 씁니다. output에만 OSError를 주면 예전 output은 보존되지만 metadata 상태는 앞서가므로, 다음 주 date window가 이동하거나 두 번째 cursor에서 재개할 때 발견했던 bibliography-only DOI를 잃습니다. PDF pending queue가 없는 비OA 서지정보도 영향을 받습니다.

QA는 완료 window 실패/다음 주 누락을 독립 재현했고 Revision은 101건 중 첫 100건 뒤 cursor를 저장한 다음 output 실패 → 다음 page의 한 건만 export되는 변형도 재현했습니다. 이는 하나의 순서 결함입니다. CI에서도 `build/paper-state`가 `public/library.json` commit/push보다 먼저 저장돼 feed publication 실패/취소 때 같은 불일치가 생길 수 있습니다. CI failure는 source inspection 결과이며 이번 push에서 live collection 실패를 관찰한 것으로 표현하지 않습니다.

## round-03 수정·검증 계약

1. 모든 metadata 완료 checkpoint와 page cursor는 해당 bibliography가 normalized output 또는 재생 가능한 durable bibliography에 기록된 뒤에만 진행합니다. `last_success`만 고치고 중간 cursor 쓰기를 남기지 않습니다. output 검증/쓰기 실패 시 원래 package와 원래 metadata 진행을 보존해 전체 DOI를 재발견할 수 있어야 합니다.
2. output 성공 뒤 state 쓰기가 실패하면 오래된 cursor로 idempotent replay해도 모든 DOI가 정확히 한 번 유지돼야 합니다. 독립 PDF pending work·OA 재검증·attempt cap·기존 파일 재사용·이전 네 해결 계약은 유지합니다.
3. CI remote progress는 대응하는 normalized feed commit/push가 성공해 origin이 인정한 뒤에만 저장합니다. 로컬 B commit이나 best-effort cache만으로 상태를 앞당기지 않습니다. root가 제시한 fail-closed save guard 계약은 feed ref, origin-acknowledged commit, exact library SHA-256을 대조하고, unpublished B는 원격 state를 진행시키지 않으며 실제 pushed B만 허용하는 경로입니다. feed push 실패/취소 시 이전 remote state와 재시도 데이터를 보존합니다.
4. 실제 회귀: 완료 window output 실패+더 늦은 날짜 재시도, capped multi-page output 실패+즉시 재시도, output 이후 state-write 실패, cache/state 복원, 실제 임시 Git remote의 unpublished/pushed B 및 잘못된 feed ref/hash 거절을 검사합니다. 모든 발견 DOI가 eventually 정확히 한 번 포함되고 기존 반응/사용자 필드가 그대로인지 확인합니다.

범위를 publisher/authentication·schema/UI 재설계로 넓히지 않고 새 전체 소스를 고정해 관련 전체 검사·정확한 web CI·두 독립 판단을 반복합니다. preliminary zero-finding 초안은 최종 새 finding 보고서로 대체됐으며 승인으로 남기지 않습니다.

## 정확한 CI와 별도 외부 단계

불변 영수증 `4fb229121ebd4597c51bae7dec30cf37dc759d61`, [manifest](web/manifest.json), [실행 39063636131](https://github.com/chemryu/chembrain/actions/runs/39063636131)은 동일 소스의 **253 PASS / Windows 전용 1 SKIP**, web build·실제 browser PASS를 기록합니다. workflow/built commit `d423c718ca3c0b7d1dd090a362ba02990d7e223a`, library SHA-256 `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c`가 terminal에도 보존됩니다.

새 실제 Pages 설정은 **403 Resource not accessible by integration**, deployment/public HTTPS는 **SKIPPED / NOT RUN**, URL null입니다. 소유자 Pages Source 응답 대기는 별도이며 green build나 코드 수정을 외부 hosting 해결로 바꾸지 않습니다. 실제 게시·source/data identity 응답 없이 접근 가능한 preview로 전달하지 않습니다.

Dispatcher는 여전히 fail-closed 미설정 artifact·미설치이며 주간 운영 미활성, 사용자 PC 작업 미설치입니다. raw PDF/review cache는 best effort이고 durable branch는 공개 DOI/queue/checkpoint whitelist만 보존합니다. 기존 draft 사실·과학 unknown·브라우저 로컬 데이터·Box/기관 인증/개인 AI API 미사용 이력을 유지합니다.
