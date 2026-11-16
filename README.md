# Candidate Lab

**Fair and Explainable Machine Learning for Automated Candidate Selection and Skill Matching**

A local-first research application that connects explicit job requirements to evidence in candidate profiles. Every match shows its exact score contributions and supporting passages, every saved run is an immutable snapshot, and every recruitment decision stays with a human reviewer.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-20.19%2B-339933?logo=node.js&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/tests-26%20API%20%C2%B7%209%20Chrome-brightgreen)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)

<p align="center">
  <img src="docs/screenshots/evidence-desktop.png" alt="Matching evidence workspace showing score contributions and requirement-to-passage evidence" width="920">
</p>

## Overview

Manual resume screening is difficult to reproduce. Keyword searches miss aliases, opaque rankings hide their reasoning, and historical hiring labels may reflect prior disadvantage. Candidate Lab makes a small matching rubric visible, records its evidence and versions, separates audit attributes from scoring, and leaves the final judgment with a reviewer.

The application is built for **accountable screening research**, not autonomous hiring. A matching score is an evidence summary, not a probability of success, and the project makes no claim of measured real-world accuracy or demographic fairness.

**Project status:** Stage-1 academic research prototype, version 0.2, verified locally on Windows on 14 November 2026.

## Features

### Transparent matching

- Explicit required and preferred skill rubrics; the job description provides context, not hidden scoring criteria.
- Exact weighted contributions: required evidence 60%, preferred evidence 15%, TF-IDF alignment 25%; without preferred skills the split becomes 75/0/25.
- Context labels v2 for **supported**, **learning**, **negated**, **uncertain** and **not found** mentions. Only supported evidence earns coverage.
- Requirement-to-passage evidence, source warnings and a score that is reproducible from visible terms.
- Immutable run snapshots that retain the profile version, rubric version, method identifier and evidence used.

### Jobs, applications and profiles

- Recruiter-managed jobs with required/preferred skills, edit previews and optimistic version checks.
- Publish and close jobs; closing stops new applications without deleting submitted records.
- Candidate-owned applications with an immutable submitted-profile snapshot per job.
- One active application per candidate and job; duplicate applications are rejected.
- Profile version history and conflict protection; correcting a profile does not rewrite an existing submission.
- PDF, DOCX and TXT extraction with a 2 MB limit and a mandatory preview/correction step.

### Human review and recruitment decisions

- Reversible internal review labels with mandatory, job-related reasons and an append-only review log.
- Recruitment decisions (under review, accept for next stage, reject) tracked separately from matching evidence.
- Server-generated candidate feedback based on the frozen matching snapshot and the selected decision.
- Recorded reviewer, timestamp and revision; stale decision revisions are rejected.
- No automatic hiring, rejection or email delivery.

### Audit and evaluation

- Auditor-only aggregate cohort report with a shared research cutoff, 95% Wilson intervals, small-group suppression (under five entries) and JSON export.
- Descriptive comparison only; no causal or real-world fairness claim.
- Labelled-dataset evaluation dashboard for NDCG@k, precision@k and recall@k.
- Dataset hash, vocabulary hash and semantic-model revision retained with each evaluation.
- Recruiters see per-query rankings; auditors receive aggregate metrics only.

### Security and roles

- Three server-enforced roles: **Recruiter**, **Auditor** and **Candidate**.
- Salted PBKDF2 password hashing and opaque HttpOnly session cookies with `SameSite=Strict`.
- Candidates register directly; recruiter and auditor accounts require a single-use, email-bound, expiring invitation issued by a local administrator.
- Cross-origin mutation requests are rejected unless the origin is explicitly allowed.
- Original uploads are parsed in memory and are not retained; confirmed extracted text is stored locally.

## How it works

```mermaid
flowchart TD
  U[Recruiter / Candidate / Auditor] --> UI[React and TypeScript interface]
  UI --> A[FastAPI: session and role enforcement]
  A --> P[PDF / DOCX / TXT parsing in memory]
  P --> C[Profile preview and correction]
  C --> D[(SQLite locally / PostgreSQL configuration)]
  A --> J[Explicit required and preferred job skills]
  D --> S[Skill passages + TF-IDF or local semantic alignment]
  J --> S
  S --> R[Immutable ranking and evidence snapshot]
  R --> H[Human review with mandatory reason]
  R --> F[Auditor-only aggregate report]
  G[(Separate synthetic audit attributes)] --> F
  F --> X[Selection rates / Wilson intervals / export]
```

The default method is `skill-tfidf-v2`. It combines explicit skill coverage with TF-IDF cosine alignment over recognized job-related passages. The optional `skill-semantic-v2` method replaces lexical alignment with a pinned local Sentence Transformers encoder. Vocabulary hashes, evidence-rule identifiers and model revisions travel with new runs, so older snapshots are never silently recalculated.

## Screenshots

| Model evaluation | Snapshot comparison |
| --- | --- |
| [<img src="docs/screenshots/model-evaluation-v2.png" alt="Model evaluation dashboard with NDCG, precision and recall metrics" width="420">](docs/screenshots/model-evaluation-v2.png) | [<img src="docs/screenshots/snapshot-comparison-v2.png" alt="Side-by-side comparison of two saved matching snapshots" width="420">](docs/screenshots/snapshot-comparison-v2.png) |

More interface captures are in [`docs/screenshots/`](docs/screenshots/).

## Tech stack

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Frontend | React 19, TypeScript, Vite 6 | Forms, evidence ledger, review workspace, audit controls |
| API | FastAPI, Pydantic 2 | Validation, session and role boundaries, endpoints |
| Persistence | SQLAlchemy 2, SQLite | Jobs, profiles, versions, snapshots, decisions, audit events |
| Optional deployment | PostgreSQL 17, psycopg 3, Docker Compose | Private containerized configuration |
| Extraction | pypdf, python-docx, dictionary aliases | Document reading and skill passage detection |
| Matching | scikit-learn TF-IDF and cosine similarity | Experimental text alignment plus explicit skill coverage |
| Semantic option | sentence-transformers `all-MiniLM-L6-v2` | Pinned local encoder; no remote inference |
| Audit | Python arithmetic | Synthetic-cohort rates, Wilson intervals, suppression |
| Verification | pytest, HTTPX TestClient, Playwright | API integration and real-browser journeys |

## Getting started

### Prerequisites

- Python **3.11+**
- Node.js **20.19+** (22 recommended)
- Google Chrome for the browser suite
- Optional: Docker with Compose and PostgreSQL for the container configuration

### Windows quick start

```powershell
# Run from the repository root
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd ci
npm.cmd run build
$env:DEMO_MODE = '1'
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. After the first setup, `./start.ps1` builds if needed and starts the loopback demo.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
npm run build
DEMO_MODE=1 uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

### Demo accounts

These accounts are created **only** when `DEMO_MODE=1` runs against an empty database. The seeded workspace contains 12 synthetic profiles, 3 jobs, one published job, one candidate application and two saved runs. It starts with no human reviews or recruitment decisions.

| Role | Email | Password |
| --- | --- | --- |
| Recruiter | `recruiter@demo.test` | `RecruiterDemo!2026` |
| Auditor | `auditor@demo.test` | `AuditorDemo!2026` |
| Candidate | `candidate@demo.test` | `CandidateDemo!2026` |

This is a private local research demo. Do not expose these credentials or bind the server to a public interface.

### Using the app

1. **Recruiter:** inspect a job rubric, run matching, open a candidate's evidence, read the contribution arithmetic and source passages, then save a reasoned review.
2. **Candidate:** add a profile from `examples/resume.txt` or another synthetic document, correct the extracted text, and apply to a published job.
3. **Auditor:** adjust the shared research cutoff, inspect aggregate rates and Wilson intervals, review the event log, and export the report as JSON.
4. **Model evaluation:** load the synthetic example, choose a top-k cutoff and methods, then compare NDCG, precision and recall with their provenance.

All seeded people, jobs, evaluations and cohort labels are synthetic. No action in the demo sends email, makes a job offer or rejects a candidate automatically.

### Optional local semantic model

The default TF-IDF path has no model dependency. To enable local semantic matching:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt
.\.venv\Scripts\python.exe scripts/download_semantic_model.py
.\start.ps1
```

`start.ps1` discovers the cached model under `models/all-MiniLM-L6-v2`. Alternatively set `SEMANTIC_MODEL_PATH` to a compatible local directory. Inference uses `local_files_only=True`; a load failure returns HTTP 503 rather than silently falling back to TF-IDF.

### Development mode

Run the API and Vite dev server in separate terminals:

```powershell
# Terminal 1 - API on http://127.0.0.1:8000
$env:DEMO_MODE = '1'
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# Terminal 2 - Vite on http://127.0.0.1:5173
npm.cmd run dev
```

Vite proxies `/api` to port 8000. Interactive API documentation is available at **http://127.0.0.1:8000/docs**.

## Testing and verification

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_backend.py tests/test_registration.py tests/test_advanced.py tests/test_naming.py -q
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
npm.cmd run test:e2e
```

The verified v0.2 baseline is **26 backend tests** and **9 Chrome journeys**, covering authentication and roles, job rubric editing, application ownership, evidence context rules, snapshot comparison, local semantic inference and evaluation access boundaries. API tests use a temporary database; browser tests start a production build on port **8001** with a disposable database, leaving the live workspace on port 8000 untouched.

See [`docs/VERIFICATION.md`](docs/VERIFICATION.md) for the full record and the checks that were not exercised.

## Docker and PostgreSQL

Put a strong `POSTGRES_PASSWORD` in `.env`, then run:

```bash
docker compose up --build
```

Compose binds the demo to `127.0.0.1:8000` and stores PostgreSQL data in a named volume. For a local Python run with PostgreSQL, set:

```text
DATABASE_URL=postgresql+psycopg://user:password@host:5432/candidate_lab
```

Tables are created on startup. Versioned Alembic migrations are a next-release requirement before evolving a populated deployment. Docker/PostgreSQL support is configuration, not a verified production deployment.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEMO_MODE` | unset | `1` seeds the synthetic workspace on an empty database |
| `DATABASE_URL` | `sqlite:///./data/candidate-lab.db` | SQLAlchemy database URL |
| `COOKIE_SECURE` | `0` | Set to `1` behind HTTPS |
| `ALLOWED_ORIGINS` | localhost origins | Explicit cross-origin allowlist |
| `SEMANTIC_MODEL_PATH` | empty | Local directory for optional semantic inference |

## Documentation and reports

- [Documentation index](docs/README.md)
- [Product contract](docs/PRODUCT.md)
- [Design system](docs/DESIGN.md)
- [UX contract](docs/UX-CONTRACT.md)
- [v0.2 upgrade guide](docs/UPGRADE-v0.2.md)
- [Evaluation guide and model card](docs/EVALUATION.md)
- [Verification record](docs/VERIFICATION.md)
- [Stage-1 report (Standard, V2)](docs/report/Candidate_Lab_Project_Report_Standard_V2.pdf)
- [Stage-1 report (Detailed, V2)](docs/report/Candidate_Lab_Project_Report_Detailed_V2.pdf)
- [Interface screenshots](docs/screenshots/)

## Repository layout

```text
backend/     FastAPI application, authentication, matching, audit and invitation CLI
src/         React and TypeScript interface plus shared components
tests/       pytest API suite and Playwright browser journeys
docs/        Product, design, UX, evaluation and verification records
docs/report/ Stage-1 reports, source format and reusable figures
examples/    Synthetic resume example for the demo
scripts/     Packaging, report generation, screenshot capture and model download helpers
public/      Static assets served by the built frontend
```

## Research scope and limitations

- No real labelled applicant dataset or independently annotated training corpus was supplied.
- No trained hiring classifier, classification error-rate metric, causal fairness analysis or mitigation is claimed.
- Matching indices are rubric summaries, **not probabilities** and not SHAP values.
- Seeded cohort labels are arbitrary synthetic A/B labels, never inferred demographics.
- Small groups are suppressed, and Wilson intervals express uncertainty rather than certify fairness.
- Dictionary extraction and context rules can miss negation, distant context, aliases and exaggeration; human review is required.
- Document parsing has size and page limits but is not a malware sandbox. Use synthetic or consented files locally.
- This is a single-workspace local research release: no multi-tenant isolation, email delivery, OCR, background queue or production identity provider is implemented.
- Docker/PostgreSQL, large-load performance and adversarial parser behavior were not exercised in the verified baseline.

## Roadmap

- Build a consented, independently annotated resume-job relevance dataset with inter-annotator agreement measurements.
- Evaluate held-out ranking quality (NDCG@k, recall@k and confidence intervals) against lexical, semantic and supervised baselines.
- Add versioned database migrations, retention/deletion workflows, isolated document parsing and production identity provisioning.
- Measure approved cohort gaps only after data governance and consent are in place; keep human oversight throughout.
- Harden packaging and deployment for environments beyond the verified local workspace.

## Contributors

Candidate Lab was developed for the Stage-1 project by:

| Name | Roll number |
| --- | --- |
| Deekshith Alle | 23911A6672 |
| Siri vennala Kammari | 23911A6698 |
| Rizwana Mohammad | 23911A66A9 |
| Harsha vardhan Dyavanapelli | 24915A6608 |

Stage-1 report authoring and verification, bug fixing, issue triage and release packaging: **Harsha vardhan Dyavanapelli**. See [`CONTRIBUTORS.md`](CONTRIBUTORS.md) for the contribution record.

## Citation

Citation metadata is in [`CITATION.cff`](CITATION.cff). If you reference this project, please cite the Stage-1 report:

```bibtex
@misc{candidate_lab_2026,
  title  = {Candidate Lab: Fair and Explainable Machine Learning for Automated Candidate Selection and Skill Matching},
  author = {Alle, Deekshith and Kammari, Siri vennala and Mohammad, Rizwana and Dyavanapelli, Harsha vardhan},
  year   = {2026},
  url    = {https://github.com/deekshithalle/Candidate_Lab}
}
```

## Acknowledgements

The optional semantic path uses the general-purpose [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) encoder (Apache-2.0). All seeded profiles, jobs, evaluations and cohort labels are synthetic fixtures created for demonstration and testing.

## License

No open-source license is included in this repository. The source, reports and documentation are academic project material; contact the authors before reuse or redistribution.
