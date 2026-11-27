# Relais Drive

Petite application pour tablette Android : on choisit un fichier `.zip`, elle le **décompresse elle-même** (rien ne se mélange dans Téléchargements) et envoie tous les fichiers sur **Google Drive**, sous-dossiers compris. Claude peut ensuite lire le dossier via son connecteur Google Drive.

```
Tablette (.zip)  →  Relais Drive  →  Google Drive / Relais tablette / nom-du-zip / …  →  Claude
```

## Utilisation au quotidien

1. Ouvrir **Relais Drive** (icône sur l'écran d'accueil).
2. **Choisir des .zip**, ou depuis l'app Fichiers : sélectionner le .zip → **Partager** → **Relais Drive**.
3. Renommer le dossier si besoin, puis **Envoyer sur le Drive**.
4. Appuyer sur **Copier la phrase pour Claude** et la coller dans Claude.

Autres détails :

- Plusieurs .zip à la fois : un dossier par zip.
- « Autres fichiers » : envoie des fichiers normaux dans un dossier « Envoi du JJ-MM-AAAA ».
- Si le zip contient un seul dossier, il n'est pas répété (`Projet/…` et non `Projet/Projet/…`).
- Les fichiers parasites (`__MACOSX`, `.DS_Store`, `Thumbs.db`) sont ignorés.
- Si un dossier du même nom existe déjà, le nouveau s'appelle « nom (2) » : rien n'est écrasé.
- En cas de coupure réseau, les fichiers en échec sont listés ; appuyer à nouveau sur « Envoyer » ne renvoie que ceux-là.

## Installation (une seule fois)

### Étape 1 : mettre l'application en ligne (GitHub Pages)

1. Sur github.com, dépôt `gringohh/app-fablab` → **Settings** → **Pages**.
2. *Source* : **Deploy from a branch** ; *Branch* : `main`, dossier `/ (root)` → **Save**.
3. Après 1 à 2 minutes, l'application est à l'adresse :
   **https://gringohh.github.io/app-fablab/relais-drive/**

> Le dépôt étant public, tout son contenu (dont `fablab.html` et `projets-sti2d/`) devient aussi consultable à cette adresse. Il l'était déjà sur github.com.

### Étape 2 : créer l'identifiant Google (avec le **Gmail perso**, celui du Drive)

1. Aller sur <https://console.cloud.google.com/> connecté avec le Gmail perso.
2. En haut : **Sélectionner un projet** → **Nouveau projet** → nom « Relais Drive » → **Créer**.
3. Menu ☰ → **API et services** → **Bibliothèque** → chercher **Google Drive API** → **Activer**.
4. Menu ☰ → **API et services** → **Écran de consentement OAuth** (ou « Google Auth Platform ») :
   - Type d'utilisateur : **Externe** ; nom de l'application « Relais Drive » ; adresse e-mail : ton Gmail.
   - **Audience / Utilisateurs test** : ajouter ton Gmail.
5. **Identifiants** (ou « Clients ») → **Créer des identifiants** → **ID client OAuth** :
   - Type : **Application Web** ;
   - **Origines JavaScript autorisées** : `https://gringohh.github.io`
   - **Créer**, puis copier l'**ID client** (il finit par `.apps.googleusercontent.com`).

L'ID client n'est pas un secret : il peut être collé dans l'application sans risque.

### Étape 3 : sur la tablette

1. Ouvrir **https://gringohh.github.io/app-fablab/relais-drive/** dans **Chrome**.
2. Coller l'ID client → **Enregistrer**.
3. Menu ⋮ de Chrome → **Ajouter à l'écran d'accueil** / **Installer l'application**. C'est nécessaire pour que « Relais Drive » apparaisse dans le menu **Partager**.
4. Premier envoi : Google affiche « Google n'a pas validé cette application ». C'est normal, c'est ton application : **Paramètres avancés** → **Accéder à Relais Drive** → **Continuer**.

### Étape 4 : vérifier le connecteur Claude

Dans Claude (compte académique) : **Paramètres** → **Connecteurs** → **Google Drive**. Il doit être connecté au **Gmail perso**, sinon Claude ne verra pas les dossiers envoyés.

## Sécurité et vie privée

- L'application demande seulement l'autorisation **`drive.file`** : elle ne peut voir et modifier que les fichiers qu'**elle a elle-même créés**, pas le reste du Drive.
- La décompression se fait dans la tablette. Les fichiers vont directement de la tablette à Google, sans serveur intermédiaire.
- La connexion dure environ 1 heure, ensuite Google redemande l'autorisation d'un simple appui.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | l'application |
| `manifest.webmanifest` | installation sur l'écran d'accueil et menu « Partager » |
| `sw.js` | fonctionnement hors ligne et réception des fichiers partagés |
| `icones/` | icônes de l'application |
