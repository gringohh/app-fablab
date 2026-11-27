# Relais Drive

Petite application pour tablette Android : on choisit un fichier `.zip`, elle le **décompresse elle-même** (rien ne se mélange dans Téléchargements) et envoie tous les fichiers sur **Google Drive**, sous-dossiers compris. Claude peut ensuite lire le dossier via son connecteur Google Drive.

```
Tablette (.zip)  →  Relais Drive  →  Google Drive / Relais tablette / nom-du-zip / …  →  Claude
```

## Utilisation au quotidien

1. Ouvrir **Relais Drive** (icône sur l'écran d'accueil).
2. **Choisir des .zip** (version avancée : aussi depuis l'app Fichiers → **Partager** → **Relais Drive**).
3. Renommer le dossier si besoin, puis **Envoyer sur le Drive**.
4. Appuyer sur **Copier la phrase pour Claude** et la coller dans Claude.

Autres détails :

- Plusieurs .zip à la fois : un dossier par zip.
- « Autres fichiers » : envoie des fichiers normaux dans un dossier « Envoi du JJ-MM-AAAA ».
- Si le zip contient un seul dossier, il n'est pas répété (`Projet/…` et non `Projet/Projet/…`).
- Les fichiers parasites (`__MACOSX`, `.DS_Store`, `Thumbs.db`) sont ignorés.
- Si un dossier du même nom existe déjà, le nouveau s'appelle « nom (2) » : rien n'est écrasé.
- En cas de coupure réseau, les fichiers en échec sont listés ; appuyer à nouveau sur « Envoyer » ne renvoie que ceux-là.

## Installation : méthode simple (recommandée, sans Google Cloud)

Tout se fait avec **Google Apps Script**, directement dans ton compte Gmail perso : pas d'API à activer, pas d'identifiant à créer. Durée : environ 5 minutes, sur ordinateur de préférence.

### Étape 1 : créer le script

1. Aller sur <https://script.google.com/>, connecté avec le **Gmail perso** (celui du Drive).
2. **Nouveau projet**. En haut à gauche, renommer « Projet sans titre » en **Relais Drive**.
3. Dans le fichier **Code.gs** : tout effacer, puis coller **tout** le contenu de [`apps-script/Relais-Drive-complet.gs`](apps-script/Relais-Drive-complet.gs) (un seul fichier, la page est incluse dedans).
   *Pour copier depuis GitHub : ouvrir le fichier → bouton « Copy raw file » (icône 📋 en haut à droite du code).*
4. Enregistrer (icône 💾).

### Étape 2 : publier le script

1. En haut à droite : **Déployer** → **Nouveau déploiement**.
2. Roue ⚙️ à côté de « Sélectionner le type » → **Application Web**.
3. *Exécuter en tant que* : **Moi** ; *Qui a accès* : **Moi uniquement**.
4. **Déployer** → **Autoriser l'accès** → choisir le Gmail perso.
5. Google affiche « Google n'a pas validé cette application ». C'est normal, c'est ton propre script : **Paramètres avancés** → **Accéder à Relais Drive (non sécurisé)** → **Autoriser**.
6. Copier l'**URL de l'application Web** (elle finit par `/exec`).

### Étape 3 : sur la tablette

1. Ouvrir l'URL `/exec` dans **Chrome**, connecté au **Gmail perso**.
   *Si Chrome est connecté à plusieurs comptes Google, la page peut afficher une erreur : l'ouvrir alors dans un onglet où seul le Gmail perso est connecté, ou en navigation privée en se connectant au Gmail perso.*
2. Menu ⋮ → **Ajouter à l'écran d'accueil**. L'icône « Relais Drive » apparaît comme une application.

### Étape 4 : vérifier le connecteur Claude

Dans Claude (compte académique) : **Paramètres** → **Connecteurs** → **Google Drive**. Il doit être connecté au **Gmail perso**, sinon Claude ne verra pas les dossiers envoyés.

### Limites de la méthode simple

- 40 Mo maximum **par fichier** (le zip lui-même peut être plus gros).
- Pas d'entrée dans le menu « Partager » d'Android : on ouvre l'icône, puis « Choisir des .zip ».
- Mise à jour du script : modifier le code, puis **Déployer** → **Gérer les déploiements** → ✏️ → *Version* : **Nouvelle version** → **Déployer** (l'URL ne change pas).

## Installation : méthode avancée (application installable)

Le dossier `relais-drive/` contient aussi une version qui s'installe comme une vraie application, apparaît dans le menu **Partager** d'Android et gère les très gros fichiers. Elle demande en contrepartie de créer un identifiant dans Google Cloud Console.

### Étape 1 : mettre l'application en ligne (GitHub Pages)

1. Sur github.com, dépôt `gringohh/app-fablab` → **Settings** → **Pages**.
2. *Source* : **Deploy from a branch** ; *Branch* : `main`, dossier `/ (root)` → **Save**.
3. Après 1 à 2 minutes : **https://gringohh.github.io/app-fablab/relais-drive/**

> Le dépôt étant public, tout son contenu devient aussi consultable à cette adresse. Il l'était déjà sur github.com.

### Étape 2 : créer l'identifiant Google (avec le Gmail perso)

1. <https://console.cloud.google.com/> → **Nouveau projet** « Relais Drive ».
2. **API et services** → **Bibliothèque** → **Google Drive API** → **Activer**.
3. **Écran de consentement OAuth** : type **Externe**, ajouter ton Gmail comme **utilisateur test**.
4. **Identifiants** → **ID client OAuth** → type **Application Web**, origine JavaScript autorisée : `https://gringohh.github.io`.
5. Copier l'**ID client** (finit par `.apps.googleusercontent.com`). Ce n'est pas un secret.

### Étape 3 : sur la tablette

1. Ouvrir l'adresse GitHub Pages dans **Chrome**, coller l'ID client → **Enregistrer**.
2. Menu ⋮ → **Installer l'application** (nécessaire pour le menu « Partager »).
3. Au premier envoi : « application non validée » → **Paramètres avancés** → **Accéder à Relais Drive**.

## Sécurité et vie privée

- Méthode simple : le script s'exécute avec ton compte et seulement pour toi (« Moi uniquement ») ; il ne fait que créer des dossiers et des fichiers dans « Relais tablette ».
- Méthode avancée : autorisation **`drive.file`**, l'application ne voit que les fichiers qu'**elle a elle-même créés**.
- La décompression se fait dans la tablette. Les fichiers vont directement de la tablette à Google, sans serveur intermédiaire.

## Fichiers

| Fichier | Rôle |
|---|---|
| `apps-script/Relais-Drive-complet.gs` | méthode simple : le seul fichier à coller dans script.google.com |
| `apps-script/Code.gs`, `apps-script/Page.html` | sources de la méthode simple (le fichier complet en est généré) |
| `index.html` | application installable (méthode avancée) |
| `manifest.webmanifest` | installation sur l'écran d'accueil et menu « Partager » |
| `sw.js` | fonctionnement hors ligne et réception des fichiers partagés |
| `icones/` | icônes de l'application |
