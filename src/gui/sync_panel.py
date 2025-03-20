import json
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, 
                            QProgressBar, QTextEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt

from src.core.audio_sync import SyncWorker

class SyncPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Start button
        self.start_button = QPushButton("Iniciar Sincronización")
        self.start_button.clicked.connect(self.start_sync)
        self.start_button.setEnabled(False)
        
        # Save button (initially hidden)
        self.save_button = QPushButton("Guardar Resultados")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setVisible(False)
        
        # Export to Excel button (initially hidden)
        self.export_button = QPushButton("Exportar a Excel")
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setVisible(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.export_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        # Add components to layout
        layout.addLayout(button_layout)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def enable_start_button(self):
        self.start_button.setEnabled(True)
        
    def disable_start_button(self):
        self.start_button.setEnabled(False)
        
    def start_sync(self):
        """
        Inicia el proceso de sincronización en un hilo separado
        """
        output_path = self.parent.get_output_path()
        if not output_path:
            output_path = "output.json"
            self.parent.set_output_path(output_path)
            
        self.log_area.clear()
        self.parent.results_panel.results_widget.setRowCount(0)  # Limpiar resultados anteriores
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.start_button.setEnabled(False)
        self.save_button.setVisible(False)
        self.export_button.setVisible(False)
        
        # Create and start worker thread
        self.worker = SyncWorker(
            self.parent.get_audio_path(), 
            self.parent.get_script_path()
        )
        self.worker.progress_update.connect(self.update_log)
        self.worker.finished_signal.connect(self.sync_finished)
        self.worker.error_signal.connect(self.sync_error)
        self.worker.start()
        
    def update_log(self, message):
        """
        Actualiza el área de registro con nuevos mensajes
        """
        self.log_area.append(message)
        # Auto-scroll to bottom
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.End)
        self.log_area.setTextCursor(cursor)
        
    def sync_finished(self, json_data):
        """
        Maneja la finalización exitosa del proceso de sincronización
        """
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        # Guardar los datos para uso posterior
        self.parent.set_sync_results(json_data)
        
        # Mostrar los resultados en la tabla
        self.parent.display_results(json_data)
        
        self.update_log(f"\n¡Sincronización completada!")
        self.update_log(f"Revise los resultados en la pestaña 'Resultados de Sincronización' y haga clic en 'Guardar Resultados' para guardar el archivo.")
        
        # Cambiar a la pestaña de resultados
        self.parent.switch_to_results_tab()
        
        # Mostrar los botones de guardar y exportar, y habilitar el botón de inicio
        self.save_button.setVisible(True)
        self.export_button.setVisible(True)
        self.start_button.setEnabled(True)
    
    def sync_error(self, error_message):
        """
        Maneja los errores durante el proceso de sincronización
        """
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.update_log(f"ERROR: {error_message}")
        self.start_button.setEnabled(True)
        self.save_button.setVisible(False)
        self.export_button.setVisible(False)
        
        QMessageBox.critical(self, "Error", 
                            f"Ha ocurrido un error durante la sincronización:\n{error_message}")
    
    def save_results(self):
        """
        Guarda los resultados de sincronización en un archivo JSON
        """
        try:
            output_path = self.parent.get_output_path()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.parent.get_sync_results(), f, indent=4, ensure_ascii=False)
                
            self.update_log(f"Archivo guardado en: {output_path}")
            
            QMessageBox.information(self, "Guardado Completado", 
                                   f"Los resultados se han guardado correctamente en:\n{output_path}")
            
            # Ocultar el botón de guardar después de guardar
            self.save_button.setVisible(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", 
                                f"No se pudo guardar el archivo:\n{str(e)}")
    
    def export_to_excel(self):
        """
        Exporta los resultados a un archivo Excel (XLSX) con el mismo formato y colores
        """
        try:
            import pandas as pd
            from openpyxl import Workbook
            from openpyxl.styles import PatternFill
            from openpyxl.utils.dataframe import dataframe_to_rows
            
            # Obtener datos de la tabla de resultados
            data = []
            results_widget = self.parent.results_panel.results_widget
            for row in range(results_widget.rowCount()):
                row_data = []
                for col in range(results_widget.columnCount()):
                    item = results_widget.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)
            
            # Crear DataFrame
            df = pd.DataFrame(data, columns=["ID", "IN", "OUT", "PERSONAJE", "DIÁLOGO"])
            
            # Crear un libro de Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Sincronización"
            
            # Añadir los datos al libro
            for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
                for c_idx, value in enumerate(row, 1):
                    ws.cell(row=r_idx, column=c_idx, value=value)
            
            # Aplicar formato (resaltado amarillo)
            yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            
            for row in range(results_widget.rowCount()):
                # Verificar si la primera celda de la fila está resaltada
                first_item = results_widget.item(row, 0)
                if first_item and first_item.background().color().name() == "#ffff00":
                    # Aplicar resaltado a toda la fila en Excel
                    for col in range(1, 6):  # Columnas 1-5 (A-E)
                        ws.cell(row=row+2, column=col).fill = yellow_fill  # +2 porque la fila 1 es el encabezado
            
            # Ajustar el ancho de las columnas
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Solicitar ubicación para guardar
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar como Excel", "", 
                "Archivos Excel (*.xlsx)"
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                wb.save(file_path)
                self.update_log(f"Archivo Excel guardado en: {file_path}")
                QMessageBox.information(self, "Exportación Completada", 
                                      f"Los resultados se han exportado correctamente a:\n{file_path}")
        except ImportError:
            QMessageBox.warning(self, "Módulos Faltantes", 
                              "Para exportar a Excel, necesita instalar pandas y openpyxl:\n"
                              "pip install pandas openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "Error al Exportar", 
                               f"No se pudo exportar a Excel:\n{str(e)}")