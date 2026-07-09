#!/usr/bin/env python3
"""
Construit index.html à partir de data/site.yaml via un template Jinja.

Toutes les sections sont pré-rendues en HTML statique (SEO / fonctionne sans JS).
Les données nécessaires à la Timeline sont embarquées dans la page
(<script id="timeline-data">), et js/timeline.js les lit au chargement
(plus de fetch, plus de fichier JSON : YAML est la seule source de vérité).

Dépendances : PyYAML, Jinja2  (voir requirements.txt).

Usage :
    python3 _build/build.py
"""

import json
import os

import yaml
from jinja2 import Environment, FileSystemLoader

# build.py vit dans _build/ ; on lit/écrit à la racine du site (un niveau au-dessus).
BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD_DIR)

with open(os.path.join(ROOT, "data", "site.yaml"), encoding="utf-8") as f:
    data = yaml.safe_load(f)
p = data["profile"]


def h(s) -> str:
    """Équivalent de htmlspecialchars(..., ENT_QUOTES, 'UTF-8') de PHP."""
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


_MONTHS = ["", "janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def fr_month_year(iso: str | None) -> str:
    """Format « MMM YYYY » en français (ex. « nov. 1999 »)."""
    if not iso:
        return ""
    y, mo, _ = (int(x) for x in iso.split("-"))
    return f"{_MONTHS[mo]} {y}"


def fr_year(iso: str | None) -> str:
    return iso[:4] if iso else ""


def type_badge(t: str | None) -> str:
    """Icône + libellé selon le type d'expérience."""
    if t == "chem":
        return (
            '<img src="assets/icons/chalkboard-teacher.svg" alt="Enseignement" width="28" height="32">'
            '<span class="type-label">Enseignement</span>'
        )
    return (
        '<img src="assets/icons/laptop-code.svg" alt="Développement web" width="28" height="32">'
        '<span class="type-label">Développement web</span>'
    )


def render_social(social: list) -> str:
    out = '<nav class="social" aria-label="Réseaux sociaux">'
    for s in social:
        out += (
            '<a href="{href}" target="_blank" rel="noopener" title="{label}">'
            '<img src="assets/icons/{icon}" alt="{label}" width="28" height="28"></a>'
        ).format(href=h(s["href"]), label=h(s["label"]), icon=h(s["icon"]))
    return out + "</nav>"


def timeline_payload() -> str:
    """Sous-ensemble des données consommé par js/timeline.js, sérialisé en JSON
    pour être embarqué dans la page. `<` est échappé pour ne jamais fermer le
    <script> par accident."""
    keep_edu = ("id", "type", "begin", "end", "title", "institution")
    keep_cv = ("id", "type", "begin", "end", "title", "employer")
    payload = {
        "profile": {"locations": p["locations"]},
        "edu": [{k: e.get(k) for k in keep_edu} for e in data["edu"]],
        "cv": [{k: c.get(k) for k in keep_cv} for c in data["cv"]],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def project_href(pr: dict) -> str:
    url = pr["url"]
    if isinstance(url, list):
        return url[0] if url else "#"
    return url


def main() -> None:
    env = Environment(
        loader=FileSystemLoader(BUILD_DIR),
        autoescape=False,        # échappement explicite via le filtre |h (parité PHP)
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["h"] = h
    env.filters["frmy"] = fr_month_year
    env.filters["fryr"] = fr_year
    env.globals["type_badge"] = type_badge
    env.globals["render_social"] = render_social

    # Formation : les entrées avec date de fin sont affichées (ordre inverse) ;
    # l'entrée sans date de fin sert de note de pied de section.
    edu_rev = list(reversed(data["edu"]))
    edu_items = [e for e in edu_rev if e.get("end")]
    edu_footer = next((e for e in edu_rev if not e.get("end")), None)

    projects = []
    for pr in data["projects"]:
        pr = dict(pr)
        pr["href"] = project_href(pr)
        projects.append(pr)

    html = env.get_template("template.html.j2").render(
        p=p,
        cv_items=list(reversed(data["cv"])),
        edu_items=edu_items,
        edu_footer=edu_footer,
        languages=list(p["languages"].values()),
        projects=projects,
        timeline_json=timeline_payload(),
    )

    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html généré ({len(html.encode('utf-8'))} octets)")


if __name__ == "__main__":
    main()
