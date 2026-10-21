/* ERP screens: make sure this device has a signed session (password or crew PIN).
   Older sign-ins only kept the name in the browser; those sign in once more. */
(function () {
  var name = '';
  try { name = localStorage.getItem('bsynchAuth') || ''; } catch (e) {}
  var leaving = false;
  function signInAgain() {
    if (leaving) return; leaving = true;
    try { localStorage.removeItem('bsynchAuth'); } catch (e) {}
    // Screens with a PIN pad show it again; the rest go to the sign-in page
    if (document.getElementById('authGate') || document.getElementById('gs1')) location.reload();
    else location.replace('/login?next=' + encodeURIComponent(location.pathname + location.search));
  }
  var origFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    return origFetch(input, init).then(function (r) {
      if (r.status === 401) r.clone().json().then(function (d) { if (d && d.error === 'login_required') signInAgain(); }).catch(function () {});
      return r;
    });
  };
  if (!name) return;
  origFetch('/api/auth/session', {credentials: 'same-origin'}).then(function (r) { return r.json(); }).then(function (s) {
    if (s && s.ok) { if (s.name !== name) { try { localStorage.setItem('bsynchAuth', s.name); } catch (e) {} } return; }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', signInAgain); else signInAgain();
  }).catch(function () {});
})();
