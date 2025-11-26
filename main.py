from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, create_engine, desc
from models import Star, Game
from generator import CrosswordGenerator
import random
import json
import os
import html
from pydantic import BaseModel
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Disable docs in production
docs_url = "/docs" if ENVIRONMENT != "production" else None
redoc_url = "/redoc" if ENVIRONMENT != "production" else None

app = FastAPI(docs_url=docs_url, redoc_url=redoc_url)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Middleware for Direct Access Restriction (Production Only)
@app.middleware("http")
async def check_direct_access(request: Request, call_next):
    if ENVIRONMENT == "production" and request.url.path.startswith("/api/"):
        referer = request.headers.get("referer")
        origin = request.headers.get("origin")
        
        # If ALLOWED_ORIGINS is set, check against it
        allowed_domains = [d.strip() for d in ALLOWED_ORIGINS_ENV.split(",") if d.strip()]
        
        if not referer and not origin:
            # Block direct access (no referer/origin)
            return JSONResponse(status_code=403, content={"detail": "Direct access forbidden"})
            
        if allowed_domains:
            # If specific domains are enforced
            valid = False
            if referer:
                for domain in allowed_domains:
                    if domain in referer:
                        valid = True
                        break
            if origin and origin in allowed_domains:
                valid = True
                
            if not valid:
                 return JSONResponse(status_code=403, content={"detail": "Forbidden source"})

    response = await call_next(request)
    return response

if ALLOWED_ORIGINS_ENV:
    origins = [d.strip() for d in ALLOWED_ORIGINS_ENV.split(",") if d.strip()]
else:
    origins = [
        "http://notispaces.cloud",
        "https://notispaces.cloud",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
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
@limiter.limit("5/minute")
def generate_game(request: Request, session: Session = Depends(get_session)):
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
@limiter.limit("10/minute")
def submit_game(request: Request, game_id: int, req: SubmitRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    solution_grid = json.loads(game.grid_data)
    user_grid = req.user_grid
    
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
@limiter.limit("5/minute")
def save_name(request: Request, game_id: int, req: NameRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    import html
    game.player_name = html.escape(req.player_name)
    session.add(game)
    session.commit()
    
    return {"message": "Name saved"}

@app.get("/api/leaderboard")
def get_leaderboard(session: Session = Depends(get_session)):
    # Get top 10 completed games with names, sorted by score desc
    statement = select(Game).where(Game.completed == True).where(Game.player_name != None).order_by(desc(Game.score)).limit(10)
    games = session.exec(statement).all()
    return games
