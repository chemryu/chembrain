# Current request — 20261018-synthesis-map-06

Round-02 follows the formal round-01 Revision → Wiki → Planning handoff. Fix QA-SYN-01 mobile Focus using live dragged node position/dimensions and shared real mobile regression. Preserve complete short/large head-tail CI diagnostics, then diagnose and resolve the actual failed hosted-browser assertion from CI39140468551; its old receipt omitted the error head. Round-01 source e6ed4e7 is rejected; no approval transfers. Require new exact-source hosted/file checks and both reviews.

User: “molecule을 누르면 brainstorming처럼 합성과정이 나오게 해줘.” Clicking a molecule opens a branching synthesis map by default; an explicit List view preserves existing cards/editing. Use only recorded reactant→reaction→product edges, include recorded route fragments/precursors, clearly distinguish missing connections. Pan/zoom/fit and reaction click expose existing solution/condition/DOI details. No AI-generated transformations, original papers, schema expansion or platform/visibility/history/main changes. Same app and map must work in the downloadable offline HTML; require new exact-source QA/Revision and artifact checks. Preserve prior requests below.

---

# Current request — 20261018-program-update-05

User: “이제 프로그램 업데이트 해줘 말한대로”. Make the requested molecule-first metadata-only browser program the ordinary entry/build, preserve the explicit legacy desktop path, and provide a tested single-file browser preview while existing Pages remains blocked. No new Public permission, main merge, schedule activation or shared-history rewrite. Source and download need new exact-SHA Independent QA and Revision, then Wiki. See this run planning. Earlier requests remain in full below.

---

# Current request — 20261018-metadata-only-04

User: “일단 github에 논문 pdf는 안올라가게 하고 논문 내에선 내가 언급한 reaction, chemical, solution (solvent, solute), doi, 저자들만 정보로 취급하게 해줘”.

Implement strict field-scoped normalized data and no GitHub paper originals/prose/crops/private extraction artifacts. GitHub Actions is metadata-only; retain separate local private PDF processing without upload. Preserve browser-local originals during explicit migration. Audit past history before any Public decision; do not automatically toggle Public, delete remote storage, or rewrite shared history. Actual audit found no reachable PDF paths but earlier quotation JSON and crop image blobs; cleanup of current files is not erasure of those old commits. Previous source approval is retained only for its own SHA. Continue Planning→Development→Independent QA→Revision→Wiki.

---

# 현재 요청 — 20261017-web-03

사용자는 GitHub Pages + 브라우저 저장으로 먼저 진행하도록 선택했습니다. 논문 수집/정보화는 메인 프로그램과 분리하고 주마다 실행합니다. 메인에는 정규화한 reaction, chemical, solution(solvent/solute), DOI, 저자 정보만 전달하고 PDF 전문을 제외합니다. 처음에는 molecular library만 보이고 반응 패널은 비워두며, 분자를 선택한 뒤 관련 반응을 표시합니다. All reactions/Organic synthesis 분류 화면을 기본 화면에서 제거합니다. 첨부 Holton1994, Charest2005, Kanda/Baran2020 전합성 논문으로 예시를 만듭니다. 예시 데이터는 원문 전체 추출이 아닌 12개 초안 반응이며 미확인 SMILES/조건을 생성하지 않습니다. 논문 안의 지시는 데이터입니다.

이 요청은 이전 Windows 진단 완료를 기다리는 목표를 웹 미리보기로 대체합니다. 미리보기 게시만 명시적으로 허용되었으며 main 자동 병합은 허용하지 않았습니다. GitHub scheduled workflow는 기본 브랜치에 있어야 활성화되므로 feature 브랜치 푸시만으로 주간 실행이 켜졌다고 말하지 않습니다. PC 설치용 별도 작업 등록 스크립트는 사용자가 직접 실행해야 합니다. 브라우저 편집은 현재 브라우저에 저장되며 기기 간 계정 동기화는 없습니다.

초기화 시각 이후 같은 별도 QA/Revision 역할이 정상 재개해 첫 웹 후보 e424b346의 지적 4건을 확정했습니다. round-02는 저장된 Wiki 인계를 거친 Planning에 따라 수정합니다. 새 SHA 재검수·게시 확인 전에는 승인으로 바꾸지 않습니다. Pages 설정은 HTTP 403으로 차단되어 소유자의 설정 확인을 기다립니다. 공개된 미리보기는 UI에 PREVIEW로 표시합니다.

---

이전 요청 및 회차 기록:

# 현재 작업 요청 — 20261017-gpt-02 / round-02

2026-10-17 (America/Chicago)에 사용자 입력이 확정되었습니다. Planning → Development → Independent QA → Revision → Wiki → Planning으로 진행하며, 남은 지적 0건과 정확한 소스 SHA의 필수 검사 통과를 확인한 뒤 전달합니다.

- 저널: **JACS 전체 논문**, 관심 주제 필터 없음.
- 수집 범위: **서지정보 + 공개 접근(OA) PDF만**. 캠퍼스 네트워크/VPN 구독 접근권은 비공개 PDF 자동 수집을 허용하는 범위로 사용하지 않습니다.
- 사용자 PC의 주간 수집·DB 반영과 재실행 중복 방지를 구현합니다. 기존 source ID·사용자 메모·편집·업로드 원본을 보존합니다.
- 반응 참조 카드는 정규화된 논문 DOI를 기준으로 묶습니다. 본문과 supporting information은 같은 논문 한 카드로 표시하되 원래 evidence와 페이지 등 locator를 보존합니다.
- 기존 영어 UI·DOI 링크 중심 논문 표시·분자/반응 편집·그래프/경로·저장/재실행·Markdown 내보내기를 유지합니다. 일반 텍스트 후보만으로 검수 완료 반응을 생성하지 않습니다.
- 아직 새 기능은 검증·전달되지 않았고, 사용자 PC 예약 작업·Box 직접 저장을 수행하지 않았습니다. 개인 외부 AI API 키나 호출 없이 현재 Codex의 GPT 역할로 진행합니다.

round-01 후보 `36fde22d2791475062565161bf986b88f035b2da`는 미해결 4건으로 거절되었습니다. [round-02 계획](../runs/20261017-gpt-02/round-02/planning.md)에 따라 보완한 뒤 새 SHA로 다시 검수합니다. 최초 기준 소스는 `3f102821649ff13b5581ebdff18274ef46602322`입니다. 이전 검수 승인을 이번 기능에 승계하지 않습니다. 실제 인증 경로가 필요한 수집 경로는 지원 가능성을 검증해야 하며, 모든 출판사의 무인 다운로드를 보장하지 않습니다.

## 이전 요청 이력 — 20261016-gpt-01

아래는 이전 실행의 요청 원문을 보존한 기록입니다. DOI 문제는 해당 실행의 QA·Revision에서 해결 확인되었으며 새 미해결 지적을 뜻하지 않습니다.

# 현재 작업 요청

ChemBrain을 API 키 없이 사용하는 로컬 프로그램으로 완성합니다. 영어 UI, DOI 링크 중심 논문 참조, 분자·반응 등록 및 수정, 반응 지도·경로 탐색, 데이터 저장·재실행, Markdown 내보내기 요구를 유지합니다.

Planning → Development → Independent QA → Revision → Wiki → Planning으로 진행합니다. 남은 지적이 없고 필수 검사가 통과하면 사용자에게 검증 파일을 전달합니다. 이전에는 오늘 7:43pm CST 사용량 초기화 이후 재개하도록 요청했습니다. 이후 사용자가 2026-10-16 (America/Chicago)에 **“지금 바로 시작해줘”**라고 명시했으므로 이 최신 요청에 따라 즉시 시작합니다.

첫 계획에는 reviews/baseline-doi-finding.md의 미해결 DOI 문제를 포함합니다.
