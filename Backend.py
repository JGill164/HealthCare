"""
SIGNAL Health — Mental Health Crisis Early Warning System
FastAPI Backend

Setup:
  pip install fastapi uvicorn transformers torch

Run:
  uvicorn backend:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import sqlite3
import datetime

app = FastAPI(title="SIGNAL Health API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading emotion model...")
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)
print("Model loaded.")

DB_PATH = "signal_health.db"
CRISIS_EMOTIONS = {"sadness", "fear", "disgust"}
CRISIS_THRESHOLD = 0.6
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life",
    "self-harm", "hurt myself", "hopeless", "can't go on"
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            dominant_emotion TEXT,
            crisis_score REAL,
            crisis_flagged INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


class JournalEntry(BaseModel):
    text: str

class EntryResponse(BaseModel):
    id: int
    dominant_emotion: str
    crisis_score: float
    crisis_flagged: bool
    emotions: dict
    timestamp: str

class HistoryItem(BaseModel):
    id: int
    text: str
    dominant_emotion: str
    crisis_score: float
    crisis_flagged: bool
    timestamp: str


def check_crisis_keywords(text: str) -> bool:
    return any(kw in text.lower() for kw in CRISIS_KEYWORDS)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=EntryResponse)
def analyze(entry: JournalEntry):
    if not entry.text.strip():
        raise HTTPException(status_code=400, detail="Entry text is empty.")

    results = emotion_classifier(entry.text)[0]
    emotions = {r["label"].lower(): round(r["score"], 4) for r in results}
    dominant = max(emotions, key=emotions.get)
    crisis_score = round(sum(emotions.get(e, 0) for e in CRISIS_EMOTIONS), 4)
    crisis_flagged = crisis_score >= CRISIS_THRESHOLD or check_crisis_keywords(entry.text)
    timestamp = datetime.datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO entries (text, dominant_emotion, crisis_score, crisis_flagged, timestamp) VALUES (?, ?, ?, ?, ?)",
        (entry.text, dominant, crisis_score, int(crisis_flagged), timestamp)
    )
    entry_id = c.lastrowid
    conn.commit()
    conn.close()

    return EntryResponse(
        id=entry_id,
        dominant_emotion=dominant,
        crisis_score=crisis_score,
        crisis_flagged=crisis_flagged,
        emotions=emotions,
        timestamp=timestamp
    )


@app.get("/history", response_model=list[HistoryItem])
def history(limit: int = 14):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, text, dominant_emotion, crisis_score, crisis_flagged, timestamp FROM entries ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [
        HistoryItem(id=r[0], text=r[1], dominant_emotion=r[2], crisis_score=r[3], crisis_flagged=bool(r[4]), timestamp=r[5])
        for r in reversed(rows)
    ]


@app.delete("/history")
def clear_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return {"status": "cleared"}
