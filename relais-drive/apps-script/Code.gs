/**
 * Relais Drive — version Google Apps Script (sans Google Cloud Console).
 *
 * À coller dans un projet sur script.google.com (fichier « Code.gs »),
 * avec le fichier « Page.html » à côté. Voir LISEZMOI.md.
 *
 * Le .zip est décompressé sur la tablette (dans la page), puis chaque fichier
 * est envoyé ici et rangé dans : Mon Drive / Relais tablette / <nom du zip> / …
 */

// Nom du dossier principal créé à la racine du Drive
const RACINE = 'Relais tablette';

// Taille maximale d'un fichier (limite d'Apps Script : 50 Mo)
const TAILLE_MAX = 40 * 1024 * 1024;

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Page')
    .setTitle('Relais Drive')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function dossierRacine_() {
  const racineDrive = DriveApp.getRootFolder();
  const it = racineDrive.getFoldersByName(RACINE);
  return it.hasNext() ? it.next() : racineDrive.createFolder(RACINE);
}

function sousDossier_(parent, nom) {
  const it = parent.getFoldersByName(nom);
  return it.hasNext() ? it.next() : parent.createFolder(nom);
}

/**
 * Crée le dossier d'un lot (sans écraser : « nom (2) » si besoin)
 * et tous ses sous-dossiers. Renvoie les identifiants pour l'envoi des fichiers.
 * @param {string} nom      nom souhaité du dossier
 * @param {string[]} chemins sous-dossiers, par ex. ["plans", "plans/vues"]
 */
function preparerLot(nom, chemins) {
  const racine = dossierRacine_();
  nom = String(nom || '').replace(/[\/\\]/g, '-').trim() || 'Envoi';
  let final = nom;
  for (let i = 2; racine.getFoldersByName(final).hasNext(); i++) final = nom + ' (' + i + ')';
  const dossier = racine.createFolder(final);

  const objets = { '': dossier };
  const ids = { '': dossier.getId() };
  // Du moins profond au plus profond, pour que le parent existe toujours
  const tries = (chemins || []).filter(String).sort(function (a, b) {
    return a.split('/').length - b.split('/').length;
  });
  tries.forEach(function (c) {
    if (objets[c]) return;
    const parties = c.split('/');
    const nomSous = parties.pop();
    const parent = objets[parties.join('/')] || dossier;
    objets[c] = sousDossier_(parent, nomSous);
    ids[c] = objets[c].getId();
  });
  return { url: dossier.getUrl(), nom: final, racine: RACINE, dossiers: ids };
}

/**
 * Enregistre un fichier dans un dossier.
 * @param {string} dossierId identifiant renvoyé par preparerLot
 * @param {string} nom       nom du fichier
 * @param {string} type      type MIME (peut être vide)
 * @param {string} base64    contenu encodé en base64
 */
function envoyerFichier(dossierId, nom, type, base64) {
  const octets = Utilities.base64Decode(base64);
  if (octets.length > TAILLE_MAX) throw new Error('Fichier trop gros (40 Mo maximum)');
  const blob = Utilities.newBlob(octets, type || 'application/octet-stream', nom);
  DriveApp.getFolderById(dossierId).createFile(blob);
  return true;
}
