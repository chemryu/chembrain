import { useState, type FormEvent } from "react";
import { Check, LoaderCircle } from "lucide-react";
import { api, json } from "./api";
import type { Source, SourceDetail } from "./types";

export const documentRoles = {
  main: "본문",
  supplement: "보충자료 · SI",
  notes: "실험 노트",
  other: "기타 자료",
};

export function SourceMetadataForm({
  source,
  sources,
  onSaved,
}: {
  source: SourceDetail;
  sources: Source[];
  onSaved: (source: SourceDetail) => Promise<void>;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    try {
      const result = await api<SourceDetail>(
        `/sources/${source.id}/metadata`,
        json(
          {
            title: data.get("title"),
            doi: data.get("doi"),
            citation: data.get("citation"),
            document_role: data.get("document_role"),
            notes: data.get("notes"),
            related_source_ids: data.getAll("related"),
          },
          "PUT",
        ),
      );
      await onSaved(result);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "서지 정보를 저장하지 못했습니다.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="source-metadata-form" onSubmit={submit}>
      <label>
        자료 제목
        <input
          name="title"
          defaultValue={source.title}
          maxLength={500}
          required
        />
      </label>
      <div className="form-grid">
        <label>
          DOI
          <input
            name="doi"
            defaultValue={source.doi || ""}
            placeholder="10.1126/science.1255525"
          />
        </label>
        <label>
          자료 구분
          <select
            name="document_role"
            aria-label="자료 구분"
            defaultValue={source.document_role || "other"}
          >
            {Object.entries(documentRoles).map(([id, label]) => (
              <option key={id} value={id}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        서지 표기
        <input
          name="citation"
          defaultValue={source.citation || ""}
          placeholder="저자 · 연도 · 학술지 · 권 · 페이지"
          maxLength={2000}
        />
      </label>
      <fieldset>
        <legend>같은 논문의 연결 자료</legend>
        {sources
          .filter((s) => s.id !== source.id && !s.is_demo)
          .map((s) => (
            <label className="check-label" key={s.id}>
              <input
                type="checkbox"
                name="related"
                value={s.id}
                defaultChecked={source.related_source_ids?.includes(s.id)}
              />
              {s.title}
            </label>
          ))}
      </fieldset>
      <label>
        자료 검토 메모
        <textarea
          name="notes"
          defaultValue={source.notes || ""}
          rows={3}
          placeholder="인쇄 페이지와 PDF 페이지 차이, 표·SI 불일치 등"
        />
      </label>
      {error && (
        <div className="alert error" role="alert">
          {error}
        </div>
      )}
      <button className="button primary small" disabled={busy}>
        {busy ? (
          <LoaderCircle size={14} className="spin" />
        ) : (
          <Check size={14} />
        )}
        서지 정보 저장
      </button>
    </form>
  );
}
