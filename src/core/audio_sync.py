import json
import whisper
import torch
from typing import Dict, List, Set, Any
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
    
    # Constants
    SIMILARITY_THRESHOLD = 0.5
    WHISPER_MODEL = "large-v3-turbo"
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self, audio_path: str, script_path: str):
        super().__init__()
        self.audio_path = audio_path
        self.script_path = script_path
        
    def run(self) -> None:
        try:
            self._initialize_progress()
            device = self._get_device()
            model = self._load_whisper_model(device)
            transcription = self._transcribe_audio(model, device)
            dialogues = self._load_script()
            json_data = self._create_json_structure()
            
            matched_dialogues = self._process_segments(transcription, dialogues, json_data)
            self._add_unmatched_dialogues(dialogues, matched_dialogues, json_data)
            self._finalize_results(dialogues, matched_dialogues, json_data)
            
        except Exception as e:
            self.error_signal.emit(f"Ha ocurrido un error: {str(e)}")
    
    def _initialize_progress(self) -> None:
        """Initialize progress indicators"""
        self.progress_percent.emit(0)
        self.progress_update.emit("Iniciando procesamiento...")
    
    def _get_device(self) -> str:
        """Determine the processing device (CPU or CUDA)"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.progress_update.emit(f"Usando dispositivo: {device}")
        return device
    
    def _load_whisper_model(self, device: str) -> Any:
        """Load the Whisper model"""
        self.progress_percent.emit(5)
        self.progress_update.emit("Cargando modelo Whisper...")
        model = whisper.load_model(self.WHISPER_MODEL).to(device)
        self.progress_percent.emit(10)
        return model
    
    def _transcribe_audio(self, model: Any, device: str) -> Dict[str, Any]:
        """Transcribe the audio file using Whisper"""
        self.progress_update.emit("Transcribiendo audio...")
        result = model.transcribe(
            self.audio_path,
            fp16=(device == "cuda"),
            language=self.DEFAULT_LANGUAGE,
            verbose=False
        )
        self.progress_percent.emit(50)
        return result
    
    def _load_script(self) -> List[Dict[str, str]]:
        """Load and parse the script file"""
        self.progress_update.emit("Leyendo guion...")
        dialogues = read_script(self.script_path)
        self.progress_percent.emit(55)
        return dialogues
    
    def _create_json_structure(self) -> Dict[str, Any]:
        """Create the base JSON structure for results"""
        return {
            "header": {
                "reference_number": "000000",
                "product_name": "PAW PATROL",
                "chapter_number": "01",
                "type": "Animacion"
            },
            "data": []
        }
    
    def _process_segments(self, transcription: Dict[str, Any], 
                          dialogues: List[Dict[str, str]], 
                          json_data: Dict[str, Any]) -> Set[int]:
        """Process each transcribed segment and match with dialogues"""
        matched_dialogues = set()
        
        self.progress_update.emit("Sincronizando segmentos...")
        total_segments = len(transcription["segments"])
        
        for segment_idx, segment in enumerate(transcription["segments"]):
            # Update progress (55% to 90%)
            progress = 55 + int((segment_idx / total_segments) * 35)
            self.progress_percent.emit(progress)
            
            if segment_idx % 5 == 0:
                self.progress_update.emit(f"Procesando segmento {segment_idx+1} de {total_segments}...")
            
            text = segment["text"].strip()
            start_time = segment["start"]
            end_time = segment["end"]
            
            best_match = self._find_best_dialogue_match(text, dialogues, matched_dialogues)
            
            if best_match["score"] > self.SIMILARITY_THRESHOLD and best_match["index"] >= 0:
                self._add_matched_dialogue(
                    json_data, 
                    best_match["index"], 
                    start_time, 
                    end_time, 
                    dialogues
                )
                matched_dialogues.add(best_match["index"])
        
        return matched_dialogues
    
    def _find_best_dialogue_match(self, text: str, 
                                 dialogues: List[Dict[str, str]], 
                                 matched_dialogues: Set[int]) -> Dict[str, Any]:
        """Find the best matching dialogue for a transcribed segment"""
        best_match_score = 0
        best_match_index = -1
        
        for i in range(len(dialogues)):
            if i not in matched_dialogues:
                script_line = dialogues[i]["dialogue"]
                similarity = similar(text, script_line)
                
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_index = i
        
        return {
            "score": best_match_score,
            "index": best_match_index
        }
    
    def _add_matched_dialogue(self, json_data: Dict[str, Any], 
                             dialogue_index: int, 
                             start_time: float, 
                             end_time: float,
                             dialogues: List[Dict[str, str]]) -> None:
        """Add a matched dialogue to the JSON data"""
        entry = {
            "ID": dialogue_index,
            "IN": seconds_to_timecode(start_time),
            "OUT": seconds_to_timecode(end_time),
            "PERSONAJE": dialogues[dialogue_index]["character"],
            "DIÁLOGO": dialogues[dialogue_index]["dialogue"],
            "SCENE": 1
        }
        json_data["data"].append(entry)
    
    def _add_unmatched_dialogues(self, dialogues: List[Dict[str, str]], 
                                matched_dialogues: Set[int], 
                                json_data: Dict[str, Any]) -> None:
        """Add unmatched dialogues with default timestamps"""
        self.progress_percent.emit(90)
        self.progress_update.emit("Añadiendo diálogos no coincidentes...")
        
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
    
    def _finalize_results(self, dialogues: List[Dict[str, str]], 
                         matched_dialogues: Set[int], 
                         json_data: Dict[str, Any]) -> None:
        """Finalize and emit the results"""
        self.progress_percent.emit(95)
        self.progress_update.emit(f"\nProcesados {len(dialogues)} diálogos")
        self.progress_update.emit(f"Coincidentes: {len(matched_dialogues)}")
        self.progress_update.emit(f"No coincidentes: {len(dialogues) - len(matched_dialogues)}")
        
        self.progress_percent.emit(100)
        self.finished_signal.emit(json_data)
