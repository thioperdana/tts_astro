import random
from typing import List, Dict, Tuple, Optional
from models import Star

class CrosswordGenerator:
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.grid = [['' for _ in range(width)] for _ in range(height)]
        self.placed_words = []

    def generate(self, words: List[Star]) -> Dict:
        # Sort words by length, longest first
        words.sort(key=lambda x: len(self._sanitize_word(x.name)), reverse=True)
        
        # Place first word
        if not words:
            return {}
            
        first_word_obj = words[0]
        first_word_clean = self._sanitize_word(first_word_obj.name)
        
        # Place in middle
        start_row = self.height // 2
        start_col = (self.width - len(first_word_clean)) // 2
        
        if self._place_word(first_word_clean, start_row, start_col, 'across'):
            self.placed_words.append({
                'word': first_word_clean,
                'original_word': first_word_obj.name,
                'clue': first_word_obj.meaning,
                'row': start_row,
                'col': start_col,
                'direction': 'across',
                'number': 1
            })
            
        # Try to place other words
        for word in words[1:]:
            self._try_place_word(word)
            
        return {
            'grid': self.grid,
            'words': self.placed_words,
            'width': self.width,
            'height': self.height
        }

    def _sanitize_word(self, word: str) -> str:
        """Remove spaces, dots, and non-alphanumeric chars, convert to upper."""
        return "".join(c for c in word if c.isalnum()).upper()

    def _try_place_word(self, word_obj: Star):
        word = self._sanitize_word(word_obj.name)
        # Find potential intersections
        for placed in self.placed_words:
            placed_word = placed['word'] # Already sanitized
            
            # Find common letters
            for i, char in enumerate(word):
                for j, placed_char in enumerate(placed_word):
                    if char == placed_char:
                        # Potential intersection
                        # If placed word is across, new word must be down
                        if placed['direction'] == 'across':
                            new_dir = 'down'
                            # Calculate start position for new word
                            # Intersection is at (placed_row, placed_col + j)
                            # New word char index is i
                            # So new word starts at (placed_row - i, placed_col + j)
                            start_row = placed['row'] - i
                            start_col = placed['col'] + j
                        else:
                            new_dir = 'across'
                            # Intersection is at (placed_row + j, placed_col)
                            # New word char index is i
                            # So new word starts at (placed_row + j, placed_col - i)
                            start_row = placed['row'] + j
                            start_col = placed['col'] - i
                            
                        if self._can_place_word(word, start_row, start_col, new_dir):
                            self._place_word(word, start_row, start_col, new_dir)
                            self.placed_words.append({
                                'word': word,
                                'original_word': word_obj.name,
                                'clue': word_obj.meaning,
                                'row': start_row,
                                'col': start_col,
                                'direction': new_dir,
                                'number': len(self.placed_words) + 1
                            })
                            return

    def _can_place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        if row < 0 or col < 0:
            return False
        if direction == 'across':
            if col + len(word) > self.width:
                return False
            if row >= self.height:
                return False
        else:
            if row + len(word) > self.height:
                return False
            if col >= self.width:
                return False
                
        # Check for collisions and adjacency
        for i, char in enumerate(word):
            r, c = (row, col + i) if direction == 'across' else (row + i, col)
            
            # Check if cell is occupied by a DIFFERENT letter
            if self.grid[r][c] != '' and self.grid[r][c] != char:
                return False
                
            # Check neighbors (to ensure words don't touch incorrectly)
            # This is a simplified check. Ideally we want to ensure no accidental words are formed.
            # For now, just check if we are overwriting an empty cell, ensure its perpendicular neighbors are empty
            if self.grid[r][c] == '':
                if direction == 'across':
                    if r > 0 and self.grid[r-1][c] != '': return False
                    if r < self.height - 1 and self.grid[r+1][c] != '': return False
                else:
                    if c > 0 and self.grid[r][c-1] != '': return False
                    if c < self.width - 1 and self.grid[r][c+1] != '': return False
                    
        # Check ends
        if direction == 'across':
            if col > 0 and self.grid[row][col-1] != '': return False
            if col + len(word) < self.width and self.grid[row][col+len(word)] != '': return False
        else:
            if row > 0 and self.grid[row-1][col] != '': return False
            if row + len(word) < self.height and self.grid[row+len(word)][col] != '': return False
            
        return True

    def _place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        # word is already sanitized and upper
        if not self._can_place_word(word, row, col, direction):
            return False
            
        for i, char in enumerate(word):
            r, c = (row, col + i) if direction == 'across' else (row + i, col)
            self.grid[r][c] = char
        return True
