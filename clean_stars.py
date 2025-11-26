import re

def clean_stars():
    input_path = "nama_bintang.txt"
    output_path = "nama_bintang_clean.txt"
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    cleaned_entries = []
    current_entry = None
    
    # Common constellations to identify start of new entry
    # We can also just check if the line has enough tabs
    
    for line in lines[2:]: # Skip header
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        
        if len(parts) >= 3: # It's a new entry (Constellation, Designation, Name, [Desc])
            if current_entry:
                cleaned_entries.append(current_entry)
            
            constellation = parts[0].strip()
            designation = parts[1].strip()
            name = parts[2].strip()
            desc = parts[3].strip() if len(parts) > 3 else ""
            
            current_entry = {
                "constellation": constellation,
                "designation": designation,
                "name": name,
                "desc": desc
            }
        else:
            # Continuation of previous entry
            if current_entry:
                current_entry["desc"] += " " + line

    if current_entry:
        cleaned_entries.append(current_entry)
        
    # Process descriptions
    final_lines = ["Constellation\tDesignation\tName\tDescription\n"]
    
    for entry in cleaned_entries:
        desc = entry["desc"]
        
        # Remove citations [1], [note 1]
        desc = re.sub(r'\[.*?\]', '', desc)
        
        # Remove pronunciation /.../
        desc = re.sub(r'\/.*?\/', '', desc)
        
        # Handle NameExoWorlds - remove the prefix
        if "NameExoWorlds" in desc:
            # Remove "NameExoWorlds YYYY " prefix
            desc = re.sub(r'NameExoWorlds \d{4}\s*', '', desc)
        
        # Simplify Arabic origins
        # Pattern: "from Arabic: <arabic> <transliteration> ('<meaning>')" -> "<meaning>"
        # Pattern: "Arabic: <arabic> <transliteration> ('<meaning>')" -> "<meaning>"
        
        # Regex to capture the meaning inside ('...') or ("...")
        # We look for "Arabic:" then eventually "('" or "('"
        
        # More aggressive regex for Arabic
        # Matches "Arabic:" followed by anything until ('meaning')
        # We use (.+?) to be non-greedy but allow any character including '
        # We allow optional whitespace before the closing parenthesis
        arabic_match = re.search(r"(?:from )?Arabic:.*?\('(.+?)'\s*\)", desc)
        if arabic_match:
            desc = arabic_match.group(1).capitalize()
        else:
            # Try double quotes
            arabic_match_2 = re.search(r'(?:from )?Arabic:.*?\("(.+?)"\s*\)', desc)
            if arabic_match_2:
                desc = arabic_match_2.group(1).capitalize()
        
        # Remove any remaining Arabic script
        desc = re.sub(r'[\u0600-\u06FF]+', '', desc)
        
        # Special case: "Member of the Pleiades..."
        if "Member of the Pleiades" in desc:
            desc = "Member of the Pleiades cluster."
            
        # Latin origins
        latin_match = re.search(r"Latin for '?(.*?)'?", desc)
        if latin_match and "Latin for" in desc and len(desc) < 100:
             desc = latin_match.group(1).capitalize()

        # Clean up extra spaces and punctuation
        desc = desc.replace("  ", " ").strip()
        desc = desc.rstrip('.,;:')
        
        # Remove "The name is originally from" or similar leftovers if regex didn't catch it all but removed the Arabic
        desc = desc.replace("The name is originally from", "")
        desc = desc.replace("The name was originally", "")
        desc = desc.replace("Derived from", "")
        desc = desc.strip()
        
        # Final formatting
        line = f"{entry['constellation']}\t{entry['designation']}\t{entry['name']}\t{desc}\n"
        final_lines.append(line)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
        
    print(f"Processed {len(cleaned_entries)} stars.")

if __name__ == "__main__":
    clean_stars()
