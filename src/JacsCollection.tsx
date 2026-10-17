import { useEffect, useRef, useState } from "react";
import { ArrowDownToLine, LoaderCircle } from "lucide-react";
import { api, json } from "./api";

type Schedule = { supported: boolean; enabled: boolean; weekday: string; time: string };
type CollectionStatus = {
  journal: string;
  policy: "open_access_only";
  running: boolean;
  last_run: null | {
    started_at: string; finished_at: string | null; status: string;
    discovered: number; added: number; existing: number; pdfs_saved: number; errors: string[];
    notices?: { code: "duplicate_doi_matches"; doi: string; source_ids: string[]; selected_source_id: string }[];
  };
  totals: { articles: number; pdfs: number };
  schedule: Schedule;
};
const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const message = (error: unknown) => error instanceof Error ? error.message : "Unable to update collection.";

export function JacsCollection({ onCollected }: { onCollected: () => Promise<unknown> }) {
  const [status, setStatus] = useState<CollectionStatus | null>(null);
  const [pollError, setPollError] = useState("");
  const [actionError, setActionError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [weekday, setWeekday] = useState("Monday");
  const [time, setTime] = useState("09:00");
  const [enabled, setEnabled] = useState(false);
  const onCollectedRef = useRef(onCollected);
  const observedRun = useRef<string | null | undefined>(undefined);
  onCollectedRef.current = onCollected;
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    let initialized = false;
    async function poll() {
      try {
        const next = await api<CollectionStatus>("/collection/jacs");
        if (!active) return;
        setStatus(next);
        if (!initialized) {
          setWeekday(next.schedule.weekday);
          setTime(next.schedule.time);
          setEnabled(next.schedule.enabled);
        }
        initialized = true;
        const completed = !next.running ? next.last_run?.finished_at || null : null;
        // The app may have loaded its workspace before a scheduled run finished.
        // Refresh once even when this is the first completed run seen on mount.
        if (completed && completed !== observedRun.current) await onCollectedRef.current();
        if (!next.running) observedRun.current = completed;
        if (active) setPollError("");
      } catch (e) {
        if (active) setPollError(message(e));
      }
      if (active) timer = setTimeout(poll, 2500);
    }
    void poll();
    return () => { active = false; clearTimeout(timer); };
  }, []);

  async function collect() {
    setBusy(true);
    setActionError("");
    try {
      await api("/collection/jacs/run", json({}));
      const next = await api<CollectionStatus>("/collection/jacs");
      setStatus(next);
      if (!next.running) {
        await onCollectedRef.current();
        observedRun.current = next.last_run?.finished_at || null;
      }
    } catch (e) { setActionError(message(e)); }
    finally { setBusy(false); }
  }
  async function saveSchedule(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setActionError("");
    try {
      const schedule = await api<Schedule>("/collection/jacs/schedule", json({ enabled, weekday, time }));
      setStatus((current) => current ? { ...current, schedule } : current);
    } catch (e) { setActionError(message(e)); }
    finally { setSaving(false); }
  }

  return <section className="jacs-collection" aria-labelledby="jacs-collection-heading">
    <div className="section-toolbar">
      <h2 id="jacs-collection-heading">JACS weekly collection</h2>
      <button className="button primary small" disabled={!status || busy || status.running} onClick={collect}>
        {busy || status?.running ? <LoaderCircle size={15} className="spin" /> : <ArrowDownToLine size={15} />}
        {status?.running ? "Collecting…" : "Collect now"}
      </button>
    </div>
    <p>Collect JACS bibliography and openly available PDFs. Subscription PDFs are not downloaded automatically.</p>
    <p className="subtle-text">Metadata and open-access collection do not require campus Wi-Fi or VPN. Use each paper’s DOI link with your campus network or VPN for institutional access.</p>
    {pollError && <div className="alert error" role="alert">{pollError}</div>}
    {actionError && <div className="alert error" role="alert">{actionError}</div>}
    {!status && !pollError && <p className="subtle-text">Loading collection status…</p>}
    {status && <>
      <p className="collection-totals">{status.totals.articles} collected papers · {status.totals.pdfs} open-access PDFs saved locally</p>
      {status.last_run && <div className="collection-result" role="status">
        <strong>Last collection: {status.last_run.status}</strong>
        <span>{status.last_run.discovered} found · {status.last_run.added} added · {status.last_run.existing} already in library · {status.last_run.pdfs_saved} PDFs saved</span>
        <span>{new Date(status.last_run.started_at).toLocaleString()}</span>
        {!!status.last_run.notices?.length && <details className="collection-notices">
          <summary>Duplicate DOI matches ({status.last_run.notices.length})</summary>
          <p>These matches do not stop collection. Existing records remain separate.</p>
          <ul>{status.last_run.notices.map((notice, index) => <li key={`${notice.doi}-${index}`}>
            <strong>DOI: {notice.doi}</strong>
            <p>{notice.source_ids.length} existing records retained. Selected source: <code>{notice.selected_source_id}</code></p>
            <p>Retained source IDs: {notice.source_ids.map((id, position) => <span key={position}>{position > 0 && ", "}<code>{id}</code></span>)}</p>
          </li>)}</ul>
        </details>}
        {!!status.last_run.errors.length && <details className="collection-errors"><summary>Collection errors ({status.last_run.errors.length})</summary><ul>{status.last_run.errors.map((item, index) => <li key={index}>{item}</li>)}</ul></details>}
      </div>}
      <form className="collection-schedule" onSubmit={saveSchedule}>
        <label className="check-label"><input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} disabled={!status.schedule.supported || saving} />Weekly collection</label>
        <label>Collection day<select aria-label="Collection day" value={weekday} onChange={(event) => setWeekday(event.target.value)} disabled={!status.schedule.supported || saving}>{weekdays.map((day) => <option key={day}>{day}</option>)}</select></label>
        <label>Local time<input aria-label="Collection local time" type="time" required value={time} onChange={(event) => setTime(event.target.value)} disabled={!status.schedule.supported || saving} /></label>
        <button className="button small" disabled={!status.schedule.supported || saving}>{saving ? "Saving…" : "Save weekly schedule"}</button>
      </form>
      <p className="subtle-text">{status.schedule.supported ? "Windows Task Scheduler uses this PC’s local time. Keep the PC on, connected to the internet and logged in; the app does not need to stay open." : "Weekly scheduling is available in the packaged Windows app. Manual collection is available here."}</p>
    </>}
  </section>;
}
