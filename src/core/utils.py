from difflib import SequenceMatcher

def seconds_to_timecode(seconds, fps=25):
    """
    Convierte segundos a formato de código de tiempo HH:MM:SS:FF
    
    Args:
        seconds (float): Tiempo en segundos
        fps (int): Frames por segundo
        
    Returns:
        str: Código de tiempo en formato HH:MM:SS:FF
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int((seconds % 1) * fps)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"

def similar(a, b):
    """
    Calcula la similitud entre dos cadenas de texto
    
    Args:
        a (str): Primera cadena
        b (str): Segunda cadena
        
    Returns:
        float: Valor de similitud entre 0 y 1
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()