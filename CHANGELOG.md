# Changelog - SCAN EPS

## 2026-10-24 (pont natif, bouton Retour, nom d'export - version affichée 1.2, versionCode 5)

- **Faux message de succès corrigé** : en mode APK, la page n'affiche plus « téléchargé avec succès » à l'appel de `saveCSV`. Kotlin signale le vrai résultat (enregistré, annulé, trop gros > 5 Mo, contenu perdu, erreur d'écriture) via `updateStatut`, message passé par `JSONObject.quote`. L'état en attente est vidé dans tous les cas.
- **Pont durci** : `shouldOverrideUrlLoading` limité à `appassets.androidplatform.net` ; caméra accordée seulement pour cette origine.
- **Bouton Retour** : Kotlin délègue à `window.__androidBack()`. La page ferme d'abord la fenêtre ouverte (aide, Sheets), sinon demande « Quitter Scan EPS ? » (modale maison) si des données sont scannées ; sans donnée, l'app se ferme. Nouvelle méthode de pont `quitApp()`.
- **Nom d'export** : `APPLICATION_CLASSE_AAAA-MM-JJ_HHhMM.csv` (ex. `TEN-EPS_3eB_2026-10-24_12h20.csv`), application et classe lues dans les données scannées ; plusieurs applications : `Multi-apps`, plus de 3 classes : `Multi-classes`, classe absente : segment omis. `:` interdit dans un nom de fichier Android, d'où `12h20`.
- Cache `scan-eps-v10`. APK signé avec le même certificat (SHA-256 5440670f…f889). **Non testé sur tablette, non publié** (push et Release en attente de confirmation).

## 2026-10-24 (charte EPS, aide, publication - version affichée 1.1, versionCode 4)

- **Charte graphique** ([DESIGN-SYSTEM-EPS.md](../DESIGN-SYSTEM-EPS.md)) : version, pied de page, police et variables CSS étaient déjà conformes. Titre et titre de l'aide : texte en dégradé transparent remplacé par une couleur unie ; boutons (`primaire`, `success`, `csv`, `sheets`, `danger`) et badge « Scanner universel » : dégradé remplacé par un fond uni (le combo `linear-gradient` + `border-radius` n'est pas rendu sur le GPU PowerVR GE8320). Non testé sur tablette.
- **Aide** : adresse web `apps.outils-eps.fr/scaneps/` (l'ancienne `msjeps.github.io` redirige), nom de l'APK `SCANEPS-signed.apk` avec lien de téléchargement (Release GitHub « latest »), limite « 5 enregistrements » retirée (le code n'en impose aucune), avertissement de QR tronqué (`...+N obs`) documenté, LaserFit classé dans les formats multi-lignes à préfixe.
- **Publication** : `index.html` + `sw.js` poussés sur `msjeps/scaneps` (cache `scan-eps-v7`). APK `versionCode` 4 (même certificat que le v3, installable par-dessus) publié dans la Release `v1.1` : https://github.com/msjeps/scaneps/releases/tag/v1.1. Le lien de l'aide n'est pas encore dans l'APK publié (prévu pour v1.2).
- **Dépôt git local** créé dans `SCAN EPS/`, relié à `origin` (`msjeps/scaneps`). L'APK n'est pas versionné (il est dans la Release).
- **À faire** : voir l'entrée ci-dessus (corrigé dans le code, pas encore publié).

## 2026-10-24 (audit de sécurité - correctif interne, version affichée inchangée)

- **Faille XSS stockée corrigée** : les données décodées d'un QR (en-têtes de colonnes, cellules,
  bandeau "colonnes détectées") étaient réinjectées dans `innerHTML` sans aucun échappement, y
  compris après rechargement depuis `localStorage`. Un QR contenant une balise HTML (`<img onerror=...>`,
  `<svg onload=...>`) s'exécutait comme du code à l'écran suivant. Nouveau helper `escapeHtml()`,
  appliqué aux 4 points de rendu concernés (`genererEntetes`, les deux bandeaux `infoColonnes`,
  `afficherDonnees`). Correctif recopié dans les assets de l'APK (`ScanEPS/app/src/main/assets/`).
  Cache du service worker passé à `scan-eps-v3`. Détails dans `security-audit-reports/SCAN-EPS/`
  et la leçon générale dans `../LECONS-TECHNIQUES.md`. Publié le 2026-10-24.
- **Injection de formule CSV corrigée** (`construireCSV` : préfixe `'` sur `= + - @`, nombres purs épargnés).
- **APK** : `allowBackup="false"`, nom de fichier assaini et taille limitée dans le pont `saveCSV`, `versionCode` 3 (version affichée 1.1 inchangée), `SCANEPS-signed.apk` reconstruit avec la même clé. Cache SW `scan-eps-v4`. Non testé sur tablette. Publié sur GitHub Pages le 2026-10-24.

## Version 1.1 - 2026-10-08 (audit de compatibilité)

- **LaserFit** : schéma dédié (`LASERFIT|classe|date|observateur`). Avant, le QR tombait dans le
  fallback générique (`LASERFIT Col 1…`). Colonnes désormais nommées : Pratiquant, Exercice/Reps/Pts N, Score total.
- **BiathlonVMA mode distance** (`m:"d"` dans BJ2/BJ3) : le détail des courses était libellé en
  mètres alors que ces valeurs sont des km/h. Libellé corrigé.
- **QR tronqué (VB EPS, LaserFit)** : la ligne `...+N obs` était ignorée en silence, le scan
  affichait « ajouté » alors que des observations manquaient. Un avertissement s'affiche maintenant.
- Cache du service worker passé à `scan-eps-v2` pour que les tablettes récupèrent la mise à jour.
- Version affichée et APK passées en 1.1 (`versionCode` 2) ; `SCANEPS-signed.apk` reconstruit avec la même clé (`scaneps.jks`) : installable par-dessus la 1.0.

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
