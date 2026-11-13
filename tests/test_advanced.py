import json
from pathlib import Path
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select
from test_backend import client, login, TEXT
from backend import app as module
from backend.advanced import ApplicationVersion, ranking_metrics, DatasetIn, evaluate_dataset
from backend.matching import assess_evidence, rank
from types import SimpleNamespace

def create_job(client):
    login(client)
    return client.post('/api/jobs',json={'title':'Applied backend role','description':'Build reliable Python services and SQL queries.','required':['Python','SQL'],'preferred':['FastAPI']}).json()

def test_applications_gaps_and_immutable_submissions(client):
    j=create_job(client)
    assert client.post(f"/api/jobs/{j['id']}/runs").status_code==422
    login(client,'candidate')
    assert client.get('/api/opportunities').json()['total']==0
    profile=client.post('/api/candidates',json={'label':'Applicant test','text':TEXT}).json()
    assert client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':profile['id']}).status_code==404
    login(client)
    client.put(f"/api/jobs/{j['id']}/publication",json={'published':True})
    login(client,'candidate')
    assert client.get('/api/opportunities').json()['total']==1
    gap=client.get(f"/api/jobs/{j['id']}/skill-gap",params={'candidate_id':profile['id']}).json()
    assert all(r['status']=='supported' for r in gap['requirements'])
    a=client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':profile['id']}).json()
    assert a['profile_version']==1
    assert client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':profile['id']}).status_code==409
    updated={**profile,'text':'Currently learning Python and SQL. No experience with FastAPI. Built React interfaces using CSS and HTML.'}
    assert client.put(f"/api/candidates/{profile['id']}",json=updated).status_code==200
    gap=client.get(f"/api/jobs/{j['id']}/skill-gap",params={'candidate_id':profile['id']}).json()
    assert [r['status'] for r in gap['requirements']]==['learning','learning','negated']
    login(client)
    r1=client.post(f"/api/jobs/{j['id']}/runs").json()
    assert r1['candidate_count']==1 and r1['results'][0]['profile_version']==1
    assert all(r['matched'] for r in r1['results'][0]['requirements'])
    login(client,'candidate')
    assert client.post(f"/api/applications/{a['id']}/withdraw").status_code==410
    decision={'status':'accepted','feedback':'Your demonstrated Python skills meet the next-stage requirements. We will arrange an interview.','revision':1,'run_id':r1['id']}
    assert client.put(f"/api/applications/{a['id']}/decision",json=decision).status_code==403
    login(client)
    review=client.get(f"/api/applications/{a['id']}/review").json()
    assert review['match']['run_id']==r1['id'] and review['match']['profile_version']==1
    assert review['submitted_text']==TEXT
    assert 'Matching evidence score:' in review['feedback_previews']['accepted']
    assert client.put(f"/api/applications/{a['id']}/decision",json={**decision,'run_id':'missing'}).status_code==409
    accepted=client.put(f"/api/applications/{a['id']}/decision",json=decision)
    assert accepted.status_code==200 and accepted.json()['status']=='accepted'
    assert client.put(f"/api/applications/{a['id']}/decision",json=decision).status_code==409
    assert client.put('/api/applications/missing/decision',json=decision).status_code==404
    login(client,'candidate')
    saved=client.get('/api/applications').json()['items'][0]
    assert saved['decisions'][0]['feedback']==review['feedback_previews']['accepted'] and saved['profile_version']==1
    assert decision['feedback'] not in saved['decisions'][0]['feedback']
    assert client.get(f"/api/applications/{a['id']}/review").status_code==403
    assert client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':profile['id']}).status_code==409
    login(client)
    rejected=client.put(f"/api/applications/{a['id']}/decision",json={**decision,'status':'rejected','revision':2,'feedback':'The role requires additional demonstrated SQL experience for the next stage.'})
    assert rejected.status_code==200 and len(rejected.json()['decisions'])==2
    assert client.post(f"/api/jobs/{j['id']}/runs").status_code==422
    assert client.get(f"/api/runs/{r1['id']}").json()['results'][0]['profile_version']==1
    login(client,'auditor')
    assert client.get('/api/applications').status_code==403
    assert client.put(f"/api/applications/{a['id']}/decision",json=decision).status_code==403
    with Session(module.engine) as session:
        assert len(session.scalars(select(ApplicationVersion)).all())==3


def test_candidate_ownership_publication_and_withdrawal(client):
    j=create_job(client);client.put(f"/api/jobs/{j['id']}/publication",json={'published':True})
    foreign=client.get('/api/candidates').json()['items'][0]['id']
    login(client,'candidate')
    own=client.get('/api/candidates').json()['items'][0]['id']
    if foreign!=own:
        assert client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':foreign}).status_code==403
    assert client.put(f"/api/jobs/{j['id']}/publication",json={'published':False}).status_code==403
    a=client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':own}).json()
    assert client.get('/api/applications').json()['total']==1
    login(client)
    assert client.post(f"/api/applications/{a['id']}/withdraw").status_code==403
    client.put(f"/api/jobs/{j['id']}/publication",json={'published':False})
    login(client,'candidate')
    assert client.get('/api/opportunities').json()['total']==0
    client.post(f"/api/applications/{a['id']}/withdraw")
    assert client.post(f"/api/jobs/{j['id']}/applications",json={'candidate_id':own}).status_code==404
    login(client)
    assert client.post(f"/api/jobs/{j['id']}/runs").status_code==201

@pytest.mark.parametrize('text,status',[
    ('No experience with Python.','negated'),('I have not used Python.','negated'),
    ('Currently learning Python.','learning'),('Skills: Python, SQL.','uncertain'),
    ('Built Python services with SQL.','supported'),('Used Java for applications.','not_found'),
    ('Used Python in a project. No Python experience.','uncertain'),
    ('Learning SQL but built Python services.','supported')])
def test_contextual_evidence(text,status):
    assert assess_evidence(text,'Python')['status']==status

def test_negated_evidence_does_not_earn_points():
    c=SimpleNamespace(id='a',label='A',text='No experience with Python. Currently learning SQL.',version=1,warnings=[])
    rows,method=rank(SimpleNamespace(required=['Python','SQL'],preferred=[]),[c])
    assert rows[0]['score']==0 and method=='skill-tfidf-v2'

def test_metrics_and_evaluation_api(client):
    assert ranking_metrics(['b','a','c'],{'a':2,'b':1,'c':0},2)['recall']==1
    assert ranking_metrics(['a','b','c'],{'a':2,'b':1,'c':0},2)['ndcg']==1
    login(client)
    dataset=client.get('/api/evaluation/template').json()
    r=client.post('/api/evaluations',json={'dataset':dataset,'k':3,'include_semantic':False})
    assert r.status_code==201,r.text
    report=r.json()
    assert report['synthetic'] and len(report['dataset_sha256'])==64
    assert len(report['methods'])==1
    assert 0<=report['methods'][0]['metrics']['ndcg']<=1
    assert report['methods'][0]['queries'][0]['metrics']['effective_k']==3
    bad=json.loads(json.dumps(dataset));bad['queries'][0]['profiles'][0]['relevance']=5
    assert client.post('/api/evaluations',json={'dataset':bad}).status_code==422
    login(client,'auditor')
    assert client.get('/api/evaluations').json()['total']==1
    assert client.post('/api/evaluations',json={'dataset':dataset}).status_code==403
    login(client,'candidate')
    assert client.get('/api/evaluations').status_code==403

def test_semantic_evaluation_failure_is_explicit(client,monkeypatch):
    import backend.matching as matching
    monkeypatch.setattr(matching,'semantic_model',lambda:None)
    login(client)
    dataset=client.get('/api/evaluation/template').json()
    assert client.post('/api/evaluations',json={'dataset':dataset,'include_semantic':True}).status_code==503
    assert client.get('/api/evaluations').json()['total']==0

def test_real_local_semantic_fixture(monkeypatch):
    import importlib.util
    import backend.matching as matching
    root=Path(__file__).resolve().parent.parent
    model=root/'models/all-MiniLM-L6-v2'
    if not (model/'model.safetensors').exists() or not importlib.util.find_spec('sentence_transformers'):
        pytest.skip('Optional local semantic model is not installed.')
    monkeypatch.setenv('SEMANTIC_MODEL_PATH',str(model))
    monkeypatch.setenv('HF_HUB_OFFLINE','1')
    monkeypatch.setenv('HF_HOME',str(root/'models/.hf'))
    matching.semantic_model.cache_clear()
    dataset=DatasetIn.model_validate_json((root/'examples/evaluation-dataset.json').read_text())
    report=evaluate_dataset(dataset,3,True)
    assert [m['method'] for m in report['methods']]==['skill-tfidf-v2','skill-semantic-v2']
    assert all(0<=m['metrics']['ndcg']<=1 for m in report['methods'])
    assert report['matching_config']['semantic_reference']['revision']
    matching.semantic_model.cache_clear()
