# Validator / Windows CI

사용자 승인된 기존 Windows 워크플로에서 고정 SHA를 검증하는 단계입니다. 모델이 아니며 워크플로를 임의 변경하지 않습니다.

| 필수 검사 | 증거 |
| --- | --- |
| windows_build | Windows EXE 빌드 로그·산출물 |
| packaged_ui | 인자 없는 일반 실행과 패키지 UI 주요 흐름·영어 UI·DOI 링크 |
| restart_persistence | 데이터 생성 후 종료·재실행 시 동일 데이터 유지 |
| runtime_path_independence | 소스 체크아웃·별도 개발 런타임에 의존하지 않는 실행, 공백 경로 |

각 상태는 PASS / FAIL / NOT RUN입니다. --smoke-test만으로 일반 실행을 대체하지 않습니다. 별도 Python·Node.js 없이 패키지가 실행되는지 검사합니다. 커밋 SHA와 실제 검증 산출물의 SHA-256을 기록합니다. 실행 불가·시간 초과는 통과가 아닙니다. Release·배포를 하지 않습니다.

