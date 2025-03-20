import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import SyncApp

def main():
    app = QApplication(sys.argv)
    window = SyncApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()