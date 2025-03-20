import json
import whisper
import torch
from difflib import SequenceMatcher

def read_script(script_path):
    dialogues = []
    
    with open(script_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Filter out empty lines and stage directions that start with '|'
    filtered_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('|')]
    
    i = 0
    while i < len(filtered_lines):
        # Check if this line looks like a character name (all uppercase, not starting with < or ()
        if (i < len(filtered_lines) and 
            filtered_lines[i].isupper() and 
            not filtered_lines[i].startswith('<') and 
            not filtered_lines[i].startswith('(')):
            
            character = filtered_lines[i]
            i += 1
            
            # Collect all dialogue lines until we hit another character name
            dialogue_parts = []
            while (i < len(filtered_lines) and 
                   not (filtered_lines[i].isupper() and 
                        not filtered_lines[i].startswith('<') and 
                        not filtered_lines[i].startswith('('))):
                dialogue_parts.append(filtered_lines[i])
                i += 1
            
            # Join all dialogue parts with spaces
            if dialogue_parts:
                full_dialogue = " ".join(dialogue_parts)
                dialogues.append({
                    "character": character,
                    "dialogue": full_dialogue
                })
            else:
                # If no dialogue found, add character with empty dialogue
                dialogues.append({
                    "character": character,
                    "dialogue": ""
                })
                # Don't increment i here as we're already at the next character
        else:
            # Skip any lines that don't match our pattern
            i += 1
    
    return dialogues

def seconds_to_timecode(seconds, fps=25):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int((seconds % 1) * fps)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def sync_audio_with_script(audio_path, script_path):
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        model = whisper.load_model("base").to(device)
        
        # Load and transcribe audio with timestamps
        result = model.transcribe(
            audio_path,
            fp16=(device == "cuda"),
            language="en",
            verbose=True
        )
        
        dialogues = read_script(script_path)
        
        json_data = {
            "header": {
                "reference_number": "000000",
                "product_name": "PAW PATROL",
                "chapter_number": "01",
                "type": "Animacion"
            },
            "data": []
        }
        
        # Create a set to track matched dialogues
        matched_dialogues = set()
        
        # Process each segment with its timestamp
        for segment in result["segments"]:
            text = segment["text"].strip()
            start_time = segment["start"]
            end_time = segment["end"]
            
            # Try to match with remaining dialogues
            best_match_score = 0
            best_match_index = -1
            
            # Look ahead in dialogues for best match
            for i in range(len(dialogues)):
                if i not in matched_dialogues:
                    script_line = dialogues[i]["dialogue"]
                    similarity = similar(text, script_line)
                    
                    if similarity > best_match_score:
                        best_match_score = similarity
                        best_match_index = i
            
            # If we found a good match (threshold 0.5)
            if best_match_score > 0.5 and best_match_index >= 0:
                entry = {
                    "ID": best_match_index,
                    "IN": seconds_to_timecode(start_time),
                    "OUT": seconds_to_timecode(end_time),
                    "PERSONAJE": dialogues[best_match_index]["character"],
                    "DIÁLOGO": dialogues[best_match_index]["dialogue"],
                    "SCENE": 1
                }
                json_data["data"].append(entry)
                matched_dialogues.add(best_match_index)
        
        # Add unmatched dialogues with 00:00:00:00 timestamps
        for i in range(len(dialogues)):
            if i not in matched_dialogues:
                entry = {
                    "ID": i,
                    "IN": "00:00:00:00",
                    "OUT": "00:00:00:00",
                    "PERSONAJE": dialogues[i]["character"],
                    "DIÁLOGO": dialogues[i]["dialogue"],
                    "SCENE": 1
                }
                json_data["data"].append(entry)
        
        # Sort the data by ID to maintain script order
        json_data["data"].sort(key=lambda x: x["ID"])
        
        # Write the result to JSON file
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        
        print(f"\nProcessed all {len(dialogues)} dialogues")
        print(f"Matched: {len(matched_dialogues)}")
        print(f"Unmatched: {len(dialogues) - len(matched_dialogues)}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

# Usage
audio_path = "c:\\Users\\PeruMixer\\Desktop\\Programazioa\\ML\\SincSub2\\Paw_Patrol_S2-05 -3a.wav"
script_path = "c:\\Users\\PeruMixer\\Desktop\\Programazioa\\ML\\SincSub2\\guion.txt"
sync_audio_with_script(audio_path, script_path)