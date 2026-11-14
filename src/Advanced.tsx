import { useEffect, useState } from "react";
import {
  api,
  date,
  method,
  type Candidate,
  type Job,
  type Page,
  type Run,
  type User,
} from "./api";
import {
  Button,
  Empty,
  Field,
  Loading,
  Notice,
  Pager,
  Panel,
  SearchField,
} from "./components";
type Go = (view: string, extra?: Record<string, string>) => void;
type Application = {
  id: string;
  job_id: string;
  candidate_id: string;
  profile_label: string;
  profile_version: number;
  status: string;
  revision: number;
  updated: string;
  job_title?: string;
  decisions: { status: string; feedback: string; created: string }[];
};
const applicationStatus = (status: string) =>
  ({
    active: "Submitted · awaiting review",
    under_review: "Under review",
    accepted: "Accepted for next stage",
    rejected: "Not selected",
    withdrawn: "Previously withdrawn",
  })[status] || status;

type ApplicationReview = {
  application: Application;
  submitted_text: string;
  match: null | {
    run_id: string;
    created: string;
    method: string;
    score: number;
    profile_version: number;
    requirements: {
      skill: string;
      kind: string;
      matched: boolean;
      evidence: string | null;
      evidence_status: string;
    }[];
    components: { name: string; contribution: number }[];
  };
  feedback_previews: Record<string, string>;
};
type Opportunity = Job & {
  published: boolean;
  application_count?: number;
  my_application?: Application | null;
};
type Finding = {
  skill: string;
  kind: string;
  status: string;
  passage: string | null;
  notes: string[];
};
function useData<T>(path: string, revision = 0) {
  const [data, setData] = useState<T>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const abort = new AbortController();
    setLoading(true);
    setError("");
    api<T>(path, { signal: abort.signal })
      .then((v) => {
        if (!abort.signal.aborted) setData(v);
      })
      .catch((e) => {
        if (!abort.signal.aborted) setError(e.message);
      })
      .finally(() => {
        if (!abort.signal.aborted) setLoading(false);
      });
    return () => abort.abort();
  }, [path, revision, retry]);
  return { data, error, loading, retry: () => setRetry((x) => x + 1) };
}
function Heading({ title, text }: { title: string; text: string }) {
  return (
    <header className="page-heading">
      <div>
        <div className="eyebrow">Candidate Lab / Advanced workspace</div>
        <h1>{title}</h1>
        <p>{text}</p>
      </div>
    </header>
  );
}
export function Opportunities({
  user,
  go,
  page,
  q,
}: {
  user: User;
  go: Go;
  page: number;
  q: string;
}) {
  const [rev, setRev] = useState(0);
  const jobs = useData<Page<Opportunity>>(
    `/opportunities?page=${page}&q=${encodeURIComponent(q)}`,
    rev,
  );
  const profiles = useData<Page<Candidate>>("/candidates?page=1", rev);
  const [profile, setProfile] = useState("");
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [failed, setFailed] = useState(false);
  const [gap, setGap] = useState<{
    job_title: string;
    profile_label: string;
    profile_version: number;
    requirements: Finding[];
    note: string;
  } | null>(null);
  const [methodChoice, setMethod] = useState("tfidf");
  useEffect(() => {
    if (gap)
      document
        .getElementById("skill-gap-report")
        ?.scrollIntoView({ block: "start" });
  }, [gap]);
  const selectedProfile = profile || profiles.data?.items[0]?.id || "";
  async function act(
    job: Opportunity,
    action: "publish" | "apply" | "gap" | "match",
  ) {
    setBusy(job.id + action);
    setMessage("");
    setFailed(false);
    try {
      if (action === "publish") {
        await api(`/jobs/${job.id}/publication`, {
          method: "PUT",
          body: JSON.stringify({ published: !job.published }),
        });
        setMessage(
          job.published
            ? "Job closed to new applications. Existing applications remain available."
            : "Job published. Candidates can now apply.",
        );
      }
      if (action === "apply") {
        await api(`/jobs/${job.id}/applications`, {
          method: "POST",
          body: JSON.stringify({ candidate_id: selectedProfile }),
        });
        setMessage(
          "Application submitted with a snapshot of this profile version.",
        );
      }
      if (action === "gap") {
        setGap(
          await api(
            `/jobs/${job.id}/skill-gap?candidate_id=${selectedProfile}`,
          ),
        );
      }
      if (action === "match") {
        const run = await api<Run>(
          `/jobs/${job.id}/runs?method=${methodChoice}`,
          { method: "POST" },
        );
        go("matches", { run: run.id });
        return;
      }
      setRev((x) => x + 1);
    } catch (e) {
      setMessage((e as Error).message);
      setFailed(true);
    } finally {
      setBusy("");
    }
  }
  return (
    <>
      <Heading
        title={
          user.role === "candidate"
            ? "Find your next opportunity."
            : "Manage job applications."
        }
        text={
          user.role === "candidate"
            ? "Review published roles, check your supporting evidence and apply with a saved profile."
            : "Publish job requirements and compare only the active applicants for each role."
        }
      />
      {message && <Notice message={message} error={failed} />}
      <Panel
        title={
          user.role === "candidate"
            ? "Your application profile"
            : "Matching settings"
        }
      >
        {user.role === "candidate" ? (
          <>
            <Field
              id="application-profile"
              label="Profile to submit"
              help="Applications retain this version. Later edits do not silently update a submitted application."
            >
              <select
                id="application-profile"
                disabled={!!busy}
                value={selectedProfile}
                onChange={(e) => {
                  setProfile(e.target.value);
                  setGap(null);
                }}
              >
                <option value="" disabled>
                  Choose a saved profile
                </option>
                {profiles.data?.items.map((p) => (
                  <option value={p.id} key={p.id}>
                    {p.label} · v{p.version}
                  </option>
                ))}
              </select>
            </Field>
            {profiles.data?.total === 0 && (
              <Button onClick={() => go("profile-new")}>
                Add your first profile
              </Button>
            )}
            {(profiles.data?.total || 0) > 10 && (
              <p className="small muted">
                Showing your ten most recently updated profiles. Update an older
                profile to bring it into this selector.
              </p>
            )}
          </>
        ) : (
          <Field
            id="application-method"
            label="Matching method"
            help="Semantic matching requires a configured local model; errors are explicit if it is unavailable."
          >
            <select
              id="application-method"
              value={methodChoice}
              onChange={(e) => setMethod(e.target.value)}
            >
              <option value="tfidf">TF-IDF + contextual skill evidence</option>
              <option value="semantic">
                Local semantic + contextual skill evidence
              </option>
            </select>
          </Field>
        )}
      </Panel>
      <Panel title="Job opportunities">
        <div className="toolbar">
          <SearchField
            placeholder="Search opportunities"
            value={q}
            onChange={(q) => go("opportunities", { q })}
          />
        </div>
        {jobs.loading ? (
          <Loading />
        ) : jobs.error ? (
          <>
            <Notice error message={jobs.error} />
            <Button onClick={jobs.retry}>Try again</Button>
          </>
        ) : !jobs.data?.items.length ? (
          <Empty title="No published opportunities available">
            <p>
              {user.role === "candidate"
                ? "A recruiter needs to publish a role before you can apply."
                : "Create a job requirements, then publish it here."}
            </p>
          </Empty>
        ) : (
          jobs.data.items.map((j) => (
            <article className="opportunity" key={j.id}>
              <div className="row">
                <h3>{j.title}</h3>
                <span className="badge">
                  {j.published
                    ? "Open for applications"
                    : "Not published / closed"}
                </span>
              </div>
              <p>{j.description}</p>
              <div className="chips">
                {j.required.map((s) => (
                  <span className="chip" key={s}>
                    {s}
                  </span>
                ))}
              </div>
              {user.role === "candidate" ? (
                <>
                  <p className="small muted">
                    {j.my_application
                      ? `Your application: ${applicationStatus(j.my_application.status)} · ${j.my_application.profile_label} v${j.my_application.profile_version}`
                      : "You have not applied to this role."}
                  </p>
                  <div className="advanced-actions">
                    <Button
                      variant="secondary"
                      disabled={!selectedProfile || !!busy}
                      busy={busy === j.id + "gap"}
                      onClick={() => act(j, "gap")}
                    >
                      Check skill evidence
                    </Button>
                    {j.my_application ? (
                      <Button
                        variant="secondary"
                        onClick={() => go("applications")}
                      >
                        View application status
                      </Button>
                    ) : (
                      <Button
                        disabled={!selectedProfile || !!busy}
                        busy={busy === j.id + "apply"}
                        onClick={() => act(j, "apply")}
                      >
                        Apply with selected profile
                      </Button>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <p className="small muted">
                    {j.application_count} active applications
                  </p>
                  <div className="advanced-actions">
                    <Button
                      variant="secondary"
                      disabled={!!busy}
                      onClick={() => act(j, "publish")}
                      busy={busy === j.id + "publish"}
                    >
                      {j.published ? "Close applications" : "Publish job"}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => go("applications", { job: j.id })}
                    >
                      View applications
                    </Button>
                    <Button
                      disabled={!j.application_count || !!busy}
                      onClick={() => act(j, "match")}
                      busy={busy === j.id + "match"}
                    >
                      Match applicants
                    </Button>
                  </div>
                </>
              )}
            </article>
          ))
        )}
        {jobs.data && (
          <Pager
            page={page}
            total={jobs.data.total}
            onPage={(p) => go("opportunities", { q, page: String(p) })}
          />
        )}
      </Panel>
      {gap && (
        <div id="skill-gap-report">
          <Panel
            title={`Skill evidence: ${gap.job_title}`}
            action={
              <Button variant="ghost" onClick={() => setGap(null)}>
                Close report
              </Button>
            }
          >
            <p className="small muted">
              {gap.profile_label} · current version {gap.profile_version}
            </p>
            <Notice message={gap.note} />
            {gap.requirements.map((r) => (
              <div className="requirement" key={r.kind + r.skill}>
                <div>
                  <strong>{r.skill}</strong>
                  <span className="badge">{r.status.replaceAll("_", " ")}</span>
                  <span className="tiny muted">{r.kind}</span>
                </div>
                <p>
                  {r.passage ||
                    "No supporting passage found. Add accurate evidence if your profile omitted relevant work."}
                </p>
                {r.notes.map((n) => (
                  <p key={n}>{n}</p>
                ))}
              </div>
            ))}
            <Button
              variant="secondary"
              onClick={() => go("profile", { id: selectedProfile })}
            >
              Correct this profile
            </Button>
          </Panel>
        </div>
      )}
    </>
  );
}

export function Applications({
  user,
  go,
  page,
  job,
}: {
  user: User;
  go: Go;
  page: number;
  job: string;
}) {
  const [rev, setRev] = useState(0);
  const list = useData<Page<Application>>(
    `/applications?page=${page}&job_id=${encodeURIComponent(job)}`,
    rev,
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [selected, setSelected] = useState<Application | null>(null);
  const [decision, setDecision] = useState("under_review");
  const [review, setReview] = useState<ApplicationReview | null>(null);
  async function inspectApplication(a: Application) {
    setSelected(a);
    setReview(null);
    setBusy(a.id);
    setError("");
    setDecision(a.status === "active" ? "under_review" : a.status);
    try {
      setReview(await api<ApplicationReview>(`/applications/${a.id}/review`));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  async function saveDecision(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    if (!review?.match) return;
    setBusy(selected.id);
    setError("");
    try {
      await api(`/applications/${selected.id}/decision`, {
        method: "PUT",
        body: JSON.stringify({
          status: decision,
          run_id: review.match.run_id,
          revision: selected.revision,
        }),
      });
      setSelected(null);
      setReview(null);
      setRev((x) => x + 1);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <>
      <Heading
        title={
          user.role === "candidate"
            ? "Your applications."
            : "Submitted applications."
        }
        text={
          user.role === "candidate"
            ? "Track your application status and read recruiter feedback. Your submitted resume version is preserved."
            : "Review applications and record a reasoned decision. Accepted means progression to the next recruitment stage, not a job offer."
        }
      />
      {error && <Notice error message={error} />}
      {selected && user.role === "recruiter" && (
        <Panel title={`Review application - ${selected.profile_label}`}>
          <p>
            {selected.job_title}. Feedback will be visible to the candidate.
            Base decisions on job-related evidence.
          </p>
          {busy && !review ? (
            <Loading />
          ) : !review ? (
            <p>
              Application evidence could not be loaded. Close and try again.
            </p>
          ) : (
            <>
              <Panel title="Submitted resume evidence">
                <p style={{ whiteSpace: "pre-wrap" }}>
                  {review.submitted_text}
                </p>
              </Panel>
              {review.match ? (
                <Panel title="Matching evidence">
                  <h3>Matching score: {review.match.score.toFixed(2)} / 100</h3>
                  <p className="small muted">
                    {review.match.method} · {date(review.match.created)} ·
                    Submitted version {review.match.profile_version}. Evidence
                    score, not a probability of success.
                  </p>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Skill</th>
                          <th>Requirement</th>
                          <th>Evidence status</th>
                          <th>Supporting passage</th>
                        </tr>
                      </thead>
                      <tbody>
                        {review.match.requirements.map((r) => (
                          <tr key={r.kind + r.skill}>
                            <td>{r.skill}</td>
                            <td>{r.kind}</td>
                            <td>{r.evidence_status.replaceAll("_", " ")}</td>
                            <td>
                              {r.evidence || "No supporting passage found"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Panel>
              ) : (
                <Panel title="Matching required">
                  <p>
                    No saved match exists for this application and the current
                    job requirements.
                  </p>
                  <Button
                    type="button"
                    onClick={() =>
                      go("opportunities", { q: selected.job_title || "" })
                    }
                  >
                    Open job matching
                  </Button>
                </Panel>
              )}
            </>
          )}
          <form noValidate onSubmit={saveDecision}>
            <Field id="recruitment-decision" label="Recruitment decision">
              <select
                id="recruitment-decision"
                value={decision}
                onChange={(e) => setDecision(e.target.value)}
              >
                <option value="under_review">Under review</option>
                <option value="accepted">Accept for next stage</option>
                <option value="rejected">Reject application</option>
              </select>
            </Field>
            <Panel title="Automatic feedback to candidate">
              <p>
                {review?.feedback_previews[decision] ||
                  "Run matching before recording a decision."}
              </p>
              <p className="small muted">
                Generated from the saved matching evidence and your chosen
                decision. Sent in the candidate dashboard when you save.
              </p>
            </Panel>
            <Button
              type="submit"
              busy={!!busy}
              disabled={!review?.match || !!busy}
            >
              Save recruitment decision
            </Button>
            <Button
              type="button"
              variant="ghost"
              disabled={!!busy}
              onClick={() => setSelected(null)}
            >
              Cancel
            </Button>
          </form>
        </Panel>
      )}
      <Panel
        title="Application history"
        action={
          job ? (
            <Button variant="ghost" onClick={() => go("applications")}>
              Show all jobs
            </Button>
          ) : undefined
        }
      >
        {list.loading ? (
          <Loading />
        ) : list.error ? (
          <>
            <Notice error message={list.error} />
            <Button onClick={list.retry}>Try again</Button>
          </>
        ) : !list.data?.items.length ? (
          <Empty title="No applications yet">
            <Button onClick={() => go("opportunities")}>
              Open opportunities
            </Button>
          </Empty>
        ) : (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Job / profile</th>
                    <th>Version</th>
                    <th>Status</th>
                    <th>Submitted / updated</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data.items.map((a) => (
                    <tr key={a.id}>
                      <td>
                        <strong>{a.job_title}</strong>
                        <div>{a.profile_label}</div>
                      </td>
                      <td>
                        Submitted version {a.profile_version}
                        <div className="tiny muted">
                          Application revision {a.revision}
                        </div>
                      </td>
                      <td>
                        {applicationStatus(a.status)}
                        {a.decisions?.map((d, i) => (
                          <div key={i} className="small">
                            <strong>{applicationStatus(d.status)}</strong>
                            <p>{d.feedback}</p>
                            <span className="tiny muted">
                              {date(d.created)}
                            </span>
                          </div>
                        ))}
                      </td>
                      <td>{date(a.updated)}</td>
                      <td>
                        {user.role === "recruiter" &&
                        a.status !== "withdrawn" ? (
                          <>
                            <Button
                              variant="ghost"
                              onClick={() => inspectApplication(a)}
                            >
                              Review application
                            </Button>
                          </>
                        ) : (
                          <span className="small muted">
                            {a.status === "active"
                              ? "Awaiting recruiter response"
                              : "See status and feedback"}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pager
              page={page}
              total={list.data.total}
              onPage={(p) => go("applications", { job, page: String(p) })}
            />
          </>
        )}
      </Panel>
    </>
  );
}

type Comparison = {
  left: { id: string; method: string; created: string; job: Job };
  right: { id: string; method: string; created: string; job: Job };
  rows: {
    candidate_id: string;
    label: string;
    before: number | null;
    after: number | null;
    delta: number | null;
    before_version: number | null;
    after_version: number | null;
    changed_requirements: string[];
    membership: string;
  }[];
  notes: string[];
};
export function Comparisons() {
  const runs = useData<Run[]>("/runs");
  const [left, setLeft] = useState("");
  const [right, setRight] = useState("");
  const [result, setResult] = useState<Comparison>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [page, setPage] = useState(1);
  const l = runs.data?.find((r) => r.id === left);
  const choices = runs.data?.filter((r) => !l || r.job_id === l.job_id);
  async function compare() {
    setBusy(true);
    setError("");
    setResult(undefined);
    try {
      setResult(await api(`/comparisons?left=${left}&right=${right}`));
      setPage(1);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Heading
        title="Compare matching snapshots."
        text="Inspect version, score and evidence changes between two saved runs for the same job."
      />
      <Panel title="Choose snapshots">
        {runs.loading ? (
          <Loading />
        ) : runs.error ? (
          <>
            <Notice error message={runs.error} />
            <Button onClick={runs.retry}>Try again</Button>
          </>
        ) : (
          <>
            <div className="two-col">
              <Field id="compare-left" label="Earlier / baseline snapshot">
                <select
                  id="compare-left"
                  value={left}
                  onChange={(e) => {
                    setLeft(e.target.value);
                    setRight("");
                    setResult(undefined);
                  }}
                >
                  <option value="">Select a snapshot</option>
                  {runs.data?.map((r, i) => (
                    <option key={r.id} value={r.id}>
                      {r.job_snapshot.title} · {date(r.created)} · Saved run{" "}
                      {(runs.data?.length || 0) - i}
                    </option>
                  ))}
                </select>
              </Field>
              <Field id="compare-right" label="Comparison snapshot">
                <select
                  id="compare-right"
                  value={right}
                  onChange={(e) => {
                    setRight(e.target.value);
                    setResult(undefined);
                  }}
                >
                  <option value="">Select same-job snapshot</option>
                  {choices
                    ?.filter((r) => r.id !== left)
                    .map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.job_snapshot.title} · {date(r.created)} · Saved run{" "}
                        {(runs.data?.length || 0) -
                          (runs.data?.findIndex((item) => item.id === r.id) ||
                            0)}
                      </option>
                    ))}
                </select>
              </Field>
            </div>
            <Button disabled={!left || !right} busy={busy} onClick={compare}>
              Compare snapshots
            </Button>
            {(runs.data?.length || 0) < 2 && (
              <p>Create two matching runs for the same job first.</p>
            )}
          </>
        )}
      </Panel>
      {error && <Notice error message={error} />}{" "}
      {result && (
        <>
          <Notice message={result.notes.join(" ")} />
          <Panel
            title={`${method(result.left.method)} → ${method(result.right.method)}`}
          >
            <p className="small muted">
              Job requirement versions: {result.left.job.version} →{" "}
              {result.right.job.version}. Profile and cohort changes are listed
              below.
            </p>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Profile</th>
                    <th>Before → after</th>
                    <th>Delta</th>
                    <th>Version / membership</th>
                    <th>Changed evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {result.rows.slice((page - 1) * 10, page * 10).map((r) => (
                    <tr key={r.candidate_id}>
                      <td>{r.label}</td>
                      <td>
                        {r.before?.toFixed(2) ?? "—"} →{" "}
                        {r.after?.toFixed(2) ?? "—"}
                      </td>
                      <td>
                        {r.delta === null
                          ? "N/A"
                          : `${r.delta > 0 ? "+" : ""}${r.delta.toFixed(2)}`}
                      </td>
                      <td>
                        v{r.before_version ?? "—"} → v{r.after_version ?? "—"}
                        <div>{r.membership}</div>
                      </td>
                      <td>
                        {r.changed_requirements.join(", ") ||
                          "No requirement passage change detected"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pager page={page} total={result.rows.length} onPage={setPage} />
          </Panel>
        </>
      )}
    </>
  );
}

type Evaluation = {
  id: string;
  created: string;
  dataset_name: string;
  dataset_sha256: string;
  synthetic: boolean;
  provenance: string;
  k: number;
  query_count: number;
  semantic_status: string;
  model_reference: string | null;
  notes: string[];
  methods: {
    method: string;
    metrics: { ndcg: number; recall: number; precision: number };
    queries: {
      query_id: string;
      metrics: {
        ndcg: number;
        recall: number;
        precision: number;
        effective_k: number;
      };
      ranking: { profile_id: string; score: number; relevance: number }[];
    }[];
  }[];
};
export function Evaluations({
  user,
  setDirty,
}: {
  user: User;
  setDirty: (v: boolean) => void;
}) {
  const [rev, setRev] = useState(0);
  const [page, setPage] = useState(1);
  const list = useData<Page<Evaluation>>(`/evaluations?page=${page}`, rev);
  const status = useData<{ semantic_configured: boolean }>(
    "/evaluation/status",
  );
  const [text, setText] = useState("");
  const [k, setK] = useState(3);
  const [semantic, setSemantic] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Evaluation>();
  async function template() {
    setError("");
    try {
      setText(JSON.stringify(await api("/evaluation/template"), null, 2));
      setDirty(true);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function evaluate() {
    setBusy(true);
    setError("");
    try {
      const dataset = JSON.parse(text);
      const r = await api<Evaluation>("/evaluations", {
        method: "POST",
        body: JSON.stringify({ dataset, k, include_semantic: semantic }),
      });
      setSelected(r);
      setRev((x) => x + 1);
      setPage(1);
      setDirty(false);
    } catch (e) {
      setError(
        e instanceof SyntaxError
          ? "Dataset JSON is invalid. Correct it before running."
          : (e as Error).message,
      );
    } finally {
      setBusy(false);
    }
  }
  const report = busy ? undefined : selected || list.data?.items[0];
  function exportReport() {
    if (!report) return;
    const link = document.createElement("a");
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }),
    );
    link.href = url;
    link.download = `model-evaluation-${report.id}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return (
    <>
      <Heading
        title="Measure matching quality."
        text="Evaluate ranking relevance on labelled resume–job examples. Metrics are calculated from the supplied dataset; no hiring outcome is inferred."
      />
      {user.role === "recruiter" && (
        <Panel title="Evaluation dataset">
          <Notice message="Use consented, pseudonymous evaluation data. Grades: 0 = not relevant, 1 = partially relevant, 2 = strongly relevant. Keep test examples separate from training data." />
          <div className="advanced-actions">
            <Button variant="secondary" onClick={template}>
              Load synthetic example
            </Button>
            <span className="small muted">
              Local semantic model:{" "}
              {status.data?.semantic_configured
                ? "configured (checked when run)"
                : "not configured"}
            </span>
          </div>
          <Field
            id="evaluation-json"
            label="Labelled dataset JSON"
            help="Paste your dataset or load the fictional smoke-test fixture. Synthetic results are not real-world accuracy."
          >
            <textarea
              className="resize-none mono"
              id="evaluation-json"
              rows={12}
              maxLength={2000000}
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                setDirty(true);
              }}
            />
          </Field>
          <div className="two-col">
            <Field id="evaluation-k" label="Top-k cutoff">
              <input
                id="evaluation-k"
                type="number"
                min={1}
                max={20}
                value={k}
                onChange={(e) => setK(Number(e.target.value))}
              />
            </Field>
            <Field id="evaluation-methods" label="Methods to compare">
              <select
                id="evaluation-methods"
                value={semantic ? "both" : "tfidf"}
                onChange={(e) => setSemantic(e.target.value === "both")}
              >
                <option value="tfidf">TF-IDF baseline</option>
                <option value="both">TF-IDF and local semantic</option>
              </select>
            </Field>
          </div>
          {error && <Notice error message={error} />}
          <Button
            disabled={!text.trim() || !Number.isInteger(k) || k < 1 || k > 20}
            busy={busy}
            onClick={evaluate}
          >
            Run evaluation
          </Button>
        </Panel>
      )}
      <Panel
        title="Saved evaluations"
        action={
          <Button variant="secondary" disabled={!report} onClick={exportReport}>
            Export evaluation
          </Button>
        }
      >
        {list.loading ? (
          <Loading />
        ) : list.error ? (
          <>
            <Notice error message={list.error} />
            <Button onClick={list.retry}>Try again</Button>
          </>
        ) : !list.data?.items.length ? (
          <Empty title="No evaluation results yet">
            <p>A recruiter can load labelled examples and run an evaluation.</p>
          </Empty>
        ) : (
          <>
            <Field id="saved-evaluation" label="Evaluation report">
              <select
                id="saved-evaluation"
                disabled={busy}
                value={report?.id || ""}
                onChange={(e) =>
                  setSelected(
                    list.data?.items.find((r) => r.id === e.target.value),
                  )
                }
              >
                {list.data.items.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.dataset_name} · {date(r.created)}
                  </option>
                ))}
              </select>
            </Field>
            <Pager
              page={page}
              total={list.data.total}
              onPage={(p) => {
                setSelected(undefined);
                setPage(p);
              }}
            />
          </>
        )}
      </Panel>
      {report && (
        <>
          <Notice
            message={
              report.synthetic
                ? "Synthetic demonstration results only. These labels are illustrative, not independent real-applicant ground truth."
                : "User-supplied evaluation labels. Verify consent, annotation quality and held-out separation before interpreting results."
            }
          />
          <Panel title={report.dataset_name}>
            <p>{report.provenance}</p>
            <p className="small mono">
              Dataset SHA-256: {report.dataset_sha256}
            </p>
            <p className="small muted">
              {report.query_count} queries · requested k={report.k} ·{" "}
              {report.model_reference
                ? `Model directory: ${report.model_reference}`
                : "Semantic method not evaluated in this report"}
            </p>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Method</th>
                    <th>NDCG@k</th>
                    <th>Recall@k</th>
                    <th>Precision@k</th>
                  </tr>
                </thead>
                <tbody>
                  {report.methods.map((m) => (
                    <tr key={m.method}>
                      <td>{m.method}</td>
                      <td>{m.metrics.ndcg.toFixed(4)}</td>
                      <td>{m.metrics.recall.toFixed(4)}</td>
                      <td>{m.metrics.precision.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="small muted">
              NDCG rewards placing highly relevant examples earlier. Recall
              measures relevant examples retrieved; precision measures relevance
              among the selected examples. Effective k is capped by each query's
              profile count.
            </p>
            {report.methods.map((m) => (
              <details key={m.method} className="evaluation-detail">
                <summary>
                  {m.method}: per-query results and ranked examples
                </summary>
                {m.queries.map((q) => (
                  <div key={q.query_id}>
                    <h3>{q.query_id}</h3>
                    <p>
                      Effective k: {q.metrics.effective_k} · NDCG{" "}
                      {q.metrics.ndcg.toFixed(4)} · Recall{" "}
                      {q.metrics.recall.toFixed(4)}
                    </p>
                    <ol>
                      {q.ranking.map((r) => (
                        <li key={r.profile_id}>
                          {r.profile_id} · score {r.score.toFixed(2)} ·
                          relevance {r.relevance}
                        </li>
                      ))}
                    </ol>
                  </div>
                ))}
              </details>
            ))}
            {report.notes.map((n) => (
              <p className="small muted" key={n}>
                {n}
              </p>
            ))}
          </Panel>
        </>
      )}
    </>
  );
}
