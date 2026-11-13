from pathlib import Path
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output/pdf/Candidate_Lab_Technology_Stack_and_Use_Cases.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
NAVY = colors.HexColor('#142b40'); TEAL = colors.HexColor('#126c68'); MUTED = colors.HexColor('#526979'); LIGHT = colors.HexColor('#f0f5f7')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX', fontName='Helvetica-Bold', fontSize=28, leading=33, textColor=NAVY, spaceAfter=18))
styles.add(ParagraphStyle(name='SubX', fontName='Helvetica', fontSize=13, leading=19, textColor=MUTED, spaceAfter=16))
styles.add(ParagraphStyle(name='H1X', fontName='Helvetica-Bold', fontSize=21, leading=26, textColor=NAVY, spaceAfter=14))
styles.add(ParagraphStyle(name='H2X', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=TEAL, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name='BodyX', fontName='Helvetica', fontSize=10, leading=15, textColor=NAVY, spaceAfter=8))
styles.add(ParagraphStyle(name='SmallX', fontName='Helvetica', fontSize=8.4, leading=12, textColor=MUTED, spaceAfter=6))
styles.add(ParagraphStyle(name='CellX', fontName='Helvetica', fontSize=8.5, leading=12, textColor=NAVY))
styles.add(ParagraphStyle(name='THX', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.white))
story=[]
def p(text, style='BodyX'): return Paragraph(text, styles[style])
def add(text, style='BodyX'): story.append(p(text, style))
def title(number, text, intro):
    if story: story.append(PageBreak())
    add(f'CANDIDATE LAB  /  {number}', 'SmallX'); add(text, 'H1X'); add(intro, 'SubX')
def section(name, text):
    story.extend([p(name,'H2X'), p(text)])
def table(headers, rows, widths):
    data=[[p(escape(x),'THX') for x in headers]]+[[p(x,'CellX') for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('LINEBELOW',(0,0),(-1,0),1,TEAL)]))
    story.append(t); story.append(Spacer(1,12))

class Architecture(Flowable):
    def __init__(self): Flowable.__init__(self); self.width=491; self.height=290
    def draw(self):
        c=self.canv
        boxes=[(0,232,491,48,'WEB INTERFACE','React + TypeScript + CSS | Candidate / Recruiter / Auditor'),(0,153,491,48,'APPLICATION API','FastAPI + Pydantic + Uvicorn | Validation and access control'),(0,72,237,48,'PROFILE AND MATCHING','pypdf / python-docx | skill rules + TF-IDF'),(254,72,237,48,'PERSISTENCE','SQLAlchemy + SQLite | versioned records'),(0,0,491,40,'OUTPUT','Evidence snapshots | Human review | Aggregate cohort audit')]
        for x,y,w,h,a,b in boxes:
            c.setFillColor(LIGHT); c.setStrokeColor(colors.HexColor('#cad9e1')); c.roundRect(x,y,w,h,6,fill=1,stroke=1)
            c.setFillColor(TEAL); c.setFont('Helvetica-Bold',9); c.drawString(x+12,y+h-17,a)
            c.setFillColor(NAVY); c.setFont('Helvetica',8); c.drawString(x+12,y+12,b)
        c.setStrokeColor(TEAL)
        for x,y1,y2 in [(245,232,201),(118,153,120),(372,153,120),(118,72,40),(372,72,40)]:
            c.line(x,y1,x,y2); c.line(x,y2,x-3,y2+5); c.line(x,y2,x+3,y2+5)

add('TECHNOLOGY STACK &amp; PROJECT USE CASES','SmallX')
story.append(Spacer(1,24))
add('Candidate Lab','TitleX')
add('Fair and Explainable Machine Learning for Automated Candidate Selection and Skill Matching','SubX')
add('Implementation guide for project submission and evaluation','H2X')
add('Prepared 2 November 2026. Based on the implemented source code, dependency manifests and recorded local verification results.')
table(['Area','Current implementation'],[
['Frontend','React, TypeScript, Vite, HTML/CSS and Lucide icons'],
['Backend','Python, FastAPI, Pydantic and Uvicorn'],
['Data','SQLAlchemy with a local SQLite database'],
['Resume processing','pypdf, python-docx, UTF-8 text parsing and skill alias rules'],
['Matching and explanation','scikit-learn TF-IDF, cosine similarity and explicit weighted contributions'],
['Quality assurance','pytest, HTTPX/TestClient, Playwright, TypeScript, ESLint and Prettier'],
['Optional configurations','PostgreSQL/psycopg, Docker Compose and local Sentence Transformers']
],[111,380])
section('What the application does','Candidates supply profile evidence. Recruiters define job criteria, compare profiles and record reasoned reviews. Auditors inspect aggregate cohort comparisons and activity records. Human judgment remains part of the process.')
section('Implementation status','The application runs locally at http://127.0.0.1:8000. It is not a public cloud deployment. The current matching method is a transparent skill-and-TF-IDF baseline, not a trained hiring-outcome classifier.')

title('01','Architecture and request flow','A browser interface talks to a Python API, which processes evidence and stores versioned records locally.')
story.append(Architecture()); story.append(Spacer(1,14))
section('Example: upload a resume','1. React sends the selected file to <b>POST /api/resumes/parse</b> as multipart form data.<br/>2. FastAPI checks the session, role, file type and size.<br/>3. pypdf or python-docx extracts text; the skill dictionary identifies supporting passages.<br/>4. The candidate checks and corrects the preview.<br/>5. <b>POST /api/candidates</b> saves confirmed text through SQLAlchemy into SQLite.')
section('Example: calculate a match','A recruiter calls <b>POST /api/jobs/{id}/runs</b>. The backend loads the job rubric and profiles, calculates skill coverage and text alignment, then stores an immutable result snapshot. The interface shows the ranking, exact contributions and source passages.')
section('Separation of responsibilities','The frontend presents and collects information. The backend enforces permissions and calculations. The database retains records. Audit attributes are stored separately and are not passed into the matching engine.')

title('02','Frontend technologies','These tools create the screens a candidate, recruiter or auditor uses in the browser.')
table(['Technology','Use in this project','Concrete example'],[
['<b>React</b>','Builds reusable components and manages changing screen state.','Profile preview, matching detail panel, registration forms and audit cutoff controls.'],
['<b>TypeScript</b>','Checks frontend data shapes and component inputs during development.','Job, Candidate, Run and Audit types help keep API responses and screens consistent.'],
['<b>Vite</b>','Runs the development server and creates optimized frontend assets.','Development on port 5173 proxies /api to 8000; production assets are built into dist/.'],
['<b>HTML + CSS</b>','Provide page structure, typography, responsive layouts and control states.','Navy navigation, teal actions, mobile cards, keyboard focus and reduced-motion styles.'],
['<b>Lucide React</b>','Provides consistent interface icons.','Briefcase for jobs, users for profiles and a shield for account access.'],
['<b>Fetch API</b>','Sends browser requests to backend JSON endpoints.','api.ts attaches session credentials and converts API errors into readable messages.'],
['<b>Node.js + npm</b>','Install dependencies and run frontend build/test tools.','npm run build performs TypeScript checks and produces the browser bundle.']
],[95,198,198])
section('Important distinction','Node.js is used for frontend tooling and the Docker build stage. The application API itself runs on Python; this project does not use an Express backend.')
section('Main frontend files','<b>src/main.tsx</b>: page navigation, roles and workspace screens.<br/><b>src/Registration.tsx</b>: new-user registration and invitation fields.<br/><b>src/components.tsx</b>: shared forms, buttons, notices, dialogs and pagination.<br/><b>src/api.ts</b>: typed request handling. <b>src/styles.css</b>: visual system and responsive rules.')

title('03','Backend, accounts and access','The server validates incoming data, checks who may access it, performs work and returns results.')
table(['Technology / mechanism','Project use case'],[
['<b>Python</b>','Implements document processing, matching, audit calculations, account handling and the invitation CLI.'],
['<b>FastAPI</b>','Defines HTTP endpoints and dependency-based session/role checks. Also exposes interactive API documentation at /docs.'],
['<b>Pydantic</b>','Validates JSON fields, lengths, allowed role values, skill vocabulary, email format and review reasons. Invalid requests receive validation errors.'],
['<b>Uvicorn</b>','Runs the FastAPI ASGI application and accepts local HTTP requests on port 8000.'],
['<b>python-multipart</b>','Enables uploaded resume files to be read from multipart form requests.'],
['<b>Python standard library</b>','hashlib provides salted PBKDF2 password hashing and token hashing; secrets generates random session/invitation tokens; hmac compares password digests.'],
['<b>Session cookies + role checks</b>','Opaque, HttpOnly, SameSite=Strict cookies identify sessions. Candidate ownership and recruiter/auditor permissions are checked on the server.'],
['<b>Invitation CLI</b>','backend/invite.py issues single-use, expiring invitations bound to a recruiter/auditor email and role. Only invitation hashes are stored.']
],[143,348])
section('Registration and login','Candidates register directly. Recruiters and auditors register with an administrator-generated invitation. Successful registration returns to sign-in; it does not automatically create a session. The app checks password confirmation and duplicate email addresses.')
section('Current boundaries','This local version has no email ownership verification, password recovery service or organization-wide SSO. No public invitation-creation endpoint exists. For HTTPS hosting, secure cookies and approved origins must be configured; the current local setup is not a public deployment.')

title('04','Database and document processing','Storage preserves the history of a review; document tools convert uploaded resumes into text that can be checked.')
table(['Technology','Use case and example'],[
['<b>SQLite - active</b>','Stores the local application database in data/candidate-lab.db. Requires no separate database server.'],
['<b>SQLAlchemy - active</b>','Maps Python model classes to database tables and performs queries/transactions. Used for profiles, jobs, versions, snapshots and reviews.'],
['<b>pypdf - active</b>','Extracts text from supported, unencrypted text PDFs. Scanned images need OCR outside this version.'],
['<b>python-docx - active</b>','Extracts text from Word paragraphs and table cells in DOCX resumes.'],
['<b>UTF-8 text parsing - active</b>','Reads TXT resumes without an additional document library.'],
['<b>Python re / skill dictionary - active</b>','Matches supported skill aliases to passages, such as pytest to Testing or PostgreSQL to SQL. This is rules-based extraction, not a trained NER model.'],
['<b>PostgreSQL + psycopg - optional</b>','Alternative database configuration for a server deployment through DATABASE_URL. Configuration is supplied; a PostgreSQL deployment was not verified locally.']
],[152,339])
section('What is stored','Users, hashed sessions, registration invitations, jobs, profiles, profile versions, matching runs, review decisions, separate audit attributes and application audit events. The recruiter overview queries actual database counts for jobs, profiles, runs and review records.')
section('Why versions and snapshots matter','A corrected profile receives a new version. Existing matching runs keep their original rubric, profile version, passages and score contributions. An old explanation therefore remains understandable after a profile changes.')
section('Upload handling','The parser accepts PDF, DOCX and TXT files up to 2 MB. PDF page/encryption checks and DOCX expanded-size checks limit processing. Original uploaded files are not retained; only saved profile text is persisted. These limits are not a malware sandbox.')

title('05','Matching, explanation and fairness audit','The current implementation makes its formula visible. It does not claim to predict employee performance.')
table(['Technology / method','Use in the implementation'],[
['<b>scikit-learn TF-IDF</b>','Converts job skill terms and recognized skill-bearing profile passages into weighted text vectors. Uses word unigrams/bigrams and sublinear term frequency.'],
['<b>Cosine similarity</b>','Measures lexical alignment between the job-skill vector and each profile vector. It contributes up to 25 points.'],
['<b>Explicit skill coverage</b>','Counts requirements with matching passages. Required coverage contributes up to 60 points; preferred coverage contributes up to 15.'],
['<b>Exact score contributions</b>','Shows each formula term and its supporting evidence. These are direct arithmetic explanations, not SHAP or LIME results.'],
['<b>Python audit arithmetic</b>','Calculates cohort counts, simulated selection rates, maximum-minus-minimum rate difference and 95% Wilson intervals. Rates are suppressed below five records.'],
['<b>NumPy</b>','Imported numerical support; used for clipping/vector arithmetic when the optional semantic path is enabled. It is a scikit-learn dependency in the baseline environment.'],
['<b>Sentence Transformers - optional</b>','A separately installed, locally cached embedding model can replace lexical alignment with semantic alignment. Disabled in the verified default setup.']
],[153,338])
section('Formula','<b>Score = 60 x required coverage + 15 x preferred coverage + 25 x text alignment.</b><br/>If no preferred skills are defined, the weights become 75 / 0 / 25. All component values are between 0 and 1. For example, 1.0 required coverage, 1.0 preferred coverage and 0.10 alignment produce 77.5 points.')
section('What the result means','The score is an experimental matching index, not a hiring probability. TF-IDF is fitted per run, so changing the candidate corpus can change alignment scores. Skill mentions can be exaggerated or negated; a person must inspect the passage and assess competence.')
section('Audit interpretation','The supplied Cohort A/B labels are arbitrary synthetic fixtures, not inferred demographics. New profiles do not receive guessed group labels. No real qualification labels were supplied, so TPR/FPR, equalized odds and real demographic fairness have not been validated.')

title('06','Testing, tooling and deployment','Quality tools check application behavior; packaging tools prepare it for a reproducible environment.')
table(['Tool','Use case'],[
['<b>pytest</b>','Runs backend integration/model tests with isolated temporary databases. Recorded result: 10 tests passed.'],
['<b>HTTPX + FastAPI TestClient</b>','Exercise API requests without a separately hosted server: authentication, role restrictions, uploads, registration, versions and score arithmetic.'],
['<b>Playwright + Chrome</b>','Checks complete browser journeys: register each role, sign in, upload/correct profiles, run matching, review evidence and export audit JSON. Recorded result: 7 journeys passed.'],
['<b>TypeScript compiler</b>','Checks frontend types before the production build.'],
['<b>ESLint + typescript-eslint</b>','Checks JavaScript/TypeScript code for common errors and consistency issues.'],
['<b>Prettier</b>','Formats frontend source consistently.'],
['<b>PowerShell + Python venv</b>','Provides Windows startup commands and an isolated Python dependency environment.'],
['<b>Docker / Compose - optional</b>','Supplies a multi-stage Node/Python container build and a private PostgreSQL service configuration. These files do not mean the app is already deployed online.']
],[153,338])
section('Recorded verification status','Build, TypeScript checks and ESLint passed. Backend coverage includes invitation expiry/role binding, profile ownership, upload validation, immutable snapshots, conflict protection and database-backed totals. Browser coverage includes registration, matching, reviews and responsive layouts. These are functional checks, not ML accuracy metrics or a complete accessibility/security certification.')
section('How the local runtime works','Vite builds React into static files in dist/. FastAPI serves those files and the /api endpoints through Uvicorn on 127.0.0.1:8000. SQLite stores data on the laptop. The loopback address is not a public link and cannot be shared with friends as an internet deployment.')

title('07','Feature-to-stack map and viva notes','Use these examples to explain which technology does what during evaluation.')
table(['Project feature','Technologies involved'],[
['Candidate registration','React form + Pydantic validation + FastAPI + PBKDF2 password hashing + SQLAlchemy/SQLite.'],
['Recruiter/auditor invitation','Python CLI + secrets-generated code + hashed invitation record + transactional, single-use redemption.'],
['Resume upload and correction','React multipart form + FastAPI + python-multipart + pypdf/python-docx + skill rules + profile versions.'],
['Job creation','React/TypeScript + supported skill vocabulary + Pydantic + SQLAlchemy.'],
['Matching and explanation','Skill evidence + scikit-learn TF-IDF/cosine similarity + weighted formula + immutable database snapshot.'],
['Human review','React review panel + validated reason/status + append-only review records + audit event.'],
['Auditor dashboard','Role-restricted FastAPI endpoint + separate synthetic attributes + rate/Wilson calculations + React charts + JSON export.'],
['Recruiter overview','SQLAlchemy counts of saved jobs/profiles/runs/reviews + typed API response + responsive React cards.']
],[151,340])
section('A short explanation to present','"Our React and TypeScript interface connects to a Python FastAPI server and SQLite storage. Resume parsers extract text; skill rules and TF-IDF calculate explainable matches. Recruiters review the evidence, and auditors examine separate aggregate comparisons."')
section('Do not claim these as implemented','A trained hiring classifier, SHAP/LIME explanations, OCR, a hosted LLM, Redis/Celery queues, automatic hiring/rejection, email verification, multi-tenant organization isolation or public cloud hosting. Docker, PostgreSQL and semantic embeddings are optional configurations; no independent real-world accuracy/fairness result is established.')
section('Implementation references','Sources reviewed: package.json, requirements*.txt; backend/app.py, matching.py and invite.py; src/; Dockerfile, compose.yaml and vite.config.ts; tests/, VERIFICATION.md, README.md and EVALUATION.md. Dependency ranges/lockfiles govern versions; exact installed patch versions are not claimed here.')

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#d4dfe6')); canvas.line(52,42,A4[0]-52,42)
    canvas.setFont('Helvetica',8); canvas.setFillColor(MUTED)
    canvas.drawString(52,28,'Candidate Lab | Technology stack and implementation guide')
    canvas.drawRightString(A4[0]-52,28,str(doc.page))
doc=SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=52,leftMargin=52,topMargin=45,bottomMargin=57,title='Candidate Lab - Technology Stack and Use Cases',author='Candidate Lab',subject='Implemented technology responsibilities and project workflows')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
