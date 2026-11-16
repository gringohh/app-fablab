# Projet — tableau de bord des projets

**Auteur : H. Hammadou** — © 2026, tous droits réservés (voir [LICENCE](LICENCE)).

Application pour remplir la fiche de projet, générer les diagrammes SysML et le planning, puis imprimer la fiche officielle en PDF.

## 1. Version fichier unique (hors ligne)

Ouvrir `index.html` dans un navigateur récent (Firefox, Chrome, Edge). C'est tout.

- **Accueil** : choix Seconde SI-CIT (version simplifiée), Première STI2D (36 h) ou Terminale 2I2D (72 h), « Charger l'exemple », « Ouvrir un projet enregistré » (.json).
- **Onglets** : Fiche projet, Équipe et tâches, Exigences, Cas d'utilisation, Contexte, Planning, Export PDF.
- **Diagrammes** : mis à jour en direct ; les éléments se déplacent à la souris ; « Réorganiser » rétablit la mise en page automatique.
- **Planning** : chaque élève dispose de 36 h (Première) ou 72 h (Terminale). Les tâches « Toute l'équipe » comptent pour chaque élève. Une alerte apparaît en cas de dépassement.
- **Sauvegarde** : automatique dans le navigateur (localStorage). « Exporter JSON » pour rendre le projet ou le reprendre sur un autre poste.
- **PDF** : onglet « Export PDF » → « Imprimer / Enregistrer en PDF » → imprimante « Enregistrer au format PDF », format A4.

Aucune donnée n'est envoyée sur Internet.

### Seconde SI-CIT (mini « Course en cours », toute l'année)

Parcours simplifié : fiche courte (nom du projet, nom de l'équipe, classe, besoin, ce que l'on va fabriquer), **règlement vérifié automatiquement** (voiture 100 mm maximum, stand 150 × 150 × 150 mm), logiciels et machines (SolidWorks, SketchUp, Tinkercad, imprimante 3D, découpe laser…), « Qui fait quoi ? » (groupes de 4 à 6), **bête à cornes**, diagramme de contexte, planning des vendredis. Fiche PDF sur 2 pages.

- **Séances** : chaque vendredi du 20/11/2026 à mi-juin 2027, 1 h puis 2 h en alternance, hors vacances de la zone B et pont de l'Ascension (23 séances, 35 h). Le professeur peut retirer ou modifier une séance (Planning → « Calendrier des séances »).
- **Tâches** : une tâche peut être faite par plusieurs élèves (bouton « Tout le groupe ») ; elle compte pour chacun. Le contrôle compare les heures de chaque élève au total des séances.
- Règlement, logiciels et calendrier se modifient en tête du script (`const SECONDE`).

## 2. Mode serveur (réseau du lycée)

Sur le PC du professeur (Python 3, aucune bibliothèque à installer) :

```
python3 serveur.py --mot-de-passe MonMotDePasse
```

Options : `--port 8000`, `--dossier chemin/des/projets`, `--local` (tests sur ce PC uniquement).

- Les élèves ouvrent `http://<adresse-du-PC>:8000/` (l'adresse s'affiche au démarrage) et disposent d'un bouton **« Envoyer au professeur »**.
- Les projets sont rangés dans `projets_recus/` (un fichier par équipe et par projet ; les versions précédentes vont dans `projets_recus/historique/`).
- Page professeur : `http://<adresse-du-PC>:8000/prof` (protégée par le mot de passe, nom d'utilisateur libre) : liste des projets, alertes d'heures, ouverture dans l'application, téléchargement JSON.

Le pare-feu Windows peut demander d'autoriser Python sur le réseau privé.

## 3. Sur tablette (iPad, Android)

L'application s'adapte à l'écran et les diagrammes se manipulent au doigt. Trois façons de l'utiliser :

**a) Installée sur l'écran d'accueil (recommandé, fonctionne ensuite hors ligne)**
L'application doit être publiée en https, par exemple avec GitHub Pages (gratuit) :
1. Sur GitHub : *Settings* → *Pages* → *Source : Deploy from a branch* → branche `main`, dossier `/ (root)` → *Save*.
2. Après une ou deux minutes, l'adresse est : `https://<compte>.github.io/app-fablab/projets-sti2d/`
3. Sur la tablette, ouvrir cette adresse puis :
   - **iPad (Safari)** : bouton Partager → « Sur l'écran d'accueil » ;
   - **Android (Chrome)** : menu ⋮ → « Installer l'application ».

L'icône « Projets STI2D » apparaît ; l'application s'ouvre en plein écran, même sans Internet. Les projets restent enregistrés sur la tablette (rien n'est envoyé en ligne). Les mises à jour publiées sur GitHub arrivent automatiquement au lancement suivant.

**b) Par le serveur du lycée** : ouvrir `http://<adresse-du-PC>:8000/` dans le navigateur de la tablette (même réseau Wi-Fi). Le bouton « Envoyer au professeur » fonctionne ; en revanche l'usage hors ligne nécessite la méthode a).

**c) Fichier local** : possible sur Android (ouvrir `index.html` avec Chrome ou Firefox), peu pratique sur iPad.

Conseils tablette :
- **PDF** : bouton « Imprimer / Enregistrer en PDF » ; sur iPad, dans l'aperçu d'impression, utiliser Partager → « Enregistrer dans Fichiers ».
- **Sauvegarde** : exporter régulièrement le projet en JSON (Fichiers / Téléchargements). Sur iPad, Safari peut effacer les données d'un site non installé après plusieurs semaines sans utilisation : l'installation sur l'écran d'accueil (méthode a) évite ce problème.

## Personnalisation

La liste des thématiques de Terminale, les spécialités, les domaines et les heures par niveau sont définis en tête du script de `index.html` (section « CONSTANTES »).

## Droits d'auteur

© 2026 H. Hammadou – Tous droits réservés. Toute reproduction, modification ou redistribution, totale ou partielle, sans l'accord écrit de l'auteur est interdite.
