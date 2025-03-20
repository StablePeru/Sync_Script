import os
from typing import Optional, Tuple, Callable
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, 
                            QLabel, QFileDialog, QMessageBox)


class FileSelectionPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.audio_label: QLabel = None
        self.script_label: QLabel = None
        self.output_label: QLabel = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Create file selection rows
        audio_layout = self._create_file_selection_row(
            "Archivo de audio: No seleccionado",
            "Seleccionar Audio",
            self.select_audio
        )
        self.audio_label = audio_layout.itemAt(0).widget()
        
        script_layout = self._create_file_selection_row(
            "Archivo de guion: No seleccionado",
            "Seleccionar Guion",
            self.select_script
        )
        self.script_label = script_layout.itemAt(0).widget()
        
        output_layout = self._create_file_selection_row(
            "Archivo de salida: output.json",
            "Seleccionar Salida",
            self.select_output
        )
        self.output_label = output_layout.itemAt(0).widget()
        
        # Add all layouts to main layout
        layout.addLayout(audio_layout)
        layout.addLayout(script_layout)
        layout.addLayout(output_layout)
        
        self.setLayout(layout)
    
    def _create_file_selection_row(self, label_text: str, button_text: str, 
                                  button_callback: Callable) -> QHBoxLayout:
        """
        Creates a reusable file selection row with label and button
        
        Args:
            label_text: Initial text for the label
            button_text: Text for the button
            button_callback: Function to call when button is clicked
            
        Returns:
            QHBoxLayout containing the created widgets
        """
        layout = QHBoxLayout()
        label = QLabel(label_text)
        button = QPushButton(button_text)
        button.clicked.connect(button_callback)
        layout.addWidget(label)
        layout.addWidget(button)
        return layout
    
    def _update_file_path(self, label: QLabel, file_path: str, prefix: str) -> None:
        """
        Updates a label with the selected file name
        
        Args:
            label: The label to update
            file_path: The full path to the file
            prefix: Text prefix to show before the filename
        """
        label.setText(f"{prefix}: {os.path.basename(file_path)}")
        
    def select_audio(self) -> None:
        file_path, _ = self._get_open_file_dialog(
            "Seleccionar archivo de audio",
            "Archivos de audio (*.wav *.mp3 *.m4a *.ogg)"
        )
        if file_path:
            self.parent.set_audio_path(file_path)
            self._update_file_path(self.audio_label, file_path, "Archivo de audio")
            self.check_start_button()
            
    def select_script(self) -> None:
        file_path, _ = self._get_open_file_dialog(
            "Seleccionar archivo de guion",
            "Archivos de texto (*.txt)"
        )
        if file_path:
            self.parent.set_script_path(file_path)
            self._update_file_path(self.script_label, file_path, "Archivo de guion")
            
            self._load_script_preview(file_path)
            self.check_start_button()
            
    def select_output(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo JSON", "output.json", 
            "Archivos JSON (*.json)"
        )
        if file_path:
            self.parent.set_output_path(file_path)
            self._update_file_path(self.output_label, file_path, "Archivo de salida")
    
    def _get_open_file_dialog(self, title: str, file_filter: str) -> Tuple[str, str]:
        """
        Shows a file open dialog with the specified parameters
        
        Args:
            title: Dialog title
            file_filter: File filter string
            
        Returns:
            Tuple containing selected file path and filter
        """
        return QFileDialog.getOpenFileName(self, title, "", file_filter)
    
    def _load_script_preview(self, file_path: str) -> None:
        """
        Loads and displays script content in the preview panel
        
        Args:
            file_path: Path to the script file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            self.parent.show_script_preview(script_content)
        except Exception as e:
            self.parent.show_script_preview(f"Error al cargar el guion: {str(e)}")
            QMessageBox.warning(self, "Error de Lectura", 
                               f"No se pudo leer el archivo de guion:\n{str(e)}")
    
    def check_start_button(self) -> None:
        """
        Habilita el botón de inicio si se han seleccionado los archivos necesarios
        """
        if self.parent.get_audio_path() and self.parent.get_script_path():
            self.parent.sync_panel.enable_start_button()
        else:
            self.parent.sync_panel.disable_start_button()