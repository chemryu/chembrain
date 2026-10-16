# 사용자 제공 논문 등록 결과

본문 3개, 보충자료 3개(총 251 PDF 페이지)를 로컬 자료 보관함에 저장했습니다. 아래 대표 반응 6개를 구조·분자식·원문 문장·선택한 표/구조 그림과 대조했습니다. 전체 논문의 모든 기질을 추출한 데이터셋은 아닙니다. 원본 PDF는 Git에 포함하지 않고 `.data/uploads/`에서 보관합니다.

| 문헌·사례 | 수율 표시값 | 상태 | 주 근거 (1부터 시작하는 PDF 페이지) |
|---|---:|---|---|
| Nicewicz 2008, Table 1 entry 3 | SI 93% | 추가 검토 초안 | `nicewicz.som.pdf` p.3, 5–6; 본문 p.3 |
| Nicewicz 2008, Table 1 entry 4 | SI 85% | 추가 검토 초안 | `nicewicz.som.pdf` p.3, 6–7; 본문 p.3 |
| Zuo 2014, Fig. 3 compound 10 (p-tolyl) | 78% | 기록 검토 완료 | `zuo.sm.pdf` p.5, 7; 본문 p.2 |
| Zuo 2014, Fig. 3 compound 14 (p-acetylphenyl) | 86% | 기록 검토 완료 | `zuo.sm.pdf` p.5, 10; 본문 p.2 |
| Horn 2016, compound 6 (tert-butyl) | 52% | 기록 검토 완료 | SI p.6–7, 45 |
| Horn 2016, compound 7 (phenyl) | 55% | 기록 검토 완료 | SI p.6–7, 45 |

새 문헌 분자는 총 14개이며, 구매·재고 상태는 모두 미확인입니다. 기존 데모 데이터는 보존했습니다. 실제 문헌 반응이 있으면 앱을 새로 열 때 데모를 기본으로 숨깁니다. ‘기록 검토 완료’는 문헌 전사와 구조 대응을 검토했다는 뜻이며 실험의 독립 재현을 뜻하지 않습니다.

## 확인한 불일치와 예외

- **Nicewicz entry 3:** 본문 Table 1은 92% yield, 90% ee이며 SI 개별 절차는 93% yield, 91% ee입니다. 표와 SI를 각각 보존하고 원인은 확정하지 않았습니다.
- **Nicewicz entry 4:** 본문은 83% yield, SI는 85% yield입니다. ee는 두 곳 모두 95%입니다.
- 위 두 반응은 `draft`라서 기본 경로 탐색에서 제외됩니다. ‘검토 전 초안 포함’을 선택하면 수치 차이 메모와 함께 탐색할 수 있습니다. 수율을 평균내거나 높은 값을 확정값으로 간주하지 않았습니다.
- Nicewicz 생성물은 SI의 `(R)` 명칭·그림·분자식에 대응하는 SMILES를 만들고 RDKit CIP `R`을 확인했습니다. 구조는 주생성물을 나타내며 실제 시료의 ee는 별도 반응 조건에 기록합니다.
- **Zuo Procedure A:** 두 개의 26 W 형광등, 72 h, Boc-Pro-OH 1.5 equiv를 기록했습니다. Procedure B의 34 W blue LED·아미노산 3 equiv 조건을 섞지 않았습니다. 본문 Fig. 3의 생성물 `(±)` 표기를 보존했습니다.
- **Horn compound 6:** 일반 용매 acetone을 그대로 적용하지 않고 개별 절차의 **MeCN 3 mL** 예외를 기록했습니다. compound 7은 일반 acetone 조건입니다.
- `10 mA/mmol`은 기질량 기준 전류입니다. `mA/cm²` 전류밀도로 변환하지 않았습니다. 소규모 RVC 전극·LiClO₄ 조건을 대규모 graphite·LiBF₄ 조건과 구분했습니다.
- 고정 시간·전하량·광자속·정확한 파장 등 선택한 절차에 없는 값은 채우지 않았습니다.
- Nicewicz와 Zuo 본문 PDF에는 앞뒤 논문의 일부도 들어 있습니다. 첫 DOI만 읽어 논문을 식별하지 않았습니다.

## 앱에서 확인

1. 반응 지도의 **논문 필터**로 세 논문 중 하나를 선택합니다.
2. 반응의 원문 근거를 누르면 해당 **PDF 페이지**로 이동합니다. ‘원본 열기’도 같은 페이지를 가리킵니다.
3. 자료 안 검색으로 `MeCN`, `General Procedure A`, `yield` 같은 표현을 찾을 수 있습니다. 그림 안 문자는 추출 텍스트 검색에 잡히지 않을 수 있습니다.
4. 각 자료의 DOI·서지 정보와 연결된 본문/SI를 확인하고 편집할 수 있습니다.
5. Markdown 내보내기에는 원문 페이지, 문헌 링크, 근거 위치와 수치 차이 메모가 포함됩니다. 원본 PDF는 이 ZIP에 포함하지 않습니다.

## 재현 및 데이터 보존

등록 전 SQLite 백업은 `.data/backups/`, 등록 ID와 재실행 결과는 `.data/curations/uploaded-literature-report.json`에 있습니다. `.data/` 전체를 백업하면 원본과 DB를 함께 보존할 수 있습니다.

검토한 반응은 [examples/uploaded-literature.json](../examples/uploaded-literature.json)에 저장했습니다. 원본 파일은 사용자 업로드이므로 별도로 유지해야 합니다. API 실행 후 다음 명령으로 다시 등록할 수 있습니다.

```bash
.venv/bin/python scripts/import_literature.py --attachments-dir /workspace/attachments
```

도구는 모든 파일의 SHA-256, 인용 페이지/문장, 분자식, 지정된 CIP를 먼저 검사합니다. 기존 파일·구조·같은 반응을 재사용하며, 재실행 시 사용자가 수정한 반응 기록과 서지 정보를 덮어쓰지 않습니다. 다른 버전 PDF는 체크섬 불일치로 중단합니다.

이번에 선택한 6개 반응 사이에 보고된 연속 합성 경로가 있다고 가정하지 않습니다. 서로 다른 문헌의 생성물·출발물질이 실제로 일치하고 조건 적합성도 확인될 때 다단계 연결을 추가해야 합니다.
