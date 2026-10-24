# Changelog - SCAN EPS

## 2026-10-24 (nom de fichier d'export Match Manager EPS et VB EPS - version 1.7, versionCode 10, publiée dans la Release `v1.7`)

- **Match Manager EPS et VB EPS** : le décodage des QR `TENEPS|` et `VBEPS|` ajoute désormais une colonne `Application` (en première position, valeurs `Match Manager EPS` et `VB EPS`), comme LaserFit et BiathlonVMA. Le CSV exporté est donc nommé `Match-Manager-EPS_<classe>_<date>_<heure>.csv` (ou `VB-EPS_...`) au lieu de `SCAN-EPS_...`. Testé en Node sur un QR de chaque app. Effet de bord voulu : le CSV gagne cette colonne. La limite notée dans l'entrée v1.6 est levée dès la prochaine publication.
- **Version 1.7** : version affichée (2 endroits de `index.html`), `versionName` 1.7 / `versionCode` 10, cache `scan-eps-v17`, `index.html` et `sw.js` recopiés dans `ScanEPS/app/src/main/assets/` (`cmp` identiques). APK reconstruit (`app-release.apk`, 5 122 762 octets), vérifié avec `apksigner` : même certificat (SHA-256 5440670f…f889), `aapt` lit versionCode 10 / versionName 1.7, assets de l'APK contenant bien la colonne `Application` et le cache v17. Guide PDF régénéré en version 1.7 (2 pages, page 1 relue). Test Node refait sur la v1.7 : `Match-Manager-EPS_3eB_..._19h46.csv` et `VB-EPS_3eB_..._19h46.csv`. **Non testé sur tablette.** **Publiée le 2026-10-24** : commit `17d71ba` (`index.html`, `sw.js`, `CHANGELOG.md`), site en ligne en `scan-eps-v17`, Release `v1.7` (`SCANEPS-signed.apk`, SHA-256 du fichier 686291a6…b66ba, identique au téléchargement « latest »), clone public à jour (`git status` propre, `cmp` ok), APK 1.6 sauvegardé dans `scaneps-backup/SCANEPS-signed-v9-1.6.apk`.
- Note : la balise `<meta name="description">` de la copie `assets/` différait déjà de celle du dépôt web avant ce correctif (texte plus court sans tiret cadratin) ; elle est maintenant alignée sur le dépôt web (invisible dans l'app).

## 2026-10-24 (aide : TEN EPS devient Match Manager EPS - version 1.6, versionCode 9, publiée dans la Release `v1.6`)

- **Aide** : le badge « TEN EPS - Tennis » devient « Match Manager EPS » (l'application a été renommée) ; la liste des formats reconnus et l'exemple de nom de fichier d'export sont mis à jour (l'exemple utilise LaserFit, dont le schéma porte la colonne `Application`). Le libellé de source affiché après un scan devient `[Match Manager EPS]`.
- **Décodage inchangé** : Match Manager EPS garde le préfixe `TENEPS|` dans ses QR, le parseur le lit toujours (testé avec un QR `TENEPS|...` : 2 lignes, 9 colonnes). Limite connue : ce schéma n'a pas de colonne `Application`, donc un export de Match Manager est nommé `SCAN-EPS_<classe>_<date>.csv`.
- Cache `scan-eps-v16`, même certificat (SHA-256 5440670f…f889, vérifié). Guide PDF régénéré avec les mêmes changements. Non testé sur tablette (texte d'aide seulement).

## 2026-10-24 (écarts de charte - version 1.5, versionCode 8, publiée dans la Release `v1.5`)

- **Plus de `alert` / `confirm` natifs** : boîte de message maison (`afficherModale`, `#modalMessage`, texte via `textContent`) pour la suppression d'une ligne, l'effacement de toutes les données, l'erreur de lecture QR, l'échec caméra et « aucune donnée à exporter ». Le scan est suspendu tant qu'elle est ouverte (comme avec `alert`) ; le bouton Retour la ferme en premier.
- **Mode immersif dans l'APK** : `MainActivity` masque les barres système (`WindowInsetsControllerCompat`, balayage du bord pour les revoir) au démarrage et à chaque reprise du focus (retour du sélecteur de fichiers).
- **Dégradés remplacés par des fonds unis** : fond de page, statuts, compteurs, bandeaux, bouton d'aide, en-tête du tableau, badges de l'aide. `inset: 0` des modales remplacé par `top/right/bottom/left`.
- **Aide** : nom du fichier d'export (`APPLICATION_CLASSE_AAAA-MM-JJ_HHhMM.csv`) et comportement du bouton Retour. **Guide PDF** `scan-eps.pdf` créé (2 pages, `generer-guide.py`, reportlab) avec le texte de l'aide, le lien de l'APK et le nom de fichier exacts ; non publié.
- Cache `scan-eps-v15`. Même certificat (SHA-256 5440670f…f889, vérifié). Testé dans un navigateur (modales, annulation, confirmation, Retour, injection HTML dans un message), puis **testé sur la Lenovo TB-X606F par Nathalie : tout est ok** (mode immersif, modales au doigt, fonds unis). Publié le 2026-10-24 : commit `5fb7d3e`, site en ligne en `scan-eps-v15`, Release `v1.5`. Le guide PDF reste à mettre en ligne sur outils-eps.fr (site en maintenance).

## 2026-10-24 (scan caméra réparé sur la tablette lente - version 1.4, versionCode 7, publiée dans la Release `v1.4`)

- **Cause trouvée par mesure sur la Lenovo TB-X606F** (débogage USB, captures et logcat) : jsQR mettait **1084 ms par image** (WebView 155, CPU Helio P22T), plus une analyse inversée (`attemptBoth`) et un nouveau canvas 1280×720 créé 60 fois par seconde. Le premier QR LaserFit demandait environ 1 minute, puis l'app saturait.
- **Lecture native `BarcodeDetector`** (134 ms par image, mesuré) utilisée en priorité quand le WebView la fournit ; jsQR reste le repli si elle est absente ou échoue, plus un essai sur 20 si elle ne lit rien. Résultat sur la tablette : premier QR lu en 1 à 2 s, les suivants s'enchaînent.
- Boucle d'analyse : un seul canvas réutilisé (`willReadFrequently`), `setTimeout` de 150 ms après la fin de chaque analyse au lieu de `requestAnimationFrame`, `dontInvert`.
- **Cadre vert statique** : l'animation `scanPulse` (ombre de 2000 px animée) repeignait toute la vidéo à chaque image sur le GPU PowerVR ; supprimée avec les coins arrondis de la zone vidéo.
- **Veille caméra** : relance automatique si l'image se fige plus de 4 s ou si la piste est coupée ; mise au point continue demandée (la caméra arrière 0 a l'autofocus).
- Permission `VIBRATE` ajoutée (la vibration de confirmation échouait silencieusement).
- Cache `scan-eps-v14`. Même certificat (SHA-256 5440670f…f889). Testé sur la tablette : scan, enchaînement, arrêt/relance de la caméra, écran allumé. Reste à tester avant publication : plusieurs minutes de scan continu, rotation, QR d'autres apps.

## 2026-10-24 (clone du dépôt public)

- **Clone de `msjeps/scaneps`** créé dans `~/Documents/APPLI EPS/APPLI EPS/scaneps/` (même convention que LaserFit, Match Manager EPS et Biathlon VMA), avec l'APK de la Release `v1.3` (`SCANEPS-signed.apk`, identique octet pour octet). **Règle : ce clone est mis à jour à chaque publication PWA ou APK.** Aucun changement de code. Le dossier `scaneps-backup/` (anciens APK + clé `scaneps.jks`) a été déplacé dans ce clone (`scaneps/scaneps-backup/`, exclu de git) ; `storeFile` de `ScanEPS/keystore.properties` mis à jour, fichier `.jks` retrouvé au nouvel emplacement.

## 2026-10-24 (écran toujours allumé - version affichée 1.3, versionCode 6)

- **`FLAG_KEEP_SCREEN_ON`** ajouté dans `MainActivity` : l'écran ne se met plus en veille pendant une session de scan (APK). **Wake Lock PWA** : l'écran reste allumé tant que l'app est ouverte (avant : seulement caméra active), réacquis au retour au premier plan et au premier toucher. Cache `scan-eps-v11`. Publié dans la Release `v1.3` le 2026-10-24 ; non testé sur tablette.

## 2026-10-24 (pont natif, bouton Retour, nom d'export - version affichée 1.2, versionCode 5)

- **Faux message de succès corrigé** : en mode APK, la page n'affiche plus « téléchargé avec succès » à l'appel de `saveCSV`. Kotlin signale le vrai résultat (enregistré, annulé, trop gros > 5 Mo, contenu perdu, erreur d'écriture) via `updateStatut`, message passé par `JSONObject.quote`. L'état en attente est vidé dans tous les cas.
- **Pont durci** : `shouldOverrideUrlLoading` limité à `appassets.androidplatform.net` ; caméra accordée seulement pour cette origine.
- **Bouton Retour** : Kotlin délègue à `window.__androidBack()`. La page ferme d'abord la fenêtre ouverte (aide, Sheets), sinon demande « Quitter Scan EPS ? » (modale maison) si des données sont scannées ; sans donnée, l'app se ferme. Nouvelle méthode de pont `quitApp()`.
- **Nom d'export** : `APPLICATION_CLASSE_AAAA-MM-JJ_HHhMM.csv` (ex. `TEN-EPS_3eB_2026-10-24_12h20.csv`), application et classe lues dans les données scannées ; plusieurs applications : `Multi-apps`, plus de 3 classes : `Multi-classes`, classe absente : segment omis. `:` interdit dans un nom de fichier Android, d'où `12h20`.
- Cache `scan-eps-v10`. APK signé avec le même certificat (SHA-256 5440670f…f889). Publié dans la Release `v1.2` (remplacée ensuite par la `v1.3`). **Non testé sur tablette.**

## 2026-10-24 (charte EPS, aide, publication - version affichée 1.1, versionCode 4)

- **Charte graphique** ([DESIGN-SYSTEM-EPS.md](../DESIGN-SYSTEM-EPS.md)) : version, pied de page, police et variables CSS étaient déjà conformes. Titre et titre de l'aide : texte en dégradé transparent remplacé par une couleur unie ; boutons (`primaire`, `success`, `csv`, `sheets`, `danger`) et badge « Scanner universel » : dégradé remplacé par un fond uni (le combo `linear-gradient` + `border-radius` n'est pas rendu sur le GPU PowerVR GE8320). Non testé sur tablette.
- **Aide** : adresse web `apps.outils-eps.fr/scaneps/` (l'ancienne `msjeps.github.io` redirige), nom de l'APK `SCANEPS-signed.apk` avec lien de téléchargement (Release GitHub « latest »), limite « 5 enregistrements » retirée (le code n'en impose aucune), avertissement de QR tronqué (`...+N obs`) documenté, LaserFit classé dans les formats multi-lignes à préfixe.
- **Publication** : `index.html` + `sw.js` poussés sur `msjeps/scaneps` (cache `scan-eps-v7`). APK `versionCode` 4 (même certificat que le v3, installable par-dessus) publié dans la Release `v1.1` : https://github.com/msjeps/scaneps/releases/tag/v1.1. Le lien de l'aide n'est pas encore dans l'APK publié (prévu pour v1.2).
- **Dépôt git local** créé dans `SCAN EPS/`, relié à `origin` (`msjeps/scaneps`). L'APK n'est pas versionné (il est dans la Release).
- **À faire** : voir l'entrée ci-dessus (corrigé et publié depuis, Releases v1.1 à v1.3).

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
