"""Applications, evidence gaps, snapshot comparisons and reproducible evaluations."""
import hashlib
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Literal
from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import Boolean, Integer, JSON, String, Text, UniqueConstraint, func, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column, object_session
from sqlalchemy.exc import IntegrityError
from .app import app, Base, Candidate, Job, Run, User, db, role, now, uid, job_out, run_out, owned_candidate, audit
from .matching import rank, assess_evidence, safe_scoring_text, SKILLS, matching_config
from .naming import profile_name, job_name

class Publication(Base):
    __tablename__ = 'job_publications'
    job_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    updated: Mapped[str] = mapped_column(String(40), default=now)

class Application(Base):
    __tablename__ = 'job_applications'
    __table_args__ = (UniqueConstraint('job_id', 'owner_id', name='one_application_per_candidate_job'),)
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    job_id: Mapped[str] = mapped_column(String(40))
    owner_id: Mapped[str] = mapped_column(String(40))
    candidate_id: Mapped[str] = mapped_column(String(40))
    snapshot: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default='active')
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created: Mapped[str] = mapped_column(String(40), default=now)
    updated: Mapped[str] = mapped_column(String(40), default=now)

class ApplicationVersion(Base):
    __tablename__ = 'application_versions'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    application_id: Mapped[str] = mapped_column(String(40))
    revision: Mapped[int] = mapped_column(Integer)
    snapshot: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20))
    created: Mapped[str] = mapped_column(String(40), default=now)

class RecruitmentDecision(Base):
    __tablename__ = 'recruitment_decisions'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    application_id: Mapped[str] = mapped_column(String(40), index=True)
    recruiter_id: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20))
    feedback: Mapped[str] = mapped_column(Text)
    revision: Mapped[int] = mapped_column(Integer)
    created: Mapped[str] = mapped_column(String(40), default=now)

class DecisionEvidence(Base):
    __tablename__ = 'decision_evidence'
    decision_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40))
    evidence: Mapped[dict] = mapped_column(JSON)


def application_match(session, a, run_id=None):
    job=session.get(Job,a.job_id)
    query=select(Run).where(Run.job_id==a.job_id)
    if run_id: query=query.where(Run.id==run_id)
    for run in session.scalars(query.order_by(Run.created.desc(),Run.id.desc())):
        if a.id not in run.job_snapshot.get('application_ids',[]): continue
        if run.job_snapshot.get('version')!=job.version: continue
        for row in run.results:
            if row['candidate_id']==a.candidate_id and row['profile_version']==a.snapshot['version']:
                return {'run_id':run.id,'created':run.created,'method':run.method,'job_version':job.version,'profile_version':a.snapshot['version'],'score':row['score'],'requirements':row['requirements'],'components':row['components']}
    return None


def candidate_feedback(match, status):
    opening={'under_review':'Your application is under review.','accepted':'Your application has been accepted for the next recruitment stage. This is not a job offer.','rejected':'The recruiter has decided not to progress your application for this role.'}[status]
    supported=[r['skill'] for r in match['requirements'] if r['matched']]
    gaps=[r['skill']+' ('+r.get('evidence_status','not_found').replace('_',' ')+')' for r in match['requirements'] if r['kind']=='required' and not r['matched']]
    return opening+' Matching evidence score: '+format(match['score'],'.2f')+'/100 using '+match['method']+'. '+('Supporting evidence found for: '+', '.join(supported)+'. ' if supported else 'No supported job-skill evidence was found. ')+('Required skills needing clearer evidence: '+', '.join(gaps)+'. ' if gaps else 'Supporting evidence was found for all required skills. ')+'This reflects the submitted resume (version '+str(match['profile_version'])+'), not a verified measure of ability. Missing evidence does not establish a missing skill. The recruiter made the decision; the score does not automatically accept or reject applications.'


@app.get('/api/applications/{ident}/review')
def application_review(ident: str, user: User = Depends(role('recruiter')), session: Session = Depends(db)):
    a=session.get(Application,ident)
    if not a: raise HTTPException(404,'Application not found.')
    match=application_match(session,a)
    return {'application':application_out(a),'submitted_text':a.snapshot['text'],'match':match,'feedback_previews':{status:candidate_feedback(match,status) for status in ['under_review','accepted','rejected']} if match else {}}

class Evaluation(Base):
    __tablename__ = 'model_evaluations'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    dataset: Mapped[dict] = mapped_column(JSON)
    report: Mapped[dict] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(String(40), default=now)

def application_out(a):
    session=object_session(a);c=session.get(Candidate,a.candidate_id) if session else None
    decisions=session.scalars(select(RecruitmentDecision).where(RecruitmentDecision.application_id==a.id).order_by(RecruitmentDecision.revision)).all() if session else []
    return {'decisions':[{'status':d.status,'feedback':d.feedback,'created':d.created} for d in decisions], 'id': a.id, 'job_id': a.job_id, 'candidate_id': a.candidate_id, 'profile_label': c.label if c else profile_name(a.snapshot['label']), 'profile_version': a.snapshot['version'], 'status': a.status, 'revision': a.revision, 'updated': a.updated}

def submitted_profiles(session, job_id):
    applications = session.scalars(select(Application).where(Application.job_id == job_id, Application.status.in_(['active','under_review','accepted'])).order_by(Application.id).limit(501)).all()
    return [SimpleNamespace(id=a.candidate_id, label=a.snapshot['label'], text=a.snapshot['text'], version=a.snapshot['version'], warnings=a.snapshot.get('warnings', []), application_id=a.id) for a in applications]

def publication_out(session, j):
    pub = session.get(Publication, j.id)
    count = session.scalar(select(func.count()).select_from(Application).where(Application.job_id == j.id, Application.status.in_(['active','under_review','accepted'])))
    return {**job_out(j), 'published': bool(pub and pub.published), 'application_count': count}

@app.get('/api/opportunities')
def opportunities(page: int = Query(1, ge=1), q: str = Query('', max_length=100), user: User = Depends(role('candidate', 'recruiter')), session: Session = Depends(db)):
    query = select(Job).where(Job.title.ilike(f'%{q}%'))
    if user.role == 'candidate':
        query = query.join(Publication, Publication.job_id == Job.id).where(Publication.published == True)
    query = query.order_by(Job.created.desc(), Job.id)
    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items=[]
    for j in session.scalars(query.offset((page-1)*10).limit(10)):
        item = publication_out(session, j)
        if user.role == 'candidate':
            a = session.scalar(select(Application).where(Application.job_id == j.id, Application.owner_id == user.id))
            item.pop('application_count', None)
            item['my_application'] = application_out(a) if a else None
        items.append(item)
    return {'items': items, 'total': total}

class PublishIn(BaseModel):
    published: bool

@app.put('/api/jobs/{ident}/publication')
def publish(ident: str, body: PublishIn, user: User = Depends(role('recruiter')), session: Session = Depends(db)):
    j = session.get(Job, ident)
    if not j: raise HTTPException(404, 'Job not found.')
    pub = session.get(Publication, ident)
    if not pub: pub = Publication(job_id=ident); session.add(pub)
    pub.published, pub.updated = body.published, now()
    audit(session, user, 'Published job' if body.published else 'Closed job to new applications', ident)
    session.commit()
    return publication_out(session, j)

class ApplyIn(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=40)

@app.post('/api/jobs/{ident}/applications', status_code=201)
def apply(ident: str, body: ApplyIn, user: User = Depends(role('candidate')), session: Session = Depends(db)):
    pub = session.get(Publication, ident)
    if not session.get(Job, ident) or not pub or not pub.published:
        raise HTTPException(404, 'This job is not open to applications.')
    profile = owned_candidate(session, body.candidate_id, user)
    existing = session.scalar(select(Application).where(Application.job_id == ident, Application.owner_id == user.id))
    if existing:
        raise HTTPException(409, 'You already applied for this job. Check Applications for the recruiter response.')
    snapshot = {'label': profile.label, 'text': profile.text, 'version': profile.version, 'warnings': profile.warnings}
    a=Application(job_id=ident,owner_id=user.id,candidate_id=profile.id,snapshot=snapshot,status='active',revision=1)
    session.add(a)
    try:
        session.flush()
        session.add(ApplicationVersion(application_id=a.id, revision=a.revision, snapshot=a.snapshot, status=a.status))
        audit(session, user, 'Submitted job application', a.id); session.commit()
    except IntegrityError:
        session.rollback(); raise HTTPException(409, 'You already have an application for this job. Reload the page.')
    return application_out(a)

@app.post('/api/applications/{ident}/withdraw')
def withdraw(ident: str, user: User = Depends(role('candidate')), session: Session = Depends(db)):
    raise HTTPException(410, 'Application withdrawal is no longer available. Track your recruiter response in Applications.')

class DecisionIn(BaseModel):
    status: Literal['under_review','accepted','rejected']
    run_id: str = Field(min_length=1,max_length=40)
    revision: int = Field(ge=1)

@app.put('/api/applications/{ident}/decision')
def decide_application(ident: str, body: DecisionIn, user: User = Depends(role('recruiter')), session: Session = Depends(db)):
    a=session.get(Application,ident)
    if not a: raise HTTPException(404,'Application not found.')
    if a.status=='withdrawn': raise HTTPException(409,'This historical application was withdrawn and cannot be reviewed.')
    match=application_match(session,a,body.run_id)
    if not match: raise HTTPException(409,'Run matching for the current job requirements and submitted profile before deciding.')
    changed=session.execute(update(Application).where(Application.id==ident,Application.revision==body.revision).values(status=body.status,revision=body.revision+1,updated=now()))
    if changed.rowcount!=1: raise HTTPException(409,'Application changed. Reload before saving your decision.')
    session.refresh(a)
    decision=RecruitmentDecision(application_id=a.id,recruiter_id=user.id,status=body.status,feedback=candidate_feedback(match,body.status),revision=a.revision)
    session.add(decision); session.flush()
    session.add(DecisionEvidence(decision_id=decision.id,run_id=match['run_id'],evidence=match))
    session.add(ApplicationVersion(application_id=a.id,revision=a.revision,snapshot=a.snapshot,status=a.status))
    audit(session,user,'Recorded recruitment decision: '+body.status,a.id)
    session.commit()
    return application_out(a)

@app.get('/api/applications')
def applications(job_id: str = Query('', max_length=40), page: int = Query(1, ge=1), user: User = Depends(role('candidate','recruiter')), session: Session = Depends(db)):
    query=select(Application)
    if user.role=='candidate': query=query.where(Application.owner_id==user.id)
    if job_id:query=query.where(Application.job_id==job_id)
    total=session.scalar(select(func.count()).select_from(query.subquery()))
    items=[]
    for a in session.scalars(query.order_by(Application.updated.desc()).offset((page-1)*10).limit(10)):
        j=session.get(Job,a.job_id)
        items.append({**application_out(a),'job_title':j.title if j else 'Unavailable job'})
    return {'items':items,'total':total}

@app.get('/api/jobs/{ident}/skill-gap')
def skill_gap(ident: str, candidate_id: str, user: User = Depends(role('candidate')), session: Session = Depends(db)):
    j=session.get(Job,ident);pub=session.get(Publication,ident)
    if not j or not pub or not pub.published:raise HTTPException(404,'Published job not found.')
    c=owned_candidate(session,candidate_id,user)
    rows=[{'skill':skill,'kind':kind,**assess_evidence(safe_scoring_text(c.text),skill)} for kind,skills in [('required',j.required),('preferred',j.preferred)] for skill in skills]
    return {'job_title':j.title,'profile_label':c.label,'profile_version':c.version,'requirements':rows,'note':'Evidence review only. Not finding evidence does not establish a missing skill. Edit your profile to correct omissions; learning or uncertain mentions do not earn coverage points.'}

@app.get('/api/comparisons')
def compare(left: str, right: str, user: User = Depends(role('recruiter')), session: Session = Depends(db)):
    a,b=session.get(Run,left),session.get(Run,right)
    if not a or not b:raise HTTPException(404,'Matching snapshot not found.')
    if a.job_id!=b.job_id:raise HTTPException(422,'Select two snapshots for the same job.')
    ao,bo=run_out(a,True),run_out(b,True)
    ar={r['candidate_id']:r for r in ao['results']};br={r['candidate_id']:r for r in bo['results']}
    rows=[]
    for ident in sorted(ar.keys()|br.keys()):
        x,y=ar.get(ident),br.get(ident)
        requirements={r['skill']:r for r in (x or {}).get('requirements',[])}
        changed=[]
        for r in (y or {}).get('requirements',[]):
            old=requirements.get(r['skill'])
            if not old or (old.get('matched'),old.get('evidence'),old.get('evidence_status')) != (r.get('matched'),r.get('evidence'),r.get('evidence_status')):changed.append(r['skill'])
        rows.append({'candidate_id':ident,'label':(y or x)['candidate_label'],'before':x['score'] if x else None,'after':y['score'] if y else None,'delta':round(y['score']-x['score'],2) if x and y else None,'before_version':x['profile_version'] if x else None,'after_version':y['profile_version'] if y else None,'changed_requirements':changed,'membership':'both' if x and y else 'added' if y else 'removed'})
    return {'left':{'id':a.id,'method':a.method,'created':a.created,'job':ao['job_snapshot']},'right':{'id':b.id,'method':b.method,'created':b.created,'job':bo['job_snapshot']},'rows':rows,'notes':['Names reflect current display names; evidence and scores retain the versions saved in each run.','Deltas are descriptive, not causal attributions. Profile, rubric, method and cohort changes can all change scores.','Legacy snapshots may include every saved profile; new snapshots include active job applications only.','TF-IDF fits each cohort separately, so scores can shift even if one profile did not change.']}

class CaseIn(BaseModel):
    id: str = Field(min_length=1,max_length=60)
    text: str = Field(min_length=40,max_length=10000)
    relevance: Literal[0,1,2]

class QueryIn(BaseModel):
    id: str = Field(min_length=1,max_length=60)
    required: list[str] = Field(min_length=1,max_length=20)
    preferred: list[str] = Field(default_factory=list,max_length=20)
    profiles: list[CaseIn] = Field(min_length=2,max_length=50)

class DatasetIn(BaseModel):
    name: str = Field(min_length=3,max_length=100)
    provenance: str = Field(min_length=20,max_length=1000)
    synthetic: bool
    queries: list[QueryIn] = Field(min_length=1,max_length=20)
    @model_validator(mode='after')
    def validate_dataset(self):
        if len({q.id for q in self.queries})!=len(self.queries):raise ValueError('Query IDs must be unique.')
        for q in self.queries:
            if len({p.id for p in q.profiles})!=len(q.profiles):raise ValueError('Profile IDs must be unique within a query.')
            if not any(p.relevance>0 for p in q.profiles):raise ValueError('Each query needs at least one relevant profile.')
            if any(s not in SKILLS for s in q.required+q.preferred):raise ValueError('Use canonical supported skill names.')
            if len(set(q.required+q.preferred))!=len(q.required+q.preferred):raise ValueError('Do not repeat required/preferred skills.')
        return self

class EvaluateIn(BaseModel):
    dataset: DatasetIn
    k: int = Field(default=3,ge=1,le=20)
    include_semantic: bool = False

def ranking_metrics(ranked, relevance, k):
    k=min(k,len(ranked));chosen=ranked[:k]
    relevant=sum(v>0 for v in relevance.values())
    dcg=sum((2**relevance[i]-1)/math.log2(n+2) for n,i in enumerate(chosen))
    ideal=sum((2**v-1)/math.log2(n+2) for n,v in enumerate(sorted(relevance.values(),reverse=True)[:k]))
    hits=sum(relevance[i]>0 for i in chosen)
    return {'ndcg':round(dcg/ideal,4) if ideal else None,'recall':round(hits/relevant,4) if relevant else None,'precision':round(hits/k,4) if k else None,'effective_k':k}

def evaluate_dataset(dataset, k, include_semantic):
    methods=['tfidf']+(['semantic'] if include_semantic else [])
    output=[]
    for mode in methods:
        cases=[]
        for q in dataset.queries:
            job=SimpleNamespace(required=q.required,preferred=q.preferred)
            people=[SimpleNamespace(id=p.id,label=p.id,text=p.text,version=1,warnings=[]) for p in q.profiles]
            rows,method=rank(job,people,mode)
            relevance={p.id:p.relevance for p in q.profiles}
            cases.append({'query_id':q.id,'metrics':ranking_metrics([r['candidate_id'] for r in rows],relevance,k),'ranking':[{'profile_id':r['candidate_id'],'score':r['score'],'relevance':relevance[r['candidate_id']]} for r in rows]})
        output.append({'method':method,'metrics':{key:round(sum(c['metrics'][key] for c in cases)/len(cases),4) for key in ['ndcg','recall','precision']},'queries':cases})
    canonical=json.dumps(dataset.model_dump(),sort_keys=True,separators=(',',':')).encode()
    return {'dataset_name':dataset.name,'dataset_sha256':hashlib.sha256(canonical).hexdigest(),'synthetic':dataset.synthetic,'provenance':dataset.provenance,'k':k,'query_count':len(dataset.queries),'methods':output,'semantic_status':'evaluated' if include_semantic else 'not_requested','model_reference':Path(os.getenv('SEMANTIC_MODEL_PATH','')).name if include_semantic else None,'matching_config':matching_config('semantic' if include_semantic else 'tfidf'),'notes':['Held-out evaluation is not enforced by this tool. Keep training data separate and document annotation procedures.','Synthetic fixture results demonstrate metrics, not real applicant accuracy or demographic fairness.','NDCG uses graded relevance 0/1/2; precision and recall treat labels 1 and 2 as relevant. Results average queries equally.','Local MiniLM inference truncates long inputs; assess the effect on your dataset.']}

@app.get('/api/evaluation/template')
def evaluation_template(user: User = Depends(role('recruiter','auditor'))):
    path=Path(__file__).resolve().parent.parent/'examples/evaluation-dataset.json'
    return json.loads(path.read_text(encoding='utf-8'))

@app.get('/api/evaluation/status')
def evaluation_status(user: User = Depends(role('recruiter','auditor'))):
    return {'semantic_configured':bool(os.getenv('SEMANTIC_MODEL_PATH','').strip()),'baseline':'skill-tfidf-v2','semantic':'skill-semantic-v2','note':'Model configuration does not guarantee loadability. A failed semantic run returns an explicit error.'}

@app.post('/api/evaluations',status_code=201)
def evaluate(body: EvaluateIn, user: User = Depends(role('recruiter')), session: Session = Depends(db)):
    try:report=evaluate_dataset(body.dataset,body.k,body.include_semantic)
    except Exception as exc:raise HTTPException(503,'Evaluation could not load the configured local semantic model. Check the model path/dependencies, or run TF-IDF only.') from exc
    record=Evaluation(dataset=body.dataset.model_dump(),report=report)
    session.add(record);session.flush();audit(session,user,'Completed model evaluation',record.id);session.commit()
    return {'id':record.id,'created':record.created,**report}

@app.get('/api/evaluations')
def evaluations(page: int = Query(1,ge=1), user: User = Depends(role('recruiter','auditor')), session: Session = Depends(db)):
    total=session.scalar(select(func.count()).select_from(Evaluation))
    items=[]
    for e in session.scalars(select(Evaluation).order_by(Evaluation.created.desc()).offset((page-1)*10).limit(10)):
        report={**e.report}
        if user.role=='auditor':
            report['methods']=[{**m,'queries':[]} for m in report['methods']]
            report['notes']=[*report['notes'],'Individual ranked examples are restricted to recruiters; this auditor report contains aggregate metrics only.']
        items.append({'id':e.id,'created':e.created,**report})
    return {'items':items,'total':total}
