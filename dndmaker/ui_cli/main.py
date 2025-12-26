"""
Point d'entrée de l'interface CLI
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..services.project_service import ProjectService
from ..core.logger import get_logger

logger = get_logger()


class CLI:
    """Interface CLI principale"""
    
    def __init__(self):
        self.project_service = ProjectService()
        self.current_project_loaded = False
    
    def run(self):
        """Lance l'interface CLI"""
        parser = argparse.ArgumentParser(
            description="DNDMaker - Gestionnaire de campagne Chroniques Oubliées",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemples:
  dndmaker-cli project create --name "Ma Campagne"
  dndmaker-cli project open --path ./MaCampagne.dndmaker
  dndmaker-cli character list --type PJ
  dndmaker-cli scene create --title "La Taverne"
  dndmaker-cli export character --name "Aragorn" --format PDF
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
        
        # Commande project
        self._add_project_commands(subparsers)
        
        # Commande character
        self._add_character_commands(subparsers)
        
        # Commande scene
        self._add_scene_commands(subparsers)
        
        # Commande session
        self._add_session_commands(subparsers)
        
        # Commande bank
        self._add_bank_commands(subparsers)
        
        # Commande export
        self._add_export_commands(subparsers)
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        try:
            # Exécuter la commande
            if hasattr(args, 'func'):
                args.func(args)
            else:
                parser.print_help()
        except Exception as e:
            print(f"❌ Erreur: {e}", file=sys.stderr)
            logger.exception(f"Erreur CLI: {e}")
            sys.exit(1)
    
    def _check_project_loaded(self) -> bool:
        """Vérifie qu'un projet est chargé"""
        if not self.current_project_loaded or not self.project_service.get_current_project():
            print("❌ Aucun projet ouvert. Utilisez 'project open' ou 'project create' d'abord.")
            return False
        return True
    
    def _add_project_commands(self, subparsers):
        """Ajoute les commandes de gestion de projet"""
        project_parser = subparsers.add_parser('project', help='Gestion de projet')
        project_subparsers = project_parser.add_subparsers(dest='project_command', help='Commandes projet')
        
        # create
        create_parser = project_subparsers.add_parser('create', help='Créer un nouveau projet')
        create_parser.add_argument('--name', required=True, help='Nom du projet')
        create_parser.add_argument('--dir', type=Path, default=Path.home() / "Documents" / "DNDMaker",
                                 help='Répertoire où créer le projet')
        create_parser.set_defaults(func=self._cmd_project_create)
        
        # open
        open_parser = project_subparsers.add_parser('open', help='Ouvrir un projet existant')
        open_parser.add_argument('--path', type=Path, required=True, help='Chemin vers le projet (.dndmaker)')
        open_parser.set_defaults(func=self._cmd_project_open)
        
        # list
        list_parser = project_subparsers.add_parser('list', help='Lister les projets disponibles')
        list_parser.add_argument('--dir', type=Path, default=Path.home() / "Documents" / "DNDMaker",
                               help='Répertoire à scanner')
        list_parser.set_defaults(func=self._cmd_project_list)
        
        # info
        info_parser = project_subparsers.add_parser('info', help='Afficher les informations du projet actuel')
        info_parser.set_defaults(func=self._cmd_project_info)
        
        # import
        import_parser = project_subparsers.add_parser('import', help='Importer un projet depuis un JSON')
        import_parser.add_argument('--json', type=Path, required=True, help='Chemin vers le fichier JSON')
        import_parser.add_argument('--dir', type=Path, default=Path.home() / "Documents" / "DNDMaker",
                                  help='Répertoire où créer le projet importé')
        import_parser.set_defaults(func=self._cmd_project_import)
    
    def _add_character_commands(self, subparsers):
        """Ajoute les commandes de gestion de personnages"""
        char_parser = subparsers.add_parser('character', aliases=['char'], help='Gestion des personnages')
        char_subparsers = char_parser.add_subparsers(dest='char_command', help='Commandes personnage')
        
        # list
        list_parser = char_subparsers.add_parser('list', help='Lister les personnages')
        list_parser.add_argument('--type', choices=['PJ', 'PNJ', 'CREATURE'], help='Filtrer par type')
        list_parser.set_defaults(func=self._cmd_character_list)
        
        # show
        show_parser = char_subparsers.add_parser('show', help='Afficher les détails d\'un personnage')
        show_parser.add_argument('--name', required=True, help='Nom du personnage')
        show_parser.set_defaults(func=self._cmd_character_show)
        
        # create
        create_parser = char_subparsers.add_parser('create', help='Créer un personnage')
        create_parser.add_argument('--name', required=True, help='Nom du personnage')
        create_parser.add_argument('--type', choices=['PJ', 'PNJ', 'CREATURE'], required=True, help='Type')
        create_parser.add_argument('--level', type=int, default=1, help='Niveau')
        create_parser.add_argument('--race', help='Race')
        create_parser.add_argument('--class', dest='character_class', help='Classe')
        create_parser.set_defaults(func=self._cmd_character_create)
        
        # delete
        delete_parser = char_subparsers.add_parser('delete', help='Supprimer un personnage')
        delete_parser.add_argument('--name', required=True, help='Nom du personnage')
        delete_parser.set_defaults(func=self._cmd_character_delete)
    
    def _add_scene_commands(self, subparsers):
        """Ajoute les commandes de gestion de scènes"""
        scene_parser = subparsers.add_parser('scene', help='Gestion des scènes')
        scene_subparsers = scene_parser.add_subparsers(dest='scene_command', help='Commandes scène')
        
        # list
        list_parser = scene_subparsers.add_parser('list', help='Lister les scènes')
        list_parser.set_defaults(func=self._cmd_scene_list)
        
        # show
        show_parser = scene_subparsers.add_parser('show', help='Afficher les détails d\'une scène')
        show_parser.add_argument('--title', required=True, help='Titre de la scène')
        show_parser.set_defaults(func=self._cmd_scene_show)
        
        # create
        create_parser = scene_subparsers.add_parser('create', help='Créer une scène')
        create_parser.add_argument('--title', required=True, help='Titre de la scène')
        create_parser.add_argument('--description', help='Description')
        create_parser.set_defaults(func=self._cmd_scene_create)
        
        # delete
        delete_parser = scene_subparsers.add_parser('delete', help='Supprimer une scène')
        delete_parser.add_argument('--title', required=True, help='Titre de la scène')
        delete_parser.set_defaults(func=self._cmd_scene_delete)
    
    def _add_session_commands(self, subparsers):
        """Ajoute les commandes de gestion de sessions"""
        session_parser = subparsers.add_parser('session', help='Gestion des sessions')
        session_subparsers = session_parser.add_subparsers(dest='session_command', help='Commandes session')
        
        # list
        list_parser = session_subparsers.add_parser('list', help='Lister les sessions')
        list_parser.set_defaults(func=self._cmd_session_list)
        
        # show
        show_parser = session_subparsers.add_parser('show', help='Afficher les détails d\'une session')
        show_parser.add_argument('--title', required=True, help='Titre de la session')
        show_parser.set_defaults(func=self._cmd_session_show)
        
        # create
        create_parser = session_subparsers.add_parser('create', help='Créer une session')
        create_parser.add_argument('--title', required=True, help='Titre de la session')
        create_parser.add_argument('--date', help='Date (format: YYYY-MM-DD)')
        create_parser.set_defaults(func=self._cmd_session_create)
        
        # delete
        delete_parser = session_subparsers.add_parser('delete', help='Supprimer une session')
        delete_parser.add_argument('--title', required=True, help='Titre de la session')
        delete_parser.set_defaults(func=self._cmd_session_delete)
    
    def _add_bank_commands(self, subparsers):
        """Ajoute les commandes de gestion des banques"""
        bank_parser = subparsers.add_parser('bank', help='Gestion des banques de données')
        bank_subparsers = bank_parser.add_subparsers(dest='bank_command', help='Commandes banque')
        
        # list
        list_parser = bank_subparsers.add_parser('list', help='Lister les entrées d\'une banque')
        list_parser.add_argument('--type', required=True,
                               choices=['NAMES', 'RACES', 'CLASSES', 'PATHS', 'STAT_TABLES',
                                       'CREATURES', 'PROFESSIONS', 'ARMORS', 'TOOLS', 'TRINKETS', 'WEAPONS'],
                               help='Type de banque')
        list_parser.set_defaults(func=self._cmd_bank_list)
    
    def _add_export_commands(self, subparsers):
        """Ajoute les commandes d'export"""
        export_parser = subparsers.add_parser('export', help='Exporter des données')
        export_subparsers = export_parser.add_subparsers(dest='export_command', help='Commandes export')
        
        # character
        char_parser = export_subparsers.add_parser('character', help='Exporter un personnage')
        char_parser.add_argument('--name', required=True, help='Nom du personnage')
        char_parser.add_argument('--format', choices=['PDF', 'JSON', 'TXT', 'Markdown'], required=True, help='Format')
        char_parser.add_argument('--output', type=Path, help='Fichier de sortie (par défaut: nom_du_personnage.format)')
        char_parser.set_defaults(func=self._cmd_export_character)
        
        # scene
        scene_parser = export_subparsers.add_parser('scene', help='Exporter une scène')
        scene_parser.add_argument('--title', required=True, help='Titre de la scène')
        scene_parser.add_argument('--format', choices=['JSON', 'TXT', 'Markdown'], required=True, help='Format')
        scene_parser.add_argument('--output', type=Path, help='Fichier de sortie')
        scene_parser.set_defaults(func=self._cmd_export_scene)
    
    # Commandes project
    def _cmd_project_create(self, args):
        """Crée un nouveau projet"""
        project = self.project_service.create_project(args.name, args.dir)
        print(f"✅ Projet '{project.name}' créé avec succès")
        print(f"   Chemin: {self.project_service.project_path}")
        self.current_project_loaded = True
    
    def _cmd_project_open(self, args):
        """Ouvre un projet"""
        project = self.project_service.load_project(args.path)
        if project:
            print(f"✅ Projet '{project.name}' ouvert (Version: {project.version})")
            self.current_project_loaded = True
        else:
            print(f"❌ Impossible d'ouvrir le projet: {args.path}")
            sys.exit(1)
    
    def _cmd_project_list(self, args):
        """Liste les projets disponibles"""
        if not args.dir.exists():
            print(f"❌ Le répertoire '{args.dir}' n'existe pas")
            return
        
        projects = [p for p in args.dir.glob("*.dndmaker") if p.is_dir()]
        if projects:
            print(f"\n📁 Projets disponibles dans {args.dir}:")
            print("-" * 60)
            for p in sorted(projects):
                print(f"  • {p.stem}")
            print(f"\nTotal: {len(projects)} projet(s)")
        else:
            print(f"ℹ️  Aucun projet trouvé dans {args.dir}")
    
    def _cmd_project_info(self, args):
        """Affiche les informations du projet"""
        if not self._check_project_loaded():
            return
        
        project = self.project_service.get_current_project()
        print(f"\n📋 Informations du projet:")
        print("-" * 60)
        print(f"  Nom:        {project.name}")
        print(f"  ID:         {project.id}")
        print(f"  Version:    {project.version}")
        print(f"  Créé le:    {project.created_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"  Modifié le: {project.updated_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"  Chemin:     {self.project_service.project_path}")
        
        # Statistiques
        chars = self.project_service.character_service.get_all_characters()
        scenes = self.project_service.scene_service.get_all_scenes()
        sessions = self.project_service.session_service.get_all_sessions()
        
        print(f"\n📊 Statistiques:")
        print(f"  Personnages: {len(chars)}")
        print(f"  Scènes:      {len(scenes)}")
        print(f"  Sessions:     {len(sessions)}")
    
    def _cmd_project_import(self, args):
        """Importe un projet depuis un JSON"""
        project = self.project_service.import_project_from_json(args.json, args.dir)
        if project:
            print(f"✅ Projet '{project.name}' importé avec succès")
            print(f"   Chemin: {self.project_service.project_path}")
            self.current_project_loaded = True
        else:
            print(f"❌ Impossible d'importer le projet depuis: {args.json}")
            sys.exit(1)
    
    # Commandes character
    def _cmd_character_list(self, args):
        """Liste les personnages"""
        if not self._check_project_loaded():
            return
        
        from ..models.character import CharacterType
        
        all_chars = self.project_service.character_service.get_all_characters()
        
        if args.type:
            char_type = CharacterType(args.type)
            chars = [c for c in all_chars if c.type == char_type]
        else:
            chars = all_chars
        
        if chars:
            print(f"\n👥 Personnages ({len(chars)}):")
            print("-" * 80)
            print(f"{'Nom':<30} {'Type':<10} {'Niveau':<8} {'Race':<15} {'Classe':<15}")
            print("-" * 80)
            for char in sorted(chars, key=lambda x: x.name):
                race = char.profile.race or "-"
                char_class = char.profile.character_class or "-"
                print(f"{char.name:<30} {char.type.value:<10} {char.profile.level:<8} {race:<15} {char_class:<15}")
        else:
            print("ℹ️  Aucun personnage trouvé")
    
    def _cmd_character_show(self, args):
        """Affiche les détails d'un personnage"""
        if not self._check_project_loaded():
            return
        
        chars = self.project_service.character_service.get_all_characters()
        char = next((c for c in chars if c.name.lower() == args.name.lower()), None)
        
        if not char:
            print(f"❌ Personnage '{args.name}' introuvable")
            return
        
        print(f"\n👤 {char.name}")
        print("=" * 60)
        print(f"Type:     {char.type.value}")
        print(f"Niveau:   {char.profile.level}")
        print(f"Race:     {char.profile.race or '-'}")
        print(f"Classe:   {char.profile.character_class or '-'}")
        print(f"Sexe:     {char.profile.gender or '-'}")
        print(f"Âge:      {char.profile.age or '-'}")
        
        print(f"\n💪 Caractéristiques:")
        print(f"  FOR: {char.characteristics.strength.value} ({char.characteristics.strength.modifier:+d})")
        print(f"  DEX: {char.characteristics.dexterity.value} ({char.characteristics.dexterity.modifier:+d})")
        print(f"  CON: {char.characteristics.constitution.value} ({char.characteristics.constitution.modifier:+d})")
        print(f"  INT: {char.characteristics.intelligence.value} ({char.characteristics.intelligence.modifier:+d})")
        print(f"  SAG: {char.characteristics.wisdom.value} ({char.characteristics.wisdom.modifier:+d})")
        print(f"  CHA: {char.characteristics.charisma.value} ({char.characteristics.charisma.modifier:+d})")
        
        print(f"\n⚔️  Combat:")
        print(f"  PV:        {char.combat.life_points}")
        print(f"  Défense:   {char.defense.calculate_total()}")
        print(f"  Initiative: {char.combat.initiative or 'DEX'}")
    
    def _cmd_character_create(self, args):
        """Crée un personnage"""
        if not self._check_project_loaded():
            return
        
        from ..models.character import CharacterType
        
        char_type = CharacterType(args.type)
        character = self.project_service.character_service.create_character(
            name=args.name,
            character_type=char_type,
            level=args.level,
            race=args.race or ""
        )
        
        if args.character_class:
            character.profile.character_class = args.character_class
        
        self.project_service.character_service.update_character(character)
        self.project_service.save_project(f"Création du personnage {args.name}")
        
        print(f"✅ Personnage '{args.name}' créé avec succès")
    
    def _cmd_character_delete(self, args):
        """Supprime un personnage"""
        if not self._check_project_loaded():
            return
        
        chars = self.project_service.character_service.get_all_characters()
        char = next((c for c in chars if c.name.lower() == args.name.lower()), None)
        
        if not char:
            print(f"❌ Personnage '{args.name}' introuvable")
            return
        
        if self.project_service.character_service.delete_character(char.id):
            self.project_service.save_project(f"Suppression du personnage {args.name}")
            print(f"✅ Personnage '{args.name}' supprimé")
        else:
            print(f"❌ Erreur lors de la suppression")
    
    # Commandes scene
    def _cmd_scene_list(self, args):
        """Liste les scènes"""
        if not self._check_project_loaded():
            return
        
        scenes = self.project_service.scene_service.get_all_scenes()
        
        if scenes:
            print(f"\n🎬 Scènes ({len(scenes)}):")
            print("-" * 80)
            print(f"{'Titre':<40} {'Créée le':<20} {'Modifiée le':<20}")
            print("-" * 80)
            for scene in sorted(scenes, key=lambda x: x.title):
                created = scene.created_at.strftime('%d/%m/%Y %H:%M')
                updated = scene.updated_at.strftime('%d/%m/%Y %H:%M')
                print(f"{scene.title:<40} {created:<20} {updated:<20}")
        else:
            print("ℹ️  Aucune scène trouvée")
    
    def _cmd_scene_show(self, args):
        """Affiche les détails d'une scène"""
        if not self._check_project_loaded():
            return
        
        scenes = self.project_service.scene_service.get_all_scenes()
        scene = next((s for s in scenes if s.title.lower() == args.title.lower()), None)
        
        if not scene:
            print(f"❌ Scène '{args.title}' introuvable")
            return
        
        print(f"\n🎬 {scene.title}")
        print("=" * 60)
        print(f"Description: {scene.description or '-'}")
        if scene.notes:
            print(f"\nNotes: {scene.notes}")
        print(f"\nCréée le:  {scene.created_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"Modifiée le: {scene.updated_at.strftime('%d/%m/%Y %H:%M')}")
    
    def _cmd_scene_create(self, args):
        """Crée une scène"""
        if not self._check_project_loaded():
            return
        
        scene = self.project_service.scene_service.create_scene(
            title=args.title,
            description=args.description or ""
        )
        self.project_service.save_project(f"Création de la scène {args.title}")
        print(f"✅ Scène '{args.title}' créée avec succès")
    
    def _cmd_scene_delete(self, args):
        """Supprime une scène"""
        if not self._check_project_loaded():
            return
        
        scenes = self.project_service.scene_service.get_all_scenes()
        scene = next((s for s in scenes if s.title.lower() == args.title.lower()), None)
        
        if not scene:
            print(f"❌ Scène '{args.title}' introuvable")
            return
        
        if self.project_service.scene_service.delete_scene(scene.id):
            self.project_service.save_project(f"Suppression de la scène {args.title}")
            print(f"✅ Scène '{args.title}' supprimée")
        else:
            print(f"❌ Erreur lors de la suppression")
    
    # Commandes session
    def _cmd_session_list(self, args):
        """Liste les sessions"""
        if not self._check_project_loaded():
            return
        
        sessions = self.project_service.session_service.get_all_sessions()
        
        if sessions:
            print(f"\n📅 Sessions ({len(sessions)}):")
            print("-" * 80)
            print(f"{'Titre':<40} {'Date':<15} {'Scènes':<10}")
            print("-" * 80)
        for session in sorted(sessions, key=lambda x: x.date if x.date else x.created_at, reverse=True):
            date_str = session.date.strftime('%d/%m/%Y') if session.date else '-'
            scenes_count = len(session.scenes)
            print(f"{session.title:<40} {date_str:<15} {scenes_count:<10}")
        else:
            print("ℹ️  Aucune session trouvée")
    
    def _cmd_session_show(self, args):
        """Affiche les détails d'une session"""
        if not self._check_project_loaded():
            return
        
        sessions = self.project_service.session_service.get_all_sessions()
        session = next((s for s in sessions if s.title.lower() == args.title.lower()), None)
        
        if not session:
            print(f"❌ Session '{args.title}' introuvable")
            return
        
        print(f"\n📅 {session.title}")
        print("=" * 60)
        print(f"Date: {session.date.strftime('%d/%m/%Y') if session.date else '-'}")
        print(f"Scènes: {len(session.scenes)}")
        if session.post_session_notes:
            print(f"\nNotes post-session:\n{session.post_session_notes}")
    
    def _cmd_session_create(self, args):
        """Crée une session"""
        if not self._check_project_loaded():
            return
        
        from datetime import datetime
        
        date = None
        if args.date:
            try:
                date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                print(f"❌ Format de date invalide. Utilisez YYYY-MM-DD")
                return
        
        session = self.project_service.session_service.create_session(
            title=args.title,
            date=date
        )
        self.project_service.save_project(f"Création de la session {args.title}")
        print(f"✅ Session '{args.title}' créée avec succès")
    
    def _cmd_session_delete(self, args):
        """Supprime une session"""
        if not self._check_project_loaded():
            return
        
        sessions = self.project_service.session_service.get_all_sessions()
        session = next((s for s in sessions if s.title.lower() == args.title.lower()), None)
        
        if not session:
            print(f"❌ Session '{args.title}' introuvable")
            return
        
        if self.project_service.session_service.delete_session(session.id):
            self.project_service.save_project(f"Suppression de la session {args.title}")
            print(f"✅ Session '{args.title}' supprimée")
        else:
            print(f"❌ Erreur lors de la suppression")
    
    # Commandes bank
    def _cmd_bank_list(self, args):
        """Liste les entrées d'une banque"""
        if not self._check_project_loaded():
            return
        
        from ..models.bank import BankType
        from ..core.data_loader import DataLoader
        
        # S'assurer que les banques sont initialisées
        DataLoader.initialize_banks(self.project_service.bank_service)
        
        bank_type = BankType(args.type)
        bank = self.project_service.bank_service.get_bank_by_type(bank_type)
        
        if not bank:
            print(f"ℹ️  Banque '{args.type}' vide")
            return
        
        print(f"\n📚 Banque: {bank_type.value} ({len(bank.entries)} entrées)")
        print("-" * 60)
        
        for entry in sorted(bank.entries, key=lambda x: x.value):
            print(f"  • {entry.value}")
    
    # Commandes export
    def _cmd_export_character(self, args):
        """Exporte un personnage"""
        if not self._check_project_loaded():
            return
        
        chars = self.project_service.character_service.get_all_characters()
        char = next((c for c in chars if c.name.lower() == args.name.lower()), None)
        
        if not char:
            print(f"❌ Personnage '{args.name}' introuvable")
            return
        
        # Déterminer le fichier de sortie
        if args.output:
            output_path = args.output
        else:
            safe_name = "".join(c for c in args.name if c.isalnum() or c in (' ', '-', '_')).strip()
            output_path = Path(f"{safe_name}.{args.format.lower()}")
        
        # Exporter
        from ..exporters.pdf_exporter import PDFExporter
        from ..exporters.json_exporter import JSONExporter
        from ..exporters.txt_exporter import TXTExporter
        from ..exporters.markdown_exporter import MarkdownExporter
        
        success = False
        if args.format == "PDF":
            exporter = PDFExporter()
            success = exporter.export_character_sheet(char, output_path)
        elif args.format == "JSON":
            success = JSONExporter.export_character(char, output_path)
        elif args.format == "TXT":
            success = TXTExporter.export_character(char, output_path)
        elif args.format == "Markdown":
            success = MarkdownExporter.export_character(char, output_path)
        
        if success:
            print(f"✅ Personnage '{args.name}' exporté vers: {output_path}")
        else:
            print(f"❌ Erreur lors de l'export")
            sys.exit(1)
    
    def _cmd_export_scene(self, args):
        """Exporte une scène"""
        if not self._check_project_loaded():
            return
        
        scenes = self.project_service.scene_service.get_all_scenes()
        scene = next((s for s in scenes if s.title.lower() == args.title.lower()), None)
        
        if not scene:
            print(f"❌ Scène '{args.title}' introuvable")
            return
        
        # Déterminer le fichier de sortie
        if args.output:
            output_path = args.output
        else:
            safe_name = "".join(c for c in args.title if c.isalnum() or c in (' ', '-', '_')).strip()
            output_path = Path(f"{safe_name}.{args.format.lower()}")
        
        # Exporter
        from ..exporters.json_exporter import JSONExporter
        from ..exporters.txt_exporter import TXTExporter
        from ..exporters.markdown_exporter import MarkdownExporter
        
        success = False
        if args.format == "JSON":
            success = JSONExporter.export_scene(scene, output_path)
        elif args.format == "TXT":
            success = TXTExporter.export_scene(scene, output_path)
        elif args.format == "Markdown":
            success = MarkdownExporter.export_scene(scene, output_path)
        
        if success:
            print(f"✅ Scène '{args.title}' exportée vers: {output_path}")
        else:
            print(f"❌ Erreur lors de l'export")
            sys.exit(1)


def main():
    """Point d'entrée principal"""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
