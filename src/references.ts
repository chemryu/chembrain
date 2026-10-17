import type { Evidence, Source } from "./types";

export type PaperReference = {
  key: string;
  doi: string;
  source?: Source;
  citations: { evidence: Evidence; source?: Source }[];
};

/** Presentation grouping only: evidence records and source IDs remain untouched. */
export function normalizeReferenceDoi(doi?: string): string {
  return (doi || "").trim().replace(/^(?:https?:\/\/(?:dx\.)?doi\.org\/|doi:\s*)/i, "").trim().toLowerCase();
}

export function groupPaperReferences(evidence: Evidence[], sources: Source[]): PaperReference[] {
  const byId = new Map(sources.map((source) => [source.id, source]));
  const groups = new Map<string, PaperReference>();
  for (const item of evidence) {
    const source = byId.get(item.source_id);
    const doi = normalizeReferenceDoi(source?.doi);
    const key = doi ? `doi:${doi}` : `source:${item.source_id}`;
    let group = groups.get(key);
    if (!group) {
      group = { key, doi, source, citations: [] };
      groups.set(key, group);
    } else if (source?.document_role === "main" && group.source?.document_role !== "main") {
      group.source = source;
    }
    group.citations.push({ evidence: item, source });
  }
  return [...groups.values()];
}
