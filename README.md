# Site statique — Michele Rizzello

CV / portfolio statique servi par **GitHub Pages** sous le domaine
[`michele.rizzello.me`](https://michele.rizzello.me).

Aucune dépendance côté client, aucun serveur : la page est **pré-générée en local**
(Python + Jinja) puis servie telle quelle.

## Structure

```
.
├── index.html          # page générée (ne pas éditer à la main → régénérée par build.py)
├── CNAME               # domaine personnalisé (GitHub Pages)
├── css/style.css       # styles autonomes, responsives
├── js/
│   ├── timeline.js     # génère la chronologie SVG à partir des données embarquées
│   └── main.js         # bouton « retour en haut »
├── data/site.yaml      # SOURCE DE VÉRITÉ des contenus (expériences, formations, projets…)
├── assets/             # photo, drapeau, icônes, images des projets, favicon
├── _build/
│   ├── build.py         # générateur : data/site.yaml -> index.html (dev only, non publié)
│   └── template.html.j2 # template Jinja
├── requirements.txt    # PyYAML + Jinja2
└── README.md
```

## Prérequis (une fois)

Le générateur a besoin de **PyYAML** et **Jinja2**. Via un environnement virtuel :

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Flux de travail (éditer → publier)

1. Modifier le contenu dans **`data/site.yaml`**.
2. Régénérer la page :

   ```bash
   .venv/bin/python _build/build.py     # data/site.yaml -> index.html
   ```

   > La Timeline se reconstruit toute seule au chargement : `_build/build.py`
   > embarque les données nécessaires dans la page (`<script id="timeline-data">`)
   > et `js/timeline.js` les lit et dessine le SVG.
3. Committer puis pousser. GitHub Pages sert automatiquement la nouvelle version.

   ```bash
   git add -A && git commit -m "maj contenu" && git push
   ```

## Test local

Le site est entièrement statique (les données de la timeline sont embarquées dans
`index.html`, plus aucun `fetch`), donc il fonctionne même en ouvrant le fichier
en `file://`. Pour un rendu fidèle on peut aussi servir via un petit serveur HTTP :

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

`_build/build.py` lit **`data/site.yaml`** (seule source à maintenir) et rend le
template Jinja `_build/template.html.j2` pour produire `index.html`, avec toutes les
sections pré-rendues en HTML statique (bon pour le SEO et le fonctionnement sans
JavaScript). Le rendu vise à reproduire l'apparence du site d'origine (thème Grav,
désormais abandonné).
