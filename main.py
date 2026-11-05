from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
import random

SQLALCHEMY_DATABASE_URL = "sqlite:///./sparkmind.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PlayerScore(Base):
    __tablename__ = "leaderboard"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    score = Column(Integer)

class UserRiddle(Base):
    __tablename__ = "user_riddles"
    id = Column(Integer, primary_key=True, index=True)
    creator = Column(String)
    question = Column(Text)
    answer = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spark Mind Pro Max API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScoreSubmit(BaseModel):
    username: str
    score: int

class RiddleSubmit(BaseModel):
    creator: str
    question: str
    answer: str

RIDDLES = [
    {
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", 
        "answer": "echo",
        "options": ["shadow", "echo", "wind", "cloud"]
    },
    {
        "question": "I have a face and two hands, but no arms or legs! What am I?", 
        "answer": "clock",
        "options": ["mirror", "clock", "doll", "statue"]
    },
    {
        "question": "I have cities but no houses, forests but no trees, and rivers but no water. What am I?", 
        "answer": "map",
        "options": ["globe", "atlas", "map", "painting"]
    },
    {
        "question": "The more you take, the more you leave behind. What am I?", 
        "answer": "footsteps",
        "options": ["time", "footsteps", "memories", "breaths"]
    },
    {
        "question": "I have keys but can't open locks, I have space but no room. What am I?", 
        "answer": "keyboard",
        "options": ["piano", "keyboard", "map", "computer"]
    }
]

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/daily-riddle/")
def get_daily_riddle():
    today_num = date.today().toordinal()
    riddle = RIDDLES[today_num % len(RIDDLES)]
    return riddle

@app.get("/random-riddle/")
def get_random_riddle():
    riddle = random.choice(RIDDLES)
    return riddle

@app.get("/speedrun-riddles/")
def get_speedrun_riddles():
    selected = random.sample(RIDDLES, min(3, len(RIDDLES)))
    return selected

@app.post("/submit-score/")
def submit_score(data: ScoreSubmit):
    db = SessionLocal()
    existing_player = db.query(PlayerScore).filter(PlayerScore.username == data.username).first()
    if existing_player:
        existing_player.score += data.score
    else:
        new_player = PlayerScore(username=data.username, score=data.score)
        db.add(new_player)
    db.commit()
    db.close()
    return {"status": "success"}

@app.get("/leaderboard/")
def get_leaderboard():
    db = SessionLocal()
    top_players = db.query(PlayerScore).order_by(PlayerScore.score.desc()).limit(10).all()
    db.close()
    return [{"username": player.username, "score": player.score} for player in top_players]

@app.get("/stats/")
def get_stats():
    db = SessionLocal()
    total_players = db.query(PlayerScore).count()
    db.close()
    return {
        "total_players": total_players,
        "active_puzzles": len(RIDDLES),
        "platform_accuracy": "95.4%"
    }

@app.post("/submit-riddle/")
def submit_riddle(data: RiddleSubmit):
    db = SessionLocal()
    new_riddle = UserRiddle(creator=data.creator, question=data.question, answer=data.answer)
    db.add(new_riddle)
    db.commit()
    db.close()
    return {"status": "success"}
