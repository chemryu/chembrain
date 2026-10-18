# Wiki 진행 기록 — 20261017-web-03 / round-03

- 날짜/시간대: 2026-10-17 (America/Chicago); 사용자 재개 이벤트 `2026-10-18T03:21:05.438839+00:00`.
- 고정·푸시된 소스: **`56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`**; 이전 거절 소스 `d423c718ca3c0b7d1dd090a362ba02990d7e223a`.
- 상태: **EXACT_SOURCE_INDEPENDENT_REVIEW_AND_CI_PENDING**. 최종 독립 승인·공개 접근 검증 없음.

## 재개 및 역할 순서

사용자 “이어서 진행해줘”가 이전 새벽 초기화 이후 대기 요청을 해제했습니다. [RESUME 체크포인트](../RESUME.md)는 당시 일시중지 이력 그대로 보존하며 현재 대기 지시로 해석하지 않습니다. 자동 예약/배경 에이전트가 재개한 것이 아닙니다. 실제 사용량 초기화 시각을 새로 확인했다고 주장하지 않습니다.

round-02 [QA](../round-02/qa.md) → [Revision](../round-02/revision.md) → [Wiki 인계](../round-02/handoff.md)는 기록 커밋 `b9285eca83cb4dc5128b9ef00f146fb43675bd88`에 게시되었습니다. 별도 Planning이 이를 읽고 [round-03 계획 및 pre-freeze clarification](planning.md)을 구현 전에 확정했습니다. root와 별도 Development helper가 [개발 기록](development.md)에 실제 수정과 검사를 기록했습니다. 보조 역할은 Development이며 Independent QA를 대신하지 않습니다.

## 구현 보고와 검증 경계

Development는 같은 WEB-QA-05/WEB-REV-05 경계에 대해 모든 advancing metadata cursor/checkpoint 쓰기를 normalized output의 검증·atomic replacement 뒤로 옮기고, 첫 실행의 nonadvancing replay anchor 및 기존 checkpoint의 고정 fourteen-day replay lower bound를 구현했습니다. CI는 authoritative state 복원 → origin이 인정한 feed A에 bootstrap anchor 저장 → 발견/normalized feed B publish → exact ref/commit/library SHA-256 검증 후 advanced state 저장 순서입니다. 실제 `paper_state.save`가 미게시 B·잘못된 ref/hash·stale acknowledgment를 거절합니다.

구현 측 증거는 Python **273 PASS / Windows 전용 DPAPI 1 SKIP**, production repository-subpath `build:web` PASS, 실제 Chromium PASS(기존 malformed editor 42종·Python export→import·저장/재시작/backup/mobile/subpath 포함), processor 내구성 집중 **34 PASS**, 임시 실제 Git remote를 사용한 feed/state provenance·cache eviction replay 검사 및 YAML/diff PASS입니다. 이전 네 지적과 초기 화면/영어 UI/DOI grouping/3논문·12초안 사실은 유지합니다.

현재 지적 상태는 **IMPLEMENTED_AWAITING_EXACT_SOURCE_INDEPENDENT_VERIFICATION**입니다. 같은 새 SHA를 별도 Independent QA와 Revision이 검토 중이며 아직 최종 원문이 없습니다. Wiki는 개발 검사나 과거 승인으로 RESOLVED/APPROVED를 만들지 않습니다.

## 외부 증거와 활성화 한계

이 새 소스의 GitHub CI 영수증은 대기 중입니다. 이전 d423의 실제 Pages 403 `Resource not accessible by integration`과 NOT RUN deployment/HTTPS는 이력으로만 보존하며 새 SHA 결과로 가정하지 않습니다. 소유자 Pages Source 설정 답변도 별도로 대기합니다. 실제 공개 HTTPS에서 정확한 workflow/built-data SHA와 library digest가 확인될 때까지 live URL을 주장하지 않습니다.

`build/paper-state`는 공개 DOI/queue/checkpoint whitelist metadata만 내구 보관하며 PDF·private review bytes를 포함하지 않습니다. Raw archive/review Actions cache는 best effort이며 영구 원문 보관이 아닙니다. dispatcher는 fail-closed 미설정 검토 artifact이고 default branch 미설치·주간 비활성, 사용자 PC 작업 미설치입니다. UI/과학 draft/unknown 및 browser-local 개인 편집 한계를 유지합니다. Box 직접 저장·동기화, 기관 인증 이전, 개인 모델 API 호출, background GPT service, main 병합·production 승인을 수행했다고 기록하지 않습니다.

다음 Wiki 단계는 QA·Revision 전체 원문과 새 source-bound CI 로그/manifest를 보존한 뒤 실제 지적과 외부 차단에 따라 최종 handoff를 작성하는 것입니다. 현재 handoff/종료 승인은 작성하지 않습니다.

## 새 정확한 CI 영수증 수신 — 최종 독립 원문 대기

불변 영수증 `5829825cf51ea5a5677922886eb1c8575405822e`, [manifest](web/manifest.json), [실행39093753253](https://github.com/chemryu/chembrain/actions/runs/39093753253)을 확인했습니다. 여섯 원본 파일의 바이트·SHA-256이 영수증 Git object와 일치함을 Wiki가 직접 확인했습니다. 동일 source/workflow/built commit은 `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`, library SHA-256은 `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c`입니다. GitHub의 Python **273 PASS / Windows 전용 1 SKIP**, web build·실제 browser PASS입니다. 이번 push에서 live collection은 SKIPPED이며 실제 공개 공급자 수집 성공을 주장하지 않습니다.

새 실제 Pages 설정은 **403 Resource not accessible by integration**입니다. Deployment/access 단계는 SKIPPED, 공개 HTTPS/source-data identity 검사는 NOT RUN, `page_url:null`입니다. 소유자 Source 설정 응답은 여전히 별도 대기이며 이전 SHA 결과를 이번 결과로 가정한 것이 아닙니다. QA는 로컬 코드 지적0 초안을 작성했지만 receipt를 반영한 최종 원문 및 Revision 최종 원문이 아직 대기 중이므로 Wiki는 종료/전달 승인을 기록하지 않습니다.

## 최종 독립 검수와 Wiki 인계

[QA 최종 원문](qa.md)과 [Revision 최종 원문](revision.md)을 읽고 그대로 보존했습니다. 두 역할 모두 소스 `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`에서 **PASS / 미해결 코드 지적0건**, WEB-QA-05/WEB-REV-05 **RESOLVED**입니다. QA는 독자적인 실제 Git 원격·두 저널202 DOI·output 실패·feed push 거절·cache 전부 소실·November replay 복구 시나리오를 PASS로 보고했습니다. Revision은 관련38tests 및 실제 competing state update에서 force-with-lease가 stale run을 거절하는 독립 CAS race를 PASS로 보고했습니다. QA의202 DOI fixture를 Revision이 다시 실행한 것으로 쓰지 않습니다.

원문 보존 SHA-256은 QA `a2573faa18859c80e889709f7c0dd58f7cc536e7a6e379928391ce24e458ff4c`, Revision `705b27850569f6a8898512bc74e09f34470343996963114ec12b1783bb0e3bda`입니다. 두 최종 보고서는 Wiki가 수정하지 않았습니다. 두 역할의 코드 판정과 정확한 CI 증거는 일치하지만 **전체 공개 미리보기 전달은 BLOCKED_EXTERNAL_PAGES_CONFIGURATION**입니다. 새 실제403, 배포/HTTPS NOT RUN, URL null을 유지합니다. 새 코드 수정 목록이 없으므로 빈 Planning 회차나 추가 구현을 만들지 않고 [최종 handoff](handoff.md)에 소유자 설정과 실제 배포/접속 증거만 남깁니다. 설정/소스가 바뀌면 증거의 적용 범위를 다시 확인하며 소스/build input 변경은 새 SHA 검수 대상입니다.

root는 추가 read-only 환경 점검에서 local static server의 subpath HTML/library startup을 확인하고 자체 server를 종료했습니다. cloud 환경 start skill과 정확한 단일 저장소/source `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae` 설정은 draft `cecfgdraft_6ad284a0831c8191890e572d9068e6ba`에 저장됐으며 `requires_publish:true`입니다. 기존 install script/network/secrets는 변경하지 않았다고 보고했습니다. draft save는 미래 runtime publish 또는 Pages 공개와 다르며 이 관찰을 앱의 별도 승인 gate로 만들지 않습니다.
