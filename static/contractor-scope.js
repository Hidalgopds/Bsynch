(function () {
  function ls(k) { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } }
  function ss(k, v) { try { if (v === undefined) return sessionStorage.getItem(k) || ''; sessionStorage.setItem(k, v); } catch (e) { return ''; } }

  var user = ls('bsynchAuth') || ls('mbrName') || ls('companyUser');
  var role = (ls('bsynchRole') || ls('mbrRole')).toLowerCase();
  var fromUrl = (new URLSearchParams(location.search).get('company') || '').toLowerCase();
  var fromPath = (location.pathname.match(/^\/contractor\/(hicons|bsynch)\b/) || [])[1] || '';
  var company = fromPath || fromUrl || ss('contractorCompany');
  if (company) ss('contractorCompany', company);

  window.CT = { user: user, role: role, company: company };

  var origFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    if (url.indexOf('/api/contractor') === 0) {
      init = init || {};
      var h = new Headers(init.headers || {});
      if (user) h.set('X-User-Name', user);
      if (company) h.set('X-Contractor-Company', company);
      init.headers = h;
    }
    return origFetch(input, init);
  };

  document.addEventListener('DOMContentLoaded', function () {
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
