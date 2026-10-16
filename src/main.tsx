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
  Upload,
  X,
} from "lucide-react";
import { api, json } from "./api";
import { Graph } from "./Graph";
import { SourceMetadataForm, documentRoles } from "./SourceMetadata";
import {
  availability,
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
  | { kind: "molecule" }
  | { kind: "reaction"; reaction?: Reaction; evidence?: Evidence }
  | null;
const emptyWorkspace: Workspace = { molecules: [], reactions: [], sources: [] };
const errorText = (error: unknown) =>
  error instanceof Error ? error.message : "요청을 처리하지 못했습니다.";

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
  const [sourcePage, setSourcePage] = useState(1);
  const sourceRequest = useRef(0);
  const [modal, setModal] = useState<Modal>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [uploading, setUploading] = useState(false);
  const [sourceLoading, setSourceLoading] = useState(false);
  const uploadRef = useRef<HTMLInputElement>(null);

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
  async function openSource(id: string, page = 1) {
    const request = ++sourceRequest.current;
    setView("sources");
    setSource(null);
    setSourcePage(page);
    setSourceLoading(true);
    try {
      const detail = await api<SourceDetail>(`/sources/${id}`);
      if (request === sourceRequest.current) {
        setSource(detail);
        setSourcePage(Math.max(1, Math.min(page, detail.page_count)));
      }
    } catch (e) {
      setError(errorText(e));
    } finally {
      if (request === sourceRequest.current) setSourceLoading(false);
    }
  }
  async function upload(file: File | undefined) {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const uploaded = await api<{ id: string }>("/sources", {
        method: "POST",
        body,
      });
      await reload();
      await openSource(uploaded.id);
      setNotice(
        "자료가 저장되었습니다. 원문을 확인하고 반응 기록을 등록하세요.",
      );
    } catch (e) {
      setError(errorText(e));
    } finally {
      setUploading(false);
      if (uploadRef.current) uploadRef.current.value = "";
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
    { id: "graph" as View, label: "반응 지도", icon: Network },
    { id: "sources" as View, label: "자료 보관함", icon: BookOpen },
    { id: "routes" as View, label: "경로 탐색", icon: GitBranch },
    { id: "molecules" as View, label: "분자 사전", icon: Hexagon },
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
            나의 연구실<small>Local workspace</small>
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
            로컬에 저장됨<small>SQLite · 외부 AI 전송 없음</small>
          </div>
          <a className="export-link" href="/api/export">
            <ArrowDownToLine size={16} />
            Markdown 내보내기
          </a>
          <div className="profile">
            <span>연</span>
            <div>
              연구자<small>Personal workspace</small>
            </div>
            <Microscope size={17} />
          </div>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            나의 연구실<span>/</span>
            <strong>{nav.find((n) => n.id === view)?.label}</strong>
          </div>
          <div className="topbar-right">
            <span className="version">LOCAL · v0.1</span>
            <button
              className="button small"
              onClick={() => uploadRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? (
                <LoaderCircle size={15} className="spin" />
              ) : (
                <Upload size={15} />
              )}
              자료 업로드
            </button>
          </div>
        </header>
        <div className="page-heading">
          <div>
            <div className="eyebrow">CONNECT THE CHEMISTRY</div>
            <h1>
              {view === "graph"
                ? "아이디어가 반응으로 이어지는 곳"
                : view === "sources"
                  ? "모든 연결에는 근거가 있습니다"
                  : view === "routes"
                    ? "목표에서 출발점까지"
                    : "우리 연구실의 분자 사전"}
            </h1>
            <p>
              {view === "graph"
                ? "분자와 반응, 그리고 그 사이의 가능성을 탐색하세요."
                : view === "sources"
                  ? "논문과 실험 노트를 모으고, 원문에서 반응의 근거를 찾아보세요."
                  : view === "routes"
                    ? "기록된 반응을 연결해 가능한 합성 경로를 비교하세요."
                    : "구조를 기준으로 분자를 연결하고, 이름과 별칭으로 찾아보세요."}
            </p>
          </div>
          <button
            className="button primary"
            onClick={() =>
              setModal({ kind: view === "molecules" ? "molecule" : "reaction" })
            }
          >
            <Plus size={17} />
            {view === "molecules" ? "분자 등록" : "반응 기록"}
          </button>
        </div>
        <input
          ref={uploadRef}
          type="file"
          accept=".pdf,.md,.txt"
          hidden
          onChange={(e) => upload(e.target.files?.[0])}
        />
        {error && (
          <div className="alert error" role="alert">
            {error}
            <button aria-label="오류 닫기" onClick={() => setError("")}>
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
            워크스페이스를 불러오는 중
          </div>
        ) : (
          <>
            <div className="stats-row">
              <Stat
                label="분자"
                value={
                  workspace.molecules.filter((m) => showDemo || !m.is_demo)
                    .length
                }
                icon={<Hexagon size={18} />}
                note="구조로 연결된 지식"
              />
              <Stat
                label="반응 기록"
                value={
                  workspace.reactions.filter((r) => showDemo || !r.is_demo)
                    .length
                }
                icon={<FlaskConical size={18} />}
                note="조건과 근거를 함께"
              />
              <Stat
                label="업로드한 자료"
                value={userSources.length}
                icon={<FileText size={18} />}
                note="논문 · 실험 노트"
              />
              <div className="insight">
                <Sparkles size={20} />
                <div>
                  작은 발견을 연결해
                  <br />
                  <strong>다음 반응의 실마리로.</strong>
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
                      전체 반응
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
                      aria-label="논문 필터"
                      value={paperFilter}
                      onChange={(e) => setPaperFilter(e.target.value)}
                    >
                      <option value="all">모든 논문</option>
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
                    placeholder="분자, 반응, SMILES 검색"
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
                        데모 포함
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
                            ? "검색 결과가 없습니다"
                            : "첫 번째 연결을 만들어보세요"
                        }
                        text="자료를 업로드하고 분자와 반응을 등록하면 지도가 만들어집니다."
                        action={
                          <button
                            className="button"
                            onClick={() => setModal({ kind: "molecule" })}
                          >
                            <Plus size={15} />
                            분자 등록
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
                      <span>드래그로 이동 · 스크롤로 확대</span>
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
                        workspace={workspace}
                        onSelect={setSelected}
                      />
                    ) : (
                      <Empty
                        icon={<Layers3 size={28} />}
                        title="연결 속 이야기를 살펴보세요"
                        text="지도에서 분자나 반응을 선택하면 구조, 조건과 원문 근거가 표시됩니다."
                      />
                    )}
                  </aside>
                </div>
                <div className="footnote">
                  <BookOpen size={14} />
                  데모는 제품 사용 예시입니다. 실제 합성 조건과 수율은 논문·실험
                  기록을 검토해 등록하세요.
                </div>
              </>
            )}
            {view === "sources" && (
              <Sources
                workspace={workspace}
                source={source}
                loading={sourceLoading}
                initialPage={sourcePage}
                onOpen={openSource}
                onBack={() => setSource(null)}
                onUpload={() => uploadRef.current?.click()}
                uploading={uploading}
                onDrop={upload}
                onUse={(evidence) => setModal({ kind: "reaction", evidence })}
                onUpdated={async (detail) => {
                  setSource(detail);
                  await reload();
                  setNotice("서지 정보가 저장되었습니다.");
                }}
              />
            )}
            {view === "molecules" && (
              <>
                <div className="section-toolbar">
                  <h2>
                    등록된 분자 <span>{workspace.molecules.length}</span>
                  </h2>
                  <SearchBox
                    value={search}
                    onChange={setSearch}
                    placeholder="이름 · 별칭 · SMILES 검색"
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
                          src={`/api/molecules/${m.id}/svg`}
                          alt={`${m.name} 구조식`}
                        />
                        <h3>{m.name}</h3>
                        <p>{m.aliases.join(" · ") || "별칭 없음"}</p>
                        <footer>
                          <span>{m.molecular_weight} g/mol</span>
                          <ArrowRight size={16} />
                        </footer>
                      </button>
                    ))}
                </div>
                {!workspace.molecules.length && (
                  <Empty
                    title="분자를 등록해보세요"
                    text="SMILES를 입력하면 구조와 식별자가 생성됩니다."
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
              ? "분자 등록"
              : modal.reaction
                ? "반응 기록 수정"
                : "새로운 반응 기록"
          }
          onClose={() => setModal(null)}
        >
          {modal.kind === "molecule" ? (
            <MoleculeForm
              onSaved={async () => {
                await reload();
                setModal(null);
                setNotice("분자가 사전에 등록되었습니다.");
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
                setNotice("반응 기록이 저장되었습니다.");
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
        <button onClick={() => onChange("")} aria-label="검색 초기화">
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
  return <span className="badge demo">DEMO · 실험 미검증</span>;
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
              {r.status === "reviewed" ? "기록 검토 완료" : "검토 전 초안"}
            </span>
          )}
          <span className="muted">{r.evidence.length}개 근거</span>
        </div>
      </div>
      <div className="inspector-section">
        <h4>반응 연결</h4>
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
        <h4>실험 조건</h4>
        {r.reagents && <p className="detail-note">시약·촉매: {r.reagents}</p>}
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
            <dt>수율</dt>
            <dd>
              {r.yield_percent == null ? "미기재" : `${r.yield_percent}%`}
            </dd>
          </div>
        </dl>
        {!Object.values(r.conditions).some(Boolean) && (
          <p className="subtle-text">원문을 검토해 조건을 등록하세요.</p>
        )}
      </div>
      <div className="inspector-section">
        <h4>
          원문 근거 <span>{r.evidence.length}</span>
        </h4>
        {r.evidence.map((e, i) => (
          <button
            className="evidence-card"
            key={i}
            onClick={() => onSource(e.source_id, e.page)}
          >
            <div>
              <FileText size={14} />
              {workspace.sources.find((s) => s.id === e.source_id)?.title}
              <ExternalLink size={12} />
            </div>
            <blockquote>{e.quote}</blockquote>
            <small>
              PDF p.{e.page} {e.locator && `· ${e.locator}`} · 원문 열기{" "}
              <ArrowRight size={12} />
            </small>
          </button>
        ))}
        {!r.evidence.length && (
          <p className="subtle-text">아직 연결된 근거가 없습니다.</p>
        )}
      </div>
      {r.notes && (
        <div className="inspector-section">
          <h4>연구 노트</h4>
          <p className="detail-note">{r.notes}</p>
        </div>
      )}
      <div className="inspector-action">
        <button className="button full" onClick={onEdit}>
          반응 기록 수정
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
}: {
  molecule: Molecule;
  workspace: Workspace;
  onSelect: (id: string) => void;
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
        <img src={`/api/molecules/${m.id}/svg`} alt={`${m.name} 구조식`} />
        <h2>{m.name}</h2>
        <p>{m.aliases.join(" · ")}</p>
        {m.is_demo && <DemoBadge />}
      </div>
      <div className="inspector-section">
        <dl className="conditions">
          <div>
            <dt>분자식</dt>
            <dd>{m.formula}</dd>
          </div>
          <div>
            <dt>분자량</dt>
            <dd>{m.molecular_weight} g/mol</dd>
          </div>
          <div>
            <dt>확보 상태</dt>
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
          연결된 반응 <span>{related.length}</span>
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
          <h4>노트</h4>
          <p className="detail-note">{m.notes}</p>
        </div>
      )}
    </>
  );
}

function Sources({
  workspace,
  source,
  loading,
  onOpen,
  onBack,
  onUpload,
  uploading,
  onDrop,
  onUse,
  initialPage,
  onUpdated,
}: {
  workspace: Workspace;
  source: SourceDetail | null;
  loading: boolean;
  onOpen: (id: string) => void;
  onBack: () => void;
  onUpload: () => void;
  uploading: boolean;
  onDrop: (file: File | undefined) => void;
  onUse: (evidence: Evidence) => void;
  initialPage: number;
  onUpdated: (source: SourceDetail) => Promise<void>;
}) {
  const [page, setPage] = useState(1);
  const [tab, setTab] = useState<"pages" | "candidates">("pages");
  const [query, setQuery] = useState("");
  const [editingMetadata, setEditingMetadata] = useState(false);
  useEffect(() => {
    setPage(initialPage);
    setTab("pages");
    setQuery("");
    setEditingMetadata(false);
  }, [source?.id, initialPage]);
  const matches = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!source || !term) return [];
    return source.pages.flatMap((p) => {
      const index = p.text.toLowerCase().indexOf(term);
      return index < 0
        ? []
        : [
            {
              page: p.number,
              snippet: p.text.slice(
                Math.max(0, index - 90),
                index + term.length + 160,
              ),
            },
          ];
    });
  }, [source, query]);
  if (loading)
    return (
      <div className="loading">
        <LoaderCircle className="spin" />
        자료를 불러오는 중
      </div>
    );
  if (source)
    return (
      <div className="source-reader">
        <div className="section-toolbar">
          <button className="text-button" onClick={onBack}>
            <ArrowLeft size={16} />
            자료 목록
          </button>
          <a
            className="button small"
            href={`/api/sources/${source.id}/file#page=${page}`}
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink size={14} />
            원본 열기
          </a>
        </div>
        <div className="source-heading">
          <span className="document-icon">
            <FileText size={24} />
          </span>
          <div>
            <h2>{source.title}</h2>
            <p>
              {source.page_count} pages ·{" "}
              {source.text_characters.toLocaleString()}자 추출{" "}
              {source.is_demo && "· 데모 자료"}
            </p>
            {source.citation && <p>{source.citation}</p>}
            {source.doi && (
              <a
                className="source-doi"
                href={`https://doi.org/${source.doi}`}
                target="_blank"
                rel="noreferrer"
              >
                DOI: {source.doi}
                <ExternalLink size={11} />
              </a>
            )}
          </div>
        </div>
        <div className="source-reader-tools">
          <span className="badge">
            {documentRoles[source.document_role || "other"]}
          </span>
          <button
            className="text-button"
            onClick={() => setEditingMetadata(!editingMetadata)}
          >
            {editingMetadata ? "서지 정보 접기" : "서지 정보 편집"}
          </button>
          <SearchBox
            value={query}
            onChange={setQuery}
            placeholder="자료 안에서 찾기"
          />
        </div>
        {editingMetadata && (
          <SourceMetadataForm
            key={source.id}
            source={source}
            sources={workspace.sources}
            onSaved={async (detail) => {
              await onUpdated(detail);
              setEditingMetadata(false);
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
            <span>같은 논문 자료</span>
            {source.related_source_ids.map((id) => (
              <button key={id} onClick={() => onOpen(id)}>
                <FileText size={13} />
                {workspace.sources.find((s) => s.id === id)?.title}
                <ArrowRight size={12} />
              </button>
            ))}
          </div>
        )}
        {query.trim() && (
          <div className="source-search-results">
            <h4>검색된 페이지 {matches.length}개</h4>
            {matches.slice(0, 50).map((match) => (
              <button
                key={match.page}
                onClick={() => {
                  setPage(match.page);
                  setTab("pages");
                  setQuery("");
                }}
              >
                <strong>PDF p.{match.page}</strong>
                <span>{match.snippet}</span>
                <ArrowRight size={14} />
              </button>
            ))}
            {!matches.length && (
              <p className="subtle-text">
                추출 텍스트에서 일치하는 내용이 없습니다. 그림 안의 문자는 원본
                PDF에서 확인하세요.
              </p>
            )}
          </div>
        )}
        {source.text_characters < 40 && (
          <div className="alert">
            추출 가능한 텍스트가 거의 없습니다. 스캔 PDF는 OCR 처리한 파일을
            올리거나 Markdown 실험 노트로 보완하세요.
          </div>
        )}
        <div className="reader-tabs">
          <button
            className={tab === "pages" ? "selected" : ""}
            onClick={() => setTab("pages")}
          >
            페이지 원문
          </button>
          <button
            className={tab === "candidates" ? "selected" : ""}
            onClick={() => setTab("candidates")}
          >
            반응 관련 후보 문장 <span>{source.candidates.length}</span>
          </button>
        </div>
        <p className="reader-hint">
          텍스트 추출과 키워드 탐색 결과입니다. 구조·조건은 원문을 검토해 반응
          기록에 입력하세요.
        </p>
        {tab === "pages" ? (
          <>
            <div className="page-controls">
              <label>
                페이지{" "}
                <select
                  aria-label="원문 페이지"
                  value={page}
                  onChange={(e) => setPage(Number(e.target.value))}
                >
                  {source.pages.map((p) => (
                    <option key={p.number} value={p.number}>
                      {p.number}
                    </option>
                  ))}
                </select>{" "}
                / {source.page_count}
              </label>
              <button
                className="button small"
                disabled={!source.pages[page - 1]?.text.trim()}
                onClick={() =>
                  onUse({
                    source_id: source.id,
                    page,
                    quote: source.pages[page - 1].text.slice(0, 10000),
                  })
                }
              >
                <Plus size={14} />이 페이지로 반응 기록
              </button>
            </div>
            <pre className="source-text">
              {source.pages[page - 1]?.text ||
                "이 페이지에서 텍스트를 추출하지 못했습니다."}
            </pre>
          </>
        ) : (
          <div className="candidate-list">
            {source.candidates.map((c, i) => (
              <article className="candidate-card" key={i}>
                <div className="eyebrow">PAGE {c.page} · 검토 필요</div>
                <p>{c.text}</p>
                <button
                  className="button small"
                  onClick={() =>
                    onUse({ source_id: source.id, page: c.page, quote: c.text })
                  }
                >
                  반응 기록에 사용
                  <ArrowRight size={14} />
                </button>
              </article>
            ))}
            {!source.candidates.length && (
              <Empty
                title="자동 탐색된 후보 문장이 없습니다"
                text="페이지 원문에서 문장을 확인해 수동으로 기록할 수 있습니다."
              />
            )}
          </div>
        )}
      </div>
    );
  return (
    <>
      <div
        className="upload-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!uploading) onDrop(e.dataTransfer.files[0]);
        }}
      >
        <div className="upload-icon">
          {uploading ? (
            <LoaderCircle className="spin" size={25} />
          ) : (
            <Upload size={25} />
          )}
        </div>
        <h2>
          {uploading
            ? "자료에서 텍스트를 추출하고 있습니다"
            : "다음 발견의 시작, 자료 한 편"}
        </h2>
        <p>논문 PDF, Supporting Information, 실험 노트를 끌어다 놓으세요.</p>
        <button
          className="button primary"
          disabled={uploading}
          onClick={onUpload}
        >
          <Plus size={16} />
          파일 선택
        </button>
        <small>PDF · MD · TXT / 파일당 최대 20 MB / 로컬 저장</small>
      </div>
      <div className="section-toolbar">
        <h2>
          자료 목록 <span>{workspace.sources.length}</span>
        </h2>
        <span className="subtle-text">
          각 파일의 원문과 페이지를 보존합니다
        </span>
      </div>
      <div className="source-list">
        {workspace.sources.map((s) => (
          <button
            className="source-row"
            key={s.id}
            onClick={() => onOpen(s.id)}
          >
            <span className="document-icon">
              <FileText size={21} />
            </span>
            <div>
              <strong>{s.title}</strong>
              <small>
                {s.filename} · {s.page_count} pages ·{" "}
                {s.text_characters.toLocaleString()}자
              </small>
              {s.doi && (
                <small className="source-citation">
                  {documentRoles[s.document_role || "other"]} ·{" "}
                  {s.citation || s.doi}
                </small>
              )}
            </div>
            {s.is_demo ? (
              <DemoBadge />
            ) : (
              <span
                className={`badge ${s.text_characters > 40 ? "reviewed" : ""}`}
              >
                {s.text_characters > 40 ? "텍스트 추출 완료" : "OCR 필요"}
              </span>
            )}
            <ArrowRight size={17} />
          </button>
        ))}
      </div>
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
          목표 생성물
          <select
            aria-label="목표 생성물"
            value={target}
            onChange={(e) => {
              setTarget(e.target.value);
              setRoutes(null);
            }}
            required
          >
            <option value="" disabled>
              분자를 선택하세요
            </option>
            {workspace.molecules.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
                {m.is_demo ? " · 데모" : ""}
              </option>
            ))}
          </select>
        </label>
        <label>
          최대 반응 단계
          <select
            aria-label="최대 반응 단계"
            value={steps}
            onChange={(e) => {
              setSteps(Number(e.target.value));
              setRoutes(null);
            }}
          >
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <option key={n} value={n}>
                {n} 단계
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
          검토 전 초안 포함
        </label>
        <button className="button primary" disabled={busy || !target}>
          {busy ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <Search size={16} />
          )}
          경로 탐색
        </button>
      </form>
      {error && <div className="alert error">{error}</div>}
      {routes === null ? (
        <Empty
          icon={<GitBranch size={36} />}
          title="목표 분자에서 거슬러 올라가세요"
          text="기록된 반응을 연결하고, 필요한 모든 출발물질 가지를 함께 보여줍니다."
        />
      ) : (
        <>
          <div className="section-toolbar">
            <h2>
              후보 경로 <span>{routes.length}</span>
            </h2>
            <span className="subtle-text">
              확보 상태 미확인 수 → 단계 수 순
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
                  <span className="badge">{route.steps} 단계</span>
                </div>
                <div>
                  {route.is_demo && <DemoBadge />}
                  {route.contains_drafts && (
                    <span className="badge">초안 포함</span>
                  )}
                </div>
              </header>
              {tree(route)}
              <footer>
                <div>
                  <strong>필요 출발물질</strong>
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
                    ? `구매·재고 미확인 ${route.unknown_availability.length}종`
                    : "사용자 입력상 확보 가능"}
                </span>
              </footer>
            </article>
          ))}
          {!routes.length && (
            <Empty
              title="연결된 경로가 없습니다"
              text="이 생성물을 만드는 반응을 등록하거나, 초안 포함 여부와 최대 단계를 확인하세요."
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
            aria-label="창 닫기"
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
function MoleculeForm({ onSaved }: { onSaved: () => Promise<void> }) {
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
        "/molecules",
        json({
          name: data.get("name"),
          smiles: data.get("smiles"),
          aliases: String(data.get("aliases") || "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          availability: data.get("availability"),
          notes: data.get("notes"),
        }),
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
        SMILES를 입력하면 RDKit이 구조를 검증하고 분자식·식별자를 만듭니다.
      </p>
      <label>
        분자 이름
        <input
          name="name"
          placeholder="예: Benzaldehyde"
          required
          maxLength={200}
        />
      </label>
      <label>
        SMILES
        <input
          name="smiles"
          className="mono"
          placeholder="예: O=Cc1ccccc1"
          required
          maxLength={2000}
        />
        <small>입체화학을 포함한 구조를 기준으로 중복을 확인합니다.</small>
      </label>
      <div className="form-grid">
        <label>
          별칭
          <input name="aliases" placeholder="쉼표로 구분: 벤즈알데하이드" />
        </label>
        <label>
          확보 상태
          <select name="availability" defaultValue="unknown">
            {Object.entries(availability).map(([id, label]) => (
              <option value={id} key={id}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        연구 노트
        <textarea
          name="notes"
          rows={3}
          placeholder="재고 위치, 공급사, 구조 관련 메모 등"
        />
      </label>
      {error && (
        <div className="alert error" role="alert">
          {error}
        </div>
      )}
      <footer>
        <span className="subtle-text">새 분자는 데모와 별도로 저장됩니다.</span>
        <button className="button primary" disabled={busy}>
          {busy ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <Check size={16} />
          )}
          분자 저장
        </button>
      </footer>
    </form>
  );
}
const conditionFields: Record<Category, string[]> = {
  organic: ["용매", "농도", "온도", "시간", "분위기", "반응 규모", "정제"],
  electrochemical: [
    "용매",
    "농도",
    "온도",
    "시간",
    "분위기",
    "반응 규모",
    "정제",
    "양극",
    "음극",
    "전해질",
    "전위·기준전극",
    "전류밀도",
    "전하량",
    "셀 구성",
  ],
  photochemical: [
    "용매",
    "농도",
    "온도",
    "시간",
    "분위기",
    "반응 규모",
    "정제",
    "파장",
    "광원",
    "출력·광자속",
    "조사 시간",
    "반응기",
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
  const [quote, setQuote] = useState("");
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
    setQuote("");
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
          aria-label={`${label} 추가`}
          value=""
          onChange={(e) => {
            if (e.target.value) change([...selected, e.target.value]);
          }}
        >
          <option value="">분자 선택 · 여러 개 추가 가능</option>
          {workspace.molecules
            .filter((m) => !selected.includes(m.id))
            .map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
                {m.is_demo ? " · 데모" : ""}
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
      setError("반응물과 생성물을 각각 한 개 이상 선택하세요.");
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
          원문에 보고된 값과 단위를 입력하세요. 미기재 값은 빈칸으로 남길 수
          있습니다.
        </p>
        <div className="form-grid">
          <label>
            반응 이름 *
            <input
              name="name"
              required
              defaultValue={initial?.name}
              placeholder="예: 알코올의 광촉매 산화"
              maxLength={200}
            />
          </label>
          <label>
            방법론
            <select
              aria-label="방법론"
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
          <h3>분자 연결</h3>
          <button
            className="text-button"
            type="button"
            onClick={() => setAddingMolecule(true)}
          >
            <Plus size={13} />새 분자 등록
          </button>
        </div>
        <div className="form-grid">
          {participant("반응물", reactants, setReactants)}
          {participant("생성물", products, setProducts)}
        </div>
        <label>
          시약·촉매
          <input
            name="reagents"
            defaultValue={initial?.reagents}
            placeholder="물질명, 당량, 촉매 사용량 등"
          />
        </label>
        <h3 className="form-section-title">실험 조건</h3>
        <div className="form-grid conditions-inputs">
          {fields.map((field) => (
            <label key={field}>
              {field}
              <input
                value={conditions[field] || ""}
                onChange={(e) =>
                  setConditions({ ...conditions, [field]: e.target.value })
                }
                placeholder="미기재 · 단위 포함"
              />
            </label>
          ))}
        </div>
        <div className="form-grid">
          <label>
            수율 (%)
            <input
              type="number"
              min="0"
              max="100"
              step="any"
              name="yield"
              defaultValue={initial?.yield_percent ?? ""}
              placeholder="미기재"
            />
          </label>
          <label>
            검토 상태
            <select
              aria-label="검토 상태"
              name="status"
              defaultValue={initial?.status || "draft"}
            >
              <option value="draft">초안 · 경로 탐색 기본 제외</option>
              <option value="reviewed">기록 검토 완료 · 원문 근거 필수</option>
            </select>
          </label>
        </div>
        <h3 className="form-section-title">원문 근거</h3>
        {evidences.map((e, i) => (
          <div className="form-evidence" key={i}>
            <div>
              <FileText size={14} />
              {workspace.sources.find((s) => s.id === e.source_id)?.title} · p.
              {e.page}
              <button
                type="button"
                className="icon-button"
                aria-label={`근거 ${i + 1} 삭제`}
                onClick={() =>
                  setEvidences(evidences.filter((_, j) => j !== i))
                }
              >
                <X size={15} />
              </button>
            </div>
            <textarea
              aria-label={`근거 문장 ${i + 1}`}
              value={e.quote}
              onChange={(event) =>
                setEvidences(
                  evidences.map((item, j) =>
                    j === i ? { ...item, quote: event.target.value } : item,
                  ),
                )
              }
              rows={3}
            />
            <small>이 페이지의 실제 문장 중 필요한 부분만 남기세요.</small>
          </div>
        ))}
        <div className="evidence-builder">
          <div className="form-grid">
            <label>
              자료 선택
              <select
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
              >
                <option value="">원문 자료 선택</option>
                {workspace.sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                    {s.is_demo ? " · 데모" : ""}
                  </option>
                ))}
              </select>
            </label>
            <label>
              페이지
              <select
                value={page}
                disabled={!sourceDetail}
                onChange={(e) => {
                  setPage(Number(e.target.value));
                  setQuote("");
                }}
              >
                {sourceDetail?.pages.map((p) => (
                  <option key={p.number} value={p.number}>
                    {p.number}
                  </option>
                )) || <option>1</option>}
              </select>
            </label>
          </div>
          {sourceDetail && (
            <>
              <details>
                <summary>선택한 페이지의 원문 보기</summary>
                <pre>
                  {sourceDetail.pages[page - 1]?.text || "추출된 텍스트 없음"}
                </pre>
              </details>
              <label>
                원문 인용
                <textarea
                  value={quote}
                  onChange={(e) => setQuote(e.target.value)}
                  placeholder="위 원문에서 근거 문장을 복사하세요."
                  rows={3}
                />
              </label>
            </>
          )}
          <button
            className="button small"
            type="button"
            disabled={!sourceDetail || !quote.trim()}
            onClick={() => {
              setEvidences([
                ...evidences,
                { source_id: sourceId, page, quote },
              ]);
              setQuote("");
            }}
          >
            <Plus size={14} />
            근거 추가
          </button>
        </div>
        <label>
          연구 노트
          <textarea
            name="notes"
            defaultValue={initial?.notes}
            rows={3}
            placeholder="선택성, 정제 과정, 재현 결과 등을 기록하세요."
          />
        </label>
        {error && (
          <div className="alert error" role="alert">
            {error}
          </div>
        )}
        <footer>
          <span className="subtle-text">
            근거 문장이 원문에 존재하는지 확인합니다.
          </span>
          <button className="button primary" disabled={busy}>
            {busy ? (
              <LoaderCircle className="spin" size={16} />
            ) : (
              <Check size={16} />
            )}
            반응 저장
          </button>
        </footer>
      </form>
      {addingMolecule &&
        createPortal(
          <ModalShell
            title="분자 등록"
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
