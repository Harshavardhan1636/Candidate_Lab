# Candidate Lab

**Version 0.2:** job-specific applications, editable job rubrics, contextual evidence labels, candidate skill-gap reports, snapshot comparison and a measured TF-IDF/local-semantic evaluation dashboard are now available. Start with [UPGRADE-v0.2.md](UPGRADE-v0.2.md) for the current workflow and model setup. New matching runs require active applications; they no longer rank the entire profile library. The current method identifiers are `skill-tfidf-v2` and `skill-semantic-v2`, with `context-rules-v2` evidence labels.

A working local research application for **Fair and Explainable Machine Learning for Automated Candidate Selection and Skill Matching**. Human-reviewed candidate-job matching, explicit score contributions, and restricted aggregate synthetic-cohort audits.

Documentation: [Product](PRODUCT.md) · [Design](DESIGN.md) · [UX contract](UX-CONTRACT.md) · [Upgrade guide](UPGRADE-v0.2.md) · [Evaluation](EVALUATION.md) · [Verification](VERIFICATION.md) · [Project report](report/Candidate_Lab_Project_Report.pdf) · [Screenshots](screenshots/)

## Run locally on Windows

Requirements: Python 3.11+ and Node.js 20.19+ (22 recommended).

```powershell
# Run from the repository root
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd ci
npm.cmd run build
$env:DEMO_MODE = '1'
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. Once dependencies are installed, `./start.ps1` builds if needed and starts the loopback demo. If PowerShell script policy blocks the helper, use the explicit commands above rather than changing machine-wide policy.

### Local demo accounts

| Role      | Email               | Password           |
| --------- | ------------------- | ------------------ |
| Recruiter | recruiter@demo.test | RecruiterDemo!2026 |
| Auditor   | auditor@demo.test   | AuditorDemo!2026   |
| Candidate | candidate@demo.test | CandidateDemo!2026 |

These accounts are created **only** when `DEMO_MODE=1` on an empty database. This is a private local research demo; do not expose demo credentials publicly. Default persistence is `data/candidate-lab.db` (SQLite). Original uploads are not retained; confirmed extracted text is stored locally. No automatic deletion of user data is performed.

The seeded workspace contains 12 synthetic profiles, 3 jobs, one published Backend Engineer job, one candidate application with its submitted version, and two saved runs: a legacy all-profile baseline and a scoped active-application run. It starts with no human reviews or recruitment decisions.

## New user registration

On the login page choose **Create a new account**, select Candidate, Recruiter or Auditor, and enter an email and matching passwords. Passwords require at least 12 characters with a letter and a number. Registration returns to sign-in with the new email filled; it does not grant a session automatically. New candidates start with an empty profile library.

Candidates can register directly. A local administrator must first generate an email-bound invitation for each recruiter or auditor:

```powershell
# Run from the repository root, against the same DATABASE_URL as the application
.\.venv\Scripts\python.exe -m backend.invite --email recruiter@example.com --role recruiter
.\.venv\Scripts\python.exe -m backend.invite --email auditor@example.com --role auditor
```

Use the intended user's actual email. The command prints a code to share privately; the user enters it during registration with the same email and role. Codes expire after 24 hours, work once, and are stored only as hashes. Set `--hours 48` to change expiry (maximum 168). A used, expired or incorrect invitation cannot create a privileged account. Existing accounts cannot use registration to change roles. Run the command against the same DATABASE_URL as the running application if using a custom database.

No email is sent automatically. Email ownership verification, password recovery and organizational SSO are not implemented. The invite command is restricted by access to the local machine/database; no public invitation-creation endpoint is exposed. All accounts share this local research workspace; approved recruiters can read saved profiles. Multi-organization isolation is not implemented.

## Developer mode

Run the backend as above and, in another terminal, `npm.cmd run dev` (http://127.0.0.1:5173). Vite proxies `/api` to port 8000. Interactive API documentation is at http://127.0.0.1:8000/docs.

## What works

- Three server-enforced roles and opaque HttpOnly session cookies; passwords hashed with salted PBKDF2.
- Persistent jobs with required/preferred skills, optimistic job-rubric editing through `GET`/`PUT` with version checks, pseudonymous candidate profiles, and PDF/DOCX/TXT extraction (2 MB maximum).
- Preview/correction before saving, profile version history, optimistic conflict protection.
- Immutable matching snapshots, exact weighted score contributions and requirement-to-passage evidence.
- Reversible human review labels with mandatory reasons and an append-only review log.
- Auditor-only aggregate cohort report with a common cutoff, 95% Wilson intervals, small-group suppression and JSON export.
- A synthetic workspace with 12 profiles, 3 jobs, one published job, one seeded application and two saved runs (legacy all-profile plus scoped active-application). Demo cohort labels are arbitrary A/B labels, never inferred demographics.
- Responsive frontend, URL-based list state, pagination, retry/empty/error handling and accessible native controls.

## Matching method and limits

The default is **skill-tfidf-v2**, an explicit heuristic: required evidence 60%, preferred evidence 15%, TF-IDF alignment 25%. With no preferred skills, required evidence becomes 75%. Only supported evidence earns coverage; learning, negated, uncertain and missing mentions are shown separately. Scores are matching indices, **not probabilities**. Contributions are exact formula terms, not SHAP or a trained predictor. Dictionary skills and aliases are defined in `backend/matching.py`. The text similarity uses recognized job-related passages; this is not comprehensive de-identification and does not guarantee freedom from proxy bias.

No real labeled dataset was supplied. Training, classification error-rate metrics, causal fairness, fairness mitigation and automatic hiring/rejection are **not claimed**. No externally hosted LLM is used. There is no email dispatch, OCR, distributed queue or background retry worker in this first release. Document processing and bounded matching are synchronous; matching rejects cohorts larger than 500 rather than silently truncating them.

### Optional local semantic model

Install `requirements-semantic.txt`, obtain and cache a compatible Sentence Transformers model separately, then set `SEMANTIC_MODEL_PATH` to that local directory before starting the server. `scripts/download_semantic_model.py` fetches the pinned `sentence-transformers/all-MiniLM-L6-v2` revision and `start.ps1` discovers it. The application uses `local_files_only=True`: inference does not automatically download a model. A load failure returns 503 and does not silently masquerade as semantic matching. The local semantic path is exercised by the test suite; evaluate and license-check any model before using real resumes. The seeded run retains its original method; create a new run after switching methods.

## Demo walkthrough

1. Sign in as recruiter. Inspect the seeded Backend Engineer job. Open Edit job, change a preferred skill, and save; the rubric version increments and stale saves return a conflict.
2. Open Matching evidence. Click Evidence, inspect contribution arithmetic and source passages, and save a reasoned review.
3. Add a profile by uploading a text PDF/DOCX/TXT or pasting text. Preview extraction, correct it and save.
4. Create and publish a job, then apply with a candidate profile. Run matching from Publish jobs and confirm the run contains only active applicants. Change a profile and verify the previous run retains its old profile-version snapshot.
5. Sign out. Sign in as auditor, adjust the common research cutoff and export the aggregate report. Review audit events.
6. Sign in as candidate and confirm only the candidate's owned profiles are visible. Restricted audit and ranking endpoints return 403 for this role.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_backend.py tests/test_registration.py tests/test_advanced.py tests/test_naming.py -q
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
# Browser tests start a separate backend and disposable database on port 8001:
# Browser tests use your installed Google Chrome
npm.cmd run test:e2e
```

The current baseline is **26 backend tests** and **9 Chrome journeys**, including job-rubric editing, application ownership, evidence rules, snapshot comparison, local semantic inference and evaluation role restrictions. Browser tests use synthetic demo accounts in a disposable database on port 8001. API tests also use a temporary database; neither modifies the live workspace on port 8000. See [VERIFICATION.md](VERIFICATION.md) for the checks performed in this workspace.

For a presentation script, architecture diagram and model card, read [EVALUATION.md](EVALUATION.md). A synthetic upload example is in `examples/resume.txt`. Run `python scripts/package_source.py` to create a ZIP with source, built frontend, documentation and screenshots, excluding local databases, credentials and dependency folders.

## PostgreSQL and Docker

For PostgreSQL set `DATABASE_URL=postgresql+psycopg://...`. The application creates its initial tables on startup. Versioned Alembic migrations are a next release requirement before evolving a populated deployment. To run Docker, put a strong `POSTGRES_PASSWORD` in `.env` and run `docker compose up --build`. Compose binds the demo only to 127.0.0.1 and stores the database in a named volume. Docker availability is environment-dependent; check [VERIFICATION.md](VERIFICATION.md) for whether it was exercised.

## Security and data boundaries

- Recruiters cannot query cohort attributes or aggregate fairness reports; auditors cannot read candidate text or individual ranking snapshots. Candidates cannot read another owner's profile.
- Cross-origin mutation requests are rejected unless their Origin is explicitly allowed. Session cookies are SameSite=Strict. For HTTPS deployments set COOKIE_SECURE=1 and configure an approved origin list.
- PDF/DOCX parsing has size/page/expanded-archive limits but is not a malware sandbox. Use synthetic or consented research files locally; production needs isolated parsing, scanning, retention controls and an organizational identity provider.
- Candidate self-registration is available. Recruiter/auditor registration requires an administrator-issued, email-bound invitation. There is no public invitation-creation or privilege-changing endpoint.
- Audit labels currently exist only for synthetic fixtures. User uploads do not acquire guessed audit attributes. True demographic auditing needs a consent and governance workflow before implementation.
- Reports suppress rates for groups with fewer than five entries. A descriptive difference and wide confidence interval are not a fairness guarantee. No real qualification labels means TPR/FPR/equalized odds are unavailable.

## Repository layout

`backend/app.py`: persistence/auth/API; `backend/matching.py`: extraction/scoring/audit arithmetic; `src`: React interface and canonical components; `tests/test_backend.py`: API/model tests; `tests`: browser journeys. Product and design boundaries live in [PRODUCT.md](PRODUCT.md), [DESIGN.md](DESIGN.md) and [UX-CONTRACT.md](UX-CONTRACT.md); verification and evaluation records are in [VERIFICATION.md](VERIFICATION.md) and [EVALUATION.md](EVALUATION.md). The Stage-1 report, source format and reusable figures are under `docs/report/`; UI captures are in `docs/screenshots/`.

## Candidate-controlled profiles

Candidates create and update their own profiles. Recruiters can browse and inspect resume evidence and extracted skills but cannot create or edit profiles. The API enforces this restriction independently of the interface. Existing profiles and historical matching evidence are retained.

## Recruitment decisions update

Recruiter → Applications → Review application → choose Under review, Accept for next stage, or Reject application → review the server-generated candidate feedback in the decision preview → Save recruitment decision. Accepting progresses the application; it is not a job offer. Candidates see status and dated feedback in Applications. Each decision records the recruiter, time and revision; stale revisions are rejected. Decisions do not overwrite submitted resume evidence or matching scores.

Candidate withdrawal and resubmission are superseded by this workflow: the interface no longer offers withdrawal, its old API returns 410, and duplicate applications are rejected. Previously withdrawn records remain historical records. Rejected applications are excluded from future matching runs; submitted, under-review and accepted applications remain eligible. Older saved matching runs retain their original results.

Recruiter decisions remain separate from matching-evidence review notes. No automatic recruitment decision or email delivery is performed. Status updates are visible inside the application. Existing data is retained; startup adds the recruitment_decisions table without changing existing table columns.

## Application review with matching evidence

Applications → Review application loads the exact submitted resume and a saved matching snapshot for that application, submitted version and current job-requirements version. The review displays score, method, date and skill evidence. Without a matching snapshot, a decision cannot be saved; open job matching first. Scores are evidence summaries, not probabilities of recruitment success.

Feedback is now generated by the server from that saved evidence and the recruiter-selected status. The manual feedback field is removed. Candidates receive the score, supported skills and required skills needing clearer evidence, with context limitations and the recruiter decision. No email is sent. A new additive decision_evidence table links each new decision to its frozen matching snapshot; later matching/profile changes do not rewrite existing feedback. Manual feedback from earlier releases remains historical. Recruiters retain control of decisions; feedback generation does not auto-select or reject people. This supersedes earlier instructions to type candidate feedback.
