# Chembrain

논문과 실험 노트를 근거로 분자·반응을 연결하는 로컬 연구 워크스페이스입니다.

## 실행

필수 도구: Python 3.12+, Node.js 22.12+ (또는 20.19+), npm.

GitHub에서 받은 ZIP을 압축 해제한 뒤 `README.md`와 `package.json`이 있는 폴더에서 터미널을 여세요. GitHub ZIP의 폴더 이름은 브랜치 이름에 따라 달라질 수 있습니다.

```bash
./scripts/setup.sh
./scripts/start.sh
```

Windows는 Python 3.12와 Node.js LTS를 설치한 뒤, 압축을 푼 `chembrain` 폴더에서 명령 프롬프트 또는 PowerShell을 열고 다음을 실행합니다.

```powershell
.\scripts\setup.cmd
.\scripts\start.cmd
```

Mac/Linux에서는 위의 `.sh` 스크립트를 사용합니다. ZIP에서 실행 권한이 보존되지 않았다면 `bash scripts/setup.sh`, `bash scripts/start.sh`로 실행할 수 있습니다. 설치 스크립트는 최초 1회(또는 의존성 변경 시), 시작 스크립트는 앱을 켤 때마다 실행합니다. 서버가 실행되는 터미널을 열어 두고 사용하며, `Ctrl+C`로 종료해도 `.data/`의 자료와 기록은 보존됩니다.

브라우저에서 `http://127.0.0.1:8000`을 엽니다. 개발 중에는 `./scripts/dev.sh`로 API와 Vite 개발 서버를 함께 실행할 수 있습니다 (화면: 포트 5173).

## 첫 사용

1. **반응 지도**에서 명확히 표시된 데모 데이터를 탐색합니다. 데모는 문헌에서 추출한 실험 결과가 아닙니다.
2. **자료 보관함**에 PDF·Markdown·텍스트 파일을 업로드합니다. PDF는 본문과 Supporting Information을 각각 올릴 수 있습니다.
3. 자료를 열고 원문 페이지와 추출된 후보 문장을 확인합니다. `반응 기록에 사용`으로 근거를 가져옵니다.
4. 분자를 SMILES로 등록하고 반응물·생성물·조건·수율을 입력합니다. 검토 완료로 저장하려면 원문 근거가 필요합니다.
5. **경로 탐색**에서 목표 생성물과 최대 단계 수를 선택합니다. 모든 반응물 가지를 포함한 등록 반응의 연결을 보여줍니다. 재고·구매 가능성 미확인 항목은 따로 표시합니다.
6. **Markdown 내보내기**로 분자·반응·자료 백링크와 기록을 ZIP으로 받을 수 있습니다.

사용자가 제공한 3편의 본문과 SI에서 대표 반응 6개를 검토한 JSON이 `examples/uploaded-literature.json`에 들어 있습니다. GitHub ZIP을 새로 실행하면 기본 데모가 표시됩니다. 실제 문헌 예제를 불러오는 방법은 아래를 참고하세요. 본문/SI 수치가 다른 두 반응은 초안으로 보관합니다. [문헌 등록 결과와 페이지별 근거](docs/literature-import.md)를 확인하세요. 실제 데이터가 있으면 반응 지도는 데모를 기본으로 숨기며, 논문별 필터·원문 페이지 이동·자료 안 검색·DOI 및 본문/SI 연결을 지원합니다.

## 받은 논문 6개로 예제 불러오기

1. 프로젝트 폴더 안에 `papers` 폴더를 만들고, 아래 원본 파일 6개를 넣습니다. 원본 PDF와 로컬 DB는 각 컴퓨터에 보관하며 GitHub ZIP에는 포함하지 않습니다.
   - `science.1161976.pdf`, `nicewicz.som.pdf`
   - `science.1255525.pdf`, `zuo.sm.pdf`
   - `nature17431.pdf`, `41586_2016_BFnature17431_MOESM219_ESM.pdf`
2. 앱 서버를 실행해 둡니다. **새 터미널**을 같은 프로젝트 폴더에서 열고 아래 명령을 실행합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe scripts\import_literature.py
```

Mac/Linux:

```bash
.venv/bin/python scripts/import_literature.py
```

3. 브라우저를 새로고침하면 문헌 자료 6개, 분자 14개, 반응 6개가 등록됩니다. 이 중 검토 완료 기록 4개는 기본 경로 탐색에 포함되고, 수치가 불일치하는 초안 2개는 ‘검토 전 초안 포함’을 선택할 때 탐색합니다.

다른 폴더에 PDF가 있다면 명령 뒤에 `--attachments-dir "PDF가 있는 폴더 경로"`를 붙입니다. 이미 등록된 자료와 반응은 재사용합니다.

## 범위

- FastAPI, RDKit, PyMuPDF / React, TypeScript, React Flow / SQLite.
- RDKit이 SMILES를 검증하고 입체화학을 포함한 canonical SMILES·InChIKey·구조 그림을 생성합니다.
- PDF 텍스트 추출과 키워드 기반 후보 문장 탐색을 제공합니다. 스캔 PDF의 OCR, 반응식 이미지 인식, LLM 자동 추출은 아직 연결하지 않았습니다. 텍스트가 없는 PDF는 화면에 표시됩니다.
- 경로 탐색은 저장된 반응의 역방향 연결입니다. 새로운 반응 예측, 조건 호환성 검증, 전체 경로의 실험 재현성을 보장하지 않습니다. 초안은 기본 탐색에서 제외됩니다.
- 구매 상태는 사용자가 입력하는 메타데이터입니다. 공급사·가격 조회는 연결하지 않았습니다.
- 로컬 단일 사용자용입니다. 로그인·팀 권한·공개 서버 배포는 별도 구현이 필요합니다.
- 외부 AI 서비스로 파일을 전송하지 않습니다. 자료와 DB는 기본적으로 `.data/`에 보관됩니다. 이 디렉터리를 백업하면 로컬 기록을 보존할 수 있습니다.

`CHEMBRAIN_DATA_DIR`로 데이터 경로, `CHEMBRAIN_PORT`로 서버 포트를 지정할 수 있습니다. 예시 데이터는 새 DB 생성 시 한 번만 들어갑니다. `CHEMBRAIN_SEED_DEMO=0`으로 비활성화할 수 있습니다.

## 개발·검증

```bash
.venv/bin/python -m pytest -q
npm run build
```

API 문서는 실행 중 `/docs`에서 확인할 수 있습니다. 추천 논문과 업로드 순서는 [docs/example-papers.md](docs/example-papers.md), 구조 설명은 [docs/architecture.md](docs/architecture.md)를 참고하세요.

선택적 브라우저 통합 검증은 Playwright와 시스템 Chromium이 있는 Python에서 `python3 scripts/browser_smoke.py`로 실행합니다. 실제 연구 데이터와 분리된 임시 DB를 사용하며 데스크톱·모바일 화면, 업로드·등록·경로·내보내기를 검증합니다. `CHROMIUM_PATH`로 브라우저 실행 파일을 지정할 수 있습니다.

Python 의존성을 의도적으로 변경할 때는 `requirements.txt`를 수정한 뒤 `uv pip compile requirements.txt --python-version 3.12 --universal --generate-hashes -o requirements.lock`으로 잠금을 갱신하세요. 설치는 해시 검증을 유지합니다. Node 의존성은 `package-lock.json`으로 고정됩니다.
