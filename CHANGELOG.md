# Changelog - SCAN EPS

## Version 1.0 - 2026-07-26

### Correctifs

- **Parsing TEN EPS** : ajout d'un schéma dédié pour les QR TEN EPS (`parseMultiLignes`), qui
  auparavant tombaient dans le fallback générique. Les lignes d'en-tête de poule (`NomPoule:`)
  ne sont plus importées comme de fausses lignes de données, et les colonnes sont nommées
  clairement (`Rang`, `Joueur`, `Points`, `Victoires`, `Défaites`, `Bonus arbitrage`) au lieu de
  `TENEPS Col 1`, `TENEPS Col 2`. Gère aussi bien le mode poules (M1/M2) que le mode bracket (M3).
- **Classe CSS `.statut-warning` manquante** : les messages d'erreur de scan et de confirmation
  d'effacement des données n'avaient aucun style (fond neutre au lieu d'un rouge/rose d'alerte).

### Aide

- Badge **TEN EPS** ajouté à la liste des applications compatibles (avec BiathlonVMA, VB EPS,
  LaserFit).
- Mention explicite de TEN EPS dans la description des formats reconnus automatiquement.
- Numéro de version réel affiché (`Version 1.0`, aligné sur le `versionName` du wrapper Android)
  à la place du texte figé « Version PWA 2025 ».

### Interface smartphone

- Compteur de scans (3 pastilles) responsive : grille 3 colonnes sous 480px de large pour tenir
  sur une seule ligne au lieu de s'empiler verticalement.
- Retour haptique (`navigator.vibrate`) sur scan réussi et sur erreur - plus fiable que le seul
  son dans le bruit d'un gymnase ou d'un stade.
- **Wake Lock API** : l'écran ne se verrouille plus pendant une session de scan (réacquis
  automatiquement si l'app repasse au premier plan).
- Suppression de la ligne de balayage animée dans le cadre de scan (`.scan-line`) : purement
  cosmétique et redondante avec le cadre vert pulsant déjà présent, elle animait la propriété
  `top` (recalcul de layout à chaque frame) pendant que le téléphone décode déjà la vidéo, le
  canvas et jsQR en boucle.

### Conformité charte DESIGN-SYSTEM-EPS.md

- Pied de page `outils-eps.fr` ajouté (logo 36px + attribution, non cliquable), avec le logo mis
  en cache dans le service worker pour rester disponible hors ligne.
- Titre remplacé par **Scan EPS** (suppression de l'émoticône), avec **Version 1.0** affichée
  juste en-dessous à la place du sous-titre « Application professeur - Compatible avec toutes
  les activités EPS ».
- Message du badge principal reformulé : « Scanner universel : regroupe les résultats de
  plusieurs élèves dans un même fichier » (à la place de « Détection automatique des colonnes »).

### Non modifié (vérifié)

- Les préfixes BiathlonVMA `BJ1`/`BJ2`/`BJ3` sont bien reconnus et correctement mappés (vérifié
  contre le code source réel de Biathlon VMA) - aucune action nécessaire.
