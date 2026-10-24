#!/usr/bin/env python3
"""Génère scan-eps.pdf, le guide d'utilisation de SCAN EPS.
Usage : python3 generer-guide.py   (reportlab requis, polices Arial de macOS)

La version affichée est lue dans index.html ("Version X.Y" sous le titre) : relancer le script à chaque version.
Le texte reprend l'aide intégrée de l'app (modale « ? ») : à mettre à jour ici quand elle change.
Convention EPS : aucun tiret cadratin dans les documents générés."""
import os
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle)

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, 'scan-eps.pdf')
with open(os.path.join(ICI, 'index.html'), encoding='utf-8') as f:
    VERSION = re.search(r'<p>Version ([0-9.]+)</p>', f.read()).group(1)

POL = '/System/Library/Fonts/Supplemental/'
pdfmetrics.registerFont(TTFont('F', POL + 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('FB', POL + 'Arial Bold.ttf'))
pdfmetrics.registerFont(TTFont('FI', POL + 'Arial Italic.ttf'))
pdfmetrics.registerFont(TTFont('FM', POL + 'Courier New Bold.ttf'))
pdfmetrics.registerFontFamily('F', normal='F', bold='FB', italic='FI', boldItalic='FB')

ROSE = colors.HexColor('#E0457B')       # rose de l'app (#FF6B9D) assombri pour le texte sur fond blanc
ROSE_BG = colors.HexColor('#FFF0F5')
TEAL = colors.HexColor('#2A9D95')
ROUGE = colors.HexColor('#C62828')
GRIS = colors.HexColor('#555555')

corps = ParagraphStyle('corps', fontName='F', fontSize=9.3, leading=12.6, spaceAfter=4, textColor=colors.HexColor('#333333'))
puce = ParagraphStyle('puce', parent=corps, leftIndent=14, bulletIndent=3, spaceAfter=3)
titre = ParagraphStyle('titre', fontName='FB', fontSize=24, leading=28, textColor=colors.HexColor('#222222'))
sous = ParagraphStyle('sous', fontName='F', fontSize=10.5, leading=14, textColor=GRIS, spaceAfter=4)
h2 = ParagraphStyle('h2', fontName='FB', fontSize=13, leading=16, textColor=ROSE, spaceBefore=9, spaceAfter=4, keepWithNext=1)
note = ParagraphStyle('note', parent=corps, fontSize=8.8, leading=12.2)


def P(t, st=corps):
    return Paragraph(t, st)


def B(t):
    return Paragraph(t, puce, bulletText='•')


def N(n, t):
    return Paragraph(t, puce, bulletText='%d.' % n)


def encadre(paragraphes):
    t = Table([[paragraphes]], colWidths=[170 * mm])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), ROSE_BG), ('BOX', (0, 0), (-1, -1), 1, ROSE),
                           ('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 6),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    return t


def en_tete(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(ROSE)
    canvas.rect(0, h - 5 * mm, w, 5 * mm, stroke=0, fill=1)
    canvas.rect(0, 0, w, 5 * mm, stroke=0, fill=1)
    canvas.setFont('F', 8)
    canvas.setFillColor(GRIS)
    canvas.drawRightString(w - 20 * mm, 10 * mm,
                           "Guide d'utilisation - SCAN EPS - version %s - page %d" % (VERSION, doc.page))
    canvas.restoreState()


def lien_apk():
    return encadre([Paragraph(
        "<b>Téléchargement de l'APK</b> (Wi-Fi, <b>avant le cours</b>) :<br/>"
        '<font name="FM" size="8.5">https://github.com/msjeps/scaneps/releases/latest/download/SCANEPS-signed.apk</font><br/>'
        'Nom du fichier : <b>SCANEPS-signed.apk</b>', corps)])


def contenu():
    s = []
    s.append(P("Guide d'utilisation", titre))
    s.append(P("SCAN EPS : scanner universel de QR codes pour les applications EPS (version %s)" % VERSION, sous))
    ligne = Table([['']], colWidths=[170 * mm], rowHeights=[2])
    ligne.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1.5, TEAL)]))
    s += [ligne, Spacer(1, 4)]

    s.append(P("À quoi sert l'application ?", h2))
    s.append(P("<b>SCAN EPS</b> collecte les résultats des élèves en scannant, avec la caméra de la tablette du "
               "professeur, les QR codes générés par les applications d'évaluation EPS. Les données de tous les élèves "
               "sont regroupées dans <b>un seul tableau</b>, exportable en CSV pour Excel ou Google Sheets."))
    s.append(P("Elle fonctionne <b>entièrement hors connexion</b> : aucun accès internet n'est nécessaire pendant le "
               "cours. Les données scannées restent sur la tablette, elles ne sont envoyées nulle part."))

    s.append(P('Applications compatibles', h2))
    s.append(B("<b>VB EPS</b> (volley-ball), <b>BiathlonVMA</b>, <b>LaserFit</b> et <b>Match Manager EPS</b> (tournois), "
               "téléchargeables sur outils-eps.fr."))
    s.append(B("Toute autre application générant un QR code au format CSV ou JSON est prise en charge "
               "automatiquement (voir la dernière section pour le format)."))

    s.append(P('Installation', h2))
    s.append(P("<b>Tablette Android, fichier APK</b> (recommandé pour la flotte, à faire en Wi-Fi avant le cours) :"))
    s.append(N(1, "Téléchargez le fichier <b>SCANEPS-signed.apk</b> sur la tablette (encadré ci-dessous)."))
    s.append(N(2, "Ouvrez le fichier téléchargé. Android demande d'autoriser les sources inconnues : acceptez, "
                  "uniquement pour cette installation."))
    s.append(N(3, "Appuyez sur <b>Installer</b> puis <b>Ouvrir</b>. Une nouvelle version s'installe par-dessus la "
                  "précédente sans perdre les données scannées."))
    s.append(Spacer(1, 3))
    s.append(lien_apk())
    s.append(Spacer(1, 5))
    s.append(P("<b>Autre option, via Chrome (application web)</b> : ouvrez <b>https://apps.outils-eps.fr/scaneps/</b>, "
               "appuyez sur les trois points en haut à droite, puis « Ajouter à l'écran d'accueil ». Après une mise à "
               "jour, ouvrez l'application deux fois avec une connexion pour voir la nouvelle version."))
    s.append(P("<b>iPhone / iPad</b> : ouvrez la même adresse dans <b>Safari</b> (obligatoire sur iOS), appuyez sur "
               "Partager, puis « Sur l'écran d'accueil »."))

    s.append(P('Utilisation rapide', h2))
    s.append(N(1, "Appuyez sur <b>Démarrer la caméra</b> (acceptez l'autorisation caméra au premier lancement)."))
    s.append(N(2, "Présentez le QR code de l'élève dans le cadre vert."))
    s.append(N(3, "Le scan est automatique : un bip et une vibration confirment la lecture, et la ligne s'ajoute au "
                  "tableau."))
    s.append(N(4, "Scannez les QR codes suivants. Un délai de 2 secondes sépare deux scans."))
    s.append(N(5, "Appuyez sur <b>Exporter en CSV</b> pour récupérer les données dans Excel ou Google Sheets."))
    s.append(P("L'écran reste allumé tant que l'application est ouverte, et l'application s'affiche en plein écran "
               "(les barres du système sont masquées ; un balayage depuis le bord de l'écran les affiche un instant)."))

    s.append(P("Ce qu'il faut savoir sur les scans", h2))
    s.append(B("<b>Plusieurs applications dans la même séance</b> : vous pouvez scanner des QR codes de "
               "applications différentes, les colonnes sont fusionnées sans erreur. Le nombre de colonnes est "
               "illimité (LaserFit peut en générer plus de 15)."))
    s.append(B("<b>Plusieurs enregistrements par QR</b> : un seul QR peut contenir plusieurs élèves ou toute une "
               "séance, tout est importé en une passe."))
    s.append(B("<b>QR tronqué</b> : si l'application d'origine a dû raccourcir son QR (mention <font name='FM'>"
               "...+N obs</font>), un avertissement indique combien d'enregistrements manquent. Utilisez alors "
               "l'export CSV de l'application d'origine."))
    s.append(B("<b>Tablettes anciennes</b> : la première lecture peut prendre quelques secondes. Si la caméra se "
               "fige, l'application la relance toute seule."))
    s.append(B("<b>QR illisible</b> : une fenêtre « Erreur de lecture du QR code » donne le détail. Appuyez sur OK "
               "et recommencez ; le scan reprend à la fermeture de la fenêtre."))

    s.append(P('Corriger et effacer', h2))
    s.append(B("<b>Supprimer une ligne</b> : bouton de la ligne dans le tableau, puis confirmation."))
    s.append(B("<b>Effacer toutes les données</b> : bouton rouge, puis confirmation « Tout effacer ». Cette action "
               "supprime aussi la détection des colonnes et ne peut pas être annulée."))
    s.append(B("<b>Sauvegarde automatique</b> : les données scannées sont conservées sur la tablette même si vous "
               "fermez l'application ou si elle plante. Elles ne sont effacées que par le bouton ci-dessus."))

    s.append(P('Exporter les données', h2))
    s.append(B("<b>Format</b> : CSV compatible Excel français (séparateur point-virgule, encodage UTF-8)."))
    s.append(B("<b>Nom du fichier</b> : généré automatiquement sous la forme "
               "<font name='FM'>APPLICATION_CLASSE_AAAA-MM-JJ_HHhMM.csv</font>, par exemple "
               "<font name='FM'>LaserFit_3eB_2026-10-24_12h20.csv</font>. L'application et la classe sont lues dans "
               "les QR scannés ; si plusieurs sont mélangées, le nom contient <font name='FM'>Multi-apps</font> ou "
               "<font name='FM'>Multi-classes</font>."))
    s.append(B("<b>Sur la tablette</b> : le sélecteur de fichiers d'Android s'ouvre pour choisir le dossier "
               "(stockage de la tablette ou Google Drive). Le bouton Retour de la tablette annule l'export, et un "
               "message le confirme. Le bouton « Exporter vers Google Sheets » ouvre le même sélecteur."))
    s.append(B("<b>Protection</b> : une cellule qui commencerait par = + - ou @ est préfixée d'une apostrophe pour "
               "qu'Excel ne l'exécute pas comme une formule."))

    s.append(P('Bouton Retour de la tablette', h2))
    s.append(B("Il ferme d'abord l'aide ou la fenêtre ouverte."))
    s.append(B("S'il y a des données scannées, il demande confirmation (« Quitter Scan EPS ? ») avant de quitter : "
               "elles restent sauvegardées et réapparaissent à la réouverture."))
    s.append(B("Sans donnée scannée, il quitte directement."))

    s.append(P('Intégrer une autre application à SCAN EPS', h2))
    s.append(P("Toute application peut être lue si son QR code respecte la <b>convention CSV EPS</b> :"))
    code = Table([[Paragraph(
        "<font name='FM' size='8.5'># Ligne 1 : en-têtes (obligatoire)<br/>Nom;Prénom;Classe;Score;Date<br/>"
        "# Lignes 2 à N : données (1 élève par ligne)<br/>Alice;Martin;3A;42;26/02/2026<br/>"
        "Bob;Dupont;3A;38;26/02/2026</font>", corps)]], colWidths=[170 * mm])
    code.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F3F3')),
                              ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBBBBB')),
                              ('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 6)]))
    s.append(code)
    s.append(Spacer(1, 4))
    s.append(B("Séparateurs acceptés : point-virgule (recommandé), virgule ou tabulation. Les guillemets sont "
               "acceptés pour une valeur qui contient le séparateur."))
    s.append(B("Encodage UTF-8, nombre de colonnes illimité."))
    s.append(B("Trois formats sont reconnus automatiquement : CSV standard, JSON compact (BiathlonVMA) et "
               "multi-lignes avec préfixe (VB EPS, Match Manager EPS, LaserFit)."))
    s.append(B("Limite d'un QR code lisible à la caméra : environ 2 000 caractères. Au-delà, l'application d'origine "
               "doit proposer son export CSV."))

    s.append(P('Confidentialité', h2))
    s.append(P("Les données des élèves ne quittent jamais la tablette : pas de compte, pas de serveur, pas de "
               "transmission réseau. Le seul fichier qui sort est le CSV que vous choisissez d'enregistrer. "
               "Pensez à effacer les données en fin de séance si la tablette est partagée."))

    s.append(Spacer(1, 8))
    s.append(P("SCAN EPS, application développée par <b>Nathalie Prenois</b>, professeure EPS (Antibes), "
               "<b>https://outils-eps.fr</b>",
               ParagraphStyle('fin', parent=note, alignment=1, textColor=GRIS)))
    return s


doc = BaseDocTemplate(SORTIE, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=15 * mm,
                      bottomMargin=15 * mm, title="Guide d'utilisation - SCAN EPS",
                      author='Nathalie Prenois', subject='SCAN EPS version %s' % VERSION)
cadre = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
doc.addPageTemplates([PageTemplate(id='p', frames=[cadre], onPage=en_tete)])
doc.build(contenu())
print('OK', SORTIE, 'version', VERSION)
