/* Left icon bar to jump between the main hubs (Settings, 2026-11-21).
   Only platform admins get it: the server answers /api/me/admin-rail with 403 to everyone else.
   Loaded by nav-arrows.js and contractor-scope.js, so every signed-in screen has it. */
(function () {
  if (window.__bsAdminRail) return;
  window.__bsAdminRail = true;
  var KEY = 'bsAdminRail';

  function current(items) {
    var p = location.pathname, best = null, len = 0;
    items.forEach(function (it) {
      (it.match || []).forEach(function (m) {
        if ((p === m || p.indexOf(m) === 0) && m.length > len) { best = it.key; len = m.length; }
      });
    });
    return best;
  }

  function draw(items) {
    var old = document.getElementById('bs-rail');
    if (old) old.remove();
    if (!items || !items.length) { document.documentElement.classList.remove('bs-has-rail'); return; }
    if (!document.getElementById('bs-rail-css')) {
      var css = document.createElement('style');
      css.id = 'bs-rail-css';
      css.textContent =
        '#bs-rail{position:fixed;left:8px;top:50%;transform:translateY(-50%);z-index:9998;display:flex;flex-direction:column;gap:4px;' +
        'background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:6px;box-shadow:0 4px 16px rgba(15,23,42,.14);font-family:system-ui,sans-serif}' +
        '#bs-rail a{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;' +
        'text-decoration:none;position:relative;color:#0f172a}' +
        '#bs-rail a:hover,#bs-rail a:focus-visible{background:#f0fdfa;outline:2px solid #0f766e;outline-offset:-2px}' +
        '#bs-rail a.on{background:#ccfbf1;box-shadow:inset 3px 0 0 #0f766e}' +
        '#bs-rail a span{position:absolute;left:48px;top:50%;transform:translateY(-50%);background:#0f172a;color:#fff;font-size:12px;' +
        'font-weight:600;padding:4px 8px;border-radius:6px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .12s}' +
        '#bs-rail a:hover span,#bs-rail a:focus-visible span{opacity:1}' +
        '#bs-rail hr{border:0;border-top:1px solid #e2e8f0;margin:2px 4px}' +
        '#bs-rail-tab{display:none}' +
        '@media(min-width:900px){html.bs-has-rail body{padding-left:64px}}' +
        '@media(max-width:899px){#bs-rail{display:none}#bs-rail.open{display:flex}' +
        '#bs-rail-tab{display:flex;position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:9998;width:22px;height:56px;' +
        'border:1px solid #e2e8f0;border-left:0;border-radius:0 10px 10px 0;background:#fff;color:#0f766e;font-size:16px;' +
        'align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(15,23,42,.14);padding:0;cursor:pointer}' +
        '#bs-rail.open + #bs-rail-tab{display:none}}' +
        '@media print{#bs-rail,#bs-rail-tab{display:none!important}html.bs-has-rail body{padding-left:0!important}}';
      document.head.appendChild(css);
    }
    var on = current(items);
    var nav = document.createElement('nav');
    nav.id = 'bs-rail';
    nav.setAttribute('aria-label', 'Main hubs (platform admin)');
    items.forEach(function (it) {
      if (it.key === 'settings') nav.appendChild(document.createElement('hr'));
      var a = document.createElement('a');
      a.href = it.href;
      a.setAttribute('aria-label', it.label);
      a.innerHTML = it.icon + '<span></span>';
      a.querySelector('span').textContent = it.label;
      if (it.key === on) { a.className = 'on'; a.setAttribute('aria-current', 'page'); }
      nav.appendChild(a);
    });
    var tab = document.createElement('button');
    tab.id = 'bs-rail-tab'; tab.type = 'button';
    tab.setAttribute('aria-label', 'Open hub menu'); tab.innerHTML = '&#9776;';
    tab.onclick = function (e) { e.stopPropagation(); nav.classList.add('open'); };
    document.addEventListener('click', function (e) { if (!nav.contains(e.target)) nav.classList.remove('open'); });
    document.body.appendChild(nav);
    var oldTab = document.getElementById('bs-rail-tab');
    if (oldTab) oldTab.remove();
    document.body.appendChild(tab);
    document.documentElement.classList.add('bs-has-rail');
  }

  function start() {
    // Draw from the last answer right away (no flicker), then confirm with the server
    try { var c = sessionStorage.getItem(KEY); if (c) draw(JSON.parse(c)); } catch (e) {}
    fetch('/api/me/admin-rail', { credentials: 'same-origin' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        var items = d && d.ok ? d.items : null;
        try { if (items) sessionStorage.setItem(KEY, JSON.stringify(items)); else sessionStorage.removeItem(KEY); } catch (e) {}
        draw(items);
      })
      .catch(function () {});
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
