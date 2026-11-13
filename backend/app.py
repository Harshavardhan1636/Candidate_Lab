import hashlib
import hmac
import io
import os
import re
import secrets
import time
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import JSON, Boolean, Integer, String, Text, create_engine, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, object_session
from sqlalchemy.exc import IntegrityError

from .matching import SKILLS, extract, fairness, rank, matching_config
from .naming import SAMPLE_PROFILES, job_name, profile_name

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
DEMO = os.getenv("DEMO_MODE", "0") == "1"
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{(DATA / 'candidate-lab.db').as_posix()}")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {}, pool_pre_ping=True)

def now():
    return datetime.now(timezone.utc).isoformat()

def uid():
    return secrets.token_hex(12)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    role: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(Text)

class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(40))
    expires: Mapped[int] = mapped_column(Integer)

class Invitation(Base):
    __tablename__ = "registration_invitations"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20))
    expires: Mapped[int] = mapped_column(Integer)
    used: Mapped[bool] = mapped_column(Boolean, default=False)

def normalize_email(value):
    value = value.strip().lower()
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}", value) or '..' in value:
        raise ValueError("Enter a valid email address.")
    return value

def create_invitation(session, email, role_name, hours=24):
    email = normalize_email(email)
    if role_name not in {"recruiter", "auditor"} or not 1 <= hours <= 168:
        raise ValueError("Choose recruiter/auditor and an expiry between 1 and 168 hours.")
    if session.scalar(select(User).where(User.email == email)):
        raise ValueError("An account already exists for that email.")
    token = secrets.token_urlsafe(32)
    session.add(Invitation(token_hash=hashlib.sha256(token.encode()).hexdigest(), email=email, role=role_name, expires=int(time.time())+hours*3600))
    session.add(AuditLog(actor_id="local-administrator", action="Created registration invitation: " + role_name, object_id=hashlib.sha256(email.encode()).hexdigest()[:24]))
    session.commit()
    return token

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    required: Mapped[list] = mapped_column(JSON)
    preferred: Mapped[list] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created: Mapped[str] = mapped_column(String(40), default=now)

class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(String(40))
    label: Mapped[str] = mapped_column(String(80))
    text: Mapped[str] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(JSON)
    warnings: Mapped[list] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    updated: Mapped[str] = mapped_column(String(40), default=now)

class ProfileVersion(Base):
    __tablename__ = "profile_versions"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    candidate_id: Mapped[str] = mapped_column(String(40))
    version: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    created: Mapped[str] = mapped_column(String(40), default=now)

class AuditAttribute(Base):
    __tablename__ = "audit_attributes"
    candidate_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    group: Mapped[str] = mapped_column(String(40))
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)

class Run(Base):
    __tablename__ = "matching_runs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(String(40))
    job_snapshot: Mapped[dict] = mapped_column(JSON)
    method: Mapped[str] = mapped_column(String(80))
    results: Mapped[list] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(String(40), default=now)

class Review(Base):
    __tablename__ = "review_decisions"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(String(40))
    candidate_id: Mapped[str] = mapped_column(String(40))
    reviewer_id: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text)
    created: Mapped[str] = mapped_column(String(40), default=now)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    actor_id: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(80))
    object_id: Mapped[str] = mapped_column(String(40))
    created: Mapped[str] = mapped_column(String(40), default=now)

def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310000).hex()
    return salt + ":" + digest

def check_password(value, stored):
    salt = stored.split(":")[0]
    return hmac.compare_digest(password_hash(value, salt), stored)

def db():
    with Session(engine) as session:
        yield session

def audit(session, actor, action, object_id):
    session.add(AuditLog(actor_id=actor.id, action=action, object_id=object_id))

def current_user(request: Request, session: Session = Depends(db)):
    raw = request.cookies.get("candidate_session", "")
    token = session.get(LoginSession, hashlib.sha256(raw.encode()).hexdigest()) if raw else None
    user = session.get(User, token.user_id) if token and token.expires > time.time() else None
    if not user:
        raise HTTPException(401, "Sign in to continue.")
    return user

def role(*roles):
    def dependency(user: User = Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Your role cannot access this resource.")
        return user
    return dependency

def job_out(j):
    return {"id": j.id, "title": j.title, "description": j.description, "required": j.required, "preferred": j.preferred, "version": j.version, "created": j.created}

def candidate_out(c, full=False):
    result = {"id": c.id, "label": c.label, "skills": c.skills, "warnings": c.warnings, "version": c.version, "synthetic": c.synthetic, "updated": c.updated}
    if full:
        result["text"] = c.text
    return result

def run_out(r, full=False):
    session=object_session(r)
    j=session.get(Job,r.job_id) if session else None
    snapshot={**r.job_snapshot,'title':j.title if j else job_name(r.job_snapshot['title'])}
    result = {"id": r.id, "job_id": r.job_id, "job_snapshot": snapshot, "method": r.method, "created": r.created, "candidate_count": len(r.results)}
    if full:
        result['results']=[]
        for row in r.results:
            c=session.get(Candidate,row['candidate_id']) if session else None
            result['results'].append({**row,'candidate_label':c.label if c else profile_name(row['candidate_label'])})
    return result

def seed(session):
    if session.scalar(select(func.count()).select_from(User)):
        return
    users = [User(email=f"{r}@demo.test", role=r, password=password_hash(p)) for r, p in [("recruiter", "RecruiterDemo!2026"), ("auditor", "AuditorDemo!2026"), ("candidate", "CandidateDemo!2026")]]
    session.add_all(users)
    session.flush()
    jobs = [Job(title="Backend Engineer", description="Build reliable Python services and document REST APIs. Work with a team to test, deploy and maintain PostgreSQL-backed applications.", required=["Python", "SQL", "REST APIs", "Testing"], preferred=["FastAPI", "Docker", "Git"]),
            Job(title="Frontend Engineer", description="Build accessible web interfaces and maintain a tested component system.", required=["React", "TypeScript", "HTML", "CSS"], preferred=["Testing", "Git"]),
            Job(title="Data Analyst", description="Investigate product questions and communicate findings with clear visual evidence.", required=["SQL", "Pandas", "Statistics"], preferred=["Python", "Data Visualization", "Excel"])]
    session.add_all(jobs)
    samples = [
        "Built REST APIs with Python and FastAPI for an inventory service. Wrote pytest integration tests and used PostgreSQL. Containerized the service with Docker and maintained Git workflows.",
        "Developed Python ETL pipelines using SQL and PostgreSQL. Added unit tests for data validation. Used Git for reviews and wrote technical documentation.",
        "Designed a React and TypeScript dashboard with HTML and CSS. Added testing for accessible forms and maintained Git history. Integrated REST APIs into the interface.",
        "Analyzed retail data with SQL, Pandas and Python. Used statistics for hypothesis testing and built data visualization reports with Tableau. Automated Excel exports.",
        "Built Python web services with Django and REST APIs. Added unit testing and used MySQL. Maintained Docker deployment scripts and Git branches.",
        "Created a Java and Spring Boot order service with SQL and REST APIs. Practiced integration tests and wrote technical documentation using Git.",
        "Developed a machine learning project with Python, Pandas, NumPy and scikit-learn. Validated statistics and displayed results with matplotlib. Added pytest tests.",
        "Built a React product page using JavaScript, HTML and CSS. Used Git. Documented component behavior and communication with the design team.",
        "Built Python REST APIs with FastAPI and SQL. Added pytest tests and Git workflows. Deployed a Docker container and used PostgreSQL for storage.",
        "Created SQL analysis queries and Excel reports. Used statistics and data visualization to explain product changes. Maintained technical documentation.",
        "Designed TypeScript and React forms with CSS and HTML. Added unit tests and Git reviews. Integrated Node.js REST APIs.",
        "Developed Python services and SQL migration scripts. Built REST endpoints and integration tests. Used FastAPI with PostgreSQL and Docker.",
    ]
    for i, text in enumerate(samples):
        c = Candidate(owner_id=users[2].id if i == 0 else users[0].id, label=SAMPLE_PROFILES[i], text=text, skills=extract(text)["skills"], warnings=[], synthetic=True)
        session.add(c)
        session.flush()
        session.add(ProfileVersion(candidate_id=c.id, version=1, text=text))
        session.add(AuditAttribute(candidate_id=c.id, group="Cohort A" if i % 2 == 0 else "Cohort B"))
    session.commit()
    people = session.scalars(select(Candidate).order_by(Candidate.label)).all()
    results, method = rank(jobs[0], people)
    session.add(Run(job_id=jobs[0].id, job_snapshot=job_out(jobs[0]), results=results, method=method))
    audit(session, users[0], "Synthetic workspace initialized", jobs[0].id)
    session.commit()

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    if DEMO:
        with Session(engine) as session:
            seed(session)
    yield

app = FastAPI(title="Candidate Lab", version="0.2.0", lifespan=lifespan)
origins = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:8000,http://localhost:8000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type"])

@app.middleware("http")
async def boundaries(request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        if origin and origin not in origins:
            return JSONResponse({"detail": "Request origin is not allowed."}, status_code=403)
        length = request.headers.get("content-length")
        if length and int(length) > 3 * 1024 * 1024:
            return JSONResponse({"detail": "Request exceeds the 3 MB limit."}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store"
    return response

class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=1, max_length=200)

# Per-process bounded demo throttle. Production requires a shared identity service.
attempts = {}

class RegisterIn(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=12, max_length=128)
    confirm_password: str = Field(max_length=128)
    role: Literal["candidate", "recruiter", "auditor"] = "candidate"
    invitation_code: str = Field(default="", max_length=200)

    @field_validator("email")
    @classmethod
    def email_format(cls, value):
        return normalize_email(value)

@app.post("/api/auth/register", status_code=201)
def register(body: RegisterIn, request: Request, session: Session = Depends(db)):
    address = "registration:" + (request.client.host if request.client else "local")
    attempts[address] = [t for t in attempts.get(address, []) if t > time.time()-60]
    if len(attempts[address]) >= 10:
        raise HTTPException(429, "Too many registration attempts. Try again in a minute.")
    attempts[address].append(time.time())
    if body.password != body.confirm_password:
        raise HTTPException(422, "Passwords do not match.")
    if not any(c.isalpha() for c in body.password) or not any(c.isdigit() for c in body.password) or body.password != body.password.strip():
        raise HTTPException(422, "Use at least 12 characters with a letter and a number, without leading or trailing spaces.")
    if session.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(409, "An account already exists for this email. Sign in instead.")
    if body.role != "candidate":
        consumed = session.execute(update(Invitation).where(
            Invitation.token_hash == hashlib.sha256(body.invitation_code.strip().encode()).hexdigest(),
            Invitation.email == body.email, Invitation.role == body.role,
            Invitation.expires > int(time.time()), Invitation.used == False
        ).values(used=True))
        if consumed.rowcount != 1:
            raise HTTPException(403, "This invitation is invalid, expired, already used, or belongs to another email or role.")
    user = User(email=body.email, role=body.role, password=password_hash(body.password))
    session.add(user)
    try:
        session.flush()
        audit(session, user, "Registered account: " + body.role, user.id)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "An account already exists for this email. Sign in instead.")
    return {"message": "Account created. Sign in with your new credentials.", "email": user.email, "role": user.role}

@app.post("/api/auth/login")
def login(body: LoginIn, request: Request, response: Response, session: Session = Depends(db)):
    address = request.client.host if request.client else "local"
    cutoff = time.time() - 60
    attempts[address] = [t for t in attempts.get(address, []) if t > cutoff]
    if len(attempts[address]) >= 20:
        raise HTTPException(429, "Too many sign-in attempts. Try again in a minute.")
    attempts[address].append(time.time())
    user = session.scalar(select(User).where(User.email == body.email.strip().lower()))
    if not user or not check_password(body.password, user.password):
        raise HTTPException(401, "Email or password is incorrect.")
    token = secrets.token_urlsafe(40)
    session.add(LoginSession(token_hash=hashlib.sha256(token.encode()).hexdigest(), user_id=user.id, expires=int(time.time())+8*3600))
    audit(session, user, "Signed in", user.id)
    session.commit()
    response.set_cookie("candidate_session", token, httponly=True, samesite="strict", secure=os.getenv("COOKIE_SECURE", "0") == "1", max_age=8*3600, path="/")
    return {"id": user.id, "email": user.email, "role": user.role}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}

@app.post("/api/auth/logout")
def logout(request: Request, response: Response, user: User = Depends(current_user), session: Session = Depends(db)):
    raw = request.cookies.get("candidate_session", "")
    record = session.get(LoginSession, hashlib.sha256(raw.encode()).hexdigest())
    if record:
        session.delete(record)
    session.commit()
    response.delete_cookie("candidate_session", path="/")
    return {"ok": True}

@app.get("/api/health")
def health(session: Session = Depends(db)):
    session.execute(select(1))
    return {"status": "ok", "demo": DEMO, "version": "0.2.0", "semantic_configured": bool(os.getenv("SEMANTIC_MODEL_PATH"))}

@app.get("/api/skills")
def skills(user: User = Depends(current_user)):
    return sorted(SKILLS)

@app.get("/api/overview")
def overview(user: User = Depends(role("recruiter")), session: Session = Depends(db)):
    counts = {name: session.scalar(select(func.count()).select_from(model)) for name, model in [("jobs", Job), ("profiles", Candidate), ("runs", Run), ("reviews", Review)]}
    counts["sample_profiles"] = session.scalar(select(func.count()).select_from(Candidate).where(Candidate.synthetic == True))
    return counts

class JobIn(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=20, max_length=5000)
    required: list[str] = Field(min_length=1, max_length=20)
    preferred: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("title", "description", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("required", "preferred")
    @classmethod
    def valid_skills(cls, values):
        catalog = {k.casefold(): k for k in SKILLS}
        unknown = [v for v in values if v.strip().casefold() not in catalog]
        if unknown:
            raise ValueError("Use skills from the supported vocabulary: " + ", ".join(catalog.values()))
        unique = list(dict.fromkeys(catalog[v.strip().casefold()] for v in values))
        return unique

@app.get("/api/jobs")
def jobs(page: int = Query(1, ge=1), q: str = Query("", max_length=100), user: User = Depends(role("recruiter", "auditor")), session: Session = Depends(db)):
    query = select(Job).where(Job.title.ilike(f"%{q}%")).order_by(Job.created.desc(), Job.id)
    count = session.scalar(select(func.count()).select_from(query.subquery()))
    return {"items": [job_out(j) for j in session.scalars(query.offset((page-1)*10).limit(10))], "total": count}

@app.post("/api/jobs", status_code=201)
def create_job(body: JobIn, user: User = Depends(role("recruiter")), session: Session = Depends(db)):
    if not body.required:
        raise HTTPException(422, "Add at least one required skill.")
    if set(x.casefold() for x in body.required) & set(x.casefold() for x in body.preferred):
        raise HTTPException(422, "A skill cannot be both required and preferred.")
    j = Job(**body.model_dump())
    session.add(j)
    session.flush()
    audit(session, user, "Created job rubric", j.id)
    session.commit()
    return job_out(j)

@app.get("/api/candidates")
def candidates(page: int = Query(1, ge=1), q: str = Query("", max_length=100), user: User = Depends(role("recruiter", "candidate")), session: Session = Depends(db)):
    query = select(Candidate).where(Candidate.label.ilike(f"%{q}%"))
    if user.role == "candidate":
        query = query.where(Candidate.owner_id == user.id)
    query = query.order_by(Candidate.updated.desc(), Candidate.id)
    count = session.scalar(select(func.count()).select_from(query.subquery()))
    return {"items": [candidate_out(c) for c in session.scalars(query.offset((page-1)*10).limit(10))], "total": count}

def owned_candidate(session, ident, user):
    c = session.get(Candidate, ident)
    if c is None:
        raise HTTPException(404, "Profile not found.")
    if user.role != "recruiter" and c.owner_id != user.id:
        raise HTTPException(403, "You can only access your own profile.")
    return c

@app.get("/api/candidates/{ident}")
def candidate(ident: str, user: User = Depends(role("recruiter", "candidate")), session: Session = Depends(db)):
    return candidate_out(owned_candidate(session, ident, user), True)

class ProfileIn(BaseModel):
    label: str = Field(min_length=3, max_length=80)
    text: str = Field(min_length=40, max_length=30000)
    version: int | None = None

    @field_validator("label", "text", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value

@app.post("/api/extract")
def preview_text(body: ProfileIn, user: User = Depends(role("recruiter", "candidate"))):
    return extract(body.text)

@app.post("/api/resumes/parse")
async def parse_resume(file: UploadFile = File(...), user: User = Depends(role("recruiter", "candidate"))):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(415, "Upload a text PDF, DOCX or UTF-8 TXT file.")
    content = await file.read(2 * 1024 * 1024 + 1)
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(413, "File exceeds the 2 MB limit.")
    try:
        if suffix == ".pdf":
            from pypdf import PdfReader
            if not content.startswith(b"%PDF"):
                raise ValueError("PDF signature is missing.")
            reader = PdfReader(io.BytesIO(content))
            if reader.is_encrypted or len(reader.pages) > 50:
                raise ValueError("Use an unencrypted document of at most 50 pages.")
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
        elif suffix == ".docx":
            from docx import Document
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                if sum(i.file_size for i in archive.infolist()) > 20 * 1024 * 1024:
                    raise ValueError("Expanded document is too large.")
            doc = Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs] + [cell.text for t in doc.tables for row in t.rows for cell in row.cells])
        else:
            text = content.decode("utf-8-sig")
        if len(text.strip()) < 40:
            raise ValueError("No usable text found. Scanned PDFs need OCR; paste or correct the text instead.")
        if len(text) > 30000:
            raise ValueError("Extracted text exceeds 30,000 characters. Use a shorter resume.")
    except Exception as exc:
        raise HTTPException(422, "Could not parse this document. Use an unencrypted text PDF, DOCX or TXT, or paste its text.") from exc
    return extract(text)

@app.post("/api/candidates", status_code=201)
def create_candidate(body: ProfileIn, user: User = Depends(role("candidate")), session: Session = Depends(db)):
    data = extract(body.text)
    c = Candidate(owner_id=user.id, label=body.label.strip(), text=body.text, skills=data["skills"], warnings=data["warnings"])
    session.add(c)
    session.flush()
    session.add(ProfileVersion(candidate_id=c.id, version=1, text=c.text))
    audit(session, user, "Created candidate profile", c.id)
    session.commit()
    return candidate_out(c, True)

@app.put("/api/candidates/{ident}")
def update_candidate(ident: str, body: ProfileIn, user: User = Depends(role("candidate")), session: Session = Depends(db)):
    c = owned_candidate(session, ident, user)
    if body.version != c.version:
        raise HTTPException(409, "This profile changed. Reload before saving to avoid overwriting a newer version.")
    data = extract(body.text)
    changed = session.execute(update(Candidate).where(Candidate.id == ident, Candidate.version == body.version).values(
        label=body.label.strip(), text=body.text, skills=data["skills"], warnings=data["warnings"], version=body.version+1, updated=now()
    ))
    if changed.rowcount != 1:
        raise HTTPException(409, "This profile changed. Reload before saving.")
    session.refresh(c)
    session.add(ProfileVersion(candidate_id=c.id, version=c.version, text=c.text))
    audit(session, user, "Corrected candidate profile", c.id)
    session.commit()
    return candidate_out(c, True)

@app.post("/api/jobs/{ident}/runs", status_code=201)
def start_run(ident: str, method: Literal['tfidf', 'semantic'] = Query('tfidf'), user: User = Depends(role("recruiter")), session: Session = Depends(db)):
    j = session.get(Job, ident)
    if not j:
        raise HTTPException(404, "Job not found.")
    from .advanced import submitted_profiles
    people = submitted_profiles(session, ident)
    if not people:
        raise HTTPException(422, "No active applications for this job. Publish it and ask candidates to apply first.")
    if len(people) > 500:
        raise HTTPException(422, "This research build supports at most 500 profiles per run. Add a durable worker before scaling.")
    try:
        results, method_name = rank(j, people, method)
    except Exception as exc:
        raise HTTPException(503, "The configured local model could not load. Check SEMANTIC_MODEL_PATH or use the TF-IDF baseline.") from exc
    r = Run(job_id=j.id, job_snapshot={**job_out(j), 'scope': 'active_applications', 'application_ids': [p.application_id for p in people], 'matching_config':matching_config(method)}, results=results, method=method_name)
    session.add(r)
    session.flush()
    audit(session, user, "Completed matching snapshot", r.id)
    session.commit()
    return run_out(r, True)

@app.get("/api/runs")
def runs(user: User = Depends(role("recruiter", "auditor")), session: Session = Depends(db)):
    return [run_out(r) for r in session.scalars(select(Run).order_by(Run.created.desc()).limit(100))]

@app.get("/api/runs/{ident}")
def get_run(ident: str, user: User = Depends(role("recruiter")), session: Session = Depends(db)):
    r = session.get(Run, ident)
    if not r:
        raise HTTPException(404, "Run not found.")
    output = run_out(r, True)
    decisions = session.scalars(select(Review).where(Review.run_id == ident).order_by(Review.created)).all()
    latest = {d.candidate_id: {"status": d.status, "reason": d.reason, "created": d.created} for d in decisions}
    output["results"] = [{**row, "review": latest.get(row["candidate_id"])} for row in output["results"]]
    return output

class ReviewIn(BaseModel):
    candidate_id: str
    status: Literal["needs_review", "shortlisted", "more_information"]
    reason: str = Field(min_length=10, max_length=2000)

    @field_validator("reason")
    @classmethod
    def substantive_reason(cls, value):
        if len(value.strip()) < 10:
            raise ValueError("Record a substantive job-related reason of at least 10 characters.")
        return value.strip()

@app.post("/api/runs/{ident}/reviews", status_code=201)
def add_review(ident: str, body: ReviewIn, user: User = Depends(role("recruiter")), session: Session = Depends(db)):
    r = session.get(Run, ident)
    if not r or not any(c["candidate_id"] == body.candidate_id for c in r.results):
        raise HTTPException(404, "Matching result not found.")
    session.add(Review(run_id=ident, reviewer_id=user.id, **body.model_dump()))
    audit(session, user, "Recorded human review: " + body.status, body.candidate_id)
    session.commit()
    return {"ok": True}

@app.get("/api/audit/fairness/{ident}")
def fairness_report(ident: str, threshold: float = Query(60, ge=0, le=100), user: User = Depends(role("auditor")), session: Session = Depends(db)):
    r = session.get(Run, ident)
    if not r:
        raise HTTPException(404, "Run not found.")
    attrs = session.scalars(select(AuditAttribute).where(AuditAttribute.synthetic == True)).all()
    report = fairness(r.results, {a.candidate_id: a.group for a in attrs}, threshold)
    report.update({"run_id": r.id, "job_title": r.job_snapshot["title"], "method": r.method, "created": now()})
    audit(session, user, "Viewed aggregate fairness report", r.id)
    session.commit()
    return report

@app.get("/api/audit/events")
def events(page: int = Query(1, ge=1), user: User = Depends(role("auditor")), session: Session = Depends(db)):
    count = session.scalar(select(func.count()).select_from(AuditLog))
    logs = session.scalars(select(AuditLog).order_by(AuditLog.created.desc()).offset((page-1)*10).limit(10))
    return {"items": [{"id": a.id, "action": a.action, "object_id": a.object_id, "created": a.created} for a in logs], "total": count}

from . import advanced  # Registers additive tables and new endpoints before startup.

if (ROOT / "dist" / "assets").exists():
    app.mount("/assets", StaticFiles(directory=ROOT / "dist" / "assets"), name="assets")

@app.get("/", include_in_schema=False)
def frontend():
    if (ROOT / "dist" / "index.html").exists():
        return FileResponse(ROOT / "dist" / "index.html")
    return {"message": "Start the frontend with npm run dev, or build it with npm run build.", "docs": "/docs"}
