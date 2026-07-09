/**
 * Timeline SVG — généré dynamiquement depuis data/site.json.
 * Reproduit fidèlement la logique du template Grav d'origine :
 *   - collection = formations (edu, par begin asc) puis expériences (cv, par begin asc)
 *   - axe : 1er janvier de la 1re année -> 31 décembre de l'année courante, largeur 600
 *   - libellé à droite pour les 4 premiers items, à gauche ensuite
 *   - décalage vertical +21 par item, SAUF pour 'cfc' et 'hep' (chevauchement voulu)
 */
(function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var WIDTH = 600, Y_START = 28, Y_DELTA = 21;

  function el(name, attrs, text) {
    var n = document.createElementNS(SVG_NS, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }
  function ms(iso) {                       // "YYYY-MM-DD" -> timestamp UTC (minuit)
    var p = iso.split('-');
    return Date.UTC(+p[0], +p[1] - 1, +p[2]);
  }
  function round1(x) { return Math.round(x * 10) / 10; }
  function round2(x) { return Math.round(x * 100) / 100; }

  function build(data) {
    var host = document.getElementById('timeline-svg');
    if (!host) return;

    // Collection combinée, chaque sous-liste triée par begin croissant (null en tête)
    function byBegin(a, b) {
      var av = a.begin ? ms(a.begin) : -Infinity;
      var bv = b.begin ? ms(b.begin) : -Infinity;
      return av - bv;
    }
    var edu = data.edu.slice().sort(byBegin).map(function (e) {
      return { id: e.id, type: e.type, begin: e.begin, end: e.end,
               title: e.title, sub: e.institution || '' };
    });
    var cv = data.cv.slice().sort(byBegin).map(function (c) {
      return { id: c.id, type: c.type, begin: c.begin, end: c.end,
               title: c.title, sub: c.employer || '' };
    });
    var items = edu.concat(cv);
    var count = data.edu.length + data.cv.length;

    // Bornes temporelles
    var yearBegin = null;
    items.forEach(function (it) {
      if (it.begin) {
        var y = +it.begin.slice(0, 4);
        if (yearBegin === null || y < yearBegin) yearBegin = y;
      }
    });
    var yearEnd = new Date().getFullYear();
    var beginMs = Date.UTC(yearBegin, 0, 1);
    var endMs = Date.UTC(yearEnd, 11, 31);
    var span = endMs - beginMs;

    var years = Math.round((span / 1000) / 3.154e7 - 1);
    var widthYear = round2(WIDTH / (years + 1));
    var height = (count - 4) * Y_DELTA + 2 * Y_START;

    function x(t) { return (t - beginMs) / span * WIDTH; }

    var svg = el('svg', {
      version: '1.1',
      viewBox: '-1 -1 ' + (WIDTH + 1) + ' ' + (height + 1),
      baseProfile: 'full',
      xmlns: SVG_NS,
      class: 'timeline'
    });

    // ---- Légende : grille des années + barres de lieux ----
    var legend = el('g', { class: 'legend' });
    legend.appendChild(el('rect', { x: 0, y: 0, width: WIDTH, height: 14, fill: '#4a4a4a', class: 'years-bg' }));
    for (var i = 0; i <= years; i++) {
      var xi = i * widthYear;
      legend.appendChild(el('line', { x1: xi, x2: xi, y1: 0, y2: height, 'stroke-width': 0.5, stroke: '#e8e8e8' }));
      legend.appendChild(el('text', {
        x: xi + 1.5, y: 11, 'text-anchor': 'start', 'font-family': 'Helvetica',
        'font-size': 6.3, 'font-weight': 'bold', fill: '#ffffff', class: 'year'
      }, yearBegin + i));
    }
    (data.profile.locations || []).forEach(function (loc) {
      var xb = round1(x(ms(loc.begin)));
      var xe = round1(x(loc.end ? ms(loc.end) : endMs));
      legend.appendChild(el('rect', {
        x: xb, y: height - 14, width: xe - xb, height: 14, fill: loc.bgcolor,
        class: 'location-bg location-bg-' + loc.id
      }));
      legend.appendChild(el('text', {
        x: xb + (xe - xb) / 2, y: height - 5, 'text-anchor': 'middle', 'font-family': 'Helvetica',
        'font-size': 6.6, 'font-weight': 'bold', fill: '#ffffff', class: 'location-txt'
      }, loc.label));
    });
    svg.appendChild(legend);

    // ---- Items ----
    var g = el('g', { class: 'items' });
    var yShift = Y_START, idx = 0;
    items.forEach(function (it) {
      idx++;                                  // loop.index 1-based (inclut 'basic')
      if (!it.type) return;                   // items sans type non dessinés

      var xb = round1(x(ms(it.begin)));
      var current = !it.end;
      var xe = round1(x(current ? Date.now() : ms(it.end)));

      var gi = el('g', { class: 'item ' + it.type + ' item-' + idx + ' item-' + it.id });
      gi.appendChild(el('line', { x1: xb, x2: xe, y1: yShift, y2: yShift, 'stroke-width': 2.5, stroke: '#999999' }));
      gi.appendChild(el('circle', { cx: xb, cy: yShift, r: 3, fill: '#ffffff', stroke: '#999999', 'stroke-width': 1.2 }));
      if (!current) {
        gi.appendChild(el('circle', { cx: xe, cy: yShift, r: 3, fill: '#ffffff', stroke: '#999999', 'stroke-width': 1.2 }));
      }
      var anchor, tx;
      if (idx <= 4) { anchor = 'start'; tx = xe + 6; }
      else { anchor = 'end'; tx = xb - 6; }
      gi.appendChild(el('text', { x: tx, y: yShift - 2, 'text-anchor': anchor, 'font-family': 'Helvetica', 'font-size': 7, 'font-weight': 'bold', fill: '#333333' }, it.title));
      gi.appendChild(el('text', { x: tx, y: yShift + 6, 'text-anchor': anchor, 'font-family': 'Helvetica', 'font-size': 7, fill: '#333333' }, it.sub));
      g.appendChild(gi);

      if (it.id !== 'cfc' && it.id !== 'hep') yShift += Y_DELTA;
    });
    svg.appendChild(g);

    host.appendChild(svg);
  }

  fetch('data/site.json')
    .then(function (r) { return r.json(); })
    .then(build)
    .catch(function (e) {
      var host = document.getElementById('timeline-svg');
      if (host) host.textContent = 'Impossible de charger la chronologie.';
      console.error(e);
    });
})();
