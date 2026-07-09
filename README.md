# Site statique — Michele Rizzello

CV / portfolio statique servi par **GitHub Pages** sous le domaine
[`michele.rizzello.me`](https://michele.rizzello.me).

Aucune dépendance, aucun serveur, aucun build côté client : la page est
**pré-générée en local** (Python) puis servie telle quelle.

## Structure

```
.
├── index.html          # page générée (ne pas éditer à la main → régénérée par build.py)
├── CNAME               # domaine personnalisé (GitHub Pages)
├── css/style.css       # styles autonomes, responsives
├── js/
│   ├── timeline.js     # génère la chronologie SVG depuis data/site.json (au chargement)
│   └── main.js         # bouton « retour en haut »
├── data/site.json      # SOURCE DE VÉRITÉ des contenus (expériences, formations, projets…)
├── assets/             # photo, drapeau, icônes, images des projets, favicon
├── _build/build.py     # générateur : data/site.json -> index.html (dev only, non publié)
└── README.md
```

## Flux de travail (éditer → publier)

1. Modifier le contenu dans **`data/site.json`** (ou, ponctuellement, `index.html`).
2. Régénérer la page :

   ```bash
   python3 _build/build.py     # data/site.json -> index.html
   ```

   > La Timeline n'a pas besoin d'être régénérée : `js/timeline.js` la
   > (re)construit à chaque chargement de page à partir de `data/site.json`.
3. Committer puis pousser. GitHub Pages sert automatiquement la nouvelle version.

   ```bash
   git add -A && git commit -m "maj contenu" && git push
   ```

## Test local

`index.html` charge `data/site.json` via `fetch()`, qui ne fonctionne pas en
`file://`. Servir via un petit serveur HTTP :

```bash
python3 -m http.server 8000     # puis http://localhost:8000
```

## Déploiement GitHub Pages

Dépôt dédié (`mrizzello/mrzl`), Pages configuré sur **branche `master` / dossier `/` (root)**.

- **`CNAME`** contient `michele.rizzello.me` (à faire pointer via un enregistrement
  CNAME DNS vers `mrizzello.github.io`, ou 4 enregistrements A vers les IP GitHub
  Pages pour un domaine apex).
- **`_build/` n'est pas publié** : le dossier est préfixé par `_`, donc exclu par
  Jekyll (traitement Pages par défaut). Nos fichiers n'ont pas de front-matter :
  Jekyll les copie tels quels, à l'octet près.
  *Ne pas ajouter de fichier `.nojekyll`* : il désactiverait Jekyll et `_build/`
  redeviendrait accessible publiquement.

## À propos du générateur

`_build/build.py` est la transposition Python de l'ancien `build.php` (site
d'origine sous Grav CMS, désormais abandonné). Il pré-rend toutes les sections en
HTML statique (bon pour le SEO et le fonctionnement sans JavaScript). `data/site.json`
est la seule source de contenu à maintenir.
