import sys
from PyQt5.QtWidgets import QApplication
# Fix the import to match the actual class name in main_window.py
# If your class is named differently, update this import
from src.gui.main_window import SyncApp  # Changed from MainWindow to SyncApp as an example

def main():
    """
    Punto de entrada principal de la aplicación
    """
    app = QApplication(sys.argv)
    window = SyncApp()  # Update this to match the class name
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()