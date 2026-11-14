#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serveur local des projets STI2D
===============================

© 2026 H. Hammadou – Tous droits réservés.
Toute reproduction, modification ou redistribution sans l'accord de l'auteur est interdite.

Petit serveur à lancer sur le PC du professeur. Il utilise uniquement la
bibliothèque standard de Python 3 (aucune installation nécessaire).

Il permet :
  * de servir l'application (index.html) aux postes élèves du réseau du lycée ;
  * de recevoir les projets JSON envoyés par les équipes (bouton
    « Envoyer au professeur » dans l'application) et de les ranger dans un dossier ;
  * d'afficher une page professeur listant tous les projets reçus.

Aucune donnée n'est envoyée sur Internet : tout reste sur ce PC.

Utilisation :
    python3 serveur.py                       (port 8000, dossier « projets_recus »)
    python3 serveur.py --port 8080 --mot-de-passe secret --dossier D:\\Projets

Puis, sur les postes élèves : http://<adresse-du-PC>:8000/
Page professeur            : http://<adresse-du-PC>:8000/prof
"""

import argparse
import base64
import datetime
import hmac
import html
import json
import re
import socket
import sys
import threading
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

# --------------------------------------------------------------------------
# Paramètres
# --------------------------------------------------------------------------
DOSSIER_APP = Path(__file__).resolve().parent
FICHIER_APP = DOSSIER_APP / "index.html"
APP_ID = "sti2d-projets"              # identifiant présent dans les fichiers JSON de l'application
NIVEAUX = {"premiere": "Première STI2D", "terminale": "Terminale 2I2D"}
HEURES = {"premiere": 36, "terminale": 72}
TAILLE_MAX = 3 * 1024 * 1024          # taille maximale d'un projet envoyé (3 Mo)
VERROU = threading.Lock()             # évite que deux envois simultanés écrivent le même fichier

CONFIG = {"dossier": None, "mot_de_passe": None}

# Fichiers annexes servis tels quels (liste fermée : aucun autre fichier n'est accessible)
FICHIERS_STATIQUES = {
    "/manifest.webmanifest": "application/manifest+json",
    "/sw.js": "text/javascript; charset=utf-8",
    "/icones/icone.svg": "image/svg+xml",
    "/icones/icone-192.png": "image/png",
    "/icones/icone-512.png": "image/png",
    "/icones/icone-maskable-512.png": "image/png",
    "/icones/apple-touch-icon.png": "image/png",
}


# --------------------------------------------------------------------------
# Outils
# --------------------------------------------------------------------------
def slug(texte, longueur=50):
    """Transforme un texte en nom de fichier sûr (sans accents ni caractères spéciaux)."""
    t = unicodedata.normalize("NFD", str(texte or "")).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:longueur] or "sans-nom"


def nom_fichier_valide(nom):
    """Vérifie qu'un nom de fichier demandé ne permet pas de sortir du dossier des projets."""
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,150}\.json", nom)) and ".." not in nom


def adresses_locales():
    """Adresses IP de ce PC sur le réseau local (pour les afficher au démarrage).
    Le « connect » UDP n'envoie aucun paquet : il sert seulement à connaître l'interface réseau."""
    adresses = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        adresses.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            adresses.add(info[4][0])
    except OSError:
        pass
    adresses.discard("127.0.0.1")
    return sorted(adresses) or ["127.0.0.1"]


def bilan_heures(projet):
    """Renvoie la liste des élèves qui dépassent le nombre d'heures prévu (même règle que l'application)."""
    limite = HEURES.get(projet.get("niveau"), 0)
    taches = projet.get("taches") or []

    def duree(t):
        try:
            return float(str(t.get("duree", 0)).replace(",", "."))
        except (TypeError, ValueError):
            return 0.0

    equipe = sum(duree(t) for t in taches if t.get("responsable") == "equipe")
    depassements = []
    for e in projet.get("eleves") or []:
        h = equipe + sum(duree(t) for t in taches if t.get("responsable") == e.get("uid"))
        if h > limite + 1e-9:
            depassements.append(f"{e.get('nom') or 'élève'} ({h:g} h)")
    return depassements


def lire_projets():
    """Lit tous les projets reçus et renvoie leurs informations principales."""
    projets = []
    for f in sorted(CONFIG["dossier"].glob("*.json")):
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        fiche = p.get("fiche") or {}
        projets.append({
            "fichier": f.name,
            "equipe": (p.get("envoi") or {}).get("equipe", ""),
            "niveau": p.get("niveau", ""),
            "intitule": fiche.get("intitule", ""),
            "eleves": [e.get("nom", "") for e in (p.get("eleves") or []) if e.get("nom")],
            "nb_exigences": len(p.get("exigences") or []),
            "nb_taches": len(p.get("taches") or []),
            "depassements": bilan_heures(p),
            "recu": datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y %H:%M"),
            "recu_tri": f.stat().st_mtime,
        })
    projets.sort(key=lambda x: x["recu_tri"], reverse=True)
    return projets


# --------------------------------------------------------------------------
# Page professeur (HTML généré par le serveur)
# --------------------------------------------------------------------------
def page_professeur():
    projets = lire_projets()
    e = html.escape
    lignes = []
    for p in projets:
        alerte = (f'<span class="ko">⚠ {e(", ".join(p["depassements"]))}</span>'
                  if p["depassements"] else '<span class="ok">✓</span>')
        lignes.append(f"""<tr>
          <td><b>{e(p['equipe'] or '—')}</b></td>
          <td>{e(NIVEAUX.get(p['niveau'], p['niveau']))}</td>
          <td>{e(p['intitule'] or 'Sans titre')}</td>
          <td>{e(', '.join(p['eleves']) or '—')}</td>
          <td class="c">{p['nb_exigences']}</td>
          <td class="c">{p['nb_taches']}</td>
          <td>{alerte}</td>
          <td>{e(p['recu'])}</td>
          <td class="actions"><a class="btn" href="./?projet={quote(p['fichier'])}" target="_blank">Ouvrir</a>
              <a class="btn sec" href="api/projets/{quote(p['fichier'])}" download>JSON</a></td>
        </tr>""")
    corps = "".join(lignes) or '<tr><td colspan="9" class="vide">Aucun projet reçu pour le moment.</td></tr>'
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Projets reçus</title>
<style>
:root{{--bg:#f3f5f9;--surface:#fff;--text:#1a2230;--muted:#5a6578;--border:#d3dae5;--primary:#1d5fc4;--ink:#fff;--ok:#23793a;--ko:#c0262d;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0f141b;--surface:#18202a;--text:#e5eaf1;--muted:#98a4b6;--border:#313b49;--primary:#6ea6ff;--ink:#0a1220;--ok:#72cf7f;--ko:#ff7d7d;color-scheme:dark}}}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,"Segoe UI",Roboto,Arial,sans-serif}}
main{{max-width:1300px;margin:0 auto;padding:1.5rem 1rem 3rem}}
h1{{margin:0 0 .3rem}} p{{color:var(--muted);margin:.2rem 0 1rem}}
.carte{{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow-x:auto}}
table{{width:100%;border-collapse:collapse}} th,td{{padding:.55rem .7rem;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}}
th{{font-size:.8rem;text-transform:uppercase;color:var(--muted)}} td.c{{text-align:center}} td.vide{{text-align:center;color:var(--muted);padding:2rem}}
.ok{{color:var(--ok);font-weight:700}} .ko{{color:var(--ko);font-weight:600}}
.actions{{white-space:nowrap}}
.btn{{display:inline-block;padding:.3rem .7rem;border-radius:7px;background:var(--primary);color:var(--ink);text-decoration:none;font-weight:600;font-size:.88rem;border:1px solid var(--primary)}}
.btn.sec{{background:transparent;color:var(--primary);border-color:var(--border)}}
.barre{{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-bottom:1rem}} .barre p{{flex:1;margin:0}}
</style></head><body><main>
<h1>Projets reçus</h1>
<div class="barre"><p>{len(projets)} projet(s) dans le dossier <code>{e(str(CONFIG['dossier']))}</code>.
« Ouvrir » charge le projet dans l'application (onglet Export PDF pour l'imprimer).</p>
<a class="btn sec" href="prof">↻ Actualiser</a> <a class="btn sec" href="./">Application</a></div>
<div class="carte"><table>
<thead><tr><th>Équipe</th><th>Niveau</th><th>Intitulé</th><th>Élèves</th><th>Exigences</th><th>Tâches</th><th>Heures</th><th>Reçu le</th><th></th></tr></thead>
<tbody>{corps}</tbody></table></div>
<p style="text-align:center;font-size:.8rem">© 2026 H. Hammadou – Tous droits réservés</p>
</main></body></html>"""


# --------------------------------------------------------------------------
# Gestion des requêtes HTTP
# --------------------------------------------------------------------------
class Gestionnaire(BaseHTTPRequestHandler):
    server_version = "ServeurProjetsSTI2D/1.0"

    # ----- réponses -----
    def envoyer(self, code, contenu, type_mime="text/html; charset=utf-8", entetes=None):
        donnees = contenu.encode("utf-8") if isinstance(contenu, str) else contenu
        self.send_response(code)
        self.send_header("Content-Type", type_mime)
        self.send_header("Content-Length", str(len(donnees)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (entetes or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(donnees)

    def json(self, code, objet):
        self.envoyer(code, json.dumps(objet, ensure_ascii=False), "application/json; charset=utf-8")

    def autorise_prof(self):
        """Protection facultative des pages professeur par mot de passe (authentification HTTP « Basic »)."""
        mdp = CONFIG["mot_de_passe"]
        if not mdp:
            return True
        entete = self.headers.get("Authorization", "")
        if entete.startswith("Basic "):
            try:
                _, _, essai = base64.b64decode(entete[6:]).decode("utf-8").partition(":")
                if hmac.compare_digest(essai, mdp):
                    return True
            except (ValueError, UnicodeDecodeError):
                pass
        self.envoyer(401, "<h1>Accès réservé au professeur</h1>",
                     entetes={"WWW-Authenticate": 'Basic realm="Projets STI2D - professeur", charset="UTF-8"'})
        return False

    # ----- GET -----
    def do_GET(self):
        chemin = unquote(urlparse(self.path).path)
        if chemin in ("/", "/index.html"):
            try:
                self.envoyer(200, FICHIER_APP.read_bytes())
            except OSError:
                self.envoyer(500, "<h1>index.html introuvable à côté de serveur.py</h1>")
        elif chemin == "/api/ping":
            self.json(200, {"ok": True, "serveur": APP_ID})
        elif chemin in ("/prof", "/prof/"):
            if self.autorise_prof():
                self.envoyer(200, page_professeur())
        elif chemin == "/api/projets":
            if self.autorise_prof():
                projets = lire_projets()
                for p in projets:
                    p.pop("recu_tri", None)
                self.json(200, projets)
        elif chemin.startswith("/api/projets/"):
            if not self.autorise_prof():
                return
            nom = chemin[len("/api/projets/"):]
            fichier = CONFIG["dossier"] / nom
            if not nom_fichier_valide(nom) or not fichier.is_file():
                self.json(404, {"ok": False, "erreur": "Projet introuvable"})
                return
            self.envoyer(200, fichier.read_bytes(), "application/json; charset=utf-8",
                         {"Content-Disposition": f'attachment; filename="{nom}"'})
        elif chemin in FICHIERS_STATIQUES:
            # Fichiers de l'installation sur tablette (manifeste, service worker, icônes)
            fichier = DOSSIER_APP / chemin.lstrip("/")
            if fichier.is_file():
                self.envoyer(200, fichier.read_bytes(), FICHIERS_STATIQUES[chemin])
            else:
                self.envoyer(404, "<h1>Fichier introuvable</h1>")
        elif chemin == "/favicon.ico":
            self.envoyer(204, b"")
        else:
            self.envoyer(404, "<h1>Page introuvable</h1><p><a href='/'>Retour à l'application</a></p>")

    do_HEAD = do_GET

    # ----- POST : réception d'un projet envoyé par une équipe -----
    def do_POST(self):
        if urlparse(self.path).path != "/api/projets":
            self.json(404, {"ok": False, "erreur": "Adresse inconnue"})
            return
        try:
            taille = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            taille = 0
        if taille <= 0 or taille > TAILLE_MAX:
            self.json(413, {"ok": False, "erreur": "Projet vide ou trop volumineux (3 Mo maximum)"})
            return
        try:
            projet = json.loads(self.rfile.read(taille).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self.json(400, {"ok": False, "erreur": "Le contenu reçu n'est pas un JSON valide"})
            return
        if not isinstance(projet, dict) or projet.get("app") != APP_ID or projet.get("niveau") not in NIVEAUX:
            self.json(400, {"ok": False, "erreur": "Ce fichier n'est pas un projet de l'application STI2D"})
            return

        equipe = str((projet.get("envoi") or {}).get("equipe", ""))
        intitule = str((projet.get("fiche") or {}).get("intitule", ""))
        # Un fichier par équipe et par projet : un nouvel envoi remplace le précédent,
        # l'ancienne version est conservée dans le sous-dossier « historique ».
        nom = f"{projet['niveau']}_{slug(equipe, 40)}_{slug(intitule, 50)}.json"
        dossier = CONFIG["dossier"]
        cible = dossier / nom
        contenu = json.dumps(projet, ensure_ascii=False, indent=2)
        with VERROU:
            if cible.exists():
                hist = dossier / "historique"
                hist.mkdir(exist_ok=True)
                horodatage = datetime.datetime.fromtimestamp(cible.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
                cible.replace(hist / f"{cible.stem}_{horodatage}.json")
            temporaire = cible.with_suffix(".tmp")
            temporaire.write_text(contenu, encoding="utf-8")
            temporaire.replace(cible)
        self.log_message("Projet reçu : %s (%s)", nom, equipe)
        self.json(200, {"ok": True, "fichier": nom})

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s - %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"),
                                             self.client_address[0], fmt % args))


# --------------------------------------------------------------------------
# Lancement
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Serveur local des projets STI2D (réseau du lycée).")
    parser.add_argument("--port", type=int, default=8000, help="port d'écoute (8000 par défaut)")
    parser.add_argument("--dossier", default=str(DOSSIER_APP / "projets_recus"),
                        help="dossier où ranger les projets reçus")
    parser.add_argument("--mot-de-passe", default=None,
                        help="mot de passe de la page professeur (fortement conseillé)")
    parser.add_argument("--local", action="store_true",
                        help="n'accepter que les connexions depuis ce PC (tests)")
    args = parser.parse_args()

    CONFIG["dossier"] = Path(args.dossier).resolve()
    CONFIG["dossier"].mkdir(parents=True, exist_ok=True)
    CONFIG["mot_de_passe"] = args.mot_de_passe

    if not FICHIER_APP.is_file():
        print(f"ERREUR : {FICHIER_APP} est introuvable. Placez serveur.py à côté de index.html.")
        sys.exit(1)

    hote = "127.0.0.1" if args.local else "0.0.0.0"
    try:
        serveur = ThreadingHTTPServer((hote, args.port), Gestionnaire)
    except OSError as e:
        print(f"ERREUR : impossible d'utiliser le port {args.port} ({e}). Essayez --port 8080.")
        sys.exit(1)

    print("=" * 64)
    print(" Serveur des projets STI2D démarré")
    print("=" * 64)
    adresses = ["127.0.0.1"] if args.local else adresses_locales()
    for a in adresses:
        print(f"  Application (élèves) : http://{a}:{args.port}/")
    print(f"  Page professeur      : http://{adresses[0]}:{args.port}/prof")
    print(f"  Projets enregistrés dans : {CONFIG['dossier']}")
    if not args.mot_de_passe:
        print("  ⚠ Page professeur sans mot de passe : relancez avec --mot-de-passe pour la protéger.")
    print("  (Ctrl+C pour arrêter)")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
    finally:
        serveur.server_close()


if __name__ == "__main__":
    main()
