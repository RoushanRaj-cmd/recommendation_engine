from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from recommend import recommend_internships

app = FastAPI(
    title="PM Internship Recommendation API",
    description="An API for the 'Sixth Sense' AI-based internship recommendation engine.",
    version="3.0.0",
)

# --- NEW: Add CORS Middleware Configuration ---
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:5500", # Common port for Live Server extension
    "null" # To allow opening the HTML file directly
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class User(BaseModel):
    skills: str
    sector: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    top_k: int = 5

class Recommendation(BaseModel):
    id: int
    sector: str
    skills: str
    education: Optional[str]
    location: str
    final_score: float
    match_reasons: List[str]

class ApiResponse(BaseModel):
    recommendation_type: str
    suggestion_prompt: str
    results: List[Recommendation]

class Feedback(BaseModel):
    user_id: str
    internship_id: int
    event_type: str

# --- API Endpoints ---
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/recommend", response_model=ApiResponse)
def recommend(user: User):
    """
    Accepts a user's profile and returns a list of top_k recommended internships.
    """
    df, rec_type, prompt = recommend_internships(
        candidate_skills=user.skills, candidate_sector=user.sector,
        candidate_education=user.education, candidate_location=user.location,
        top_k=user.top_k
    )

    results = []
    for _, row in df.iterrows():
        results.append(Recommendation(
            id=int(row["id"]), sector=str(row["sector"]),
            skills=str(row["skills"]),
            education=str(row.get("education", "")) if pd.notna(row.get("education")) else None,
            location=str(row["location"]),
            final_score=float(row["final_score"]),
            match_reasons=row["match_reasons"]
        ))

    return ApiResponse(recommendation_type=rec_type, suggestion_prompt=prompt, results=results)

@app.post("/api/feedback")
def log_feedback(feedback: Feedback):
    """Logs user interaction with a recommendation to the database."""
    DB_PATH = "internships.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        user_id TEXT, internship_id INTEGER, event_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    cursor.execute(
        "INSERT INTO user_feedback (user_id, internship_id, event_type) VALUES (?, ?, ?)",
        (feedback.user_id, feedback.internship_id, feedback.event_type)
    )
    conn.commit()
    conn.close()
    return {"status": "feedback logged"}