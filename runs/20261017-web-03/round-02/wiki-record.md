# Wiki 진행 기록 — 20261017-web-03 / round-02

- 날짜/시간대: 2026-10-17 (America/Chicago).
- 고정·푸시된 소스: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`; 이전 거절 소스 `e424b34653fb96b911f5ee5708286c92baddfe5f`.
- 상태: **INDEPENDENT_REVIEW_AND_PAGES_CI_PENDING**, 최종 독립 승인·공개 접근 검증 없음.

round-01 QA·Revision → Wiki 인계는 기록 커밋 `128c3fca84fbc222043c5aaaddcc126bcc62c172`에 먼저 게시됐고, 그 뒤 별도 Planning이 [round-02 계획](planning.md)을 작성했습니다. Development는 [전체 구현 기록](development.md), [editor](development-editor.md), [contract](development-contract.md), [queue](development-queue.md) 세 보조 기록을 보관했습니다. 보조 역할은 Development이며 Independent QA를 대신하지 않습니다.

Development는 malformed editor 안전 처리, portable v1 계약 parity, durable eligible DOI 재시도, trigger/code와 실제 built-data identity 전달을 구현했다고 보고했습니다. 네 지적의 상태는 **구현 완료·독립 검증 대기**이며 Development의 주장만으로 RESOLVED로 올리지 않습니다. 별도 QA·Revision이 새 전체 SHA를 검토 중입니다.

구현 측 실제 증거는 Python **253 PASS / Windows 전용 DPAPI 1 SKIP**, build:web PASS, 실제 Chromium PASS(42 malformed editor shape·수정/취소/기존 저장 보존, Python export→browser import 포함), portable corpus 195개·queue 17 tests 및 Git 상태/provenance 검사 PASS입니다. 새 소스의 CI 영수증은 대기 중입니다.

`build/paper-state`의 내구성 대상은 공개 DOI/재시도/체크포인트 등 whitelist metadata뿐이며 PDF·private review bytes를 기록하지 않습니다. Raw PDF/review의 Actions cache는 best effort이고 영구 문서 보관을 보장하지 않습니다. 장기 원문 보관에는 별도 지속 local 저장이 필요합니다. Pages에는 정규화 데이터만 전달합니다.

이전 e424 실행의 Pages 403은 실제 역사로 보존하고 새 SHA에서도 같은 결과라고 미리 단정하지 않습니다. 소유자 Pages Source 설정 질문은 아직 응답 대기이고, 새 공개 URL·HTTP 성공을 주장하지 않습니다. `docs/weekly-dispatcher.yml`은 **fail-closed·미설정 검토 artifact**일 뿐 default branch에 설치되지 않았습니다. 주간 예약은 비활성, PC installer 미실행·사용자 PC 작업 미설치입니다. Box·기관 인증·개인 AI API·자동 검수 완료 화학정보 추출을 수행한 것으로 기록하지 않습니다.

## 후속 최종 기록

최종 QA·Revision 원문은 이전 네 지적 RESOLVED·신규 WEB-QA-05/WEB-REV-05 한 건 CHANGES REQUESTED입니다. [최종 인계](handoff.md)로 round-03 Planning에 output/checkpoint·feed/state 내구성 순서를 넘깁니다. 새 terminal CI는 build PASS, Pages 설정403·배포/HTTPS NOT RUN입니다. 위 진행 중 문구와 preliminary zero-finding 판단은 최종 승인으로 해석하지 않습니다.
