import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { createPortal } from "react-dom";
import {
  ArrowDownToLine,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  ExternalLink,
  FileText,
  FlaskConical,
  GitBranch,
  Hexagon,
  Layers3,
  LoaderCircle,
  Microscope,
  Network,
  Plus,
  Search,
  Sparkles,
  X,
} from "lucide-react";
import { api, json } from "./api";
import { Graph } from "./Graph";
import { SourceMetadataForm, documentRoles, doiUrl } from "./SourceMetadata";
import {
  availability,
  evidencePageLabel,
  categories,
  type Category,
  type Evidence,
  type Molecule,
  type Reaction,
  type Route,
  type RouteNode,
  type SourceDetail,
  type Workspace,
} from "./types";
import "./styles.css";

type View = "graph" | "sources" | "routes" | "molecules";
type Modal =
  | { kind: "molecule"; molecule?: Molecule }
  | { kind: "reaction"; reaction?: Reaction; evidence?: Evidence }
  | null;
const emptyWorkspace: Workspace = { molecules: [], reactions: [], sources: [] };
const errorText = (error: unknown) =>
  error instanceof Error ? error.message : "Unable to process the request.";

function App() {
  const [workspace, setWorkspace] = useState<Workspace>(emptyWorkspace);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>("graph");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<Category | "all">("all");
  const [paperFilter, setPaperFilter] = useState("all");
  const [showDemo, setShowDemo] = useState(true);
  const [selected, setSelected] = useState<string | null>("demo-acylation");
  const [source, setSource] = useState<SourceDetail | null>(null);
  const sourceRequest = useRef(0);
  const [modal, setModal] = useState<Modal>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [sourceLoading, setSourceLoading] = useState(false);

  async function reload() {
    const data = await api<Workspace>("/workspace");
    setWorkspace(data);
    return data;
  }
  useEffect(() => {
    reload()
      .then((data) => {
        const firstReal = data.reactions.find((r) => !r.is_demo);
        if (firstReal) {
          setShowDemo(false);
          setSelected(firstReal.id);
        }
      })
      .catch((e) => setError(errorText(e)))
      .finally(() => setLoading(false));
  }, []);
  useEffect(() => {
    if (notice) {
      const id = setTimeout(() => setNotice(""), 5000);
      return () => clearTimeout(id);
    }
  }, [notice]);
  async function openSource(id: string) {
    const request = ++sourceRequest.current;
    setView("sources");
    setSource(null);
    setSourceLoading(true);
    try {
      const detail = await api<SourceDetail>(`/sources/${id}`);
      if (request === sourceRequest.current) {
        setSource(detail);
      }
    } catch (e) {
      setError(errorText(e));
    } finally {
      if (request === sourceRequest.current) setSourceLoading(false);
    }
  }
  const visible = useMemo(() => {
    const molecules = workspace.molecules.filter((m) => showDemo || !m.is_demo);
    const ids = new Set(molecules.map((m) => m.id));
    const query = search.trim().toLowerCase();
    const matchingMolecules = new Set(
      molecules
        .filter((m) =>
          [m.name, m.smiles, m.inchikey, ...m.aliases].some((s) =>
            s.toLowerCase().includes(query),
          ),
        )
        .map((m) => m.id),
    );
    const reactions = workspace.reactions.filter(
      (r) =>
        (showDemo || !r.is_demo) &&
        (paperFilter === "all" ||
          r.evidence.some(
            (e) =>
              workspace.sources.find((s) => s.id === e.source_id)?.doi ===
              paperFilter,
          )) &&
        (category === "all" || r.category === category) &&
        r.reactants.concat(r.products).every((id) => ids.has(id)) &&
        (!query ||
          r.name.toLowerCase().includes(query) ||
          [...r.reactants, ...r.products].some((id) =>
            matchingMolecules.has(id),
          )),
    );
    const connected = new Set(
      reactions.flatMap((r) => [...r.reactants, ...r.products]),
    );
    return {
      molecules: molecules.filter(
        (m) =>
          connected.has(m.id) ||
          (category === "all" &&
            paperFilter === "all" &&
            (!query || matchingMolecules.has(m.id))),
      ),
      reactions,
    };
  }, [workspace, showDemo, search, category, paperFilter]);
  const selectedMolecule = visible.molecules.find((m) => m.id === selected);
  const selectedReaction = visible.reactions.find((r) => r.id === selected);
  const userSources = workspace.sources.filter((s) => !s.is_demo);
  const nav = [
    { id: "graph" as View, label: "Reaction map", icon: Network },
    { id: "sources" as View, label: "Paper library", icon: BookOpen },
    { id: "routes" as View, label: "Find routes", icon: GitBranch },
    { id: "molecules" as View, label: "Molecule library", icon: Hexagon },
  ];
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setView("graph");
          }}
        >
          <span className="brand-mark">
            <Hexagon size={24} />
            <span />
          </span>
          chembrain<span className="brand-dot">.</span>
        </a>
        <div className="workspace-label">RESEARCH WORKSPACE</div>
        <button
          className="workspace-switch"
          onClick={() => {
            setView("graph");
            setSearch("");
            setCategory("all");
          }}
        >
          <span className="workspace-avatar">C</span>
          <span>
            My lab<small>Local workspace</small>
          </span>
          <ChevronDown size={14} />
        </button>
        <nav>
          {nav.map((item) => (
            <button
              className={view === item.id ? "nav-item active" : "nav-item"}
              onClick={() => {
                setView(item.id);
                setSearch("");
              }}
              key={item.id}
            >
              <item.icon size={18} />
              {item.label}
              {item.id === "sources" && (
                <span className="nav-count">{userSources.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-divider" />
        <div className="workspace-label">REACTION COLLECTIONS</div>
        {Object.entries(categories).map(([id, item]) => (
          <button
            className="collection"
            key={id}
            onClick={() => {
              setCategory(id as Category);
              setView("graph");
            }}
          >
            <span style={{ background: item.color }} />
            {item.label}
            <small>
              {
                workspace.reactions.filter(
                  (r) => r.category === id && (showDemo || !r.is_demo),
                ).length
              }
            </small>
          </button>
        ))}
        <div className="sidebar-bottom">
          <div className="local-status">
            <span />
            Saved locally<small>SQLite · No external AI uploads</small>
          </div>
          <a className="export-link" href="/api/export">
            <ArrowDownToLine size={16} />
            Export Markdown
          </a>
          <div className="profile">
            <span>R</span>
            <div>
              Researcher<small>Personal workspace</small>
            </div>
            <Microscope size={17} />
          </div>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            My lab<span>/</span>
            <strong>{nav.find((n) => n.id === view)?.label}</strong>
          </div>
          <div className="topbar-right">
            <span className="version">LOCAL · v0.2</span>
            <button
              className="button small"
              onClick={() => {
                setView("sources");
                setSource(null);
              }}
            >
              <Plus size={15} />
              Add paper
            </button>
          </div>
        </header>
        <div className="page-heading">
          <div>
            <div className="eyebrow">CONNECT THE CHEMISTRY</div>
            <h1>
              {view === "graph"
                ? "Where ideas become reactions"
                : view === "sources"
                  ? "A reference for every connection"
                  : view === "routes"
                    ? "From target to starting materials"
                    : "Your molecular library"}
            </h1>
            <p>
              {view === "graph"
                ? "Explore molecules, reactions and the possibilities between them."
                : view === "sources"
                  ? "Keep paper citations and DOI links beside your reaction records."
                  : view === "routes"
                    ? "Connect recorded reactions and compare possible synthesis routes."
                    : "Connect molecules by structure and find them by name or alias."}
            </p>
          </div>
          <button
            className="button primary"
            onClick={() =>
              setModal({ kind: view === "molecules" ? "molecule" : "reaction" })
            }
          >
            <Plus size={17} />
            {view === "molecules" ? "Add molecule" : "Add reaction"}
          </button>
        </div>
        {error && (
          <div className="alert error" role="alert">
            {error}
            <button aria-label="Dismiss error" onClick={() => setError("")}>
              <X size={16} />
            </button>
          </div>
        )}
        {notice && (
          <div className="toast" role="status">
            <CheckCircle2 size={17} />
            {notice}
          </div>
        )}
        {loading ? (
          <div className="loading">
            <LoaderCircle className="spin" />
            Loading workspace
          </div>
        ) : (
          <>
            <div className="stats-row">
              <Stat
                label="Molecules"
                value={
                  workspace.molecules.filter((m) => showDemo || !m.is_demo)
                    .length
                }
                icon={<Hexagon size={18} />}
                note="Connected by chemical structure"
              />
              <Stat
                label="Reaction records"
                value={
                  workspace.reactions.filter((r) => showDemo || !r.is_demo)
                    .length
                }
                icon={<FlaskConical size={18} />}
                note="Conditions with references"
              />
              <Stat
                label="References"
                value={userSources.length}
                icon={<FileText size={18} />}
                note="Citations and DOI links"
              />
              <div className="insight">
                <Sparkles size={20} />
                <div>
                  Connect small discoveries
                  <br />
                  <strong>Find your next reaction.</strong>
                </div>
                <span className="insight-orbit">⌬</span>
              </div>
            </div>
            {view === "graph" && (
              <>
                <div className="graph-toolbar">
                  <div className="filter-tabs">
                    <button
                      className={category === "all" ? "selected" : ""}
                      onClick={() => setCategory("all")}
                    >
                      All reactions
                    </button>
                    {Object.entries(categories).map(([id, c]) => (
                      <button
                        className={category === id ? "selected" : ""}
                        key={id}
                        onClick={() => setCategory(id as Category)}
                      >
                        <span
                          className="small-dot"
                          style={{ background: c.color }}
                        />
                        {c.label}
                      </button>
                    ))}
                  </div>
                  {workspace.sources.some((s) => s.doi) && (
                    <select
                      className="paper-select"
                      aria-label="Paper filter"
                      value={paperFilter}
                      onChange={(e) => setPaperFilter(e.target.value)}
                    >
                      <option value="all">All papers</option>
                      {workspace.sources
                        .filter((s) => s.doi && s.document_role === "main")
                        .map((s) => (
                          <option key={s.id} value={s.doi}>
                            {s.citation || s.title}
                          </option>
                        ))}
                    </select>
                  )}
                  <SearchBox
                    value={search}
                    onChange={setSearch}
                    placeholder="Search molecules, reactions, SMILES"
                  />
                </div>
                <div className="graph-workspace">
                  <section className="graph-canvas">
                    <div className="canvas-top">
                      <span>
                        <Network size={14} />
                        REACTION NETWORK
                      </span>
                      <label className="check-label">
                        <input
                          type="checkbox"
                          checked={showDemo}
                          onChange={(e) => setShowDemo(e.target.checked)}
                        />
                        Include demos
                      </label>
                    </div>
                    {visible.molecules.length ? (
                      <Graph
                        molecules={visible.molecules}
                        reactions={visible.reactions}
                        selected={selected}
                        onSelect={setSelected}
                      />
                    ) : (
                      <Empty
                        icon={<Network size={32} />}
                        title={
                          search
                            ? "No matching results"
                            : "Create your first connection"
                        }
                        text="Add molecules and reaction records to build your map."
                        action={
                          <button
                            className="button"
                            onClick={() => setModal({ kind: "molecule" })}
                          >
                            <Plus size={15} />
                            Add molecule
                          </button>
                        }
                      />
                    )}
                    <div className="canvas-bottom">
                      <span>
                        <span className="small-dot" />
                        {visible.molecules.length} molecules
                        <span className="dot-separator">·</span>
                        {visible.reactions.length} reactions
                      </span>
                      <span>Drag to pan · Scroll to zoom</span>
                    </div>
                  </section>
                  <aside className="inspector">
                    {selectedReaction ? (
                      <ReactionDetail
                        reaction={selectedReaction}
                        workspace={workspace}
                        onSource={openSource}
                        onSelect={setSelected}
                        onEdit={() =>
                          setModal({
                            kind: "reaction",
                            reaction: selectedReaction,
                          })
                        }
                      />
                    ) : selectedMolecule ? (
                      <MoleculeDetail
                        molecule={selectedMolecule}
                        onEdit={() =>
                          setModal({
                            kind: "molecule",
                            molecule: selectedMolecule,
                          })
                        }
                        workspace={workspace}
                        onSelect={setSelected}
                      />
                    ) : (
                      <Empty
                        icon={<Layers3 size={28} />}
                        title="Explore a connection"
                        text="Select a molecule or reaction to see its structure, conditions and DOI references."
                      />
                    )}
                  </aside>
                </div>
                <div className="footnote">
                  <BookOpen size={14} />
                  Demo records illustrate the app. Check the literature or your
                  experimental records before entering conditions and yields.
                </div>
              </>
            )}
            {view === "sources" && (
              <Sources
                workspace={workspace}
                source={source}
                loading={sourceLoading}
                onOpen={openSource}
                onBack={() => setSource(null)}
                onUpdated={async (detail) => {
                  setSource(detail);
                  await reload();
                  setNotice("Reference saved.");
                }}
              />
            )}
            {view === "molecules" && (
              <>
                <div className="section-toolbar">
                  <h2>
                    Registered molecules{" "}
                    <span>{workspace.molecules.length}</span>
                  </h2>
                  <SearchBox
                    value={search}
                    onChange={setSearch}
                    placeholder="Search names, aliases, SMILES"
                  />
                </div>
                <div className="molecule-grid">
                  {workspace.molecules
                    .filter((m) =>
                      [m.name, ...m.aliases, m.smiles, m.inchikey].some((s) =>
                        s.toLowerCase().includes(search.toLowerCase()),
                      ),
                    )
                    .map((m) => (
                      <button
                        className="molecule-tile"
                        key={m.id}
                        onClick={() => {
                          setView("graph");
                          setCategory("all");
                          setPaperFilter("all");
                          setShowDemo(true);
                          setSelected(m.id);
                          setSearch("");
                        }}
                      >
                        <div className="tile-top">
                          <span className="mono">{m.formula}</span>
                          {m.is_demo && <DemoBadge />}
                        </div>
                        <img
                          src={`/api/molecules/${m.id}/svg?v=${encodeURIComponent(m.smiles)}`}
                          alt={`${m.name} structure`}
                        />
                        <h3>{m.name}</h3>
                        <p>{m.aliases.join(" · ") || "No aliases"}</p>
                        <footer>
                          <span>{m.molecular_weight} g/mol</span>
                          <ArrowRight size={16} />
                        </footer>
                      </button>
                    ))}
                </div>
                {!workspace.molecules.length && (
                  <Empty
                    title="Add your first molecule"
                    text="Enter a SMILES string to generate a structure and identifiers."
                  />
                )}
              </>
            )}
            {view === "routes" && (
              <RouteExplorer
                workspace={workspace}
                onSelect={(id) => {
                  setSelected(id);
                  setCategory("all");
                  setPaperFilter("all");
                  setShowDemo(true);
                  setSearch("");
                  setView("graph");
                }}
              />
            )}
          </>
        )}
      </main>
      {modal && (
        <ModalShell
          title={
            modal.kind === "molecule"
              ? modal.molecule
                ? "Edit molecule"
                : "Add molecule"
              : modal.reaction
                ? "Edit reaction record"
                : "New reaction record"
          }
          onClose={() => setModal(null)}
        >
          {modal.kind === "molecule" ? (
            <MoleculeForm
              initial={modal.molecule}
              structureLocked={
                !!modal.molecule &&
                workspace.reactions.some((r) =>
                  [...r.reactants, ...r.products].includes(modal.molecule!.id),
                )
              }
              onSaved={async () => {
                await reload();
                setModal(null);
                setNotice(
                  modal.molecule
                    ? "Molecule updated."
                    : "Molecule added to the library.",
                );
              }}
            />
          ) : (
            <ReactionForm
              workspace={workspace}
              initial={modal.reaction}
              evidence={modal.evidence}
              onMoleculeAdded={async () => {
                await reload();
              }}
              onSaved={async (id) => {
                await reload();
                setModal(null);
                setSelected(id);
                setSearch("");
                setCategory("all");
                setPaperFilter("all");
                setShowDemo(true);
                setView("graph");
                setNotice("Reaction record saved.");
              }}
            />
          )}
        </ModalShell>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  icon,
  note,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  note: string;
}) {
  return (
    <div className="stat">
      <div className="stat-label">
        {label}
        <span>{icon}</span>
      </div>
      <strong>{String(value).padStart(2, "0")}</strong>
      <small>{note}</small>
    </div>
  );
}
function SearchBox({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (s: string) => void;
  placeholder: string;
}) {
  return (
    <label className="search">
      <Search size={16} />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
      />
      {value && (
        <button onClick={() => onChange("")} aria-label="Clear search">
          <X size={14} />
        </button>
      )}
    </label>
  );
}
function Empty({
  icon,
  title,
  text,
  action,
}: {
  icon?: React.ReactNode;
  title: string;
  text: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="empty">
      {icon}
      <h3>{title}</h3>
      <p>{text}</p>
      {action}
    </div>
  );
}
function DemoBadge() {
  return <span className="badge demo">DEMO · Not experimentally verified</span>;
}
function ReactionDetail({
  reaction: r,
  workspace,
  onSource,
  onSelect,
  onEdit,
}: {
  reaction: Reaction;
  workspace: Workspace;
  onSource: (id: string, page?: number) => void;
  onSelect: (id: string) => void;
  onEdit: () => void;
}) {
  return (
    <>
      <div className="inspector-heading">
        <span>REACTION DETAILS</span>
        <FlaskConical size={17} />
      </div>
      <div className="reaction-title">
        <span
          className="category-badge"
          style={{ color: categories[r.category].color }}
        >
          {categories[r.category].label}
        </span>
        <h2>{r.name}</h2>
        <div className="badge-row">
          {r.is_demo ? (
            <DemoBadge />
          ) : (
            <span
              className={`badge ${r.status === "reviewed" ? "reviewed" : ""}`}
            >
              {r.status === "reviewed" ? "Record reviewed" : "Draft"}
            </span>
          )}
          <span className="muted">{r.evidence.length} references</span>
        </div>
      </div>
      <div className="inspector-section">
        <h4>Reaction participants</h4>
        <div className="reaction-equation">
          {r.reactants.map((id, i) => (
            <React.Fragment key={id}>
              {i > 0 && <span>+</span>}
              <button onClick={() => onSelect(id)}>
                {workspace.molecules.find((m) => m.id === id)?.name}
              </button>
            </React.Fragment>
          ))}
          <ArrowRight size={16} />
          {r.products.map((id) => (
            <button
              className="product-pill"
              key={id}
              onClick={() => onSelect(id)}
            >
              {workspace.molecules.find((m) => m.id === id)?.name}
            </button>
          ))}
        </div>
      </div>
      <div className="inspector-section">
        <h4>Experimental conditions</h4>
        {r.reagents && (
          <p className="detail-note">Reagents and catalysts: {r.reagents}</p>
        )}
        <dl className="conditions">
          {Object.entries(r.conditions)
            .filter(([, v]) => v)
            .map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{v}</dd>
              </div>
            ))}
          <div>
            <dt>Yield</dt>
            <dd>
              {r.yield_percent == null ? "Not reported" : `${r.yield_percent}%`}
            </dd>
          </div>
        </dl>
        {!Object.values(r.conditions).some(Boolean) && (
          <p className="subtle-text">
            Check the referenced paper and enter its reported conditions.
          </p>
        )}
      </div>
      <div className="inspector-section">
        <h4>
          References <span>{r.evidence.length}</span>
        </h4>
        {r.evidence.map((e, i) => {
          const reference = workspace.sources.find((s) => s.id === e.source_id);
          const content = (
            <>
              <div>
                <BookOpen size={14} />
                {reference?.title}
                <ExternalLink size={12} />
              </div>
              <small>
                {evidencePageLabel(e, reference)}
                {e.locator && ` · ${e.locator}`}
              </small>
              <span className="source-doi">
                {reference?.doi || "Reference metadata"}
              </span>
            </>
          );
          return reference?.doi ? (
            <a
              className="evidence-card"
              key={i}
              href={doiUrl(reference.doi)}
              target="_blank"
              rel="noreferrer"
            >
              {content}
            </a>
          ) : (
            <button
              className="evidence-card"
              key={i}
              onClick={() => onSource(e.source_id)}
            >
              {content}
            </button>
          );
        })}
        {!r.evidence.length && (
          <p className="subtle-text">No references linked yet.</p>
        )}
      </div>
      {r.notes && (
        <div className="inspector-section">
          <h4>Research notes</h4>
          <p className="detail-note">{r.notes}</p>
        </div>
      )}
      <div className="inspector-action">
        <button className="button full" onClick={onEdit}>
          Edit reaction record
          <ArrowRight size={15} />
        </button>
      </div>
    </>
  );
}
function MoleculeDetail({
  molecule: m,
  workspace,
  onSelect,
  onEdit,
}: {
  molecule: Molecule;
  workspace: Workspace;
  onSelect: (id: string) => void;
  onEdit: () => void;
}) {
  const related = workspace.reactions.filter((r) =>
    [...r.reactants, ...r.products].includes(m.id),
  );
  return (
    <>
      <div className="inspector-heading">
        <span>MOLECULE DETAILS</span>
        <Hexagon size={17} />
      </div>
      <div className="molecule-hero">
        <img
          src={`/api/molecules/${m.id}/svg?v=${encodeURIComponent(m.smiles)}`}
          alt={`${m.name} structure`}
        />
        <h2>{m.name}</h2>
        <p>{m.aliases.join(" · ")}</p>
        {m.is_demo && <DemoBadge />}
      </div>
      <div className="inspector-section">
        <dl className="conditions">
          <div>
            <dt>Formula</dt>
            <dd>{m.formula}</dd>
          </div>
          <div>
            <dt>Molecular weight</dt>
            <dd>{m.molecular_weight} g/mol</dd>
          </div>
          <div>
            <dt>Availability</dt>
            <dd>{availability[m.availability]}</dd>
          </div>
        </dl>
        <h4>SMILES</h4>
        <code className="structure-code">{m.smiles}</code>
        <h4>InChIKey</h4>
        <code className="structure-code">{m.inchikey}</code>
      </div>
      <div className="inspector-section">
        <h4>
          Linked reactions <span>{related.length}</span>
        </h4>
        {related.map((r) => (
          <button
            className="related-reaction"
            key={r.id}
            onClick={() => onSelect(r.id)}
          >
            <span
              className="small-dot"
              style={{ background: categories[r.category].color }}
            />
            {r.name}
            <ArrowRight size={14} />
          </button>
        ))}
      </div>
      {m.notes && (
        <div className="inspector-section">
          <h4>Notes</h4>
          <p className="detail-note">{m.notes}</p>
        </div>
      )}
      <div className="inspector-action">
        <button className="button full" onClick={onEdit}>
          Edit molecule
          <ArrowRight size={15} />
        </button>
      </div>
    </>
  );
}

function Sources({
  workspace,
  source,
  loading,
  onOpen,
  onBack,
  onUpdated,
}: {
  workspace: Workspace;
  source: SourceDetail | null;
  loading: boolean;
  onOpen: (id: string) => void;
  onBack: () => void;
  onUpdated: (source: SourceDetail) => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => setEditing(false), [source?.id]);
  async function addReference(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy(true);
    setError("");
    try {
      const created = await api<SourceDetail>(
        "/references",
        json({
          title: data.get("title"),
          doi: data.get("doi"),
          citation: data.get("citation"),
          document_role: "main",
        }),
      );
      await onUpdated(created);
      form.reset();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  if (loading)
    return (
      <div className="loading">
        <LoaderCircle className="spin" />
        Loading reference
      </div>
    );
  if (source)
    return (
      <div className="source-reader">
        <div className="section-toolbar">
          <button className="text-button" onClick={onBack}>
            <ArrowLeft size={16} />
            All papers
          </button>
          {source.doi && (
            <a
              className="button primary small"
              href={doiUrl(source.doi)}
              target="_blank"
              rel="noreferrer"
            >
              <ExternalLink size={14} />
              Open DOI
            </a>
          )}
        </div>
        <div className="source-heading">
          <span className="document-icon">
            <BookOpen size={24} />
          </span>
          <div>
            <h2>{source.title}</h2>
            <p>{source.citation || "Citation not provided"}</p>
            {source.doi && (
              <a
                className="source-doi"
                href={doiUrl(source.doi)}
                target="_blank"
                rel="noreferrer"
              >
                {source.doi}
                <ExternalLink size={12} />
              </a>
            )}
          </div>
        </div>
        <div className="source-reader-tools">
          <span className="badge">
            {documentRoles[source.document_role || "other"]}
          </span>
          <button className="text-button" onClick={() => setEditing(!editing)}>
            {editing ? "Close editor" : "Edit reference"}
          </button>
        </div>
        {editing && (
          <SourceMetadataForm
            key={source.id}
            source={source}
            sources={workspace.sources}
            onSaved={async (detail) => {
              await onUpdated(detail);
              setEditing(false);
            }}
          />
        )}
        {source.notes && (
          <div className="alert source-review-note">
            <BookOpen size={15} />
            {source.notes}
          </div>
        )}
        {!!source.related_source_ids?.length && (
          <div className="linked-sources">
            <span>Related references</span>
            {source.related_source_ids.map((id) => (
              <button key={id} onClick={() => onOpen(id)}>
                {workspace.sources.find((s) => s.id === id)?.title}
                <ArrowRight size={12} />
              </button>
            ))}
          </div>
        )}
        <h3>Linked reactions</h3>
        {workspace.reactions
          .filter((r) => r.evidence.some((e) => e.source_id === source.id))
          .map((r) => (
            <article className="candidate-card" key={r.id}>
              <h3>{r.name}</h3>
              <span className="badge">
                {r.status === "reviewed" ? "Record reviewed" : "Draft"}
              </span>
              <p>
                {r.evidence
                  .filter((e) => e.source_id === source.id)
                  .map(
                    (e) =>
                      `${evidencePageLabel(e, source)}${e.locator ? ` · ${e.locator}` : ""}`,
                  )
                  .join("; ")}
              </p>
            </article>
          ))}
      </div>
    );
  const papers = workspace.sources.filter((s) => !s.is_demo);
  return (
    <>
      <form className="source-metadata-form" onSubmit={addReference}>
        <h2>Add a paper by DOI</h2>
        <p className="subtle-text">
          Keep citations and reaction links together. No PDF download required.
        </p>
        <div className="form-grid">
          <label>
            Paper title
            <input
              name="title"
              required
              maxLength={500}
              placeholder="Author, year or article title"
            />
          </label>
          <label>
            DOI or DOI URL
            <input
              name="doi"
              required
              maxLength={200}
              placeholder="https://doi.org/10.1038/nature17431"
            />
          </label>
        </div>
        <label>
          Citation
          <input
            name="citation"
            maxLength={2000}
            placeholder="Authors · year · journal · pages"
          />
        </label>
        {error && (
          <div className="alert error" role="alert">
            {error}
          </div>
        )}
        <button className="button primary small" disabled={busy}>
          {busy ? (
            <LoaderCircle size={15} className="spin" />
          ) : (
            <Plus size={15} />
          )}
          Add reference
        </button>
      </form>
      <div className="section-toolbar">
        <h2>
          Paper library <span>{papers.length}</span>
        </h2>
        <span className="subtle-text">DOI links and citations</span>
      </div>
      <div className="source-grid">
        {papers.map((s) => (
          <article className="source-card" key={s.id}>
            <span className="document-icon">
              <BookOpen size={23} />
            </span>
            <h3>{s.title}</h3>
            <p>{s.citation || "Citation not provided"}</p>
            <span className="badge">
              {documentRoles[s.document_role || "other"]}
            </span>
            {s.doi && (
              <a
                className="source-doi"
                href={doiUrl(s.doi)}
                target="_blank"
                rel="noreferrer"
              >
                {s.doi}
                <ExternalLink size={12} />
              </a>
            )}
            <button className="text-button" onClick={() => onOpen(s.id)}>
              Reference details
              <ArrowRight size={14} />
            </button>
          </article>
        ))}
      </div>
      {!papers.length && (
        <Empty
          title="Start your paper library"
          text="Add a DOI to connect a paper to your reaction records."
        />
      )}
    </>
  );
}
function RouteExplorer({
  workspace,
  onSelect,
}: {
  workspace: Workspace;
  onSelect: (id: string) => void;
}) {
  const [target, setTarget] = useState(
    workspace.reactions.find((r) => !r.is_demo && r.status === "reviewed")
      ?.products[0] ||
      workspace.molecules.find((m) => m.id === "acetanilide")?.id ||
      workspace.molecules[0]?.id ||
      "",
  );
  const [steps, setSteps] = useState(3);
  const [drafts, setDrafts] = useState(false);
  const [routes, setRoutes] = useState<Route[] | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function run(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setRoutes(null);
    try {
      const result = await api<{ routes: Route[]; notice: string }>(
        `/routes?target=${encodeURIComponent(target)}&max_steps=${steps}&include_drafts=${drafts}`,
      );
      setRoutes(result.routes);
      setNotice(result.notice);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  const name = (id: string) =>
    workspace.molecules.find((m) => m.id === id)?.name || id;
  function tree(node: RouteNode, level = 0): React.ReactNode {
    const reaction = workspace.reactions.find((r) => r.id === node.reaction_id);
    return (
      <div
        className="route-branch"
        style={{ "--level": level } as React.CSSProperties}
        key={`${node.molecule_id}-${level}`}
      >
        <button
          className="route-molecule"
          onClick={() => onSelect(node.molecule_id)}
        >
          <Hexagon size={15} />
          {name(node.molecule_id)}
          {!reaction && (
            <small>
              {
                availability[
                  workspace.molecules.find((m) => m.id === node.molecule_id)
                    ?.availability || "unknown"
                ]
              }
            </small>
          )}
        </button>
        {reaction && (
          <>
            <button
              className="route-reaction"
              onClick={() => onSelect(reaction.id)}
            >
              <GitBranch size={14} />
              {reaction.name}
              <span>{categories[reaction.category].label}</span>
            </button>
            <div className="route-children">
              {node.children.map((child) => tree(child, level + 1))}
            </div>
          </>
        )}
      </div>
    );
  }
  return (
    <>
      <form className="route-search" onSubmit={run}>
        <div className="route-search-icon">
          <GitBranch size={25} />
        </div>
        <label>
          Target product
          <select
            aria-label="Target product"
            value={target}
            onChange={(e) => {
              setTarget(e.target.value);
              setRoutes(null);
            }}
            required
          >
            <option value="" disabled>
              Select a molecule
            </option>
            {workspace.molecules.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
                {m.is_demo ? " · Demo" : ""}
              </option>
            ))}
          </select>
        </label>
        <label>
          Maximum steps
          <select
            aria-label="Maximum steps"
            value={steps}
            onChange={(e) => {
              setSteps(Number(e.target.value));
              setRoutes(null);
            }}
          >
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <option key={n} value={n}>
                {n} steps
              </option>
            ))}
          </select>
        </label>
        <label className="check-label">
          <input
            type="checkbox"
            checked={drafts}
            onChange={(e) => {
              setDrafts(e.target.checked);
              setRoutes(null);
            }}
          />
          Include drafts
        </label>
        <button className="button primary" disabled={busy || !target}>
          {busy ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <Search size={16} />
          )}
          Find routes
        </button>
      </form>
      {error && <div className="alert error">{error}</div>}
      {routes === null ? (
        <Empty
          icon={<GitBranch size={36} />}
          title="Work backwards from a target"
          text="Connect recorded reactions with every required starting material branch."
        />
      ) : (
        <>
          <div className="section-toolbar">
            <h2>
              Candidate routes <span>{routes.length}</span>
            </h2>
            <span className="subtle-text">
              Sorted by unknown availability, then steps
            </span>
          </div>
          <div className="alert">
            <BookOpen size={16} />
            {notice}
          </div>
          {routes.map((route, i) => (
            <article className="route-card" key={i}>
              <header>
                <div>
                  <span className="route-number">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <strong>{name(route.molecule_id)}</strong>
                  <span className="badge">{route.steps} steps</span>
                </div>
                <div>
                  {route.is_demo && <DemoBadge />}
                  {route.contains_drafts && (
                    <span className="badge">Contains drafts</span>
                  )}
                </div>
              </header>
              {tree(route)}
              <footer>
                <div>
                  <strong>Required starting materials</strong>
                  {route.starting_materials.map(name).join(" · ")}
                </div>
                <span
                  className={
                    route.unknown_availability.length
                      ? "availability-warning"
                      : "availability-ok"
                  }
                >
                  {route.unknown_availability.length
                    ? `Availability unknown ${route.unknown_availability.length} materials`
                    : "Available according to your inventory"}
                </span>
              </footer>
            </article>
          ))}
          {!routes.length && (
            <Empty
              title="No connected routes"
              text="Add a reaction for this product, or adjust the draft filter and step limit."
            />
          )}
        </>
      )}
    </>
  );
}

function ModalShell({
  title,
  children,
  onClose,
}: {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
}) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const modalRef = useRef<HTMLElement>(null);
  useEffect(() => {
    const prior = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const handler = (e: KeyboardEvent) => {
      const openModals = document.querySelectorAll(".modal");
      if (openModals[openModals.length - 1] !== modalRef.current) return;
      if (e.key === "Escape") onClose();
      if (e.key === "Tab") {
        const elements = Array.from(
          modalRef.current!.querySelectorAll<HTMLElement>(
            "button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href]",
          ),
        );
        const first = elements[0],
          last = elements[elements.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        }
        if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", handler);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = previousOverflow;
      prior?.focus();
    };
  }, [onClose]);
  return (
    <div
      className="modal-overlay"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <section
        ref={modalRef}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <header>
          <div>
            <div className="eyebrow">BUILD YOUR KNOWLEDGE</div>
            <h2>{title}</h2>
          </div>
          <button
            ref={closeRef}
            className="icon-button"
            aria-label="Close dialog"
            onClick={onClose}
          >
            <X size={21} />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}
function MoleculeForm({
  onSaved,
  initial,
  structureLocked = false,
}: {
  onSaved: () => Promise<void>;
  initial?: Molecule;
  structureLocked?: boolean;
}) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    e.stopPropagation();
    const data = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      await api(
        initial ? `/molecules/${initial.id}` : "/molecules",
        json(
          {
            name: data.get("name"),
            smiles: data.get("smiles"),
            aliases: String(data.get("aliases") || "")
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
            availability: data.get("availability"),
            notes: data.get("notes"),
          },
          initial ? "PUT" : "POST",
        ),
      );
      await onSaved();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="edit-form" onSubmit={submit}>
      <p className="form-intro">
        RDKit validates the SMILES string and generates a formula and
        identifiers.
      </p>
      <label>
        Molecule name
        <input
          name="name"
          defaultValue={initial?.name}
          placeholder="e.g. Benzaldehyde"
          required
          maxLength={200}
        />
      </label>
      <label>
        SMILES
        <input
          name="smiles"
          aria-label="SMILES"
          defaultValue={initial?.smiles}
          readOnly={structureLocked}
          className="mono"
          placeholder="e.g. O=Cc1ccccc1"
          required
          maxLength={2000}
        />
        <small>
          {structureLocked
            ? "This structure is used in reactions. Add a new molecule to change its chemical identity."
            : "Duplicates are checked by chemical structure, including stereochemistry."}
        </small>
      </label>
      <div className="form-grid">
        <label>
          Aliases
          <input
            name="aliases"
            defaultValue={initial?.aliases.join(", ")}
            placeholder="Comma-separated synonyms"
          />
        </label>
        <label>
          Availability
          <select
            name="availability"
            aria-label="Availability"
            defaultValue={initial?.availability || "unknown"}
          >
            {Object.entries(availability).map(([id, label]) => (
              <option value={id} key={id}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        Research notes
        <textarea
          name="notes"
          aria-label="Research notes"
          defaultValue={initial?.notes}
          rows={3}
          placeholder="Stock location, supplier or structural notes"
        />
      </label>
      {error && (
        <div className="alert error" role="alert">
          {error}
        </div>
      )}
      <footer>
        <span className="subtle-text">
          {initial
            ? "Changes keep the same molecule ID and reaction links."
            : "New molecules are saved in your workspace."}
        </span>
        <button className="button primary" disabled={busy}>
          {busy ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <Check size={16} />
          )}
          Save molecule
        </button>
      </footer>
    </form>
  );
}
const conditionFields: Record<Category, string[]> = {
  organic: [
    "Solvent",
    "Concentration",
    "Temperature",
    "Time",
    "Atmosphere",
    "Scale",
    "Purification",
  ],
  electrochemical: [
    "Solvent",
    "Concentration",
    "Temperature",
    "Time",
    "Atmosphere",
    "Scale",
    "Purification",
    "Anode",
    "Cathode",
    "Electrolyte",
    "Potential and reference electrode",
    "Current density",
    "Charge",
    "Cell setup",
  ],
  photochemical: [
    "Solvent",
    "Concentration",
    "Temperature",
    "Time",
    "Atmosphere",
    "Scale",
    "Purification",
    "Wavelength",
    "Light source",
    "Power or photon flux",
    "Irradiation time",
    "Reactor",
  ],
};
function ReactionForm({
  workspace,
  initial,
  evidence,
  onMoleculeAdded,
  onSaved,
}: {
  workspace: Workspace;
  initial?: Reaction;
  evidence?: Evidence;
  onMoleculeAdded: () => Promise<void>;
  onSaved: (id: string) => Promise<void>;
}) {
  const [category, setCategory] = useState<Category>(
    initial?.category || "organic",
  );
  const [reactants, setReactants] = useState(initial?.reactants || []);
  const [products, setProducts] = useState(initial?.products || []);
  const [addingMolecule, setAddingMolecule] = useState(false);
  const [evidences, setEvidences] = useState<Evidence[]>(
    initial?.evidence || (evidence ? [evidence] : []),
  );
  const [sourceId, setSourceId] = useState("");
  const [page, setPage] = useState(1);
  const [locator, setLocator] = useState("");
  const [pageNumbering, setPageNumbering] = useState<
    "pdf" | "printed" | "unspecified"
  >("unspecified");
  const [sourceDetail, setSourceDetail] = useState<SourceDetail | null>(null);
  const [conditions, setConditions] = useState<Record<string, string>>(
    initial?.conditions || {},
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    setSourceDetail(null);
    setPage(1);
    setLocator("");
    if (sourceId)
      api<SourceDetail>(`/sources/${sourceId}`)
        .then((s) => {
          if (active) setSourceDetail(s);
        })
        .catch((e) => {
          if (active) setError(errorText(e));
        });
    return () => {
      active = false;
    };
  }, [sourceId]);
  const fields = [
    ...new Set([...conditionFields[category], ...Object.keys(conditions)]),
  ];
  function participant(
    label: string,
    selected: string[],
    change: (v: string[]) => void,
  ) {
    return (
      <fieldset className="participant-field">
        <legend>{label} *</legend>
        <div className="selected-pills">
          {selected.map((id) => (
            <button
              type="button"
              key={id}
              onClick={() => change(selected.filter((mid) => mid !== id))}
            >
              {workspace.molecules.find((m) => m.id === id)?.name}
              <X size={12} />
            </button>
          ))}
        </div>
        <select
          aria-label={`Add ${label}`}
          value=""
          onChange={(e) => {
            if (e.target.value) change([...selected, e.target.value]);
          }}
        >
          <option value="">Select a molecule · multiple allowed</option>
          {workspace.molecules
            .filter((m) => !selected.includes(m.id))
            .map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
                {m.is_demo ? " · Demo" : ""}
              </option>
            ))}
        </select>
      </fieldset>
    );
  }
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    if (!reactants.length || !products.length) {
      setError("Select at least one reactant and one product.");
      return;
    }
    const data = new FormData(e.currentTarget);
    setBusy(true);
    try {
      const result = await api<Reaction>(
        initial ? `/reactions/${initial.id}` : "/reactions",
        json(
          {
            name: data.get("name"),
            category,
            reactants,
            products,
            reagents: data.get("reagents"),
            conditions: Object.fromEntries(
              Object.entries(conditions).filter(([, v]) => v.trim()),
            ),
            yield_percent:
              data.get("yield") === "" ? null : Number(data.get("yield")),
            status: data.get("status"),
            evidence: evidences,
            notes: data.get("notes"),
          },
          initial ? "PUT" : "POST",
        ),
      );
      await onSaved(result.id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <form className="edit-form" onSubmit={submit}>
        <p className="form-intro">
          Enter the values and units reported in the paper. Leave unreported
          values blank.
        </p>
        <div className="form-grid">
          <label>
            Reaction name *
            <input
              name="name"
              required
              defaultValue={initial?.name}
              placeholder="e.g. Photocatalytic alcohol oxidation"
              maxLength={200}
            />
          </label>
          <label>
            Method
            <select
              aria-label="Method"
              value={category}
              onChange={(e) => setCategory(e.target.value as Category)}
            >
              {Object.entries(categories).map(([id, c]) => (
                <option key={id} value={id}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="form-section-title">
          <h3>Molecule connections</h3>
          <button
            className="text-button"
            type="button"
            onClick={() => setAddingMolecule(true)}
          >
            <Plus size={13} />
            Add new molecule
          </button>
        </div>
        <div className="form-grid">
          {participant("Reactants", reactants, setReactants)}
          {participant("Products", products, setProducts)}
        </div>
        <label>
          Reagents and catalysts
          <input
            name="reagents"
            defaultValue={initial?.reagents}
            placeholder="Names, equivalents and catalyst loading"
          />
        </label>
        <h3 className="form-section-title">Experimental conditions</h3>
        <div className="form-grid conditions-inputs">
          {fields.map((field) => (
            <label key={field}>
              {field}
              <input
                value={conditions[field] || ""}
                onChange={(e) =>
                  setConditions({ ...conditions, [field]: e.target.value })
                }
                placeholder="Not reported · include units"
              />
            </label>
          ))}
        </div>
        <div className="form-grid">
          <label>
            Yield (%)
            <input
              type="number"
              min="0"
              max="100"
              step="any"
              name="yield"
              defaultValue={initial?.yield_percent ?? ""}
              placeholder="Not reported"
            />
          </label>
          <label>
            Review status
            <select
              aria-label="Review status"
              name="status"
              defaultValue={initial?.status || "draft"}
            >
              <option value="draft">
                Draft · excluded from routes by default
              </option>
              <option value="reviewed">
                Record reviewed · reference required
              </option>
            </select>
          </label>
        </div>
        <h3 className="form-section-title">References</h3>
        {evidences.map((e, i) => (
          <div className="form-evidence" key={i}>
            <div>
              <FileText size={14} />
              {workspace.sources.find((s) => s.id === e.source_id)?.title} · p.
              {e.page}
              <button
                type="button"
                className="icon-button"
                aria-label={`Remove reference ${i + 1}`}
                onClick={() =>
                  setEvidences(evidences.filter((_, j) => j !== i))
                }
              >
                <X size={15} />
              </button>
            </div>
            <label>
              Page, figure or procedure
              <input
                value={e.locator || ""}
                onChange={(event) =>
                  setEvidences(
                    evidences.map((item, j) =>
                      j === i ? { ...item, locator: event.target.value } : item,
                    ),
                  )
                }
              />
            </label>
            <small>
              {e.citation_only
                ? "DOI citation · manually checked"
                : "Imported source evidence"}
            </small>
          </div>
        ))}
        <div className="evidence-builder">
          <div className="form-grid">
            <label>
              Reference
              <select
                aria-label="Reference"
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
              >
                <option value="">Select a reference</option>
                {workspace.sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                    {s.is_demo ? " · Demo" : ""}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Page
              <input
                type="number"
                min={1}
                max={sourceDetail?.page_count || undefined}
                value={page}
                onChange={(e) => setPage(Number(e.target.value))}
              />
            </label>
          </div>
          {sourceDetail?.doi && (
            <a
              className="source-doi"
              href={doiUrl(sourceDetail.doi)}
              target="_blank"
              rel="noreferrer"
            >
              Open DOI to check this reference
              <ExternalLink size={12} />
            </a>
          )}
          <label>
            Page numbering
            <select
              aria-label="Page numbering"
              value={pageNumbering}
              onChange={(e) =>
                setPageNumbering(e.target.value as typeof pageNumbering)
              }
            >
              <option value="unspecified">Unspecified</option>
              <option value="pdf">Original PDF page (1-based)</option>
              <option value="printed">Printed page label</option>
            </select>
          </label>
          <label>
            Page, figure or procedure
            <input
              value={locator}
              onChange={(e) => setLocator(e.target.value)}
              placeholder="e.g. SI, compound 6, p. 45"
              maxLength={300}
            />
          </label>
          <button
            className="button small"
            type="button"
            disabled={!sourceDetail?.doi || !locator.trim() || page < 1}
            onClick={() => {
              setEvidences([
                ...evidences,
                {
                  source_id: sourceId,
                  page,
                  quote: "",
                  locator,
                  citation_only: true,
                  page_numbering: pageNumbering,
                },
              ]);
              setLocator("");
            }}
          >
            <Plus size={14} />
            Add citation
          </button>
        </div>
        <label>
          Research notes
          <textarea
            name="notes"
            aria-label="Research notes"
            defaultValue={initial?.notes}
            rows={3}
            placeholder="Selectivity, purification and replication notes"
          />
        </label>
        {error && (
          <div className="alert error" role="alert">
            {error}
          </div>
        )}
        <footer>
          <span className="subtle-text">
            DOI citations record your review; no automatic text verification is
            performed.
          </span>
          <button className="button primary" disabled={busy}>
            {busy ? (
              <LoaderCircle className="spin" size={16} />
            ) : (
              <Check size={16} />
            )}
            Save reaction
          </button>
        </footer>
      </form>
      {addingMolecule &&
        createPortal(
          <ModalShell
            title="Add molecule"
            onClose={() => setAddingMolecule(false)}
          >
            <MoleculeForm
              onSaved={async () => {
                setAddingMolecule(false);
                await onMoleculeAdded();
              }}
            />
          </ModalShell>,
          document.body,
        )}
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
