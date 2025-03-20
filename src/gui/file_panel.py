import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, 
                            QLabel, QFileDialog, QMessageBox)

class FileSelectionPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Audio file selection
        audio_layout = QHBoxLayout()
        self.audio_label = QLabel("Archivo de audio: No seleccionado")
        audio_button = QPushButton("Seleccionar Audio")
        audio_button.clicked.connect(self.select_audio)
        audio_layout.addWidget(self.audio_label)
        audio_layout.addWidget(audio_button)
        
        # Script file selection
        script_layout = QHBoxLayout()
        self.script_label = QLabel("Archivo de guion: No seleccionado")
        script_button = QPushButton("Seleccionar Guion")
        script_button.clicked.connect(self.select_script)
        script_layout.addWidget(self.script_label)
        script_layout.addWidget(script_button)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Archivo de salida: output.json")
        output_button = QPushButton("Seleccionar Salida")
        output_button.clicked.connect(self.select_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(output_button)
        
        # Add all layouts to main layout
        layout.addLayout(audio_layout)
        layout.addLayout(script_layout)
        layout.addLayout(output_layout)
        
        self.setLayout(layout)
        
    def select_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "", 
            "Archivos de audio (*.wav *.mp3 *.m4a *.ogg)"
        )
        if file_path:
            self.parent.set_audio_path(file_path)
            self.audio_label.setText(f"Archivo de audio: {os.path.basename(file_path)}")
            self.check_start_button()
            
    def select_script(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de guion", "", 
            "Archivos de texto (*.txt)"
        )
        if file_path:
            self.parent.set_script_path(file_path)
            self.script_label.setText(f"Archivo de guion: {os.path.basename(file_path)}")
            
            # Cargar y mostrar el contenido del guion en la vista previa
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                self.parent.show_script_preview(script_content)
            except Exception as e:
                self.parent.show_script_preview(f"Error al cargar el guion: {str(e)}")
                QMessageBox.warning(self, "Error de Lectura", 
                                   f"No se pudo leer el archivo de guion:\n{str(e)}")
            
            self.check_start_button()
            
    def select_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo JSON", "output.json", 
            "Archivos JSON (*.json)"
        )
        if file_path:
            self.parent.set_output_path(file_path)
            self.output_label.setText(f"Archivo de salida: {os.path.basename(file_path)}")
    
    def check_start_button(self):
        """
        Habilita el botón de inicio si se han seleccionado los archivos necesarios
        """
        if self.parent.get_audio_path() and self.parent.get_script_path():
            self.parent.sync_panel.enable_start_button()
        else:
            self.parent.sync_panel.disable_start_button()