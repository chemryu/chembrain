# ChemBrain 진행 위키

## 현재 상태 — 합성 brainstorming Map / synthesis-map round-02

**다운로드 합성 Map 미리보기 READY / 별도 QA·Revision material 지적 0건 — 새 Pages403·과거 역사 Public 미승인은 별도 유지**

- 정확한 고정·푸시 소스 **`02d0dff2ce66a00f10e0c873baea80fa6f94e963`**, 실행 `20261018-synthesis-map-06 / round-02`. 거절 round-01 Revision → Wiki → 별도 [Planning](runs/20261018-synthesis-map-06/round-02/planning.md) → [Development](runs/20261018-synthesis-map-06/round-02/development.md) → 별도 [QA 전체 원문](runs/20261018-synthesis-map-06/round-02/qa.md) → 별도 [Revision 전체 원문](runs/20261018-synthesis-map-06/round-02/revision.md) → [Wiki](runs/20261018-synthesis-map-06/round-02/wiki-record.md)·[전달](runs/20261018-synthesis-map-06/round-02/handoff.md) 완료입니다. 두 독립 역할은 **bounded downloadable preview PASS / 지적 0건**, QA-SYN-01 해결을 각각 실제 모바일 재현으로 확인했습니다.
- 분자를 선택하면 brainstorming 형태의 **Map**이 기본으로 열립니다. 기록된 분자→반응→생성물만 화살표로 연결하고, 빠진 단계는 분리된 fragment로 안내합니다. 확대/축소·이동·Fit/선택 분자 Focus·반응 클릭 조건/용매·용질/DOI 확인이 가능하며 **List**로 기존 카드·편집을 엽니다. 미확인 구조·조건과 draft 표시를 유지하며 새 화학 사실을 만들지 않았습니다.
- **[업데이트 프로그램 다운로드](https://github.com/chemryu/chembrain/actions/runs/39141206671/artifacts/12140894328)**: GitHub 로그인 → ZIP 다운로드·압축 해제 → `Chembrain.html`을 Edge/Chrome에서 엽니다. Python·Node·AI API 키 설치 없이 사용합니다. 기존 파일을 바꾸거나 옮기기 전에 **Backup JSON**, 새 파일에서 **Import package**로 복원하세요. 브라우저/프로필/파일 위치 저장이며 기기 간 동기화를 보장하지 않습니다.
- 실제 HTML **722585 bytes**, SHA-256 **`a1a175882c6701e2d3f98b61b80dbed27d643e0de1eb661823c930b36384278d`**; artifact ID12140894328, CI-reported ZIP digest `d5ba0bad0030913a63c36824123dd4ae2561c5034556cab32e1daa23eb331ee2`. [delivery.json](runs/20261018-synthesis-map-06/round-02/delivery.json)에 identity를 보존했습니다. 로컬 HTML/CI manifest·라이브러리 digest 일치를 확인했으나 ZIP 자체를 독립 다운로드했다고 주장하지 않습니다.
- 새 실제 [CI39141206671](https://github.com/chemryu/chembrain/actions/runs/39141206671), 불변 영수증 **`8c8d3c6317433502ffd4984df39fd6b4290ef52e`**: **290 PASS / Windows DPAPI 1 SKIP**, hosted build/browser·payload·portable build·**실제 file:// 오프라인 browser PASS**, artifact upload SUCCESS입니다. 모바일 실제 card drag→Focus geometry와 기존 편집/저장/backup/import/오류보존/보안 검사 포함. QA/Revision/Wiki가 [9개 원본](runs/20261018-synthesis-map-06/round-02/web/manifest.json)의 bytes/hash와 불변 Git receipt를 대조했습니다. 로컬 관리 브라우저 file 차단은 우회하지 않았고 별도 CI runner의 실제 파일 실행과 구분합니다.
- 모바일 Focus는 ReactFlow의 현재 위치·치수를 읽도록 수정했습니다. QA·Revision이 각각 이전 실패 재현을 그대로 실행해 카드가 화면 안으로 돌아오는 것을 확인했습니다. CI 진단은 짧은 로그 전체·큰 로그 앞뒤를 보존하며 실제 Git receipt 회귀 검사를 추가했습니다. **이전 e6ed4e7 CI 실패의 사라진 최초 assertion 원인은 여전히 UNRESOLVED**이고 이번 성공으로 원인을 밝혔거나 이전 실행이 통과했다고 표현하지 않습니다. 이전 거절 원문·4개 CI 증거는 그대로 보존합니다.
- 이번 CI는 실제 Pages 설정을 시도하여 **새 403 Resource not accessible by integration**, 배포/HTTP **NOT RUN**, URL null을 기록했습니다. collection SKIP·주간 미활성·PC 예약 미설치·Box 미동기화입니다. 역사 인용문/crop과 원격 storage UNVERIFIED 때문에 Public 전환은 계속 미승인입니다. visibility/history/main/권한 변경·production release 없음입니다. cloud 환경 draft는 새 소스로 저장됐지만 **환경 Publish 필요**이며 앱 다운로드 실행과 별개입니다. 새 코드 수정 지적이 없어 빈 Planning 회차를 만들지 않고 다운로드 미리보기 전달로 종료합니다.

## 이전 상태 — 합성 brainstorming Map / synthesis-map round-01

**CHANGES REQUESTED / 미해결 앱 지적 1건 + 새 CI browser FAIL — round-02 Planning 환류, 새 다운로드 미승인**

- 실행 `20261018-synthesis-map-06 / round-01`, 정확한 고정·푸시 소스 **`e6ed4e70028fa77dfd59cbeede249ccc1a52b274`**. [Planning](runs/20261018-synthesis-map-06/round-01/planning.md) → [Development](runs/20261018-synthesis-map-06/round-01/development.md) → 별도 [QA 전체 원문](runs/20261018-synthesis-map-06/round-01/qa.md) → 별도 [Revision 전체 원문](runs/20261018-synthesis-map-06/round-01/revision.md) → [Wiki 기록](runs/20261018-synthesis-map-06/round-01/wiki-record.md)·[round-02 인계](runs/20261018-synthesis-map-06/round-01/handoff.md)입니다. 두 독립 역할 모두 **CHANGES REQUESTED**, 이전 승인은 새 소스에 승계하지 않습니다.
- 분자 선택 시 Map을 기본으로 열고 실제 reactant→reaction→product만 표시했습니다. List·기존 편집·조건/용매/용질/DOI 확인을 유지하며, 기록 없는 연결은 만들지 않고 분리된 fragment로 안내합니다. 하지만 **QA-SYN-01 P2**: 모바일에서 선택 분자 카드를 드래그한 뒤 Focus를 누르면 초기 좌표로 이동해 실제 카드가 화면 밖에 남습니다. QA와 Revision이 각각 실제 Chromium에서 재현했습니다. 현재 ReactFlow 노드 위치·치수를 사용하고 실제 모바일 drag→Focus 회귀 검사가 필요합니다.
- Development 전체 **289 PASS / Windows DPAPI 1 SKIP**, build·broad hosted browser·payload gates PASS, QA 별도 집중 **15 PASS**·hosted browser·HTTP-only portable PASS입니다. 이 broad 검사는 추가 모바일 실패를 놓쳤으며 통과로 상쇄하지 않습니다. 로컬 실제 file://는 관리 브라우저 정책으로 NOT RUN, 우회하지 않았습니다.
- 새 실제 [CI 39140468551](https://github.com/chemryu/chembrain/actions/runs/39140468551), 불변 영수증 **`44c569c9fc284fe30fb59b440a61eb7ad084ed57`**: tests **289 PASS / 1 SKIP**, app build PASS이나 **hosted browser FAIL**입니다. 현재 보존된 `web-browser.log`는 tail DOM만 있어 최초 실패 원인은 **UNRESOLVED**이며 QA-SYN-01과 같다고 단정하지 않습니다. portable build·실제 file:// 검사·artifact upload는 **SKIP/NOT RUN**, 새 전달 artifact 없음입니다. [네 원본 파일/manifest](runs/20261018-synthesis-map-06/round-01/web/manifest.json)는 Wiki가 bytes/SHA-256 및 불변 영수증과 대조했습니다.
- 이 CI에서는 publish가 생략되어 **Pages 설정·배포·HTTPS 모두 NOT RUN, URL null**입니다. 이전 `aaf4d8b` 실행의 Pages403은 역사이며 이번 실행에서 새 403을 관찰했다고 쓰지 않습니다. 이전 다운로드는 이전 프로그램용으로만 보존하고 합성 Map 전달물로 제시하지 않습니다.
- 다음 순서: [round-02 Planning 인계](runs/20261018-synthesis-map-06/round-01/handoff.md) → 좁은 mobile Focus 수정·실제 drag 회귀·CI 실패 head/tail/간결한 진단 보존 및 실제 원인 해결 → 새 SHA/HTML 전체 필수 검사와 두 독립 검수 → Wiki. 완료 기준을 낮추지 않습니다. 알려진 Git 역사 원문/그림·원격 Actions storage UNVERIFIED·Public 미승인, Box 미동기화·주간 미활성·main 미병합·브라우저 로컬 저장 한계는 그대로입니다.

## 이전 상태 — 설치 없는 브라우저 프로그램 업데이트 / program-update round-01

**다운로드 브라우저 미리보기 READY / Independent QA·Revision 지적 0건 — Pages403·기존 역사 Public 미승인은 별도 유지**

- 실행 `20261018-program-update-05 / round-01`, 고정·푸시 소스 **`aaf4d8b13d4604e98458cd6eec59cc8205254bae`**. [Planning](runs/20261018-program-update-05/round-01/planning.md) → [Development](runs/20261018-program-update-05/round-01/development.md) → [Independent QA 전체 원문](runs/20261018-program-update-05/round-01/qa.md) → [Revision 전체 원문](runs/20261018-program-update-05/round-01/revision.md) → [Wiki 기록](runs/20261018-program-update-05/round-01/wiki-record.md)·[인계](runs/20261018-program-update-05/round-01/handoff.md) 완료. 두 독립 검토는 정확한 새 소스의 미해결 material 지적 **0건**, bounded browser preview **PASS**입니다. 이전 승인으로 대체하지 않았습니다.
- 일반 개발·빌드가 영어 molecular library를 기본으로 열며 Python API 없이 동작합니다. 처음엔 반응 패널이 비어 있고 분자를 선택하면 관련 반응이 나옵니다. 논문 정보는 반응·chemical·solution(용매·용질)·DOI·저자 범위이며 참조는 DOI별 중복 제거합니다. 기존 desktop은 명시적 별도 mode로 유지됩니다.
- **[브라우저 프로그램 다운로드](https://github.com/chemryu/chembrain/actions/runs/39102813926/artifacts/12127033101)**: GitHub 로그인 → artifact ZIP 다운로드/압축 해제 → `Chembrain.html` 더블클릭 → Edge/Chrome에서 사용합니다. Python·Node·개인 AI API 설치 없이 실행합니다. 이것은 설치형 EXE나 게시된 웹사이트가 아닌 다운로드 미리보기입니다.
- 실제 HTML **463557 bytes**, SHA-256 **`843a7e610582352dfc0e30be310133834684084b20125f89bf894fb5934da10a`**. CI artifact ID **12127033101**, reported archive digest `ef31fe4f69971b576390986cfb5f564f2a331512002e314d80a99d6f63d115d2`. [delivery.json](runs/20261018-program-update-05/round-01/delivery.json)에 소스/파일/CI identity를 보존합니다. 로컬 HTML/CI manifest 일치를 확인했지만 artifact archive 자체를 독립 다운로드했다고 주장하지 않습니다.
- 정확한 실제 CI [39102813926](https://github.com/chemryu/chembrain/actions/runs/39102813926), 불변 영수증 **`8ad7371b089fafad09bfbc222cd565e5cc3a28b5`**: **284 PASS / Windows DPAPI 1 SKIP**, hosted build/browser·payload gate PASS, **실제 file:// HTML 오프라인 브라우저 PASS**. 추가 요청 전부 차단/앱 요청 0건, 편집·재실행·JSON backup/import·저장 오류 보존·mobile·악성 embedding 검사 포함. QA/Revision은 [9개 원본](runs/20261018-program-update-05/round-01/web/manifest.json)을 불변 영수증과 bytes/hash 대조했습니다. 로컬 관리 브라우저의 file 정책 차단은 그대로 기록하며 다른 CI runner의 실제 파일 검증과 구분합니다.
- 편집은 현재 브라우저·프로필·파일 위치의 로컬 저장입니다. **파일을 교체·이동하거나 브라우저를 바꾸기 전에 JSON Backup을 저장하고 Import로 옮기세요.** 동기화·자동 업데이트·경로 간 동일 저장을 보장하지 않습니다. 원본 PDF·원문·논문 crop이나 private legacy backup은 프로그램 배포에 포함하지 않습니다.
- 새 CI도 Pages 설정 **403 Resource not accessible by integration**, 배포/HTTP 접근 **NOT RUN**, URL **null**입니다. collection **SKIP**, 주간 작업 미활성·PC 예약 미설치·Box 직접 저장/동기화 없음·새 Windows EXE 승인 없음입니다. 기존 Git 역사 인용문 JSON 2개·copied crop 2개와 원격 artifact/cache UNVERIFIED를 유지하므로 **기존 저장소 Public 전환 미승인**입니다. visibility 변경/역사 재작성/main merge를 수행하지 않았습니다.
- root가 cloud 환경 draft의 소스·install·start 설정을 저장했지만 **환경 Publish 필요**입니다. 환경 설정 Publish는 앱 파일 실행이나 Pages 게시와 별개이며 앱 추가 승인 gate가 아닙니다. 앱 코드 수정 지적이 없어 빈 다음 Planning을 만들지 않고 미리보기 전달로 종료합니다.

## 이전 상태 — 정보 범위 제한 / metadata-only round-01

**현재 소스 정책 검수 PASS / 두 독립 역할 material 지적 0건 — Public 준비 미승인·Pages403**

- 최신 사용자 요청은 GitHub에 논문 PDF를 올리지 않고 reaction, chemical, solution(용매·용질), DOI, 저자만 논문 정보로 다루는 것입니다. 논문 원문·인용문·PDF 그림·추출 후보도 GitHub/Pages 공개 데이터에서 제외했습니다.
- 실행/회차 `20261018-metadata-only-04 / round-01`; 새 고정 소스 **`6280794c87e7867b0ccd2e2d4f6924814917997a`**. 이전 `56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`의 두 독립 검수 지적 0건은 역사이며 새 변경의 승인이 아닙니다.
- [Planning](runs/20261018-metadata-only-04/round-01/planning.md) → [Development](runs/20261018-metadata-only-04/round-01/development.md) 완료. [Independent QA](runs/20261018-metadata-only-04/round-01/qa.md)는 같은 소스의 material 지적 0건·현재 정책 PASS를 확인했습니다. 별도 전체 검사 284 PASS/1 SKIP, 집중 56 PASS, 실제 Chromium·payload gate PASS입니다. [Revision](runs/20261018-metadata-only-04/round-01/revision.md)도 독립 집중 38 PASS 및 원본 CI/manifest 대조로 material 지적 0건·현재 정책 PASS를 확정했습니다. 현재 코드 변경 완료와 과거 역사 포함 Public 전환 승인은 구분합니다.
- 개발 검사: **284 PASS / Windows 전용 DPAPI 1 SKIP**, 웹 production build·실제 Chromium PASS. 중첩 allowlist, DOI/저자만 있는 paper, 레거시 원본 로컬 백업 실패 시 보존, metadata-only 수집·내구성·payload gate를 검사했습니다. 독립 승인으로 대체하지 않습니다.
- 현재 app은 논문 제목·저널·연도·paper notes를 내보내지 않고 DOI/저자만 참조로 표시합니다. reaction/chemical/solution 조건·연결 ID·근거 위치·draft/검토 상태는 유지합니다. 레거시 원본은 정확한 bytes로 브라우저 안에 별도 백업하며 GitHub 업로드용이 아닙니다. 미확인 구조·조건은 unknown으로 유지합니다.
- GitHub Actions는 강제 metadata-only로 PDF 다운로드/텍스트 추출을 실행하지 않습니다. paper-work cache는 제거했고 원격 durable state는 명시적 checkpoint/anchor만 저장합니다. 별도 로컬 PDF 처리는 Git 밖 비공개 작업으로 남습니다. PC 주간 작업·기본 브랜치 cron은 활성화하지 않았습니다.
- [현재 트리](runs/20261018-metadata-only-04/round-01/audit/current-tree.json)와 [dist](runs/20261018-metadata-only-04/round-01/audit/dist.json) payload 검사 PASS. **[도달 가능한 역사 검사](runs/20261018-metadata-only-04/round-01/audit/reachable-history.json)는 PDF blob 0개이나, 과거 인용문 JSON blob 2개와 논문 그림 crop blob 2개를 확인했습니다. 현재 파일 삭제는 과거 commit 삭제가 아닙니다.** 원문 자체는 보고서에 재인용하지 않습니다.
- GitHub Actions의 과거 artifact/cache·삭제된 ref·서버의 unreachable object는 완전 확인하지 못했습니다. 따라서 Public-safe·모든 원격 원문 제거를 주장하지 않습니다. visibility 변경·역사 재작성·브랜치/태그 삭제·원격 artifact/cache 삭제는 수행하지 않았습니다. 별도 깨끗한 배포 저장소는 대안이며 아직 만들지 않았습니다.
- 소유자 화면은 현재 비공개 저장소 요금제의 Pages 제한을 확인했습니다. 새 소스 실제 CI `39098202973` / 불변 영수증 `c3add00d19e2e6e2daf1e9d92efe69b3835d48f2`는 284 PASS/1 SKIP·웹 빌드·실제 브라우저·payload gate PASS, collection SKIP입니다. 새 Pages 설정도 실제 **403 Resource not accessible by integration**이며 배포·HTTPS 검사는 NOT RUN, URL null입니다. [원본 6개와 검증 manifest](runs/20261018-metadata-only-04/round-01/web/manifest.json)를 보존했습니다. 실제 공개 URL·production 승인은 없습니다. Box 자동 저장/동기화·개인 AI API 호출도 없습니다.

- 최종 [Wiki 기록](runs/20261018-metadata-only-04/round-01/wiki-record.md)과 [인계](runs/20261018-metadata-only-04/round-01/handoff.md)에 두 독립 원문·해시·정확한 CI 증거·외부 제한을 보존했습니다. 새 코드 수정 지적이 없어 빈 Planning 회차를 만들지 않습니다. 알려진 과거 인용문/그림 처리 또는 깨끗한 별도 배포 저장소 결정이 다음 외부 작업이며 현재 Public 전환은 권하지 않습니다.
- cloud 환경 draft는 현재 `6280794c87e7867b0ccd2e2d4f6924814917997a` 저장소/소스와 start skill로 갱신 저장했으며 **Publish 필요**입니다. 네트워크·설치·비밀 설정은 바꾸지 않았고 앱 승인의 추가 조건으로 만들지 않습니다.

## 이전 웹 round-03 상태

**SOURCE REVIEW PASS / CODE FINDINGS 0 — 공개 미리보기는 PAGES 설정403으로 BLOCKED**

- 사용자 **“이어서 진행해줘”**가 이전 일시중지를 해제했습니다. 재개 요청 기록 `2026-10-18T03:21:05.438839+00:00`는 America/Chicago 기준 2026-10-17입니다. 예약 자동 재개가 아닙니다.
- 실행/회차: `20261017-web-03 / round-03`; 고정·푸시된 소스 **`56be43bf15b4c98b8b515d2dc3bbd2bd0fcbbbae`**. 이전 거절 소스 `d423c718ca3c0b7d1dd090a362ba02990d7e223a`와 원문은 보존합니다.
- 순서: 게시된 round-02 QA → Revision → Wiki 인계(`b9285eca83cb4dc5128b9ef00f146fb43675bd88`) → 별도 [round-03 Planning](runs/20261017-web-03/round-03/planning.md) → [Development 구현·검사](runs/20261017-web-03/round-03/development.md) → 별도 [Independent QA](runs/20261017-web-03/round-03/qa.md) → [Revision](runs/20261017-web-03/round-03/revision.md) → [Wiki 최종 인계](runs/20261017-web-03/round-03/handoff.md) 완료입니다.
- 두 독립 역할은 이 정확한 소스에 **PASS / 미해결 코드 지적 0건**을 확정했고 WEB-QA-05/WEB-REV-05를 **RESOLVED**로 판정했습니다. 이전 네 지적도 해결 상태를 유지합니다. 코드 검수 통과와 공개 접근 가능한 전달 완료는 구분합니다.
- Development 증거: Python **273 PASS / Windows 전용 DPAPI 1 SKIP**, `build:web`·실제 Chromium PASS, processor 내구성 집중 34 PASS, 실제 임시 Git remote/provenance·YAML·diff 검사 PASS. 개발 검사이며 독립 승인 근거를 대신하지 않습니다.
- 새 실제 CI 실행 `39093753253` / 불변 영수증 `5829825cf51ea5a5677922886eb1c8575405822e`: **273 PASS / 1 SKIP·웹 빌드·실제 브라우저 PASS**, 새 Pages 설정 **403 Resource not accessible by integration**, 배포·공개 HTTPS **NOT RUN**, URL null입니다. 이전 결과를 가정한 것이 아니라 새 SHA의 실제 결과입니다. 소유자 Source 설정 응답은 별도 대기입니다.
- 새 replay anchor, output 성공 뒤 metadata 진행, origin이 인정한 feed 뒤 remote state 저장과 정확한 feed/hash 검증을 구현했습니다. durable state는 공개 DOI/queue/checkpoint whitelist metadata만 저장하며 raw PDF/private review cache는 best effort입니다.
- 주간 dispatcher는 미설정 검토 artifact·미설치로 **주간 비활성**이고 사용자 PC 작업도 미설치입니다. UI·3논문/12초안·과학 unknown·브라우저 로컬 저장은 유지합니다. Box 저장/동기화·기관 인증 이전·개인 AI API·production 승인을 주장하지 않습니다.
- 현재 기록: [round-03 Wiki](runs/20261017-web-03/round-03/wiki-record.md). QA·Revision 원문과 여섯 CI 원본/manifest를 보존했습니다. 새 코드 수정 목록은 없어 Planning으로 빈 회차를 돌리지 않으며, 소유자 Pages 설정과 같은 SHA의 실제 배포·HTTPS 증거를 기다립니다. 공개 앱 전달/production 승인은 아직 없습니다.
- cloud 환경 설정은 root가 정확한 저장소/소스 및 start skill을 **draft로 저장**했습니다. runtime publish와 Pages 게시는 별개이며 아직 publish 완료가 아닙니다. 이 관찰은 앱의 추가 검수 승인 조건으로 만들지 않습니다.

## 이전 일시중지와 round-02 이력

**사용자 요청으로 작업 일시중지 — 새벽 12:05 이후 재개 요청**

- 최신 요청이 이전 즉시 시작 요청보다 우선합니다. 소스 d423c718은 그대로 보존했습니다.
- 앞선 중부시간 문맥에 따라 2026-10-18 00:05 America/Chicago로 잠정 이해했습니다. 실제 한도 초기화 시각을 확인한 것은 아닙니다.
- 이 세션에는 예약 자동 재개 도구가 없어 **예약되지 않았습니다**. 사용자 재접속 또는 실제 지원되는 클라이언트 작업으로 재개해야 합니다.
- 다음 지점: [재개 체크포인트](runs/20261017-web-03/RESUME.md) → 별도 round-03 Planning. 구현은 아직 시작하지 않았습니다.
- 아래 round-02 최종 검수·외부 차단과 모든 과거 기록을 그대로 유지합니다.


**CHANGES_REQUESTED — web round-02 이전 4건 해결·신규 내구성 순서 1건 + Pages 403**

- 날짜/시간대: 2026-10-17 (America/Chicago)
- 실행/회차: `20261017-web-03 / round-02`
- 고정·푸시된 소스: `d423c718ca3c0b7d1dd090a362ba02990d7e223a`; 이전 거절 소스 `e424b34653fb96b911f5ee5708286c92baddfe5f`
- 순서: round-01 인계 기록 `128c3fca84fbc222043c5aaaddcc126bcc62c172` 게시 → 별도 round-02 Planning → Development 구현/로컬 검사 완료
- Independent QA·Revision 최종: **CHANGES REQUESTED / 신규 WEB-QA-05·WEB-REV-05 1건**. 이전 네 지적은 모두 RESOLVED
- 다음 단계: [round-02 인계](runs/20261017-web-03/round-02/handoff.md) → 좁은 내구성 순서 보완 round-03 Planning
- 구현 측 검사: Python 253 PASS / Windows 전용 DPAPI 1 SKIP, build:web·실제 Chromium PASS, malformed editor 42종·Python export→import 포함
- 새 CI: 불변 영수증 `4fb229121ebd4597c51bae7dec30cf37dc759d61`, 실행 `39063636131` — 253 PASS/1 SKIP·웹/실제 브라우저 PASS, workflow/built SHA와 library hash 보존
- 새 실제 Pages 설정: **403 Resource not accessible by integration**, 배포·실제 HTTPS/source-data marker **NOT RUN**, URL 없음
- 이전 403을 가정한 것이 아니라 새 SHA에서도 실제 403을 확인. 소유자 Source 설정 응답은 별도 대기
- durable state branch는 공개 DOI/queue/checkpoint whitelist metadata만 저장, PDF·private review는 제외. Raw archive cache는 best effort로 영구 보관 아님
- 주간 dispatcher는 fail-closed·미설정 검토 artifact뿐이며 **미설치·주간 비활성**. 사용자 PC 작업도 미설치
- 미리보기만 사용자 명시 허용; 새 앱/production 승인 없음. 브라우저 로컬 저장·정규화 데이터·초기 빈 반응 패널·과학 draft 한계 유지
- 기록: [round-02 Wiki](runs/20261017-web-03/round-02/wiki-record.md). Box 직접 저장·기관 인증 이전·개인 외부 AI API 호출 없음

## 이전 웹 검수 거절 상태 — 20261017-web-03 / round-01

**CHANGES_REQUESTED — 웹 round-01 미해결 4건 + 별도 Pages 403 차단**

- 날짜/시간대: 2026-10-17 (America/Chicago)
- 최신 선택: **GitHub Pages + 브라우저 저장**, 별도 주간 논문 processor와 정규화 데이터만 전달
- 초기 화면: molecular library, 분자 선택 전 반응 패널 비움; 기본 All reactions/Organic synthesis 화면 제거
- 고정·푸시된 소스: `e424b34653fb96b911f5ee5708286c92baddfe5f`; 기준 `c96c210a89a077869da78e7e570f06c80768cc16`
- Development: root 구현·로컬 검사 완료. 최초 계획은 root가 구현 전에 작성; 별도 Planning addendum은 구현 후 작성·보존됨
- Independent QA·Revision: 초기화 후 기존 역할이 실제 검수 완료, 둘 다 **CHANGES REQUESTED / 미해결 4건 / 전달 승인 없음**
- 다음 단계: [round-01 인계](runs/20261017-web-03/round-01/handoff.md) → round-02 Planning
- 로컬 구현 검사: Python 237 PASS / Windows 전용 DPAPI 1 SKIP, build:web·실제 브라우저 PASS
- Pages 실행: `39062568338`, 불변 terminal 영수증 `0331192af8d03426f4a2c28a584eaf7f9d34bb1d` — 테스트 237 PASS/1 SKIP·웹 빌드·브라우저 PASS, 설정은 **403 Resource not accessible by integration**
- Pages 배포·실제 공개 접근: **NOT RUN**, URL 없음. 소유자 Pages 설정 응답 대기
- 예시: 3 papers / 12 draft reactions, 데이터 약 22 KB / 사이트 약 420 KB; 미확인 SMILES·조건 null, 완전한 OCR 아님
- 사용자 허용: PREVIEW로 표시한 **공개 미리보기 게시**. 독립 production 승인·main 자동 병합은 없음
- 주간 cron: feature 브랜치에만 있어 **미활성**. 사용자 PC 설치 스크립트도 미실행·예약 작업 미설치
- 브라우저 저장: 현재 브라우저만 사용, 기기 간 계정 동기화 없음. PDF 전문/원문 후보는 메인 데이터·사이트에서 제외
- 기록 원본: GitHub `codex/gpt-workflow-records`; 실행 소스 `codex/gpt-agent-workflow`
- 이전 Windows 차단/승인 이력은 아래와 회차 원문에 보존. Box 직접 저장·기관 인증 이전·개인 외부 AI API 호출 없음
- 자세한 순서/범위: [새 실행 Wiki 기록](runs/20261017-web-03/round-01/wiki-record.md)

## 이전 Windows 실행 차단 상태 — 20261017-gpt-02

**BLOCKED_REQUIRED_WINDOWS_EVIDENCE — round-02 앱 지적 0건, 필수 증거 미확인·round-03 Planning 인계**

- 날짜/시간대: 2026-10-17 (America/Chicago)
- 확정 범위: JACS 전체 논문, 주제 필터 없음, **서지정보 + OA PDF만**
- 추가 요구: 본문·SI 참조 카드를 정규화 논문 DOI별 하나로 묶고 locator·원래 evidence 보존
- 역할: round-02 Planning·Development·QA·Revision·Wiki 기록 완료, 다음 round-03 Planning 대기
- 고정된 새 소스 SHA: `c96c210a89a077869da78e7e570f06c80768cc16` — 소스 브랜치에 푸시됨
- 이전 거절 SHA: `36fde22d2791475062565161bf986b88f035b2da` — 계속 거절 상태이며 [round-01 보고서](runs/20261017-gpt-02/round-01/) 보존
- 이전 거절 기록 게시: `27ad901ccd0183f018d840d78259ebd4158bb728`
- 회차 시작 기반: `3f102821649ff13b5581ebdff18274ef46602322` — 이전 승인은 신규 변경에 승계하지 않음
- 이전 지적 4건: QA와 Revision이 각각 독립 재현으로 **모두 해결 확인**, 미해결 앱 코드 지적 0건. 필수 증거 차단은 별도 문제
- QA·Revision 최종 판정: 둘 다 **BLOCKED_REQUIRED_WINDOWS_EVIDENCE**, 최종 승인·전달 허가 없음
- 다음 Planning: [round-02 인계](runs/20261017-gpt-02/round-02/handoff.md)를 읽고 CI 관찰/종료 보고·headless 검증만 round-03으로 계획
- 정확한 SHA의 Windows 실제 runner 상태: **UNKNOWN**. [마지막 관찰](runs/20261017-gpt-02/round-02/windows-pending/observation.json)은 `65a2dcf…`의 오래된 running 영수증뿐이며 최종 로그·artifact·체크섬 없음; timeout/실패로 단정하지 않음
- 로컬 검사: Python 227 PASS / Windows 전용 DPAPI 1 SKIP, collector 64 PASS, 빌드·실제 브라우저·소스 시작/재실행·스모크 PASS
- 클라우드 공개 공급자 관찰: **UNAVAILABLE** (네트워크/DNS 제한) — 실제 다운로드 PASS가 아님
- 전달 가능 여부: **아니오**, 승인된 새 artifact 없음. 사용자 PC 예약 작업 설치: **아직 없음**
- 기록 원본: GitHub `codex/gpt-workflow-records`; 실행 소스 `codex/gpt-agent-workflow`
- Box 직접 저장·자동 동기화: 미구성. 기관 인증 이전·개인 외부 AI API 호출: 없음

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

## 2026-10-17 · gpt-02 round-02 소스 고정

Wiki가 원문을 보존한 round-01 거절·4건 수정 인계는 기록 커밋 `27ad901ccd0183f018d840d78259ebd4158bb728`에 게시되었습니다. [round-02 Planning](runs/20261017-gpt-02/round-02/planning.md)이 범위를 확정했고, Development가 네 수정을 구현해 소스 `c96c210a89a077869da78e7e570f06c80768cc16`를 고정·푸시했습니다. [Development 원문](runs/20261017-gpt-02/round-02/development.md)에 실제 명령과 결과를 보관합니다.

수정은 PDF 각 리다이렉트의 원래 DOI/경로 결속, OA 유효일·버전·제공 링크/type provenance, 400페이지 상한, 기존 중복 DOI의 비파괴 notice 보고입니다. Development 로컬 전체 검사는 227 PASS / Windows 전용 DPAPI 1 SKIP, collector 집중 검사는 64 PASS이며 빌드·실제 Chromium·소스 일반 시작/실제 재실행·네트워크 없는 collector 스모크도 PASS입니다. 이 결과는 **구현 증거**이며 네 지적의 독립 해결 판정은 아직 아닙니다.

QA·Revision은 새 전체 SHA를 검토 중이고 Windows CI는 PENDING입니다. 이전 거절 후보 `36fde22d2791475062565161bf986b88f035b2da`는 승인되지 않은 상태로 보존하며, 다른 SHA의 빌드나 과거 앱 승인을 가져오지 않습니다. 최종 보고서와 필수 증거가 완료되기 전에는 새 artifact를 승인하거나 전달하지 않습니다. 공개 공급자의 cloud UNAVAILABLE 관찰과 깨끗한 Windows VM/실제 기본 브라우저 NOT RUN, 사용자 PC 예약·Box 미설치 한계를 유지합니다.

## 2026-10-17 · round-02 로컬 독립 검증 완료·Windows 진행 중

[QA 중간 보고서](runs/20261017-gpt-02/round-02/qa.md)는 소스 `c96c210a89a077869da78e7e570f06c80768cc16`의 이전 4건을 로컬에서 독립 재현해 해결을 확인했고, **로컬 미해결 지적 0건 / 정확한 Windows 증거 대기**로 기록했습니다. 별도 Revision의 보완 로컬 검사도 현재 지적 0건으로 보고되었으나 QA 최종 보고서와 Windows 결과를 기다립니다. 두 역할의 최종 승인이나 전달 승인이 완료된 상태가 아닙니다.

새 SHA의 [Windows 실행](https://github.com/chemryu/chembrain/actions/runs/39011910077)은 RUNNING이며 현재 영수증 `65a2dcf…`는 실행 중 상태만 나타냅니다. 최종 필수 로그·공급자 관찰·artifact·체크섬을 확인하기 전에는 통과로 기록하지 않습니다. 이전 `36fde22…` 거절 및 네 지적 원문/인계는 그대로 보존하며, 클라우드 공급자 UNAVAILABLE를 실제 다운로드 성공으로 변경하지 않습니다. 새 코드 변경은 없고 사용자 PC 작업/Box 설치도 수행하지 않았습니다.

## 2026-10-17 · round-02 필수 증거 차단 및 Planning 환류

QA·Revision 최종 원문은 모두 **BLOCKED_REQUIRED_WINDOWS_EVIDENCE / 미해결 앱 코드 지적 0건**입니다. 이전 네 앱 수정은 해결된 상태로 보존하며 다시 미해결로 열지 않습니다. [round-02 인계](runs/20261017-gpt-02/round-02/handoff.md)는 다음 Planning에 CI 단계 관찰·중단 시에도 정확한 최종 증거 보존·live provider와 독립적인 packaged headless CLI 검증만 전달합니다.

`2026-10-17T07:35:21.810849Z` 관찰에서도 마지막 영수증 `65a2dcf538f6ce8ef11fce32ee9615a6c38ad35f`는 `07:04:12Z`에 게시된 running 상태·빈 단계 결과·null artifact였습니다. 30분 job 예산보다 오래 지났지만 실제 runner 상태는 **UNKNOWN**입니다. Actions API Forbidden 때문에 권위 있는 현재 결과를 확인하지 못했으며 timeout·실패·계속 실행 중이라고 단정하지 않습니다. 같은 소스의 Windows 패키지/일반 실행/UI/재실행/PATH/scheduler/headless/최종 체크섬은 NOT VERIFIED입니다.

live Crossref의 첫 관찰이 실패하면 packaged `--sync-jacs` 호출도 생략되는 검증 경로는 별도로 수정해야 합니다. 호출 생략은 NOT RUN이며 오프라인 smoke fixture나 로컬 PASS로 대체하지 않습니다. 새 SHA에 대한 기존 필수 검사·독립 QA·Revision을 그대로 유지하고 앱 범위를 넓히거나 합격 기준을 낮추지 않습니다. 현재 전달 가능한 새 artifact는 없습니다.

## 2026-10-17 · 웹 구조로 목표 변경

사용자의 최신 요청에 따라 이전 Windows 진단 완료를 기다리는 목표를 **GitHub Pages 공개 미리보기 + 브라우저 저장**으로 대체했습니다. 별도 주간 processor와 분리한 정규화 데이터, 분자 우선 화면을 새 실행 `20261017-web-03`으로 기록합니다. 원문 PDF는 게시하지 않으며 예시 12개는 검토가 필요한 초안입니다.

[초기 root 계획](runs/20261017-web-03/round-01/planning.md)은 구현 전 작성됐고 별도 Planning addendum은 구현 후 요청되었습니다. 앞선 사용량 오류는 이력으로 남기며, 초기화 안내 시각을 지난 뒤 기존 QA·Revision의 정상 재개가 진행 중입니다. 실제 최종 보고서 전에는 독립 승인을 기록하지 않습니다. 공개 게시 역시 정확한 소스 marker의 실제 HTTP 확인 전에는 접근 가능으로 확정하지 않습니다. 주간 cron은 기본 브랜치 반영 전 미활성이고 PC 설치 스크립트는 사용자가 직접 실행해야 합니다.

## 2026-10-17 · web round-01 검수 거절·외부 게시 차단

[QA 전체 원문](runs/20261017-web-03/round-01/qa.md)과 [Revision 전체 원문](runs/20261017-web-03/round-01/revision.md)을 그대로 보존했습니다. 두 역할은 소스 `e424b34653fb96b911f5ee5708286c92baddfe5f`를 초기화 이후 정상 재개해 검수했고 **CHANGES REQUESTED / MEDIUM 4건**을 확정했습니다. 현재 결과는 usage-limit으로 미검수한 상태가 아니며 source-time placeholder를 소급 수정하지 않습니다.

1. malformed advanced JSON shape가 저장 전 editor/app 전체를 unmount하는 문제.
2. processor가 성공 export한 v1 데이터가 browser 계약에서 거절되는 불일치.
3. weekly PDF cap 뒤 알려진 eligible work가 checkpoint 진행과 함께 영구 누락되는 문제.
4. collection 데이터 커밋 이후에도 trigger SHA로 공개 marker를 만들어 실제 built data identity가 사라지는 문제.

[Planning 인계](runs/20261017-web-03/round-01/handoff.md)에 각 수정 계약과 검사를 전달했습니다. 별도 Pages 설정 403 `Resource not accessible by integration`은 [불변 영수증/로그](runs/20261017-web-03/round-01/web/manifest.json)로 확인됐고 소유자 설정 응답을 기다립니다. CI 테스트 237 PASS/1 SKIP·웹 빌드·브라우저는 PASS이나 배포와 실제 HTTP 확인은 NOT RUN, URL도 없습니다. 앱 검사 성공을 접근 가능·독립 승인으로 바꾸지 않습니다.

새 source/data identity를 고정해 수정 검사와 두 독립 검토 및 실제 게시 응답을 확인하기 전에는 완료로 전달하지 않습니다. 기존 과학 draft/미확정 구조, 비활성 주간 cron, 미설치 PC 작업, 브라우저 로컬 저장 및 이전 Windows 기록의 한계를 유지합니다.

## 2026-10-17 · web round-02 고정 소스 검수 시작

[Planning](runs/20261017-web-03/round-02/planning.md)과 [Development](runs/20261017-web-03/round-02/development.md)를 읽고 소스 `d423c718ca3c0b7d1dd090a362ba02990d7e223a`의 중간 상태를 기록했습니다. 세 Development 보조 기록은 같은 역할의 구현 증거이며 QA·Revision의 독립 승인을 대신하지 않습니다. 네 이전 지적의 해결 여부는 실제 두 보고서가 나온 뒤 기록합니다. 새 CI 및 실제 Pages 접근 역시 아직 미확인입니다.

공개 DOI/재시도 state의 Git 내구성과 private PDF/review cache의 best effort를 구분합니다. 미설정 dispatcher artifact는 실제 예약 설치가 아니며, 이전 Pages 403 및 소유자 설정 응답 대기를 성공으로 바꾸지 않습니다. 모든 이전 회차의 승인·거절·외부 차단을 보존합니다.

## 2026-10-17 · web round-02 최종 거절·신규 한 문제 인계

최종 [QA 원문](runs/20261017-web-03/round-02/qa.md)과 [Revision 원문](runs/20261017-web-03/round-02/revision.md)은 기존 네 문제를 독립적으로 해결 확인했지만, **신규 WEB-QA-05/WEB-REV-05 MEDIUM 1건**으로 CHANGES REQUESTED를 기록했습니다. 일부 preliminary 지적 0건 초안은 최종 승인으로 사용하지 않습니다.

신규 문제는 최종 bibliography output보다 metadata 완료 checkpoint·page cursor가 먼저 저장되고, CI에서는 feed commit/push보다 remote state가 먼저 저장되는 순서입니다. output 실패 뒤 다음 window/cursor 재개에서 이미 발견한 서지정보가 사라지는 경우가 독립 재현됐습니다. [round-03 Planning 인계](runs/20261017-web-03/round-02/handoff.md)는 output→state와 origin이 인정한 feed→remote progress의 내구성 경계 및 실패/재시도·Git publication guard 회귀만 보완합니다. 이전 네 해결 계약을 다시 열거나 기능 범위를 넓히지 않습니다.

새 불변 영수증 `4fb229121ebd4597c51bae7dec30cf37dc759d61`은 253 PASS/1 SKIP·웹 빌드·실제 브라우저 PASS와 정확한 library digest를 유지했지만, Pages 설정은 실제 403이며 배포/공개 HTTPS는 NOT RUN입니다. 원문·영수증을 보존하고 승인·URL을 주장하지 않으며 소유자 외부 설정 응답은 별도로 기다립니다. 주간 dispatcher와 PC 작업도 아직 미설치·미활성입니다.
