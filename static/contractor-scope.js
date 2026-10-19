(function () {
  function ls(k) { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } }
  function ss(k, v) { try { if (v === undefined) return sessionStorage.getItem(k) || ''; sessionStorage.setItem(k, v); } catch (e) { return ''; } }

  var user = ls('bsynchAuth') || ls('mbrName') || ls('companyUser');
  var role = (ls('bsynchRole') || ls('mbrRole')).toLowerCase();
  var fromUrl = (new URLSearchParams(location.search).get('company') || '').toLowerCase();
  var fromPath = (location.pathname.match(/^\/contractor\/(hicons|bsynch)\b/) || [])[1] || '';
  var company = fromPath || fromUrl || ss('contractorCompany');
  if (company) ss('contractorCompany', company);
  var here = location.pathname + location.search;

  window.CT = { user: user, role: role, company: company };

  if (!user) {
    location.replace('/login?next=' + encodeURIComponent(here));
    return;
  }

  var origFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    if (url.indexOf('/api/contractor') === 0) {
      init = init || {};
      var h = new Headers(init.headers || {});
      h.set('X-User-Name', user);
      if (company) h.set('X-Contractor-Company', company);
      init.headers = h;
    }
    return origFetch(input, init);
  };

  // Everyone must sign the confidentiality / data-use agreement before using the module.
  if (!window.CT_SKIP_AGREEMENT && ss('ctAgreementOk') !== user) {
    window.fetch('/api/contractor/agreement').then(function (r) { return r.json(); }).then(function (a) {
      if (a.ok && a.signed) { ss('ctAgreementOk', user); return; }
      if (a.ok) location.replace('/contractor/agreement?next=' + encodeURIComponent(here));
    }).catch(function () {});
  }

  // Location: only while the app is open and visible. Nothing runs in the background.
  var LOC_EVERY = 5 * 60 * 1000, locTimer = null, lastSent = 0;
  function sampleLocation() {
    if (document.visibilityState !== 'visible' || !navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(function (p) {
      CT.lastPos = {lat: p.coords.latitude, lng: p.coords.longitude, accuracy: p.coords.accuracy, at: Date.now()};
      if (Date.now() - lastSent < 60 * 1000) return;
      lastSent = Date.now();
      window.fetch('/api/contractor/location', {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({lat: CT.lastPos.lat, lng: CT.lastPos.lng, accuracy: CT.lastPos.accuracy, page: location.pathname})}).catch(function () {});
    }, function () {}, {enableHighAccuracy: false, timeout: 20000, maximumAge: 2 * 60 * 1000});
  }
  function startLocation() {
    if (locTimer || document.visibilityState !== 'visible') return;
    sampleLocation();
    locTimer = setInterval(sampleLocation, LOC_EVERY);
  }
  function stopLocation() { if (locTimer) { clearInterval(locTimer); locTimer = null; } }
  CT.startLocation = startLocation;
  function locationAllowed(cb) {
    if (navigator.permissions && navigator.permissions.query) {
      navigator.permissions.query({name: 'geolocation'}).then(function (st) { cb(st.state === 'granted'); }).catch(function () { cb(ls('ctLocOk') === '1'); });
    } else cb(ls('ctLocOk') === '1');
  }
  if (!window.CT_SKIP_AGREEMENT && navigator.geolocation) {
    locationAllowed(function (ok) {
      if (!ok) return;
      startLocation();
      document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') startLocation(); else stopLocation();
      });
      window.addEventListener('pagehide', stopLocation);
    });
  }

  // Installable app (PWA)
  var mf = document.createElement('link');
  mf.rel = 'manifest'; mf.href = '/contractor/manifest.webmanifest';
  document.head.appendChild(mf);
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(function () {});
  var deferredInstall = null;
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault(); deferredInstall = e;
    document.dispatchEvent(new Event('ct-installable'));
  });
  CT.isInstalled = function () {
    return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  };
  CT.isIOS = function () { return /iphone|ipad|ipod/i.test(navigator.userAgent); };
  CT.canPromptInstall = function () { return !!deferredInstall; };
  CT.install = function () {
    if (!deferredInstall) return Promise.resolve(false);
    deferredInstall.prompt();
    return deferredInstall.userChoice.then(function (c) { deferredInstall = null; return c.outcome === 'accepted'; });
  };

  function addNavArrows() {
    var header = document.querySelector('header');
    if (!header || header.querySelector('.ct-nav')) return;
    var style = document.createElement('style');
    style.textContent = '.ct-nav{display:flex;gap:4px;flex-shrink:0}' +
      '.ct-nav button{width:32px;height:32px;border-radius:8px;border:1px solid rgba(148,163,184,.35);background:transparent;color:inherit;font-size:16px;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center}' +
      '.ct-nav button:hover{border-color:#1e9484;color:#1e9484}' +
      '.ct-acct{width:32px;height:32px;border-radius:50%;border:1px solid rgba(148,163,184,.35);display:flex;align-items:center;justify-content:center;text-decoration:none;color:inherit;font-size:15px;flex-shrink:0}' +
      '.ct-acct:hover{border-color:#1e9484}';
    document.head.appendChild(style);
    var nav = document.createElement('div');
    nav.className = 'ct-nav';
    nav.innerHTML = '<button type="button" aria-label="Back" title="Back">&#8592;</button>' +
                    '<button type="button" aria-label="Forward" title="Forward">&#8594;</button>';
    nav.children[0].onclick = function () { history.back(); };
    nav.children[1].onclick = function () { history.forward(); };
    var badge = header.querySelector('.logo-badge');
    if (badge) badge.insertAdjacentElement('afterend', nav); else header.insertBefore(nav, header.firstChild);
    if (location.pathname !== '/contractor/account') {
      var acct = document.createElement('a');
      acct.className = 'ct-acct'; acct.href = '/contractor/account'; acct.title = 'My account';
      acct.setAttribute('aria-label', 'My account'); acct.innerHTML = '&#128100;';
      var right = header.querySelector('.hdr-right');
      if (right) right.insertBefore(acct, right.firstChild); else header.appendChild(acct);
    }
  }

  function applyBrand(b) {
    if (!b || !b.ok) return;
    var hex = /^#[0-9a-fA-F]{6}$/;
    var primary = hex.test(b.primary || '') ? b.primary : '#0d1b36';
    var accent = hex.test(b.accent || '') ? b.accent : '#e8a317';
    var css = document.createElement('style');
    css.textContent = 'html[data-theme] header{background:' + primary + ' !important;border-bottom:3px solid ' + accent + ' !important;}' +
      '.ct-logo{height:36px;max-width:120px;padding:3px 8px;border-radius:9px;background:#fff;display:flex;align-items:center;flex-shrink:0;}' +
      '.ct-logo img{max-height:30px;max-width:104px;object-fit:contain;display:block;}';
    document.head.appendChild(css);
    var logoOk = /^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+\/=]+$/.test(b.logo || '') || /^\/static\/brand\/[\w.-]+\.(png|jpg|webp)$/.test(b.logo || '');
    var badge = document.querySelector('header .logo-badge');
    if (badge && logoOk) {
      var box = document.createElement('div');
      box.className = 'ct-logo';
      var img = document.createElement('img');
      img.src = b.logo; img.alt = b.name || '';
      box.appendChild(img);
      badge.replaceWith(box);
    }
  }
  function loadBrand() {
    if (!company) return;
    var key = 'ctBrand_' + company, cached = ss(key);
    if (cached) { try { applyBrand(JSON.parse(cached)); return; } catch (e) {} }
    window.fetch('/api/contractor/' + company + '/brand').then(function (r) { return r.json(); }).then(function (b) {
      if (b.ok) ss(key, JSON.stringify(b));
      applyBrand(b);
    }).catch(function () {});
  }

  document.addEventListener('DOMContentLoaded', function () {
    addNavArrows();
    loadBrand();
    if (!company) return;
    var title = document.querySelector('.hdr-title');
    if (title && !document.body.hasAttribute('data-ct-hub')) {
      title.textContent += ' · ' + company.charAt(0).toUpperCase() + company.slice(1);
    }
    document.querySelectorAll('a[href]').forEach(function (a) {
      var href = a.getAttribute('href');
      if (href === '/contractor-hub' && !document.body.hasAttribute('data-ct-hub')) {
        a.setAttribute('href', '/contractor/' + company);
      } else if (/^\/contractor\/(projects|dashboard|workorders)$/.test(href)) {
        a.setAttribute('href', href + '?company=' + company);
      }
    });
  });
})();
