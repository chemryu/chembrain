# Wiki → Planning 인계 — 20261017-web-03 / round-01

- 검토 소스: `e424b34653fb96b911f5ee5708286c92baddfe5f`.
- 날짜/시간대: 2026-10-17 (America/Chicago).
- QA·Revision 최종 결과: **CHANGES REQUESTED / 미해결 4건**.
- 별도 외부 차단: **Pages 설정 HTTP 403 — Resource not accessible by integration**.
- 최종 전달 승인: **없음**. 공개 URL·실제 접근은 검증되지 않았습니다.
- 다음 단계: **round-02 Planning**. [QA 원문](qa.md)·[Revision 원문](revision.md)을 변경하지 않고 보존했습니다.

## Revision이 확정한 네 수정 계약

| ID / 심각도 | 수정 계약 | 필수 회귀 증거 |
| --- | --- | --- |
| WEB-REV-01 / WEB-QA-01 · MEDIUM | Advanced JSON에서 문법은 유효하나 aliases/authors/steps/solutes 등 shape가 틀린 draft를 안전하게 렌더링하고, 원문과 오류를 유지해 수정·취소 가능하게 합니다. 잘못된 기록을 저장하거나 기존 로컬 데이터를 지우지 않습니다. | 실제 브라우저에서 null/잘못된 배열·객체를 각 editor에 넣어 app shell 유지·유용한 오류·수정/취소·저장 데이터 보존 확인. |
| WEB-REV-02 / WEB-QA-02 · MEDIUM | Python processor와 브라우저의 portable v1 필수 필드·canonical optional null/empty 규약을 일치시킵니다. 성공한 export는 browser import 가능해야 합니다. required 오류는 양쪽에서 거절하고 과학 값을 지어내지 않습니다. | 누락 journal/steps/targets/concentration 및 중첩 solute/unit 등 absent/null/shape의 cross-language 수용·거절 parity, 실제 export→import, 실패 시 기존 데이터 보존. |
| WEB-REV-03 / WEB-QA-03 · MEDIUM | 한 번 발견한 eligible PDF가 10개 cap 때문에 사라지지 않도록 durable pending/continuation과 deferred 결과를 보존합니다. metadata checkpoint와 미완료 다운로드를 분리하며 겹침 창 밖에서도 재시도합니다. | 두 날짜에 걸친 11개 eligible fixture에서 10+1 처리·deferred 보고·checkpoint·OA 재검증·검증 파일 재사용 확인. 인증/출판사 범위 및 네트워크/바이트/페이지 제한 유지. |
| WEB-REV-04 / WEB-QA-04 · MEDIUM | event/workflow/code SHA와 실제 built-data commit/digest를 구분해 build→deploy→HTTP 검사→terminal 기록으로 전달합니다. fresh checkout이 실제 built identity를 덮어쓰지 않게 합니다. | 이벤트 SHA A 이후 데이터 커밋 B를 만든 통제 시나리오에서 marker와 최종 영수증이 두 identity를 정확히 유지하고, 다른 library/digest의 실제 응답은 거절함을 검사. |

## 외부 Pages 차단과 정확한 CI 증거

[원본 manifest](web/manifest.json)와 인접 로그는 불변 영수증 `0331192af8d03426f4a2c28a584eaf7f9d34bb1d`, [실행 39062568338](https://github.com/chemryu/chembrain/actions/runs/39062568338)의 원본 증거입니다. 같은 소스의 테스트 **237 PASS / Windows 전용 DPAPI 1 SKIP**, 웹 빌드·실제 browser smoke는 PASS입니다. Pages 설정은 **403**, deployment와 public HTTP/source-marker 검사는 **SKIPPED / NOT RUN**, `page_url`은 null입니다. green build는 네 문제나 외부 설정 차단을 해소하지 않습니다.

소유자 Pages 설정 확인은 root가 비동기 답변을 기다립니다. 이 결과는 저장소/계정 integration 차단이며 자동 승인 심사의 거절이 아닙니다. 앱을 main에 자동 병합하거나 스케줄을 켜는 방식으로 우회하지 않습니다. 수정된 새 SHA와 실제 built data identity에 대해 CI·독립 QA·Revision 및 실제 공개 HTTP 확인을 반복해야 접근 가능한 미리보기로 기록할 수 있습니다.

## 유지할 순서와 범위

root Planning snapshot은 구현 전, 별도 Planning addendum은 구현 후 작성되었습니다. 앞선 사용량 오류는 사실대로 보존하지만, 초기화 후 기존 QA·Revision 역할이 정상 재개해 **실제 검수 보고서**를 냈으므로 현재 상태를 usage-limit 때문에 검수하지 못한 상태로 표시하지 않습니다. 모델/키 전환이나 한도 우회는 없었습니다. 고정 소스의 예전 준비 문구를 소급해 승인으로 바꾸지 않습니다.

분자 우선 초기 빈 반응 패널·브라우저 로컬 데이터·DOI별 참조·모든 locator·과학적 미확정 값·OA-only를 유지합니다. 세 논문/12개 draft는 원문 대조에서 구체적 불일치가 없었으나 완전한 OCR·구조/전합성/SI 검증이 아닙니다. 자동 화학정보 추출이 완료됐다고 표현하지 않습니다. GitHub cron은 feature 브랜치에만 있어 미활성이고 PC installer도 미실행입니다. 이전 Windows 차단/승인은 역사로 남기며 새 웹 소스에 승계하지 않습니다. Box 직접 기록·기관 인증·개인 AI API·기기 간 계정 동기화·공개 production 승인은 없습니다.
