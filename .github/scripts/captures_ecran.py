"""
Captures d'écran du site VALORIS PATRIMOINE (Playwright + Chromium).

Variables d'environnement :
  SITE_URL           URL de la page à capturer (obligatoire)
  OUT_DIR            dossier de sortie (défaut : captures)
  PAGE_NAME          préfixe des fichiers (défaut : homepage)
  SEUIL_PLEINE_PAGE  hauteur (px) au-delà de laquelle la page entière est assemblée
                     par segments au lieu d'une capture Chromium unique (défaut : 15000)
  CHROME_PATH        facultatif : chemin d'un Chromium local (tests hors GitHub Actions)

Fichiers produits dans OUT_DIR, pour chaque format (desktop 1440, tablet 768, mobile 390) :
  <PAGE_NAME>-<format>.png                  page entière, du haut jusqu'en bas
  <PAGE_NAME>-<format>-premier-ecran.png    premier écran, tel qu'il s'affiche à l'ouverture
  parts/<PAGE_NAME>-<format>-part-NN.png    la page entière découpée en tranches consécutives
et rapport.json (dimensions, méthode de capture, alertes, erreurs console, requêtes en échec).
"""
import io
import json
import os
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

SITE_URL = os.environ.get("SITE_URL", "").strip()
OUT_DIR = Path(os.environ.get("OUT_DIR", "captures"))
PAGE_NAME = os.environ.get("PAGE_NAME", "homepage")
SEUIL_PLEINE_PAGE = int(os.environ.get("SEUIL_PLEINE_PAGE", "15000"))
CHROME_PATH = os.environ.get("CHROME_PATH") or None

# Les images viennent de notre propre site : on lève la limite anti-« bombe » de Pillow,
# qui bloquerait les pages très longues (au-delà d'environ 89 millions de pixels).
Image.MAX_IMAGE_PIXELS = None

UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
UA_TABLETTE = ("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
               "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

# "tranche" = hauteur maximale de chaque tranche, en pixels.
FORMATS = [
    {"nom": "desktop", "viewport": {"width": 1440, "height": 900}, "is_mobile": False,
     "has_touch": False, "user_agent": None, "tranche": 1800},
    {"nom": "tablet", "viewport": {"width": 768, "height": 1024}, "is_mobile": True,
     "has_touch": True, "user_agent": UA_TABLETTE, "tranche": 2000},
    {"nom": "mobile", "viewport": {"width": 390, "height": 844}, "is_mobile": True,
     "has_touch": True, "user_agent": UA_MOBILE, "tranche": 1700},
]

# Gèle animations, transitions et curseur pour obtenir des images stables.
CSS_STABILITE = """
*, *::before, *::after {
  animation-duration: 0s !important; animation-delay: 0s !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0s !important; transition-delay: 0s !important;
  caret-color: transparent !important; scroll-behavior: auto !important;
}
html { scroll-behavior: auto !important; }
"""

# Force le chargement des images différées puis parcourt toute la page.
# Bornes : 300 pas et 45 s au maximum, même si la page s'allonge pendant le défilement.
JS_DECLENCHER_LAZY = """
async () => {
  const limite = Date.now() + 45000;
  document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
  document.querySelectorAll('img[data-src]').forEach(img => {
    if (!img.getAttribute('src')) { img.setAttribute('src', img.getAttribute('data-src')); }
  });
  document.querySelectorAll('img[data-srcset]').forEach(img => {
    if (!img.getAttribute('srcset')) { img.setAttribute('srcset', img.getAttribute('data-srcset')); }
  });
  const pas = Math.max(200, Math.floor(window.innerHeight * 0.8));
  let y = 0, n = 0;
  while (y < document.documentElement.scrollHeight && n < 300 && Date.now() < limite) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 120));
    y += pas; n++;
  }
  window.scrollTo(0, document.documentElement.scrollHeight);
  await new Promise(r => setTimeout(r, 300));
  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 300));
  return { pas: n, complet: y >= document.documentElement.scrollHeight };
}
"""

# Attend les polices (10 s max) puis les images (10 s max par image, 25 s au total).
JS_ATTENDRE_RESSOURCES = """
async () => {
  const delai = (ms) => new Promise(r => setTimeout(() => r('delai'), ms));
  let polices = 'ok';
  if (document.fonts && document.fonts.ready) {
    polices = await Promise.race([document.fonts.ready.then(() => 'ok'), delai(10000)]);
  }
  const imgs = Array.from(document.images);
  const chargement = Promise.all(imgs.map(img => img.complete ? Promise.resolve() : new Promise(r => {
    img.addEventListener('load', r, { once: true });
    img.addEventListener('error', r, { once: true });
    setTimeout(r, 10000);
  }))).then(() => Promise.all(imgs.map(img => img.decode ? img.decode().catch(() => {}) : null)))
     .then(() => 'ok');
  const images = await Promise.race([chargement, delai(25000)]);
  return {
    attentePolices: polices,
    attenteImages: images,
    polices: document.fonts
      ? Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight)
      : [],
    images: imgs.length,
    imagesEnErreur: imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.currentSrc || i.getAttribute('src'))
  };
}
"""

JS_DIAGNOSTIC = """
() => ({
  largeurFenetre: window.innerWidth,
  hauteurFenetre: window.innerHeight,
  largeurMiseEnPage: document.documentElement.clientWidth,
  largeurContenu: document.documentElement.scrollWidth,
  hauteurPage: Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0),
  debordementHorizontal: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  modeDocument: document.compatMode === 'CSS1Compat' ? 'standard' : 'quirks (doctype absent)',
  metaViewport: !!document.querySelector('meta[name="viewport"]'),
  titre: document.title
})
"""

# Masque les éléments en position fixe pour la capture pleine page :
# sinon Chromium les dessine au milieu de l'image, par-dessus le contenu.
JS_MASQUER_FIXES = """
() => {
  let n = 0;
  document.querySelectorAll('body *').forEach(el => {
    if (getComputedStyle(el).position === 'fixed') {
      el.style.setProperty('visibility', 'hidden', 'important');
      n++;
    }
  });
  return n;
}
"""

# Mode segments : un en-tête « sticky » se répéterait sur chaque segment.
# On le remet dans le flux normal ; il apparaît une seule fois, en haut, comme en capture native.
JS_FIGER_STICKY = """
() => {
  let n = 0;
  document.querySelectorAll('body *').forEach(el => {
    if (getComputedStyle(el).position === 'sticky') {
      el.style.setProperty('position', 'relative', 'important');
      el.style.setProperty('top', 'auto', 'important');
      n++;
    }
  });
  return n;
}
"""


def charger(page, url):
    """Chargement initial : délais courts et bornés, aucune attente bloquante."""
    page.goto(url, wait_until="load", timeout=60_000)
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        print("  réseau encore actif après 15 s : on continue")


def pleine_page_native(page, fichier):
    page.screenshot(path=str(fichier), full_page=True, animations="disabled", caret="hide", timeout=120_000)


def pleine_page_segments(page, fichier):
    """
    Assemble la page entière à partir de captures de l'écran, segment par segment.
    Contourne la limite de taille des textures de Chromium (environ 16 384 px) qui peut
    tronquer ou dupliquer le bas des captures pleine page très longues.
    Même résolution que la capture native : aucune perte de qualité.
    """
    page.evaluate(JS_FIGER_STICKY)
    page.wait_for_timeout(200)
    hauteur_css = page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)")
    vh = page.evaluate("() => window.innerHeight")
    segments, y, echelle = [], 0, None
    while y < hauteur_css:
        page.evaluate(f"() => window.scrollTo(0, {y})")
        page.wait_for_timeout(150)
        reel = page.evaluate("() => window.scrollY")
        img = Image.open(io.BytesIO(page.screenshot(full_page=False, animations="disabled", caret="hide")))
        img.load()
        if echelle is None:
            echelle = img.height / vh
        # En bas de page, le défilement s'arrête avant y : on retire la partie déjà capturée.
        decalage = round((y - reel) * echelle)
        if decalage > 0:
            img = img.crop((0, decalage, img.width, img.height))
        segments.append(img)
        y += vh
    page.evaluate("() => window.scrollTo(0, 0)")
    largeur = segments[0].width
    hauteur = min(sum(s.height for s in segments), round(hauteur_css * echelle))
    toile = Image.new("RGB", (largeur, hauteur), "white")
    pos = 0
    for s in segments:
        toile.paste(s.convert("RGB"), (0, pos))
        pos += s.height
    toile.save(fichier, optimize=True)


def decouper(fichier, fmt):
    """Découpe l'image pleine page en tranches consécutives : ni chevauchement, ni perte."""
    dossier = OUT_DIR / "parts"
    dossier.mkdir(parents=True, exist_ok=True)
    tranches = []
    with Image.open(fichier) as img:
        largeur, hauteur = img.size
        y, n = 0, 1
        while y < hauteur:
            bas = min(y + fmt["tranche"], hauteur)
            # Un reste inférieur au quart d'une tranche est rattaché à la tranche courante.
            if hauteur - bas < fmt["tranche"] // 4:
                bas = hauteur
            nom = f"{PAGE_NAME}-{fmt['nom']}-part-{n:02d}.png"
            img.crop((0, y, largeur, bas)).save(dossier / nom, optimize=True)
            tranches.append({"fichier": f"parts/{nom}", "de": y, "a": bas})
            y, n = bas, n + 1
    # Contrôle : la somme des hauteurs des tranches doit égaler la hauteur de la page.
    total = sum(t["a"] - t["de"] for t in tranches)
    if total != hauteur:
        raise RuntimeError(f"Tranches incohérentes pour {fmt['nom']} : {total} px au lieu de {hauteur} px")
    return largeur, hauteur, tranches


def capturer(navigateur, fmt, url):
    erreurs_console, requetes_echouees = [], []
    contexte = navigateur.new_context(
        viewport=fmt["viewport"], device_scale_factor=1, is_mobile=fmt["is_mobile"],
        has_touch=fmt["has_touch"], user_agent=fmt["user_agent"], reduced_motion="reduce",
        locale="fr-FR", timezone_id="Europe/Paris", color_scheme="light",
    )
    try:
        page = contexte.new_page()
        page.set_default_timeout(30_000)
        page.on("console", lambda m: erreurs_console.append(m.text) if m.type == "error" else None)
        page.on("requestfailed", lambda r: requetes_echouees.append(f"{r.url} ({r.failure})"))

        charger(page, url)
        page.add_style_tag(content=CSS_STABILITE)
        defilement = page.evaluate(JS_DECLENCHER_LAZY)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass
        ressources = page.evaluate(JS_ATTENDRE_RESSOURCES)
        ressources["defilement"] = defilement
        page.wait_for_timeout(800)
        diag = page.evaluate(JS_DIAGNOSTIC)

        # 1) Premier écran, éléments fixes compris (barre d'action mobile, en-tête).
        ecran1 = OUT_DIR / f"{PAGE_NAME}-{fmt['nom']}-premier-ecran.png"
        page.screenshot(path=str(ecran1), full_page=False, animations="disabled", caret="hide")

        # 2) Page entière, éléments fixes masqués.
        nb_fixes = page.evaluate(JS_MASQUER_FIXES)
        fichier = OUT_DIR / f"{PAGE_NAME}-{fmt['nom']}.png"
        if diag["hauteurPage"] <= SEUIL_PLEINE_PAGE:
            methode = "capture Chromium pleine page"
            pleine_page_native(page, fichier)
        else:
            methode = f"assemblage par segments (page de plus de {SEUIL_PLEINE_PAGE} px)"
            pleine_page_segments(page, fichier)
    finally:
        contexte.close()

    # 3) Tranches découpées dans l'image pleine page.
    largeur, hauteur, tranches = decouper(fichier, fmt)

    return {
        "format": fmt["nom"],
        "fichier": fichier.name,
        "premierEcran": ecran1.name,
        "largeurViewport": fmt["viewport"]["width"],
        "largeurImage": largeur,
        "hauteurImage": hauteur,
        "tailleOctets": fichier.stat().st_size,
        "methodePleinePage": methode,
        "tranches": [t["fichier"] for t in tranches],
        "tranchesPixels": tranches,
        "elementsFixesMasquesPleinePage": nb_fixes,
        "diagnostic": diag,
        "ressources": ressources,
        "erreursConsole": erreurs_console,
        "requetesEchouees": requetes_echouees,
    }


def alertes_pour(r, fmt):
    alertes = []
    if r["largeurImage"] != fmt["viewport"]["width"]:
        alertes.append(f"Mise en page de {r['largeurImage']} px au lieu de {fmt['viewport']['width']} px : "
                       "sur un vrai appareil, la page s'affiche réduite (balise meta viewport absente ?).")
    if not r["diagnostic"]["metaViewport"]:
        alertes.append("Balise <meta name=\"viewport\"> absente.")
    if r["diagnostic"]["modeDocument"] != "standard":
        alertes.append("Déclaration <!doctype html> absente : le navigateur affiche la page "
                       "en mode de compatibilité (quirks).")
    if r["diagnostic"]["debordementHorizontal"]:
        alertes.append("Débordement horizontal : la page défile sur le côté.")
    if r["ressources"]["imagesEnErreur"]:
        alertes.append(f"{len(r['ressources']['imagesEnErreur'])} image(s) non chargée(s).")
    if r["ressources"]["attentePolices"] != "ok":
        alertes.append("Polices non chargées après 10 s : la capture peut utiliser des polices de secours.")
    if r["ressources"]["attenteImages"] != "ok":
        alertes.append("Images encore en chargement après 25 s : certaines peuvent manquer.")
    if not r["ressources"]["defilement"]["complet"]:
        alertes.append("Défilement interrompu (page très longue ou qui s'allonge) : "
                       "des éléments différés en bas de page peuvent manquer.")
    return alertes


def main():
    if not SITE_URL:
        sys.exit("SITE_URL manquante")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resultats = []
    with sync_playwright() as p:
        navigateur = p.chromium.launch(executable_path=CHROME_PATH) if CHROME_PATH else p.chromium.launch()
        try:
            for fmt in FORMATS:
                r = None
                for essai in (1, 2):
                    try:
                        r = capturer(navigateur, fmt, SITE_URL)
                        break
                    except Exception as exc:
                        if essai == 2:
                            raise
                        print(f"[{fmt['nom']}] nouvel essai dans 10 s après l'erreur : {exc}")
                        time.sleep(10)
                if r["tailleOctets"] < 5_000 or r["hauteurImage"] < 100:
                    sys.exit(f"Capture {fmt['nom']} invalide : {r['largeurImage']}x{r['hauteurImage']} px, "
                             f"{r['tailleOctets']} octets")
                r["alertes"] = alertes_pour(r, fmt)
                for a in r["alertes"]:
                    print(f"::warning title=Capture {fmt['nom']}::{a}")
                print(f"[{fmt['nom']}] {r['largeurImage']}x{r['hauteurImage']} px, "
                      f"{len(r['tranches'])} tranche(s), {r['methodePleinePage']}, "
                      f"mode {r['diagnostic']['modeDocument']}")
                resultats.append(r)
        finally:
            navigateur.close()

    # Contrôle final : les trois formats et tous les fichiers annoncés existent.
    formats = {r["format"] for r in resultats}
    if formats != {"desktop", "tablet", "mobile"}:
        sys.exit(f"Formats manquants : {sorted({'desktop', 'tablet', 'mobile'} - formats)}")
    attendus = []
    for r in resultats:
        attendus += [r["fichier"], r["premierEcran"], *r["tranches"]]
    manquants = [f for f in attendus if not (OUT_DIR / f).is_file()]
    if manquants:
        sys.exit(f"Fichiers manquants : {manquants}")

    rapport = {"url": SITE_URL, "dateUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "captures": resultats}
    (OUT_DIR / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(attendus)} images et rapport.json écrits dans {OUT_DIR}")


if __name__ == "__main__":
    main()
