# Verification record

Version 0.2 verified locally on Windows, 14 November 2026. Synthetic relevance metrics demonstrate evaluation functionality; no real-applicant predictive quality or demographic fairness result is claimed.

| Check                               | Result                                                      |
| ----------------------------------- | ----------------------------------------------------------- |
| API/model integration suite         | 26 tests passed, including actual cached semantic inference |
| Production-build Chrome journeys    | 9 tests passed                                              |
| Demo seed counts                    | 12 profiles, 3 jobs, 1 application, 2 runs, 0 reviews       |
| TypeScript type checking            | Passed                                                      |
| Production shell assets             | `/` and `/favicon.svg` served with 200; SPA shell loads     |
| Vite production build               | Passed                                                      |
| ESLint                              | Passed with no warnings                                     |
| Prettier source formatting          | Passed                                                      |
| DESIGN.md validator                 | Earlier run: 0 errors; 7 orphan-token warnings              |
| Desktop and 390px audit screenshots | Rendered and visually inspected; no page overflow at 390px  |

## Integration coverage

Version 0.2 adds tests for job creation, retrieval and optimistic rubric editing, publish/close behavior, application ownership, duplicate applications, immutable submitted profiles, the retired withdrawal path (410), matching only active applicants, same-job snapshot comparison, evidence context states, dataset validation, independently calculated ranking metrics, aggregate-only auditor access and explicit semantic load failures. Actual all-MiniLM-L6-v2 inference was exercised offline with a pinned cached model revision.
Presentation update verified on 14 November 2026: recruiter overview totals match database records, counts update after profile creation, and candidate/auditor access to those totals is rejected. Professional sign-in and recruiter overview were visually checked; the new cards fit at 390px width. Academic/prototype branding was removed while sample-data and scoring limitations remain visible.
Registration coverage includes all three roles, normalized/duplicate email, password confirmation and strength, stored password hashing, candidate ownership, invalid/expired/used invitations and incorrect invitation email/role. No automatic session is issued by registration.
Unauthenticated and incorrect-password responses, logout, candidate ownership, auditor/recruiter role separation, skill normalization and unsupported skill rejection, required/preferred overlap rejection, profile creation and version conflicts, immutable historical evidence, score arithmetic, mandatory reasoned human review, audit small-group suppression and confidence intervals, valid TXT/DOCX/PDF parsing, malformed/unsupported/oversized files, and rejected mutation origins.

## Browser coverage

Version 0.2 adds a complete job-edit/publication/application/correction/comparison journey and an actual TF-IDF-versus-local-semantic evaluation/export journey. Final full run: 9 passed in Chrome. Evaluation results are hidden while a new run is processing to avoid showing an old report as the new result. The current sidebar and evaluation layout were visually inspected. Model evaluation passed a 390px page-overflow check.
New candidate, recruiter and auditor accounts each register, correct a mismatched password, return to login with a cleared password, and sign in to their role-specific workspace. Privileged invitations are generated with the local administrator CLI against the isolated browser-test database.
Recruiter creates and edits a job rubric, uploads a text resume, edits the profile, publishes the job, applies as a candidate, runs matching, inspects evidence, saves a review and records a recruitment decision. Auditor changes the common threshold with the keyboard, exports JSON, uses the event log, and checks the narrow layout. Invalid credentials and invalid forms keep entered values. The unsaved-draft modal supports Escape and intercepts browser-back navigation. Candidate sees the owned seed profile and restricted views show no ranking.

The browser suite starts its own production-build server on port 8001 with a disposable SQLite database and an explicit allowed origin. API tests also use an isolated temporary database. The live workspace on port 8000 is preserved.

## Non-blocking warnings

The earlier TestClient HTTPX deprecation warning is resolved by the currently installed dependencies. [DESIGN.md](DESIGN.md)'s validator previously reported seven custom color tokens as unreferenced by its component YAML; these tokens are implemented in src/styles.css. Typecheck, ESLint, build and browser journeys cover the current UI. No complete accessibility or security certification is claimed.

## Not exercised

Docker/PostgreSQL deployment, large-load performance, representative real applicant evaluation, adversarial parser sandboxing and production identity/retention workflows. The local pretrained semantic model is now installed and tested; no recruitment fine-tuning was performed. Context rules improve selected negation/learning cases but do not reliably understand every linguistic construction; human review remains required.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_backend.py tests/test_registration.py tests/test_advanced.py tests/test_naming.py -q
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
npm.cmd run test:e2e
```

The checked-in Playwright configuration uses an installed Google Chrome. For a machine without Chrome, install a Playwright Chromium browser and remove the channel override in playwright.config.ts.

## Readable naming update

Known generated timestamp titles and profile labels were migrated to readable professional names after a database backup. User-entered names are preserved. Current names appear consistently in applications, saved matching results and comparisons; original evidence, scores and stored historical snapshots remain unchanged. Naming tests cover this separation.

## Candidate-controlled profiles

Candidates create and update their own profiles. Recruiters can browse and inspect resume evidence and extracted skills but cannot create or edit profiles. The API enforces this restriction independently of the interface. Existing profiles and historical matching evidence are retained.

## Recruitment decisions update

Recruiter → Applications → Review application → choose Under review, Accept for next stage, or Reject application → review the server-generated candidate feedback in the decision preview → Save recruitment decision. Accepting progresses the application; it is not a job offer. Candidates see status and dated feedback in Applications. Each decision records the recruiter, time and revision; stale revisions are rejected. Decisions do not overwrite submitted resume evidence or matching scores.

Candidate withdrawal and resubmission are superseded by this workflow: the interface no longer offers withdrawal, its old API returns 410, and duplicate applications are rejected. Previously withdrawn records remain historical records. Rejected applications are excluded from future matching runs; submitted, under-review and accepted applications remain eligible. Older saved matching runs retain their original results.

Recruiter decisions remain separate from matching-evidence review notes. No automatic recruitment decision or email delivery is performed. Status updates are visible inside the application. Existing data is retained; startup adds the recruitment_decisions table without changing existing table columns.

## Application review with matching evidence

Applications → Review application loads the exact submitted resume and a saved matching snapshot for that application, submitted version and current job-requirements version. The review displays score, method, date and skill evidence. Without a matching snapshot, a decision cannot be saved; open job matching first. Scores are evidence summaries, not probabilities of recruitment success.

Feedback is now generated by the server from that saved evidence and the recruiter-selected status. The manual feedback field is removed. Candidates receive the score, supported skills and required skills needing clearer evidence, with context limitations and the recruiter decision. No email is sent. A new additive decision_evidence table links each new decision to its frozen matching snapshot; later matching/profile changes do not rewrite existing feedback. Manual feedback from earlier releases remains historical. Recruiters retain control of decisions; feedback generation does not auto-select or reject people. This supersedes earlier instructions to type candidate feedback.
