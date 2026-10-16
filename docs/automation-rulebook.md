# Box 기반 구현·독립 검수 자동화

사용자 작업 폴더는 `C:\Users\Ren Lab\Box\AIWorkflow\ChemBrainProject`입니다. Linux 클라우드는 사용자 Windows 디스크에 직접 접근할 수 없습니다. 준비한 설치 도구를 사용자 PC에서 실행해야 하며 템플릿 작성과 실제 설치 완료를 구분합니다.

`workflowkit/templates/`에 한국어 룰북·초기 위키·역할별 지침·요청·설정 예시가 있습니다. 설치 도구는 기존 사용자 파일을 확인 없이 덮어쓰지 않아야 합니다. 설정 도구의 설치 권한과 모델의 소스 수정 권한은 별개입니다.

GPT는 소스 변경안을 반환하고 Claude는 고정 SHA의 소스를 독립 검수합니다. 기존 GitHub Actions Windows 러너가 동일 SHA의 실제 패키지를 검증합니다. 로컬 컨트롤러가 변경 적용·SHA 고정·검수 반환·반복 상한·원자적 위키 기록·최종 전달을 강제합니다. 역할 MD는 OS ACL이나 이미 실행 중인 에이전트가 아닙니다.

## 초기 설정

1. 사용자 PC에서 설치 도구로 Box 폴더를 초기화합니다.
2. 사용 가능한 모델 ID와 저장소·브랜치를 설정합니다. 기본 모델 ID는 비어 있습니다.
3. OpenAI·Anthropic·GitHub 인증을 설정합니다. 키는 Box 밖에 Windows DPAPI로 보관합니다. ChatGPT·Claude 구독과 API 사용료는 별개입니다.
4. requests/current.md 안내문을 실제 요청·완료 기준으로 바꿉니다.
5. 이 PC에서 로컬 컨트롤러를 실행합니다.

물리 Box Drive 동기화를 사용하므로 Box API는 필요하지 않습니다. 컨트롤러는 한 PC에서 하나만 실행하며 Box 동기화는 분산 잠금이 아닙니다. 다른 PC는 실행 중인 작업 폴더에 쓰지 않습니다. PC나 컨트롤러를 종료하면 진행도 중단됩니다.

기본 반복 상한은 5회이며 API 출력·시간 예산도 유한하게 제한합니다. 검수 차단·시간 초과·필수 검사 실패·NOT RUN·SHA 불일치는 통과가 아닙니다. 검수 승인·지적 0건과 필수 검사 전부 PASS를 같은 SHA에 대해 확인해야 검증한 파일 그대로 deliverables/에 전달합니다. GitHub Release나 서비스 배포는 하지 않습니다.

운영 규칙은 [RULEBOOK.md](../workflowkit/templates/RULEBOOK.md)에 있습니다. 인증·설정·컨트롤러 실행 전에는 준비 단계이며 두 모델의 자동 통신이나 Windows 검사가 활성화되었다고 안내하지 않습니다.
