
from generator import CrosswordGenerator
from models import Star

def test_generation():
    # Create dummy data with spaces and dots
    stars = [
        Star(name="Alpha Centauri", constellation="Centaurus", meaning="Closest star system"),
        Star(name="R. Leonis", constellation="Leo", meaning="Variable star"),
        Star(name="Betelgeuse", constellation="Orion", meaning="Red supergiant")
    ]

    generator = CrosswordGenerator(width=20, height=20)
    puzzle = generator.generate(stars)
    
    grid = puzzle['grid']
    words = puzzle['words']
    
    print("Placed words:")
    for w in words:
        print(f"- {w['word']} ({w['direction']}) at {w['row']},{w['col']}")
        
    # Check for spaces and dots in the grid
    found_space = False
    found_dot = False
    
    for row in grid:
        for cell in row:
            if cell == ' ':
                found_space = True
            if cell == '.':
                found_dot = True
                
    print(f"\nFound space in grid: {found_space}")
    print(f"Found dot in grid: {found_dot}")

    if found_space or found_dot:
        print("\nISSUE REPRODUCED: Grid contains spaces or dots.")
    else:
        print("\nISSUE NOT REPRODUCED: Grid is clean.")

if __name__ == "__main__":
    test_generation()
