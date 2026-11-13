from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/pdf/Candidate_Lab_Project_Differentiators.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
NAVY=colors.HexColor('#142b40');TEAL=colors.HexColor('#126c68');LIGHT=colors.HexColor('#eef4f6')
s=getSampleStyleSheet()
for name,size,leading,font in [('TitleD',25,30,'Helvetica-Bold'),('HeadingD',17,22,'Helvetica-Bold'),('SubD',12,17,'Helvetica-Bold'),('BodyD',10.5,16,'Helvetica'),('CellD',9,13,'Helvetica'),('SmallD',8.5,12,'Helvetica')]:
    s.add(ParagraphStyle(name=name,fontName=font,fontSize=size,leading=leading,textColor=NAVY,spaceAfter=10,spaceBefore=8 if name=='SubD' else 0))
story=[]
def p(t,style='BodyD'):return Paragraph(t,s[style])
def add(t,style='BodyD'):story.append(p(t,style))
def heading(t):add(t,'SubD')
def table(headers,rows,widths):
    t=Table([[p('<b>'+x+'</b>','CellD') for x in headers]]+[[p(x,'CellD') for x in r] for r in rows],colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce9ec')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)]));story.append(t)
add('CANDIDATE LAB / EVALUATION BRIEF','SmallD')
add('How our project differs','TitleD')
add('Fair and Explainable Machine Learning for Automated Candidate Selection and Skill Matching')
add('Prepared 2 November 2026','SmallD')
heading('The central contribution')
add('Candidate Lab connects <b>matching scores, source evidence, profile corrections, human review and aggregate auditing</b> in one application. Its strongest differentiator is a traceable review workflow rather than a new ranking algorithm.')
table(['Team member','Roll number'],[['Deekshith Alle','23911A6672'],['Sirivennala Kammari','23911A6698'],['Rizwana Mohammad','23911A66A9'],['Harshavardhan Dyavanapelli','24915A6608']],[320,171])
heading('What is implemented')
add('The application supports resume-text extraction and correction, explicit required/preferred skill rubrics, skill evidence and TF-IDF matching, versioned profiles, immutable result snapshots, reasoned human reviews and a restricted synthetic-cohort audit dashboard.')
heading('How to read the comparison')
add('The following pages compare Candidate Lab with a <b>simplified keyword-only student baseline</b>. This is a design comparison, not a market survey. Commercial recruitment platforms may already provide similar functions. No claim of being the first, universally better or more accurate is established.')
heading('One sentence for evaluation')
add('"Our project makes candidate matching inspectable and traceable: reviewers can see the evidence behind a score, preserve the history of a comparison and record their own reasoned review."')

story.append(PageBreak());add('Feature-by-feature comparison','HeadingD')
table(['Area','Keyword-only baseline','Candidate Lab'],[
['Skill matching','Finds terms and displays a score.','Links matched requirements to the source passage in the profile.'],
['Score explanation','Presents one overall number.','Shows required-skill, preferred-skill and text-alignment contributions separately.'],
['Extraction errors','May accept parsed text without correction.','Provides a preview and editable evidence before saving.'],
['Historical context','May overwrite or recalculate results without retaining context.','Saves the job rubric, profile version, evidence and component scores in an immutable snapshot.'],
['User responsibilities','Often provides one general interface.','Separates candidate, recruiter and auditor access, enforced by the backend.'],
['Human accountability','Displays a ranking or shortlist.','Records a review status and mandatory job-related reason separately from the score.'],
['Group examination','May omit aggregate comparisons.','Shows synthetic-cohort rates, sample sizes, Wilson intervals and small-group suppression.'],
['Traceability','May retain only the latest state.','Maintains profile versions, review records and application audit events.']
],[91,174,226])
heading('Why the integration matters')
add('A passage alone does not explain the full review lifecycle. A score alone does not preserve its context. Candidate Lab combines these records so that a reviewer can inspect both the calculation and the sequence of actions around it.')
add('These are implemented software capabilities. Improved hiring outcomes, faster review or reduced discrimination would require separate empirical evidence.','SmallD')

story.append(PageBreak());add('A practical example','HeadingD')
heading('1. Define the criteria')
add('A recruiter creates a Backend Engineer rubric with Python and SQL as required skills and FastAPI as a preferred skill. The criteria are explicit before the comparison is run.')
heading('2. Inspect the evidence and score')
add('A fictional profile contains: "Built Python REST APIs with FastAPI and SQL." The interface links that sentence to the relevant requirements. An illustrative score can be explained as <b>60 required-evidence points + 15 preferred-evidence points + 2.5 alignment points = 77.5</b>. The score is an alignment index, not a 77.5% probability of success.')
heading('3. Preserve the original comparison')
add('Suppose the candidate later corrects the resume. The saved profile receives a new version. The old matching snapshot still retains the earlier evidence and score, while a new run can use the corrected profile. This makes it possible to reconstruct what was reviewed at a particular time.')
heading('4. Record a separate human review')
add('The recruiter reads the passages and saves a status with a job-related reason. The review does not alter the saved numerical score. A shortlist label is an internal record, not an automatic hiring decision or an email to the candidate.')
heading('5. Examine aggregate outcomes')
add('An auditor examines a saved run using a shared cutoff and permitted synthetic group labels. Changing the cutoff recalculates the group rates without rewriting the scores. Cohort labels are separate from the matcher inputs. This supports investigation but does not establish fairness in a real applicant population.')
heading('The differentiator demonstrated')
add('<b>Requirement &gt; evidence &gt; score &gt; saved context &gt; reasoned review &gt; aggregate audit.</b> The value lies in making those connections visible and preserving their history.')

story.append(PageBreak());add('How to present the contribution','HeadingD')
heading('Evaluator-ready explanation')
add('"Our contribution is an integrated, explainable candidate-review workflow. We show the supporting passage for each detected skill, separate the score into visible terms and preserve historical matching snapshots. Candidates can correct their profiles, recruiters record reasoned human reviews, and auditors examine aggregate differences without supplying cohort labels to the scoring engine. We demonstrate these controls in a working application, while treating real-world fairness validation as future research."')
heading('Claims that are supported')
add('The application implements evidence display, profile correction and versioning, immutable matching snapshots, server-enforced role boundaries, review reasons and synthetic-cohort reports. These are demonstrable features in the current code and interface.')
heading('Claims to avoid')
add('Do not describe the system as the first of its kind, superior to every commercial platform, proven unbiased or a validated predictor of employee performance. The current method uses skill rules and TF-IDF. It is not a trained hiring-outcome classifier, and it does not implement SHAP/LIME explanations. No measured improvement in hiring accuracy or discrimination reduction has been established.')
heading('How to establish stronger research evidence')
add('<b>Ranking relevance:</b> obtain consented, annotated resume-job pairs; compare against keyword-only and other baselines using held-out ranking measures such as recall@k and NDCG@k.<br/><b>Explanation usefulness:</b> ask reviewers to locate and verify supporting evidence, then measure task success and time under a controlled protocol.<br/><b>Review consistency:</b> use a common rubric and compare reviewer agreement.<br/><b>Fairness evaluation:</b> define valid outcomes and an approved target population, obtain governed audit attributes and report uncertainty and tradeoffs.')
heading('Evidence basis')
add('This brief describes the implemented project rather than a surveyed market. Relevant local sources include backend/app.py, backend/matching.py, backend/invite.py, src/, tests/, README.md and VERIFICATION.md. Optional semantic models, public hosting and real-world demographic validation are not claimed as completed.','SmallD')

def footer(c,d):
    c.setStrokeColor(colors.HexColor('#d4dfe6'));c.line(52,43,A4[0]-52,43);c.setFillColor(NAVY);c.setFont('Helvetica',8)
    c.drawString(52,29,'Candidate Lab | Project differentiation and evaluation');c.drawRightString(A4[0]-52,29,str(d.page))
SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=52,rightMargin=52,topMargin=45,bottomMargin=58,title='Candidate Lab - Project Differentiators',author='Deekshith Alle; Sirivennala Kammari; Rizwana Mohammad; Harshavardhan Dyavanapelli').build(story,onFirstPage=footer,onLaterPages=footer)
r=PdfReader(OUT);print(OUT);print('Pages:',len(r.pages));assert len(r.pages)==4
