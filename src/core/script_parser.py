def read_script(script_path):
    """
    Lee un archivo de guion y extrae los diálogos y personajes
    
    Args:
        script_path (str): Ruta al archivo de guion
        
    Returns:
        list: Lista de diccionarios con personajes y diálogos
    """
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