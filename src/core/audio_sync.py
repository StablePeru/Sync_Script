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
    progress_percent = pyqtSignal(int)  # Nueva señal para porcentaje de progreso
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, audio_path, script_path):
        super().__init__()
        self.audio_path = audio_path
        self.script_path = script_path
        
    def run(self):
        try:
            # Inicializar progreso
            self.progress_percent.emit(0)
            self.progress_update.emit("Iniciando procesamiento...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.progress_update.emit(f"Usando dispositivo: {device}")
            
            # Carga del modelo (10%)
            self.progress_percent.emit(5)
            self.progress_update.emit("Cargando modelo Whisper...")
            model = whisper.load_model("large-v3-turbo").to(device)
            self.progress_percent.emit(10)
            
            # Transcripción (40%)
            self.progress_update.emit("Transcribiendo audio...")
            result = model.transcribe(
                self.audio_path,
                fp16=(device == "cuda"),
                language="en",
                verbose=False
            )
            self.progress_percent.emit(50)
            
            # Lectura del guion (5%)
            self.progress_update.emit("Leyendo guion...")
            dialogues = read_script(self.script_path)
            self.progress_percent.emit(55)
            
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
            total_segments = len(result["segments"])
            for i, segment in enumerate(result["segments"]):
                # Calcular progreso (del 55% al 90%)
                progress = 55 + int((i / total_segments) * 35)
                self.progress_percent.emit(progress)
                
                if i % 5 == 0:  # Update progress every 5 segments
                    self.progress_update.emit(f"Procesando segmento {i+1} de {total_segments}...")
                
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
            
            # Finalización (90% a 100%)
            self.progress_percent.emit(90)
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
            
            self.progress_percent.emit(95)
            self.progress_update.emit(f"\nProcesados {len(dialogues)} diálogos")
            self.progress_update.emit(f"Coincidentes: {len(matched_dialogues)}")
            self.progress_update.emit(f"No coincidentes: {len(dialogues) - len(matched_dialogues)}")
            
            self.progress_percent.emit(100)
            self.finished_signal.emit(json_data)
            
        except Exception as e:
            self.error_signal.emit(f"Ha ocurrido un error: {str(e)}")
