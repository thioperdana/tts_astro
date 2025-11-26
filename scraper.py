
from sqlmodel import Session, SQLModel, create_engine
from models import Star

def scrape_stars():
    file_path = "nama_bintang.txt"
    print(f"Reading {file_path}...")
    
    stars = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines[2:]:  # Skip header lines
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 4:
                constellation = parts[0].strip()
                designation = parts[1].strip()
                name = parts[2].strip()
                description = parts[3].strip()
                
                if name and constellation:
                    # Always start with "Bintang di [constellation]"
                    meaning = f"Bintang di {constellation}"
                    
                    if description:
                        meaning += f". {description}"
                    
                    stars.append(Star(
                        name=name,
                        constellation=constellation,
                        meaning=meaning
                    ))
        
        print(f"Found {len(stars)} stars from file.")
    except Exception as e:
        print(f"Error reading file: {e}")
        # Fallback data
        stars = [
            Star(name="Sirius", constellation="Canis Major", meaning="Bintang di Canis Major. The brightest star in the sky"),
            Star(name="Canopus", constellation="Carina", meaning="Bintang di Carina"),
            Star(name="Arcturus", constellation="Boötes", meaning="Bintang di Boötes. Guardian of the Bear"),
            Star(name="Vega", constellation="Lyra", meaning="Bintang di Lyra"),
            Star(name="Rigel", constellation="Orion", meaning="Bintang di Orion"),
            Star(name="Betelgeuse", constellation="Orion", meaning="Bintang di Orion"),
        ]
        print(f"Using {len(stars)} fallback stars.")
            
    return stars

def init_db():
    sqlite_file_name = "data/astro.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)
    return engine

if __name__ == "__main__":
    engine = init_db()
    stars = scrape_stars()
    
    with Session(engine) as session:
        # Clear existing data using raw SQL to be safe and simple
        from sqlmodel import text
        session.exec(text("DELETE FROM star"))
        session.commit()
        print("Cleared existing data.")
        
        for star in stars:
            session.add(star)
        session.commit()
        print("Database populated.")
