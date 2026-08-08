/* BSynch Theme System — theme.js
   Runs synchronously in <head> to avoid flash of wrong theme.
   Theme switching available in Settings pages of each module. */
(function () {
  'use strict';

  var THEMES = ['light', 'dark', 'bsynch'];
  var META = {
    light:  { label: '☀️ Light',  swatch: '#f0f4f8', border: '#cbd5e1' },
    dark:   { label: '🌙 Dark',   swatch: '#1a1d27', border: '#3b4255' },
    bsynch: { label: '🌿 BSynch', swatch: '#ffffff', border: '#1e9484' }
  };

  // ── 1. Apply saved theme immediately (no paint flash) ──
  var saved = localStorage.getItem('bsynch-theme') || 'light';
  if (!META[saved]) saved = 'light';
  // migrate old 'green' value
  if (saved === 'green') { saved = 'bsynch'; localStorage.setItem('bsynch-theme', 'bsynch'); }
  document.documentElement.setAttribute('data-theme', saved);

  // ── 2. Public API ──
  function setTheme(t) {
    if (!META[t]) return;
    localStorage.setItem('bsynch-theme', t);
    document.documentElement.setAttribute('data-theme', t);
    // Update any rendered switchers on the page
    THEMES.forEach(function (k) {
      var el = document.getElementById('th-opt-' + k);
      if (el) el.classList.toggle('th-active', k === t);
    });
  }
  window.setTheme = setTheme;

  // ── 3. Cross-tab sync ──
  window.addEventListener('storage', function (e) {
    if (e.key === 'bsynch-theme' && META[e.newValue]) {
      document.documentElement.setAttribute('data-theme', e.newValue);
      THEMES.forEach(function (k) {
        var el = document.getElementById('th-opt-' + k);
        if (el) el.classList.toggle('th-active', k === e.newValue);
      });
    }
  });

  // ── 4. Expose renderThemeSwitcher() for Settings pages ──
  window.renderThemeSwitcher = function (containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var current = localStorage.getItem('bsynch-theme') || 'light';
    var html = '<div class="theme-picker">';
    THEMES.forEach(function (t) {
      var m = META[t];
      html += '<button id="th-opt-' + t + '" class="th-option' + (current === t ? ' th-active' : '') + '" ' +
              'onclick="setTheme(\'' + t + '\')" title="' + m.label + '">' +
              '<span class="th-dot-swatch" style="background:' + m.swatch + ';border-color:' + m.border + '"></span>' +
              m.label + '</button>';
    });
    html += '</div>';
    container.innerHTML = html;
  };
})();
