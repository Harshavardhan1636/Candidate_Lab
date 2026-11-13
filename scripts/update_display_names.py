"""Rename generated sample records without changing evidence or historical snapshots."""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app import engine, Job, Candidate, AuditLog, DB_URL
from backend.naming import job_name, profile_name

root=Path(__file__).resolve().parent.parent
if not DB_URL.startswith('sqlite:///'):
    raise SystemExit('Use a reviewed migration for a non-SQLite deployment.')
source=Path(DB_URL.removeprefix('sqlite:///')).resolve()
backup=root/'data/backups'/('before-naming-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.db')
backup.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(source) as src, sqlite3.connect(backup) as dest:src.backup(dest)
changes=0
with Session(engine) as session:
    renamed_ids=set(session.scalars(select(AuditLog.object_id).where(AuditLog.action.like('Updated readable %'))))
    variants={
        'Python Backend Engineer':['Python Backend Engineer','Python API Engineer','Backend Integration Developer','Python Services Engineer','API Platform Developer','Backend Software Engineer','Python Application Engineer','Python API Developer'],
        'Python Application Developer':['Python Application Developer','Python Database Developer','Backend Application Developer','Python Service Developer'],
        'Python Developer - Project Experience':['Python Developer - Project Experience','Python Developer - Database Projects','Python Developer - Tested Services'],
        'Python Developer - API Testing':['Python Developer - API Testing','Python Developer - Integration Testing','Python Developer - Service Testing','Python Developer - API Validation'],
    }
    counts={}
    for model,field,fn in [(Job,'title',job_name),(Candidate,'label',profile_name)]:
        for record in session.scalars(select(model).order_by(model.id)):
            old=getattr(record,field);new=fn(old)
            if new in variants and (old!=new or record.id in renamed_ids):
                index=counts.get(new,0);counts[new]=index+1
                new=variants[new][index%len(variants[new])]
            if old!=new:
                setattr(record,field,new)
                session.add(AuditLog(actor_id='local-operator',action='Updated readable '+('job title' if model is Job else 'profile name'),object_id=record.id))
                changes+=1
    session.commit()
print('Readable display names updated:',changes)
print('Backup:',backup)
