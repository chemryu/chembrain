# ChemBrain 자동 검수 워크플로 설치

이 패키지는 Chembrain 앱의 최종 배포본이 아니라 **작성·검수·기록 자동화 도구**입니다. 현재 ChatGPT/Claude 채팅창을 자동으로 깨우는 기능이 아니라 OpenAI/Anthropic API를 사용하는 별도 실행 프로그램입니다.

1. ZIP 전체를 압축 해제합니다.
2. `Install-Workflow.cmd`를 더블클릭합니다. 별도 Python 설치나 PowerShell 스크립트 실행 권한 변경 없이 EXE가 초기 폴더와 실행 바로가기를 만듭니다.

   기본 설치 폴더는 `C:\Users\Ren Lab\Box\AIWorkflow\ChemBrainProject`입니다. 관리자 권한이나 Box 권한 확대를 요청하지 않습니다. 다른 폴더를 지정하려면 터미널에서 다음처럼 실행합니다.

   ```powershell
   .\ChembrainWorkflow.exe install --root 'D:\Box\ChemBrainProject'
   ```

3. 설치 폴더의 `Start-Workflow.cmd`를 열고 Configure를 선택합니다. 두 API의 모델 이름과 OpenAI·Anthropic API 키, GitHub 토큰을 입력합니다. 키 입력은 화면에 표시되지 않습니다. **키를 wiki.md, Box 문서, 채팅에 붙여넣지 마세요.**
4. `requests/current.md`를 실제 요청과 완료 기준으로 교체하고 `WORKFLOW_REQUEST_INACTIVE` 표시를 지웁니다.
5. 한 번 실행하려면 메뉴 Run, 새 요청을 계속 감지하려면 `Watch-Workflow.cmd`를 실행합니다. 컨트롤러가 실행 중이고 PC가 켜져 있어야 합니다.

## 연결과 권한

- Box Drive가 이미 로그인해 동기화하는 폴더를 이용하므로 별도 Box API 토큰은 필요 없습니다.
- OpenAI·Anthropic API는 채팅 구독과 과금이 별개입니다. 모델 이름은 계정에서 사용 가능한 정확한 API 모델 식별자를 지정하세요. 최대 5회 반복이 기본이며 10회를 넘길 수 없습니다. 요청이 실패·차단되면 자동으로 유료 실행을 재시도하지 않습니다.
- GitHub 토큰은 `chemryu/chembrain`에 한정한 fine-grained 토큰을 권장합니다. 코드 변경을 올리기 위한 Contents 읽기/쓰기와 Actions 결과·artifact를 읽을 권한이 필요합니다. 저장소 관리/조직 관리 권한은 필요 없습니다.
- Windows 사용자에 묶인 DPAPI로 키를 암호화해 `%LOCALAPPDATA%\ChembrainWorkflow\credentials.dpapi`에 보관합니다. Box에는 API 키가 들어가지 않습니다. 다른 PC로 이 파일을 복사해도 그대로 사용할 수 없습니다.
- 에이전트 권한은 컨트롤러가 수행 가능한 작업을 제한하는 논리 권한입니다. Windows 계정이나 ACL을 새로 만들거나 관리자 권한을 부여하지 않습니다.
- 한 폴더에는 지정한 PC의 컨트롤러 하나만 실행합니다. Box 동기화는 여러 PC 사이의 분산 잠금이나 실시간 메시지 큐가 아닙니다.

## 산출물과 정지 조건

`wiki.md`는 회차별 대화·진행 기록, `reviews/`는 구조화된 검수 결과, `changes/`는 수정 제안, `runs/`는 검증 근거와 이벤트입니다. 모델 출력은 파일·리뷰 데이터로만 처리하며 임의 명령을 실행하지 않습니다.

같은 커밋에 대한 필수 Windows 검사 PASS, 독립 검수 승인, 남은 지적 0건, artifact 체크섬 일치를 모두 확인해야 `deliverables/<커밋>/`에 ZIP과 READY.md를 만듭니다. 자동 GitHub Release 게시는 하지 않습니다. 외부 권한·검사 누락·커밋 불일치·반복 횟수 초과가 있으면 BLOCKED 또는 NEEDS_ATTENTION으로 멈추고 위키에 기록합니다.

깨끗한 Windows VM과 사용자 기본 브라우저 연동은 현재 검수의 별도 제한 사항입니다. PATH 분리 검사를 깨끗한 PC 검사로 표현하지 않습니다. 검수자가 이 제한을 배포 차단으로 판단하면 최종 파일을 전달하지 않습니다.

실제 API 계정 인증·과금 승인·Box Drive 로그인을 대신 완료해 주는 도구는 아닙니다. 설치 전 클라우드에서 이 Windows 로컬 폴더에 파일이 생성된 것은 아닙니다.
