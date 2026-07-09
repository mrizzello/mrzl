#!/usr/bin/env python3
"""
Construit index.html à partir de data/site.json.

Toutes les sections sont pré-rendues en HTML statique (SEO / fonctionne sans JS) ;
la Timeline reste un conteneur rempli côté client par js/timeline.js depuis le JSON.

Transposition Python du script d'origine _build/build.php (Grav abandonné,
data/site.json est désormais la seule source de vérité).

Usage :
    python3 _build/build.py
"""

import json
import os

# build.py vit dans _build/ ; on lit/écrit à la racine du site (un niveau au-dessus).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8") as f:
    data = json.load(f)
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


def build_body() -> str:
    out: list[str] = []
    w = out.append

    w('<div class="wrap">')

    w("<!-- ============ HEADER ============ -->")
    w('<header class="hero" id="top">')
    w(f'<img class="portrait" src="assets/michele-rizzello.jpg" alt="{h(p["name"])}" width="180" height="180">')
    w(f'<h1 class="name">{h(p["name"])}</h1>')
    w('<ul class="subtitles">')
    for s in p["subtitles"]:
        w(f"<li>{h(s)}</li>")
    w("</ul>")
    w(f'<div class="location">{h(p["location"])} <img src="assets/ch.png" alt="Suisse" width="18" height="12"></div>')
    w(render_social(p["social"]))
    w("</header>")

    w("<main>")

    w("<!-- ============ SKILLS ============ -->")
    w('<section class="section" id="skills">')
    w('<div class="columns">')
    for key in ("hardSkills", "softSkills"):
        block = p["skills"][key]
        w('<div class="col">')
        w(f'<h2>{h(block["title"])}</h2>')
        w('<ul class="bullets">')
        for i in block["items"]:
            w(f"<li>{h(i)}</li>")
        w("</ul>")
        w("</div>")
    w("</div>")
    w("</section>")

    w("<!-- ============ EXPÉRIENCE ============ -->")
    w('<section class="section" id="experience">')
    w(f'<h2>{h(p["sections"]["cv"])}</h2>')
    for item in reversed(data["cv"]):
        w('<article class="cv-item">')
        w('<div class="cv-meta">')
        end = fr_month_year(item["end"]) if item["end"] else "act."
        w(f'<div class="dates">{fr_month_year(item["begin"])} &ndash; {end}</div>')
        w(f'<div class="city">{h(item["city"])}</div>')
        w(f'<div class="type">{type_badge(item["type"])}</div>')
        w("</div>")
        w('<div class="cv-body">')
        w(f'<h3>{h(item["title"])}</h3>')
        contract = f'<span class="contract">| {h(item["contract"])}</span>' if item.get("contract") else ""
        w(f'<div class="employer">{h(item["employer"])}{contract}</div>')
        w(f'<div class="content">{item["content"]}</div>')
        if item.get("tools"):
            w('<div class="tags">')
            for t in item["tools"]:
                w(f'<span class="tag">{h(t)}</span>')
            w("</div>")
        if item.get("projects"):
            w('<details class="projects">')
            w(f'<summary>Projets ({len(item["projects"])})</summary>')
            w('<div class="projects-body">')
            for pr in item["projects"]:
                w(f'<h4>{h(pr["title"])}</h4>')
                if pr.get("urls"):
                    w('<ul class="url">')
                    for u in pr["urls"]:
                        w(f'<li><a href="{h(u)}" target="_blank" rel="noopener">{h(u)}</a></li>')
                    w("</ul>")
                w(f'<div class="content">{pr["content"]}</div>')
                if pr.get("tools"):
                    w('<div class="tags">')
                    for t in pr["tools"]:
                        w(f'<span class="tag">{h(t)}</span>')
                    w("</div>")
            w("</div>")
            w("</details>")
        w("</div>")
        w("</article>")
    w("</section>")

    w("<!-- ============ FORMATION ============ -->")
    w('<section class="section" id="formation">')
    w(f'<h2>{h(p["sections"]["edu"])}</h2>')
    footer = None
    for e in reversed(data["edu"]):
        if not e["end"]:
            footer = e
            continue
        w('<div class="edu-item">')
        w(f'<div class="edu-year">{fr_year(e["end"])}</div>')
        w(f'<div class="edu-title">{h(e["title"])}</div>')
        w(f'<div class="edu-topic">{h(e["topic"])}</div>')
        prix = f'<div class="prix">{h(e["prix"])}</div>' if e.get("prix") else ""
        w(f'<div class="edu-inst">{h(e["institution"])}{prix}</div>')
        w("</div>")
    if footer:
        w(f'<p class="edu-footer">{h(footer["title"])}</p>')
    w("</section>")

    w("<!-- ============ TIMELINE (JS) ============ -->")
    w('<section class="section" id="timeline">')
    w(f'<h2>{h(p["sections"]["timeline"])}</h2>')
    w('<div id="timeline-svg" class="timeline-wrap" aria-label="Chronologie carrière et formation"></div>')
    w("</section>")

    w("<!-- ============ INFORMATIQUE ============ -->")
    w('<section class="section" id="tools">')
    w(f'<h2>{h(p["sections"]["tools"])}</h2>')
    w('<div class="tools-grid">')
    for cat, tools in p["tools"].items():
        w('<table class="tbl">')
        w(f'<thead><tr><th colspan="2">{h(cat)}</th></tr></thead>')
        w("<tbody>")
        for name, t in tools.items():
            w(f'<tr><td>{h(name)}</td><td>{h(t.get("comment", ""))}</td></tr>')
        w("</tbody>")
        w("</table>")
    w("</div>")
    w("</section>")

    w("<!-- ============ LANGUES ============ -->")
    w('<section class="section" id="langues">')
    w(f'<h2>{h(p["sections"]["languages"])}</h2>')
    w('<table class="tbl langs">')
    w("<tbody>")
    for l in p["languages"].values():
        w(f'<tr><td><strong>{h(l["label"])}</strong></td><td>{h(l["comment"])}</td></tr>')
    w("</tbody>")
    w("</table>")
    w("</section>")

    w("<!-- ============ PROJETS ============ -->")
    w('<section class="section" id="projets">')
    w(f'<h2>{h(p["sections"]["projects"])}</h2>')
    for pr in data["projects"]:
        url = (pr["url"][0] if pr["url"] else "#") if isinstance(pr["url"], list) else pr["url"]
        w('<div class="project">')
        w(f'<a class="project-img" href="{h(url)}" target="_blank" rel="noopener" title="{h(pr["title"])}">')
        w(f'<img src="assets/projects/{h(pr["image"])}" alt="{h(pr["title"])}" width="200" height="200">')
        w("</a>")
        w('<div class="project-body">')
        w(f'<div class="project-title"><a href="{h(url)}" target="_blank" rel="noopener">{h(pr["title"])} &#8599;</a></div>')
        w(f'<div class="content">{pr["content"]}</div>')
        w("</div>")
        w("</div>")
    w("</section>")

    w("</main>")

    w('<footer class="footer">')
    w(render_social(p["social"]))
    w("</footer>")
    w("</div>")

    w('<a href="#top" id="scroll-top" title="Haut de page" aria-label="Haut de page">&#8593;</a>')

    return "\n".join(out)


def build_html() -> str:
    title = h(p["name"])
    desc = h(p["description"])
    body = build_body()
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://rizzello.me/">
  <link rel="icon" type="image/x-icon" href="assets/favico.ico">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
{body}
  <script src="js/timeline.js" defer></script>
  <script src="js/main.js" defer></script>
</body>
</html>
"""


def main() -> None:
    html = build_html()
    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html généré ({len(html.encode('utf-8'))} octets)")


if __name__ == "__main__":
    main()
