"""
Widget pour l'upload et l'affichage d'images
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QMimeData
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent

from ...core.i18n import tr
from .draggable_image_label import DraggableImageLabel


class ImageUploadWidget(QWidget):
    """Widget pour uploader et afficher une image"""
    
    def __init__(self, project_service=None, entity_type: str = "", entity_id: str = "", parent=None):
        """
        Crée un widget d'upload d'image
        
        Args:
            project_service: Service de projet
            entity_type: Type d'entité ('character', 'scene', 'session', etc.)
            entity_id: ID de l'entité
            parent: Widget parent
        """
        super().__init__(parent)
        self.project_service = project_service
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.current_image_id = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Label pour l'image avec support du drag and drop
        self.image_label = DraggableImageLabel(
            parent=self,
            on_image_dropped=self._handle_dropped_image
        )
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setMaximumSize(300, 300)
        self.image_label.setText(tr("image.no_image") + "\n" + tr("image.drag_drop_hint"))
        layout.addWidget(self.image_label)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton(tr("image.upload"))
        self.upload_btn.clicked.connect(self._upload_image)
        button_layout.addWidget(self.upload_btn)
        
        self.remove_btn = QPushButton(tr("image.remove"))
        self.remove_btn.clicked.connect(self._remove_image)
        self.remove_btn.setEnabled(False)
        button_layout.addWidget(self.remove_btn)
        
        layout.addLayout(button_layout)
    
    def _upload_image(self):
        """Ouvre un dialogue pour sélectionner une image"""
        if not self.project_service or not self.project_service.media_service:
            QMessageBox.warning(self, tr("msg.error"), tr("image.service_unavailable"))
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("image.select_file"),
            "",
            tr("image.file_filter")
        )
        
        if not file_path:
            return
        
        source_path = Path(file_path)
        
        # Vérifier que c'est bien une image
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if source_path.suffix.lower() not in valid_extensions:
            QMessageBox.warning(self, tr("msg.error"), tr("image.invalid_format"))
            return
        
        # Upload l'image
        image_id = self.project_service.media_service.upload_image(
            source_path,
            self.entity_type,
            self.entity_id
        )
        
        if image_id:
            self.current_image_id = image_id
            self._display_image(image_id)
            self.remove_btn.setEnabled(True)
            # Sauvegarder le projet
            self.project_service.save_project()
        else:
            QMessageBox.warning(self, tr("msg.error"), tr("image.upload_failed"))
    
    def _remove_image(self):
        """Supprime l'image actuelle"""
        if not self.current_image_id:
            return
        
        reply = QMessageBox.question(
            self,
            tr("msg.confirm"),
            tr("image.confirm_remove"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.project_service and self.project_service.media_service:
                self.project_service.media_service.delete_media(self.current_image_id)
                self.project_service.save_project()
            
            self.current_image_id = None
            self.image_label.clear()
            self.image_label.setText(tr("image.no_image"))
            self.remove_btn.setEnabled(False)
    
    def _display_image(self, image_id: str):
        """Affiche une image"""
        if not self.project_service or not self.project_service.media_service:
            return
        
        image_path = self.project_service.media_service.get_image_path(image_id)
        if not image_path or not image_path.exists():
            return
        
        try:
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                # Redimensionner pour s'adapter au label
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Erreur lors de l'affichage de l'image: {e}")
    
    def set_image_id(self, image_id: str):
        """Définit l'image à afficher"""
        self.current_image_id = image_id
        if image_id:
            self._display_image(image_id)
            self.remove_btn.setEnabled(True)
        else:
            self.image_label.clear()
            self.image_label.setText(tr("image.no_image"))
            self.remove_btn.setEnabled(False)
    
    def get_image_id(self) -> str:
        """Récupère l'ID de l'image actuelle"""
        return self.current_image_id or ""
    
    def _handle_dropped_image(self, file_path: Path):
        """Gère le dépôt d'une image via drag and drop"""
        if not self.project_service or not self.project_service.media_service:
            QMessageBox.warning(self, tr("msg.error"), tr("image.service_unavailable"))
            return
        
        # Vérifier que c'est bien une image
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if file_path.suffix.lower() not in valid_extensions:
            QMessageBox.warning(self, tr("msg.error"), tr("image.invalid_format"))
            return
        
        # Upload l'image
        image_id = self.project_service.media_service.upload_image(
            file_path,
            self.entity_type,
            self.entity_id
        )
        
        if image_id:
            self.current_image_id = image_id
            self._display_image(image_id)
            self.remove_btn.setEnabled(True)
            # Sauvegarder le projet
            self.project_service.save_project()
        else:
            QMessageBox.warning(self, tr("msg.error"), tr("image.upload_failed"))

