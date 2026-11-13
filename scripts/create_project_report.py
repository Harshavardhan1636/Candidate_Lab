"""Academic report based on the user's Batch-05 layout; project facts from source."""
from pathlib import Path
from html import escape
import math
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, Image, Preformatted, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/pdf/Candidate_Lab_Final_Project_Report.pdf'
TMP=ROOT/'tmp/pdfs/report'; TMP.mkdir(parents=True,exist_ok=True); OUT.parent.mkdir(parents=True,exist_ok=True)
for name,file in [('TNR','times.ttf'),('TNR-Bold','timesbd.ttf'),('TNR-Italic','timesi.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-Bold',italic='TNR-Italic',boldItalic='TNR-Bold')
NAVY=colors.HexColor('#142b40'); TEAL=colors.HexColor('#126c68'); LIGHT=colors.HexColor('#eef3f5'); INK=colors.HexColor('#17252e')
S=StyleSheet1()
for name,font,size,lead,align in [('body','TNR',12,17,TA_JUSTIFY),('h1','TNR-Bold',16,21,TA_CENTER),('h2','TNR-Bold',13,18,0),('small','TNR',9.5,13,0),('cell','TNR',10,14,0),('th','TNR-Bold',10,14,0),('center','TNR',12,17,TA_CENTER),('cover','TNR-Bold',19,25,TA_CENTER),('caption','TNR-Italic',10,14,TA_CENTER)]:
    S.add(ParagraphStyle(name=name,fontName=font,fontSize=size,leading=lead,alignment=align,spaceAfter=9,textColor=INK))
S['h2'].spaceBefore=10; S['h1'].spaceAfter=16
TITLE='FAIR AND EXPLAINABLE MACHINE LEARNING FOR AUTOMATED CANDIDATE SELECTION AND SKILL MATCHING'
TEAM=[('Deekshith Alle','23911A6672'),('Sirivennala Kammari','23911A6698'),('Rizwana Mohammad','23911A66A9'),('Harshavardhan Dyavanapelli','24915A6608')]
GUIDE='Mrs. Y. Uma Mythraye'; COLLEGE='VIDYA JYOTHI INSTITUTE OF TECHNOLOGY'
story=[]; physical=0
def p(s,sty='body'): return Paragraph(s,S[sty])
def add(s,sty='body'): story.append(p(s,sty))
def page(chapter=None,title=None):
    global physical
    if story: story.append(PageBreak())
    physical+=1
    if chapter: add('CHAPTER '+str(chapter),'h1')
    if title: add(title,'h1')
def sec(h,*paras):
    add(h,'h2')
    for s in paras: add(s)
def tab(headers,rows,widths=None):
    widths=widths or [469/len(headers)]*len(headers)
    data=[[p(escape(str(x)),'th') for x in headers]]+[[p(str(x),'cell') for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#9eafb9')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)])); story.append(t); story.append(Spacer(1,8))
def team(sign=False): tab(['Name','Roll number']+(['Signature'] if sign else []),[[a,b]+(['________________'] if sign else []) for a,b in TEAM],[220,110,139] if sign else [320,149])
def cap(text): add(text,'caption')

class Diagram(Flowable):
    def __init__(self,kind,height=330): Flowable.__init__(self); self.width=469; self.height=height; self.kind=kind
    def box(self,x,y,w,h,title,body='',oval=False):
        c=self.canv;c.setStrokeColor(NAVY);c.setFillColor(LIGHT)
        if oval: c.ellipse(x,y,x+w,y+h,fill=1,stroke=1)
        else: c.roundRect(x,y,w,h,4,fill=1,stroke=1)
        st=ParagraphStyle('d',fontName='TNR-Bold',fontSize=10,leading=13,alignment=TA_CENTER,textColor=NAVY)
        text=Paragraph(title+('<br/><font name="TNR" size="9">'+body+'</font>' if body else ''),st)
        _,ph=text.wrap(w-14,h-8); text.drawOn(c,x+7,y+(h-ph)/2)
    def arrow(self,x1,y1,x2,y2,label=''):
        c=self.canv;c.setStrokeColor(TEAL);c.setFillColor(TEAL);c.line(x1,y1,x2,y2)
        angle=math.atan2(y2-y1,x2-x1)
        for d in [-.5,.5]: c.line(x2,y2,x2-7*math.cos(angle+d),y2-7*math.sin(angle+d))
        if label: c.setFont('TNR',8);c.setFillColor(INK);c.drawCentredString((x1+x2)/2+5,(y1+y2)/2+6,label)
    def draw(self):
        c=self.canv; k=self.kind
        base={'architecture':330,'usecase':330,'sequence':365,'activity':365,'component':190,'deployment':165,'er':345}[k]
        c.scale(1,self.height/base)
        if k=='activity':c.translate(0,22)
        if k=='architecture':
            self.box(0,270,469,52,'Role-specific browser interface','Candidate | Recruiter | Auditor - React / TypeScript')
            self.box(0,180,469,56,'FastAPI application services','Session checks | Validation | Profile and job operations')
            self.box(0,78,220,62,'Matching and explanation','Skill rules + TF-IDF / cosine similarity')
            self.box(249,78,220,62,'SQLAlchemy / SQLite','Versions | Runs | Reviews | Audit records')
            self.box(0,0,469,40,'Evidence-led review and aggregate audit')
            for a in [(234,270,234,236),(110,180,110,140),(359,180,359,140),(110,78,110,40),(359,78,359,40)]: self.arrow(*a)
        elif k=='usecase':
            for x,y,t in [(0,280,'Candidate'),(0,140,'Recruiter'),(375,140,'Auditor'),(375,280,'Local admin')]: self.box(x,y,94,38,t)
            cases=[(122,280,'Register / sign in'),(122,215,'Upload / correct own profile'),(122,150,'Define job / run matching'),(122,85,'Inspect evidence / record review'),(122,20,'View aggregate audit / events')]
            for x,y,t in cases: self.box(x,y,225,43,t,oval=True)
            for a in [(94,299,122,301),(94,299,122,237),(94,159,122,172),(94,159,122,106),(375,159,347,42),(375,299,347,301)]: self.arrow(*a)
        elif k=='sequence':
            xs=[37,165,302,432]; labels=['Recruiter','React UI','FastAPI','Database']
            for x,t in zip(xs,labels): self.box(x-36,325,73,32,t);c.setDash(3,3);c.line(x,20,x,325);c.setDash()
            for y,a,b,t in [(298,0,1,'Run matching'),(260,1,2,'POST /jobs/{id}/runs'),(222,2,3,'Load job and profiles'),(184,3,2,'Stored records'),(106,2,3,'Save evidence snapshot'),(66,2,1,'Ranking + contributions'),(28,1,0,'Display evidence')]: self.arrow(xs[a],y,xs[b],y,t)
            self.box(244,132,116,33,'Calculate scores')
        elif k=='activity':
            for y,t in [(300,'Sign in and choose a role'),(236,'Upload / paste resume evidence'),(172,'Preview and correct extracted text'),(108,'Save profile and define job rubric'),(44,'Run matching and inspect evidence')]: self.box(85,y,300,42,t)
            for y in [300,236,172,108]: self.arrow(235,y,235,y-22)
            self.box(0,-18,219,38,'Record human review');self.box(250,-18,219,38,'Inspect aggregate audit')
            self.arrow(190,44,110,20);self.arrow(280,44,359,20)
        elif k=='component':
            self.box(0,140,469,44,'React interface','main.tsx | Registration.tsx | components.tsx | api.ts')
            self.box(0,50,215,50,'API / persistence','backend/app.py - role enforcement')
            self.box(254,50,215,50,'Matching / auditing','backend/matching.py')
            self.arrow(107,140,107,100);self.arrow(361,140,361,100);self.arrow(215,75,254,75)
        elif k=='deployment':
            self.box(0,92,469,65,'One local laptop / PC','Browser + Uvicorn/FastAPI + dist assets + SQLite file')
            self.box(0,0,220,52,'Browser','http://127.0.0.1:8000');self.box(249,0,220,52,'Local storage','data/candidate-lab.db')
            self.arrow(110,92,110,52);self.arrow(359,92,359,52)
        elif k=='er':
            boxes=[(0,270,140,65,'User','id, email, role, password hash'),(165,270,140,65,'Candidate','owner_id, text, version'),(330,270,139,65,'ProfileVersion','candidate_id, version, text'),(0,150,140,65,'Job','required, preferred, version'),(165,150,140,65,'Run','job_id, JSON snapshots'),(330,150,139,65,'Review','run_id, candidate_id, reason'),(0,30,140,65,'Invitation / Session','hash, expiry, role/email'),(165,30,140,65,'AuditAttribute','candidate_id, synthetic group'),(330,30,139,65,'AuditLog','actor, action, object, time')]
            for a in boxes:self.box(*a)
            for a in [(140,302,165,302),(305,302,330,302),(140,182,165,182),(305,182,330,182),(235,270,235,215),(235,270,235,95)]:self.arrow(*a)

class Shot(Flowable):
    def __init__(self,file,maxh=400,crop=None):
        Flowable.__init__(self);self.file=str(ROOT/'screenshots'/file);self.crop=crop;self.hAlign='CENTER'
        from PIL import Image as PI
        im=PI.open(self.file);w,h=im.size
        if crop:w,h=crop[-2:]
        self.sw=w;self.sh=h;self.scale=min(469/w,maxh/h);self.width=w*self.scale;self.height=h*self.scale
    def draw(self):
        c=self.canv;c.saveState();c.scale(self.scale,self.scale)
        if self.crop:
            from PIL import Image as PI
            im=PI.open(self.file);iw,ih=im.size
            path=c.beginPath();path.rect(0,0,self.sw,self.sh);c.clipPath(path,stroke=0,fill=0)
            cx,cy=self.crop[:2] if len(self.crop)==4 else (0,0)
            c.drawImage(self.file,-cx,self.sh-ih+cy,width=iw,height=ih)
        else:c.drawImage(self.file,0,0,width=self.sw,height=self.sh)
        c.restoreState()

# Front matter uses the institution and personnel explicitly confirmed by the user.
page()
add('A<br/>MAJOR PROJECT REPORT<br/>ON','h1');add(TITLE,'cover')
add('Submitted in partial fulfillment of the requirements for the award of the degree of','center')
add('<b>BACHELOR OF TECHNOLOGY</b><br/>in<br/><b>COMPUTER SCIENCE AND ENGINEERING<br/>(ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING)</b>','center')
add('<b>By</b>','center');team()
add('Under the guidance of<br/><b>'+GUIDE+'</b><br/>Assistant Professor','center')
reference=PdfReader('C:/Users/deeek/Downloads/Batch-05.pdf')
logo=TMP/'institute-logo.jpg';logo.write_bytes(reference.pages[0].images[0].data)
story.append(Image(str(logo),width=105,height=60,kind='proportional'))
add('<b>'+COLLEGE+'</b><br/>(An Autonomous Institution)','center')
add('Aziz Nagar Gate, C.B. Post, Hyderabad - 500075<br/><b>2025-2026</b>','center')

page(title='CERTIFICATE')
add('<b>'+COLLEGE+'</b><br/>Department of Computer Science and Engineering<br/>(Artificial Intelligence and Machine Learning)','center')
story.append(Spacer(1,20))
add('This is to certify that the project report entitled <b>"'+TITLE+'"</b> is submitted by <b>'+', '.join(a+' ('+b+')' for a,b in TEAM)+'</b> in partial fulfillment of the requirements for the award of the Bachelor of Technology degree in Computer Science and Engineering (Artificial Intelligence and Machine Learning).')
add('The report presents the design, implementation and evaluation of Candidate Lab, a web application for evidence-based candidate matching and aggregate audit. It is submitted for institutional review under the guidance and supervision of the undersigned.')
story.append(Spacer(1,55))
tab(['Internal Guide','Head of Department'],[[GUIDE+'<br/>Assistant Professor<br/><br/>Signature: ______________','Dr. N. Anusha<br/>Associate Professor<br/><br/>Signature: ______________']],[234,235])
story.append(Spacer(1,45));add('<b>External Examiner</b><br/><br/>Signature: _______________________','center')
add('Date: ____________________<br/>Place: ____________________')

page(title='DECLARATION')
add('We, <b>'+', '.join(a for a,b in TEAM)+'</b>, submit the project report entitled <b>"'+TITLE+'"</b> as a record of our project work for the Bachelor of Technology degree in Computer Science and Engineering (Artificial Intelligence and Machine Learning).')
add('The report describes the implemented Candidate Lab application and acknowledges the external research and software documentation used in its preparation. The certificate and declaration are to be reviewed and signed by the authors and the appropriate institutional authorities before submission.')
add('We understand that the current implementation supports candidate matching and human review. No claim is made that the application has been validated as a real-world hiring predictor or that synthetic cohort comparisons establish demographic fairness.')
story.append(Spacer(1,35));team(True)
story.append(Spacer(1,30));add('Date: ____________________<br/>Place: ____________________')

page(title='ACKNOWLEDGEMENT')
add('We express our sincere gratitude to our project guide, <b>'+GUIDE+'</b>, Assistant Professor, Department of Computer Science and Engineering (Artificial Intelligence and Machine Learning), Vidya Jyothi Institute of Technology, for guidance and encouragement during the preparation of this project.')
add('We thank <b>Dr. N. Anusha</b>, Associate Professor and Head of the Department, for academic support and for encouraging a systematic approach to project development and evaluation.')
add('We extend our thanks to <b>Dr. A. Srujana</b>, Principal, for the institutional support and learning environment. We also acknowledge the faculty members, our families and peers for their encouragement.')
add('We acknowledge the authors of the research papers cited in this report and the maintainers of the open-source tools used in Candidate Lab. Their work made it possible to implement and study document processing, transparent matching, web application development and software verification.')
story.append(Spacer(1,30));team()

page(title='ABSTRACT')
add(TITLE,'h2')
add('Resume screening involves comparing varied candidate descriptions against job requirements. Manual review can be difficult to reproduce, while opaque rankings can leave reviewers unable to understand how a result was produced. Candidate Lab addresses this problem through an evidence-led web application that combines explicit skill coverage with lexical text alignment and preserves the information used for each comparison.')
add('The application is implemented with React and TypeScript for the interface, Python and FastAPI for the API, and SQLAlchemy with SQLite for local persistence. PDF, DOCX and TXT resumes are parsed into editable text. A dictionary of supported skills and aliases links requirements to source passages. The default matching method combines required skill coverage, preferred skill coverage and TF-IDF cosine similarity into an inspectable score. Immutable matching snapshots preserve the job rubric, profile versions and component contributions.')
add('Candidates manage their own profiles; recruiters define jobs and record reasoned human reviews; auditors examine separate aggregate cohort reports and activity logs. Recruiter and auditor registration uses email-bound, expiring, single-use invitations. The audit demonstration reports simulated selection rates, Wilson confidence intervals and rate differences for arbitrary synthetic cohorts, with suppression below five records.')
add('Recorded verification includes ten backend tests and seven browser journeys, together with build and type checks. These results establish tested application behavior, not model accuracy. No real labeled hiring dataset was supplied; a trained hiring classifier, real demographic fairness validation and public cloud deployment are outside the current implementation. The project demonstrates a transparent local baseline and a foundation for future supervised evaluation and deployment hardening.')
add('<b>Keywords:</b> candidate matching; resume parsing; TF-IDF; explainability; human review; cohort audit; FastAPI; React.','small')

page(title='CONTENTS')
tab(['Chapter / section','Page'],[
['1. Introduction<br/>Background, problem statement, objectives and scope','1-2'],
['2. Literature Survey<br/>Lexical/semantic matching, explainability and fairness','3-4'],
['3. Feasibility Study<br/>Technical, operational and economic feasibility','5'],
['4. System Requirements<br/>Existing/proposed system, functional and technical needs','6-8'],
['5. System Design<br/>Architecture, UML, data model, scoring and audit design','9-16'],
['6. Software Implementation<br/>Modules, authentication, versions, code and local runtime','17-21'],
['7. System Testing<br/>Strategy, coverage and recorded outcomes','22-23'],
['8. Results and Output Screens<br/>Sign-in, registration, recruiter, evidence and audit views','24-27'],
['9. Conclusion','28'],['10. Future Scope','29'],['11. References','30'],['Appendix A. API and terminology quick reference','31']
],[400,69])
add('Preliminary pages: certificate, declaration, acknowledgement, abstract, contents and list of figures. Body page numbering begins at Chapter 1.','small')

page(title='LIST OF FIGURES AND ABBREVIATIONS')
tab(['Figure','Description','Page'],[
['5.1','Layered application architecture','9'],['5.2','Role-based use case diagram','10'],['5.3','Matching sequence diagram','11'],['5.4','Application activity diagram','12'],['5.5','Component diagram','13'],['5.6','Local deployment diagram','13'],['5.7','Logical data relationship diagram','14'],['8.1','Current simplified sign-in screen','24'],['8.2','Recruiter overview screen','25'],['8.3','Matching evidence and review screen','26'],['8.4','Aggregate cohort audit screen','27']
],[52,365,52])
tab(['Term','Meaning'],[['API','Application Programming Interface'],['ASGI','Asynchronous Server Gateway Interface'],['TF-IDF','Term Frequency-Inverse Document Frequency'],['RBAC','Role-Based Access Control'],['PBKDF2','Password-Based Key Derivation Function 2'],['UML','Unified Modeling Language'],['TPR / FPR','True Positive Rate / False Positive Rate']],[88,381])

# Body page 1
page(1,'INTRODUCTION')
sec('1.1 Background of the Study','Candidate screening requires a reviewer to connect the skills described in a resume with the skills needed for a job. Resumes differ in structure, vocabulary and level of detail. Job descriptions also combine essential requirements with contextual responsibilities and desirable qualifications. A score without visible evidence can therefore be difficult to interpret, reproduce or challenge.','Digital screening tools can help organize information, but automation alone does not make a comparison valid. A candidate may mention a skill without demonstrating competence, a parser may miss useful text, and a similarity model may reward wording rather than relevant ability. Effective decision support should preserve the distinction between extracted evidence, calculated alignment and a human judgment.')
sec('1.2 Project Context','Candidate Lab provides a local workspace for three roles: candidate, recruiter and auditor. Candidates submit profile evidence and can correct the text. Recruiters define explicit required and preferred skills, inspect matching explanations and record job-related review reasons. Auditors examine aggregate comparisons and a record of application activity.','The project title establishes the broader direction of fair and explainable machine learning. The implemented release deliberately starts with an inspectable baseline: dictionary-based skill evidence and TF-IDF text alignment. It does not claim a trained predictor of hiring success. This boundary helps evaluators distinguish demonstrated functionality from future research goals.')
sec('1.3 Motivation','The motivation is to make each stage of screening easier to inspect. Explicit rubrics clarify what is being compared, source passages explain skill matches, versioned profiles preserve corrections and saved snapshots retain historical explanations. A separate audit view supports investigation of group differences without exposing audit attributes to the matching engine.')

page(title='PROBLEM STATEMENT AND OBJECTIVES')
sec('1.4 Problem Statement','Develop an application that accepts candidate evidence, compares it with explicit job-related requirements, explains the resulting score and supports accountable human review. The system should enforce role boundaries, retain the information used for a matching run and provide an aggregate audit demonstration without claiming that synthetic comparisons establish real-world fairness.')
sec('1.5 Objectives','<b>Evidence preparation:</b> accept text PDFs, DOCX and TXT files; show extracted text and skill passages; allow correction before persistence.','<b>Transparent comparison:</b> distinguish required and preferred skills, calculate explicit coverage and text-alignment contributions, and display supporting passages.','<b>Traceability:</b> save profile versions, immutable run snapshots, review reasons and audit events.','<b>Controlled access:</b> scope candidate access to owned profiles; reserve matching for recruiters and aggregate auditing for auditors.','<b>Evaluation:</b> verify key API and browser workflows and document what those checks do and do not establish.')
sec('1.6 Scope','The implemented scope is one shared local workspace with a bounded synchronous matching process, a supported skill vocabulary and synthetic audit attributes. Original uploads are processed in memory; confirmed text is stored locally. PostgreSQL and container configuration are supplied as optional deployment paths.','The current scope excludes automatic hiring or rejection, automated email delivery, OCR, a production identity provider, multi-organization tenancy, a labeled training corpus and public hosting. These are described as future work rather than implied by the interface.')
sec('1.7 Organization of the Report','The following chapters review relevant approaches, assess feasibility, specify requirements, describe design and implementation, present testing evidence and output screens, and conclude with limitations and future improvements. The structure follows the supplied Batch-05 reference, with content rewritten for Candidate Lab.')

page(2,'LITERATURE SURVEY')
sec('2.1 Lexical Document Matching','TF-IDF represents documents using weighted term features. Terms frequent in one document but less common across the corpus can receive higher weight. Cosine similarity then measures the angular alignment between document vectors. The scikit-learn feature-extraction documentation describes this family of representations [1].','For this project, lexical matching provides a straightforward baseline with modest runtime requirements. It supports local processing without a remote language service. However, similar wording is not the same as equivalent competence, and different expressions of the same skill may not align. Candidate Lab supplements lexical alignment with explicit aliases and visible evidence passages.')
sec('2.2 Semantic Sentence Representations','Reimers and Gurevych describe Sentence-BERT as a method for deriving sentence embeddings that can be compared using cosine similarity [2]. Such representations can support comparison of semantically related text expressed with different words.','Candidate Lab includes an optional local Sentence Transformers integration. A compatible model must be obtained and configured separately. The verified default release does not enable that path and therefore does not claim semantic-model evaluation. Any future comparison should use a held-out, consented dataset with a documented relevance rubric.')
sec('2.3 Evidence Extraction','Document parsing and skill recognition are separate tasks. A parser recovers text from a file, while an extraction method identifies potentially relevant information in that text. The pypdf and python-docx documentation describe text-access interfaces for PDF and Word formats [3,4].','The current system uses explicit skill aliases and source sentences rather than a trained named-entity recognizer. This choice makes the vocabulary understandable and editable, but requires reviewers to handle negation, ambiguity and unsupported skills. Extraction quality must be evaluated separately from ranking quality.')

page(title='EXPLAINABILITY AND FAIRNESS CONTEXT')
sec('2.4 Explanation of Model Outputs','Lundberg and Lee introduce SHAP as a framework for attributing model predictions to input features [5]. Such methods are relevant when explaining a learned model, but they are not the only way to make a system inspectable.','Candidate Lab uses direct formula contributions: required coverage, preferred coverage and text alignment. Because these terms are explicit, the interface can show their exact arithmetic contribution. The project does not implement SHAP or LIME and does not describe its contribution bars as causal explanations.')
sec('2.5 Group Comparisons and Qualification Labels','Hardt, Price and Srebro examine equality-of-opportunity criteria for supervised learning [6]. This work motivates the distinction between comparing selection outcomes and comparing error rates conditional on valid outcome labels.','The current audit dashboard has no verified qualification labels. It can describe the fraction of synthetic profiles above a common score threshold, but it cannot establish true-positive or false-positive rates for qualified applicants. Equalized odds is therefore not an available evaluation result in this release.')
tab(['Approach','Project relevance','Current status'],[['TF-IDF + cosine','Local lexical baseline','Implemented'],['Skill aliases + passages','Inspectability of evidence','Implemented'],['Direct contribution formula','Arithmetic explanation','Implemented'],['Sentence embeddings','Potential semantic baseline','Optional, not evaluated'],['SHAP / supervised fairness','Learned-model evaluation context','Literature / future work']],[124,220,125])
sec('2.6 Identified Gap','The project focuses on connecting the comparison result to the underlying evidence and record history. It addresses an inspectability gap within a bounded application demonstration; it does not claim to outperform commercial applicant-tracking systems or solve hiring bias in general.')

page(3,'FEASIBILITY STUDY')
sec('3.1 Technical Feasibility','The application is technically feasible on an ordinary development laptop because it uses a browser interface, a Python API and an embedded local database. Default extraction and matching require no external AI service or GPU. React/TypeScript and FastAPI divide interface work from server-side validation and calculations.','Matching executes synchronously and rejects runs exceeding 500 profiles rather than silently truncating them. Uploads are limited to 2 MB, text length is bounded and PDF/DOCX checks limit processing. These controls define a practical demonstration boundary, not measured enterprise capacity.')
sec('3.2 Operational Feasibility','Separate role navigation keeps each user focused on an appropriate task. Candidates see owned profiles, recruiters see job and matching functions, and auditors see aggregate reports and events. Error messages explain validation failures; unsaved form changes use a confirmation dialog.','Operational limitations remain. Recruiter/auditor invitation creation requires a trusted local operator. Password recovery, email verification and retention administration have not been implemented. Users need an explanation of matching indices, evidence uncertainty and the fact that an internal review status does not send a message.')
sec('3.3 Economic Feasibility','The default stack uses open-source software and local computation, avoiding mandatory paid API calls or a separate database service for the demonstration. Existing computing equipment can support development and evaluation. This is a qualitative cost assessment; no measured hosting bill or market comparison is claimed.','Public deployment would introduce infrastructure, database, backup, monitoring, security and maintenance costs. Optional model use may introduce licensing and hardware considerations. These costs should be estimated after selecting a deployment environment and expected workload.')
sec('3.4 Risk and Mitigation','The main risks are extraction errors, vocabulary gaps, misleading score interpretation, proxy information in prose and unauthorized access. Mitigations include editable previews, evidence display, explicit limits, separate audit attributes, role enforcement and functional tests. Real applicant deployment would require stronger operational and governance controls.')

page(4,'SYSTEM REQUIREMENTS')
sec('4.1 Existing Approaches','A manual screening process reads each resume and compares it with a job. It allows contextual judgment, but different reviewers may apply different criteria and record inconsistent explanations. Spreadsheet and keyword-search workflows organize information but may lose source context or the version of the resume that was reviewed.','Opaque ranking tools can offer convenient ordering while leaving the reviewer uncertain about the meaning of the score. Without an explicit rubric and historical record, a later profile correction can make it difficult to reconstruct the original comparison. These are design concerns, not claims about every existing commercial system.')
sec('4.2 Proposed System','Candidate Lab combines a documented skill vocabulary, editable profile evidence, explicit job criteria and inspectable matching. Each run stores an immutable snapshot; a human review is recorded separately from the numerical score. A restricted auditor view describes synthetic group outcomes and activity history.')
tab(['Concern','Proposed behavior'],[['Inconsistent criteria','Required/preferred skill rubric'],['Unclear skill match','Requirement-to-passage evidence'],['Unexplained score','Three visible weighted contributions'],['Corrections obscure history','Profile versions and immutable snapshots'],['Role confusion','Server-enforced role/ownership checks'],['Unqualified fairness claims','Synthetic provenance, intervals and suppression']],[180,289])
sec('4.3 Expected Advantages','The implementation makes the evaluation process more inspectable and supports reproducibility of saved runs. These are functional advantages of the design. Improved hiring quality, reduced discrimination and time savings require separate empirical evaluation and are not reported as measured outcomes.')

page(title='FUNCTIONAL REQUIREMENTS')
tab(['ID','Requirement','Role / result'],[
['FR-01','Register and sign in with validated credentials','All users; privileged roles need invitation'],['FR-02','Generate single-use, expiring role invitations','Trusted local administrator CLI'],['FR-03','Upload or paste resume text and preview skills','Candidate/recruiter'],['FR-04','Save and correct profile evidence with version checks','Candidate owner/recruiter'],['FR-05','Create jobs using required and preferred skills','Recruiter'],['FR-06','Run matching across the supported cohort','Recruiter; snapshot persisted'],['FR-07','Inspect score components and source passages','Recruiter'],['FR-08','Record review status with job-related reason','Recruiter; review history appended'],['FR-09','Show real overview counts from the database','Recruiter'],['FR-10','Inspect aggregate cohort report and export JSON','Auditor'],['FR-11','Show application event records','Auditor'],['FR-12','Reject unauthorized role/ownership requests','Backend enforcement']
],[47,255,167])
sec('4.4 Acceptance Conditions','A new candidate must begin with an empty owned-profile library. Changing the role selection in a browser must not grant privileged access. A profile update with an old version must return a conflict. A saved matching snapshot must retain its old evidence after a correction. An auditor must not receive raw profile text or individual ranking snapshots.')
sec('4.5 Data Entry Rules','Email addresses are normalized and checked for duplicate accounts. Registration requires matching passwords of at least twelve characters with letters and numbers. Supported skill names are normalized, and a skill cannot be both required and preferred. Human review requires a substantive reason of at least ten characters.')

page(title='SOFTWARE, HARDWARE AND QUALITY REQUIREMENTS')
tab(['Category','Requirement / use'],[['Operating environment','Windows development environment; browser-based interface'],['Python','Python 3.11+ recommended by setup; backend dependencies in requirements.txt'],['Frontend tooling','Node.js 20.19+ and npm; Node 22 used in container build configuration'],['Browser','Modern browser; recorded browser tests use installed Chrome'],['Database','SQLite by default; optional PostgreSQL through DATABASE_URL'],['Document formats','Text PDF, DOCX and UTF-8 TXT; no integrated OCR'],['Suggested machine','Modern multicore laptop, 8 GB RAM and free space for dependencies; planning guidance, not benchmarked minimum'],['Network','Not required for default local inference after dependencies are installed; setup downloads require connectivity']],[125,344])
sec('4.6 Non-functional Requirements','<b>Usability:</b> readable forms, clear action names, responsive layout, explicit loading/error states and preserved input on failure.','<b>Security:</b> server-side role checks, ownership checks, password hashing, opaque sessions, origin restrictions and bounded upload handling.','<b>Traceability:</b> immutable evidence snapshots, version-conflict protection, reasoned reviews and append-only application events.','<b>Maintainability:</b> shared frontend controls, typed API interfaces, modular matching logic and documented configuration.')
sec('4.7 Evaluation Boundaries','No throughput, latency service-level objective, complete accessibility conformance or production penetration-test result is established. The recorded tests verify selected behaviors. These claims must remain separate from performance and model-quality measurements.')

page(5,'SYSTEM DESIGN')
sec('5.1 Layered Architecture','The architecture separates presentation, application processing and persistence. The React interface collects inputs and displays evidence. FastAPI controls permissions and request validation. Matching logic calculates explicit evidence coverage and text alignment. SQLAlchemy stores and retrieves the records used by these services.')
story.append(Diagram('architecture',290));cap('Figure 5.1: Layered architecture of Candidate Lab')
sec('5.1.1 Presentation and Application Boundaries','The browser cannot grant itself a role by changing visible controls. Backend dependencies check the authenticated session and approved role before processing protected operations. The frontend mirrors those boundaries through role-specific navigation, but the server remains authoritative.')
sec('5.1.2 Evidence and Audit Separation','Audit attributes occupy a separate table and are not passed into the ranking function. The report endpoint combines a saved run with approved synthetic attributes only after an auditor access check. This separation avoids using the audit label as an explicit score input; it does not guarantee removal of proxy information from free text.')

page(title='ROLE-BASED USE CASE DESIGN')
story.append(Diagram('usecase',330));cap('Figure 5.2: Use case view of user responsibilities')
sec('5.2 Candidate Use Cases','A candidate registers, signs in, uploads or pastes evidence, previews skills and saves or corrects owned profiles. Candidate access excludes the recruiter ranking and auditor reports. The current workspace does not include job applications, interview scheduling or a candidate-facing selection decision.')
sec('5.3 Recruiter Use Cases','A recruiter creates job rubrics, accesses workspace profiles, starts matching, inspects evidence and records a review. Overview cards summarize actual records rather than invented recruitment performance indicators. Review records count actions, not unique hires.')
sec('5.4 Auditor and Administrator Use Cases','Auditors inspect aggregate cohort reports and event records. The local administrator generates invitations using a command; there is no separate administrator dashboard. Invitation creation does not register the invited person or verify email ownership.')

page(title='SEQUENCE DESIGN FOR MATCHING')
story.append(Diagram('sequence',325));cap('Figure 5.3: Sequence of a recruiter matching request')
sec('5.5 Request Lifecycle','The recruiter selects Run matching for a job. React sends a POST request to the matching endpoint. FastAPI verifies the session and recruiter role, looks up the job and retrieves the candidate cohort. If the job is absent, no profiles exist or the cohort exceeds the supported bound, the request returns a specific error.')
sec('5.5.1 Calculation and Persistence','The matching function prepares skill-bearing text, calculates similarity and attaches evidence for each requirement. It returns stable score ordering and a method identifier. The API stores the job snapshot and result JSON in a new run, records an audit event and returns the saved result to the browser.')
sec('5.5.2 Error Handling','A configured local semantic model that cannot load causes an explicit service error rather than silently pretending semantic inference succeeded. The default local TF-IDF mode does not require that optional model. Interface errors preserve context and provide recovery or retry guidance.')

page(title='ACTIVITY DESIGN')
story.append(Diagram('activity',365));cap('Figure 5.4: Activity flow from profile evidence to review and audit')
sec('5.6 Profile Preparation','Parsing creates a draft preview, not an automatically saved candidate. A user checks the text and passages, corrects extraction problems and explicitly saves the result. Very short text or missing vocabulary evidence produces warnings or validation feedback.')
sec('5.6.1 Human Review Branch','After a matching run, the recruiter opens a profile explanation, checks the requirement passages and records a reasoned status. The label is an internal review record and does not change the matching score. Additional assessment of skill proficiency remains a human task.')
sec('5.6.2 Audit Branch','An auditor chooses a saved run and adjusts one common cutoff to simulate a selection-rate comparison. The report remains separate from the recruiter review. No branch automatically hires or rejects a person, sends an email or infers a demographic group.')

page(title='COMPONENT AND DEPLOYMENT DESIGN')
story.append(Diagram('component',190));cap('Figure 5.5: Main software components and their interfaces')
add('Shared frontend components own common behavior such as forms, notices, dialogs and paging. The API module owns persistence and authorization, while matching.py contains extraction, score and audit arithmetic. The local invitation module uses the same configured database.')
story.append(Spacer(1,12));story.append(Diagram('deployment',165));cap('Figure 5.6: Current local deployment on one laptop')
sec('5.7 Current Deployment Boundary','Uvicorn serves the FastAPI application on 127.0.0.1:8000. The API also serves built frontend assets from dist/. The SQLite file persists data on the laptop. This loopback address is not a public internet endpoint and cannot be shared as a working remote link.')
sec('5.7.1 Optional Deployment Configuration','A Dockerfile provides a Node build stage and Python runtime stage. Compose describes an application service and PostgreSQL database with persistent storage. These are supplied configurations, not evidence of a verified public deployment. HTTPS, secure cookie configuration, identity administration and backup operations remain deployment requirements.')

page(title='DATABASE DESIGN')
story.append(Diagram('er',345));cap('Figure 5.7: Logical data relationships (not a physical foreign-key constraint diagram)')
sec('5.8 Persistent Entities','Users store normalized email, role and password hash. Login sessions store a token hash and expiry. Invitations store a hashed code, bound email/role, expiry and used flag. Candidate and ProfileVersion records preserve confirmed evidence and its history. Job records hold the explicit rubric.')
sec('5.8.1 Results and Accountability','A Run stores job information and profile result snapshots as JSON. Review stores a result reference, reviewer, status, reason and timestamp. AuditLog records the actor, action, object and time. AuditAttribute is separate and currently contains only synthetic fixture labels.')
sec('5.8.2 Design Limits','The arrows show application-level references and responsibilities. They must not be read as a claim that all SQL foreign keys or cascade rules are declared. The application creates initial tables at startup; versioned schema migrations, retention/deletion workflows and broader integrity hardening are future requirements.')

page(title='MATCHING ALGORITHM DESIGN')
sec('5.9 Skill Evidence and Text Preparation','Supported canonical skills map to aliases. Sentence-level matches provide a passage for a requirement. For example, pytest and integration tests can support Testing, while PostgreSQL can also support SQL. Skill-bearing passages are used for alignment; common contact/identity headers are filtered heuristically.','The filter is not complete anonymization. A name or proxy characteristic can remain inside prose, and a keyword match can misunderstand negation. Evidence remains editable, and absence of a detected passage does not prove absence of skill.')
sec('5.9.1 TF-IDF and Cosine Similarity','The query is formed from required and preferred skills. TF-IDF uses unigrams, bigrams and sublinear term frequency to create a matrix for that query and the profile texts. Cosine similarity measures lexical alignment between the query vector and each profile vector. The corpus is fitted for each run; adding profiles can therefore change the alignment term.')
tab(['Component','Value','Weight'],[['Required coverage','Matched required skills / all required skills','0.60'],['Preferred coverage','Matched preferred skills / all preferred skills','0.15'],['Text alignment','Cosine similarity of query and profile','0.25']],[135,262,72])
add('<b>Score = 100 x (0.60R + 0.15P + 0.25L)</b>','center')
sec('5.9.2 Explanation and Special Case','If no preferred skills exist, the weights become 0.75, 0 and 0.25. Components are displayed as exact point contributions. A profile with R = 1, P = 1 and L = 0.10 scores 77.5. This is a matching index, not a calibrated probability. Scores are sorted descending, with candidate identifier used as a stable tie-breaker.')

page(title='AGGREGATE AUDIT DESIGN')
sec('5.10 Cohort Selection Rates','For a selected run and a shared cutoff t, the report counts profiles whose saved score is at least t. For a group g, the simulated rate is the number above the cutoff divided by the audited group size. Unattributed profiles are counted separately and excluded from group comparisons.','The displayed rate difference is the maximum group rate minus the minimum group rate when at least two groups can be compared without suppression. Current Cohort A/B labels are arbitrary synthetic labels, not demographic identities or valid qualification labels.')
sec('5.10.1 Uncertainty and Suppression','The report calculates 95% Wilson intervals for displayed rates. These intervals communicate the wide uncertainty associated with small samples; they do not certify fairness. If a group has fewer than five records, its selected count, rate and interval are suppressed. Group sample counts remain visible.')
tab(['Illustration from a saved demonstration','Cohort A','Cohort B'],[['Group size','6','6'],['Profiles above cutoff 60','3 (50.0%)','3 (50.0%)'],['Profiles above cutoff 65','2 (33.3%)','1 (16.7%)']],[255,107,107])
add('At cutoff 60, the displayed gap is 0 percentage points. At cutoff 65, it is 16.7 percentage points. This is a descriptive demonstration; no policy recommendation follows from those values.')
sec('5.10.2 Limits of the Fairness Claim','Without validated outcome labels, the system cannot report qualification-conditioned TPR/FPR or equalized odds. Without real consented demographic attributes and a representative evaluation population, the synthetic report cannot establish demographic fairness. These limits are visible in the audit interface and remain central to interpreting the results.')

page(6,'SOFTWARE IMPLEMENTATION')
sec('6.1 Frontend Implementation','React renders role-specific pages and shared controls. TypeScript defines shapes for users, jobs, candidates, matching runs and audit responses. Query-string navigation preserves page and search state, while AbortController prevents superseded requests from replacing newer results. CSS implements the navy/teal visual system, focus states and responsive layouts.','The sign-in page now uses a minimal introduction panel without the earlier illustrative evidence box. Academic/prototype branding was removed from the product interface for a professional presentation; sample-data provenance and scoring limitations remain visible where they affect interpretation.')
sec('6.2 Backend Implementation','FastAPI routes JSON and multipart requests and uses dependency functions for session and role checks. Pydantic validates field lengths, allowed roles, passwords, skill lists and review input. Uvicorn runs the ASGI application. SQLAlchemy performs database queries and transactions.')
tab(['Module','Responsibility'],[['src/main.tsx','Navigation, role screens, jobs/profiles/evidence/audit'],['src/Registration.tsx','Validated account creation and invitation input'],['src/api.ts / components.tsx','Typed requests and shared interaction controls'],['backend/app.py','API, authentication, storage and access enforcement'],['backend/matching.py','Skill extraction, matching and cohort calculations'],['backend/invite.py','Local administrator invitation command']],[178,291])
sec('6.3 Technology Selection','SQLite reduces local setup requirements; React supports reusable interaction patterns; FastAPI makes validation and role checks explicit. TF-IDF provides a local lexical baseline. Sentence Transformers, PostgreSQL and Docker configuration are optional and are not presented as active verified services.')

page(title='REGISTRATION AND SECURITY IMPLEMENTATION')
sec('6.4 Account Creation','The registration form supports Candidate, Recruiter and Auditor. Candidate registration is direct. A recruiter or auditor must supply a code generated by a local administrator for the same normalized email and role. Codes expire, are stored only as hashes and are redeemed through a conditional transaction that marks them used.','Registration checks duplicate email, password confirmation and a password of at least twelve characters with letters and numbers. A successful response returns to sign-in with email filled and passwords cleared. Registration does not automatically authenticate the new account or allow an existing candidate to self-upgrade a role.')
sec('6.4.1 Session Handling','Passwords use salted PBKDF2-HMAC-SHA256 with 310,000 iterations. Successful login creates a random opaque token; its hash and expiry are stored in the database. The browser receives an HttpOnly, SameSite=Strict session cookie. Session validation occurs on protected API calls. Logout removes the stored session.','The local HTTP configuration does not set Secure unless configured through the environment. Public HTTPS deployment must enable it. Origin checks restrict browser mutations to approved origins, and process-local throttles limit login and registration attempts. These mechanisms do not replace a production identity and abuse-control system.')
sec('6.4.2 Access Boundaries','Candidates are limited to owned profiles. Recruiters can access workspace profiles, jobs and matching but cannot read auditor reports. Auditors can read aggregate audits and event logs but cannot retrieve candidate text or individual ranking snapshots. The backend rejects violations even if a user guesses a route.')
sec('6.4.3 Operational Gaps','No email verification, password-reset delivery or organizational SSO is implemented. The local administrator command is protected by machine/database access rather than a dedicated administration service. Multi-tenant isolation and a complete privacy-retention workflow remain future work.')

page(title='DOCUMENTS, VERSIONS AND REVIEW RECORDS')
sec('6.5 Resume Processing','A multipart upload is accepted only for PDF, DOCX or TXT. The parser reads at most the permitted size; PDFs must have an appropriate signature, be unencrypted and fit the page limit. DOCX archives are checked for expanded size before paragraph and table-cell text is read. TXT input uses UTF-8 decoding.','The interface displays editable text and extraction warnings. A scanned PDF without usable text needs external OCR or manual text entry. Original uploads are not retained. Saving persists the confirmed text, dictionary evidence and warnings. File checks constrain processing but do not constitute antivirus scanning or parser isolation.')
sec('6.5.1 Version-conflict Protection','Each update includes the version the user loaded. The backend compares it with the current version and performs a conditional update. If another edit has already changed the record, the request returns a conflict rather than overwriting the newer text. A successful update appends a ProfileVersion record.')
sec('6.5.2 Immutable Runs','A matching run records the job snapshot, method identifier, profile versions, skill-bearing text, requirements and contribution values. Corrections affect future runs, while the stored result remains unchanged. The current method label is skill-tfidf-v1 unless an optional local semantic model is explicitly configured.')
sec('6.5.3 Human Review','A review appends a status and reason linked to a run and candidate. The result screen overlays the latest review without mutating the saved numerical score. Status options are needs_review, shortlisted and more_information. These labels do not create employment decisions or automatically dispatch communications. Audit events provide a separate record of the action.')

page(title='IMPLEMENTATION LOGIC EXCERPTS')
sec('6.6 Score Calculation','The following shortened excerpt reflects the implemented weighting logic. Coverage and similarity values are bounded feature terms; multiplying by 100 expresses their point contributions.')
code='''required_weight = 0.60 if preferred else 0.75
preferred_weight = 0.15 if preferred else 0.0
components = [
    required_weight * required_coverage * 100,
    preferred_weight * preferred_coverage * 100,
    0.25 * text_alignment * 100,
]
score = round(sum(components), 2)'''
story.append(Preformatted(code,ParagraphStyle('code',fontName='Courier',fontSize=9.2,leading=13,backColor=LIGHT,borderPadding=10,spaceAfter=14)))
sec('6.6.1 Invitation Redemption','Conceptually, a privileged registration updates exactly one unused invitation whose hash, email, role and expiry match. If the update affects no record, registration fails. Duplicate account creation rolls back the transaction. This prevents a browser role selector from becoming a privilege-granting mechanism.')
code2='''match = invitation_hash == hash(submitted_code)
eligible = match and email_matches and role_matches
eligible = eligible and not used and expires > now
# In the application: conditional SQL UPDATE,
# followed by account creation in one transaction.'''
story.append(Preformatted(code2,ParagraphStyle('code2',fontName='Courier',fontSize=9.2,leading=13,backColor=LIGHT,borderPadding=10,spaceAfter=14)))
sec('6.6.2 Evidence Handling','Aliases are matched with word-boundary-aware regular expressions, and the first supporting sentence is retained for a requirement. The text filter excludes recognized identity/contact headers, but cannot promise full de-identification. A reviewer should check the actual passage rather than equating a keyword with competence.')
add('Excerpts are condensed for readability. The authoritative implementation is in backend/app.py and backend/matching.py; no credentials or personal resume data are reproduced.','small')

page(title='LOCAL EXECUTION AND CONFIGURATION')
sec('6.7 Local Runtime','After Python and Node dependencies are installed, npm run build checks types and creates static frontend assets. Starting Uvicorn serves the API and those assets on http://127.0.0.1:8000. start.ps1 provides a Windows helper. The default SQLite file is data/candidate-lab.db.')
tab(['Setting / tool','Purpose'],[['DEMO_MODE','Seeds sample accounts, jobs, profiles and initial run only when enabled on an empty user database'],['DATABASE_URL','Selects SQLite by default or an explicitly configured server database'],['ALLOWED_ORIGINS','Defines approved browser origins for requests'],['COOKIE_SECURE','Enables the Secure cookie attribute for HTTPS deployments'],['SEMANTIC_MODEL_PATH','Points to a separately cached local Sentence Transformers model'],['Vite dev server','Port 5173 with /api proxy to the backend during development']],[165,304])
sec('6.7.1 Optional Server Configuration','The Dockerfile builds frontend assets in a Node stage and packages a Python runtime. Compose defines a PostgreSQL service and application service with a loopback host binding. The database password must be configured separately. Docker/PostgreSQL operation has not been exercised in the recorded local verification.')
sec('6.7.2 Public Sharing Status','The project has not been publicly deployed. A loopback URL points to the computer opening it, so a friend cannot use that URL to reach this laptop. Public hosting would require a reachable application server, durable database, HTTPS, secure configuration, backup strategy and explicit handling of sample accounts and applicant data.')
sec('6.7.3 Reproducibility','package-lock.json and dependency manifests describe the environment, while project documentation records startup and testing commands. The source ZIP excludes local credentials, databases and dependency folders. Configuration support should not be confused with proof of an online deployment.')

page(7,'SYSTEM TESTING')
sec('7.1 Testing Strategy','The verification strategy checks the application at calculation, API and browser levels. Backend tests use temporary databases so that assertions do not depend on the user workspace. Browser tests use fictional evaluation records and the local application. The tests verify behaviors and boundaries; they are not a substitute for an empirical hiring study.')
sec('7.2 Backend and Integration Checks','pytest with FastAPI TestClient/HTTPX covers authentication, candidate ownership, role boundaries, document validation, profile conflicts, matching snapshots, review reasons, invitation rules and database counts. Calculation-level checks verify contribution arithmetic, synthetic audit suppression and interval behavior.','Ten backend tests were recorded as passing. Several tests make multiple related assertions in one workflow; ten is the count of test functions/parameterized cases, not the number of individual assertions or a model accuracy percentage.')
sec('7.3 Browser Checks','Playwright in Chrome checks complete workflows: recruiter job/profile/match/review, auditor cutoff/export/events, invalid login and unsaved form behavior, candidate restrictions, and new registration for all three roles. Seven browser journeys were recorded as passing. A focused additional mobile candidate-registration check also passed.','Build-time TypeScript validation and ESLint passed. The sign-in and overview layouts were visually inspected, including 390-pixel mobile width. These checks do not establish complete accessibility conformance, adversarial document safety or production load capacity.')
sec('7.4 Test Environment and Limits','The recorded environment is a Windows laptop, a local Uvicorn/FastAPI server, SQLite and installed Chrome. One TestClient dependency deprecation warning was non-blocking. No performance benchmark, public cloud test, PostgreSQL deployment test or optional semantic-model evaluation is claimed. Verification details are retained in VERIFICATION.md.')

page(title='TEST CASES AND RECORDED OUTCOMES')
tab(['ID','Scenario','Expected / recorded result'],[
['TC-01','Unauthenticated protected request','401; passed'],['TC-02','Candidate reads another owner profile','403; passed'],['TC-03','Auditor retrieves raw profiles/ranking','403; passed'],['TC-04','Valid TXT, DOCX and text PDF parsing','Usable preview; passed'],['TC-05','Malformed / unsupported / oversized file','Validation error; passed'],['TC-06','Profile save with stale version','409 conflict; passed'],['TC-07','Profile corrected after matching','Old snapshot unchanged; passed'],['TC-08','Score contribution sum','Matches saved score within rounding; passed'],['TC-09','Review without substantive reason','Rejected; valid review persists; passed'],['TC-10','Registration invitation wrong/expired/used','Privileged registration rejected; passed'],['TC-11','Duplicate email and password mismatch','Explicit error; passed'],['TC-12','Small audit cohort','Rate suppressed; passed'],['TC-13','New profile changes overview totals','Database-backed count updates; passed'],['TC-14','Role-based registration and first login','Correct landing and access; passed'],['TC-15','Mobile form, dialog and report export','Selected browser checks passed']
],[50,213,206])
sec('7.5 Interpretation','No dataset-wide precision, recall, NDCG, time-saving percentage or discrimination-reduction result is reported. Such outcomes would need valid annotations, a specified evaluation protocol, representative sampling and uncertainty analysis. Functional test success should be presented as application verification only.')

page(8,'RESULTS AND OUTPUT SCREENS')
sec('8.1 Sign-in and Registration Interface','The current sign-in page presents a concise product introduction and account controls. Candidates can register directly; recruiter and auditor registration reveals an invitation field. Errors retain entered data, and successful registration returns to login with passwords cleared.')
story.append(Shot('minimal-signin.png',maxh=330,crop=(2035,853)));cap('Figure 8.1: Simplified sign-in screen after the final visual refinement')
sec('8.1.1 Role-specific Entry','After authentication, the server-assigned role determines the available workspace. Demo-account shortcuts are labelled as sample access and do not grant arbitrary privileges. The invitation command is operated separately by a trusted local administrator.')
sec('8.1.2 Candidate Profile Preparation','A new candidate starts with no owned profiles. Add profile accepts a file or pasted text and shows an extraction ledger. Preview alone does not save a record; Save profile persists the confirmed evidence. The fictional text preview used in the tour was discarded without creating a profile.')
add('Screens in this chapter are recorded outputs of the implemented application. Counts and timestamps reflect the captured state, not a fixed production dataset. Sample and browser-test records may appear.','small')

page(title='RECRUITER OVERVIEW OUTPUT')
sec('8.2 Dashboard and Job Rubrics','The overview shows actual counts of saved jobs, candidate profiles, matching snapshots and human review actions. The profile card states how many labelled sample profiles are included. These are database totals, not invented hiring success statistics.')
story.append(Shot('professional-dashboard.png',maxh=310));cap('Figure 8.2: Recruiter overview with database-backed summary cards')
sec('8.2.1 Navigation and Actions','Create job opens a form for the title, description and required/preferred skill lists. Candidate profiles opens the evidence library. Matching evidence opens saved comparisons. Search and pagination help navigate bounded lists. Each card routes to the related area; the review count refers to recorded actions, not unique candidates hired.')
sec('8.2.2 Observed Behavior','A new profile increases the stored profile count, while the synthetic-profile count remains unchanged. This behavior was tested against an isolated database. The captured screen includes development evaluation jobs; their presence reflects saved test records and does not imply real vacancies or a recruitment campaign.')
sec('8.2.3 Professional Presentation','The interface uses a consistent navy/teal palette and shared controls. Academic/prototype branding and the illustrative left-side evidence box were removed from sign-in as requested. Important sample-data and human-review limitations remain visible in the functional workspace.')

page(title='MATCHING EXPLANATION AND HUMAN REVIEW')
story.append(Shot('evidence-desktop.png',maxh=370,crop=(808,530,420,690)));story.append(Spacer(1,8));cap('Figure 8.3: Detail of recorded score components and supporting requirement passages')
sec('8.3 Reading the Result','The ranking displays a matching index, required-evidence count and latest review label. Opening Evidence shows the profile version and exact arithmetic contributions. Each requirement is paired with a supporting sentence or a message that no evidence was found. A missing match is not proof that the person lacks the skill.')
sec('8.3.1 Review Outcome','A recruiter can record needs_review, shortlisted or more_information with a reason. The saved review is displayed alongside evidence, while the numerical snapshot remains unchanged. This is an internal accountability record, not an automated employment decision or notification.')

page(title='AUDIT OUTPUT AND RESULT INTERPRETATION')
story.append(Shot('audit-mobile.png',maxh=320,crop=(20,800,340,650)));story.append(Spacer(1,8));cap('Figure 8.4: Detail of aggregate counts, cohort rates and uncertainty in the mobile report')
sec('8.4 Aggregate Report','The auditor selects a matching snapshot and shared score cutoff. The report shows audited and unattributed counts, cohort rates, sample sizes, Wilson intervals and a descriptive rate difference. JSON export captures the report; the audit trail shows related application actions and times.')
sec('8.4.1 What Was Demonstrated','In one saved example, cutoff 60 produced 50% above the cutoff in both synthetic groups. At cutoff 65, the rates became 33.3% and 16.7%. The cutoff changed the simulated comparison, not the scores. This demonstrates the dashboard interaction, not a valid hiring policy or real demographic evaluation.')
sec('8.4.2 Overall Result','The application demonstrates local profile processing, explicit matching, evidence inspection, access boundaries and traceable reviews. The recorded ten backend tests and seven browser journeys support these functional claims. No learned-model accuracy, fairness certificate or public deployment result is asserted.')

page(9,'CONCLUSION')
add('Candidate Lab implements an evidence-led workflow for candidate matching and human review. It connects explicit job requirements to resume passages, calculates a visible matching index and preserves the information used to produce each result. The main achievement is an integrated, inspectable application rather than an unsupported claim of automated hiring intelligence.')
add('The system brings together a React/TypeScript interface, FastAPI services, SQLAlchemy/SQLite persistence, document parsers and a TF-IDF-based matching baseline. Candidates can manage owned profiles; recruiters can define rubrics and record reasons; auditors can inspect separate aggregate reports and application events. Expiring role invitations and backend permission checks support controlled access in the shared local workspace.')
add('Version-conflict handling protects corrections, while immutable snapshots retain historical explanations. Direct contribution terms clarify why points were awarded. These features make the software easier to demonstrate and examine, but keyword evidence and lexical similarity still require contextual interpretation. A profile can mention a technology without showing proficiency, and useful information can be missed during parsing or vocabulary matching.')
add('Recorded verification demonstrates selected functional behavior through ten backend tests and seven browser journeys, plus build, type and interface checks. This does not establish production readiness or predictive quality. The synthetic cohort audit illustrates rates and uncertainty but cannot establish fairness in real applicant populations.')
add('The project therefore provides a coherent foundation for further research. A next stage should collect consented annotations, compare lexical and semantic baselines, evaluate relevance and cohort outcomes on held-out data and harden identity, retention and deployment operations. Human oversight and accurate communication of limitations remain essential as the system evolves.')
sec('9.1 Contribution Summary','The deliverable is a working local application with transparent evidence matching, role-based workflows, account registration, historical records, aggregate audit demonstration and documented verification. The report distinguishes these implemented functions from optional configurations and proposed extensions.')

page(10,'FUTURE SCOPE')
sec('10.1 Validated Learning and Ranking Evaluation','Collect consented resume-job relevance annotations under a documented, job-related rubric. Use multiple annotators and report agreement. Split by candidate and job family to reduce leakage, then compare skill/TF-IDF, semantic and supervised approaches on held-out data. Suitable ranking measures include recall at k and NDCG at k, with uncertainty estimates; no such results are claimed for the present release.')
sec('10.2 Extraction and Explanation','Evaluate passage extraction independently and add tests for negation, abbreviations and unsupported skills. Introduce OCR for image-only documents through an isolated processing service. If a learned model is added, evaluate appropriate explanations and preserve provenance for the model, data, rubric and vocabulary versions.')
sec('10.3 Fairness and Governance','Obtain approved, consented audit attributes without inferring protected characteristics. Define the target population and valid qualification labels before selecting fairness measures. Examine intersectional and small-sample effects, report uncertainty and evaluate any mitigation against relevance and operational tradeoffs. A single threshold gap should not be treated as proof of fairness.')
sec('10.4 Production Operations','Add email verification and password recovery, organization-specific identity, tenant isolation, database migrations, isolated parsing, monitoring, backups and retention/deletion workflows that include historical snapshots. Replace process-local throttles with operational controls and use durable workers if workload requirements exceed bounded synchronous processing.')
sec('10.5 Deployment and Usability','Verify the optional PostgreSQL/container path, configure HTTPS and secure cookies, and deliberately manage sample accounts before public hosting. Conduct accessibility testing and usability studies with representative candidates, recruiters and auditors. Notifications or candidate applications should be introduced only with clear authorization and lifecycle rules.')

page(11,'REFERENCES')
refs=[
('[1] scikit-learn developers. Text feature extraction documentation.','https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction'),
('[2] Reimers, N., and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP.','https://aclanthology.org/D19-1410/'),
('[3] pypdf developers. Extract text from a PDF.','https://pypdf.readthedocs.io/en/stable/user/extract-text.html'),
('[4] python-docx developers. Documentation.','https://python-docx.readthedocs.io/en/latest/'),
('[5] Lundberg, S. M., and Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. Advances in Neural Information Processing Systems 30.','https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html'),
('[6] Hardt, M., Price, E., and Srebro, N. (2016). Equality of Opportunity in Supervised Learning. Advances in Neural Information Processing Systems 29.','https://proceedings.neurips.cc/paper_files/paper/2016/hash/6a9659feb1216f14f7384ba499518b38-Abstract.html'),
('[7] FastAPI. Official documentation.','https://fastapi.tiangolo.com/'),
('[8] React. Official documentation.','https://react.dev/'),
('[9] SQLAlchemy. Official documentation.','https://docs.sqlalchemy.org/'),
('[10] Playwright. Test documentation.','https://playwright.dev/docs/intro'),
]
for desc,url in refs:
    add(desc,'small');add('<link href="'+url+'" color="#126c68">'+escape(url)+'</link>','small')
add('[11] Candidate Lab implementation: package.json, requirements.txt, backend/, src/, tests/, VERIFICATION.md, README.md and EVALUATION.md. Local project source reviewed 2 November 2026.','small')
add('[12] Batch-05.pdf, user-supplied institutional report. Used only as the structural/presentation reference and for the institution, guide and academic year confirmed by the user. Subject matter and unrelated text were not reused.','small')

page(title='APPENDIX A: API AND TERMINOLOGY')
tab(['Endpoint group','Purpose / access'],[['POST /api/auth/register','Create candidate or invited privileged account'],['POST /api/auth/login / logout','Start or end authenticated session'],['GET /api/auth/me','Return current user identity/role'],['POST /api/resumes/parse','Parse supported document into preview'],['GET / POST / PUT /api/candidates','List, create or version-update permitted profiles'],['GET / POST /api/jobs','List or create job rubrics; recruiter creates'],['POST /api/jobs/{id}/runs','Create immutable matching result; recruiter'],['GET /api/runs/{id}','Inspect saved ranking; recruiter'],['POST /api/runs/{id}/reviews','Append human review; recruiter'],['GET /api/overview','Stored-record totals; recruiter'],['GET /api/audit/fairness/{id}','Aggregate synthetic-cohort report; auditor'],['GET /api/audit/events','Activity records; auditor']],[232,237])
sec('A.1 Terminology','<b>Rubric:</b> the explicit required and preferred skills for a job.<br/><b>Evidence:</b> text supporting a detected skill; not proof of proficiency.<br/><b>Snapshot:</b> saved information from one matching run.<br/><b>Matching index:</b> a weighted alignment score, not a hiring probability.<br/><b>Cohort:</b> a group used for an aggregate comparison; current labels are synthetic.<br/><b>Percentage points:</b> the arithmetic difference between two percentages.')
add('Documentation note: sample accounts, passwords, invitation codes and personal resume text are not reproduced in this report. Signature fields require completion by the relevant individuals.','small')

def roman(n):
    out=''
    for val,s in [(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=val:out+=s;n-=val
    return out
def footer(c,doc):
    if doc.page==1:return
    c.setStrokeColor(colors.HexColor('#adb7be'));c.line(72,40,A4[0]-54,40)
    c.setFillColor(INK);c.setFont('TNR',9)
    c.drawString(72,27,'Candidate Lab | CSE (Artificial Intelligence and Machine Learning)')
    number=roman(doc.page-1) if doc.page<=7 else str(doc.page-7)
    c.drawRightString(A4[0]-54,27,number)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=72,rightMargin=54,topMargin=48,bottomMargin=54,title='Candidate Lab - Final Project Report',author='; '.join(a for a,b in TEAM),subject=TITLE)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(str(OUT))
print('Expected pages:',physical,'Actual pages:',len(reader.pages))
for i,pg in enumerate(reader.pages):
    txt=pg.extract_text() or ''
    print(i+1,len(txt),txt[:80].replace('\n',' '))
print(OUT)
