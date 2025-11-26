
import re

def analyze_stars():
    file_path = "nama_bintang.txt"
    print(f"Reading {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        count = 0
        for line in lines[2:]:  # Skip header lines
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 4:
                constellation = parts[0].strip()
                name = parts[2].strip()
                description = parts[3].strip()
                
                if name and constellation:
                    meaning = f"Bintang di {constellation}"
                    
                    if description:
                        meaning += f". {description}"
                    
                    print(f"Name: {name}")
                    print(f"Meaning: {meaning}")
                    print("-" * 20)
                    
                    count += 1
                    if count >= 50:
                        break
                        
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    analyze_stars()
