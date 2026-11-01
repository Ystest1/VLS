# Thème WordPress VALORIS PATRIMOINE — guide rapide

Thème bloc léger, sans extension ni constructeur de pages. WordPress 6.6 ou plus récent (testé avec 7.1.4), PHP 7.4 ou plus récent.

## 1. Installation

1. Dans WordPress : **Apparence → Thèmes → Ajouter → Téléverser un thème**, choisir `valoris-patrimoine.zip`, puis **Installer** et **Activer**.
2. Sur un site neuf, l'activation crée automatiquement la page **« Accueil »** avec toutes les sections et la définit comme page d'accueil.
   Sur un site qui a déjà une page d'accueil statique, rien n'est modifié : créez une page, choisissez la composition **« Page d'accueil complète »**, puis **Réglages → Lecture → Une page statique**.
3. **Réglages → Permaliens** : choisir **« Titre de la publication »** (adresses du type `/proprietaires/`).
4. Pendant la construction : **Réglages → Lecture → « Demander aux moteurs de recherche de ne pas indexer ce site »**.

## 2. Modifier les contenus (sans code)

| Ce que l'on modifie | Où |
|---|---|
| Textes, titres, listes, FAQ, boutons de la page d'accueil | **Pages → Accueil** : cliquer dans le texte et écrire |
| Lien d'un bouton | Cliquer sur le bouton → icône de lien |
| Image du premier écran | Cliquer sur l'illustration → **Remplacer** ; supprimer ou modifier la légende (étiquette sombre) |
| Menu, logo, bouton de l'en-tête | **Apparence → Éditeur → Parties de modèle → En-tête** |
| Pied de page, coordonnées du pied de page, barre mobile (Appeler / WhatsApp / Étudier mon logement) | **Apparence → Éditeur → Parties de modèle → Pied de page et barre mobile** |
| Logo définitif | Cliquer sur le logo (en-tête et pied de page) → **Remplacer** |
| Couleurs et polices du site | **Apparence → Éditeur → Styles** |

Numéros de téléphone : dans la barre mobile, le lien du bouton « Appeler » s'écrit `tel:+33612345678`, celui de « WhatsApp » `https://wa.me/33612345678`.

Coordonnées présentes à plusieurs endroits (section « Appel final » de l'accueil et pied de page) : les modifier aux deux endroits, ou transformer le bloc en **composition synchronisée** (sélectionner le bloc → ⋮ → **Créer une composition**, option synchronisée) pour ne les modifier qu'une fois.

## 3. Créer une nouvelle page

- **Page composée de sections** (comme l'accueil) : créer la page, choisir le modèle **« Page en sections (sans titre) »** dans le panneau de droite, puis insérer les sections depuis l'outil **+ → Compositions → VALORIS PATRIMOINE**.
- **Page simple** (mentions légales, confidentialité…) : modèle par défaut **« Page »** ; le titre s'affiche en haut et l'on écrit directement le texte.

Sections disponibles : premier écran, fonctionnement, avantages, profils, étapes, entreprises, société, FAQ, appel final, section de texte (fond clair ou beige).

## 4. Règles à respecter (sinon une petite intervention dans le code sera nécessaire)

- Ne pas retirer les **classes CSS** des sections (panneau **Avancé → Classe(s) CSS additionnelle(s)**, par ex. `vp-hero`, `vp-section`, `vp-noeud`). Dupliquer une section ou modifier son contenu ne pose aucun problème.
- Les trois styles de bouton se choisissent dans le panneau **Styles** du bloc Bouton : par défaut (bleu nuit), **Secondaire**, **Champagne** et **Contour clair** (ces deux derniers pour les fonds bleu nuit).
- Les seuils mobile / tablette / ordinateur sont fixés dans le code (`assets/css/valoris.css`).
- La barre mobile se replie tant que les boutons du premier écran sont visibles : ce bloc Boutons doit garder la classe `vp-actions`.

## 5. Contenu du thème

```
style.css            identité du thème
theme.json           couleurs, polices, tailles, largeurs (réglables dans Styles)
functions.php        chargement des styles et du script, styles de boutons, création de l'accueil
assets/css/          styles des sections (repris de la maquette V3)
assets/js/           barre mobile (12 lignes)
assets/fonts/        Playfair Display, Bodoni Moda, Hanken Grotesk (WOFF2, licence SIL OFL 1.1)
assets/images/       logo provisoire (SVG) et illustration provisoire
templates/, parts/   gabarits et parties de modèle
patterns/            une composition par section
```

Aucune police ni aucun script n'est chargé depuis un site externe.
