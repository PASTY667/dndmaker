"""
Exporteur TXT
"""

from pathlib import Path
from typing import List

from ..models.character import Character
from ..models.scene import Scene
from ..models.session import Session


class TXTExporter:
    """Exporteur TXT"""
    
    @staticmethod
    def export_character(character: Character, output_path: Path) -> bool:
        """Exporte un personnage en TXT"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"FICHE DE PERSONNAGE: {character.name}\n")
                f.write("=" * 60 + "\n\n")
                
                # Profil
                f.write("PROFIL\n")
                f.write("-" * 60 + "\n")
                f.write(f"Type: {character.type.value}\n")
                f.write(f"Niveau: {character.profile.level}\n")
                f.write(f"Race: {character.profile.race or '-'}\n")
                f.write(f"Classe: {character.profile.character_class or '-'}\n")
                f.write(f"Sexe: {character.profile.gender or '-'}\n")
                f.write(f"Âge: {character.profile.age or '-'}\n")
                f.write(f"Taille: {character.profile.height or '-'}\n")
                f.write(f"Poids: {character.profile.weight or '-'}\n\n")
                
                # Caractéristiques
                f.write("CARACTÉRISTIQUES\n")
                f.write("-" * 60 + "\n")
                f.write(f"FOR: {character.characteristics.strength.value} ({character.characteristics.strength.modifier:+d})\n")
                f.write(f"DEX: {character.characteristics.dexterity.value} ({character.characteristics.dexterity.modifier:+d})\n")
                f.write(f"CON: {character.characteristics.constitution.value} ({character.characteristics.constitution.modifier:+d})\n")
                f.write(f"INT: {character.characteristics.intelligence.value} ({character.characteristics.intelligence.modifier:+d})\n")
                f.write(f"SAG: {character.characteristics.wisdom.value} ({character.characteristics.wisdom.modifier:+d})\n")
                f.write(f"CHA: {character.characteristics.charisma.value} ({character.characteristics.charisma.modifier:+d})\n\n")
                
                # Combat
                f.write("COMBAT\n")
                f.write("-" * 60 + "\n")
                f.write(f"Attaque au contact: {character.combat.melee_attack or 'FOR+NIV'}\n")
                f.write(f"Attaque à distance: {character.combat.ranged_attack or 'DEX+NIV'}\n")
                f.write(f"Attaque magique: {character.combat.magic_attack or 'NIV'}\n")
                f.write(f"Initiative: {character.combat.initiative or 'DEX'}\n")
                f.write(f"DV: {character.combat.life_dice or '-'}\n")
                f.write(f"PV: {character.combat.life_points}\n")
                f.write(f"PV restants: {character.combat.current_life_points}\n\n")
                
                # Défense
                f.write("DÉFENSE\n")
                f.write("-" * 60 + "\n")
                f.write(f"Base: {character.defense.base}\n")
                f.write(f"Armure: {character.defense.armor}\n")
                f.write(f"Bouclier: {character.defense.shield}\n")
                f.write(f"DEX: {character.defense.dexterity}\n")
                f.write(f"Divers: {character.defense.misc}\n")
                f.write(f"Total: {character.defense.calculate_total()}\n\n")
                
                # Armes
                if character.weapons:
                    f.write("ARMES\n")
                    f.write("-" * 60 + "\n")
                    for weapon in character.weapons:
                        f.write(f"{weapon.name}: {weapon.attack} / {weapon.damage}")
                        if weapon.special:
                            f.write(f" ({weapon.special})")
                        f.write("\n")
                    f.write("\n")
                
                # Équipement
                if character.equipment:
                    f.write("ÉQUIPEMENT\n")
                    f.write("-" * 60 + "\n")
                    for item in character.equipment:
                        f.write(f"• {item}\n")
                    f.write("\n")
                
                # Notes
                if character.notes:
                    f.write("NOTES\n")
                    f.write("-" * 60 + "\n")
                    f.write(character.notes + "\n")
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'export TXT: {e}")
            return False
    
    @staticmethod
    def export_scene(scene: Scene, output_path: Path) -> bool:
        """Exporte une scène en TXT"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"SCÈNE: {scene.title}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Description:\n{scene.description or '-'}\n\n")
                if scene.notes:
                    f.write(f"Notes:\n{scene.notes}\n")
            return True
        except Exception as e:
            print(f"Erreur lors de l'export TXT: {e}")
            return False
    
    @staticmethod
    def export_session(session: Session, output_path: Path) -> bool:
        """Exporte une session en TXT"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"SESSION: {session.title}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Date: {session.date.strftime('%d/%m/%Y') if session.date else '-'}\n\n")
                f.write("Scènes:\n")
                for scene_id in session.scene_ids:
                    f.write(f"• {scene_id}\n")
                f.write(f"\nNotes post-session:\n{session.post_session_notes or '-'}\n")
            return True
        except Exception as e:
            print(f"Erreur lors de l'export TXT: {e}")
            return False

