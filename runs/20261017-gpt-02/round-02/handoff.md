# Wiki → Planning 인계 — 20261017-gpt-02 / round-02

- 날짜/시간대: 2026-10-17 (America/Chicago).
- 소스: `c96c210a89a077869da78e7e570f06c80768cc16`.
- QA·Revision 최종 결과: **BLOCKED_REQUIRED_WINDOWS_EVIDENCE**.
- 미해결 앱 코드 지적: **0건**. 이전 네 앱 지적은 두 역할의 독립 재현으로 **RESOLVED**입니다.
- 필수 Windows 증거: **NOT VERIFIED**, 최종 승인·artifact·체크섬 없음.
- 다음 단계: **round-03 Planning**, CI 증거 관찰·종료 보고 및 독립 headless 검증만 좁게 수정합니다.
- [QA 전체 원문](qa.md)과 [Revision 전체 원문](revision.md)을 변경하지 않고 보존했습니다.

## 관찰 사실과 미확인 상태

[마지막 영수증](windows-pending/last-observed-status.json)은 같은 SHA·실행 `39011910077`을 가리키지만 `status: running`, 빈 `steps`, `artifact_url: null`입니다. 불변 영수증 커밋은 `65a2dcf538f6ce8ef11fce32ee9615a6c38ad35f`, 게시 시각은 `2026-10-17T07:04:12Z`입니다. [관찰 기록](windows-pending/observation.json)의 확인 시각은 `2026-10-17T07:35:21.810849Z`입니다.

설정된 30분 job 예산보다 오래 지난 뒤에도 최종 결과를 관찰하지 못했습니다. **실제 runner 상태는 UNKNOWN**입니다. 경과 시간이나 오래된 running 영수증만으로 timeout·실패·실행 중·종료를 단정하지 않습니다. GitHub Actions API는 환경 재연결 후 재시도에서도 Forbidden이었습니다. 로컬 PASS는 이 필수 Windows 증거를 대신하지 않습니다.

## round-03 Planning 작업

1. 의존성·프런트엔드/API·패키징·EXE 스모크/fixture·일반 시작/UI/재실행/PATH·임시 scheduler·headless CLI·gateway 관찰·artifact 업로드 전후에 **소스/실행 ID와 시각이 결속된** 단계 영수증 및 제한된 진단 로그를 보존합니다. heartbeat 자체를 테스트 통과로 해석하지 않습니다.
2. 개별 단계 실행을 제한하고, 중단될 수 있는 build job 내부의 마지막 단계에만 의존하지 않는 **실패/취소/timeout에도 사실을 보존하는 최종 증거 경로**를 계획합니다. 권위 있는 terminal outcome과 관찰 불가를 구분하고, 경과 시간만으로 timeout/success를 만들어내지 않습니다. 비밀·환경 덤프·논문 본문을 로그에 남기지 않습니다.
3. `scripts/observe_jacs_gateway.py`의 packaged `--sync-jacs` 실행을 초기 live Crossref 성공 여부와 독립적으로 검증합니다. 제한된 실제 packaged 프로세스의 provider-unavailable JSON/종료 결과와 통제된 성공 fixture를 구분합니다. live probe 실패로 호출이 생략됐다면 NOT RUN이며, `--smoke-test` 내부 fixture로 headless CLI 검증을 대신하지 않습니다. fixture 성공을 live PDF 성공으로 기록하지 않습니다.
4. 기존 필수 Windows 빌드·패키지 검사·일반 실행/UI·진짜 재실행·PATH·실제 미래 시각 임시 작업 등록/조회/정리를 모두 유지합니다. scheduler 검사는 수집 작업을 실행하거나 사용자 PC에 설치하지 않습니다. 변경된 CI/검사 입력을 **새 전체 SHA**로 고정하고 필수 검사와 두 독립 검토를 반복합니다.

새 소스 변경 전에 현재 SHA의 권위 있는 늦은 최종 영수증이 나타나면 별도로 확인합니다. 현재 start 영수증만으로 승인하지 않습니다. 네 앱 수정을 다시 미해결로 되돌리지 않고, 기능 범위·OA-only·기존 데이터와 모든 locator 보존·합격 기준을 그대로 유지합니다. 이전 EXE나 다른 SHA의 승인으로 대체하지 않습니다.

## 유지할 한계

클라우드 공급자 관찰은 UNAVAILABLE이며 새 live PDF 성공을 주장하지 않습니다. 깨끗한 Windows VM·실제 기본 브라우저·사용자 PC 수집/예약 설치·Box 직접 저장/동기화는 NOT RUN입니다. 기관 인증·구독 PDF 수집·개인 모델 API·공개 Release·배포·권한 변경 없이 검증 인프라 범위만 계획합니다.
