from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QVBoxLayout, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

class ResultsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Results table
        self.results_widget = QTableWidget()
        self.results_widget.setColumnCount(5)
        self.results_widget.setHorizontalHeaderLabels(["ID", "IN", "OUT", "PERSONAJE", "DIÁLOGO"])
        self.results_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        layout.addWidget(self.results_widget)
        self.setLayout(layout)
        
    def display_results(self, json_data):
        """
        Muestra los resultados de sincronización en la tabla
        """
        data = json_data.get("data", [])
        self.results_widget.setRowCount(len(data))
        
        prev_in_time = None  # Para rastrear el tiempo IN anterior
        
        for row, item in enumerate(data):
            # ID
            id_item = QTableWidgetItem(str(item.get("ID", "")))
            self.results_widget.setItem(row, 0, id_item)
            
            # IN
            in_time = item.get("IN", "00:00:00:00")
            in_item = QTableWidgetItem(in_time)
            self.results_widget.setItem(row, 1, in_item)
            
            # OUT
            out_time = item.get("OUT", "00:00:00:00")
            out_item = QTableWidgetItem(out_time)
            self.results_widget.setItem(row, 2, out_item)
            
            # PERSONAJE
            character_item = QTableWidgetItem(item.get("PERSONAJE", ""))
            self.results_widget.setItem(row, 3, character_item)
            
            # DIÁLOGO
            dialogue_item = QTableWidgetItem(item.get("DIÁLOGO", ""))
            self.results_widget.setItem(row, 4, dialogue_item)
            
            # Resaltar filas sin tiempo asignado o con tiempo anterior al previo
            highlight_row = False
            if in_time == "00:00:00:00" or out_time == "00:00:00:00":
                highlight_row = True
            elif prev_in_time and self._compare_timecodes(in_time, prev_in_time) < 0:
                # Si el tiempo actual es menor que el anterior
                highlight_row = True
                
            # Aplicar resaltado a toda la fila si es necesario
            if highlight_row:
                for col in range(5):  # Resaltar todas las columnas de la fila
                    self.results_widget.item(row, col).setBackground(Qt.yellow)
            
            prev_in_time = in_time  # Actualizar el tiempo anterior
    
    def _compare_timecodes(self, tc1, tc2):
        """
        Compara dos códigos de tiempo en formato "HH:MM:SS:FF"
        Retorna: -1 si tc1 < tc2, 0 si son iguales, 1 si tc1 > tc2
        """
        # Convertir a segundos para comparación
        def tc_to_seconds(tc):
            parts = tc.split(':')
            if len(parts) != 4:
                return 0
            h, m, s, f = map(int, parts)
            return h * 3600 + m * 60 + s + f/30  # Asumiendo 30fps
            
        tc1_seconds = tc_to_seconds(tc1)
        tc2_seconds = tc_to_seconds(tc2)
        
        if tc1_seconds < tc2_seconds:
            return -1
        elif tc1_seconds > tc2_seconds:
            return 1
        else:
            return 0
    
    def get_table_data(self):
        """
        Obtiene los datos de la tabla para exportación
        """
        data = []
        for row in range(self.results_widget.rowCount()):
            row_data = []
            for col in range(self.results_widget.columnCount()):
                item = self.results_widget.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append(row_data)
        return data