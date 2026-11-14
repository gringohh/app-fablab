# Tableau de bord des projets STI2D

Application pour remplir la fiche de projet, générer les diagrammes SysML et le planning, puis imprimer la fiche officielle en PDF.

## 1. Version fichier unique (hors ligne)

Ouvrir `index.html` dans un navigateur récent (Firefox, Chrome, Edge). C'est tout.

- **Accueil** : choix Première STI2D (36 h) ou Terminale 2I2D (72 h), « Charger l'exemple », « Ouvrir un projet enregistré » (.json).
- **Onglets** : Fiche projet, Équipe et tâches, Exigences, Cas d'utilisation, Contexte, Planning, Export PDF.
- **Diagrammes** : mis à jour en direct ; les éléments se déplacent à la souris ; « Réorganiser » rétablit la mise en page automatique.
- **Planning** : chaque élève dispose de 36 h (Première) ou 72 h (Terminale). Les tâches « Toute l'équipe » comptent pour chaque élève. Une alerte apparaît en cas de dépassement.
- **Sauvegarde** : automatique dans le navigateur (localStorage). « Exporter JSON » pour rendre le projet ou le reprendre sur un autre poste.
- **PDF** : onglet « Export PDF » → « Imprimer / Enregistrer en PDF » → imprimante « Enregistrer au format PDF », format A4.

Aucune donnée n'est envoyée sur Internet.

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

## Personnalisation

La liste des thématiques de Terminale, les spécialités, les domaines et les heures par niveau sont définis en tête du script de `index.html` (section « CONSTANTES »).
