# Wiki 진행 기록 — 20261017-web-03 / round-01

- 날짜/시간대: 2026-10-17 (America/Chicago).
- 고정·푸시된 소스: `e424b34653fb96b911f5ee5708286c92baddfe5f`; 기준 Windows 소스 `c96c210a89a077869da78e7e570f06c80768cc16`.
- 현재 상태: **PREVIEW_BUILD_AND_INDEPENDENT_REVIEW_RUNNING**. 새 QA·Revision 최종 승인 없음.

## 요청 변경과 실제 순서

사용자가 GitHub Pages + 브라우저 저장을 선택하고 **공개 미리보기 게시를 명시적으로 허용**했습니다. 메인은 정규화된 papers/chemicals/solutions/reactions, DOI와 저자 정보만 사용하고 PDF 전문은 제외합니다. 초기 화면은 molecular library와 비어 있는 반응 영역이며 분자를 선택한 뒤 관련 반응을 표시합니다. 별도 주간 논문 processor가 공개 서지정보·지원되는 명시적 OA 자료를 처리하고 검토 후보를 생성합니다.

주 에이전트가 구현 전에 [Planning snapshot](planning.md)을 작성했습니다. 당시 별도 에이전트가 실제 사용량 한도 오류를 반환해 Development와 실제 검사를 주 에이전트가 수행했습니다. 이후 제한 안내의 초기화 시각(오전 11:28)이 지난 14:30 America/Chicago에 기존 QA·Revision 역할의 정상 재개를 요청했으며 현재 검토 중입니다. 모델·키를 바꾸어 한도를 우회하지 않았습니다. 별도 Planning addendum은 구현 후 요청되었으며, 구현 전 독립 Planning이 완료된 것으로 기록하지 않습니다.

## 현재 구현 측 증거

- Root 전체 Python: **237 PASS / Windows 전용 DPAPI 1 SKIP**.
- `build:web`: PASS. 실제 브라우저 검사: PASS. 독립 QA 실행 결과로 바꾸지 않습니다.
- 예시: Holton1994, Charest2005, Kanda/Baran2020의 **3 papers / 12 draft reactions**, 정규화 데이터 약 22 KB, 정적 사이트 약 420 KB.
- 미확인 SMILES·실험 조건은 null이며 완전한 OCR/전합성/기질 범위 추출이 아닙니다. 논문 원문과 후보 텍스트를 사이트에 포함하지 않습니다.
- Pages 실행 `39062568338`은 마지막 실제 Git 영수증에서 **browser-checks 단계**입니다. 최종 게시·실제 공개 HTTP의 정확한 소스 marker 확인은 아직 대기입니다. root가 영수증 수집을 조정합니다.

## 승인 및 운영 한계

독립 QA·Revision은 현재 실행 중이며 실제 보고서 전에는 PASS로 기록하지 않습니다. 허용된 것은 명확히 PREVIEW로 표시한 미리보기 게시이며, 독립 production 승인·main 자동 병합이 아닙니다. GitHub cron은 feature 브랜치에만 있어 **아직 활성화되지 않았으며**, 기본 브랜치에 반영되어야 예약됩니다. 로컬 설치 스크립트는 사용자가 실행해야 하며 PC 작업을 설치하지 않았습니다. 브라우저 편집은 현재 브라우저에만 저장되고 계정/기기 간 자동 동기화가 없습니다.

이전 `20261017-gpt-02 / round-02`의 앱 지적은 0건이지만 Windows 증거 차단·미승인 상태를 그대로 보존합니다. 미완료 round-03 진단 변경은 별도로 보존했으며 이 웹 앱에 혼합하지 않았고 완료로 기록하지 않습니다. 이전 승인·영수증을 새 소스에 승계하지 않습니다. Box 직접 쓰기·개인 외부 AI API·기관 인증 이전·사용자 PC 예약 설치는 수행하지 않았습니다.

## 후속 최종 기록

QA와 Revision의 실제 보고서가 정상 재개 후 저장되었고 두 원문은 CHANGES REQUESTED / 4건입니다. [최종 인계](handoff.md)와 wiki.md/progress.json이 현재 상태를 기록합니다. Pages CI는 build PASS지만 설정403으로 배포/실제 접근 NOT RUN입니다. 위의 진행 중 표현은 최초 기록 당시 상태이며 최종 승인으로 해석하지 않습니다.
