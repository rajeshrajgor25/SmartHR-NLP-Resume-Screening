from sentence_transformers import SentenceTransformer, util
import re

MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

COMMON_SKILLS = [
    'python','sql','excel','power bi','tableau','machine learning','r','java','c++',
    'nlp','aws','azure','react','node','postgres','docker','redis','seo','google analytics','UI/UX'
]

def clean_text(text):
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_skills(text):
    t = text.lower()
    found = [s for s in COMMON_SKILLS if s in t]
    return list(sorted(set(found)))

def compute_similarity(jd_text, candidate_text):
    jd = clean_text(jd_text)
    cand = clean_text(candidate_text)
    if not jd or not cand:
        return 0.0
    jd_emb = model.encode(jd, convert_to_tensor=True)
    cand_emb = model.encode(cand, convert_to_tensor=True)
    sim = util.cos_sim(jd_emb, cand_emb).item()
    return float(sim)
