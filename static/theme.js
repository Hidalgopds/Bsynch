/* BSynch Theme System — theme.js
   Runs synchronously in <head> to avoid flash of wrong theme.
   Also injects the floating theme switcher after DOMContentLoaded. */
(function () {
  'use strict';

  var THEMES = ['light', 'dark', 'green'];
  var META = {
    light: { label: '☀️ Light', swatch: '#f0f4f8', border: '#cbd5e1' },
    dark:  { label: '🌙 Dark',  swatch: '#1a1d27', border: '#3b4255' },
    green: { label: '🌿 Green', swatch: '#0f2a20', border: '#1e9484' }
  };

  // ── 1. Apply saved theme immediately (no paint flash) ──
  var saved = localStorage.getItem('bsynch-theme') || 'light';
  if (!META[saved]) saved = 'light';
  document.documentElement.setAttribute('data-theme', saved);

  // ── 2. Public API ──
  function setTheme(t) {
    if (!META[t]) return;
    localStorage.setItem('bsynch-theme', t);
    document.documentElement.setAttribute('data-theme', t);
    updateActive(t);
  }
  window.setTheme = setTheme;

  // ── 3. Cross-tab sync ──
  window.addEventListener('storage', function (e) {
    if (e.key === 'bsynch-theme' && META[e.newValue]) {
      document.documentElement.setAttribute('data-theme', e.newValue);
      updateActive(e.newValue);
    }
  });

  // ── 4. Inject switcher after DOM ready ──
  document.addEventListener('DOMContentLoaded', function () {
    var wrap = document.createElement('div');
    wrap.id = 'bsynch-theme-sw';

    var btn = document.createElement('button');
    btn.id = 'bsynch-theme-btn';
    btn.title = 'Change theme';
    btn.innerHTML = '🎨';
    btn.setAttribute('aria-label', 'Theme switcher');

    var panel = document.createElement('div');
    panel.id = 'bsynch-theme-panel';

    THEMES.forEach(function (t) {
      var m = META[t];
      var opt = document.createElement('button');
      opt.className = 'th-option' + (saved === t ? ' th-active' : '');
      opt.id = 'th-opt-' + t;
      opt.title = m.label;
      opt.innerHTML =
        '<span class="th-dot-swatch" style="background:' + m.swatch +
        ';border-color:' + m.border + '"></span>' + m.label;
      opt.addEventListener('click', function () {
        setTheme(t);
        panel.classList.remove('th-open');
      });
      panel.appendChild(opt);
    });

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      panel.classList.toggle('th-open');
    });

    document.addEventListener('click', function () {
      panel.classList.remove('th-open');
    });

    wrap.appendChild(panel);
    wrap.appendChild(btn);
    document.body.appendChild(wrap);
  });

  function updateActive(active) {
    THEMES.forEach(function (t) {
      var el = document.getElementById('th-opt-' + t);
      if (el) el.classList.toggle('th-active', t === active);
    });
  }
})();
