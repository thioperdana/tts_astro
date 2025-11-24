from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON
from datetime import datetime

class Star(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    constellation: str
    meaning: Optional[str] = None
    
class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    grid_data: str # JSON string of the grid
    words_data: str # JSON string of the words/clues
    status: str = "active" # active, completed
    
    # New fields for scoring system
    score: int = Field(default=0)
    player_name: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
