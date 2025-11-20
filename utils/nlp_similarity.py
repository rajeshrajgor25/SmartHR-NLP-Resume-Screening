from sentence_transformers import SentenceTransformer, util
import re

MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

COMMON_SKILLS = [

    # ---------- Data Analyst Skills ----------
    "sql", "excel", "power bi", "tableau", "python",
    "data analysis", "data visualization", "analytics",

    # ---------- Backend Developer Skills ----------
    "node.js", "nodejs", "python", "rest apis", "postgresql",
    "docker", "aws", "redis", "api development", "backend development",

    # ---------- Digital Marketing Skills ----------
    "seo", "google analytics", "facebook ads", "content creation",
    "digital marketing", "social media ads", "paid ads",

    # ---------- Social Media Manager Skills ----------
    "social media strategy", "content planning", "content scheduling",
    "canva", "video editing", "analytics understanding",
    "copywriting", "influencer collaboration", "instagram marketing",
    "linkedin marketing", "youtube marketing", "facebook marketing",

    # ---------- UI/UX Designer Skills ----------
    "figma", "wireframing", "prototyping", "user research",
    "user flow", "ui design", "ux design", "usability testing",
    "design systems", "html", "css", "frontend basics"
]


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text):
    """Extract skills from candidate resume using COMMON_SKILLS list."""
    t = text.lower()
    found = [s for s in COMMON_SKILLS if s.lower() in t]
    return sorted(set(found))


def compute_similarity(jd_text, candidate_text):
    """Calculate cosine similarity between JD & candidate resume."""
    jd = clean_text(jd_text)
    cand = clean_text(candidate_text)

    if not jd or not cand:
        return 0.0

    jd_emb = model.encode(jd, convert_to_tensor=True)
    cand_emb = model.encode(cand, convert_to_tensor=True)

    sim = util.cos_sim(jd_emb, cand_emb).item()
    return float(sim)
