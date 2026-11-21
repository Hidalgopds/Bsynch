/* Back / Forward arrows on every signed-in screen (Settings, 2026-11-21).
   Contractor screens already have them (contractor-scope.js): nothing is added twice.
   The arrows go in the screen's top bar; a screen without a recognizable bar gets a small floating pair. */
(function () {
  if (window.__bsNavArrows) return;
  window.__bsNavArrows = true;

  function make(floating) {
    var css = document.createElement('style');
    css.textContent =
      '.bs-nav{display:flex;gap:4px;flex-shrink:0;align-items:center}' +
      '.bs-nav button{width:32px;height:32px;border-radius:8px;border:1px solid rgba(148,163,184,.45);background:transparent;' +
      'color:inherit;font-size:16px;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0}' +
      '.bs-nav button:hover,.bs-nav button:focus-visible{border-color:#0f766e;color:#0f766e;outline:none}' +
      '.bs-nav.float{position:fixed;left:12px;bottom:78px;z-index:9999;background:#fff;color:#0f172a;padding:4px;border-radius:10px;' +
      'box-shadow:0 2px 10px rgba(15,23,42,.18)}' +
      '@media print{.bs-nav{display:none!important}}';
    document.head.appendChild(css);
    var nav = document.createElement('div');
    nav.className = 'bs-nav' + (floating ? ' float' : '');
    nav.setAttribute('role', 'group');
    nav.setAttribute('aria-label', 'Navigation');
    nav.innerHTML = '<button type="button" aria-label="Back" title="Back">&#8592;</button>' +
                    '<button type="button" aria-label="Forward" title="Forward">&#8594;</button>';
    nav.children[0].onclick = function () {
      // A fresh tab (no page behind): Back goes to the start screen instead of doing nothing
      if (history.length > 1) history.back(); else location.href = '/home';
    };
    nav.children[1].onclick = function () { history.forward(); };
    return nav;
  }

  // Light arrows on dark bars, dark arrows on light bars (AA contrast either way)
  function onDark(el) {
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) {
      var c = getComputedStyle(n).backgroundColor.match(/[\d.]+/g);
      if (c && (c.length < 4 || +c[3] > 0.5)) return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) < 140;
    }
    return false;
  }

  function place() {
    if (document.querySelector('.ct-nav, .bs-nav')) return;  // Contractor's own arrows, or already placed
    var bar = document.querySelector('#bsynch-status-bar > div') ||   // ERP status bar (left group)
              document.querySelector('header') ||
              document.querySelector('.top-bar-primary') ||
              document.querySelector('.top-bar');
    if (!bar) { document.body.appendChild(make(true)); return; }
    var nav = make(false);
    nav.style.color = onDark(bar) ? '#e2e8f0' : '#334155';
    var logo = bar.querySelector(':scope > .logo-badge, :scope > .logo, :scope > img');
    if (logo) logo.insertAdjacentElement('afterend', nav);
    else bar.insertBefore(nav, bar.firstChild);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', place);
  else place();
})();
