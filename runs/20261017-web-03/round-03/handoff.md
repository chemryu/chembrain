# Wiki 최종 인계 — 20261017-web-03 / round-03

- 정확한 검수 소스: **`56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`**, 실행 브랜치 `codex/gpt-agent-workflow`.
- [Independent QA](qa.md)와 [Revision](revision.md): **PASS / 미해결 코드 지적0건**. WEB-QA-05/WEB-REV-05 RESOLVED, 이전 네 해결 계약 유지. 두 원문을 수정 없이 보존했습니다.
- 전체 사용자 전달: **BLOCKED_EXTERNAL_PAGES_CONFIGURATION**. 코드 검수 통과만으로 인터넷에서 열리는 미리보기 전달을 완료했다고 표시하지 않습니다.

## 코드 회차의 결과

[Planning](planning.md) → [Development](development.md) → 별도 QA → 별도 Revision → [Wiki 기록](wiki-record.md) 순서를 마쳤습니다. 모든 advancing metadata cursor/checkpoint는 normalized output atomic write 뒤로 옮겼고, first-run nonadvancing anchor·고정 checkpoint lookback이 늦은 재시도에도 window를 보존합니다. CI는 origin이 인정한 feed A에 bootstrap state를 먼저 묶고, feed B publish 이후에만 그 정확한 ref/commit/library digest를 검증해 진행 상태를 저장합니다. 독립 실패/복구 및 경쟁 push 검사가 해결을 확인했습니다.

새 코드 지적이 없으므로 다음 Planning에 보낼 코드 수정 목록은 없습니다. 현재 소스를 계속 고정하고 외부 게시 단계가 열릴 때까지 앱 변경을 반복하지 않습니다. 이후 app/test/build input이 바뀌면 새 전체 SHA와 영향받는 검사 및 두 독립 검수가 필요합니다.

## 실제 CI와 남은 외부 조치

불변 영수증 **`5829825cf51ea5a5677922886eb1c8575405822e`**, [manifest](web/manifest.json), [GitHub run39093753253](https://github.com/chemryu/chembrain/actions/runs/39093753253)은 정확한 workflow/built commit `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`, library SHA-256 `25e98df9810b686e9da2c3c3b3f7f5da627dd2186ab3b00533b28d34072aef8c`를 보존합니다. 여섯 원본 파일의 바이트/해시를 QA·Revision·Wiki가 각각 확인했습니다. Python **273 PASS / Windows 전용1 SKIP**, production web build·실제 Chromium PASS입니다. 이번 push는 live collection/feed 단계를 SKIP했으며 주간 수집 실행이 활성화된 증거가 아닙니다.

새 실제 Pages configuration은 **HTTP403 `Resource not accessible by integration`**입니다. deployment/access는 SKIPPED, 공개 HTTPS 및 source/data/digest 검사는 NOT RUN, URL은 null입니다. 이전 실패를 이번 결과로 가정한 것이 아닙니다.

1. 소유자가 [저장소 Pages 설정](https://github.com/chemryu/chembrain/settings/pages)의 Source 상태를 확인해 전달해야 합니다. root의 관련 질문은 대기 중입니다. 사용자 명시 미리보기 게시 권한은 이미 있으나 실제 플랫폼 설정 차단을 우회하지 않습니다.
2. 설정이 해결되면 검수한 같은 소스에 대해 실제 게시를 실행하고, terminal receipt와 실제 HTTPS 응답의 workflow SHA·built-data SHA·library digest를 확인해야 합니다. 성공한 실제 URL만 전달합니다. 단순 green build나 예상 URL은 공개 접속 증거가 아닙니다.
3. 코드 검수통과는 production release·main 병합·default branch 변경·설정 우회·예약 작업 활성화를 승인하지 않습니다.

## 운영 범위와 보관

세 논문/열두 draft 반응, 과학 unknown, 영어 molecule-first 화면과 처음 빈 반응 패널, DOI별 한 참조 카드/locator 보존, browser-local 개인 편집과 compact backup을 유지합니다. 완전한 reaction extraction·SI검수·stereochemical 검증이나 모든 publisher OA 수집을 주장하지 않습니다.

주간 dispatcher는 fail-closed 미설정 검토 artifact이며 default branch 미설치·주간 비활성, 사용자 PC task도 미설치입니다. 공개 state branch는 whitelist DOI/queue/checkpoint metadata만 담고 private PDF/review는 별도 local workdir 또는 best-effort Actions cache에 있습니다. Git은 영구 PDF archive가 아닙니다. Box 직접 저장/동기화·기관 인증 이전·개인 AI API·상시 GPT service는 수행하지 않았습니다.

cloud 환경 start skill/단일 저장소 설정은 별도 draft로 저장됐고 runtime publish가 필요합니다. 이는 Pages 게시나 앱 승인과 같은 작업이 아닙니다. 이전 pause/RESUME와 모든 거절/차단/승인 이력은 역사로 보존했으며 이번 사용자 “이어서 진행해줘”가 즉시 재개를 허용했습니다. 자동 예약 재개는 없었습니다.

## 원문 무결성

- QA SHA-256: `a2573faa18859c80e889709f7c0dd58f7cc536e7a6e379928391ce24e458ff4c`.
- Revision SHA-256: `705b27850569f6a8898512bc74e09f34470343996963114ec12b1783bb0e3bda`.

원문/위키/진행 상태의 GitHub records branch 게시와 최종 source HEAD 확인은 root가 수행합니다. Wiki는 source 수정·commit·push·권한 변경·배포를 수행하지 않았습니다.
