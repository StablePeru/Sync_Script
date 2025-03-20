from typing import List, Dict, Any


def read_script(script_path: str) -> List[Dict[str, str]]:
    """
    Lee un archivo de guion y extrae los diálogos y personajes
    
    Args:
        script_path (str): Ruta al archivo de guion
        
    Returns:
        list: Lista de diccionarios con personajes y diálogos
    """
    dialogues = []
    
    # Read and filter the script file
    filtered_lines = _read_and_filter_script(script_path)
    
    # Process the filtered lines to extract characters and dialogues
    i = 0
    while i < len(filtered_lines):
        if _is_character_line(filtered_lines[i]):
            character = filtered_lines[i]
            i += 1
            
            dialogue_parts, i = _collect_dialogue_parts(filtered_lines, i)
            
            if dialogue_parts:
                full_dialogue = " ".join(dialogue_parts)
                dialogues.append({
                    "character": character,
                    "dialogue": full_dialogue
                })
            else:
                dialogues.append({
                    "character": character,
                    "dialogue": ""
                })
        else:
            i += 1
    
    return dialogues


def _read_and_filter_script(script_path: str) -> List[str]:
    """
    Read the script file and filter out empty lines and stage directions
    
    Args:
        script_path (str): Path to the script file
        
    Returns:
        List[str]: Filtered lines from the script
    """
    with open(script_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Filter out empty lines and stage directions that start with '|'
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith('|')]


def _is_character_line(line: str) -> bool:
    """
    Check if a line represents a character name
    
    Args:
        line (str): The line to check
        
    Returns:
        bool: True if the line is a character name, False otherwise
    """
    return (line.isupper() and 
            not line.startswith('<') and 
            not line.startswith('('))


def _collect_dialogue_parts(filtered_lines: List[str], start_index: int) -> tuple:
    """
    Collect all dialogue parts for a character
    
    Args:
        filtered_lines (List[str]): The filtered script lines
        start_index (int): The index to start collecting from
        
    Returns:
        tuple: (dialogue_parts, new_index)
    """
    dialogue_parts = []
    i = start_index
    
    while (i < len(filtered_lines) and 
           not _is_character_line(filtered_lines[i])):
        dialogue_parts.append(filtered_lines[i])
        i += 1
    
    return dialogue_parts, i