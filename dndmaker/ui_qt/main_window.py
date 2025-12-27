"""
Fenêtre principale de l'application Qt
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget, QTabWidget,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from pathlib import Path
from typing import Optional

from ..services.project_service import ProjectService
from ..core.config import Config
from ..core.logger import get_logger
from ..core.i18n import Translator, Language, tr

logger = get_logger()


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    # Signal pour notifier le changement de langue
    language_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.project_service = ProjectService()
        self.config = Config()
        
        # Charger la langue depuis la config
        lang_code = self.config.get_language()
        if lang_code == 'en':
            Translator.set_language(Language.ENGLISH)
        else:
            Translator.set_language(Language.FRENCH)
        
        self._init_ui()
        self._apply_dark_theme()
        self._load_last_project()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        self._update_window_title()
        self.setMinimumSize(1200, 800)
        
        # Menu bar
        self._create_menu_bar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation latérale
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(200)
        self._update_navigation()
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        
        # Zone de contenu (onglets)
        self.content_stack = QStackedWidget()
        
        # Créer les vues
        from .views.project_view import ProjectView
        from .views.sessions_view import SessionsView
        from .views.scenes_view import ScenesView
        from .views.characters_view import CharactersView
        from .views.banks_view import BanksView
        from .views.exports_view import ExportsView
        
        self.project_view = ProjectView(self.project_service, self)
        # Connecter les signaux de ProjectView aux méthodes de MainWindow
        self.project_view.new_project_requested.connect(self._new_project)
        self.project_view.open_project_requested.connect(self._open_project)
        self.project_view.import_project_requested.connect(self._import_project)
        # Connecter le signal de changement de langue
        self.language_changed.connect(self.project_view.on_language_changed)
        
        self.sessions_view = SessionsView(self.project_service, self)
        self.language_changed.connect(self.sessions_view.on_language_changed)
        
        self.scenes_view = ScenesView(self.project_service, self)
        self.language_changed.connect(self.scenes_view.on_language_changed)
        
        self.characters_view_pj = CharactersView(self.project_service, self)
        self.language_changed.connect(self.characters_view_pj.on_language_changed)
        
        # Créer une instance séparée pour PNJ/Créatures (même vue mais instance différente)
        self.characters_view_npc = CharactersView(self.project_service, self)
        self.language_changed.connect(self.characters_view_npc.on_language_changed)
        
        self.banks_view = BanksView(self.project_service, self)
        self.language_changed.connect(self.banks_view.on_language_changed)
        
        self.exports_view = ExportsView(self.project_service, self)
        self.language_changed.connect(self.exports_view.on_language_changed)
        
        self.content_stack.addWidget(self.project_view)           # Index 0: Projet
        self.content_stack.addWidget(self.sessions_view)          # Index 1: Sessions
        self.content_stack.addWidget(self.scenes_view)            # Index 2: Scènes
        self.content_stack.addWidget(self.characters_view_pj)     # Index 3: PJ
        self.content_stack.addWidget(self.characters_view_npc)    # Index 4: PNJ / Créatures
        self.content_stack.addWidget(self.banks_view)             # Index 5: Banques
        self.content_stack.addWidget(self.exports_view)           # Index 6: Exports
        
        # Ajouter au layout
        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Status bar
        self._update_status_bar()
        
        # Sélectionner la vue Projet par défaut
        self.nav_list.setCurrentRow(0)
        
        # Connecter le signal de changement de langue
        self.language_changed.connect(self._on_language_changed)
    
    def _create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        self.file_menu = menubar.addMenu(tr("campaign.title"))
        self._update_file_menu()
        
        # Menu Édition
        self.edit_menu = menubar.addMenu(tr("menu.edit"))
        
        # Menu Aide
        self.help_menu = menubar.addMenu(tr("menu.help"))
        self.about_action = QAction(tr("msg.about"), self)
        self.about_action.triggered.connect(self._show_about)
        self.help_menu.addAction(self.about_action)
        
        # Bouton de changement de langue (en haut à droite)
        lang_button = QPushButton()
        lang_button.setMaximumWidth(100)
        lang_button.setMinimumHeight(30)
        self._update_language_button(lang_button)
        lang_button.clicked.connect(self._toggle_language)
        
        # Ajouter le bouton dans la barre de menu (en haut à droite)
        menubar.setCornerWidget(lang_button, Qt.Corner.TopRightCorner)
        self.language_button = lang_button
    
    def _on_nav_changed(self, index: int):
        """Gère le changement de navigation"""
        self.content_stack.setCurrentIndex(index)
        self._update_status()
    
    def _new_project(self):
        """Crée un nouveau projet"""
        from PyQt6.QtWidgets import QInputDialog
        
        if Translator.get_language() == Language.ENGLISH:
            title = "New Campaign"
            label = "Campaign name:"
            dir_dialog_title = "Choose where to save the campaign"
            default_dir = str(Path.home() / "Documents" / "DNDMaker")
        else:
            title = "Nouvelle campagne"
            label = "Nom de la campagne:"
            dir_dialog_title = "Choisir où sauvegarder la campagne"
            default_dir = str(Path.home() / "Documents" / "DNDMaker")
        
        # Demander le nom de la campagne
        name, ok = QInputDialog.getText(
            self,
            title,
            label
        )
        if not ok or not name:
            return
        
        # Demander où sauvegarder la campagne
        project_dir_str = QFileDialog.getExistingDirectory(
            self,
            dir_dialog_title,
            default_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not project_dir_str:
            # L'utilisateur a annulé
            return
        
        project_dir = Path(project_dir_str)
        
        try:
            project = self.project_service.create_project(name, project_dir)
            # Sauvegarder le dernier projet ouvert
            self.config.set_last_project(self.project_service.project_path)
            if Translator.get_language() == Language.ENGLISH:
                self.statusBar().showMessage(f"Campaign '{name}' created successfully")
            else:
                self.statusBar().showMessage(f"Campagne '{name}' créée avec succès")
            self._refresh_all_views()
        except Exception as e:
            if Translator.get_language() == Language.ENGLISH:
                QMessageBox.critical(self, "Error", f"Could not create campaign: {str(e)}")
            else:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer la campagne: {str(e)}")
    
    def _import_project(self, json_path: str):
        """Importe un projet depuis un fichier JSON"""
        from pathlib import Path
        
        logger.log_ui_action("Import de projet demandé", json_path=json_path)
        
        try:
            json_file = Path(json_path)
            if not json_file.exists():
                QMessageBox.warning(self, "Erreur", f"Le fichier JSON n'existe pas:\n{json_path}")
                return
            
            # Demander où créer le nouveau projet
            project_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le répertoire où créer le projet importé",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            if not project_dir:
                logger.log_ui_action("Import annulé par l'utilisateur")
                return
            
            project_dir = Path(project_dir)
            
            # Importer le projet
            project = self.project_service.import_project_from_json(json_file, project_dir)
            
            if project:
                # Sauvegarder le dernier projet ouvert
                self.config.set_last_project(self.project_service.project_path)
                logger.log_project_action("Importé avec succès", project_name=project.name)
                self.statusBar().showMessage(f"Projet '{project.name}' importé avec succès")
                self._refresh_all_views()
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Le projet '{project.name}' a été importé avec succès dans:\n{self.project_service.project_path}"
                )
            else:
                logger.warning(f"Impossible d'importer le projet depuis: {json_path}")
                QMessageBox.warning(
                    self,
                    "Erreur",
                    f"Impossible d'importer le projet depuis:\n{json_path}\n\n"
                    f"Vérifiez que le fichier JSON est valide et contient toutes les données nécessaires."
                )
        except Exception as e:
            logger.exception(f"Exception lors de l'import du projet: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'import:\n{str(e)}\n\nVoir la console pour plus de détails."
            )
    
    def _open_project(self, project_path: Optional[Path] = None):
        """Ouvre un projet existant"""
        logger.log_ui_action("Ouverture de projet demandée")
        
        # Si un chemin est fourni directement (ex: depuis _load_last_project), l'utiliser
        if project_path is not None and isinstance(project_path, Path):
            logger.debug(f"Ouverture directe du projet: {project_path}")
        else:
            # Sinon, ouvrir le dialogue de sélection
            # Déterminer le répertoire de départ
            start_dir = None
            last_project = self.config.get_last_project()
            if last_project and last_project.parent.exists():
                start_dir = last_project.parent
            else:
                try:
                    start_dir = Path.home() / "Documents" / "DNDMaker"
                    if not start_dir.exists():
                        start_dir = Path.home() / "Documents"
                except (OSError, TypeError, AttributeError):
                    start_dir = Path.cwd()
            
            # Ouvrir l'explorateur de fichiers standard
            if Translator.get_language() == Language.ENGLISH:
                dialog_title = "Open a Campaign - Select the campaign folder"
            else:
                dialog_title = "Ouvrir une campagne - Sélectionnez le dossier de la campagne"
            
            project_path_str = QFileDialog.getExistingDirectory(
                self,
                dialog_title,
                str(start_dir) if start_dir else "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            # Vérifier que l'utilisateur n'a pas annulé
            # QFileDialog.getExistingDirectory retourne une chaîne vide "" si annulé
            if not project_path_str or project_path_str == "":
                logger.log_ui_action("Dialogue d'ouverture annulé")
                return
            
            # Convertir en Path
            try:
                project_path = Path(str(project_path_str))
            except (TypeError, ValueError) as e:
                logger.exception(f"Erreur de conversion du chemin: {e}")
                QMessageBox.warning(self, "Erreur", f"Chemin invalide:\n{project_path_str}")
                return
        
        # Vérifier que le chemin existe et est un répertoire
        if not project_path or not isinstance(project_path, Path):
            logger.error(f"project_path invalide: {project_path} (type: {type(project_path)})")
            return
            
        if not project_path.exists():
            logger.warning(f"Le chemin sélectionné n'existe pas: {project_path}")
            QMessageBox.warning(self, "Erreur", f"Le répertoire sélectionné n'existe pas:\n{project_path}")
            return
        
        if not project_path.is_dir():
            logger.warning(f"Le chemin sélectionné n'est pas un répertoire: {project_path}")
            QMessageBox.warning(self, "Erreur", f"Le chemin sélectionné n'est pas un répertoire:\n{project_path}")
            return
        
        try:
            logger.log_project_action("Chargement", project_path=str(project_path))
            project = self.project_service.load_project(project_path)
            if project:
                # Sauvegarder le dernier projet ouvert
                self.config.set_last_project(project_path)
                logger.log_project_action("Chargé avec succès", project_name=project.name, 
                                        version=project.version)
                self.statusBar().showMessage(f"Projet '{project.name}' chargé")
                self._refresh_all_views()
            else:
                logger.warning(f"Impossible de charger le projet depuis: {project_path}")
                if Translator.get_language() == Language.ENGLISH:
                    error_msg = (
                        f"Unable to load campaign from:\n{project_path}\n\n"
                        f"Please verify that:\n"
                        f"- The directory exists\n"
                        f"- The project.json file is present\n"
                        f"- The project.json file is valid"
                    )
                else:
                    error_msg = (
                        f"Impossible de charger la campagne depuis:\n{project_path}\n\n"
                        f"Vérifiez que:\n"
                        f"- Le répertoire existe\n"
                        f"- Le fichier project.json est présent\n"
                        f"- Le fichier project.json est valide"
                    )
                QMessageBox.warning(self, "Erreur", error_msg)
        except Exception as e:
            logger.exception(f"Exception lors du chargement du projet: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement:\n{str(e)}\n\nVoir la console pour plus de détails."
            )
    
    def _save_project(self):
        """Sauvegarde le projet actuel"""
        logger.log_ui_action("Sauvegarde demandée")
        try:
            project = self.project_service.get_current_project()
            if project:
                logger.log_project_action("Sauvegarde", project_name=project.name)
            self.project_service.save_project()
            # Mettre à jour le dernier projet si nécessaire
            if self.project_service.project_path:
                self.config.set_last_project(self.project_service.project_path)
            logger.log_project_action("Sauvegardé avec succès", 
                                    project_name=project.name if project else None)
            self.statusBar().showMessage("Projet sauvegardé")
        except ValueError as e:
            logger.exception(f"Erreur lors de la sauvegarde: {e}")
            QMessageBox.warning(self, "Erreur", str(e))
    
    def _load_last_project(self):
        """Charge automatiquement le dernier projet ouvert"""
        last_project = self.config.get_last_project()
        if last_project:
            try:
                # S'assurer que last_project est un Path
                if not isinstance(last_project, Path):
                    last_project = Path(str(last_project))
                
                project = self.project_service.load_project(last_project)
                if project:
                    self.statusBar().showMessage(f"Projet '{project.name}' chargé automatiquement")
                    self._refresh_all_views()
            except Exception as e:
                # En cas d'erreur, on ignore silencieusement
                # L'utilisateur pourra ouvrir un projet manuellement
                pass
    
    def _refresh_all_views(self):
        """Rafraîchit toutes les vues"""
        self.project_view.refresh()
        self.sessions_view.refresh()
        self.scenes_view.refresh()
        self.characters_view_pj.refresh()
        self.characters_view_npc.refresh()
        self.banks_view.refresh()
        self.banks_view.refresh()
        self.exports_view.refresh()
    
    def _update_status(self):
        """Met à jour la barre de statut"""
        project = self.project_service.get_current_project()
        if project:
            self.statusBar().showMessage(
                f"Projet: {project.name} | Version: {project.version}"
            )
        else:
            self.statusBar().showMessage("Aucun projet ouvert")
    
    def _show_about(self):
        """Affiche la boîte À propos"""
        if Translator.get_language() == Language.ENGLISH:
            title = "About DNDMaker"
            text = "DNDMaker v0.1.0\n\nCampaign management application\nChroniques Oubliées\n\nDeveloped with Python and PyQt6"
        else:
            title = "À propos de DNDMaker"
            text = "DNDMaker v0.1.0\n\nApplication de gestion de campagne\nChroniques Oubliées\n\nDéveloppé avec Python et PyQt6"
        
        QMessageBox.about(self, title, text)
    
    def _toggle_language(self):
        """Change la langue de l'interface"""
        current_lang = Translator.get_language()
        if current_lang == Language.FRENCH:
            new_lang = Language.ENGLISH
            lang_code = 'en'
        else:
            new_lang = Language.FRENCH
            lang_code = 'fr'
        
        Translator.set_language(new_lang)
        self.config.set_language(lang_code)
        
        # Émettre le signal pour mettre à jour toutes les vues
        self.language_changed.emit()
        
        # Mettre à jour l'interface de la fenêtre principale
        self._update_ui_texts()
    
    def _update_language_button(self, button: QPushButton):
        """Met à jour le texte du bouton de langue"""
        current_lang = Translator.get_language()
        if current_lang == Language.FRENCH:
            button.setText("🇫🇷 FR")
            button.setToolTip(tr("lang.change"))
        else:
            button.setText("🇬🇧 EN")
            button.setToolTip(tr("lang.change"))
    
    def _update_window_title(self):
        """Met à jour le titre de la fenêtre"""
        if Translator.get_language() == Language.ENGLISH:
            self.setWindowTitle("DNDMaker - Chroniques Oubliées Campaign Manager")
        else:
            self.setWindowTitle("DNDMaker - Gestionnaire de campagne Chroniques Oubliées")
    
    def _update_navigation(self):
        """Met à jour les éléments de navigation"""
        self.nav_list.clear()
        self.nav_list.addItems([
            tr("nav.campaign"),
            tr("nav.sessions"),
            tr("nav.scenes"),
            tr("nav.characters"),
            tr("nav.npcs"),
            tr("nav.banks"),
            tr("nav.exports")
        ])
    
    def _update_file_menu(self):
        """Met à jour le menu Fichier"""
        if not hasattr(self, 'file_menu'):
            return
        
        self.file_menu.clear()
        
        new_action = QAction(tr("campaign.new"), self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_project)
        self.file_menu.addAction(new_action)
        
        open_action = QAction(tr("campaign.open"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_project)
        self.file_menu.addAction(open_action)
        
        import_action = QAction(tr("campaign.import"), self)
        import_action.triggered.connect(lambda: self._import_project(""))
        self.file_menu.addAction(import_action)
        
        self.file_menu.addSeparator()
        
        save_action = QAction(tr("btn.save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_project)
        self.file_menu.addAction(save_action)
        
        self.file_menu.addSeparator()
        
        if Translator.get_language() == Language.ENGLISH:
            exit_text = "Quit"
        else:
            exit_text = "Quitter"
        
        exit_action = QAction(exit_text, self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
    
    def _update_status_bar(self):
        """Met à jour la barre de statut"""
        project = self.project_service.get_current_project()
        if project:
            if Translator.get_language() == Language.ENGLISH:
                self.statusBar().showMessage(f"Project: {project.name} | Version: {project.version}")
            else:
                self.statusBar().showMessage(f"Projet: {project.name} | Version: {project.version}")
        else:
            if Translator.get_language() == Language.ENGLISH:
                self.statusBar().showMessage("No project open")
            else:
                self.statusBar().showMessage("Aucun projet ouvert")
    
    def _update_ui_texts(self):
        """Met à jour tous les textes de l'interface"""
        self._update_window_title()
        self._update_navigation()
        self._update_file_menu()
        self._update_menu_bar()
        self._update_status_bar()
        if hasattr(self, 'language_button'):
            self._update_language_button(self.language_button)
        
        # Rafraîchir toutes les vues
        self._refresh_all_views()
    
    def _update_menu_bar(self):
        """Met à jour les menus de la barre de menu"""
        if hasattr(self, 'file_menu'):
            self.file_menu.setTitle(tr("campaign.title"))
        if hasattr(self, 'edit_menu'):
            self.edit_menu.setTitle(tr("menu.edit"))
        if hasattr(self, 'help_menu'):
            self.help_menu.setTitle(tr("menu.help"))
        if hasattr(self, 'about_action'):
            self.about_action.setText(tr("msg.about"))
    
    def _on_language_changed(self):
        """Gère le changement de langue"""
        self._update_ui_texts()
    
    def _apply_dark_theme(self):
        """Applique le thème sombre"""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QTabWidget::pane {
                background-color: #2b2b2b;
                border: 1px solid #555555;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 20px;
                border: 1px solid #555555;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QLineEdit, QTextEdit, QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #3c3c3c;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c !important;
                color: #ffffff !important;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 5px;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #555555;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QComboBox::item {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QComboBox::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        # Appliquer aussi à la fenêtre principale pour les widgets enfants
        self.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #3c3c3c;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c !important;
                color: #ffffff !important;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 5px;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #555555;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
        """)
        # Appliquer aussi à la fenêtre principale pour les widgets enfants
        self.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #3c3c3c;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c !important;
                color: #ffffff !important;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 5px;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #555555;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
        """)
    
    def _show_about(self):
        """Affiche la boîte de dialogue À propos"""
        QMessageBox.about(
            self,
            tr("msg.about_title"),
            tr("msg.about_text")
        )

