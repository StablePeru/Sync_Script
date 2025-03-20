import json
import whisper
import torch
from PyQt5.QtCore import QThread, pyqtSignal

from src.core.script_parser import read_script
from src.core.utils import seconds_to_timecode, similar

class SyncWorker(QThread):
    """
    Worker thread para procesar la sincronización de audio y guion
    """
    progress_update = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, audio_path, script_path):
        super().__init__()
        self.audio_path = audio_path
        self.script_path = script_path
        
    def run(self):
        try:
            self.progress_update.emit("Iniciando procesamiento...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.progress_update.emit(f"Usando dispositivo: {device}")
            
            self.progress_update.emit("Cargando modelo Whisper...")
            model = whisper.load_model("base").to(device)
            
            self.progress_update.emit("Transcribiendo audio...")
            result = model.transcribe(
                self.audio_path,
                fp16=(device == "cuda"),
                language="en",
                verbose=False
            )
            
            self.progress_update.emit("Leyendo guion...")
            dialogues = read_script(self.script_path)
            
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
            
            self.progress_update.emit("Sincronizando segmentos...")
            # Process each segment with its timestamp
            for i, segment in enumerate(result["segments"]):
                if i % 5 == 0:  # Update progress every 5 segments
                    self.progress_update.emit(f"Procesando segmento {i+1} de {len(result['segments'])}...")
                
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
            
            self.progress_update.emit("Añadiendo diálogos no coincidentes...")
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
            
            self.progress_update.emit(f"\nProcesados {len(dialogues)} diálogos")
            self.progress_update.emit(f"Coincidentes: {len(matched_dialogues)}")
            self.progress_update.emit(f"No coincidentes: {len(dialogues) - len(matched_dialogues)}")
            
            self.finished_signal.emit(json_data)
            
        except Exception as e:
            self.error_signal.emit(f"Ha ocurrido un error: {str(e)}")