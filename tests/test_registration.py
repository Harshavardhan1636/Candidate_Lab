import time
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend import app as module
from test_backend import client

def body(role="candidate", email="new@example.test", code=""):
    return {"email": email, "password": "StrongPassword!2026", "confirm_password": "StrongPassword!2026", "role": role, "invitation_code": code}

@pytest.mark.parametrize("role", ["candidate", "recruiter", "auditor"])
def test_register_and_login_all_roles(client, role):
    email = f"new-{role}@example.test"
    code = ""
    if role != "candidate":
        with Session(module.engine) as session:
            code = module.create_invitation(session, email, role)
    response = client.post("/api/auth/register", json=body(role, email.upper(), code))
    assert response.status_code == 201, response.text
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/register", json=body(role, email, code)).status_code == 409
    signed = client.post("/api/auth/login", json={"email": email, "password": "StrongPassword!2026"})
    assert signed.status_code == 200 and signed.json()["role"] == role
    if role == "candidate":
        assert client.get("/api/candidates").json()["total"] == 0
        assert client.get("/api/runs").status_code == 403
    elif role == "recruiter":
        assert client.get("/api/jobs").status_code == 200
        assert client.get("/api/audit/events").status_code == 403
    else:
        assert client.get("/api/audit/events").status_code == 200
        assert client.get("/api/candidates").status_code == 403
    with Session(module.engine) as session:
        user = session.scalar(select(module.User).where(module.User.email == email))
        assert user.password != "StrongPassword!2026"
        assert module.check_password("StrongPassword!2026", user.password)
        if code:
            invitation = session.scalar(select(module.Invitation).where(module.Invitation.email == email))
            assert invitation.used and invitation.token_hash != code

def test_invitation_boundaries_and_expiry(client):
    with Session(module.engine) as session:
        code = module.create_invitation(session, "invited@example.test", "recruiter")
    assert client.post("/api/auth/register", json=body("recruiter")).status_code == 403
    assert client.post("/api/auth/register", json=body("recruiter", "wrong@example.test", code)).status_code == 403
    assert client.post("/api/auth/register", json=body("auditor", "invited@example.test", code)).status_code == 403
    with Session(module.engine) as session:
        invitation = session.scalar(select(module.Invitation))
        assert not invitation.used
        invitation.expires = int(time.time()) - 1
        session.commit()
    assert client.post("/api/auth/register", json=body("recruiter", "invited@example.test", code)).status_code == 403
    with Session(module.engine) as session:
        invitation = session.scalar(select(module.Invitation))
        invitation.expires = int(time.time()) + 3600
        invitation.used = True
        session.commit()
    assert client.post("/api/auth/register", json=body("recruiter", "invited@example.test", code)).status_code == 403

def test_registration_validation_and_origin(client):
    for change in [{"email": "not-an-email"}, {"password": "short"}, {"confirm_password": "mismatch"}, {"password": "abcdefghijklmn", "confirm_password": "abcdefghijklmn"}, {"role": "admin"}]:
        assert client.post("/api/auth/register", json={**body(), **change}).status_code == 422
    assert client.post("/api/auth/register", json=body(), headers={"Origin": "https://evil.example"}).status_code == 403
