export type Category = "organic" | "electrochemical" | "photochemical";
export type Molecule = {
  id: string;
  name: string;
  smiles: string;
  inchikey: string;
  formula: string;
  molecular_weight: number;
  aliases: string[];
  availability: "in_stock" | "order" | "unknown";
  notes: string;
  is_demo: boolean;
};
export type Evidence = {
  source_id: string;
  page: number;
  quote: string;
  locator?: string;
  citation_only?: boolean;
  page_numbering?: "pdf" | "printed" | "unspecified";
};
export type Reaction = {
  id: string;
  name: string;
  category: Category;
  reactants: string[];
  products: string[];
  reagents: string;
  conditions: Record<string, string>;
  yield_percent: number | null;
  status: "draft" | "reviewed";
  evidence: Evidence[];
  notes: string;
  is_demo: boolean;
};
export type Source = {
  id: string;
  title: string;
  filename: string;
  kind: string;
  is_demo: boolean;
  page_count: number;
  text_characters: number;
  created_at: string;
  doi?: string;
  citation?: string;
  document_role?: "main" | "supplement" | "notes" | "other";
  related_source_ids?: string[];
  notes?: string;
};
export type SourceDetail = Source & {
  pages: { number: number; text: string }[];
  candidates: { page: number; text: string }[];
};
export type Workspace = {
  molecules: Molecule[];
  reactions: Reaction[];
  sources: Source[];
};
export type RouteNode = {
  molecule_id: string;
  reaction_id: string | null;
  children: RouteNode[];
  steps: number;
};
export type Route = RouteNode & {
  starting_materials: string[];
  unknown_availability: string[];
  reaction_ids: string[];
  is_demo: boolean;
  contains_drafts: boolean;
};
export const categories: Record<
  Category,
  { label: string; short: string; color: string }
> = {
  organic: { label: "Organic synthesis", short: "ORGANIC", color: "#c3e88d" },
  electrochemical: {
    label: "Electrochemistry",
    short: "ELECTRO",
    color: "#d9b788",
  },
  photochemical: { label: "Photochemistry", short: "PHOTO", color: "#a5b8ee" },
};
export const availability = {
  in_stock: "In stock",
  order: "Orderable · user reported",
  unknown: "Availability unknown",
};

export function evidencePageLabel(e: Evidence, source?: Source): string {
  if (
    e.page_numbering === "pdf" ||
    (!e.citation_only &&
      (!e.page_numbering || e.page_numbering === "unspecified") && source?.kind === "pdf")
  )
    return `Original PDF page ${e.page} (1-based; printed page labels may differ)`;
  if (e.page_numbering === "printed") return `Printed page ${e.page}`;
  return `Reference page ${e.page} (numbering unspecified)`;
}
