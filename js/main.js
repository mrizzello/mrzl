/* Bouton « retour en haut » : apparaît après défilement. */
(function () {
  'use strict';
  var btn = document.getElementById('scroll-top');
  if (!btn) return;
  function toggle() { btn.classList.toggle('visible', window.scrollY > 200); }
  window.addEventListener('scroll', toggle, { passive: true });
  btn.addEventListener('click', function (e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  toggle();
})();
