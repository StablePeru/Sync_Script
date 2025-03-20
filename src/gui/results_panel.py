from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QVBoxLayout, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ResultsPanel(QWidget):
    # Constants
    DEFAULT_TIMECODE = "00:00:00:00"
    HIGHLIGHT_COLOR = Qt.yellow
    FPS = 30
    
    # Table columns
    COL_ID = 0
    COL_IN = 1
    COL_OUT = 2
    COL_CHARACTER = 3
    COL_DIALOGUE = 4
    COLUMN_COUNT = 5
    
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        
    def initUI(self) -> None:
        layout = QVBoxLayout()
        
        # Results table
        self.results_widget = QTableWidget()
        self.results_widget.setColumnCount(self.COLUMN_COUNT)
        self.results_widget.setHorizontalHeaderLabels(["ID", "IN", "OUT", "PERSONAJE", "DIÁLOGO"])
        self.results_widget.horizontalHeader().setSectionResizeMode(self.COL_DIALOGUE, QHeaderView.Stretch)
        
        layout.addWidget(self.results_widget)
        self.setLayout(layout)
        
    def display_results(self, json_data: Dict[str, Any]) -> None:
        """
        Muestra los resultados de sincronización en la tabla
        """
        data = json_data.get("data", [])
        self.results_widget.setRowCount(len(data))
        
        prev_in_time = None  # Para rastrear el tiempo IN anterior
        
        for row, item in enumerate(data):
            self._populate_row(row, item, prev_in_time)
            prev_in_time = item.get("IN", self.DEFAULT_TIMECODE)
    
    def _populate_row(self, row: int, item: Dict[str, Any], prev_in_time: Optional[str]) -> None:
        """Populate a single row in the results table"""
        # Set cell values
        self._set_cell_value(row, self.COL_ID, str(item.get("ID", "")))
        in_time = item.get("IN", self.DEFAULT_TIMECODE)
        out_time = item.get("OUT", self.DEFAULT_TIMECODE)
        self._set_cell_value(row, self.COL_IN, in_time)
        self._set_cell_value(row, self.COL_OUT, out_time)
        self._set_cell_value(row, self.COL_CHARACTER, item.get("PERSONAJE", ""))
        self._set_cell_value(row, self.COL_DIALOGUE, item.get("DIÁLOGO", ""))
        
        # Check if row needs highlighting
        if self._should_highlight_row(in_time, out_time, prev_in_time):
            self._highlight_row(row)
    
    def _set_cell_value(self, row: int, column: int, value: str) -> None:
        """Set a cell value in the table"""
        item = QTableWidgetItem(value)
        self.results_widget.setItem(row, column, item)
    
    def _should_highlight_row(self, in_time: str, out_time: str, prev_in_time: Optional[str]) -> bool:
        """Determine if a row should be highlighted"""
        if in_time == self.DEFAULT_TIMECODE or out_time == self.DEFAULT_TIMECODE:
            return True
        if prev_in_time and self._compare_timecodes(in_time, prev_in_time) < 0:
            return True
        return False
    
    def _highlight_row(self, row: int) -> None:
        """Highlight all cells in a row"""
        for col in range(self.COLUMN_COUNT):
            item = self.results_widget.item(row, col)
            if item:
                item.setBackground(self.HIGHLIGHT_COLOR)
    
    def _compare_timecodes(self, tc1: str, tc2: str) -> int:
        """
        Compara dos códigos de tiempo en formato "HH:MM:SS:FF"
        Retorna: -1 si tc1 < tc2, 0 si son iguales, 1 si tc1 > tc2
        """
        tc1_seconds = self._timecode_to_seconds(tc1)
        tc2_seconds = self._timecode_to_seconds(tc2)
        
        if tc1_seconds < tc2_seconds:
            return -1
        elif tc1_seconds > tc2_seconds:
            return 1
        else:
            return 0
    
    def _timecode_to_seconds(self, timecode: str) -> float:
        """Convert a timecode string to seconds"""
        parts = timecode.split(':')
        if len(parts) != 4:
            return 0.0
        
        try:
            h, m, s, f = map(int, parts)
            return h * 3600 + m * 60 + s + f / self.FPS
        except ValueError:
            # Handle invalid timecode format
            return 0.0
    
    def get_table_data(self) -> List[List[str]]:
        """
        Obtiene los datos de la tabla para exportación
        """
        data = []
        for row in range(self.results_widget.rowCount()):
            row_data = []
            for col in range(self.results_widget.columnCount()):
                item = self.results_widget.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data