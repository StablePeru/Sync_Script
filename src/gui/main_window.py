import os
import json
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QSplitter, QTabWidget)
from PyQt5.QtCore import Qt

from src.gui.file_panel import FileSelectionPanel
from src.gui.results_panel import ResultsPanel
from src.gui.sync_panel import SyncPanel
from src.gui.preview_panel import PreviewPanel

class SyncApp(QMainWindow):
    """
    Ventana principal de la aplicación de sincronización
    """
    def __init__(self):
        super().__init__()
        self.audio_path = ""
        self.script_path = ""
        self.output_path = ""
        self.sync_results = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Sincronizador de Audio y Guion')
        self.setGeometry(100, 100, 1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create panels
        self.file_panel = FileSelectionPanel(self)
        self.sync_panel = SyncPanel(self)
        
        # Create tabs container
        splitter = QSplitter(Qt.Vertical)
        self.tab_widget = QTabWidget()
        
        # Create preview and results panels
        self.preview_panel = PreviewPanel()
        self.results_panel = ResultsPanel()
        
        # Add panels to tabs
        self.tab_widget.addTab(self.preview_panel, "Vista Previa del Guion")
        self.tab_widget.addTab(self.results_panel, "Resultados de Sincronización")
        self.tab_widget.addTab(self.sync_panel.log_area, "Log de Procesamiento")
        
        # Add tabs to splitter
        splitter.addWidget(self.tab_widget)
        
        # Add all components to main layout
        main_layout.addWidget(self.file_panel)
        main_layout.addWidget(self.sync_panel)
        main_layout.addWidget(splitter, 1)  # Splitter takes remaining space
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def get_audio_path(self):
        return self.audio_path
    
    def set_audio_path(self, path):
        self.audio_path = path
        
    def get_script_path(self):
        return self.script_path
    
    def set_script_path(self, path):
        self.script_path = path
        
    def get_output_path(self):
        return self.output_path
    
    def set_output_path(self, path):
        self.output_path = path
        
    def get_sync_results(self):
        return self.sync_results
    
    def set_sync_results(self, results):
        self.sync_results = results
        
    def show_script_preview(self, content):
        self.preview_panel.set_content(content)
        
    def display_results(self, json_data):
        self.results_panel.display_results(json_data)
        
    def update_log(self, message):
        self.sync_panel.update_log(message)
        
    def switch_to_results_tab(self):
        self.tab_widget.setCurrentIndex(1)
