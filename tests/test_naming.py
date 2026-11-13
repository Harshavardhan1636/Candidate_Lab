from backend.naming import job_name,profile_name
from test_backend import client,login,TEXT
from backend import app as module
from sqlalchemy import select
from sqlalchemy.orm import Session

def test_known_generated_names_only():
    assert job_name('Evaluation Engineer 1793769990568')=='Python Backend Engineer'
    assert job_name('3D Graphics Engineer')=='3D Graphics Engineer'
    assert profile_name('Learning profile 1793769983587')=='Python Developer - Project Experience'
    assert profile_name('Deekshith Alle')=='Deekshith Alle'

def test_current_display_names_do_not_rewrite_saved_evidence(client):
    login(client)
    run=client.get('/api/runs').json()[0]
    before=client.get(f"/api/runs/{run['id']}").json()
    original=before['results'][0]
    with Session(module.engine) as session:
        candidate=session.get(module.Candidate,original['candidate_id'])
        candidate.label='Updated Professional Profile'
        job=session.get(module.Job,run['job_id'])
        job.title='Updated Backend Engineer'
        session.commit()
    after=client.get(f"/api/runs/{run['id']}").json()
    updated=next(r for r in after['results'] if r['candidate_id']==original['candidate_id'])
    assert updated['candidate_label']=='Updated Professional Profile'
    assert updated['profile_snapshot']==original['profile_snapshot']
    assert updated['score']==original['score']
    assert after['job_snapshot']['title']=='Updated Backend Engineer'
    with Session(module.engine) as session:
        stored=session.get(module.Run,run['id'])
        assert stored.job_snapshot['title']!='Updated Backend Engineer'
        assert next(r for r in stored.results if r['candidate_id']==original['candidate_id'])['candidate_label']!='Updated Professional Profile'
