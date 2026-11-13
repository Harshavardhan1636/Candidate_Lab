import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BriefcaseBusiness,
  UsersRound,
  ScanSearch,
  Scale,
  BookOpenCheck,
  LogOut,
  Plus,
  ArrowUpRight,
  ChevronRight,
  Upload,
  Check,
  ShieldCheck,
  Layers3,
  Fingerprint,
  Eye,
  EyeOff,
  Download,
} from "lucide-react";
import {
  api,
  date,
  method,
  type User,
  type Job,
  type Candidate,
  type Run,
  type Audit,
  type Page,
} from "./api";
import {
  Button,
  Field,
  Panel,
  Notice,
  Loading,
  Empty,
  Pager,
  SearchField,
  Dialog,
} from "./components";
import "./styles.css";
import { Registration } from "./Registration";
import {
  Opportunities,
  Applications,
  Comparisons,
  Evaluations,
} from "./Advanced";

function useLoad<T>(path: string | null, refresh = 0) {
  const [state, set] = useState<{ data?: T; error?: string; loading: boolean }>(
    { loading: true },
  );
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    if (!path) {
      set({ loading: false });
      return;
    }
    const controller = new AbortController();
    set({ loading: true });
    api<T>(path, { signal: controller.signal })
      .then((data) => set({ data, loading: false }))
      .catch((err) => {
        if (!controller.signal.aborted)
          set({
            error: err.message || "Could not connect to the server.",
            loading: false,
          });
      });
    return () => controller.abort();
  }, [path, refresh, retry]);
  return { ...state, retry: () => setRetry((v) => v + 1) };
}
type Go = (view: string, extra?: Record<string, string>) => void;
function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}
function Failure({ message, retry }: { message: string; retry: () => void }) {
  return (
    <>
      <Notice message={message} error />
      <Button variant="secondary" onClick={retry}>
        Try again
      </Button>
    </>
  );
}
function Login({ onLogin }: { onLogin: (u: User) => void }) {
  const [registering, setRegistering] = useState(false);
  const [success, setSuccess] = useState("");
  const [email, setEmail] = useState("recruiter@demo.test");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const health = useLoad<{ demo: boolean }>("/health");
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError("Enter your email and password.");
      document.getElementById(!email.trim() ? "email" : "password")?.focus();
      return;
    }
    setBusy(true);
    setError("");
    try {
      onLogin(
        await api<User>("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="login">
      <section className="login-story">
        <div className="brand">
          <span className="brand-mark">
            <Layers3 />
          </span>
          Candidate Lab
        </div>
        <div className="login-intro">
          <div className="eyebrow">Explainable candidate matching</div>
          <h1>
            Evidence before <br />
            decisions.
          </h1>
          <p>
            A focused workspace for candidate profiles, skill matching and
            accountable hiring reviews.
          </p>
        </div>
        <div className="login-foot">
          <ShieldCheck size={16} />
          Role-based access · Candidate, recruiter and auditor workspaces
        </div>
      </section>
      <section className="login-form">
        <div className="login-form-inner">
          <ShieldCheck className="teal" size={30} />
          {registering ? (
            <Registration
              cancel={() => setRegistering(false)}
              created={(email) => {
                setEmail(email);
                setPassword("");
                setError("");
                setSuccess(
                  "Account created. Sign in with your new credentials.",
                );
                setRegistering(false);
              }}
            />
          ) : (
            <>
              <div className="auth-eyebrow">YOUR CANDIDATE LAB ACCOUNT</div>
              <h2>Welcome back.</h2>
              <p className="muted">
                Sign in to manage profiles, review matches or explore audit
                reports.
              </p>
              <form noValidate onSubmit={submit}>
                {success && <Notice message={success} />}
                {error && <Notice error message={error} />}
                <Field id="email" label="Email">
                  <input
                    id="email"
                    type="email"
                    autoComplete="username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </Field>
                <Field id="password" label="Password">
                  <div className="secret">
                    <input
                      id="password"
                      type={show ? "text" : "password"}
                      autoComplete="current-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      className="icon-button"
                      aria-label={show ? "Hide password" : "Show password"}
                      onClick={() => setShow(!show)}
                    >
                      {show ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </Field>
                <Button type="submit" busy={busy} className="full">
                  Sign in <ArrowUpRight size={17} />
                </Button>
              </form>
              <Button
                variant="secondary"
                className="full"
                onClick={() => {
                  setPassword("");
                  setError("");
                  setSuccess("");
                  setRegistering(true);
                }}
              >
                Create a new account
              </Button>
              {health.data?.demo && (
                <div className="demo-accounts">
                  <strong>Explore with a sample account</strong>
                  <p>
                    Prefill a demo login. Sample profiles are clearly labelled.
                  </p>
                  {(["recruiter", "auditor", "candidate"] as const).map(
                    (role) => (
                      <button
                        key={role}
                        onClick={() => {
                          setEmail(`${role}@demo.test`);
                          setPassword(
                            `${role[0].toUpperCase()}${role.slice(1)}Demo!2026`,
                          );
                        }}
                        type="button"
                      >
                        {role}
                        <ArrowUpRight size={13} />
                      </button>
                    ),
                  )}
                </div>
              )}
              <p className="small muted">
                Scores support a review. They do not make employment decisions.
              </p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

function Jobs({
  go,
  user,
  q,
  page,
  notice,
}: {
  go: Go;
  user: User;
  q: string;
  page: number;
  notice: (m: string) => void;
}) {
  const load = useLoad<Page<Job>>(
    `/jobs?page=${page}&q=${encodeURIComponent(q)}`,
  );
  const overview = useLoad<{
    jobs: number;
    profiles: number;
    runs: number;
    reviews: number;
    sample_profiles: number;
  }>(user.role === "recruiter" ? "/overview" : null);
  const [busy, setBusy] = useState("");
  async function match(job: Job) {
    setBusy(job.id);
    try {
      const run = await api<Run>(`/jobs/${job.id}/runs`, { method: "POST" });
      notice(
        "Matching snapshot saved. Open any profile to inspect its evidence.",
      );
      go("matches", { run: run.id });
    } catch (e) {
      notice((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <>
      <PageHeader
        eyebrow="Recruitment workspace"
        title="Recruitment overview"
        description="Manage job requirements, review candidate evidence and keep decisions accountable."
        action={
          user.role === "recruiter" && (
            <Button onClick={() => go("job-new")}>
              <Plus size={17} />
              Create job
            </Button>
          )
        }
      />
      {overview.data && (
        <section className="overview-grid" aria-label="Workspace overview">
          {[
            {
              label: "Job details",
              value: overview.data.jobs,
              note: "Defined role requirements",
              icon: BriefcaseBusiness,
              view: "jobs",
            },
            {
              label: "Candidate profiles",
              value: overview.data.profiles,
              note: `${overview.data.sample_profiles} labelled sample profiles included`,
              icon: UsersRound,
              view: "candidates",
            },
            {
              label: "Matching snapshots",
              value: overview.data.runs,
              note: "Saved comparisons with evidence",
              icon: ScanSearch,
              view: "matches",
            },
            {
              label: "Review records",
              value: overview.data.reviews,
              note: "Recorded human review actions",
              icon: BookOpenCheck,
              view: "matches",
            },
          ].map((item) => (
            <button
              className="overview-card"
              key={item.label}
              onClick={() => go(item.view)}
            >
              <span className="overview-card-top">
                {item.label}
                <item.icon size={19} />
              </span>
              <strong>{item.value}</strong>
              <span className="small muted">{item.note}</span>
            </button>
          ))}
        </section>
      )}
      {overview.error && (
        <Notice
          error
          message="Workspace totals could not be loaded. Job details remain available below."
        />
      )}
      <div className="research-strip">
        <ShieldCheck size={21} />
        <div>
          <strong>Transparent matching, accountable review</strong>
          <span>
            Every matching run saves its job requirements, method and profile
            versions. Scores are matching indices, not hiring probabilities.
          </span>
        </div>
        <span className="badge">Human review required</span>
      </div>
      <Panel
        title="Job details"
        action={
          <span className="muted small">{load.data?.total ?? "—"} roles</span>
        }
      >
        <div className="toolbar">
          <SearchField
            value={q}
            placeholder="Search jobs"
            onChange={(q) => go("jobs", { q })}
          />
          <span className="small muted">
            Required skills drive the evidence ledger
          </span>
        </div>
        {load.loading ? (
          <Loading />
        ) : load.error ? (
          <Failure message={load.error} retry={load.retry} />
        ) : !load.data?.items.length ? (
          <Empty
            title={
              q
                ? "No jobs match your search"
                : "Create your first job requirements"
            }
          >
            <p>Add the skills candidates should demonstrate.</p>
          </Empty>
        ) : (
          <div className="job-list">
            {load.data.items.map((j) => (
              <article className="job-row" key={j.id}>
                <div className="job-icon">
                  <BriefcaseBusiness size={22} />
                </div>
                <div className="job-content">
                  <div className="row">
                    <h3>{j.title}</h3>
                    <span className="tiny muted">Job requirements</span>
                  </div>
                  <p>{j.description}</p>
                  <div className="chips">
                    {j.required.map((s) => (
                      <span key={s} className="chip">
                        {s}
                      </span>
                    ))}
                    {j.preferred.length > 0 && (
                      <span className="small muted">
                        + {j.preferred.length} preferred
                      </span>
                    )}
                  </div>
                </div>
                {user.role === "recruiter" && (
                  <Button
                    variant="secondary"
                    busy={busy === j.id}
                    disabled={!!busy}
                    onClick={() => match(j)}
                  >
                    Run matching
                    <ArrowUpRight size={16} />
                  </Button>
                )}
              </article>
            ))}
          </div>
        )}
        {load.data && (
          <Pager
            page={page}
            total={load.data.total}
            onPage={(p) => go("jobs", { q, page: String(p) })}
          />
        )}
      </Panel>
      <div className="two-col info-panels">
        <Panel title="What a score means">
          <p>
            Required skill evidence, preferred evidence and text alignment
            contribute to an inspectable matching index.
          </p>
          <span className="small muted">
            Configured scoring rules · Human assessment required
          </span>
        </Panel>
        <Panel title="What stays separate">
          <p>
            Auditor cohort attributes are stored separately and never sent to
            the matching engine or recruiter ranking.
          </p>
          <span className="small muted">
            Role-based access · Aggregate research audit
          </span>
        </Panel>
      </div>
    </>
  );
}

function JobForm({
  go,
  setDirty,
  notice,
}: {
  go: Go;
  setDirty: (v: boolean) => void;
  notice: (s: string) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [required, setRequired] = useState("");
  const [preferred, setPreferred] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const catalog = useLoad<string[]>("/skills");
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const missing =
      title.trim().length < 3
        ? "title"
        : description.trim().length < 20
          ? "description"
          : !required.trim()
            ? "required"
            : "";
    if (missing) {
      setError(
        "Add a title (3+ characters), description (20+ characters) and required skills.",
      );
      document.getElementById(missing)?.focus();
      return;
    }
    setBusy(true);
    try {
      await api("/jobs", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          required: required
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          preferred: preferred
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
        }),
      });
      setDirty(false);
      notice("Job created.");
      go("jobs", { saved: String(Date.now()) });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeader
        eyebrow="Jobs / New job"
        title="Define the evidence you need."
        description="Use role-related skills. Avoid identity, prestige and unsupported personality criteria."
      />
      <form
        className="form-layout"
        noValidate
        onSubmit={submit}
        onChange={() => setDirty(true)}
      >
        <Panel title="Job requirements">
          {error && <Notice error message={error} />}
          <Field
            id="title"
            label="Job title"
            error={
              error && title.trim().length < 3
                ? "Use at least 3 characters."
                : undefined
            }
          >
            <input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={120}
            />
          </Field>
          <Field
            id="description"
            error={
              error && description.trim().length < 20
                ? "Use at least 20 characters."
                : undefined
            }
            label="Role description"
            help="Describe responsibilities and context. Matching uses the required and preferred skills below."
          >
            <textarea
              className="resize-none"
              id="description"
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Field>
          <Field
            id="required"
            error={
              error && !required.trim() ? "Add a supported skill." : undefined
            }
            label="Required skills"
            help="Comma-separated skills from the supported vocabulary."
          >
            <input
              id="required"
              value={required}
              placeholder="Python, SQL, REST APIs, Testing"
              onChange={(e) => setRequired(e.target.value)}
            />
          </Field>
          <Field
            id="preferred"
            label="Preferred skills"
            help="Optional. Do not repeat required skills."
          >
            <input
              id="preferred"
              value={preferred}
              placeholder="FastAPI, Docker, Git"
              onChange={(e) => setPreferred(e.target.value)}
            />
          </Field>
          <div className="form-actions">
            <Button
              variant="secondary"
              type="button"
              onClick={() => go("jobs")}
            >
              Cancel
            </Button>
            <Button type="submit" busy={busy}>
              Create job
            </Button>
          </div>
        </Panel>
        <aside>
          <Panel title="Supported vocabulary">
            <div className="chips">
              {catalog.data?.map((s) => (
                <span className="chip" key={s}>
                  {s}
                </span>
              ))}
            </div>
            <p className="small muted">
              Vocabulary-based evidence matching is explicit and reproducible.
              Extending the dictionary requires versioned model evaluation.
            </p>
          </Panel>
        </aside>
      </form>
    </>
  );
}

function Candidates({
  go,
  page,
  q,
  user,
}: {
  go: Go;
  page: number;
  q: string;
  user: User;
}) {
  const load = useLoad<Page<Candidate>>(
    `/candidates?page=${page}&q=${encodeURIComponent(q)}`,
  );
  return (
    <>
      <PageHeader
        eyebrow="Evidence library"
        title={
          user.role === "candidate"
            ? "Your profile, your evidence."
            : "Profiles ready for review."
        }
        description={
          user.role === "candidate"
            ? "Manage your resume, review extracted skills and keep your evidence up to date."
            : "Review candidate profiles, extracted skills and supporting resume evidence."
        }
        action={
          user.role === "candidate" && (
            <Button onClick={() => go("profile-new")}>
              <Plus size={17} />
              Add profile
            </Button>
          )
        }
      />
      <Panel title="Candidate profiles">
        <div className="toolbar">
          <SearchField
            value={q}
            placeholder="Search candidate profiles"
            onChange={(q) => go("candidates", { q })}
          />
          <span className="small muted">
            Pseudonymous labels · {load.data?.total ?? "—"} profiles
          </span>
        </div>
        {load.loading ? (
          <Loading />
        ) : load.error ? (
          <Failure message={load.error} retry={load.retry} />
        ) : !load.data?.items.length ? (
          <Empty
            title={
              q
                ? "No matching profiles"
                : user.role === "candidate"
                  ? "Add your first candidate profile"
                  : "No candidate profiles yet"
            }
          >
            <p>
              {user.role === "candidate"
                ? "Upload a document or paste job-related evidence."
                : "Profiles will appear when candidates create them in their accounts."}
            </p>
          </Empty>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Profile</th>
                  <th>Evidence found</th>
                  <th>Version</th>
                  <th>Updated</th>
                  <th>
                    <span className="sr-only">Action</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {load.data.items.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <strong>{c.label}</strong>
                      <div className="tiny muted">
                        {c.synthetic
                          ? "Synthetic fixture"
                          : "User-provided profile"}
                      </div>
                    </td>
                    <td>
                      <div className="chips">
                        {c.skills.slice(0, 4).map((s) => (
                          <span className="chip" key={s.skill}>
                            {s.skill}
                          </span>
                        ))}
                        {c.skills.length > 4 && (
                          <span className="tiny muted">
                            +{c.skills.length - 4}
                          </span>
                        )}
                        {!c.skills.length && (
                          <span>Needs extraction review</span>
                        )}
                      </div>
                    </td>
                    <td>Version {c.version}</td>
                    <td className="small">{date(c.updated)}</td>
                    <td>
                      <Button
                        variant="ghost"
                        onClick={() => go("profile", { id: c.id })}
                      >
                        Inspect
                        <ArrowUpRight size={15} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {load.data && (
          <Pager
            page={page}
            total={load.data.total}
            onPage={(p) => go("candidates", { q, page: String(p) })}
          />
        )}
      </Panel>
    </>
  );
}

function ProfilePage({
  user,
  ident,
  go,
  setDirty,
  notice,
}: {
  ident: string | null;
  user: User;
  go: Go;
  setDirty: (v: boolean) => void;
  notice: (s: string) => void;
}) {
  const load = useLoad<Candidate>(ident ? `/candidates/${ident}` : null);
  if (ident && load.loading) return <Loading />;
  if (load.error) return <Failure message={load.error} retry={load.retry} />;
  if (user.role === "recruiter" && load.data) {
    const profile = load.data;
    return (
      <>
        <PageHeader
          eyebrow="Candidate profile / Review"
          title={profile.label}
          description="Read-only candidate information. Candidates manage their own resumes and skills."
          action={
            <Button variant="secondary" onClick={() => go("candidates")}>
              Back to profiles
            </Button>
          }
        />
        <div className="form-layout">
          <Panel title={`Resume evidence � Version ${profile.version}`}>
            <p style={{ whiteSpace: "pre-wrap" }}>{profile.text}</p>
          </Panel>
          <aside>
            <Panel title="Extracted skills and evidence">
              {profile.warnings.map((warning) => (
                <Notice key={warning} message={warning} />
              ))}
              {profile.skills.length === 0 && (
                <p>No supported skill evidence found.</p>
              )}
              {profile.skills.map((skill) => (
                <div key={skill.skill}>
                  <h3>{skill.skill}</h3>
                  <p className="small muted">{skill.status}</p>
                  <p>{skill.passage}</p>
                </div>
              ))}
            </Panel>
          </aside>
        </div>
      </>
    );
  }
  return (
    <ProfileForm
      key={ident || "new"}
      initial={load.data}
      go={go}
      setDirty={setDirty}
      notice={notice}
    />
  );
}
function ProfileForm({
  initial,
  go,
  setDirty,
  notice,
}: {
  initial?: Candidate;
  go: Go;
  setDirty: (v: boolean) => void;
  notice: (s: string) => void;
}) {
  const [label, setLabel] = useState(initial?.label || "");
  const [text, setText] = useState(initial?.text || "");
  const [preview, setPreview] = useState<{
    skills: Candidate["skills"];
    warnings: string[];
  } | null>(initial || null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const file = useRef<HTMLInputElement>(null);
  async function parse(f: File) {
    setError("");
    if (!/\.(pdf|docx|txt)$/i.test(f.name) || f.size > 2 * 1024 * 1024) {
      setError("Choose a PDF, DOCX or TXT file under 2 MB.");
      return;
    }
    const form = new FormData();
    form.append("file", f);
    setBusy("parse");
    try {
      const data = await api<{
        text: string;
        skills: Candidate["skills"];
        warnings: string[];
      }>("/resumes/parse", { method: "POST", body: form });
      setText(data.text);
      setPreview(data);
      setDirty(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
      if (file.current) file.current.value = "";
    }
  }
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (label.trim().length < 3 || text.trim().length < 40) {
      setError(
        "Add a clear profile name (3+ characters) and at least 40 characters of resume evidence.",
      );
      document
        .getElementById(label.trim().length < 3 ? "label" : "resume-text")
        ?.focus();
      return;
    }
    setBusy("save");
    setError("");
    try {
      await api(initial ? `/candidates/${initial.id}` : "/candidates", {
        method: initial ? "PUT" : "POST",
        body: JSON.stringify({
          label: label.trim(),
          text,
          version: initial?.version,
        }),
      });
      setDirty(false);
      notice(
        initial
          ? "Profile corrected. Previous matching snapshots are unchanged."
          : "Candidate profile saved.",
      );
      go("candidates", { saved: String(Date.now()) });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  async function inspect() {
    if (text.trim().length < 40) {
      setError("Paste at least 40 characters of evidence first.");
      return;
    }
    setBusy("inspect");
    try {
      setPreview(
        await api("/extract", {
          method: "POST",
          body: JSON.stringify({ label: label || "Draft profile", text }),
        }),
      );
      setError("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <>
      <PageHeader
        eyebrow="Profiles / Evidence review"
        title={
          initial
            ? "Correct the profile evidence."
            : "Bring the evidence into view."
        }
        description="Original files are parsed in memory. Only the text you confirm is saved to this workspace."
      />
      <form className="form-layout" noValidate onSubmit={save}>
        <Panel
          title={
            initial
              ? `Profile version ${initial.version}`
              : "New candidate profile"
          }
        >
          {error && <Notice error message={error} />}
          <Field
            id="label"
            label="Profile name"
            help="Use a clear name, such as a candidate name or a descriptive professional profile title."
          >
            <input
              id="label"
              value={label}
              onChange={(e) => {
                setLabel(e.target.value);
                setDirty(true);
              }}
              placeholder="Python Developer - Project Experience"
              maxLength={80}
            />
          </Field>
          <div className="upload">
            <Upload size={25} />
            <div>
              <strong>Upload a resume</strong>
              <p>Text PDF, DOCX or TXT · Up to 2 MB</p>
            </div>
            <input
              type="file"
              id="resume-file"
              ref={file}
              accept=".pdf,.docx,.txt"
              className="sr-only"
              onChange={(e) => e.target.files?.[0] && parse(e.target.files[0])}
            />
            <Button
              type="button"
              variant="secondary"
              busy={busy === "parse"}
              disabled={!!busy}
              onClick={() => file.current?.click()}
            >
              Choose file
            </Button>
          </div>
          <Field
            id="resume-text"
            label="Resume evidence"
            help="Review and correct extraction. Scanned PDFs need OCR outside this first version."
          >
            <textarea
              className="resize-none"
              id="resume-text"
              rows={12}
              value={text}
              maxLength={30000}
              onChange={(e) => {
                setText(e.target.value);
                setDirty(true);
                setPreview(null);
              }}
              placeholder="Built REST APIs with Python and FastAPI…"
            />
          </Field>
          <div className="form-actions">
            <Button
              variant="secondary"
              type="button"
              disabled={!!busy}
              busy={busy === "inspect"}
              onClick={inspect}
            >
              Preview extraction
            </Button>
            <div>
              <Button
                variant="ghost"
                type="button"
                onClick={() => go("candidates")}
              >
                Cancel
              </Button>
              <Button type="submit" busy={busy === "save"} disabled={!!busy}>
                {initial ? "Save changes" : "Save profile"}
              </Button>
            </div>
          </div>
        </Panel>
        <aside>
          <Panel title="Extraction ledger">
            {preview ? (
              <>
                {preview.warnings.map((w) => (
                  <Notice key={w} message={w} />
                ))}
                <p className="small muted">
                  Dictionary extraction · Check every passage
                </p>
                {preview.skills.map((s) => (
                  <div className="evidence-item" key={s.skill}>
                    <strong>{s.skill}</strong>
                    <span className="badge evidence-state">
                      {s.status || "legacy mention"}
                    </span>
                    <p>{s.passage}</p>
                  </div>
                ))}
                {!preview.skills.length && (
                  <Empty title="No dictionary skills found">
                    <p>Correct the text or extend the skill vocabulary.</p>
                  </Empty>
                )}
              </>
            ) : (
              <Empty title="Preview the extracted skills">
                <p>
                  Upload or paste text, then inspect the requirements and
                  passages.
                </p>
              </Empty>
            )}
          </Panel>
          <p className="small muted">
            Profile corrections create a version. Matching snapshots retain the
            evidence available at the time of each run.
          </p>
        </aside>
      </form>
    </>
  );
}

function MatchPage({
  selectedRun,
  go,
  notice,
  page,
}: {
  selectedRun: string | null;
  go: Go;
  notice: (s: string) => void;
  page: number;
}) {
  const list = useLoad<Run[]>("/runs");
  const runId = selectedRun || list.data?.[0]?.id || null;
  const [refresh, setRefresh] = useState(0);
  const detail = useLoad<Run>(runId ? `/runs/${runId}` : null, refresh);
  const [selected, setSelected] = useState<string | null>(null);
  const [reason, setReason] = useState("");
  const [status, setStatus] = useState("shortlisted");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    setSelected(null);
    setReason("");
  }, [runId]);
  const row = detail.data?.results?.find((r) => r.candidate_id === selected);
  async function review(e: React.FormEvent) {
    e.preventDefault();
    if (reason.trim().length < 10) {
      setError("Record a job-related reason with at least 10 characters.");
      document.getElementById("review-reason")?.focus();
      return;
    }
    setBusy(true);
    setError("");
    try {
      await api(`/runs/${runId}/reviews`, {
        method: "POST",
        body: JSON.stringify({
          candidate_id: row!.candidate_id,
          status,
          reason: reason.trim(),
        }),
      });
      notice("Human review recorded. The matching score was not changed.");
      setRefresh((v) => v + 1);
      setReason("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeader
        eyebrow="Matching / Evidence workspace"
        title="Understand the match."
        description="A score is a starting point. Read the evidence and record your own review."
      />
      <div className="toolbar run-toolbar">
        <label htmlFor="run-select">Matching snapshot</label>
        <select
          id="run-select"
          value={runId || ""}
          onChange={(e) => go("matches", { run: e.target.value })}
        >
          {list.data?.map((r) => (
            <option key={r.id} value={r.id}>
              {r.job_snapshot.title} · {date(r.created)}
            </option>
          ))}
        </select>
      </div>
      {list.loading || detail.loading ? (
        <Loading />
      ) : list.error || detail.error ? (
        <Failure
          message={list.error || detail.error || ""}
          retry={() => {
            list.retry();
            detail.retry();
          }}
        />
      ) : !detail.data ? (
        <Panel>
          <Empty title="No matching snapshots yet">
            <p>Create a job and add profiles, then run matching.</p>
            <Button onClick={() => go("jobs")}>Open jobs</Button>
          </Empty>
        </Panel>
      ) : (
        <>
          <div className="snapshot">
            <div>
              <span className="eyebrow">{detail.data.job_snapshot.title}</span>
              <h2>
                {detail.data.candidate_count} profiles, one set of job
                requirements.
              </h2>
              <span className="small muted">
                {method(detail.data.method)} · Job requirements version
                {detail.data.job_snapshot.version}
              </span>
            </div>
            <div className="snapshot-note">
              <Fingerprint size={22} />
              <span>
                Immutable snapshot
                <br />
                <strong>{detail.data.id.slice(0, 12)}</strong>
              </span>
            </div>
          </div>
          <Notice
            message={
              detail.data.job_snapshot.scope === "active_applications"
                ? "This snapshot compares only active applications for this job, using the submitted profile versions."
                : "Legacy snapshot: this earlier run may include all saved profiles. New runs compare active job applicants only."
            }
          />
          <div className={`results-layout ${row ? "with-detail" : ""}`}>
            <Panel
              title="Candidate evidence ranking"
              action={<span className="small muted">Match index / 100</span>}
            >
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Profile</th>
                      <th>Match</th>
                      <th>Required skills supported</th>
                      <th>Review</th>
                      <th>
                        <span className="sr-only">Inspect</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.data.results
                      ?.slice((page - 1) * 10, page * 10)
                      .map((r, i) => (
                        <tr
                          key={r.candidate_id}
                          className={
                            selected === r.candidate_id ? "selected-row" : ""
                          }
                        >
                          <td>
                            <span className="rank">
                              {(page - 1) * 10 + i + 1}
                            </span>
                            <strong>{r.candidate_label}</strong>
                            <div className="tiny muted">
                              Submitted version {r.profile_version}
                            </div>
                          </td>
                          <td>
                            <strong className="score">
                              {r.score.toFixed(1)}
                            </strong>
                            <div className="mini-track">
                              <span style={{ width: `${r.score}%` }} />
                            </div>
                          </td>
                          <td>
                            {
                              r.requirements.filter(
                                (x) => x.kind === "required" && x.matched,
                              ).length
                            }{" "}
                            /{" "}
                            {
                              r.requirements.filter(
                                (x) => x.kind === "required",
                              ).length
                            }{" "}
                            found
                          </td>
                          <td>
                            <span
                              className={`badge ${r.review?.status === "shortlisted" ? "success" : ""}`}
                            >
                              {(r.review?.status || "needs_review").replaceAll(
                                "_",
                                " ",
                              )}
                            </span>
                          </td>
                          <td>
                            <Button
                              variant="ghost"
                              onClick={() => {
                                setSelected(r.candidate_id);
                                setReason("");
                                setError("");
                              }}
                            >
                              Evidence
                              <ChevronRight size={16} />
                            </Button>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
              <Pager
                page={page}
                total={detail.data.candidate_count}
                onPage={(p) => go("matches", { run: runId!, page: String(p) })}
              />
            </Panel>
            {row && (
              <aside className="detail-panel">
                <Panel
                  title={row.candidate_label}
                  action={
                    <Button variant="ghost" onClick={() => setSelected(null)}>
                      Close
                    </Button>
                  }
                >
                  <p className="small muted">
                    Evidence at profile v{row.profile_version}. No evidence
                    found does not establish a missing skill.
                  </p>
                  <h3 className="subhead">How the score adds up</h3>
                  {row.components.map((c) => (
                    <div className="contribution" key={c.name}>
                      <div>
                        <span>{c.name}</span>
                        <strong>+{c.contribution.toFixed(1)}</strong>
                      </div>
                      <div className="bar-track">
                        <span style={{ width: `${c.value * 100}%` }} />
                      </div>
                      <span className="tiny muted">
                        {Math.round(c.weight * 100)}% of score ·{" "}
                        {Math.round(c.value * 100)}% alignment
                      </span>
                    </div>
                  ))}
                  <div className="ledger-title">
                    <h3>Requirement → evidence</h3>
                    <BookOpenCheck size={18} />
                  </div>
                  {row.requirements.map((req) => (
                    <div
                      key={`${req.kind}-${req.skill}`}
                      className={`requirement ${req.matched ? "found" : ""}`}
                    >
                      <div>
                        <span className="requirement-symbol">
                          {req.matched ? <Check size={14} /> : "—"}
                        </span>
                        <strong>{req.skill}</strong>
                        <span className="tiny muted">{req.kind}</span>
                        <span className="badge">
                          {(
                            req.evidence_status ||
                            (req.matched ? "legacy match" : "not found")
                          ).replaceAll("_", " ")}
                        </span>
                      </div>
                      <p>
                        {req.evidence ||
                          "No supporting evidence found in the scoring text."}
                      </p>
                      {req.notes?.map((n) => (
                        <p className="small muted" key={n}>
                          {n}
                        </p>
                      ))}
                    </div>
                  ))}
                  {row.review && (
                    <div className="saved-review">
                      <strong>Last human review</strong>
                      <p>{row.review.reason}</p>
                      <span className="small muted">
                        {date(row.review.created)}
                      </span>
                    </div>
                  )}
                  <form noValidate onSubmit={review}>
                    <h3 className="subhead">Record your review</h3>
                    {error && <Notice error message={error} />}
                    <Field id="review-status" label="Review status">
                      <select
                        id="review-status"
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                      >
                        <option value="shortlisted">
                          Shortlisted for human consideration
                        </option>
                        <option value="more_information">
                          Request more information
                        </option>
                        <option value="needs_review">Needs review</option>
                      </select>
                    </Field>
                    <Field
                      id="review-reason"
                      label="Job-related reason"
                      error={
                        error && reason.trim().length < 10
                          ? "Record at least 10 characters."
                          : undefined
                      }
                    >
                      <textarea
                        className="resize-none"
                        id="review-reason"
                        rows={3}
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="Explain the evidence behind your review…"
                      />
                    </Field>
                    <Button type="submit" className="full" busy={busy}>
                      Save review
                    </Button>
                    <p className="tiny muted">
                      An internal review label, not an automated employment
                      decision.
                    </p>
                  </form>
                </Panel>
              </aside>
            )}
          </div>
          <p className="footnote">
            Method: weighted skill evidence +{" "}
            {detail.data.method.includes("semantic")
              ? "local semantic"
              : "TF-IDF lexical"}{" "}
            alignment. Contributions are exact rubric terms, not SHAP values or
            causal explanations.
          </p>
        </>
      )}
    </>
  );
}

function AuditPage() {
  const list = useLoad<Run[]>("/runs");
  const [run, setRun] = useState("");
  const [threshold, setThreshold] = useState(60);
  const selected = run || list.data?.[0]?.id;
  const report = useLoad<Audit>(
    selected ? `/audit/fairness/${selected}?threshold=${threshold}` : null,
  );
  function download() {
    if (!report.data) return;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(
      new Blob([JSON.stringify(report.data, null, 2)], {
        type: "application/json",
      }),
    );
    a.download = `cohort-audit-${report.data.run_id}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  return (
    <>
      <PageHeader
        eyebrow="Auditor workspace / Aggregate evaluation"
        title="Measure the differences."
        description="Inspect simulated selection rates with sample sizes and uncertainty. No single measure proves fairness."
        action={
          <Button
            variant="secondary"
            disabled={!report.data}
            onClick={download}
          >
            <Download size={16} />
            Export report
          </Button>
        }
      />
      <Notice message="Synthetic cohort labels only. This demonstration does not measure demographic fairness in a real applicant population." />
      <Panel title="Research comparison settings">
        <div className="audit-controls">
          <Field id="audit-run" label="Matching snapshot">
            <select
              id="audit-run"
              value={selected || ""}
              onChange={(e) => setRun(e.target.value)}
            >
              {list.data?.map((r) => (
                <option value={r.id} key={r.id}>
                  {r.job_snapshot.title} · {date(r.created)}
                </option>
              ))}
            </select>
          </Field>
          <Field
            id="threshold"
            label={`Common score cutoff: ${threshold}`}
            help="One shared research threshold, not a hiring policy."
          >
            <input
              id="threshold"
              type="range"
              min={0}
              max={100}
              step={5}
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
            />
          </Field>
        </div>
      </Panel>
      {report.loading || list.loading ? (
        <Loading />
      ) : report.error || list.error ? (
        <Failure
          message={report.error || list.error || ""}
          retry={() => {
            report.retry();
            list.retry();
          }}
        />
      ) : !report.data ? (
        <Panel>
          <Empty title="No matching run available">
            <p>A recruiter must create a snapshot first.</p>
          </Empty>
        </Panel>
      ) : (
        <>
          <div className="metric-grid">
            <div className="metric">
              <span>Audited profiles</span>
              <strong>{report.data.audited_count}</strong>
              <small>Consented synthetic fixtures</small>
            </div>
            <div className="metric">
              <span>Without audit attributes</span>
              <strong>{report.data.unattributed_count}</strong>
              <small>Excluded from group comparisons</small>
            </div>
            <div className="metric">
              <span>Selection-rate difference</span>
              <strong>
                {report.data.demographic_parity_difference === null
                  ? "N/A"
                  : `${(report.data.demographic_parity_difference * 100).toFixed(1)} pp`}
              </strong>
              <small>Descriptive, not a fairness verdict</small>
            </div>
          </div>
          <Panel
            title="Cohort selection rates"
            action={<span className="small muted">95% Wilson intervals</span>}
          >
            <div className="audit-bars">
              {report.data.groups.map((g) => (
                <div key={g.group} className="audit-group">
                  <div>
                    <strong>{g.group}</strong>
                    <span className="small muted">n = {g.count}</span>
                  </div>
                  {g.suppressed ? (
                    <p>Suppressed: fewer than 5 records.</p>
                  ) : (
                    <>
                      <div className="audit-track">
                        <span
                          style={{ width: `${g.selection_rate! * 100}%` }}
                        />
                      </div>
                      <div className="row">
                        <span>
                          {g.selected} of {g.count} above cutoff
                        </span>
                        <strong>{(g.selection_rate! * 100).toFixed(1)}%</strong>
                      </div>
                      <p className="small muted">
                        Interval: {(g.interval![0] * 100).toFixed(1)}%–
                        {(g.interval![1] * 100).toFixed(1)}%
                      </p>
                    </>
                  )}
                </div>
              ))}
            </div>
            {!report.data.groups.length && (
              <Empty title="No audit attributes for this run">
                <p>
                  No demographic inference or automatic grouping is performed.
                </p>
              </Empty>
            )}
          </Panel>
          <Panel title="Interpretation and limits">
            <ul className="limits">
              {report.data.limitations.map((l) => (
                <li key={l}>{l}</li>
              ))}
            </ul>
            <p className="small muted">
              {report.data.provenance} Method: {method(report.data.method)}.
              Changing the cutoff recalculates the audit; it does not change the
              saved matching scores.
            </p>
          </Panel>
        </>
      )}
    </>
  );
}
function Events({ page, go }: { page: number; go: Go }) {
  const load = useLoad<
    Page<{ id: string; action: string; object_id: string; created: string }>
  >(`/audit/events?page=${page}`);
  return (
    <>
      <PageHeader
        eyebrow="Auditor workspace / Traceability"
        title="A record of the work."
        description="Append-only application events connect profile changes, matching snapshots and human review."
      />
      <Panel title="Workspace event log">
        {load.loading ? (
          <Loading />
        ) : load.error ? (
          <Failure message={load.error} retry={load.retry} />
        ) : (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>Object reference</th>
                    <th>Recorded</th>
                  </tr>
                </thead>
                <tbody>
                  {load.data?.items.map((e) => (
                    <tr key={e.id}>
                      <td>{e.action}</td>
                      <td className="mono small">{e.object_id.slice(0, 16)}</td>
                      <td>{date(e.created)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {load.data && (
              <Pager
                page={page}
                total={load.data.total}
                onPage={(p) => go("events", { page: String(p) })}
              />
            )}
          </>
        )}
      </Panel>
    </>
  );
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);
  const [route, setRoute] = useState(new URLSearchParams(location.search));
  const [message, setMessage] = useState("");
  const [dirty, setDirty] = useState(false);
  const dirtyRef = useRef(false);
  const routeRef = useRef(location.href);
  const [pending, setPending] = useState<(() => void) | null>(null);
  const setDraft = (v: boolean) => {
    dirtyRef.current = v;
    setDirty(v);
  };
  function rawGo(view: string, extra: Record<string, string> = {}) {
    const p = new URLSearchParams({ view, ...extra });
    history.pushState(null, "", `?${p}`);
    routeRef.current = location.href;
    setRoute(p);
    window.scrollTo({ top: 0 });
  }
  const go: Go = (view, extra = {}) => {
    if (dirtyRef.current) {
      setPending(() => () => {
        setDraft(false);
        rawGo(view, extra);
      });
      return;
    }
    rawGo(view, extra);
  };
  useEffect(() => {
    api<User>("/auth/me")
      .then(setUser)
      .catch(() => {})
      .finally(() => setChecking(false));
  }, []);
  useEffect(() => {
    const fn = () => {
      const target = location.href;
      if (dirtyRef.current) {
        history.pushState(null, "", routeRef.current);
        setPending(() => () => {
          setDraft(false);
          history.pushState(null, "", target);
          routeRef.current = target;
          setRoute(new URLSearchParams(location.search));
        });
      } else {
        routeRef.current = target;
        setRoute(new URLSearchParams(location.search));
      }
    };
    window.addEventListener("popstate", fn);
    return () => window.removeEventListener("popstate", fn);
  }, []);
  useEffect(() => {
    const expired = () => {
      setUser(null);
      setDraft(false);
      setPending(null);
    };
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, []);
  useEffect(() => {
    if (!dirty) return;
    const fn = (e: BeforeUnloadEvent) => e.preventDefault();
    window.addEventListener("beforeunload", fn);
    return () => window.removeEventListener("beforeunload", fn);
  }, [dirty]);
  const fallback =
    user?.role === "auditor"
      ? "audit"
      : user?.role === "candidate"
        ? "candidates"
        : "jobs";
  const view = route.get("view") || fallback;
  useEffect(() => {
    document.title = `${view.replaceAll("-", " ")} · Candidate Lab`;
  }, [view]);
  async function logout() {
    const action = async () => {
      try {
        await api("/auth/logout", { method: "POST" });
        setUser(null);
        setDraft(false);
        setMessage("");
        history.replaceState(null, "", location.pathname);
        setRoute(new URLSearchParams());
      } catch (e) {
        setMessage((e as Error).message);
      }
    };
    if (dirtyRef.current) setPending(() => action);
    else await action();
  }
  if (checking) return <Loading />;
  if (!user)
    return (
      <Login
        onLogin={(u) => {
          setUser(u);
          rawGo(
            u.role === "auditor"
              ? "audit"
              : u.role === "candidate"
                ? "candidates"
                : "jobs",
          );
        }}
      />
    );
  const nav =
    user.role === "auditor"
      ? [
          { id: "audit", title: "Cohort audit", icon: Scale },
          { id: "events", title: "Audit trail", icon: Fingerprint },
          { id: "evaluations", title: "Model evaluation", icon: ScanSearch },
        ]
      : user.role === "candidate"
        ? [
            { id: "candidates", title: "My profiles", icon: UsersRound },
            {
              id: "opportunities",
              title: "Job opportunities",
              icon: BriefcaseBusiness,
            },
            {
              id: "applications",
              title: "My applications",
              icon: BookOpenCheck,
            },
          ]
        : [
            { id: "jobs", title: "Job details", icon: BriefcaseBusiness },
            { id: "candidates", title: "Candidate profiles", icon: UsersRound },
            { id: "matches", title: "Matching evidence", icon: ScanSearch },
            {
              id: "opportunities",
              title: "Publish jobs",
              icon: BriefcaseBusiness,
            },
            { id: "applications", title: "Applications", icon: UsersRound },
            { id: "compare", title: "Compare snapshots", icon: Layers3 },
            { id: "evaluations", title: "Model evaluation", icon: Scale },
          ];
  const allowed =
    user.role === "auditor"
      ? ["audit", "events", "evaluations"]
      : user.role === "candidate"
        ? [
            "candidates",
            "profile",
            "profile-new",
            "opportunities",
            "applications",
          ]
        : [
            "jobs",
            "job-new",
            "candidates",
            "profile",
            "matches",
            "opportunities",
            "applications",
            "compare",
            "evaluations",
          ];
  const page = Math.max(1, Number(route.get("page")) || 1);
  const q = route.get("q") || "";
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          href="?view=jobs"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            go(fallback);
          }}
        >
          <span className="brand-mark">
            <Layers3 size={22} />
          </span>
          <span>
            Candidate<span className="brand-light">Lab</span>
          </span>
        </a>
        <div className="nav-label">Workspace</div>
        <nav aria-label="Main navigation">
          {nav.map((n) => (
            <a
              href={`?view=${n.id}`}
              className={
                view.startsWith(n.id === "candidates" ? "profile" : n.id) ||
                view === n.id
                  ? "active"
                  : ""
              }
              aria-current={view === n.id ? "page" : undefined}
              key={n.id}
              onClick={(e) => {
                e.preventDefault();
                go(n.id);
              }}
            >
              <n.icon size={19} />
              {n.title}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="principle">
            <BookOpenCheck size={20} />
            <strong>Evidence, then judgment.</strong>
            <p>Inspect the match. Keep the human decision accountable.</p>
          </div>
          <div className="account">
            <div className="avatar">{user.role[0].toUpperCase()}</div>
            <div>
              <strong>{user.role}</strong>
              <span>Signed in</span>
            </div>
            <button
              className="icon-button"
              aria-label="Sign out"
              title="Sign out"
              onClick={logout}
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>
      <main className="main">
        <div className="topbar">
          <span>
            <span className="status-dot" />
            Candidate intelligence
          </span>
          <div>
            <span className="tiny">Local-first</span>
            <span className="topbar-separator" />
            <span className="small">{user.role} access</span>
          </div>
        </div>
        <div className="page-content">
          {message && (
            <Notice message={message} onClose={() => setMessage("")} />
          )}
          <div className="sr-only" aria-live="polite">
            {message}
          </div>
          {!allowed.includes(view) ? (
            <Panel>
              <Empty title="This view is not available for your role">
                <Button onClick={() => go(fallback)}>
                  Return to workspace
                </Button>
              </Empty>
            </Panel>
          ) : view === "opportunities" ? (
            <Opportunities user={user} go={go} page={page} q={q} />
          ) : view === "applications" ? (
            <Applications
              user={user}
              go={go}
              page={page}
              job={route.get("job") || ""}
            />
          ) : view === "compare" ? (
            <Comparisons />
          ) : view === "evaluations" ? (
            <Evaluations user={user} setDirty={setDraft} />
          ) : view === "jobs" ? (
            <Jobs go={go} user={user} q={q} page={page} notice={setMessage} />
          ) : view === "job-new" ? (
            <JobForm go={go} setDirty={setDraft} notice={setMessage} />
          ) : view === "candidates" ? (
            <Candidates go={go} page={page} q={q} user={user} />
          ) : view === "profile" || view === "profile-new" ? (
            <ProfilePage
              user={user}
              ident={view === "profile" ? route.get("id") : null}
              go={go}
              setDirty={setDraft}
              notice={setMessage}
            />
          ) : view === "matches" ? (
            <MatchPage
              selectedRun={route.get("run")}
              go={go}
              notice={setMessage}
              page={page}
            />
          ) : view === "audit" ? (
            <AuditPage />
          ) : (
            <Events page={page} go={go} />
          )}
        </div>
        <footer className="app-footer">
          Candidate Lab · Fair and Explainable Candidate Matching
          <span>Explainable matching · Human review required</span>
        </footer>
      </main>
      {pending && (
        <Dialog title="Leave unsaved changes?" close={() => setPending(null)}>
          <p>
            Your current form changes have not been saved. Stay to finish, or
            discard this draft.
          </p>
          <div className="form-actions">
            <Button
              variant="secondary"
              onClick={() => setPending(null)}
              autoFocus
            >
              Keep editing
            </Button>
            <Button
              onClick={() => {
                const action = pending;
                setPending(null);
                action();
              }}
            >
              Discard draft and leave
            </Button>
          </div>
        </Dialog>
      )}
    </div>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
