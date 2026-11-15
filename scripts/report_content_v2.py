"""Version 2 body content for the Standard and Detailed reports.

The front matter is shared with :mod:`report_content` so pages 1-4 stay
identical to the reviewed edition.  Version 2 rebuilds the body: every edition
now carries the complete set of seven design diagrams, each diagram is
explained in prose, and the Standard chapter 4 is condensed to a single page.
"""
from __future__ import annotations

from report_content import (
    ACKNOWLEDGEMENT,
    COLLEGE,
    DEPARTMENT,
    GUIDE,
    GUIDE_DESIGNATION,
    HOD,
    HOD_DESIGNATION,
    PRINCIPAL,
    SHORT_TITLE,
    STUDENTS,
    TITLE,
    YEAR,
    _approach_table,
    _gap_table,
    _modules_table,
    _objectives_table,
    _preprocess_table,
    _stack_table,
    _tradeoffs_table,
    _verification_table,
)

__all__ = [
    "ACKNOWLEDGEMENT",
    "COLLEGE",
    "DEPARTMENT",
    "GUIDE",
    "GUIDE_DESIGNATION",
    "HOD",
    "HOD_DESIGNATION",
    "PRINCIPAL",
    "SHORT_TITLE",
    "STUDENTS",
    "TITLE",
    "YEAR",
    "STANDARD_BLOCKS",
    "DETAILED_BLOCKS",
    "REFERENCES",
    "PROOF_TEXT",
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
    "[11] Microsoft, \"Playwright documentation.\" [Online]. Available: "
    "https://playwright.dev/",
    "[12] OWASP Foundation, \"OWASP Application Security Verification Standard 4.0.3,\" 2021. "
    "[Online]. Available: https://owasp.org/www-project-application-security-verification-standard/",
    "[13] National Institute of Standards and Technology, \"Artificial Intelligence Risk "
    "Management Framework (AI RMF 1.0),\" NIST AI 100-1, 2023.",
    "[14] C. D. Manning, P. Raghavan, and H. Schutze, Introduction to Information Retrieval. "
    "Cambridge, U.K.: Cambridge University Press, 2008.",
    "[15] G. Salton and C. Buckley, \"Term-weighting approaches in automatic text retrieval,\" "
    "Information Processing & Management, vol. 24, no. 5, pp. 513-523, 1988.",
]

PROOF_TEXT = (
    "Publication is not claimed at the time of this Stage-1 submission. No paper from this work "
    "has been communicated, accepted or published. This page records the verification status of "
    "the report and is intentionally reserved for an authentic acceptance letter, conference or "
    "journal first page, or DOI record once a publication exists. A placeholder is used instead "
    "of a fabricated certificate."
)

PROOF_NOTE = (
    "The authors confirm that this report is original work, that every external source used in "
    "the design, implementation and evaluation is cited in the reference list, and that the "
    "figures and tables were produced for this project. The publication fields will be completed "
    "only after a genuine acceptance, and the placeholder will then be replaced by the "
    "corresponding documentary evidence."
)


def _worked_table(caption: str) -> tuple:
    return (
        "table",
        caption,
        ["Component", "Symbol", "Value", "Weight", "Points"],
        [
            ["Required coverage", "R", "0.75", "0.60", "45.00"],
            ["Preferred coverage", "P", "0.50", "0.15", "7.50"],
            ["Lexical alignment", "L", "0.42", "0.25", "10.50"],
            ["Matching index", "S", "-", "-", "63.00"],
        ],
        [5.2, 1.6, 2.2, 2.2, 4.4],
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
            "rankers capture subtler relationships but need labelled data and resist audit. "
            "Candidate Lab is a local, role-aware decision-support application. Candidates correct "
            "profiles and apply to published jobs; recruiters define explicit rubrics, inspect "
            "evidence-linked rankings and record reasoned decisions; auditors see aggregate rates "
            "and an append-only event log.",
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
            "semantic embeddings, supervised ranking and post-hoc explanation. These approaches are "
            "complementary, but each addresses only part of the problem; Table 2.1 compares their "
            "limits for this project.",
        ),
        (
            "body",
            "Keyword filters miss aliases and negation; TF-IDF is reproducible but bag-of-words "
            "[1,15]; Sentence-BERT reduces the vocabulary gap but adds dependencies [2]; and parsing "
            "can reorder or omit text [3,4]. Supervised rankers inherit their labels and can reproduce "
            "historical disadvantage. SHAP explains a prediction rather than validating its data [5], "
            "while equalized odds needs qualification labels [6]. Wilson intervals quantify "
            "uncertainty [10] but do not certify fairness. The gap is an integrated workflow that "
            "keeps criteria, evidence, versions, roles, decisions and audit limits visible in one "
            "application.",
        ),
        _approach_table(),
        ("section", "2.2 Proposed System"),
        (
            "body",
            "Candidate Lab proposes evidence-led decision support, not autonomous ranking. The unit "
            "of comparison is a saved application snapshot: a job rubric, a confirmed profile version "
            "and its extracted evidence. The recruiter sees the index and its passages; the final "
            "decision remains a separate, attributed human action.",
        ),
        (
            "body",
            "Six principles guide the design: explicit required and preferred skills, evidence "
            "before score, append-only history, server-enforced roles, audit attributes isolated "
            "from ranking, and bounded claims. OCR, production identity, multi-tenancy and a labelled "
            "dataset remain outside this prototype.",
        ),
        ("chapter", 3, "METHODOLOGY"),
        ("section", "3.1 Data Collection and Preprocessing"),
        (
            "body",
            "Candidate input is accepted as PDF, DOCX, UTF-8 TXT or pasted text, limited to 2 MB "
            "and 50 PDF pages; originals are processed in memory. Extraction produces an editable "
            "draft, so parser errors can be corrected before saving. Normalisation handles sentence "
            "and clause boundaries, aliases and 24 canonical skills, while context-rules-v2 labels "
            "each mention as supported, learning, uncertain or negated. Only supported evidence earns "
            "coverage; every saved profile and application keeps a versioned snapshot.",
        ),
        ("section", "3.2 Architecture Diagram"),
        (
            "body",
            "A React and TypeScript single-page application is served by a FastAPI process that "
            "owns session validation, role dependencies, request validation, origin checks, size "
            "limits and static assets. Domain services implement authentication, parsing, jobs, "
            "applications, decisions, matching and audit; SQLAlchemy persists records in SQLite, with "
            "PostgreSQL optional. The ranking path receives only the rubric and submitted snapshot; "
            "names, contact details and audit attributes never enter the matcher. Figure 3.1 shows "
            "the layers and trust boundaries.",
        ),
        ("figure", "architecture.png", "Figure 3.1: Layered architecture of Candidate Lab", 11.5, 7.2),
        (
            "body",
            "The presentation layer holds no authority: navigation reflects the role, but every "
            "protected request is re-checked on the server. The API boundary is therefore the trust "
            "boundary, and keeping the optional semantic encoder local avoids sending resume text to "
            "an external service.",
        ),
        ("section", "3.3 Proposed Methodology"),
        ("subsection", "3.3.1 Matching and Scoring Method"),
        (
            "body",
            "R is the fraction of required skills with supported evidence, P the corresponding "
            "fraction for preferred skills, and L the cosine similarity between the skill query and "
            "profile text. The matching index is:",
        ),
        ("formula", "Score = 100 x (0.60R + 0.15P + 0.25L)"),
        (
            "body",
            "With no preferred skills, the required weight rises to 0.75 and P becomes zero. "
            "Components are multiplied by 100 and rounded to four decimals, and the contributions sum "
            "to the saved score. Table 3.1 shows a worked case: three of four required skills, one of "
            "two preferred skills and moderate alignment produce 63.00 points.",
        ),
        _worked_table("Table 3.1: Worked scoring example"),
        (
            "body",
            "A requirement is supported only when a positive alias appears in a relevant context. "
            "Learning, negated or ambiguous mentions earn no coverage; not-found means no passage was "
            "found, not that the skill is absent. Results sort by descending score with a stable "
            "tie-breaker, and saved runs retain method, rubric, versions, evidence and contributions. "
            "The default is skill-tfidf-v2; skill-semantic-v2 uses a pinned local MiniLM model and "
            "fails explicitly if it cannot load.",
        ),
        ("subsection", "3.3.2 System Models and Data Flow"),
        (
            "body",
            "Six further models document the same system at different levels: the context and "
            "level-1 data-flow diagrams, the persistent class model, the matching sequence, the "
            "application state chart and the human activity flow.",
        ),
        ("figure", "dfd_level0.png", "Figure 3.2: Level-0 data-flow diagram (context)", 12.0, 6.5),
        (
            "body",
            "Figure 3.2 treats Candidate Lab as one process: candidates give evidence, recruiters "
            "set rubrics and see rankings, and auditors see aggregates only; audit attributes never "
            "enter ranking.",
        ),
        ("figure", "dfd_level1.png", "Figure 3.3: Level-1 data-flow diagram", 12.0, 7.1),
        (
            "body",
            "The level-1 diagram separates account, profile, job, ranking and audit processes and "
            "their stores; profile text is read only through a snapshot, and the matcher writes an "
            "immutable run.",
        ),
        ("figure", "class_diagram.png", "Figure 3.4: Class diagram of the persistent domain", 12.0, 7.3),
        (
            "body",
            "The class model keeps profile and application versions, runs, evidence, decisions and "
            "audit events as separate records, so a correction appends rather than overwrites earlier "
            "evidence.",
        ),
        ("figure", "sequence_diagram.png", "Figure 3.5: Sequence diagram for application and matching", 12.0, 7.7),
        (
            "body",
            "The sequence model shows one run: load the rubric and active snapshots, score each "
            "candidate, persist the result with evidence and return the ranking; a review cannot "
            "alter it.",
        ),
        ("figure", "state_chart.png", "Figure 3.6: State chart for a job application", 12.0, 6.6),
        (
            "body",
            "The state chart limits an application to submitted, under review, shortlisted, "
            "rejected and withdrawn; acceptance is not an offer, and rejected applications leave "
            "later runs unchanged.",
        ),
        ("figure", "activity_diagram.png", "Figure 3.7: Activity diagram from evidence preparation to audit", 8.5, 10.4),
        (
            "body",
            "The activity model follows preparation, submission, matching, evidence review, a "
            "reasoned decision and audit. The candidate confirms a version, the recruiter runs "
            "matching, and the reviewer decides from the cited passages; no role can rewrite a saved "
            "run.",
        ),
        ("chapter", 4, "IMPLEMENTATION"),
        ("section", "4.1 Development Environment and Technology Stack"),
        (
            "body",
            "The verified build uses Python 3.11.9, FastAPI 0.162.7, Pydantic 2.14.3, SQLAlchemy "
            "2.1.8 and scikit-learn 1.9.1 on the backend, with React 19, TypeScript 5.7 and Vite 6 "
            "on the frontend [1,7-9]. SQLite is the default store, PostgreSQL is optional, and "
            "Playwright 1.56 drives the Chrome journeys [11].",
        ),
        ("section", "4.2 Application Implementation"),
        (
            "body",
            "The frontend is role-aware: candidates manage profiles and applications, recruiters "
            "manage jobs, matching and decisions, and auditors see aggregate reports and events. "
            "The backend owns authentication, parsing, versions, runs, evidence and audit. An "
            "application stores the exact submitted version, and a run keeps an immutable rubric, "
            "method and result so later edits cannot rewrite an earlier explanation.",
        ),
        ("section", "4.3 Security, Privacy and Role Controls"),
        (
            "body",
            "Passwords use salted PBKDF2-HMAC-SHA256 with 310,000 iterations; sessions are opaque "
            "tokens stored as hashes with an eight-hour expiry and HttpOnly, SameSite=Strict cookies. "
            "Role and ownership checks run on the server. Recruiter and auditor registration needs a "
            "single-use, email-bound invitation. Uploaded originals are discarded, audit attributes "
            "never enter the matcher, and unapproved mutation origins are rejected [12].",
        ),
        ("section", "4.4 Verification and Results"),
        (
            "body",
            "Twenty-six backend tests cover authentication, ownership, roles, versions, evidence, "
            "scoring, invitations, parsing, decisions, audit suppression and evaluation. Nine "
            "production-build browser journeys cover registration, job editing, profile correction, "
            "matching, evidence review, decisions, audit export and mobile layout [11].",
        ),
        ("section", "4.5 Discussion"),
        (
            "body",
            "The index is a transparent rubric, not a probability of suitability. Required coverage "
            "dominates, so optional alignment cannot hide a missing skill. Immutable versions keep "
            "scores reproducible, but the synthetic audit cannot establish fairness [6,10,13].",
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
                (
                    "F5.",
                    "Verify PostgreSQL and container deployment, configure HTTPS and secure cookies, "
                    "and conduct accessibility and usability studies with representative users.",
                ),
            ],
        ),
    ]


def _detailed_blocks() -> list:
    blocks = _standard_blocks()

    # Expanded chapter 1.
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
            "delivery or a representative labelled dataset. It does include the complete candidate, "
            "recruiter and auditor workflow, immutable snapshots, an evidence ledger, a transparent "
            "matching rubric, a bounded evaluation fixture and a verification record.",
        ),
        (
            "body",
            "Chapter 2 reviews existing approaches and states the proposed system. Chapter 3 "
            "explains the methodology, scoring and all seven system models. Chapter 4 summarises "
            "implementation, security, verification and the design trade-offs. Chapter 5 concludes "
            "the work and identifies next steps. The report separates functional evidence from "
            "model-quality and fairness claims, and every limitation maps to a bounded statement or "
            "a future-scope item.",
        ),
    ]

    # Expanded chapter 2.
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
            "reproducible lexical baseline [1,15], but remain bag-of-words methods [14]. "
            "Sentence-BERT [2] reduces the vocabulary gap at the cost of model dependencies and less "
            "direct explanation. Document parsing adds further error because PDF and DOCX extraction "
            "can reorder or omit text [3,4]. PDF extraction depends on internal structure and fails "
            "for scanned images without OCR; DOCX extraction must handle paragraphs, tables and "
            "compressed archives. Parser failures can remove evidence or introduce ordering artefacts.",
        ),
        (
            "body",
            "Supervised rankers inherit the label-generation process and can reproduce historical "
            "disadvantage. SHAP explains a prediction rather than validating its data [5]. Fairness "
            "research distinguishes demographic parity, which compares selection rates, from "
            "equalized odds, which compares true- and false-positive rates conditional on a valid "
            "qualification label [6]. The second family needs labels; neither is established by "
            "arbitrary group labels or a small synthetic sample. Wilson intervals express uncertainty "
            "[10], but wide intervals warn rather than certify.",
        ),
        _approach_table(),
        (
            "body",
            "Three implications follow. Lexical and semantic methods are complementary baselines, "
            "not competing claims of intelligence. Explanation should link each point to a "
            "requirement and passage, because post-hoc attributions do not validate the data or "
            "rubric. Fairness claims must remain separate from ranking quality, since a stable score "
            "can reflect an unjustified policy.",
        ),
        ("section", "2.2 Proposed System"),
        (
            "body",
            "Candidate Lab proposes evidence-led decision support, not autonomous ranking. The unit "
            "of comparison is a saved application snapshot: a job rubric, a confirmed profile version "
            "and its extracted evidence. The recruiter sees the index and its passages; the final "
            "decision remains a separate, attributed human action.",
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
        (
            "body",
            "The proposed system is therefore narrower than a hiring platform but stronger as an "
            "inspectable instrument. It does not infer protected characteristics, rank unknown "
            "candidates or replace a recruiter. Success means a reviewer can reconstruct why a result "
            "appeared, which evidence supported it, which version produced it and what the sample "
            "cannot establish.",
        ),
    ]

    # Expanded chapter 3 with every diagram explained in place.
    start = blocks.index(("chapter", 3, "METHODOLOGY"))
    end = blocks.index(("chapter", 4, "IMPLEMENTATION"))
    blocks[start:end] = [
        ("chapter", 3, "METHODOLOGY"),
        ("section", "3.1 Data Collection and Preprocessing"),
        (
            "body",
            "The methodology uses candidate documents, job descriptions, a synthetic demonstration "
            "workspace and a relevance fixture. Input is accepted as PDF, DOCX, UTF-8 TXT or pasted "
            "text; uploads are limited to 2 MB, 50 PDF pages and a bounded DOCX archive, and "
            "originals are processed in memory. Extraction produces an editable draft, so parser "
            "errors can be corrected. Normalisation handles sentence and clause boundaries, aliases "
            "and 24 canonical skills; context-rules-v2 labels each mention as supported, learning, "
            "uncertain or negated, and only supported evidence earns coverage. Every saved profile "
            "produces a version, and an application stores its own snapshot and revision. Table 3.1 "
            "summarises the stages.",
        ),
        _preprocess_table(),
        ("section", "3.2 Architecture Diagram"),
        (
            "body",
            "The system uses a layered architecture. A React and TypeScript single-page application "
            "is served by a FastAPI process that owns session validation, role dependencies, request "
            "validation, origin checks, size limits and static assets. Domain services implement "
            "authentication, parsing, jobs, applications, decisions, matching and audit. SQLAlchemy "
            "persists records in SQLite by default, with PostgreSQL optional, and a local Sentence "
            "Transformers model supports the semantic path. Every protected request checks the "
            "required role; the ranking path receives only the rubric and submitted snapshot. Figure "
            "3.1 shows the layers.",
        ),
        ("figure", "architecture.png", "Figure 3.1: Layered architecture of Candidate Lab", 11.5, 7.2),
        (
            "body",
            "The presentation layer holds no authority: navigation reflects the role, but every "
            "protected request is re-checked on the server. The API boundary is therefore the trust "
            "boundary, and keeping the optional semantic encoder local avoids sending resume text to "
            "an external service.",
        ),
        ("section", "3.3 Proposed Methodology"),
        ("subsection", "3.3.1 Matching and Scoring Method"),
        (
            "body",
            "For each active application, R is the fraction of required skills with supported "
            "evidence, P the corresponding fraction for preferred skills, and L the cosine similarity "
            "between a skill-name query and the profile text. The matching index is:",
        ),
        ("formula", "Score = 100 x (0.60R + 0.15P + 0.25L)"),
        (
            "body",
            "When a job has no preferred skills, the required weight rises to 0.75 and P becomes "
            "zero. Each component is multiplied by 100 and rounded to four decimals, and the "
            "contributions sum to the saved score. Table 3.2 shows a worked case: three of four "
            "required skills, one of two preferred skills and moderate alignment produce 63.00 "
            "points. The default is skill-tfidf-v2; skill-semantic-v2 uses a pinned local MiniLM "
            "model and fails explicitly if it cannot load.",
        ),
        _worked_table("Table 3.2: Worked scoring example"),
        (
            "body",
            "A requirement is supported only when a positive alias appears in a relevant context. "
            "Learning, negated or ambiguous mentions earn no coverage; not-found means no passage was "
            "found, not that the skill is absent. Results sort by descending score with a stable "
            "tie-breaker, and saved runs retain method, rubric, versions, evidence and contributions. "
            "The audit report uses a common cutoff, group sizes, 95% Wilson intervals and suppression "
            "below five records; it is descriptive and cannot establish fairness.",
        ),
        ("subsection", "3.3.2 System Models and Data Flow"),
        (
            "body",
            "Figures 3.2 to 3.7 document the context, data flow, persistent classes, sequence, state "
            "and activity views. The architecture shows trust boundaries, the data-flow diagrams show "
            "information movement, the class model shows durable records, and the sequence, state and "
            "activity views show time and human workflow.",
        ),
        ("figure", "dfd_level0.png", "Figure 3.2: Level-0 data-flow diagram (context)", 12.0, 6.5),
        (
            "body",
            "Figure 3.2 treats Candidate Lab as one process: candidates give evidence, recruiters "
            "set rubrics and see rankings, and auditors see aggregates only; audit attributes never "
            "enter ranking.",
        ),
        ("figure", "dfd_level1.png", "Figure 3.3: Level-1 data-flow diagram", 12.0, 7.1),
        (
            "body",
            "The level-1 diagram separates account, profile, job, ranking and audit processes and "
            "their stores; profile text is read only through a snapshot, and the matcher writes an "
            "immutable run.",
        ),
        ("figure", "class_diagram.png", "Figure 3.4: Class diagram of the persistent domain", 12.0, 7.3),
        (
            "body",
            "The class model makes history explicit: user, profile, application, run, result, "
            "evidence, decision and audit records are separate entities, so a correction appends a "
            "version rather than overwriting earlier evidence. The version and match tables preserve "
            "the exact text, rubric, arithmetic and passages that a run consumed, making a saved "
            "explanation reproducible.",
        ),
        ("figure", "sequence_diagram.png", "Figure 3.5: Sequence diagram for application and matching", 12.0, 7.7),
        (
            "body",
            "The sequence model shows one run: load the rubric and active snapshots, score each "
            "candidate, persist the result with its evidence and return the ranked view. A review "
            "cannot alter the saved run, and the auditor view consumes aggregates, not individual "
            "rankings.",
        ),
        ("figure", "state_chart.png", "Figure 3.6: State chart for a job application", 12.0, 6.6),
        (
            "body",
            "The state chart limits an application to submitted, under review, shortlisted, "
            "rejected and withdrawn. Acceptance is not a job offer; rejected applications leave later "
            "runs unchanged, and transition rules prevent a stale screen from overwriting a newer "
            "decision.",
        ),
        ("figure", "activity_diagram.png", "Figure 3.7: Activity diagram from evidence preparation to audit", 8.5, 10.4),
        (
            "body",
            "The activity model follows preparation, submission, matching, evidence review, a "
            "reasoned decision and separate audit. Automation prepares and compares evidence, while "
            "the reviewer decides and the auditor sees aggregates.",
        ),
        ("subsection", "3.3.3 Design Walkthrough"),
        (
            "body",
            "A candidate registers, uploads or pastes a resume, corrects the draft and confirms a "
            "version. A recruiter publishes a rubric and runs matching against active applications. "
            "The reviewer opens the cited passages, records a reasoned decision and the application "
            "advances; only supported evidence earns coverage, while learning or negated mentions "
            "remain visible but score nothing.",
        ),
        (
            "body",
            "The walkthrough also demonstrates the separation of duties: candidates control their "
            "evidence, recruiters control rubrics and decisions, and auditors receive only aggregate "
            "rates and event records. No role can rewrite a saved run.",
        ),
    ]

    # Expanded chapter 4 with a threats-to-validity section.
    start = blocks.index(("chapter", 4, "IMPLEMENTATION"))
    end = blocks.index(("chapter", 5, "CONCLUSION"))
    blocks[start:end] = [
        ("chapter", 4, "IMPLEMENTATION"),
        ("section", "4.1 Development Environment and Technology Stack"),
        (
            "body",
            "The prototype was verified on a local Windows laptop with Python 3.11.9, Node.js "
            "24.15.0, FastAPI 0.162.7, Pydantic 2.14.3, SQLAlchemy 2.1.8 and scikit-learn 1.9.1. "
            "The frontend uses React 19, TypeScript 5.7 and Vite 6; SQLite is the default, "
            "PostgreSQL is optional, and Playwright 1.56 drives the Chrome tests [1,7-9,11]. Table "
            "4.1 records the stack.",
        ),
        _stack_table(),
        ("section", "4.2 Frontend Implementation"),
        (
            "body",
            "The frontend is a role-aware single-page application. After authentication the "
            "server-assigned role determines navigation: candidates see profiles, opportunities and "
            "applications; recruiters see jobs, candidates, matching and evaluation; auditors see "
            "aggregate reports and events. List state is held in the query string, and unsaved forms "
            "use a confirmation dialog.",
        ),
        (
            "body",
            "The profile editor shows extracted text and warnings before saving; matching shows "
            "score, method, version and component breakdown; application review loads the submitted "
            "snapshot and saved evidence; the audit screen exposes cutoff, counts, rates, intervals "
            "and JSON export.",
        ),
        ("section", "4.3 Backend and Data Implementation"),
        (
            "body",
            "The backend is split into four modules, summarised in Table 4.2. It owns "
            "authentication, profiles, parsing, jobs, applications, matching runs, decisions, "
            "evidence and audit events. An application inserts its row and first version together; a "
            "unique constraint prevents duplicates, and a matching run stores a complete immutable "
            "result. A decision checks the current revision, appends evidence and updates status.",
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
            "Passwords use salted PBKDF2-HMAC-SHA256 with 310,000 iterations. Login stores only a "
            "SHA-256 token hash with an eight-hour expiry and sets an HttpOnly, SameSite=Strict "
            "cookie. Role and ownership checks are server dependencies, and recruiter or auditor "
            "registration needs a single-use invitation bound to the same email and role.",
        ),
        (
            "body",
            "Middleware rejects unapproved mutation origins and sets nosniff, frame-denial and "
            "no-store headers [12]. Original uploads are not retained; retention, deletion, consent "
            "and organisation isolation remain future work, and audit attributes never enter the "
            "matcher.",
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
            "decisions, audit export and mobile layout. These results establish functional behaviour, "
            "not model accuracy or real-world fairness.",
        ),
        ("section", "4.6 Discussion"),
        (
            "body",
            "The default matcher is lexical because TF-IDF is local, deterministic and cheap to "
            "explain; the optional semantic path reduces vocabulary mismatch but adds a dependency "
            "and a less direct explanation. Required coverage dominates the index, so optional "
            "alignment cannot compensate for a missing essential skill. The weights are policy "
            "choices, not learned parameters.",
        ),
        (
            "body",
            "Evidence extraction favours precision: a requirement is supported only by a positive "
            "alias in a relevant context, which avoids inflated coverage but can understate "
            "equivalent experience in unfamiliar words. Expanding aliases and evaluating passage "
            "extraction independently are prerequisites for broader use.",
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
            "Security is proportionate to a local prototype. Opaque session tokens are stored as "
            "hashes, invitations are single-use and email-bound, roles and ownership are enforced on "
            "the server, and uploaded originals are discarded. Organisation isolation, retention "
            "schedules, consent records and administrator recovery remain necessary before "
            "multi-tenant use.",
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
            "These trade-offs keep the prototype honest: it makes a reviewer's reasoning faster to "
            "inspect, not replace it, and each limitation maps to a bounded claim and a future-scope "
            "item.",
        ),
        ("section", "4.7 Threats to Validity"),
        (
            "body",
            "Construct validity is limited by the skill dictionary and context rules. Coverage "
            "measures whether a supported alias appears in a relevant passage, not whether the "
            "candidate can perform the skill. A synonym outside the vocabulary, a project without "
            "the expected tool name, or an unusual negation can change the result. The worked example "
            "shows the arithmetic, but independent relevance judgements are needed to validate the "
            "construct.",
        ),
        (
            "body",
            "Internal validity depends on the verification boundary. The 26 backend tests and nine "
            "browser journeys exercise selected paths against temporary databases and a disposable "
            "server, so they detect integration regressions rather than measure extraction accuracy "
            "or ranking quality. The synthetic evaluation fixture checks that NDCG, recall and "
            "precision are computed and exported, but its profiles and grades were written for this "
            "project and cannot stand in for a benchmark.",
        ),
        (
            "body",
            "External validity is bounded by the local deployment and the synthetic cohort. SQLite "
            "is the verified store, PostgreSQL and container deployment are configuration support "
            "rather than tested deployments, and no real applicant population was available. The "
            "audit report can illustrate selection rates, Wilson intervals and suppression, but it "
            "cannot establish demographic parity, equalized odds or the absence of disparate impact "
            "in a real setting [6,10,13].",
        ),
        (
            "body",
            "These threats define the claims the prototype can support: an inspectable baseline, a "
            "reproducible evidence trail and a verification record explicit about what was tested.",
        ),
    ]

    # Expanded chapter 5.
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
            "properties that a single score can certify. The system is a research instrument for "
            "accountable screening, not a substitute for a hiring decision.",
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
