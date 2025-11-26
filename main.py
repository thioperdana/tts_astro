from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, create_engine, desc
from models import Star, Game
from generator import CrosswordGenerator
import random
import json
from pydantic import BaseModel
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://notispaces.cloud",
    "https://notispaces.cloud"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
sqlite_file_name = "data/astro.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def get_session():
    with Session(engine) as session:
        yield session

# Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/generate")
def generate_game(session: Session = Depends(get_session)):
    stars = session.exec(select(Star)).all()
    if not stars:
        raise HTTPException(status_code=404, detail="No stars found in database")
    
    # Pick random stars (e.g. 15)
    selected_stars = random.sample(stars, min(len(stars), 15))
    
    generator = CrosswordGenerator(width=20, height=20)
    puzzle = generator.generate(selected_stars)
    
    return puzzle

@app.post("/api/save")
def save_game(game_data: dict, session: Session = Depends(get_session)):
    # game_data should contain grid, words, status
    # We'll just store the raw JSON for simplicity
    try:
        game = Game(
            grid_data=json.dumps(game_data.get('grid')),
            words_data=json.dumps(game_data.get('words')),
            status="active"
        )
        session.add(game)
        session.commit()
        session.refresh(game)
        return {"id": game.id, "message": "Game saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games")
def list_games(session: Session = Depends(get_session)):
    games = session.exec(select(Game).order_by(Game.created_at.desc())).all()
    return [{"id": g.id, "created_at": g.created_at, "status": g.status} for g in games]

@app.get("/api/load/{game_id}")
def load_game(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "grid": json.loads(game.grid_data),
        "words": json.loads(game.words_data),
        "id": game.id
    }

class SubmitRequest(BaseModel):
    user_grid: List[List[Optional[str]]]

class NameRequest(BaseModel):
    player_name: str

@app.post("/api/games/{game_id}/submit")
def submit_game(game_id: int, request: SubmitRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    solution_grid = json.loads(game.grid_data)
    user_grid = request.user_grid
    
    score = 0
    total_letters = 0
    correct_letters = 0
    
    # Calculate score
    # Assuming grids are same size 20x20
    for r in range(len(solution_grid)):
        for c in range(len(solution_grid[0])):
            if solution_grid[r][c]: # If this cell is part of a word
                total_letters += 1
                # Check if user input matches (case insensitive)
                if (r < len(user_grid) and c < len(user_grid[0]) and 
                    user_grid[r][c] and 
                    user_grid[r][c].upper() == solution_grid[r][c].upper()):
                    correct_letters += 1
                    score += 10 # 10 points per correct letter
    
    # Update game
    game.score = score
    game.completed = True
    game.status = "completed"
    session.add(game)
    session.commit()
    session.refresh(game)
    
    return {
        "score": score,
        "correct_letters": correct_letters,
        "total_letters": total_letters,
        "percentage": int((correct_letters / total_letters) * 100) if total_letters > 0 else 0
    }

@app.post("/api/games/{game_id}/save_name")
def save_name(game_id: int, request: NameRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game.player_name = request.player_name
    session.add(game)
    session.commit()
    
    return {"message": "Name saved"}

@app.get("/api/leaderboard")
def get_leaderboard(session: Session = Depends(get_session)):
    # Get top 10 completed games with names, sorted by score desc
    statement = select(Game).where(Game.completed == True).where(Game.player_name != None).order_by(desc(Game.score)).limit(10)
    games = session.exec(statement).all()
    return games
