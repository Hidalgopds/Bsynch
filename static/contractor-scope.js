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

  document.addEventListener('DOMContentLoaded', function () {
    addNavArrows();
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
