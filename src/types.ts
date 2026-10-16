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
  organic: { label: "유기 합성", short: "ORGANIC", color: "#c3e88d" },
  electrochemical: { label: "전기화학", short: "ELECTRO", color: "#d9b788" },
  photochemical: { label: "광화학", short: "PHOTO", color: "#a5b8ee" },
};
export const availability = {
  in_stock: "재고 있음",
  order: "구매 가능 · 사용자 입력",
  unknown: "구매·재고 미확인",
};
