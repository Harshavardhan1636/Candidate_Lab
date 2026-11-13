"""Evidence-based research scoring. Audit attributes are deliberately not inputs."""
import os
import json
import hashlib
import re
from functools import lru_cache
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = {
    "Python": ["python"], "SQL": ["sql", "postgresql", "postgres", "mysql", "sqlite"],
    "PostgreSQL": ["postgresql", "postgres"], "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"], "REST APIs": ["rest api", "rest apis", "restful", "rest endpoint", "rest endpoints", "rest services"],
    "Docker": ["docker", "containerized", "containerised"], "Git": ["git", "github", "gitlab"],
    "Testing": ["pytest", "unit tests", "unit testing", "integration tests", "testing"],
    "JavaScript": ["javascript", "js"], "TypeScript": ["typescript"], "React": ["react", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node js"], "HTML": ["html"], "CSS": ["css", "tailwind"],
    "Machine Learning": ["machine learning", "scikit-learn", "sklearn"], "Pandas": ["pandas"],
    "NumPy": ["numpy"], "Data Visualization": ["matplotlib", "seaborn", "data visualization", "power bi", "tableau"],
    "Statistics": ["statistics", "statistical", "hypothesis testing"], "Excel": ["excel"],
    "AWS": ["aws", "amazon web services"], "Java": ["java"], "Spring Boot": ["spring boot"],
    "Communication": ["stakeholder presentation", "technical documentation", "communication"],
}

def contains(text, term):
    return bool(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I))

def sentences(text):
    return [x.strip() for x in re.split(r"\n+|(?<=[.!?])\s+", text) if x.strip()]

def assess_evidence(text, skill):
    """Conservative local rules; labels describe text, never verified competence."""
    aliases = next((v for k, v in SKILLS.items() if k.casefold() == skill.casefold()), [skill])
    observations = []
    for sentence in sentences(text):
        for clause in re.split(r"\s+(?:but|however|whereas|although)\s+|;", sentence, flags=re.I):
            for alias in aliases:
                for match in re.finditer(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", clause, re.I):
                    before = clause[max(0, match.start()-85):match.start()]
                    after = clause[match.end():match.end()+65]
                    if re.search(r"\b(?:no|without|never|not|haven't|have not|don't|do not|lack|lacking)\b[^.;:]{0,65}$", before, re.I) or re.match(r"\s+(?:experience\s+)?(?:is\s+)?(?:absent|not\s+(?:used|known|available))\b", after, re.I):
                        state = 'negated'
                    elif re.search(r"\b(?:learning|learn|studying|beginner|introductory|plan to|want to|interested in|exploring|course in)\b[^.;:]{0,65}$", before, re.I):
                        state = 'learning'
                    elif re.search(r"\b(?:built|developed|implemented|used|using|created|deployed|maintained|designed|wrote|analyzed|automated|tested|managed|integrated|worked|experience|proficient|skilled)\b", clause, re.I):
                        state = 'supported'
                    else:
                        state = 'uncertain'
                    observations.append({'status': state, 'passage': clause.strip()[:600]})
    priority = {'supported': 0, 'learning': 1, 'uncertain': 2, 'negated': 3}
    if not observations:
        return {'status': 'not_found', 'passage': None, 'notes': []}
    best = min(observations, key=lambda x: priority[x['status']])
    states = {x['status'] for x in observations}
    notes = []
    if 'negated' in states and 'supported' in states:
        best = next(x for x in observations if x['status'] == 'negated')
        best = {**best, 'status': 'uncertain'}
        notes.append('Conflicting positive and negative mentions; human verification required.')
    return {**best, 'notes': notes}

def extract(text):
    lines = sentences(text)
    evidence = []
    for skill, aliases in SKILLS.items():
        finding = assess_evidence(text, skill)
        if finding['status'] != 'not_found':
            evidence.append({"skill": skill, **finding})
    warnings = []
    if len(text.strip()) < 80:
        warnings.append("Very little text was extracted. Check the original document before scoring.")
    if not evidence:
        warnings.append("No dictionary skills were found. Add job-related evidence or correct the profile.")
    if any(x['status'] != 'supported' for x in evidence):
        warnings.append('Learning, negated or ambiguous mentions are flagged; they do not earn skill-coverage points.')
    return {"text": text, "skills": evidence, "warnings": warnings, "method": "context-rules-v2"}

def evidence_for(text, skill):
    aliases = next((v for k, v in SKILLS.items() if k.casefold() == skill.casefold()), [skill])
    hits = [s for s in sentences(text) if any(contains(s, a) for a in aliases)]
    return hits[0][:600] if hits else None

def safe_scoring_text(text):
    """Only recognized skill-bearing passages, not identity/contact headers."""
    lines = []
    for line in sentences(text):
        if re.search(r"[\w.+-]+@[\w.-]+|\b(?:gender|religion|caste|marital|born|date of birth|address|name)\s*:", line, re.I):
            continue
        if any(contains(line, a) for aliases in SKILLS.values() for a in aliases):
            line = re.sub(r"\b\d{7,}\b", " ", line)
            lines.append(line)
    return "\n".join(lines)

@lru_cache(maxsize=1)
def semantic_model():
    path = os.getenv("SEMANTIC_MODEL_PATH", "").strip()
    if not path:
        return None
    from sentence_transformers import SentenceTransformer
    # No implicit network transmission or model downloads during resume processing.
    return SentenceTransformer(path, local_files_only=True, device='cpu', trust_remote_code=False)

def matching_config(mode='tfidf'):
    reference={}
    if mode=='semantic':
        from pathlib import Path
        path=Path(os.getenv('SEMANTIC_MODEL_PATH',''))/'model-reference.json'
        if path.is_file():reference=json.loads(path.read_text(encoding='utf-8'))
    return {'evidence_rules':'context-rules-v2','vocabulary_sha256':hashlib.sha256(json.dumps(SKILLS,sort_keys=True).encode()).hexdigest(),'method':mode,'semantic_reference':reference}

def rank(job, candidates, mode='tfidf'):
    if mode not in {'tfidf', 'semantic'}:
        raise ValueError('Unknown matching method.')
    # Alignment uses only positively supported skill clauses, excluding learning/negation.
    docs = ['\n'.join(dict.fromkeys(a['passage'] for skill in SKILLS for a in [assess_evidence(safe_scoring_text(c.text), skill)] if a['status'] == 'supported')) for c in candidates]
    query = " ".join(job.required + job.preferred)  # free-form title/identity not used
    method = "skill-tfidf-v2"
    sims = [0.0] * len(docs)
    if candidates:
        model = semantic_model() if mode == 'semantic' else None
        if mode == 'semantic' and model is None:
            raise ValueError('Configure a local semantic model first.')
        if model is not None:
            vectors = model.encode([query] + docs, normalize_embeddings=True)
            sims = np.clip(vectors[1:] @ vectors[0], 0, 1).tolist()
            sims = [value if doc.strip() else 0.0 for doc,value in zip(docs,sims)]
            method = "skill-semantic-v2"
        else:
            try:
                matrix = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit_transform([query] + docs)
                sims = cosine_similarity(matrix[0:1], matrix[1:]).ravel().tolist()
            except ValueError:
                pass
    results = []
    for c, similarity in zip(candidates, sims):
        requirements = []
        for kind, skills in [("required", job.required), ("preferred", job.preferred)]:
            for skill in skills:
                finding = assess_evidence(safe_scoring_text(c.text), skill)
                requirements.append({"skill": skill, "kind": kind, "matched": finding['status'] == 'supported', "evidence": finding['passage'], "evidence_status": finding['status'], "notes": finding['notes']})
        required = [x for x in requirements if x["kind"] == "required"]
        preferred = [x for x in requirements if x["kind"] == "preferred"]
        coverage = sum(x["matched"] for x in required) / len(required)
        pref = sum(x["matched"] for x in preferred) / len(preferred) if preferred else 0
        # Keep 100 total weight even when no preferred skills exist.
        weights = {"required": .60 if preferred else .75, "preferred": .15 if preferred else 0, "similarity": .25}
        components = [
            {"name": "Required skill evidence", "value": coverage, "weight": weights["required"]},
            {"name": "Preferred skill evidence", "value": pref, "weight": weights["preferred"]},
            {"name": "Semantic alignment" if mode == 'semantic' else "Lexical alignment", "value": float(similarity), "weight": weights["similarity"]},
        ]
        for comp in components:
            comp["contribution"] = round(comp["value"] * comp["weight"] * 100, 4)
        score = round(sum(x["contribution"] for x in components), 2)
        results.append({"candidate_id": c.id, "candidate_label": c.label, "profile_version": c.version,
                        "score": score, "components": components, "requirements": requirements,
                        "method": method, "warnings": c.warnings,
                        "profile_snapshot": {"text": safe_scoring_text(c.text), "version": c.version},
                        "status": "needs_review"})
    # Stable tie ordering, independent of demographic audit data.
    return sorted(results, key=lambda x: (-x["score"], x["candidate_id"])), method

def wilson(successes, n):
    if not n:
        return None
    z = 1.96
    p = successes / n
    den = 1 + z*z/n
    mid = (p + z*z/(2*n))/den
    delta = z * ((p*(1-p)/n + z*z/(4*n*n)) ** .5)/den
    return [round(max(0, mid-delta), 4), round(min(1, mid+delta), 4)]

def fairness(results, attributes, threshold):
    groups = {}
    for row in results:
        group = attributes.get(row["candidate_id"])
        if group is None:
            continue
        bucket = groups.setdefault(group, {"count": 0, "selected": 0})
        bucket["count"] += 1
        bucket["selected"] += row["score"] >= threshold
    output = []
    rates = []
    for name, data in sorted(groups.items()):
        n = data["count"]
        rate = data["selected"] / n
        suppressed = n < 5
        if not suppressed:
            rates.append(rate)
        output.append({"group": name, "count": n, "selected": None if suppressed else data["selected"],
                       "selection_rate": None if suppressed else round(rate, 4), "interval": None if suppressed else wilson(data["selected"], n), "suppressed": suppressed})
    comparable = len(rates) >= 2 and all(not g["suppressed"] for g in output)
    return {"groups": output, "threshold": threshold, "audited_count": sum(g["count"] for g in output),
            "unattributed_count": len(results) - sum(g["count"] for g in output),
            "demographic_parity_difference": round(max(rates)-min(rates), 4) if comparable else None,
            "provenance": "Synthetic cohort labels only; not demographic identity or qualification labels.",
            "limitations": ["Research cutoff, not a hiring decision.", "Small samples produce wide uncertainty.", "Rates below five records are suppressed.", "No validated qualification labels: TPR, FPR and equalized odds are unavailable.", "No fairness certificate or real-world population claim."]}
