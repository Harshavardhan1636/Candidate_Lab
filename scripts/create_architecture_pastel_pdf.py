from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from math import atan2, cos, sin
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/pdf/Candidate_Lab_Architecture_and_Workflows_Pastel.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
NAVY=colors.HexColor('#303a43');TEAL=colors.HexColor('#718c87');LIGHT=colors.HexColor('#e3eeea');MUTED=colors.HexColor('#626b72')
PALETTE=['#e2ebe5','#e4e8f3','#f3e6dc','#e8e1f0','#e0edf0','#f1e8cf']

st=getSampleStyleSheet()
for name,size,leading,col in [('TitleX',38,44,NAVY),('HeadX',21,27,NAVY),('BodyX',10,15,NAVY),('SmallX',8.5,12,MUTED),('BoxX',9,12,NAVY)]:
 st.add(ParagraphStyle(name=name,fontName='Times-Roman' if name in ['TitleX','HeadX'] else 'Helvetica',fontSize=size,leading=leading,textColor=col,spaceAfter=10))
story=[]
def p(t,style='BodyX'):return Paragraph(t,st[style])
def add(t,style='BodyX'):story.append(p(t,style))
def page(n,title,intro):
 if story:story.append(PageBreak())
 add('ARCHITECTURE &amp; WORKFLOWS / '+str(n),'SmallX');add(title,'HeadX');add(intro)
class Diagram(Flowable):
 def __init__(self,nodes,edges,height=370):super().__init__();self.width=491;self.height=height;self.nodes=nodes;self.edges=edges
 def draw(self):
  c=self.canv
  for a,b in self.edges:
   x,y,w,h,_=self.nodes[a];xx,yy,ww,hh,_=self.nodes[b]
   ax,ay=x+w/2,y+h/2;bx,by=xx+ww/2,yy+hh/2
   dx,dy=bx-ax,by-ay
   ta=min(w/2/abs(dx) if dx else 1e9,h/2/abs(dy) if dy else 1e9)
   tb=min(ww/2/abs(dx) if dx else 1e9,hh/2/abs(dy) if dy else 1e9)
   x1,y1=ax+dx*ta,ay+dy*ta;x2,y2=bx-dx*tb,by-dy*tb
   c.setStrokeColor(TEAL);c.setLineWidth(1.2);c.line(x1,y1,x2,y2)
   ang=atan2(y2-y1,x2-x1)
   c.line(x2,y2,x2-6*cos(ang-.45),y2-6*sin(ang-.45));c.line(x2,y2,x2-6*cos(ang+.45),y2-6*sin(ang+.45))
  for index,(x,y,w,h,text) in enumerate(self.nodes):
   c.setFillColor(colors.HexColor('#e8e6e1'));c.roundRect(x,y-2,w,h,9,fill=1,stroke=0)
   c.setFillColor(colors.HexColor(PALETTE[index%len(PALETTE)]));c.roundRect(x,y,w,h,9,fill=1,stroke=0)
   c.setFillColor(colors.white);c.circle(x+18,y+h/2,10,fill=1,stroke=0)
   c.setFillColor(MUTED);c.setFont('Helvetica-Bold',7);c.drawCentredString(x+18,y+h/2-2.5,str(index+1).zfill(2))
   para=p(text,'BoxX');_,ph=para.wrap(w-48,h-8)
   if ph>h-14:
    compact=ParagraphStyle(name='Compact',parent=st['BoxX'],fontSize=8,leading=10)
    para=Paragraph(text,compact);_,ph=para.wrap(w-48,h-8)
   para.drawOn(c,x+36,y+(h-ph)/2+5)

def graph(rows,edges,height=370):
 nodes=[]
 for ri,row in enumerate(rows):
  w=(491-(len(row)-1)*18)/len(row);y=height-55-ri*78
  nodes.extend([(i*(w+18),y,w,58,text) for i,text in enumerate(row)])
 story.append(Diagram(nodes,edges,height));story.append(Spacer(1,10))
def note(t):
 t=Table([[p('<b>PRESENTER NOTE</b><br/>'+t)]],colWidths=[491])
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eee8dc')),('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t)

page('01','Candidate Lab','Fair and Explainable Machine Learning for Automated Candidate Selection and Skill Matching')
story.append(Spacer(1,25));add('Architecture &amp;<br/>Workflow Guide','TitleX');add('A visual explanation for project reviewers, presenters and nontechnical readers.');story.append(Spacer(1,22))
add('<b>Project overview</b>');add('Candidate Lab connects job requirements with evidence in submitted resumes. Candidates manage their profiles, recruiters inspect explainable matching results and record decisions, and auditors access permitted aggregate reports. Human reviewers retain responsibility for recruitment decisions.')
add('<b>Inside this guide</b>');add('1. Overall architecture<br/>2. Components and responsibilities<br/>3. Complete recruitment workflow<br/>4. Candidate profile workflow<br/>5. Matching and explanation workflow<br/>6. Application review and automatic feedback<br/>7. Model evaluation workflow<br/>8. Role and access structure')
story.append(Spacer(1,25));add('Prepared for project explanation and evaluation<br/>Current local implementation | 4 November 2026','SmallX')
page('02','Overall architecture','Four layers separate the user interface, recruitment rules, matching analysis and stored records.')
graph([['<b>Users</b><br/>Candidate | Recruiter | Auditor'],['<b>Presentation</b><br/>React + TypeScript role-based dashboards'],['<b>Application</b><br/>FastAPI: authentication, profiles, jobs, applications, decisions and audit'],['<b>Matching</b><br/>Resume parsing, contextual skills, TF-IDF or local semantic model'],['<b>Storage</b><br/>SQLAlchemy + SQLite records | Local semantic model files']],[(0,1),(1,2),(2,3),(3,4)],370)
note('The frontend sends HTTP API requests. FastAPI validates access and coordinates operations. The matching engine produces evidence and scores. Database records retain the results and history. Model files are stored locally, separately from the database.')
page('03','Components and responsibilities','Each technology has a specific job in the application.')
rows=[('React + TypeScript','Displays dashboards, forms, applications and evidence.'),('FastAPI / Python','Receives API requests and implements application rules.'),('Authentication and permissions','Restricts features and records according to the signed-in role.'),('Resume parsers','Extract text from supported PDF, DOCX and TXT documents.'),('Contextual skill analysis','Distinguishes supported, learning, negated, uncertain and absent evidence.'),('TF-IDF','Compares text using weighted words.'),('Local semantic model','Compares text using meaning-based representations.'),('SQLAlchemy','Reads and writes database records.'),('SQLite','Stores accounts, profiles, jobs, applications, snapshots and decisions.'),('Saved snapshots and history','Preserve submitted evidence, matching results and recruitment feedback.')]
t=Table([[p('<b>Component</b>'),p('<b>Purpose</b>')]]+[[p(a),p(b)] for a,b in rows],colWidths=[165,326]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),LIGHT),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f8f6f1'),colors.HexColor('#eeeef2')]),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#dedbd4')),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));story.append(t)
page('04','Complete recruitment workflow','Recruitment moves from job publication to an application, an evidence-based review and a candidate-visible response.')
graph([['Recruiter creates requirements<br/>and publishes a job','Candidate creates profile<br/>and reviews resume extraction'],['Candidate views published jobs<br/>and applies'],['System preserves submitted resume<br/>Recruiter runs matching'],['Recruiter reviews score and evidence<br/>Chooses a recruitment status'],['Under review','Accepted for next stage','Not selected'],['System generates feedback and saves decision history<br/>Candidate reads status and feedback']],[(0,2),(1,2),(2,3),(3,4),(4,5),(4,6),(4,7),(5,8),(6,8),(7,8)],460)
note('The system provides matching evidence. The recruiter chooses the decision. Accepted for next stage means progression in recruitment, not a job offer.')
page('05','Candidate profile workflow','Candidates own their profiles and can correct extracted text before saving it.')
graph([['Upload PDF, DOCX or TXT','Paste resume text'],['Validate document and extract text'],['Analyse skill evidence<br/>Show skills and supporting passages'],['Candidate checks and corrects text<br/>Saves a profile version'],['Apply for a published job<br/>Save an immutable submitted snapshot']],[(0,2),(1,2),(2,3),(3,4),(4,5)],370)
add('<b>Later edits</b>');add('A candidate can save a newer profile version. Existing applications continue to use the version originally submitted. This prevents later edits from silently changing the evidence under review. Recruiters can inspect profiles but cannot create or edit them.')
page('06','Matching and explanation','Matching combines contextual skill evidence with text similarity, then saves the result for review.')
graph([['Job requirements','Submitted resume snapshots'],['Prepare job-related scoring text'],['Contextual skill analysis','TF-IDF OR local semantic similarity'],['Combine supported skill coverage<br/>with text similarity'],['Score out of 100 + contribution breakdown<br/>Supporting passages saved in matching snapshot']],[(0,2),(1,2),(2,3),(2,4),(3,5),(4,5),(5,6)],370)
add('<b>Context matters</b>');add('“Currently learning Python” is treated differently from “Built Python APIs.” Evidence states include supported, learning, negated, uncertain and not found. Only supported evidence earns skill-coverage credit.')
note('The score summarises the match to configured requirements. It is not a probability of job success. Missing evidence does not establish that a candidate lacks a skill.')
page('07','Application review & automatic feedback','Recruiters inspect saved evidence directly inside Applications > Review application.')
graph([['Open application review<br/>Load the submitted resume'],['Compatible saved match exists?'],['No: open job matching,<br/>run matching and return','Yes: show score, method,<br/>date and skill evidence'],['Recruiter chooses a status<br/>System previews automatic feedback'],['Save decision and evidence reference<br/>Candidate sees feedback in My applications']],[(0,1),(1,2),(1,3),(3,4),(4,5)],370)
add('A decision cannot be saved without a compatible matching snapshot. Compatibility includes the application, submitted profile version and current job-requirements version.')
add('Feedback summarises supported skills, required skills needing clearer evidence, the saved score and the selected status. It is generated by the server; the recruiter does not type it manually. Saving makes it visible in the candidate dashboard. It does not send email.')
note('The saved feedback and evidence reference remain unchanged by later profile edits or new matching runs. Recruiter decisions remain separate from model scores.')
page('08','Model evaluation workflow','This section tests the matching methods against examples with known relevance labels.')
graph([['Load labelled test dataset<br/>Jobs, example profiles and expected relevance'],['Run TF-IDF ranking','Run local semantic ranking'],['Compare predicted rankings<br/>with relevance labels'],['Calculate Precision@k, Recall@k and NDCG@k'],['Save and export evaluation report<br/>Recruiter: detailed results | Auditor: aggregate results']],[(0,1),(0,2),(1,3),(2,3),(3,4),(4,5)],370)
add('<b>Labels:</b> 0 = not relevant; 1 = partially relevant; 2 = strongly relevant. <b>Top-k</b> means the first k ranked results.')
add('<b>Precision@k:</b> how many top results are relevant. <b>Recall@k:</b> how many relevant examples were retrieved. <b>NDCG@k:</b> whether stronger matches appear near the top.')
note('Load the synthetic example, select k = 3, choose methods and run evaluation. This tests methods; it does not train them. The small synthetic dataset does not establish real-world accuracy or demographic fairness.')
page('09','Roles and presentation summary','Access controls separate candidate ownership, recruiter review and aggregate auditing.')
graph([['Sign in<br/>Backend checks account role'],['Candidate','Recruiter','Auditor'],['Manage own profile<br/>Apply for jobs<br/>Read own status and feedback','Create and publish jobs<br/>Inspect profiles and matches<br/>Record recruitment decisions','Inspect permitted audit events<br/>View aggregate audit and<br/>evaluation reports']],[(0,1),(0,2),(0,3),(1,4),(2,5),(3,6)],240)
add('<b>Recruiter workspace</b>');add('Job details defines requirements; Publish jobs makes roles available; Applications supports decisions; Matching evidence explains saved results; Compare snapshots shows changes between same-job runs; Model evaluation tests ranking methods.')
add('<b>Suggested presentation introduction</b>');add('“Candidate Lab separates profile ownership, recruitment review and auditing. Candidates manage their information and apply for jobs. Recruiters define requirements and inspect explainable matching results before making decisions. The system preserves submitted evidence, generates feedback from saved matching results, and maintains a history so the review can be traced.”')
add('<b>Deployment context</b>');add('The current application runs locally at http://127.0.0.1:8000. That address is local to the machine; it is not a public deployment link. Email delivery, interview scheduling and other proposed features are outside the workflows illustrated here.','SmallX')
def footer(c,d):
 c.saveState()
 c.setFillColor(colors.HexColor('#faf8f3'));c.rect(0,0,A4[0],A4[1],fill=1,stroke=0)
 c.setFillColor(colors.HexColor(PALETTE[(d.page-1)%len(PALETTE)]));c.roundRect(38,775,519,39,12,fill=1,stroke=0)
 c.setFillColor(NAVY);c.setFont('Helvetica-Bold',9);c.drawString(53,791,'CANDIDATE LAB')
 c.setFont('Helvetica',8);c.drawRightString(541,791,'SYSTEM DESIGN / VISUAL GUIDE')
 c.setStrokeColor(colors.HexColor('#d9d5cd'));c.line(52,43,543,43)
 c.setFont('Helvetica',8);c.setFillColor(MUTED);c.drawString(52,29,'Explainable matching. Accountable decisions.')
 c.drawRightString(543,29,str(d.page).zfill(2)+' / 09')
 c.restoreState()
SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=52,leftMargin=52,topMargin=88,bottomMargin=58,title='Candidate Lab - Architecture and Workflows',author='Candidate Lab Project Team').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
