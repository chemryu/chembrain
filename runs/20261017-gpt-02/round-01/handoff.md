# Wiki → Planning 인계 — 20261017-gpt-02 / round-01

- 날짜/시간대: 2026-10-17 (America/Chicago).
- 검토 대상 소스: `36fde22d2791475062565161bf986b88f035b2da`.
- 최종 검수: **CHANGES REQUESTED / 미해결 4건 / 전달 승인 없음**.
- 다음 단계: **Planning이 round-02 계획을 작성**합니다. 이번 후보를 최종 파일로 전달하지 않습니다.
- 원문: [Independent QA](qa.md), [Revision](revision.md). 두 보고서를 변경하지 않고 보존했습니다.

## Revision이 확인한 수정 작업

| ID / 심각도 | 다음 Planning에 전달할 작업 | 필요한 검증 |
| --- | --- | --- |
| REV-01 / QA-01 · HIGH | PDF 요청과 모든 리다이렉트를 원래 정규화 DOI 및 허용된 동일 논문 PDF 경로/버전에 결속합니다. 같은 출판사라도 다른 DOI·임의 경로는 요청 전에 거절하며 현재 HTTPS·공개 주소 보호를 유지합니다. | 실제 production redirect handler를 호출해 같은 논문의 허용 경로는 통과하고, 다른 DOI·비PDF 경로·허용되지 않은 호스트는 거절하는 회귀 검사. |
| REV-02 / QA-02 · MEDIUM | 검증된 라이선스 시작/종료(제공된 경우), 콘텐츠 버전, 제공 PDF 링크를 첨부 provenance에 보존하고 Crossref 문서 type을 collection에 기록합니다. 기존 사용자 필드·source ID·원본 업로드를 덮어쓰지 않습니다. | 정상 첨부 후 공개 provenance를 확인하고 사용자 메타데이터 및 원본 보존, UI/내보내기에 비공개 경로·전문이 노출되지 않음을 검사. |
| REV-03 / QA-03 · MEDIUM | 문서화한 최대 PDF 페이지 수를 설치 전에 적용합니다. 초과 파일은 정확한 거절 상태를 남기고 DOI 참조·기존 정상 첨부·증거를 보존하며 임시 파일을 남기지 않습니다. | 페이지 경계 및 초과 입력, 기존 바이트/매직/파싱/암호화 검사 유지, 실패 시 원자성과 정리 검사. |
| REV-04 / QA-04 · MEDIUM | 같은 정규화 DOI의 기존 main source가 여러 개면 DOI·source ID 목록·개수를 collection notice/status에 보고합니다. 모든 기록과 사용자 필드를 보존하며 파괴적으로 병합하지 않습니다. | 중복 기존 기록·반복 수집·deterministic source 선택·본문/SI 구분 및 모든 원래 기록 보존을 검사. |

## 현재 증거와 다음 승인 조건

QA는 전체 로컬 Python **210 PASS / Windows 전용 DPAPI 1 SKIP**와 프런트엔드 빌드 PASS를 독립 실행했으나, 네 문제를 해결하는 증거는 아닙니다. Development의 추가 브라우저·재실행 PASS는 구현 측 증거로만 보존합니다. 현재 정확한 SHA의 Windows CI는 보고서 시점에 **PENDING**이며, 나중에 성공하더라도 이 후보의 검수 거절을 뒤집지 않습니다.

Planning은 기존 JACS 전체·서지정보+OA PDF만·사용자 데이터 보존·본문/SI DOI 카드 통합 조건을 유지해 round-02를 계획합니다. Development가 수정 후 새 전체 SHA를 고정하고 필수 로컬/Windows 검사와 두 독립 검토를 그 SHA로 다시 수행해야 합니다. 합격 기준을 낮추거나 이전 SHA의 결과를 승계하지 않습니다.

클라우드 공급자 관찰은 **UNAVAILABLE**로 유지합니다. fixture 성공은 실제 공급자 다운로드 성공이 아닙니다. 깨끗한 Windows VM·실제 사용자 기본 브라우저 연동은 NOT RUN이며 사용자 PC 예약 작업 설치·Box 직접 기록/동기화·기관 인증 이전·개인 외부 AI API 호출은 수행하지 않았습니다.
