"""
Exporteur Markdown
"""

from pathlib import Path
from typing import List

from ..models.character import Character
from ..models.scene import Scene
from ..models.session import Session


class MarkdownExporter:
    """Exporteur Markdown"""
    
    @staticmethod
    def export_character(character: Character, output_path: Path) -> bool:
        """Exporte un personnage en Markdown"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {character.name}\n\n")
                f.write(f"**Type:** {character.type.value}\n\n")
                
                # Profil
                f.write("## Profil\n\n")
                f.write(f"- **Niveau:** {character.profile.level}\n")
                f.write(f"- **Race:** {character.profile.race or '-'}\n")
                f.write(f"- **Classe:** {character.profile.character_class or '-'}\n")
                f.write(f"- **Sexe:** {character.profile.gender or '-'}\n")
                f.write(f"- **Âge:** {character.profile.age or '-'}\n")
                f.write(f"- **Taille:** {character.profile.height or '-'}\n")
                f.write(f"- **Poids:** {character.profile.weight or '-'}\n\n")
                
                # Caractéristiques
                f.write("## Caractéristiques\n\n")
                f.write("| Caractéristique | Valeur | Modificateur |\n")
                f.write("|----------------|--------|-------------|\n")
                f.write(f"| FOR (Force) | {character.characteristics.strength.value} | {character.characteristics.strength.modifier:+d} |\n")
                f.write(f"| DEX (Dextérité) | {character.characteristics.dexterity.value} | {character.characteristics.dexterity.modifier:+d} |\n")
                f.write(f"| CON (Condition) | {character.characteristics.constitution.value} | {character.characteristics.constitution.modifier:+d} |\n")
                f.write(f"| INT (Intelligence) | {character.characteristics.intelligence.value} | {character.characteristics.intelligence.modifier:+d} |\n")
                f.write(f"| SAG (Sagesse) | {character.characteristics.wisdom.value} | {character.characteristics.wisdom.modifier:+d} |\n")
                f.write(f"| CHA (Charisme) | {character.characteristics.charisma.value} | {character.characteristics.charisma.modifier:+d} |\n\n")
                
                # Combat
                f.write("## Combat\n\n")
                f.write(f"- **Attaque au contact:** {character.combat.melee_attack or 'FOR+NIV'}\n")
                f.write(f"- **Attaque à distance:** {character.combat.ranged_attack or 'DEX+NIV'}\n")
                f.write(f"- **Attaque magique:** {character.combat.magic_attack or 'NIV'}\n")
                f.write(f"- **Initiative:** {character.combat.initiative or 'DEX'}\n")
                f.write(f"- **DV:** {character.combat.life_dice or '-'}\n")
                f.write(f"- **PV:** {character.combat.life_points}\n")
                f.write(f"- **PV restants:** {character.combat.current_life_points}\n\n")
                
                # Défense
                f.write("## Défense\n\n")
                f.write(f"- **Base:** {character.defense.base}\n")
                f.write(f"- **Armure:** {character.defense.armor}\n")
                f.write(f"- **Bouclier:** {character.defense.shield}\n")
                f.write(f"- **DEX:** {character.defense.dexterity}\n")
                f.write(f"- **Divers:** {character.defense.misc}\n")
                f.write(f"- **Total:** {character.defense.calculate_total()}\n\n")
                
                # Armes
                if character.weapons:
                    f.write("## Armes\n\n")
                    for weapon in character.weapons:
                        f.write(f"### {weapon.name}\n\n")
                        f.write(f"- **Attaque:** {weapon.attack}\n")
                        f.write(f"- **Dégâts:** {weapon.damage}\n")
                        if weapon.special:
                            f.write(f"- **Spécial:** {weapon.special}\n")
                        f.write("\n")
                
                # Équipement
                if character.equipment:
                    f.write("## Équipement\n\n")
                    for item in character.equipment:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                # Notes
                if character.notes:
                    f.write("## Notes\n\n")
                    f.write(character.notes + "\n")
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'export Markdown: {e}")
            return False
    
    @staticmethod
    def export_scene(scene: Scene, output_path: Path) -> bool:
        """Exporte une scène en Markdown"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {scene.title}\n\n")
                f.write(f"{scene.description or 'Aucune description'}\n\n")
                if scene.notes:
                    f.write("## Notes\n\n")
                    f.write(scene.notes + "\n")
            return True
        except Exception as e:
            print(f"Erreur lors de l'export Markdown: {e}")
            return False
    
    @staticmethod
    def export_session(session: Session, output_path: Path) -> bool:
        """Exporte une session en Markdown"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {session.title}\n\n")
                f.write(f"**Date:** {session.date.strftime('%d/%m/%Y') if session.date else '-'}\n\n")
                f.write("## Scènes\n\n")
                for scene_id in session.scene_ids:
                    f.write(f"- {scene_id}\n")
                f.write(f"\n## Notes post-session\n\n{session.post_session_notes or '-'}\n")
            return True
        except Exception as e:
            print(f"Erreur lors de l'export Markdown: {e}")
            return False

