"""Content blocks for the Standard and Detailed Candidate Lab reports.

The blocks are data-only so that layout, pagination and image sizing can be
changed in one builder without rewriting the report text. The Standard edition
is deliberately concise (one page per chapter); the Detailed edition adds
tables, discussion and the complete set of design diagrams.
"""
from __future__ import annotations

TITLE = (
    "CANDIDATE LAB: AN EXPLAINABLE AL FRAMEWORK FOR FAIR AND OBJECTIVE "
    "TALENT ACQUISITION"
)
SHORT_TITLE = "Candidate Lab"
STUDENTS = [
    ("Deekshith Alle", "23911A6672"),
    ("Sirivennala Kammari", "23911A6698"),
    ("Rizwana Mohammad", "23911A66A9"),
    ("Harshavardhan Dyavanapelli", "24915A6608"),
]
GUIDE = "Mrs. Y. Uma Mythraye"
GUIDE_DESIGNATION = "Assistant Professor"
HOD = "Dr. N. Anusha"
HOD_DESIGNATION = "Associate Professor"
PRINCIPAL = "Dr. A. Srujana"
COLLEGE = "VIDYA JYOTHI INSTITUTE OF TECHNOLOGY"
DEPARTMENT = "COMPUTER SCIENCE & ENGINEERING (AI&ML)"
YEAR = "2025 - 2026"

ACKNOWLEDGEMENT = [
    "Any endeavour in the field of development is a person's intensive activity. A successful "
    "project is a fruitful culmination of efforts by many people, some directly involved and "
    "some others who have quietly encouraged and supported.",
    "We express our profound gratitude to **" + GUIDE + "**, **" + GUIDE_DESIGNATION + "** of "
    "CSE (AI&ML), for her continuous encouragement, patient guidance and valuable suggestions "
    "throughout this project.",
    "We thank **" + HOD + "**, **Head of the Department**, Department of CSE (AI&ML), for "
    "guiding us through the project and our academic work, and **" + PRINCIPAL + "**, Principal, "
    "for the support that made this work possible.",
    "We are grateful to the faculty members and technical staff of the Department of CSE (AI&ML) "
    "for their assistance during reviews, demonstrations and verification activities, and to the "
    "college management for providing the infrastructure and laboratory facilities used in this "
    "project.",
    "Last but not least, we thank our family members and friends, who are the backbone of our "
    "efforts and who provide support in every possible way.",
]

ABSTRACT = [
    "Candidate screening requires a reviewer to connect the skills described in a resume with the "
    "skills required by a job. Resumes differ in structure, vocabulary and detail; job descriptions "
    "mix essential requirements with desirable qualifications; and a score without visible evidence "
    "is difficult to interpret, reproduce or challenge. Candidate Lab is a local, role-aware "
    "decision-support application that addresses this inspectability problem through document "
    "extraction, explicit skill rubrics, evidence-linked matching, immutable snapshots, candidate "
    "applications, recruiter decisions and a restricted aggregate audit view.",
    "Candidate profiles are parsed from text PDF, DOCX or TXT files, or pasted text, and are "
    "previewed and corrected before saving. A context-aware dictionary identifies supported, "
    "learning, uncertain and negated skill mentions and retains the supporting passage. Matching "
    "combines required-skill coverage (60%), preferred-skill coverage (15%) and lexical alignment "
    "(25%), or 75% required coverage when no preferred skills exist. Every component is shown as an "
    "exact arithmetic contribution. A pinned local Sentence Transformers model can replace lexical "
    "alignment when explicitly configured; the default method is skill-tfidf-v2 with "
    "context-rules-v2.",
    "The prototype separates candidate, recruiter and auditor access at the server boundary. "
    "Candidates manage owned profiles and applications; recruiters publish jobs, inspect evidence "
    "and record reasoned decisions; auditors see aggregate cohort rates, Wilson intervals and "
    "activity records without receiving resume text or ranking snapshots. Verification covers 26 "
    "backend tests and 9 production-build browser journeys, together with type checking, linting "
    "and a production build. The project does not claim a trained hiring predictor, measured "
    "hiring accuracy or real-world fairness; its contribution is an inspectable baseline and an "
    "honest evaluation frame.",
]

REFERENCES = [
    "[1] scikit-learn developers, \"Text feature extraction,\" scikit-learn documentation. "
    "[Online]. Available: https://scikit-learn.org/stable/modules/feature_extraction.html",
    "[2] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using Siamese "
    "BERT-networks,\" in Proceedings of EMNLP-IJCNLP, 2019, pp. 3982-3992.",
    "[3] pypdf developers, \"Extract text from a PDF,\" pypdf documentation. [Online]. "
    "Available: https://pypdf.readthedocs.io/en/stable/user/extract-text.html",
    "[4] python-docx developers, \"python-docx documentation.\" [Online]. Available: "
    "https://python-docx.readthedocs.io/en/latest/",
    "[5] S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" "
    "in Advances in Neural Information Processing Systems, 2017, pp. 4765-4774.",
    "[6] M. Hardt, E. Price, and N. Srebro, \"Equality of opportunity in supervised learning,\" "
    "in Advances in Neural Information Processing Systems, 2016, pp. 3315-3323.",
    "[7] S. Ramirez, \"FastAPI documentation.\" [Online]. Available: https://fastapi.tiangolo.com/",
    "[8] Meta Platforms, \"React documentation.\" [Online]. Available: https://react.dev/",
    "[9] M. Bayer, \"SQLAlchemy documentation.\" [Online]. Available: "
    "https://docs.sqlalchemy.org/",
    "[10] E. B. Wilson, \"Probable inference, the law of succession, and statistical inference,\" "
    "Journal of the American Statistical Association, vol. 22, no. 158, pp. 209-212, 1927.",
]

PROOF_TEXT = (
    "Publication is not claimed at the time of this Stage-1 submission. No paper from this work "
    "has been communicated, accepted or published. This page is intentionally reserved for an "
    "authentic acceptance letter, conference or journal first page, or DOI record once a "
    "publication exists. A placeholder is used instead of a fabricated certificate."
)


def _objectives_table(short: bool = True) -> tuple:
    if short:
        rows = [
            ["O1 Evidence preparation", "PDF, DOCX, TXT or pasted text produces an editable preview."],
            ["O2 Transparent comparison", "Coverage and alignment shown with exact point contributions."],
            ["O3 Traceability", "Stale edits conflict; saved runs retain original evidence."],
            ["O4 Controlled access", "Server rejects unauthenticated, cross-owner and cross-role requests."],
            ["O5 Auditable comparison", "Aggregate report with sample sizes, Wilson intervals and suppression."],
            ["O6 Verification", "Backend and browser suites pass; claims stay bounded."],
        ]
    else:
        rows = [
            [
                "O1 Evidence preparation",
                "Supported PDF, DOCX, TXT or pasted text produces an editable preview; invalid "
                "files return a clear validation error.",
            ],
            [
                "O2 Transparent comparison",
                "Required and preferred coverage and alignment are displayed with exact point "
                "contributions and source passages.",
            ],
            [
                "O3 Traceability",
                "A stale update returns a conflict; a saved run retains its original profile "
                "version and evidence after correction.",
            ],
            [
                "O4 Controlled access",
                "Unauthenticated, cross-owner, cross-role and invalid-invitation requests are "
                "rejected on the server.",
            ],
            [
                "O5 Auditable comparison",
                "Auditor-only aggregate report with sample sizes, Wilson intervals, small-group "
                "suppression and JSON export.",
            ],
            [
                "O6 Verification",
                "Backend and browser suites pass; the report separates functional evidence from "
                "model-quality and fairness claims.",
            ],
        ]
    return (
        "table",
        "Table 1.1: Objectives mapped to verification evidence",
        ["Objective", "Success indicator"],
        rows,
        [4.2, 11.4],
    )


def _approach_table() -> tuple:
    return (
        "table",
        "Table 2.1: Existing approaches and their limitations",
        ["Approach", "Strength", "Limitation for this project"],
        [
            ["Manual review", "Uses context and progression", "Inconsistent, slow, hard to reproduce"],
            ["Keyword / Boolean", "Fast, deterministic and simple", "Misses aliases, negation and repetition"],
            ["TF-IDF retrieval", "Local, reproducible lexical baseline", "Bag-of-words; misses paraphrase and context"],
            ["Semantic embeddings", "Reduces vocabulary mismatch", "Dependencies; diffuse explanation"],
            ["Supervised ranking", "Can model complex relevance", "Needs labels; may reproduce bias"],
        ],
        [3.6, 5.4, 6.6],
    )


def _gap_table() -> tuple:
    return (
        "table",
        "Table 2.2: Identified gaps mapped to design responses",
        ["Gap", "Design response"],
        [
            ["Evidence is lost when a score is shown alone", "Every requirement keeps its supporting passage and status"],
            ["Corrections rewrite history", "Append-only profile, application and run versions"],
            ["Roles are hidden in the interface", "Server-side role and ownership dependencies"],
            ["Audit attributes leak into ranking", "Separate audit context; matcher sees rubric and snapshot only"],
            ["Fairness cannot be inferred from a score", "Bound claims, uncertainty intervals and suppression"],
        ],
        [7.4, 8.2],
    )


def _data_sources_table() -> tuple:
    return (
        "table",
        "Table 3.1: Data sources and their role",
        ["Source", "Content", "Role in the project"],
        [
            ["Candidate document", "PDF, DOCX, TXT or pasted text", "Evidence for the profile and matching snapshot"],
            ["Job description", "Title, description, required and preferred skills", "Rubric used for scoring"],
            ["Demo workspace", "Twelve fictional profiles, three jobs, applications and runs", "Reproducible demonstration"],
            ["Evaluation fixture", "Queries, fictional profiles and relevance grades", "Metric smoke test, not a benchmark"],
        ],
        [3.8, 6.0, 5.8],
    )


def _preprocess_table() -> tuple:
    return (
        "table",
        "Table 3.1: Preprocessing stages and outputs",
        ["Stage", "Operation", "Output"],
        [
            ["Validation", "Type, size, page and archive limits", "Accepted file or clear error"],
            ["Extraction", "PDF, DOCX and TXT text extraction", "Editable draft"],
            ["Correction", "Human review of text and warnings", "Confirmed profile text"],
            ["Normalisation", "Whitespace, sentences, clauses, aliases", "Canonical skill mentions"],
            ["Context rules", "Supported, learning, uncertain or negated", "Evidence with status and passage"],
            ["Snapshot", "Versioned profile and application", "Immutable matching input"],
        ],
        [3.2, 6.6, 5.8],
    )


def _layers_table() -> tuple:
    return (
        "table",
        "Table 3.3: Architecture layers and responsibilities",
        ["Layer", "Responsibility"],
        [
            ["Presentation", "React SPA, role-aware navigation, forms and evidence views"],
            ["API boundary", "Sessions, roles, validation, origin checks, size limits, static assets"],
            ["Domain services", "Authentication, parsing, jobs, applications, decisions, matching, audit"],
            ["Data and model", "SQLAlchemy persistence, SQLite or PostgreSQL, optional local encoder"],
        ],
        [3.4, 12.2],
    )


def _score_table() -> tuple:
    return (
        "table",
        "Table 3.4: Matching index components",
        ["Component", "Symbol", "Weight", "Meaning"],
        [
            ["Required coverage", "R", "0.60 (0.75 if no preferred)", "Required skills with supported evidence"],
            ["Preferred coverage", "P", "0.15 (0.00 if no preferred)", "Preferred skills with supported evidence"],
            ["Lexical alignment", "L", "0.25", "TF-IDF cosine similarity to skill-bearing text"],
        ],
        [4.3, 1.4, 4.6, 5.3],
    )


def _stack_table() -> tuple:
    return (
        "table",
        "Table 4.1: Verified development stack",
        ["Layer", "Technology used in the verified build"],
        [
            ["Backend", "Python 3.11.9, FastAPI 0.162.7, Pydantic 2.14.3"],
            ["Data and matching", "SQLAlchemy 2.1.8, SQLite or PostgreSQL, scikit-learn 1.9.1"],
            ["Frontend", "React 19, TypeScript 5.7, Vite 6"],
            ["Testing", "pytest, Playwright 1.56 and installed Google Chrome"],
        ],
        [4.0, 11.6],
    )


def _modules_table() -> tuple:
    return (
        "table",
        "Table 4.2: Backend modules and responsibilities",
        ["Module", "Responsibility"],
        [
            ["backend/app.py", "Core models, authentication, invitations, jobs, profiles, parsing, runs, reviews, audit"],
            ["backend/advanced.py", "Publications, applications, decisions, evidence, comparisons, evaluation"],
            ["backend/matching.py", "Skill vocabulary, context rules, scoring, Wilson intervals, aggregate audit"],
            ["backend/invite.py", "Local administrator command for expiring, email-bound invitations"],
        ],
        [3.8, 11.8],
    )


def _verification_table(caption: str = "Table 4.2: Verification summary") -> tuple:
    return (
        "table",
        caption,
        ["Check", "Result", "Coverage"],
        [
            ["Backend and API suite", "26 passed", "Auth, ownership, roles, parsing, versions, runs, reviews, audit, evaluation"],
            ["Production-build browser suite", "9 passed", "Three-role registration, job edit, profile, matching, decisions, audit, mobile"],
            ["Static checks", "Passed", "TypeScript, ESLint, Prettier and Vite production build"],
        ],
        [4.2, 2.2, 9.2],
    )


def _tradeoffs_table() -> tuple:
    return (
        "table",
        "Table 4.4: Design trade-offs and mitigations",
        ["Decision", "Trade-off", "Mitigation"],
        [
            ["Lexical default", "Misses paraphrase and vocabulary mismatch", "Optional local semantic method; evidence shown for every match"],
            ["Precision-first evidence", "Equivalent experience may be understated", "Not-found wording; editable profile and alias expansion"],
            ["Immutable versions", "Higher storage and query cost", "Bounded prototype data; retention policy in future scope"],
            ["Local accounts", "No email recovery or tenant isolation", "Single-use invitations; server-side role checks"],
            ["Synthetic audit", "Cannot establish real-world fairness", "Wilson intervals, small-group suppression, stated limits"],
        ],
        [4.0, 5.2, 6.68],
    )


def _standard_blocks() -> list:
    return [
        ("chapter", 1, "INTRODUCTION"),
        ("section", "1.1 Introduction"),
        (
            "body",
            "Recruitment requires a reviewer to judge whether documented experience is relevant "
            "to a job. Resumes differ in structure, vocabulary and detail, while job descriptions "
            "mix essential requirements with desirable skills. A useful screening system must "
            "preserve the connection between a requirement, the evidence found in a document and "
            "the judgment made by a reviewer.",
        ),
        (
            "body",
            "Keyword filters are fast and deterministic but miss aliases and negations. Learned "
            "rankers capture subtler relationships but depend on labelled data and are difficult to "
            "audit. Candidate Lab is a local, role-aware decision-support application. Candidates "
            "correct profiles and apply to published jobs; recruiters define explicit rubrics, "
            "inspect evidence-linked rankings and record reasoned decisions; auditors see aggregate "
            "rates and an append-only event log.",
        ),
        ("section", "1.2 Problem Statement"),
        (
            "body",
            "Manual shortlisting is flexible but difficult to reproduce. Reviewers apply "
            "different thresholds, corrections overwrite earlier documents, and candidates may "
            "never learn that relevant experience was ignored. Automated tools add "
            "vocabulary-sensitive filters, historical bias in labels and opaque similarity. The "
            "task is to turn heterogeneous documents and explicit requirements into a traceable "
            "comparison while separating ranking from human decision and stating which fairness "
            "questions the data cannot answer.",
        ),
        ("section", "1.3 Objectives"),
        (
            "body",
            "Table 1.1 maps each objective to an observable indicator.",
        ),
        _objectives_table(short=True),
        ("chapter", 2, "LITERATURE SURVEY"),
        ("section", "2.1 Existing System"),
        (
            "body",
            "Existing practice spans manual review, keyword or Boolean search, lexical retrieval, "
            "semantic embeddings, supervised ranking and post-hoc explanation. These approaches "
            "are complementary, but each addresses only part of the inspectability problem. Table "
            "2.1 compares their strengths and limitations for this project.",
        ),
        (
            "body",
            "Keyword filters miss aliases and negation; TF-IDF is reproducible but bag-of-words "
            "[1]; Sentence-BERT reduces the vocabulary gap at the cost of dependencies [2]; and PDF "
            "or DOCX extraction can reorder or omit text [3,4]. Supervised rankers inherit the "
            "label-generation process and can reproduce historical disadvantage. SHAP explains a "
            "model's prediction rather than validating its data [5], while fairness criteria such "
            "as equalized odds require qualification labels [6]. Wilson intervals quantify "
            "uncertainty [10] but do not certify fairness. The gap is an integrated workflow that "
            "keeps job criteria, evidence, versions, roles, human decisions and audit limits visible "
            "in one application.",
        ),
        _approach_table(),
        ("section", "2.2 Proposed System"),
        (
            "body",
            "Candidate Lab proposes evidence-led decision support rather than autonomous ranking. "
            "The unit of comparison is a saved application snapshot: a job rubric, a confirmed "
            "profile version and the evidence extracted from that version. The recruiter sees a "
            "matching index and the passages that produced it; the final decision remains a "
            "separate, attributed human action. Six principles guide the design: explicit required "
            "and preferred skills, evidence before score, append-only history, server-enforced "
            "roles, audit attributes isolated from the ranking path, and bounded claims. OCR, "
            "production identity, multi-tenancy and a representative labelled dataset remain "
            "outside this Stage-1 prototype.",
        ),
        ("chapter", 3, "METHODOLOGY"),
        ("section", "3.1 Data Collection and Preprocessing"),
        (
            "body",
            "Candidate input is accepted as PDF, DOCX, UTF-8 TXT or pasted text, limited to 2 MB "
            "and 50 PDF pages; originals are not retained. Extraction produces an editable draft, so "
            "parser errors can be corrected before saving. Normalisation handles sentence boundaries, "
            "aliases and 24 skills, and context-rules-v2 labels each mention as supported, learning, "
            "uncertain or negated.",
        ),
        ("section", "3.2 Architecture Diagram"),
        (
            "body",
            "A React and TypeScript single-page application is served by a FastAPI process that "
            "owns session validation, role checks and request validation. Domain services implement "
            "authentication, parsing, jobs, applications, decisions, matching and audit arithmetic; "
            "SQLAlchemy persists records in SQLite, with PostgreSQL optional. The ranking path "
            "receives only the rubric and submitted snapshot. Figure 3.1 shows the layers; the "
            "remaining design models appear in the Detailed edition.",
        ),
        ("figure", "architecture.png", "Figure 3.1: Layered architecture of Candidate Lab", 7.8, 5.6),
        ("section", "3.3 Proposed Methodology"),
        ("subsection", "3.3.1 Matching and Scoring Method"),
        (
            "body",
            "Required coverage R is the fraction of required skills with supported evidence, "
            "preferred coverage P is the fraction for preferred skills, and lexical alignment L is "
            "the cosine similarity between the skill query and the profile's skill-bearing text. The "
            "index is:",
        ),
        ("formula", "Score = 100 x (0.60R + 0.15P + 0.25L)"),
        (
            "body",
            "With no preferred skills, the required weight rises to 0.75 and P becomes zero. Each "
            "component is multiplied by 100 and rounded to four decimals, and the contributions sum "
            "to the saved score; for R = 1.0, P = 1.0 and L = 0.10, the score is 77.5. Learning, "
            "negated or ambiguous mentions earn no coverage.",
        ),
        ("subsection", "3.3.2 System Models"),
        (
            "body",
            "Data-flow, class, sequence, state and activity models document the design; the context "
            "diagram treats Candidate Lab as one process with candidate, recruiter and auditor "
            "entities. The Detailed edition reproduces all seven diagrams.",
        ),
        ("figure", "dfd_level0.png", "Figure 3.2: Level-0 data-flow diagram (context)", 8.8, 5.6),
        ("subsection", "3.3.3 Design Walkthrough"),
        (
            "body",
            "A candidate registers, uploads a resume or pastes text, reviews the extracted draft and "
            "confirms a profile version. A recruiter creates a job with required and preferred "
            "skills, publishes it and starts a run against active applications. Each run saves one "
            "result per application with the method, rubric and component contributions; the "
            "reviewer opens the cited passages, records a decision and the application advances.",
        ),
        (
            "body",
            "Only supported evidence contributes to coverage. Learning, negated or uncertain "
            "mentions remain visible but earn no points, and a passage that is not found is reported "
            "as not found rather than as absence of the skill. The state chart limits transitions "
            "to submitted, under review, shortlisted, rejected and withdrawn, while the activity "
            "model follows the same path to the recorded decision and audit event.",
        ),
        ("chapter", 4, "IMPLEMENTATION"),
        ("section", "4.1 Development Environment and Technology Stack"),
        (
            "body",
            "The prototype was verified on a Windows laptop with Python 3.11.9, Node.js 24.15.0, "
            "FastAPI, Pydantic, SQLAlchemy and scikit-learn. The frontend uses React 19, TypeScript "
            "5.7 and Vite 6; SQLite is the default database, PostgreSQL optional, and Playwright "
            "1.56 drives the Chrome journeys. Table 4.1 records the verified stack.",
        ),
        _stack_table(),
        ("section", "4.2 Application Implementation"),
        (
            "body",
            "The frontend is a role-aware single-page application: navigation follows the assigned "
            "role, list state is held in the query string, unsaved forms use a confirmation dialog, "
            "and the typed API client centralises errors. The backend owns authentication, profiles, "
            "parsing, jobs, applications, matching runs, decisions, evidence and audit events; "
            "applications and first versions are inserted together, and a run stores an immutable "
            "snapshot.",
        ),
        ("section", "4.3 Security, Privacy and Role Controls"),
        (
            "body",
            "Passwords use salted PBKDF2-HMAC-SHA256 with 310,000 iterations. Login creates a "
            "random token; only its SHA-256 hash and an eight-hour expiry are stored, and the browser "
            "receives an HttpOnly, SameSite=Strict cookie. Role and ownership checks are server "
            "dependencies, and recruiter or auditor registration requires a single-use invitation "
            "bound to the same email and role. Middleware rejects unapproved origins and sets safe "
            "response headers.",
        ),
        ("section", "4.4 Verification and Results"),
        (
            "body",
            "Verification combines calculation tests, API integration tests and production-build "
            "browser journeys. The 26 backend tests cover authentication, ownership, roles, versions, "
            "evidence, scoring, invitations, parsing, decisions, audit suppression and evaluation. "
            "The nine browser journeys cover registration, job editing, profile correction, matching, "
            "evidence review, decisions, audit export and mobile layout. Table 4.2 summarises the "
            "checks.",
        ),
        _verification_table(),
        ("section", "4.5 Discussion"),
        (
            "body",
            "The results show that the main workflow is wired end to end: registration, profile "
            "preparation, job publication, matching, evidence review, decision recording and audit "
            "export all execute against a production build. The backend suite uses temporary "
            "databases and the browser suite starts a disposable server on port 8001, so the "
            "demonstration database is never modified. Passing tests do not measure extraction "
            "accuracy or ranking quality.",
        ),
        (
            "body",
            "The matching index is a transparent rubric score, not a probability of suitability. "
            "Weights make required coverage dominant and keep lexical alignment as a tie-breaker; "
            "they were not optimized on labelled data. Skill coverage depends on a 24-item "
            "vocabulary and context rules, so a valid synonym outside the vocabulary may be missed. "
            "The semantic method reduces vocabulary mismatch but makes the reason for a match less "
            "direct.",
        ),
        (
            "body",
            "Two design choices proved especially valuable. Every saved profile and application "
            "version is immutable, so a later correction cannot rewrite the evidence behind an "
            "earlier decision. The decision is also a separate attributed record rather than a "
            "status field, which preserves the reviewer's note and the exact run that informed it. "
            "Both choices add storage and query complexity but make the audit trail defensible.",
        ),
        (
            "body",
            "The audit screen reports descriptive rates with Wilson intervals and suppresses small "
            "groups, but the synthetic cohort cannot establish fairness for a real applicant "
            "population. Explainability and fairness are treated as obligations to expose "
            "assumptions, evidence and limits rather than properties certified by a score. "
            "Production use would require consented evaluation data, retention and tenant controls, "
            "monitoring and a governed review process.",
        ),
        ("chapter", 5, "CONCLUSION"),
        ("section", "5.1 Conclusion"),
        (
            "body",
            "Candidate Lab implements an evidence-led workflow for matching and human review. It "
            "connects explicit job requirements to resume passages, calculates a visible matching "
            "index, preserves the information used for each result and keeps the final decision "
            "with a reviewer. The main achievement is an integrated, inspectable application, not "
            "a claim of automated hiring intelligence.",
        ),
        (
            "body",
            "Version conflicts protect corrections, immutable snapshots retain historical "
            "explanations, and direct contribution terms show why points were awarded. Keyword "
            "evidence and lexical similarity still require interpretation. The 26 backend tests "
            "and nine browser journeys establish selected functional behaviour, not production "
            "readiness or predictive quality. The synthetic audit illustrates rates and "
            "uncertainty but cannot establish fairness in a real applicant population. "
            "Explainability and fairness are therefore treated as obligations to make assumptions "
            "and limits visible, not as properties that a single score can certify.",
        ),
        ("section", "5.2 Future Scope"),
        (
            "bullets",
            [
                (
                    "F1.",
                    "Collect consented relevance annotations under a documented rubric and compare "
                    "lexical, semantic and supervised methods on held-out data.",
                ),
                (
                    "F2.",
                    "Evaluate passage extraction independently, add isolated OCR and preserve "
                    "provenance for model, data, rubric and vocabulary versions.",
                ),
                (
                    "F3.",
                    "Obtain approved audit attributes without inferring protected characteristics, "
                    "define qualification labels and report uncertainty for every fairness measure.",
                ),
                (
                    "F4.",
                    "Add email verification, tenant isolation, migrations, monitoring, backups and "
                    "retention workflows before any shared deployment.",
                ),
            ],
        ),
    ]


def _detailed_blocks() -> list:
    blocks = _standard_blocks()

    # Replace the concise chapter 1 material with the expanded discussion.
    start = blocks.index(("chapter", 1, "INTRODUCTION"))
    end = blocks.index(("chapter", 2, "LITERATURE SURVEY"))
    blocks[start:end] = [
        ("chapter", 1, "INTRODUCTION"),
        ("section", "1.1 Introduction"),
        (
            "body",
            "Recruitment requires a reviewer to judge whether documented experience is relevant "
            "to a job. Resumes differ in structure, vocabulary and detail, while job descriptions "
            "mix essential requirements with desirable skills. A useful screening system must "
            "preserve the connection between a requirement, the evidence found in a document and "
            "the judgment made by a reviewer.",
        ),
        (
            "body",
            "The project title refers to fair and explainable machine learning, but the "
            "implemented release does not pretend to be a trained predictor of hiring success. Its "
            "default matcher is a transparent heuristic built from dictionary evidence, context "
            "rules and TF-IDF alignment. This choice makes every input and arithmetic term "
            "inspectable, while exposing the limits of lexical matching: a mention is not proof of "
            "proficiency, a missing phrase is not proof that a skill is absent, and a high score is "
            "not a calibrated probability.",
        ),
        (
            "body",
            "Candidate Lab is a local, role-aware decision-support application built around these "
            "concerns. Candidates create and correct profiles and apply to published jobs; "
            "recruiters define explicit skill rubrics, inspect evidence-linked rankings and record "
            "reasoned decisions; auditors see aggregate cohort rates and an append-only event log. "
            "The Stage-1 work covers the problem definition, relevant literature, data and "
            "preprocessing pipeline, architecture and design models, the implemented prototype and "
            "the verification evidence.",
        ),
        ("section", "1.2 Problem Statement"),
        (
            "body",
            "Manual shortlisting is flexible but difficult to reproduce. Reviewers apply "
            "different thresholds, corrections overwrite earlier documents, and candidates may "
            "never learn that relevant experience was ignored. Automated tools add "
            "vocabulary-sensitive filters, historical bias in labels, opaque semantic similarity "
            "and audit reports that lack valid qualification labels.",
        ),
        (
            "body",
            "The technical problem is to transform heterogeneous documents and explicit job "
            "requirements into a traceable comparison while preserving evidence, version and role "
            "context. The research problem is to do so without overstating what the comparison "
            "establishes. The prototype must make assumptions visible, separate ranking from human "
            "decision, keep audit attributes out of the scoring path and state which fairness "
            "questions cannot be answered with the available data.",
        ),
        ("section", "1.3 Objectives"),
        (
            "body",
            "Table 1.1 maps each objective to an observable indicator that can be examined in the "
            "implementation or the verification record. The objectives deliberately cover the "
            "workflow rather than a single accuracy target.",
        ),
        _objectives_table(short=False),
        ("section", "1.4 Scope and Organisation"),
        (
            "body",
            "The scope is intentionally local and bounded. The prototype does not include OCR, a "
            "production identity provider, multi-organisation tenancy, background workers, email "
            "delivery or a representative labelled dataset. Chapter 2 reviews existing approaches "
            "and states the proposed system. Chapter 3 explains the methodology, scoring and system "
            "models. Chapter 4 summarises implementation, security and verification. Chapter 5 "
            "concludes the work and identifies next steps.",
        ),
    ]

    # Expand chapter 2.
    start = blocks.index(("chapter", 2, "LITERATURE SURVEY"))
    end = blocks.index(("chapter", 3, "METHODOLOGY"))
    blocks[start:end] = [
        ("chapter", 2, "LITERATURE SURVEY"),
        ("section", "2.1 Existing System"),
        (
            "body",
            "Existing practice spans manual review, keyword or Boolean search, lexical retrieval, "
            "semantic embeddings, supervised ranking and post-hoc explanation. These approaches "
            "are complementary, but each addresses only part of the inspectability problem. Manual "
            "review uses context that a parser cannot: a project may demonstrate a skill even when "
            "the exact tool name is absent, and progression may matter more than a keyword count. "
            "Its weakness is consistency. Different reviewers apply different thresholds, reasons "
            "are rarely retained in structured form, and a later correction makes it difficult to "
            "reconstruct the document originally reviewed.",
        ),
        (
            "body",
            "Keyword filters treat 'PostgreSQL' and 'Postgres' as different terms and may count "
            "'no experience with Docker' as a positive hit. TF-IDF and cosine similarity provide a "
            "reproducible lexical baseline [1], but remain bag-of-words methods. Sentence-BERT [2] "
            "reduces the vocabulary gap at the cost of model dependencies and less direct "
            "explanation. Document parsing adds further error because PDF and DOCX extraction can "
            "reorder or omit text [3,4]. PDF extraction depends on internal structure and fails "
            "for scanned images without OCR; DOCX extraction must handle paragraphs, tables and "
            "compressed archives. Parser failures can remove relevant evidence or introduce "
            "ordering artefacts.",
        ),
        (
            "body",
            "Supervised rankers inherit the label-generation process and can reproduce historical "
            "disadvantage. SHAP explains a model's prediction rather than validating its data [5]. "
            "Fairness research distinguishes demographic parity, which compares selection rates, "
            "from equalized odds, which compares true-positive and false-positive rates "
            "conditional on a valid qualification label [6]. The second family cannot be estimated "
            "without labels, and neither can be established from arbitrary group labels or a small "
            "synthetic sample. Wilson intervals express the uncertainty of a rate estimated from a "
            "finite sample [10], but wide intervals are a warning rather than a fairness "
            "certificate.",
        ),
        _approach_table(),
        ("section", "2.2 Proposed System"),
        (
            "body",
            "Candidate Lab proposes evidence-led decision support rather than autonomous ranking. "
            "The unit of comparison is a saved application snapshot: a job rubric, a confirmed "
            "profile version and the evidence extracted from that version. The recruiter sees a "
            "matching index and the passages that produced it; the final decision remains a "
            "separate, attributed human action.",
        ),
        (
            "body",
            "The design follows six principles: explicit required and preferred skills; evidence "
            "before score; append-only profile, application, run and decision history; "
            "server-enforced roles; audit attributes isolated from the ranking path; and bounded "
            "claims. Table 2.2 maps the gaps identified above to specific design responses. OCR, "
            "production identity, multi-tenant isolation, background workers and a representative "
            "labelled dataset are outside this Stage-1 prototype.",
        ),
        _gap_table(),
    ]

    # Expand chapter 3 while keeping all diagrams inside the text block.
    start = blocks.index(("chapter", 3, "METHODOLOGY"))
    end = blocks.index(("chapter", 4, "IMPLEMENTATION"))
    blocks[start:end] = [
        ("chapter", 3, "METHODOLOGY"),
        ("section", "3.1 Data Collection and Preprocessing"),
        (
            "body",
            "The methodology uses candidate documents, job descriptions, a synthetic demonstration "
            "workspace and a synthetic relevance fixture. Candidate input is accepted as PDF, DOCX, "
            "UTF-8 TXT or pasted text, with uploads limited to 2 MB, PDFs to 50 pages and DOCX "
            "archives to a bounded expanded size; originals are processed in memory and not "
            "retained. Extraction produces an editable draft: the text, warnings and recognised "
            "skills are shown before saving, so parser errors can be corrected. Normalisation "
            "handles sentence and clause boundaries, aliases and 24 canonical skills; "
            "context-rules-v2 labels each mention as supported, learning, uncertain or negated, and "
            "only supported evidence earns coverage. Every saved profile produces a version, and an "
            "application stores its own snapshot and revision. Table 3.1 summarises the stages.",
        ),
        _preprocess_table(),
        ("section", "3.2 Architecture Diagram"),
        (
            "body",
            "The system uses a layered architecture. A React and TypeScript single-page application "
            "is served by a FastAPI process that owns session validation, role dependencies, request "
            "validation, origin checks, size limits and static assets. Domain services implement "
            "authentication, parsing, jobs, applications, decisions, matching and audit arithmetic. "
            "SQLAlchemy persists records in SQLite by default, with PostgreSQL optional, and a local "
            "Sentence Transformers model supports the semantic path. Every protected request checks "
            "the required role before a service is called; the ranking path receives only the rubric "
            "and submitted snapshot. Figure 3.1 shows the layers.",
        ),
        ("figure", "architecture.png", "Figure 3.1: Layered architecture of Candidate Lab", 9.2, 6.2),
        ("section", "3.3 Proposed Methodology"),
        ("subsection", "3.3.1 Matching and Scoring Method"),
        (
            "body",
            "For each active application, required coverage R is the fraction of required skills "
            "with supported evidence, preferred coverage P is the corresponding fraction for "
            "preferred skills, and lexical alignment L is the cosine similarity between a query "
            "built from the skill names and the profile's skill-bearing text. The matching index "
            "is:",
        ),
        ("formula", "Score = 100 x (0.60R + 0.15P + 0.25L)"),
        (
            "body",
            "When a job has no preferred skills, the required weight rises to 0.75 and the preferred "
            "term becomes zero. Each component is multiplied by 100 and rounded to four decimals, "
            "and the displayed contributions sum to the saved score; for R = 1.0, P = 1.0 and "
            "L = 0.10, the score is 77.5. The default method is skill-tfidf-v2; skill-semantic-v2 "
            "replaces lexical alignment with a pinned local MiniLM model and fails explicitly if the "
            "model cannot load.",
        ),
        (
            "body",
            "A requirement is supported only when a positive use of an alias is found. Learning, "
            "negated or ambiguous mentions earn no coverage; not-found means the rules did not find "
            "a passage, not that the candidate lacks the skill. Results are sorted by descending "
            "score with a stable tie-breaker, and saved runs retain method, rubric, versions, "
            "evidence and contributions. The auditor report uses a common cutoff, group sizes, 95% "
            "Wilson intervals and suppression below five records; it is descriptive and cannot "
            "establish real-world fairness.",
        ),
        ("subsection", "3.3.2 System Models and Data Flow"),
        (
            "body",
            "Figures 3.2 to 3.7 document the context, data flow, persistent classes, sequence, state "
            "and activity views.",
        ),
        (
            "body",
            "Taken together, the models describe the same system at different levels of abstraction. "
            "The architecture shows trust boundaries; the data-flow diagrams show information "
            "movement; the class diagram shows durable records; the sequence and state models show "
            "time and lifecycle; and the activity model shows the human workflow.",
        ),
        ("figure", "dfd_level0.png", "Figure 3.2: Level-0 data-flow diagram (context)", 9.0, 5.6),
        ("figure", "dfd_level1.png", "Figure 3.3: Level-1 data-flow diagram", 9.0, 5.8),
        ("figure", "class_diagram.png", "Figure 3.4: Class diagram of the persistent domain", 9.0, 5.6),
        ("figure", "sequence_diagram.png", "Figure 3.5: Sequence diagram for application and matching", 9.0, 5.8),
        ("figure", "state_chart.png", "Figure 3.6: State chart for a job application", 8.8, 5.2),
        ("figure", "activity_diagram.png", "Figure 3.7: Activity diagram from evidence preparation to audit", 6.4, 8.0),
    ]

    # Expand chapter 4.
    start = blocks.index(("chapter", 4, "IMPLEMENTATION"))
    end = blocks.index(("chapter", 5, "CONCLUSION"))
    blocks[start:end] = [
        ("chapter", 4, "IMPLEMENTATION"),
        ("section", "4.1 Development Environment and Technology Stack"),
        (
            "body",
            "The prototype was verified on a local Windows laptop with Python 3.11.9, Node.js "
            "24.15.0, FastAPI 0.162.7, Pydantic 2.14.3, SQLAlchemy 2.1.8 and scikit-learn 1.9.1. "
            "The frontend uses React 19, TypeScript 5.7 and Vite 6; SQLite is the default database, "
            "PostgreSQL is optional, and Playwright 1.56 drives the Chrome tests. Table 4.1 records "
            "the verified stack.",
        ),
        _stack_table(),
        ("section", "4.2 Frontend Implementation"),
        (
            "body",
            "The frontend is a role-aware single-page application. Public screens handle sign-in and "
            "registration; after authentication the server-assigned role determines navigation. "
            "Candidates see profiles, opportunities and applications; recruiters see jobs, "
            "candidates, matching and evaluation; auditors see aggregate reports and events. List "
            "state is held in the query string, unsaved forms use a confirmation dialog, and the "
            "typed API client centralises errors.",
        ),
        (
            "body",
            "The profile editor shows extracted text and warnings before saving; matching shows "
            "score, method, version and component breakdown; application review loads the submitted "
            "snapshot and saved evidence; the audit screen exposes cutoff, counts, rates, intervals, "
            "suppression and JSON export.",
        ),
        ("section", "4.3 Backend and Data Implementation"),
        (
            "body",
            "The backend is split into four modules, summarised in Table 4.2. It owns "
            "authentication, profiles, parsing, jobs, applications, matching runs, decisions, "
            "evidence and audit events. An application inserts its row and first version together, "
            "and a unique constraint prevents duplicate active applications. A matching run loads "
            "active snapshots and stores a complete immutable result; a decision checks the current "
            "revision, appends a new decision and evidence, and updates status.",
        ),
        _modules_table(),
        (
            "body",
            "A synthetic evaluation path loads a JSON dataset of queries, fictional profiles and "
            "relevance grades, runs TF-IDF-only or TF-IDF plus the configured local model, and "
            "computes NDCG, recall and precision per query. The shipped fixture is a smoke test, not "
            "a representative benchmark.",
        ),
        ("section", "4.4 Security, Privacy and Role Controls"),
        (
            "body",
            "Passwords use salted PBKDF2-HMAC-SHA256 with 310,000 iterations. Login creates a random "
            "opaque token; only its SHA-256 hash and an eight-hour expiry are stored, and the browser "
            "receives an HttpOnly, SameSite=Strict cookie. Role and ownership checks are server "
            "dependencies. Recruiter and auditor registration requires a single-use invitation bound "
            "to the same email and role, stored as a hash and expiring after 24 hours by default.",
        ),
        (
            "body",
            "Middleware rejects unapproved mutation origins and sets nosniff, frame-denial and "
            "no-store headers. Original uploads are not retained, and confirmed text is stored "
            "locally. Retention, deletion, consent and organisation isolation remain future work; "
            "audit attributes never enter the matcher.",
        ),
        ("section", "4.5 Verification and Results"),
        (
            "body",
            "Verification combines calculation tests, API integration tests and production-build "
            "browser journeys. The backend suite uses temporary databases; the browser suite starts "
            "its own server on port 8001 with a disposable database. Table 4.3 summarises the checks.",
        ),
        _verification_table("Table 4.3: Verification summary"),
        (
            "body",
            "The backend tests cover authentication, ownership, roles, versions, evidence, scoring, "
            "invitations, parsing, decisions, audit suppression and evaluation. The browser journeys "
            "cover registration, job editing, profile correction, matching, evidence review, "
            "decisions, audit export and mobile layout. These results establish selected functional "
            "behaviour, not model accuracy or real-world fairness.",
        ),
        ("section", "4.6 Discussion"),
        (
            "body",
            "The implementation makes several deliberate trade-offs. The default matcher is lexical "
            "because TF-IDF is local, deterministic and cheap to explain; the optional semantic path "
            "reduces vocabulary mismatch but adds a model dependency and makes the reason for a "
            "match less direct. Required coverage dominates the index so that strong optional "
            "alignment cannot compensate for a missing essential skill. The weights are policy "
            "choices, not learned parameters, and should be reviewed with domain experts before "
            "operational use.",
        ),
        (
            "body",
            "Evidence extraction favours precision over recall. A requirement is supported only "
            "when a positive alias appears in a relevant context, which protects reviewers from "
            "inflated coverage but can understate a candidate who describes equivalent experience "
            "in unfamiliar words. The 24-skill vocabulary and context-rules-v2 are therefore a "
            "starting point: expanding aliases and evaluating passage extraction independently are "
            "prerequisites for broader use.",
        ),
        (
            "body",
            "Data integrity relies on append-only versions and snapshots. A profile correction "
            "creates a new version, an application stores the exact version it submitted, and a "
            "matching run stores the rubric, method, evidence and contributions that produced its "
            "result. A decision checks the current revision before appending, which prevents a "
            "reviewer from acting on a stale screen. This design costs storage and adds query "
            "complexity, but it makes every displayed score reproducible after later edits.",
        ),
        (
            "body",
            "Security is proportionate to a local prototype rather than a production service. "
            "Opaque session tokens are stored as hashes, invitations are single-use and email-bound, "
            "roles and ownership are enforced on the server, and uploaded originals are discarded "
            "after extraction. Organisation isolation, retention schedules, consent records, email "
            "verification and administrator recovery are not implemented. These are not cosmetic "
            "gaps: multi-tenant use would require them before real candidate data is processed.",
        ),
        (
            "body",
            "Verification demonstrates functional integration, not predictive validity. The backend "
            "suite uses temporary databases, the browser suite runs against a production build on a "
            "disposable server, and static checks cover typing, linting, formatting and bundling. "
            "The synthetic evaluation fixture and cohort audit are smoke tests. A credible claim of "
            "matching quality or fairness would need consented relevance judgements, a held-out "
            "protocol, uncertainty reporting and independent review.",
        ),
        _tradeoffs_table(),
        (
            "body",
            "These trade-offs keep the prototype honest about what it can support. The system is "
            "designed to make a reviewer's reasoning faster to inspect, not to replace it; each "
            "limitation maps to a bounded claim in this report and to a concrete item in the future "
            "scope.",
        ),
    ]

    # Expand chapter 5.
    start = blocks.index(("chapter", 5, "CONCLUSION"))
    blocks[start:] = [
        ("chapter", 5, "CONCLUSION"),
        ("section", "5.1 Conclusion"),
        (
            "body",
            "Candidate Lab implements an evidence-led workflow for matching and human review. It "
            "connects explicit job requirements to resume passages, calculates a visible matching "
            "index, preserves the information used for each result and keeps the final decision with "
            "a reviewer. The prototype combines a React and TypeScript interface, FastAPI services, "
            "SQLAlchemy persistence, document parsers, context-aware skill rules and a TF-IDF "
            "baseline with an optional local semantic path.",
        ),
        (
            "body",
            "Version conflicts protect corrections, immutable snapshots retain historical "
            "explanations, and direct contribution terms show why points were awarded. Keyword "
            "evidence and lexical similarity still require interpretation, and the recorded "
            "verification establishes selected functional behaviour rather than production readiness "
            "or predictive quality. The synthetic cohort audit illustrates rates and uncertainty but "
            "cannot establish fairness in a real applicant population. Explainability and fairness "
            "are therefore treated as obligations to make assumptions and limits visible, not as "
            "properties that a single score can certify.",
        ),
        ("section", "5.2 Future Scope"),
        (
            "bullets",
            [
                (
                    "F1.",
                    "Collect consented relevance annotations under a documented rubric, measure "
                    "agreement and compare lexical, semantic and supervised methods on held-out data.",
                ),
                (
                    "F2.",
                    "Evaluate passage extraction independently, add OCR through an isolated service "
                    "and preserve provenance for model, data, rubric and vocabulary versions.",
                ),
                (
                    "F3.",
                    "Obtain approved audit attributes without inferring protected characteristics, "
                    "define qualification labels and report uncertainty for every fairness measure.",
                ),
                (
                    "F4.",
                    "Add email verification, tenant isolation, migrations, isolated parsing, "
                    "monitoring, backups and retention workflows before any shared deployment.",
                ),
                (
                    "F5.",
                    "Verify PostgreSQL and container deployment, configure HTTPS and secure cookies, "
                    "and conduct accessibility and usability studies with representative users.",
                ),
            ],
        ),
    ]
    return blocks


STANDARD_BLOCKS = _standard_blocks()
DETAILED_BLOCKS = _detailed_blocks()
