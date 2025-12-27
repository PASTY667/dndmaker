"""
Widget de timeline/arbre visuel pour les scènes
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from typing import List, Dict, Optional
from datetime import datetime

from ...models.scene import Scene
from ...models.session import Session
from ...services.project_service import ProjectService
from ...core.i18n import tr


class SceneTimelineWidget(QWidget):
    """Widget affichant une timeline/arbre visuel des scènes"""
    
    scene_selected = pyqtSignal(str)  # Émet l'ID de la scène sélectionnée
    
    def __init__(self, project_service: ProjectService, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.current_scene_id: Optional[str] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Titre
        title = QLabel("Timeline des scènes")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Vue graphique pour la timeline
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.NoDrag)
        layout.addWidget(self.graphics_view)
        
        # Connecter les événements de clic
        self.graphics_scene.selectionChanged.connect(self._on_selection_changed)
        
        # Contrôles
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Actualiser")
        self.refresh_btn.clicked.connect(self.refresh)
        controls_layout.addWidget(self.refresh_btn)
        
        self.view_mode_combo = QPushButton("Vue: Timeline")
        self.view_mode_combo.setCheckable(True)
        self.view_mode_combo.clicked.connect(self._toggle_view_mode)
        controls_layout.addWidget(self.view_mode_combo)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.view_mode = "timeline"  # "timeline" ou "tree"
    
    def _toggle_view_mode(self):
        """Bascule entre la vue timeline et arbre"""
        if self.view_mode == "timeline":
            self.view_mode = "tree"
            self.view_mode_combo.setText("Vue: Arbre")
        else:
            self.view_mode = "timeline"
            self.view_mode_combo.setText("Vue: Timeline")
        self.refresh()
    
    def set_current_scene(self, scene_id: Optional[str]):
        """Définit la scène actuellement affichée"""
        self.current_scene_id = scene_id
        self.refresh()
    
    def refresh(self):
        """Rafraîchit l'affichage"""
        self.graphics_scene.clear()
        
        if not self.project_service or not self.project_service.scene_service:
            return
        
        scenes = self.project_service.scene_service.get_all_scenes()
        if not scenes:
            return
        
        if self.view_mode == "timeline":
            self._draw_timeline(scenes)
        else:
            self._draw_tree(scenes)
    
    def _draw_timeline(self, scenes: List[Scene]):
        """Dessine la vue timeline"""
        # Organiser les scènes par sessions
        sessions = self.project_service.session_service.get_all_sessions() if self.project_service.session_service else []
        
        y_pos = 50
        x_start = 50
        scene_width = 150
        scene_height = 80
        spacing = 20
        
        # Dessiner les sessions
        for session in sessions:
            # Titre de la session
            session_text = self.graphics_scene.addText(
                f"Session: {session.title}",
                QFont("Arial", 12, QFont.Weight.Bold)
            )
            session_text.setPos(x_start, y_pos - 30)
            
            # Dessiner les scènes de la session
            x_pos = x_start
            for i, scene_id in enumerate(session.scenes):
                scene = next((s for s in scenes if s.id == scene_id), None)
                if scene:
                    self._draw_scene_box(
                        scene, x_pos, y_pos, scene_width, scene_height,
                        is_current=(scene.id == self.current_scene_id)
                    )
                    
                    # Ligne de connexion
                    if i > 0:
                        line = self.graphics_scene.addLine(
                            x_pos - spacing, y_pos + scene_height // 2,
                            x_pos, y_pos + scene_height // 2,
                            QPen(QColor(100, 100, 100), 2)
                        )
                    
                    x_pos += scene_width + spacing
            
            y_pos += scene_height + 60
        
        # Dessiner les scènes non assignées
        assigned_scene_ids = set()
        for session in sessions:
            assigned_scene_ids.update(session.scenes)
        
        unassigned_scenes = [s for s in scenes if s.id not in assigned_scene_ids]
        if unassigned_scenes:
            unassigned_text = self.graphics_scene.addText(
                "Scènes non assignées",
                QFont("Arial", 12, QFont.Weight.Bold)
            )
            unassigned_text.setPos(x_start, y_pos - 30)
            
            x_pos = x_start
            for i, scene in enumerate(unassigned_scenes):
                self._draw_scene_box(
                    scene, x_pos, y_pos, scene_width, scene_height,
                    is_current=(scene.id == self.current_scene_id)
                )
                if i < len(unassigned_scenes) - 1:
                    x_pos += scene_width + spacing
    
    def _draw_tree(self, scenes: List[Scene]):
        """Dessine la vue arbre des relations"""
        # Créer un graphe des relations
        scene_dict = {s.id: s for s in scenes}
        
        # Trouver les scènes racines (celles qui ne sont référencées par aucune autre)
        referenced_ids = set()
        for scene in scenes:
            referenced_ids.update(scene.referenced_scenes)
        
        root_scenes = [s for s in scenes if s.id not in referenced_ids]
        
        y_pos = 50
        x_start = 50
        scene_width = 150
        scene_height = 60
        level_spacing = 200
        
        def draw_scene_recursive(scene: Scene, x: float, y: float, level: int = 0):
            """Dessine récursivement une scène et ses références"""
            # Dessiner la scène
            self._draw_scene_box(
                scene, x, y, scene_width, scene_height,
                is_current=(scene.id == self.current_scene_id)
            )
            
            # Dessiner les scènes référencées
            if scene.referenced_scenes:
                child_y = y + scene_height + 50
                child_x_start = x - (len(scene.referenced_scenes) - 1) * (scene_width + 30) / 2
                
                for i, ref_id in enumerate(scene.referenced_scenes):
                    ref_scene = scene_dict.get(ref_id)
                    if ref_scene:
                        child_x = child_x_start + i * (scene_width + 30)
                        
                        # Ligne de connexion
                        line = self.graphics_scene.addLine(
                            x + scene_width // 2, y + scene_height,
                            child_x + scene_width // 2, child_y,
                            QPen(QColor(100, 100, 100), 2)
                        )
                        
                        # Dessiner récursivement
                        draw_scene_recursive(ref_scene, child_x, child_y, level + 1)
        
        # Dessiner à partir des racines
        x_pos = x_start
        for i, root_scene in enumerate(root_scenes):
            draw_scene_recursive(root_scene, x_pos, y_pos)
            x_pos += scene_width + 100
        
        # Si pas de racines, dessiner toutes les scènes
        if not root_scenes:
            x_pos = x_start
            for i, scene in enumerate(scenes[:5]):  # Limiter à 5 pour éviter le surchargement
                self._draw_scene_box(
                    scene, x_pos, y_pos, scene_width, scene_height,
                    is_current=(scene.id == self.current_scene_id)
                )
                x_pos += scene_width + 30
    
    def _draw_scene_box(self, scene: Scene, x: float, y: float, width: float, height: float, is_current: bool = False):
        """Dessine une boîte représentant une scène"""
        # Couleur selon si c'est la scène actuelle
        if is_current:
            color = QColor(70, 130, 180)  # Bleu
            border_color = QColor(30, 100, 150)
            text_color = QColor(255, 255, 255)
            info_color = QColor(220, 220, 220)
        else:
            color = QColor(200, 200, 200)  # Gris
            border_color = QColor(150, 150, 150)
            text_color = QColor(0, 0, 0)
            info_color = QColor(50, 50, 50)
        
        # Rectangle
        rect = self.graphics_scene.addRect(
            x, y, width, height,
            QPen(border_color, 2),
            QBrush(color)
        )
        rect.setData(0, scene.id)  # Stocker l'ID pour la sélection
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Titre (tronqué si trop long)
        title = scene.title[:20] + "..." if len(scene.title) > 20 else scene.title
        title_text = self.graphics_scene.addText(title, QFont("Arial", 10, QFont.Weight.Bold))
        title_text.setPos(x + 5, y + 5)
        title_text.setDefaultTextColor(text_color)
        
        # Informations supplémentaires
        info = f"PJ: {len(scene.player_characters)} | PNJ: {len(scene.npcs)}"
        info_text = self.graphics_scene.addText(info, QFont("Arial", 8))
        info_text.setPos(x + 5, y + 25)
        info_text.setDefaultTextColor(info_color)
    
    def _on_selection_changed(self):
        """Gère le changement de sélection dans la scène graphique"""
        selected_items = self.graphics_scene.selectedItems()
        if selected_items:
            item = selected_items[0]
            scene_id = item.data(0)
            if scene_id:
                self.scene_selected.emit(scene_id)
    
    def resizeEvent(self, event):
        """Ajuste la vue lors du redimensionnement"""
        super().resizeEvent(event)
        if self.graphics_scene:
            self.graphics_view.fitInView(
                self.graphics_scene.itemsBoundingRect(),
                Qt.AspectRatioMode.KeepAspectRatio
            )

