# Candidate Lab 0.2 - applications and measured matching

Released 4 November 2026; documentation refreshed 14 November 2026. This release adds a complete job-specific workflow while preserving existing profiles and legacy matching snapshots. New tables are created on startup; existing table columns are unchanged, and no automatic destructive migration is performed.

## Try the new workflow

1. **Recruiter -> Job details:** create the required/preferred skill rubric.
2. **Recruiter -> Publish jobs:** publish it. Closing a job stops new applications but preserves submitted records.
3. **Candidate -> My profiles:** save accurate project/work evidence. Dictionary-only skill lists can be marked uncertain; learning and negated claims receive separate labels.
4. **Candidate -> Job opportunities:** choose a profile, click Check skill evidence, inspect the gaps, then Apply with selected profile.
5. **Recruiter -> Applications:** see submitted profile versions and active status; historical withdrawn records remain visible. Under Publish jobs, choose TF-IDF or local semantic and click Match applicants.
6. **Matching evidence:** inspect context labels and exact score contributions. New runs contain only active applicants, using their submitted evidence. Legacy runs are explicitly identified.
7. Submitted evidence is immutable. Correcting a profile does not change an application that was already submitted, and duplicate applications for the same job are rejected. Withdrawal/resubmission is retired: the old endpoint returns 410, while previously withdrawn records remain as history. Use saved snapshot comparison to inspect how later profile edits affect new runs.
8. Create another run for the same job, then open Compare snapshots. Inspect score deltas, profile versions, membership and changed requirements. A delta does not establish its cause; cohort, rubric and method also affect scores.

One candidate account can have one active application per job. Profile choice is restricted to owned profiles; application versions retain the exact submitted snapshot. This is still one shared local workspace, not a multi-tenant recruitment service. No application or review action automatically sends email or hires/rejects anyone.

## Evidence rules v2

The rule engine labels a mention **supported**, **learning**, **negated**, **uncertain**, or **not found**. It checks nearby language and contrasting clauses, and flags conflicting positive/negative statements for review. Only supported mentions count toward required/preferred coverage. Text alignment uses supported clauses; an entirely unsupported document receives zero alignment. These are conservative rules, not a verified competence classifier. Complex negation, distant context, vocabulary omissions and exaggeration can still cause errors.

New method identifiers are skill-tfidf-v2 and skill-semantic-v2. Older snapshots are not recalculated. Vocabulary hashes and evidence-rule identifiers are stored with new runs. Model references include the pinned repository revision when supplied by the download helper.

## Semantic setup

The current laptop has the optional dependencies and cached pretrained **sentence-transformers/all-MiniLM-L6-v2** installed. It is a general-purpose sentence encoder, not fine-tuned on hiring data. The model revision is recorded in models/all-MiniLM-L6-v2/model-reference.json. Model information: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 (Apache-2.0).

On another machine:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt
.\.venv\Scripts\python.exe scripts/download_semantic_model.py
.\start.ps1
```

The helper downloads safetensors/config/tokenizer files from the official repository at a pinned revision. It sends no resume text. start.ps1 discovers the cached model and enables offline inference. Set SEMANTIC_MODEL_PATH explicitly to use another compatible local model. No silent fallback occurs if semantic matching is requested but cannot load. The source ZIP excludes model weights and dependency environments; download them separately. Docker users must supply their own model mount and semantic dependencies; the default container remains TF-IDF only.

## Evaluation dashboard

Recruiter -> Model evaluation -> Load synthetic example -> choose Top-k and Methods to compare -> Run evaluation. You can replace the JSON with consented, pseudonymous labelled examples using the same schema. Labels are 0 (not relevant), 1 (partially relevant), or 2 (strongly relevant). Every query needs at least one relevant example. No training or fine-tuning is performed by this screen.

The dashboard computes NDCG@k using graded relevance, plus precision/recall with grades 1 and 2 considered relevant. Effective k is min(requested k, cohort size); query metrics are averaged equally. Reports retain dataset provenance/hash and method/model configuration, show per-query rankings to recruiters, and export JSON. Auditors receive aggregate metrics only, with individual ranked examples removed.

The included dataset has two fictional job queries and eight short profiles with illustrative labels. On the local smoke test at k=3, both methods produced NDCG=1.0000, recall=1.0000 and precision=0.6667. Equal results on this tiny fixture do not show a semantic improvement or establish real-world accuracy/fairness. Use independently reviewed, held-out data for a research claim. The tool cannot prove annotation quality, consent or train/test separation. Long semantic inputs are truncated by the configured encoder.

## New endpoints

| Endpoint                                          | Purpose                                                              |
| ------------------------------------------------- | -------------------------------------------------------------------- |
| GET /api/jobs/{id}                                | Read a job rubric and its current version; recruiter/auditor         |
| PUT /api/jobs/{id}                                | Edit a job rubric with optimistic version checking; recruiter        |
| GET /api/opportunities                            | Published jobs for candidates; all publication states for recruiters |
| PUT /api/jobs/{id}/publication                    | Publish or close a job; recruiter                                    |
| POST /api/jobs/{id}/applications                  | Submit an owned profile snapshot; candidate                          |
| POST /api/applications/{id}/withdraw              | Retired compatibility endpoint; returns 410                          |
| GET /api/applications                             | Own history or recruiter workspace history                           |
| GET /api/jobs/{id}/skill-gap?candidate_id=...     | Current owned-profile evidence versus published rubric               |
| POST /api/jobs/{id}/runs?method=tfidf or semantic | Match active submitted applicants                                    |
| GET /api/comparisons?left=...&right=...           | Compare two same-job snapshots; recruiter                            |
| GET /api/evaluation/template and /status          | Dataset example and local-model configuration                        |
| POST /api/evaluations                             | Save measured evaluation; recruiter                                  |
| GET /api/evaluations                              | Saved reports; auditor receives aggregates only                      |

## Verification and documentation

The expanded test suite covers applications, ownership, publication, job editing with version conflicts, immutable submissions, contextual evidence, snapshot deltas, metric calculations, evaluation role restrictions and actual local semantic inference. See VERIFICATION.md for completed checks. Older generated PDFs describe the earlier release and are retained as historical documents; this guide records the new scope.

Still outside this release: training a recruitment model, real demographic fairness validation, email verification/recovery, OCR, tenant isolation, durable workers and public cloud deployment. PostgreSQL/Docker production verification and comprehensive schema migrations remain follow-up work.

## Clear names throughout the workspace

Job details contains readable job titles; versions are shown separately. Candidate profiles use descriptive professional names, with a clearer Profile name field. Known generated timestamp names were renamed after a local database backup. Saved results and applications display current names without rewriting historical evidence or scores. Browser tests now run on a separate disposable database at port 8001.

## Candidate-controlled profiles

Candidates create and update their own profiles. Recruiters can browse and inspect resume evidence and extracted skills but cannot create or edit profiles. The API enforces this restriction independently of the interface. Existing profiles and historical matching evidence are retained.

## Recruitment decisions update

Recruiter → Applications → Review application → choose Under review, Accept for next stage, or Reject application → review the server-generated candidate feedback in the decision preview → Save recruitment decision. Accepting progresses the application; it is not a job offer. Candidates see status and dated feedback in Applications. Each decision records the recruiter, time and revision; stale revisions are rejected. Decisions do not overwrite submitted resume evidence or matching scores.

Candidate withdrawal and resubmission are superseded by this workflow: the interface no longer offers withdrawal, its old API returns 410, and duplicate applications are rejected. Previously withdrawn records remain historical records. Rejected applications are excluded from future matching runs; submitted, under-review and accepted applications remain eligible. Older saved matching runs retain their original results.

Recruiter decisions remain separate from matching-evidence review notes. No automatic recruitment decision or email delivery is performed. Status updates are visible inside the application. Existing data is retained; startup adds the recruitment_decisions table without changing existing table columns.

## Application review with matching evidence

Applications → Review application loads the exact submitted resume and a saved matching snapshot for that application, submitted version and current job-requirements version. The review displays score, method, date and skill evidence. Without a matching snapshot, a decision cannot be saved; open job matching first. Scores are evidence summaries, not probabilities of recruitment success.

Feedback is now generated by the server from that saved evidence and the recruiter-selected status. The manual feedback field is removed. Candidates receive the score, supported skills and required skills needing clearer evidence, with context limitations and the recruiter decision. No email is sent. A new additive decision_evidence table links each new decision to its frozen matching snapshot; later matching/profile changes do not rewrite existing feedback. Manual feedback from earlier releases remains historical. Recruiters retain control of decisions; feedback generation does not auto-select or reject people. This supersedes earlier instructions to type candidate feedback.
