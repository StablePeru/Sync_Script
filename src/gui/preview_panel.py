from PyQt5.QtWidgets import QTextEdit

class PreviewPanel(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText("El contenido del guion se mostrará aquí cuando se cargue un archivo.")
        
    def set_content(self, content):
        self.setText(content)
        self.moveCursor(self.textCursor().Start)