import os
import json
from typing import Dict, Any, Optional
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
        # Initialize attributes
        self.audio_path: str = ""
        self.script_path: str = ""
        self.output_path: str = "output.json"  # Default output path
        self.sync_results: Optional[Dict[str, Any]] = None
        
        # Initialize UI components
        self.file_panel: Optional[FileSelectionPanel] = None
        self.sync_panel: Optional[SyncPanel] = None
        self.preview_panel: Optional[PreviewPanel] = None
        self.results_panel: Optional[ResultsPanel] = None
        self.tab_widget: Optional[QTabWidget] = None
        
        # Setup UI
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface components"""
        self._setup_window_properties()
        main_widget, main_layout = self._create_main_layout()
        
        # Create and add UI components
        self._create_panels()
        self._create_tab_container(main_layout)
        
        # Finalize layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def _setup_window_properties(self):
        """Set up window title and geometry"""
        self.setWindowTitle('Sincronizador de Audio y Guion')
        self.setGeometry(100, 100, 1000, 700)
    
    def _create_main_layout(self) -> tuple:
        """Create the main widget and layout"""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        return main_widget, main_layout
    
    def _create_panels(self):
        """Create all application panels"""
        self.file_panel = FileSelectionPanel(self)
        self.sync_panel = SyncPanel(self)
        self.preview_panel = PreviewPanel()
        self.results_panel = ResultsPanel()
    
    def _create_tab_container(self, main_layout: QVBoxLayout):
        """Create and set up the tab container"""
        # Create tabs container with splitter
        splitter = QSplitter(Qt.Vertical)
        self.tab_widget = QTabWidget()
        
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
    
    # Path getters and setters
    def get_audio_path(self) -> str:
        """Get the audio file path"""
        return self.audio_path
    
    def set_audio_path(self, path: str) -> None:
        """Set the audio file path"""
        self.audio_path = path
        
    def get_script_path(self) -> str:
        """Get the script file path"""
        return self.script_path
    
    def set_script_path(self, path: str) -> None:
        """Set the script file path"""
        self.script_path = path
        
    def get_output_path(self) -> str:
        """Get the output file path"""
        return self.output_path
    
    def set_output_path(self, path: str) -> None:
        """Set the output file path"""
        self.output_path = path
    
    # Results handling
    def get_sync_results(self) -> Optional[Dict[str, Any]]:
        """Get the synchronization results"""
        return self.sync_results
    
    def set_sync_results(self, results: Dict[str, Any]) -> None:
        """Set the synchronization results"""
        self.sync_results = results
    
    # UI update methods
    def show_script_preview(self, content: str) -> None:
        """Update the script preview panel with content"""
        self.preview_panel.set_content(content)
        
    def display_results(self, json_data: Dict[str, Any]) -> None:
        """Display results in the results panel"""
        self.results_panel.display_results(json_data)
        
    def update_log(self, message: str) -> None:
        """Update the log with a new message"""
        self.sync_panel.update_log(message)
        
    def switch_to_results_tab(self) -> None:
        """Switch to the results tab"""
        self.tab_widget.setCurrentIndex(1)
