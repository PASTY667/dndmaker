"""
Point d'entrée de l'interface graphique PyQt
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from .main_window import MainWindow


def main():
    """Lance l'application PyQt"""
    app = QApplication(sys.argv)
    app.setApplicationName("DNDMaker")
    
    # Fenêtre principale
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

