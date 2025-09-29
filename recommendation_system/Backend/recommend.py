import re
import math
import json
import sqlite3
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---
DB_PATH = "internships.db"
TABLE_NAME = "internships"
MIN_SCORE_THRESHOLD = 0.2

# --- Load Configuration from JSON ---
print("Loading configuration from config.json...")
with open("config.json", "r") as f:
    config = json.load(f)
weights = config['weights']
SOFT_SKILLS_DICTIONARY = config['soft_skills']

# ----------------------------
# Data Loading from Database
# ----------------------------
print(f"Connecting to database at {DB_PATH} and loading data...")
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
conn.close()
print(f"Data loaded successfully. Found {len(df)} internships.")

# ----------------------------
# Preprocessing and Vectorization
# ----------------------------
def preprocess_text(txt: str) -> str:
    if not isinstance(txt, str): return ""
    return re.sub(r"\s+", " ", txt.lower().replace(";", " ")).strip()

df["skills_processed"] = df["skills"].fillna("").apply(preprocess_text)

tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words="english", min_df=2, max_df=0.8)
internship_matrix = tfidf.fit_transform(df["skills_processed"])
internship_similarity_matrix = cosine_similarity(internship_matrix)

# ----------------------------
# Hybrid Skill Tagger (Soft Skills)
# ----------------------------
def soft_skill_score(candidate_skills: str, internship_skills: str) -> float:
    candidate_processed = preprocess_text(candidate_skills)
    internship_processed = preprocess_text(internship_skills)
    for category, keywords in SOFT_SKILLS_DICTIONARY.items():
        if any(kw in candidate_processed for kw in keywords) and any(kw in internship_processed for kw in keywords):
            return weights.get('soft_skill_boost', 0.1)
    return 0.0

# ----------------------------
# Helper Functions (Stepping Stone, Scoring, MMR, Reasons)
# ----------------------------
def get_top_skills_per_sector(dataf, top_n=10):
    # (This function remains the same as before)
    sector_skills = {}
    for sector in dataf['sector'].unique():
        if pd.isna(sector): continue
        sector_df = dataf[dataf['sector'] == sector]
        all_skills = ' '.join(sector_df['skills_processed'])
        if not all_skills: continue
        try:
            temp_tfidf = TfidfVectorizer(max_features=top_n, stop_words='english').fit(all_skills.split())
            sector_skills[sector] = list(temp_tfidf.vocabulary_.keys())
        except ValueError:
            sector_skills[sector] = []
    return sector_skills

sector_top_skills = get_top_skills_per_sector(df)

def location_score(candidate_city: Optional[str], job_city: Optional[str]) -> float:
    if not all([candidate_city, job_city, isinstance(job_city, str)]): return 0.0
    return 1.0 if candidate_city.strip().lower() == job_city.strip().lower() else 0.0

def education_score(candidate_education: Optional[str], job_education: Optional[str]) -> float:
    if not all([candidate_education, job_education, isinstance(job_education, str)]): return 0.0
    return 1.0 if candidate_education.strip().lower() in job_education.strip().lower() else 0.0

def _apply_mmr(ranked_df: pd.DataFrame, top_k: int, lambda_param: float = 0.7) -> pd.DataFrame:
    # (This function remains the same as before)
    if len(ranked_df) < top_k: return ranked_df
    results_indices, remaining_indices = [], list(ranked_df.index)
    if not remaining_indices: return pd.DataFrame()
    best_initial_idx = remaining_indices.pop(0)
    results_indices.append(best_initial_idx)
    while len(results_indices) < top_k and remaining_indices:
        mmr_scores = []
        for idx in remaining_indices:
            sim_to_results = internship_similarity_matrix[idx, results_indices].max()
            original_score = ranked_df.loc[idx, 'final_score']
            mmr_score = lambda_param * original_score - (1 - lambda_param) * sim_to_results
            mmr_scores.append((idx, mmr_score))
        if not mmr_scores: break
        best_next_idx, _ = max(mmr_scores, key=lambda x: x[1])
        results_indices.append(best_next_idx)
        remaining_indices.remove(best_next_idx)
    return ranked_df.loc[results_indices].copy()

def _generate_reasons(row: pd.Series) -> List[str]:
    # (This function remains the same as before)
    reasons = []
    if row.get('skills_similarity', 0) > 0.4: reasons.append("Strongly matches your technical skills.")
    elif row.get('skills_similarity', 0) > 0.2: reasons.append("Good technical skill alignment.")
    if row.get('soft_skill_boost', 0) > 0: reasons.append("Matches your soft skills (e.g., Communication, Teamwork).")
    if row.get('sector_boost', 0) > 0: reasons.append(f"It's in your preferred sector: {row['sector']}.")
    if row.get('location_boost', 0) > 0: reasons.append(f"Located in your preferred city: {row['location']}.")
    if not reasons: reasons.append("This is a potential opportunity to explore.")
    return reasons

# ----------------------------
# Core Recommendation Logic
# ----------------------------
def recommend_internships(
    candidate_skills: str,
    candidate_sector: Optional[str] = None,
    candidate_education: Optional[str] = None,
    candidate_location: Optional[str] = None,
    top_k: int = 5
) -> Tuple[pd.DataFrame, str, str]:
    
    recs = df.copy()
    cand_vec = tfidf.transform([preprocess_text(candidate_skills)])
    recs["skills_similarity"] = cosine_similarity(cand_vec, internship_matrix).flatten()
    recs["soft_skill_boost"] = recs["skills"].apply(lambda s: soft_skill_score(candidate_skills, s))
    recs["sector_boost"] = recs["sector"].str.lower().eq(candidate_sector.strip().lower() if candidate_sector else "").astype(float) * weights['sector_boost']
    recs["education_boost"] = recs["education"].apply(lambda e: education_score(candidate_education, e)) * weights['education_boost']
    recs["location_boost"] = recs["location"].apply(lambda c: location_score(candidate_location, c)) * weights['location_boost']
    
    recs["final_score"] = (recs["skills_similarity"] * weights['skills_similarity'] + recs["soft_skill_boost"] +
                           recs["sector_boost"] + recs["education_boost"] + recs["location_boost"])
    
    ranked_recs = recs.sort_values("final_score", ascending=False)

    if ranked_recs.empty or ranked_recs.iloc[0]["final_score"] < MIN_SCORE_THRESHOLD:
        top_skills_needed = sector_top_skills.get(candidate_sector, [])
        if not top_skills_needed:
             diverse_recs = _apply_mmr(ranked_recs, top_k)
             if not diverse_recs.empty: diverse_recs["match_reasons"] = diverse_recs.apply(_generate_reasons, axis=1)
             return diverse_recs, "direct_match", "We couldn't find a strong match. Here are some diverse options to explore."
        
        prompt = f"To succeed in the {candidate_sector} sector, consider roles that build skills like: {', '.join(top_skills_needed[:3])}."
        recs["stepping_stone_score"] = recs['skills_processed'].apply(lambda x: sum(1 for skill in top_skills_needed if skill in x))
        stepping_stone_recs = recs.nlargest(top_k, "stepping_stone_score").copy()
        if not stepping_stone_recs.empty:
            reasons_list = [[f"Builds key skill: {s}."] for r in stepping_stone_recs.itertuples() for s in top_skills_needed if s in r.skills_processed][:1]
            stepping_stone_recs["match_reasons"] = reasons_list
        return stepping_stone_recs, "stepping_stone", prompt

    top_2k_recs = ranked_recs.head(top_k * 2)
    diverse_recs = _apply_mmr(top_2k_recs, top_k)
    if not diverse_recs.empty: diverse_recs["match_reasons"] = diverse_recs.apply(_generate_reasons, axis=1)
    return diverse_recs, "direct_match", "Here are your top personalized recommendations!"