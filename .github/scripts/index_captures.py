"""
Génère README.md et latest.json à la racine de la branche « screenshots ».

Variables d'environnement obligatoires :
  PUB_DIR       dossier de travail de la branche screenshots
  RAW_BASE      https://raw.githubusercontent.com/<propriétaire>/<dépôt>/screenshots
  ARBO_BASE     https://github.com/<propriétaire>/<dépôt>/tree/screenshots
  HISTO         dossier d'historique de cette version (ex. 2026-10-31_173512_dab2414)
  COMMIT_SITE   SHA du commit du site capturé
  SITE_URL      URL capturée
Variables facultatives :
  SITE_A_JOUR   "oui" uniquement si la version en ligne a été confirmée de façon fiable
  SITE_METHODE  méthode ayant permis (ou non) cette confirmation
"""
import json
import os
import sys
from pathlib import Path

FORMATS_REQUIS = ("desktop", "mobile", "tablet")
NOMS = {"desktop": "Ordinateur (1440 px)", "mobile": "Mobile (390 px)", "tablet": "Tablette (768 px)"}

REQUISES = ["PUB_DIR", "RAW_BASE", "ARBO_BASE", "HISTO", "COMMIT_SITE", "SITE_URL"]
manquantes = [v for v in REQUISES if not os.environ.get(v)]
if manquantes:
    sys.exit(f"Variables d'environnement manquantes : {', '.join(manquantes)}")

pub = Path(os.environ["PUB_DIR"])
raw = os.environ["RAW_BASE"].rstrip("/")
arbo = os.environ["ARBO_BASE"].rstrip("/")
histo = os.environ["HISTO"]
commit = os.environ["COMMIT_SITE"]
site = os.environ["SITE_URL"]
a_jour = os.environ.get("SITE_A_JOUR", "non") == "oui"
methode = os.environ.get("SITE_METHODE", "non précisée")

rapport_fichier = pub / "screenshots" / "rapport.json"
if not rapport_fichier.is_file():
    sys.exit("screenshots/rapport.json introuvable")
rapport = json.loads(rapport_fichier.read_text(encoding="utf-8"))
captures = {c["format"]: c for c in rapport.get("captures", [])}

# Les trois formats sont obligatoires.
absents = [f for f in FORMATS_REQUIS if f not in captures]
if absents:
    sys.exit(f"Format(s) de capture manquant(s) dans rapport.json : {', '.join(absents)}. "
             "Publication annulée.")

# Contrôle de cohérence : chaque fichier cité doit exister dans screenshots/ et dans history/.
for f in FORMATS_REQUIS:
    c = captures[f]
    if not c.get("tranches"):
        sys.exit(f"Aucune tranche pour le format {f}")
    for nom in [c["fichier"], c["premierEcran"], *c["tranches"]]:
        if not (pub / "screenshots" / nom).is_file():
            sys.exit(f"Fichier introuvable dans screenshots/ : {nom}")
    for nom in [c["fichier"], c["premierEcran"]]:
        if not (pub / "history" / histo / nom).is_file():
            sys.exit(f"Fichier introuvable dans history/{histo}/ : {nom}")
if not (pub / "history" / histo / "rapport.json").is_file():
    sys.exit(f"Fichier introuvable : history/{histo}/rapport.json")


def liens(fmt):
    c = captures[fmt]
    return {
        "pageEntiere": f"{raw}/screenshots/{c['fichier']}",
        "premierEcran": f"{raw}/screenshots/{c['premierEcran']}",
        "tranches": [f"{raw}/screenshots/{t}" for t in c["tranches"]],
        "pageEntiereVersionFigee": f"{raw}/history/{histo}/{c['fichier']}",
        "premierEcranVersionFigee": f"{raw}/history/{histo}/{c['premierEcran']}",
        "dimensions": f"{c['largeurImage']} x {c['hauteurImage']} px",
        "methodePleinePage": c.get("methodePleinePage", ""),
        "alertes": c.get("alertes", []),
    }


latest = {
    "site": site,
    "commitDuSite": commit,
    "dateUTC": rapport["dateUTC"],
    "versionEnLigneConfirmee": a_jour,
    "methodeConfirmation": methode,
    "rapport": f"{raw}/screenshots/rapport.json",
    "rapportVersionFigee": f"{raw}/history/{histo}/rapport.json",
    "historique": f"{arbo}/history/{histo}",
    "captures": {f: liens(f) for f in FORMATS_REQUIS},
}
(pub / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")

lignes = [
    "# Captures d'écran - VALORIS PATRIMOINE",
    "",
    "Fichiers générés automatiquement à chaque mise à jour du site. Ne pas modifier cette branche à la main.",
    "",
    f"- Site capturé : {site}",
    f"- Commit du site : `{commit[:7]}`",
    f"- Date (UTC) : {rapport['dateUTC']}",
    "- Version en ligne confirmée identique au commit : "
    + ("**oui**" if a_jour else "**non** (voir le journal du workflow)"),
    f"- Méthode de vérification : {methode}",
    f"- Rapport technique : {raw}/screenshots/rapport.json",
    "",
    "## Liens permanents (toujours la dernière version)",
    "",
]
for f in FORMATS_REQUIS:
    x = liens(f)
    lignes += [
        f"### {NOMS[f]}",
        "",
        f"- Page entière : {x['pageEntiere']}",
        f"- Premier écran : {x['premierEcran']}",
        "- Tranches : " + " | ".join(f"[{i + 1}]({u})" for i, u in enumerate(x["tranches"])),
        f"- Dimensions : {x['dimensions']} ({x['methodePleinePage']})",
    ]
    lignes += [f"- Attention : {a}" for a in x["alertes"]]
    lignes.append("")
lignes += [
    "## Version figée de cette capture",
    "",
    f"Dossier : {arbo}/history/{histo}",
    "",
    "Les liens de l'historique ne changent jamais : ils servent à comparer deux versions.",
    "Les liens permanents peuvent mettre jusqu'à 5 minutes à refléter la dernière capture (cache de GitHub).",
    "",
    "## Aperçu",
    "",
]
for f in FORMATS_REQUIS:
    lignes += [f"**{NOMS[f]} - premier écran**", "", f"![{NOMS[f]}](screenshots/{captures[f]['premierEcran']})", ""]
(pub / "README.md").write_text("\n".join(lignes), encoding="utf-8")
print("README.md et latest.json écrits")
