import { useState, type FormEvent } from "react";
import { Check, LoaderCircle } from "lucide-react";
import { api, json } from "./api";
import type { Source, SourceDetail } from "./types";

export const documentRoles = {
  main: "Main article",
  supplement: "Supporting information",
  notes: "Lab notes",
  other: "Other",
};

export function SourceMetadataForm({
  source,
  sources,
  doiRequired,
  onSaved,
}: {
  source: SourceDetail;
  sources: Source[];
  doiRequired: boolean;
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
          : "Unable to save the reference.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="source-metadata-form" onSubmit={submit}>
      <label>
        Reference title
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
            required={doiRequired}
            maxLength={200}
            aria-describedby={doiRequired ? "source-doi-help" : undefined}
          />
        </label>
        <label>
          Document type
          <select
            name="document_role"
            aria-label="Document type"
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
      {doiRequired && (
        <small id="source-doi-help">
          A DOI is required because this reference or a linked reaction relies on its DOI link.
        </small>
      )}
      <label>
        Citation
        <input
          name="citation"
          defaultValue={source.citation || ""}
          placeholder="Authors · year · journal · volume · pages"
          maxLength={2000}
        />
      </label>
      <fieldset>
        <legend>Related references</legend>
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
        Reference notes
        <textarea
          name="notes"
          defaultValue={source.notes || ""}
          rows={3}
          placeholder="Page numbering or disagreements between the article and SI"
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
        Save reference
      </button>
    </form>
  );
}

export const doiUrl = (doi: string) =>
  `https://doi.org/${doi.split("/").map(encodeURIComponent).join("/")}`;
