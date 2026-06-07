import os
import pickle
import logging
import numpy as np
import pandas as pd
import scipy.sparse
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from geopy.distance import geodesic
from rapidfuzz import fuzz
import torch

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────
MODEL_DIR  = ""
CACHE_FILE = os.path.join(MODEL_DIR, "geo_cache.pkl")

EXP_RANK = {
    "internship": 1, "entry level": 2, "associate": 3,
    "mid-senior level": 4, "director": 5, "executive": 6,
    "unknown": 0, "": 0
}

# ── Load all models at startup ────────────────────────────────
logger.info("Loading models...")

df           = pd.read_pickle(os.path.join(MODEL_DIR, "jobs_clean.pkl"))
embeddings   = np.load(os.path.join(MODEL_DIR, "job_embeddings.npy"))
tfidf_matrix = scipy.sparse.load_npz(os.path.join(MODEL_DIR, "tfidf_matrix.npz"))

with open(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
    tfidf = pickle.load(f)

with open(CACHE_FILE, "rb") as f:
    geo_cache = pickle.load(f)

device = "cuda" if torch.cuda.is_available() else "cpu"
model  = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# Reset index to ensure alignment
df = df.reset_index(drop=True)

logger.info(f"Loaded {len(df)} jobs — API ready on device: {device}")

# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="Job Recommender API",
    description="Skill-based, semantic, geolocation, and similarity job recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ───────────────────────────────────────────
class RecommendRequest(BaseModel):
    skills:           str            = Field("", description="Comma separated skills")
    location:         Optional[str]  = Field(None, description="e.g. New York, NY")
    experience_level: Optional[str]  = Field(None, description="entry/mid/senior/executive")
    salary_min:       Optional[float]= Field(None, description="Minimum salary")
    salary_max:       Optional[float]= Field(None, description="Maximum salary")
    max_distance_km:  float          = Field(100,  description="Max distance in km")
    top_n:            int            = Field(10,   description="Number of results")
    weight_skill:     float          = Field(0.40)
    weight_semantic:  float          = Field(0.25)
    weight_location:  float          = Field(0.15)
    weight_exp:       float          = Field(0.10)
    weight_salary:    float          = Field(0.10)

class SearchRequest(BaseModel):
    query:           str            = Field(..., description="Free text search query")
    location:        Optional[str]  = Field(None)
    max_distance_km: float          = Field(100)
    top_n:           int            = Field(10)

class SimilarRequest(BaseModel):
    job_id:    Optional[str] = Field(None, description="Job ID to find similar jobs for")
    job_title: Optional[str] = Field(None, description="Job title to find similar jobs for")
    top_n:     int           = Field(10)

class JobResult(BaseModel):
    job_id:           str
    title:            str
    company_name:     str
    location:         str
    skills:           str
    experience_level: str
    salary:           str
    work_type:        str
    url:              str
    score:            float

# ── Helpers ───────────────────────────────────────────────────
def get_coords_from_cache(location_str):
    """Look up coordinates from pre-built geo cache."""
    if not location_str:
        return None
    key = str(location_str).strip().lower()
    return geo_cache.get(key)

def haversine_km(c1, c2):
    """Distance in km between two (lat, lon) tuples."""
    if c1 is None or c2 is None:
        return np.inf
    try:
        return geodesic(c1, c2).km
    except:
        return np.inf

def safe_str(val):
    """Convert any value to clean string."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    return str(val).strip()

def format_results(indices, scores, score_label="score") -> List[dict]:
    """Convert dataframe rows + scores into clean result dicts."""
    results = []
    for i in indices:
        row = df.iloc[i]
        results.append({
            "job_id":           safe_str(row.get("job_id", "")),
            "title":            safe_str(row.get("title", "")),
            "company_name":     safe_str(row.get("company_name", "")),
            "location":         safe_str(row.get("location", "")),
            "skills":           safe_str(row.get("skills", "")),
            "experience_level": safe_str(row.get("Experience", "")),
            "salary":           safe_str(row.get("Salary", "")),
            "work_type":        safe_str(row.get("work_type", "")),
            "url":              safe_str(row.get("url", "")),
            "score":            round(float(scores[i]) * 100, 1),
        })
    return results

# ── Core Scoring Engine ───────────────────────────────────────
def compute_scores(
    skills         = "",
    query_text     = "",
    location       = None,
    exp_level      = "",
    salary_min     = None,
    salary_max     = None,
    max_distance_km= 100,
    w_skill        = 0.40,
    w_sem          = 0.25,
    w_loc          = 0.15,
    w_exp          = 0.10,
    w_sal          = 0.10,
):
    n = len(df)

    # ── Skill score (TF-IDF cosine similarity) ────────────────
    if skills.strip():
        vec          = tfidf.transform([skills.lower()])
        skill_scores = cosine_similarity(vec, tfidf_matrix).flatten()
    else:
        skill_scores = np.zeros(n)

    # ── Semantic score (sentence embeddings) ──────────────────
    text = query_text.strip() or skills.strip()
    if text:
        q_emb      = model.encode([text.lower()], convert_to_numpy=True)
        sem_scores = cosine_similarity(q_emb, embeddings).flatten()
    else:
        sem_scores = np.zeros(n)

    # ── Location score (geolocation proximity) ────────────────
    if location:
        cand_coords = get_coords_from_cache(location)
        if cand_coords:
            def location_score(job_coords):
                dist = haversine_km(cand_coords, job_coords)
                if dist == np.inf:   return 0.0
                if dist <= 20:       return 1.0
                if dist <= max_distance_km:
                    return max(0.2, 1.0 - (dist / max_distance_km) * 0.8)
                return 0.0
            loc_scores = np.array([
                location_score(c) for c in df["coords"]
            ])
        else:
            # Location not in cache — neutral score
            logger.warning(f"Location not found in cache: {location}")
            loc_scores = np.full(n, 0.5)
    else:
        loc_scores = np.full(n, 0.5)

    # ── Experience score ──────────────────────────────────────
    if exp_level and exp_level.lower() in EXP_RANK:
        cand_rank  = EXP_RANK[exp_level.lower()]
        exp_map    = {0: 1.0, 1: 0.6, 2: 0.3, 3: 0.1}
        exp_scores = np.array([
            0.5 if r == 0
            else exp_map.get(abs(cand_rank - int(r)), 0.0)
            for r in df["exp_rank"]
        ])
    else:
        exp_scores = np.full(n, 0.5)

    # ── Salary score ──────────────────────────────────────────
    if salary_min is not None or salary_max is not None:
        lo = salary_min or 0
        hi = salary_max or 1e9
        def salary_score(sal):
            if pd.isna(sal):      return 0.3
            if lo <= sal <= hi:   return 1.0
            miss = min(abs(sal - lo), abs(sal - hi))
            return max(0.0, 1.0 - miss / max(hi - lo, 10000))
        sal_scores = np.array([salary_score(s) for s in df["salary_num"]])
    else:
        sal_scores = np.full(n, 0.5)

    # ── Weighted final score ──────────────────────────────────
    final = (
        w_skill * skill_scores +
        w_sem   * sem_scores   +
        w_loc   * loc_scores   +
        w_exp   * exp_scores   +
        w_sal   * sal_scores
    )

    return final

# ── Endpoints ─────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status":      "ok",
        "jobs_loaded": len(df),
        "device":      device,
        "endpoints":   ["/recommend", "/search", "/similar", "/filters", "/job/{job_id}"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "jobs": len(df)}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """Skill-based + geolocation + experience + salary recommendation."""
    if not req.skills.strip() and not req.location:
        raise HTTPException(
            status_code=400,
            detail="Provide at least skills or location"
        )

    scores  = compute_scores(
        skills          = req.skills,
        location        = req.location,
        exp_level       = req.experience_level or "",
        salary_min      = req.salary_min,
        salary_max      = req.salary_max,
        max_distance_km = req.max_distance_km,
        w_skill         = req.weight_skill,
        w_sem           = req.weight_semantic,
        w_loc           = req.weight_location,
        w_exp           = req.weight_exp,
        w_sal           = req.weight_salary,
    )

    top_idx = np.argsort(scores)[::-1][:req.top_n]
    results = format_results(top_idx, scores)

    return {
        "total_results": len(results),
        "results":       results
    }

@app.post("/search")
def search(req: SearchRequest):
    """Free text semantic search with optional geolocation."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    scores  = compute_scores(
        query_text      = req.query,
        location        = req.location,
        max_distance_km = req.max_distance_km,
        w_skill         = 0.10,
        w_sem           = 0.55,
        w_loc           = 0.20,
        w_exp           = 0.05,
        w_sal           = 0.10,
    )

    top_idx = np.argsort(scores)[::-1][:req.top_n]
    results = format_results(top_idx, scores)

    return {
        "query":         req.query,
        "total_results": len(results),
        "results":       results
    }

@app.post("/similar")
def similar(req: SimilarRequest):
    """Find jobs similar to a given job by ID or title."""
    if not req.job_id and not req.job_title:
        raise HTTPException(
            status_code=400,
            detail="Provide job_id or job_title"
        )

    # Find source job index
    if req.job_id:
        mask = df["job_id"].astype(str) == str(req.job_id)
        if not mask.any():
            raise HTTPException(
                status_code=404,
                detail=f"job_id '{req.job_id}' not found"
            )
        src_idx = int(df[mask].index[0])
    else:
        # Fuzzy title match
        title_scores = df["title"].apply(
            lambda t: fuzz.token_sort_ratio(
                str(t).lower(), req.job_title.lower()
            )
        )
        src_idx = int(title_scores.idxmax())
        logger.info(
            f"Title match: '{df.iloc[src_idx]['title']}' "
            f"(score={title_scores.max()})"
        )

    # Compute similarity
    src_skill  = tfidf_matrix[src_idx]
    src_emb    = embeddings[src_idx].reshape(1, -1)
    skill_sim  = cosine_similarity(src_skill, tfidf_matrix).flatten()
    sem_sim    = cosine_similarity(src_emb, embeddings).flatten()
    combined   = 0.5 * skill_sim + 0.5 * sem_sim
    combined[src_idx] = -1   # exclude source job

    top_idx = np.argsort(combined)[::-1][:req.top_n]
    results = format_results(top_idx, combined)

    source = df.iloc[src_idx]
    return {
        "source_job": {
            "job_id":       safe_str(source.get("job_id", "")),
            "title":        safe_str(source.get("title", "")),
            "company_name": safe_str(source.get("company_name", "")),
            "location":     safe_str(source.get("location", "")),
            "skills":       safe_str(source.get("skills", "")),
        },
        "total_results": len(results),
        "results":       results,
    }

@app.get("/job/{job_id}")
def get_job(job_id: str):
    """Get full details of a single job by ID."""
    mask = df["job_id"].astype(str) == str(job_id)
    if not mask.any():
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    row = df[mask].iloc[0]
    return {
        "job_id":           safe_str(row.get("job_id", "")),
        "title":            safe_str(row.get("title", "")),
        "company_name":     safe_str(row.get("company_name", "")),
        "location":         safe_str(row.get("location", "")),
        "skills":           safe_str(row.get("skills", "")),
        "experience_level": safe_str(row.get("Experience", "")),
        "salary":           safe_str(row.get("Salary", "")),
        "work_type":        safe_str(row.get("work_type", "")),
        "url":              safe_str(row.get("url", "")),
        "description":      safe_str(row.get("description", "")),
    }

@app.get("/filters")
def filters():
    """Return all available filter options for the frontend."""
    exp_levels = (
        df["Experience"]
        .dropna()
        .str.strip()
        .unique()
        .tolist()
    )
    exp_levels = sorted([e for e in exp_levels if e and e.lower() != "unknown"])

    salary_vals = df["salary_num"].dropna()

    return {
        "experience_levels": exp_levels,
        "work_types":        sorted(df["work_type"].dropna().unique().tolist()),
        "states":            sorted(df["state"].dropna().unique().tolist()) if "state" in df.columns else [],
        "salary_range": {
            "min": int(salary_vals.min()) if len(salary_vals) > 0 else 0,
            "max": int(salary_vals.max()) if len(salary_vals) > 0 else 500000,
        },
        "total_jobs": len(df),
    }