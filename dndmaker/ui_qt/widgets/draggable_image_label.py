"""
Label personnalisé avec support du drag and drop pour les images
"""

from pathlib import Path
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap


class DraggableImageLabel(QLabel):
    """Label qui accepte le drag and drop d'images"""
    
    def __init__(self, parent=None, on_image_dropped=None):
        """
        Crée un label avec support du drag and drop
        
        Args:
            parent: Widget parent
            on_image_dropped: Callback appelé avec le chemin du fichier quand une image est déposée
        """
        super().__init__(parent)
        self.on_image_dropped = on_image_dropped
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed gray; background-color: #f0f0f0;")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Appelé quand un élément est glissé sur le widget"""
        if event.mimeData().hasUrls():
            # Vérifier que c'est une image
            urls = event.mimeData().urls()
            if urls:
                file_path = Path(urls[0].toLocalFile())
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                if file_path.suffix.lower() in valid_extensions:
                    event.acceptProposedAction()
                    self.setStyleSheet("border: 2px dashed blue; background-color: #e0e0ff;")
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Appelé quand l'élément quitte le widget"""
        self.setStyleSheet("border: 2px dashed gray; background-color: #f0f0f0;")
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        """Appelé quand un élément est déposé sur le widget"""
        self.setStyleSheet("border: 2px dashed gray; background-color: #f0f0f0;")
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = Path(urls[0].toLocalFile())
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                if file_path.suffix.lower() in valid_extensions:
                    event.acceptProposedAction()
                    if self.on_image_dropped:
                        self.on_image_dropped(file_path)
                    return
        event.ignore()

