from difflib import SequenceMatcher
from typing import Union, Tuple


def seconds_to_timecode(seconds: float, fps: int = 25) -> str:
    """
    Convierte segundos a formato de código de tiempo HH:MM:SS:FF
    
    Args:
        seconds (float): Tiempo en segundos
        fps (int): Frames por segundo
        
    Returns:
        str: Código de tiempo en formato HH:MM:SS:FF
    """
    components = _split_seconds_to_components(seconds, fps)
    hours, minutes, secs, frames = components
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


def _split_seconds_to_components(seconds: float, fps: int) -> Tuple[int, int, int, int]:
    """
    Divide los segundos en componentes de tiempo (horas, minutos, segundos, frames)
    
    Args:
        seconds (float): Tiempo en segundos
        fps (int): Frames por segundo
        
    Returns:
        Tuple[int, int, int, int]: Tupla con (horas, minutos, segundos, frames)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int((seconds % 1) * fps)
    
    return hours, minutes, secs, frames


def similar(a: str, b: str) -> float:
    """
    Calcula la similitud entre dos cadenas de texto
    
    Args:
        a (str): Primera cadena
        b (str): Segunda cadena
        
    Returns:
        float: Valor de similitud entre 0 y 1
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()