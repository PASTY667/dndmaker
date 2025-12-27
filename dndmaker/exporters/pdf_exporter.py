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
from PIL import Image as PILImage

from ..models.character import Character, CharacterType
from ..models.scene import Scene
from ..models.session import Session


class PDFExporter:
    """Exporteur PDF pour les fiches de personnage"""
    
    def __init__(self, project_service=None):
        """
        Initialise l'exporteur PDF
        
        Args:
            project_service: Service de projet pour accéder aux médias (optionnel)
        """
        self.page_width, self.page_height = A4
        self.project_service = project_service
    
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
            c.drawString(20*mm, self.page_height - 30*mm, f"Personnage: {character.name}")
            
            # Image du personnage (si disponible) - placée en haut à droite, avant le contenu
            image_height_used = 0
            image_x_pos = 120*mm
            image_width = 50*mm
            image_height = 50*mm
            image_y_start = self.page_height - 40*mm  # Juste sous le titre
            
            if character.image_id and self.project_service and self.project_service.media_service:
                image_path = self.project_service.media_service.get_image_path(character.image_id)
                if image_path and image_path.exists():
                    try:
                        # Charger l'image avec PIL pour obtenir ses dimensions
                        pil_image = PILImage.open(str(image_path))
                        img_width, img_height = pil_image.size
                        
                        # Calculer les dimensions en conservant le ratio
                        ratio = min(image_width / img_width, image_height / img_height)
                        new_width = img_width * ratio
                        new_height = img_height * ratio
                        
                        # Centrer l'image horizontalement dans l'espace alloué
                        x_offset = image_x_pos + (image_width - new_width) / 2
                        y_offset = image_y_start - new_height
                        
                        # Dessiner l'image avec reportlab (qui utilise PIL en interne)
                        c.drawImage(str(image_path), x_offset, y_offset, 
                                  width=new_width, height=new_height, 
                                  preserveAspectRatio=True, mask='auto')
                        image_height_used = new_height + 5*mm  # Espace utilisé + marge
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de l'image au PDF: {e}")
            
            # Section Profil - commence après le titre
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
            
            # Sauvegarder la position Y de la colonne de gauche après "Langues connues"
            left_column_y_after_langues = y_pos
            
            # Calculer la position de départ de la section Combat (colonne de droite)
            # Cette variable est nécessaire pour éviter les chevauchements avec les capacités
            combat_y_start = self.page_height - 50*mm
            if image_height_used > 0:
                # Commencer après l'image avec une marge
                combat_y_start = self.page_height - 40*mm - image_height_used - 10*mm
            
            # Combat - décalé vers le bas si une image est présente
            x_pos = 120*mm
            y_pos = combat_y_start
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
            
            # Sauvegarder la position Y de la colonne de droite après Armes
            right_column_y_after_armes = y_pos
            
            # Capacités du personnage - placées après les caractéristiques à gauche
            # Calculer la position Y en fonction de la fin des caractéristiques
            capabilities_y_start = left_column_y_after_langues - 20*mm  # Espace après "Langues connues"
            
            # Vérifier qu'on ne chevauche pas avec la section Combat à droite
            # Si la section Combat commence trop haut, décaler les capacités
            if image_height_used > 0:
                # Estimation de la hauteur de la section Combat (titre + données)
                combat_bottom = combat_y_start - 100*mm
                if capabilities_y_start > combat_bottom:
                    capabilities_y_start = combat_bottom - 15*mm
            
            y_pos = capabilities_y_start
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
            # Calculer la hauteur maximale nécessaire pour toutes les voies
            max_path_height = 0
            for i, path in enumerate(paths):
                x = 20*mm + i * 40*mm
                path_y = y_pos
                path_lines = 0
                if path.name:
                    path_lines += 1  # R: rank
                    if path.level1:
                        path_lines += 1
                    if path.level2:
                        path_lines += 1
                    if path.level3:
                        path_lines += 1
                    path_height = path_lines * 6*mm
                    max_path_height = max(max_path_height, path_height)
                    
                    # Dessiner le contenu de la voie
                    c.drawString(x, path_y, f"R: {path.rank}")
                    path_y -= 6*mm
                    if path.level1:
                        c.drawString(x, path_y, f"1: {path.level1}")
                        path_y -= 6*mm
                    if path.level2:
                        c.drawString(x, path_y, f"2: {path.level2}")
                        path_y -= 6*mm
                    if path.level3:
                        c.drawString(x, path_y, f"3: {path.level3}")
                        path_y -= 6*mm
            
            # Ajuster y_pos pour la prochaine section (équipement)
            # Si aucune voie n'a de contenu, max_path_height sera 0, donc on décale juste de 10mm
            left_column_y = y_pos - max_path_height - 10*mm if max_path_height > 0 else y_pos - 10*mm
            
            # Équipement - continue la colonne de gauche
            y_pos = left_column_y
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
                y_pos -= 5*mm
            
            # Objets de valeur - continue la colonne de droite après Armes
            y_pos = right_column_y_after_armes
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
            
            # Notes - en bas de page, colonne de gauche
            # Utiliser la position la plus basse entre les deux colonnes
            # Calculer où se termine la colonne de droite (Objets de valeur)
            right_column_y_final = y_pos
            notes_y = min(left_column_y, right_column_y_final) - 20*mm
            y_pos = notes_y
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
            import traceback
            error_msg = f"Erreur lors de l'export PDF: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False

