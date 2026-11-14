import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from backend import app as module
from backend.matching import fairness, safe_scoring_text

TEXT = "Built Python REST APIs with FastAPI and PostgreSQL. Added pytest integration tests and deployed Docker services using Git."

@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}", connect_args={"check_same_thread": False})
    monkeypatch.setattr(module, "engine", engine)
    monkeypatch.setattr(module, "DEMO", True)
    module.attempts.clear()
    with TestClient(module.app) as client:
        yield client
    engine.dispose()

def login(client, role="recruiter"):
    response = client.post("/api/auth/login", json={"email": f"{role}@demo.test", "password": f"{role.title()}Demo!2026"})
    assert response.status_code == 200

def test_auth_and_role_boundaries(client):
    assert client.get("/api/jobs").status_code == 401
    assert client.post("/api/auth/login", json={"email": "recruiter@demo.test", "password": "bad"}).status_code == 401
    login(client, "candidate")
    assert client.get("/api/jobs").status_code == 403
    own = client.get("/api/candidates").json()
    assert own["total"] == 1
    with Session(module.engine) as session:
        other = session.scalar(select(module.Candidate).where(module.Candidate.label == "Python Developer - Data Pipelines"))
        assert client.get(f"/api/candidates/{other.id}").status_code == 403
    assert client.get("/api/runs").status_code == 403
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    login(client, "auditor")
    assert client.get("/api/candidates").status_code == 403
    run = client.get("/api/runs").json()[0]
    assert "results" not in run
    assert client.get(f"/api/runs/{run['id']}").status_code == 403
    assert client.post("/api/jobs", json={}).status_code == 403

def test_complete_matching_and_snapshot_flow(client):
    login(client)
    job_data = {"title": "Test engineer", "description": "Develop reliable backend services and integration tests.", "required": ["python", "SQL"], "preferred": ["FastAPI"]}
    response = client.post("/api/jobs", json=job_data)
    assert response.status_code == 201
    job = response.json()
    assert job["required"] == ["Python", "SQL"]
    loaded = client.get(f"/api/jobs/{job['id']}")
    assert loaded.status_code == 200 and loaded.json()["version"] == 1
    updated_job = {**job_data, "title": "Test engineer II", "version": 1}
    edited = client.put(f"/api/jobs/{job['id']}", json=updated_job)
    assert edited.status_code == 200 and edited.json()["version"] == 2
    assert edited.json()["title"] == "Test engineer II"
    assert client.put(f"/api/jobs/{job['id']}", json=updated_job).status_code == 409
    assert client.put("/api/jobs/missing", json=updated_job).status_code == 404
    assert client.put(f"/api/jobs/{job['id']}/publication", json={'published':True}).status_code == 200
    login(client, 'candidate')
    profile = client.post("/api/candidates", json={"label": "Test profile", "text": TEXT}).json()
    assert profile["version"] == 1
    assert client.put(f"/api/jobs/{job['id']}", json={**updated_job, "version": 2}).status_code == 403
    assert client.post(f"/api/jobs/{job['id']}/applications", json={'candidate_id':profile['id']}).status_code == 201
    login(client)
    assert client.get(f"/api/jobs/{job['id']}").json()["version"] == 2
    result = client.post(f"/api/jobs/{job['id']}/runs")
    assert result.status_code == 201
    run = result.json()
    row = next(r for r in run["results"] if r["candidate_id"] == profile["id"])
    assert row["profile_version"] == 1
    assert all(x["matched"] for x in row["requirements"])
    assert abs(sum(c["contribution"] for c in row["components"]) - row["score"]) < .011
    assert 0 <= row["score"] <= 100
    assert "Cohort" not in str(row)
    body = {"label": profile["label"], "text": "Built React and TypeScript interfaces with HTML and CSS. Used Git and automated unit tests.", "version": 1}
    assert client.put(f"/api/candidates/{profile['id']}", json=body).status_code == 403
    assert client.post("/api/candidates", json={"label": "Unauthorized profile", "text": TEXT}).status_code == 403
    assert client.get(f"/api/candidates/{profile['id']}").status_code == 200
    login(client, "candidate")
    assert client.put(f"/api/candidates/{profile['id']}", json=body).json()["version"] == 2
    assert client.put(f"/api/candidates/{profile['id']}", json=body).status_code == 409
    login(client)
    saved = client.get(f"/api/runs/{run['id']}").json()
    assert next(r for r in saved["results"] if r["candidate_id"] == profile["id"])["profile_snapshot"] == row["profile_snapshot"]
    review = {"candidate_id": profile["id"], "status": "shortlisted", "reason": "Evidence of the required Python and SQL skills warrants further human review."}
    assert client.post(f"/api/runs/{run['id']}/reviews", json={**review, "reason": "short"}).status_code == 422
    assert client.post(f"/api/runs/{run['id']}/reviews", json=review).status_code == 201
    reviewed = next(r for r in client.get(f"/api/runs/{run['id']}").json()["results"] if r["candidate_id"] == profile["id"])
    assert reviewed["review"]["status"] == "shortlisted"
    assert reviewed["score"] == row["score"]
    login(client, "auditor")
    report = client.get(f"/api/audit/fairness/{run['id']}").json()
    assert report["unattributed_count"] == 1
    assert report['audited_count'] == 0
    assert not any("candidate_id" in g for g in report["groups"])
    assert client.get("/api/audit/events").json()["total"] > 0

def test_uploads_and_validation(client):
    login(client)
    good = client.post("/api/resumes/parse", files={"file": ("resume.txt", TEXT.encode(), "text/plain")})
    assert good.status_code == 200
    assert "Python" in [s["skill"] for s in good.json()["skills"]]
    assert "REST APIs" in [s["skill"] for s in good.json()["skills"]]
    from docx import Document
    doc = Document(); doc.add_paragraph(TEXT)
    stream = io.BytesIO(); doc.save(stream)
    assert client.post("/api/resumes/parse", files={"file": ("resume.docx", stream.getvalue())}).status_code == 200
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    pdf = PdfWriter(); page = pdf.add_blank_page(width=612, height=792)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): pdf._add_object(font)})})
    content = DecodedStreamObject(); content.set_data(f'BT /F1 10 Tf 30 700 Td ({TEXT}) Tj ET'.encode())
    page[NameObject('/Contents')] = pdf._add_object(content)
    stream = io.BytesIO(); pdf.write(stream)
    assert client.post("/api/resumes/parse", files={"file": ("resume.pdf", stream.getvalue())}).status_code == 200
    assert client.post("/api/resumes/parse", files={"file": ("resume.exe", b"invalid")}).status_code == 415
    assert client.post("/api/resumes/parse", files={"file": ("resume.pdf", b"not a pdf")}).status_code == 422
    assert client.post("/api/resumes/parse", files={"file": ("resume.txt", b"x" * (2*1024*1024+1))}).status_code == 413
    job = {"title": "Engineer", "description": "Create reliable and tested applications.", "required": ["Unrecognized skill"]}
    assert client.post("/api/jobs", json=job).status_code == 422
    assert client.post("/api/jobs", json={**job, "required": ["Python"], "preferred": ["python"]}).status_code == 422
    login(client, "candidate")
    assert client.post("/api/candidates", json={"label": "ok", "text": "short"}).status_code == 422
    assert client.post("/api/extract", json={"label": "Valid", "text": TEXT}, headers={"Origin": "https://evil.example"}).status_code == 403

def test_fairness_suppression_and_uncertainty():
    rows = [{"candidate_id": str(i), "score": i * 10} for i in range(12)]
    attrs = {str(i): "A" if i < 6 else "B" for i in range(12)}
    report = fairness(rows, attrs, 60)
    assert report["demographic_parity_difference"] == 1
    assert report["groups"][0]["interval"][1] > 0
    assert report["groups"][1]["interval"][0] < 1
    small = fairness(rows[:3], attrs, 60)
    assert small["groups"][0]["selection_rate"] is None
    assert small["demographic_parity_difference"] is None
    assert fairness(rows, {}, 60)["unattributed_count"] == 12
    assert "Ada" not in safe_scoring_text("Name: Ada\nGender: Woman\nEmail: ada@example.test\n" + TEXT)
    assert safe_scoring_text("Name: Bob\n" + TEXT) == safe_scoring_text("Name: Ada\n" + TEXT)

def test_overview_uses_persisted_counts_and_role_boundaries(client):
    assert client.get('/api/overview').status_code == 401
    login(client)
    counts = client.get('/api/overview').json()
    assert counts == {'jobs': 3, 'profiles': 12, 'runs': 2, 'reviews': 0, 'sample_profiles': 12}
    login(client, 'candidate')
    client.post('/api/candidates', json={'label': 'Overview test profile', 'text': TEXT})
    login(client)
    counts = client.get('/api/overview').json()
    assert counts['profiles'] == 13 and counts['sample_profiles'] == 12
    login(client, 'candidate')
    assert client.get('/api/overview').status_code == 403
    login(client, 'auditor')
    assert client.get('/api/overview').status_code == 403
