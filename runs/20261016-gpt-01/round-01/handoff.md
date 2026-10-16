# Wiki 최종 인계 — 20261016-gpt-01 / round-01

- 역할: 별도 Wiki GPT. 검수 판단을 대신하지 않고 QA·Revision 전체 보고서를 보존하고 완료 상태를 기록합니다.
- 날짜: 2026-10-16 (America/Chicago).
- 검수된 실행 소스: `3f102821649ff13b5581ebdff18274ef46602322` / `codex/gpt-agent-workflow`.
- 기록 원본: GitHub `codex/gpt-workflow-records`.
- 최종 상태: **READY_REVIEWED_CANDIDATE**.
- 다음 Planning 인계: **CLOSE / 추가 회차 없음**.
- 남은 지적: **0건**. 필수 자동 검사: **PASS**.

## Revision 결과와 종료 근거

[Planning](planning.md) → [Development](development.md) → [Independent QA 원문](qa.md) → [Revision 원문](revision.md)을 보존했습니다. QA와 Revision은 같은 전체 소스 SHA에 대해 각각 후보 전달 범위의 PASS와 남은 지적 0건을 보고했습니다. Revision은 DOI 삭제 방지·업로드 문서의 선택 DOI·영어 편집 UI·실패 시 저장 불변성·정확한 SHA의 Windows 증거를 대조하고, 독립 추가 DOI 행렬도 실행했습니다. 원문을 축약하거나 지적의 의미를 변경하지 않았습니다.

Wiki는 두 독립 판단과 필수 검사 완료를 기록하고 회차를 종료합니다. Planning에 넘길 추가 구현 작업이 없으므로 새 회차를 시작하지 않습니다. 이후 새 요구나 실행 소스 변경이 발생하면 새 계획·검사·독립 검수 회차를 시작합니다.

| 필수 증거 | 결과 |
| --- | --- |
| 독립 QA 로컬 Python 전체 검사 | PASS — 153 passed, Windows 전용 DPAPI 1 skipped |
| 실제 Windows Python 전체 검사 | PASS — 154 passed, 0 skipped |
| 프런트엔드 빌드·실제 Chromium UI·DOI 독립 행렬 | PASS |
| 소스 일반 시작·실제 재실행 저장 유지 | PASS |
| Windows EXE 빌드·패키지 스모크·인자 없는 일반 시작·실제 UI | PASS |
| Windows 실제 프로세스 재실행·전체 데이터 유지 | PASS |
| EXE 자식 프로세스의 Python/Node 없는 제한 PATH | PASS |
| QA·Revision·Windows의 전체 소스 SHA 일치 | PASS |
| CI가 테스트한 후보 패키지의 체크섬과 artifact 원본 | PASS — 아래 출처 범위로 확인 |

## 사용자 전달 파일과 실행 방법

- [검수된 Windows 후보 다운로드](https://github.com/chemryu/chembrain/actions/runs/38978428660/artifacts/12080600552)
- 소스 SHA: `3f102821649ff13b5581ebdff18274ef46602322`
- 불변 Windows 영수증 SHA: `0c6df260af7ef7a340cd2aff80415d4577c63bbf`
- 내부 파일: `Chembrain-Windows-x64.zip`
- 내부 ZIP SHA-256: `ceacbc857ec919b45687f4108fe1394d8a4405643e592358e75cf942ba06b9c0`
- 원본 [상태](windows/status.json), [Windows 테스트](windows/api.log), [스모크](windows/packaged-smoke.log), [일반 시작/UI/재실행](windows/normal-launch.log), [체크섬](windows/SHA256SUMS.txt)

1. 위 GitHub Actions artifact를 다운로드합니다. 필요하면 저장소 접근 권한이 있는 GitHub 계정으로 로그인합니다.
2. 다운로드된 외부 artifact ZIP을 압축 해제합니다.
3. 그 안의 `Chembrain-Windows-x64.zip`도 압축 해제합니다.
4. `Chembrain.exe`를 더블클릭합니다. 첫 실행은 압축을 푸느라 조금 걸릴 수 있습니다.
5. 앱 사용 중 콘솔 창을 열어 둡니다. 종료하려면 콘솔을 닫거나 `Ctrl+C`를 누릅니다.

Python·Node.js 설치나 API 키는 필요하지 않습니다. 사용자 데이터는 `%LOCALAPPDATA%\Chembrain`에 저장하며 EXE 위치와 별개로 유지됩니다. 알려진 문제가 있는 이전 `windows-3` 릴리스나 다른 SHA의 패키지로 대체하지 않습니다.

체크섬은 CI가 방금 테스트한 EXE 패키지로부터 생성해 동일 artifact에 업로드했습니다. 이 세션에서 확인한 것은 불변 영수증·원본 검사 로그·CI 체크섬과 업로드 출처입니다. 인증이 필요한 artifact를 별도로 내려받아 바이트를 재계산하지는 않았습니다. 위 artifact를 그대로 연결하며 대체·재압축하지 않습니다.

## 수동 검사 한계와 수행하지 않은 작업

깨끗한 Windows VM 실행과 사용자의 실제 기본 브라우저 등록·연동은 **NOT RUN**입니다. 제한 PATH 검사는 PATH 독립성을, 브라우저 요청 프로브와 별도 Chromium 검사는 요청 의도와 앱 UI를 검증합니다. 수동 검사 두 항목의 통과를 뜻하지 않습니다. 이 제한을 공개한 **검수 후보 전달**이며 정식 공개 Release 승인은 아닙니다.

외부 개인 AI API·API 키를 사용하지 않았습니다. 사용자 Windows Box 폴더 직접 저장·Box 동기화·공개 Release·서비스 배포·권한 변경·영구 GPT 백그라운드 실행·자동 예약 재개를 수행하지 않았습니다. 다섯 GPT 역할은 이번 활성 Codex 작업 안에서 완료했습니다.
