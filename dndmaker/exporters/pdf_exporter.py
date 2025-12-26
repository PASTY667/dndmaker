"""
Exporteur PDF pour les fiches de personnage Chroniques Oubliées
"""

from pathlib import Path
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from ..models.character import Character, CharacterType


class PDFExporter:
    """Exporteur PDF pour les fiches de personnage"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
    
    def export_character_sheet(self, character: Character, output_path: Path) -> bool:
        """
        Exporte une fiche de personnage au format PDF
        
        Args:
            character: Le personnage à exporter
            output_path: Chemin de sortie du fichier PDF
            
        Returns:
            True si l'export a réussi, False sinon
        """
        try:
            c = canvas.Canvas(str(output_path), pagesize=A4)
            
            # Couleurs
            black = colors.black
            dark_gray = colors.HexColor('#333333')
            
            # Titre
            c.setFont("Helvetica-Bold", 16)
            c.drawString(20*mm, self.page_height - 20*mm, "CHRONIQUES OUBLIÉES")
            c.setFont("Helvetica-Bold", 14)
            c.drawString(20*mm, self.page_height - 30*mm, "Personnage")
            
            # Section Profil
            y_pos = self.page_height - 50*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20*mm, y_pos, "Profil")
            
            y_pos -= 15*mm
            c.setFont("Helvetica", 10)
            profile_data = [
                ("Niveau", str(character.profile.level)),
                ("Race", character.profile.race or ""),
                ("Classe", character.profile.character_class or ""),
                ("Sexe", character.profile.gender or ""),
                ("Âge", str(character.profile.age) if character.profile.age else ""),
                ("Taille", character.profile.height or ""),
                ("Poids", character.profile.weight or ""),
            ]
            
            for label, value in profile_data:
                c.drawString(20*mm, y_pos, f"{label}: {value}")
                y_pos -= 6*mm
            
            # Caractéristiques
            y_pos -= 10*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20*mm, y_pos, "Caractéristiques")
            
            y_pos -= 15*mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(20*mm, y_pos, "CARAC.")
            c.drawString(60*mm, y_pos, "Valeur")
            c.drawString(90*mm, y_pos, "Mod.")
            
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            characteristics = [
                ("FOR", "FORCE", character.characteristics.strength),
                ("DEX", "DEXTERITÉ", character.characteristics.dexterity),
                ("CON", "CONDITION", character.characteristics.constitution),
                ("INT", "INTÉLIGENCE", character.characteristics.intelligence),
                ("SAG", "SAGESSE", character.characteristics.wisdom),
                ("CHA", "CHARISME", character.characteristics.charisma),
            ]
            
            for abbr, full, char_value in characteristics:
                c.drawString(20*mm, y_pos, f"{abbr} {full}")
                c.drawString(60*mm, y_pos, str(char_value.value))
                c.drawString(90*mm, y_pos, f"{char_value.modifier:+d}")
                y_pos -= 6*mm
            
            # Capacité raciale
            y_pos -= 10*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y_pos, "Capacité raciale:")
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            if character.profile.racial_ability:
                # Découper le texte en lignes si trop long
                words = character.profile.racial_ability.split()
                line = ""
                for word in words:
                    if len(line + word) < 80:
                        line += word + " "
                    else:
                        c.drawString(20*mm, y_pos, line.strip())
                        y_pos -= 5*mm
                        line = word + " "
                if line:
                    c.drawString(20*mm, y_pos, line.strip())
                    y_pos -= 5*mm
            
            # Langues connues
            y_pos -= 10*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y_pos, "Langues connues:")
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            if character.profile.known_languages:
                c.drawString(20*mm, y_pos, ", ".join(character.profile.known_languages))
            else:
                c.drawString(20*mm, y_pos, "-")
            
            # Combat
            y_pos = self.page_height - 50*mm
            x_pos = 120*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos, y_pos, "Combat")
            
            y_pos -= 15*mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_pos, y_pos, "COMBAT")
            c.drawString(x_pos + 40*mm, y_pos, "Total")
            c.drawString(x_pos + 70*mm, y_pos, "VITALITÉ")
            
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            combat_data = [
                ("Attaque au contact", character.combat.melee_attack or "FOR+NIV", ""),
                ("Attaque à distance", character.combat.ranged_attack or "DEX+NIV", ""),
                ("Attaque magique", character.combat.magic_attack or "NIV", ""),
                ("Initiative", character.combat.initiative or "DEX", ""),
            ]
            
            for label, value, _ in combat_data:
                c.drawString(x_pos, y_pos, label)
                c.drawString(x_pos + 40*mm, y_pos, value)
                y_pos -= 6*mm
            
            y_pos -= 5*mm
            c.drawString(x_pos, y_pos, "DV (Dé de vie):")
            c.drawString(x_pos + 40*mm, y_pos, character.combat.life_dice or "")
            y_pos -= 6*mm
            c.drawString(x_pos, y_pos, "PV (Points de vie):")
            c.drawString(x_pos + 40*mm, y_pos, str(character.combat.life_points))
            y_pos -= 6*mm
            c.drawString(x_pos, y_pos, "PV restants:")
            c.drawString(x_pos + 40*mm, y_pos, str(character.combat.current_life_points))
            y_pos -= 6*mm
            c.drawString(x_pos, y_pos, "DM temporaire:")
            c.drawString(x_pos + 40*mm, y_pos, str(character.combat.temporary_damage))
            
            # Défense
            y_pos -= 20*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos, y_pos, "Défense")
            
            y_pos -= 15*mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_pos, y_pos, "DÉFENSE")
            c.drawString(x_pos + 30*mm, y_pos, "10+")
            c.drawString(x_pos + 45*mm, y_pos, "ARMURE")
            c.drawString(x_pos + 70*mm, y_pos, "BOUCLIER")
            c.drawString(x_pos + 95*mm, y_pos, "DEX")
            c.drawString(x_pos + 110*mm, y_pos, "DIVERS")
            
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            c.drawString(x_pos, y_pos, "Total")
            c.drawString(x_pos + 30*mm, y_pos, str(character.defense.base))
            c.drawString(x_pos + 45*mm, y_pos, str(character.defense.armor))
            c.drawString(x_pos + 70*mm, y_pos, str(character.defense.shield))
            c.drawString(x_pos + 95*mm, y_pos, str(character.defense.dexterity))
            c.drawString(x_pos + 110*mm, y_pos, str(character.defense.misc))
            c.drawString(x_pos + 130*mm, y_pos, str(character.defense.calculate_total()))
            
            # Armes
            y_pos -= 20*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos, y_pos, "Armes")
            
            y_pos -= 15*mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_pos, y_pos, "ARME")
            c.drawString(x_pos + 40*mm, y_pos, "ATTAQUE")
            c.drawString(x_pos + 70*mm, y_pos, "DM")
            c.drawString(x_pos + 90*mm, y_pos, "SPÉCIAL")
            
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            for weapon in character.weapons[:3]:  # Maximum 3 armes
                c.drawString(x_pos, y_pos, weapon.name or "")
                c.drawString(x_pos + 40*mm, y_pos, weapon.attack or "1d20+")
                c.drawString(x_pos + 70*mm, y_pos, weapon.damage or "")
                c.drawString(x_pos + 90*mm, y_pos, weapon.special or "")
                y_pos -= 6*mm
            
            # Capacités du personnage
            y_pos = 150*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20*mm, y_pos, "Capacités du personnage")
            
            y_pos -= 15*mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(20*mm, y_pos, "Voie 1")
            c.drawString(60*mm, y_pos, "Voie 2")
            c.drawString(100*mm, y_pos, "Voie 3")
            
            y_pos -= 8*mm
            c.setFont("Helvetica", 9)
            paths = [character.capabilities.path1, character.capabilities.path2, character.capabilities.path3]
            for i, path in enumerate(paths):
                x = 20*mm + i * 40*mm
                if path.name:
                    c.drawString(x, y_pos, f"R: {path.rank}")
                    y_pos -= 6*mm
                    if path.level1:
                        c.drawString(x, y_pos, f"1: {path.level1}")
                    y_pos -= 6*mm
                    if path.level2:
                        c.drawString(x, y_pos, f"2: {path.level2}")
                    y_pos -= 6*mm
                    if path.level3:
                        c.drawString(x, y_pos, f"3: {path.level3}")
                    y_pos -= 6*mm
            
            # Équipement
            y_pos = 100*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20*mm, y_pos, "Équipement")
            
            y_pos -= 15*mm
            c.setFont("Helvetica", 9)
            if character.equipment:
                for item in character.equipment[:10]:  # Maximum 10 items
                    c.drawString(20*mm, y_pos, f"• {item}")
                    y_pos -= 5*mm
            else:
                c.drawString(20*mm, y_pos, "-")
            
            # Objets de valeur
            y_pos = 100*mm
            x_pos = 120*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos, y_pos, "Objets de valeur")
            
            y_pos -= 15*mm
            c.setFont("Helvetica", 9)
            c.drawString(x_pos, y_pos, f"Bourse: {character.valuables.purse or ''}")
            y_pos -= 8*mm
            if character.valuables.items:
                for item in character.valuables.items[:10]:
                    c.drawString(x_pos, y_pos, f"• {item}")
                    y_pos -= 5*mm
            
            # Notes
            y_pos = 50*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y_pos, "Notes:")
            y_pos -= 8*mm
            c.setFont("Helvetica", 8)
            if character.notes:
                words = character.notes.split()
                line = ""
                for word in words:
                    if len(line + word) < 100:
                        line += word + " "
                    else:
                        c.drawString(20*mm, y_pos, line.strip())
                        y_pos -= 5*mm
                        line = word + " "
                if line:
                    c.drawString(20*mm, y_pos, line.strip())
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export PDF: {e}")
            return False

