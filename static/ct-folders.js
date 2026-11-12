/* Client folders: the company's client master. A Manager names each folder, picks its colour
   and chooses which clients go in it; work orders are then grouped by folder.
   CTFolders.open(company, done) opens the editor; done() runs after any change. */
(function () {
  var COLORS = ['#1e9484', '#2563eb', '#7c3aed', '#db2777', '#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#0891b2', '#475569'];
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); }
  function ensureStyle() {
    if (document.getElementById('ct-cf-style')) return;
    var st = document.createElement('style'); st.id = 'ct-cf-style';
    st.textContent =
      '.ct-cf{position:fixed;inset:0;background:rgba(15,23,42,.45);display:flex;align-items:center;justify-content:center;padding:16px;z-index:400;font-family:"Segoe UI",system-ui,sans-serif}' +
      '.ct-cf *{box-sizing:border-box}' +
      '.ct-cf-box{background:#fff;color:#0f172a;border-radius:16px;padding:20px;width:100%;max-width:480px;max-height:92vh;overflow:auto}' +
      '.ct-cf-box h3{font-size:17px;margin:0 0 2px;color:#0f172a}.ct-cf-sub{font-size:13px;color:#64748b;margin-bottom:14px}' +
      '.ct-cf-row{display:flex;align-items:center;gap:10px;padding:11px 12px;border:1px solid #e2e8f0;border-radius:12px;margin-bottom:8px;cursor:pointer;background:#fff}' +
      '.ct-cf-row:hover{border-color:#8fcfc2}' +
      '.ct-cf-ico{width:34px;height:28px;border-radius:5px 5px 7px 7px;position:relative;flex-shrink:0}' +
      '.ct-cf-ico:before{content:"";position:absolute;left:0;top:-5px;width:15px;height:8px;border-radius:4px 4px 0 0;background:inherit}' +
      '.ct-cf-name{flex:1;min-width:0;font-weight:700;font-size:14px;color:#0f172a}.ct-cf-n{font-size:12px;color:#64748b;font-weight:400}' +
      '.ct-cf label{display:block;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.4px;font-weight:700;margin:12px 0 5px}' +
      '.ct-cf input[type=text],.ct-cf input[type=search]{width:100%;border:1px solid #cbd5e1;border-radius:9px;padding:9px 11px;font-size:14px;font-family:inherit;background:#fff;color:#0f172a}' +
      '.ct-cf-sw{display:flex;flex-wrap:wrap;gap:8px;align-items:center}' +
      '.ct-cf-sw button{width:30px;height:30px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 1px #cbd5e1;cursor:pointer;padding:0}' +
      '.ct-cf-sw button.on{box-shadow:0 0 0 2px #0f172a}' +
      '.ct-cf-sw input[type=color]{width:34px;height:34px;border:none;padding:0;background:none;cursor:pointer}' +
      '.ct-cf-cl{max-height:240px;overflow:auto;border:1px solid #e2e8f0;border-radius:10px;padding:4px 0}' +
      '.ct-cf-cl label{display:flex;align-items:center;gap:9px;margin:0;padding:7px 12px;text-transform:none;letter-spacing:0;font-size:14px;font-weight:600;color:#0f172a;cursor:pointer}' +
      '.ct-cf-cl label small{display:block;font-weight:400;color:#64748b;font-size:12px}' +
      '.ct-cf-cl input{width:18px;height:18px;flex-shrink:0;accent-color:#1e9484}' +
      '.ct-cf-other{font-size:11px;color:#b45309;font-weight:600}' +
      '.ct-cf-act{display:flex;gap:8px;justify-content:flex-end;margin-top:16px;flex-wrap:wrap}' +
      '.ct-cf-act button{padding:9px 16px;border-radius:9px;font-weight:700;font-size:14px;cursor:pointer;border:1px solid #8fcfc2;background:#fff;color:#0f766e}' +
      '.ct-cf-act button.go{background:#1e9484;border-color:#1e9484;color:#fff}.ct-cf-act button.del{border-color:#fecaca;color:#b91c1c;margin-right:auto}' +
      '.ct-cf-act button:disabled{opacity:.6}' +
      '.ct-cf-msg{color:#b91c1c;font-size:13px;margin-top:8px;min-height:16px;text-align:right}' +
      '.ct-cf-empty{text-align:center;color:#64748b;font-size:13px;padding:14px 0}';
    document.head.appendChild(st);
  }
  function api(method, url, body) {
    return fetch(url, {method: method, headers: {'Content-Type': 'application/json'}, body: body ? JSON.stringify(body) : undefined})
      .then(function (r) { return r.json(); });
  }

  function open(company, done) {
    ensureStyle();
    var base = '/api/contractor/' + encodeURIComponent(company) + '/client-folders';
    var wrap = document.createElement('div');
    wrap.className = 'ct-cf'; wrap.setAttribute('role', 'dialog'); wrap.setAttribute('aria-modal', 'true');
    wrap.innerHTML = '<div class="ct-cf-box"><div class="ct-cf-empty">Loading&hellip;</div></div>';
    document.body.appendChild(wrap);
    var box = wrap.querySelector('.ct-cf-box'), data = null, changed = false;
    function close() { wrap.remove(); if (changed && done) done(); }
    wrap.addEventListener('click', function (e) { if (e.target === wrap) close(); });
    function load() {
      return api('GET', base).then(function (d) {
        if (!d.ok) { box.innerHTML = '<div class="ct-cf-empty">' + esc(d.error || 'Could not load the folders') + '</div>'; return; }
        data = d; list();
      }).catch(function () { box.innerHTML = '<div class="ct-cf-empty">Connection error. Try again.</div>'; });
    }
    function countIn(id) { return data.clients.filter(function (c) { return c.folder_id === id; }).length; }

    function list() {
      box.innerHTML = '<h3>&#128193; Client folders</h3>' +
        '<div class="ct-cf-sub">Group the work orders by client. Each folder has a name and a colour you choose.</div>' +
        (data.folders.length ? data.folders.map(function (f) {
          var n = countIn(f.id);
          return '<div class="ct-cf-row" data-id="' + esc(f.id) + '"><span class="ct-cf-ico" style="background:' + esc(f.color) + '"></span>' +
            '<span class="ct-cf-name">' + esc(f.name) + '<br><span class="ct-cf-n">' + n + (n === 1 ? ' client' : ' clients') + '</span></span>' +
            '<span style="color:#94a3b8">&#9998;</span></div>';
        }).join('') : '<div class="ct-cf-empty">No folders yet. Create the first one, e.g. <b>Newmark Homes</b>.</div>') +
        '<div class="ct-cf-act"><button type="button" class="no">Close</button><button type="button" class="go">+ New folder</button></div>';
      box.querySelector('.no').onclick = close;
      box.querySelector('.go').onclick = function () { edit(null); };
      Array.prototype.forEach.call(box.querySelectorAll('.ct-cf-row'), function (row) {
        row.onclick = function () { edit(data.folders.filter(function (f) { return f.id === row.dataset.id; })[0]); };
      });
    }

    function edit(folder) {
      var color = folder ? folder.color : COLORS[data.folders.length % COLORS.length];
      var folderName = function (id) { var f = data.folders.filter(function (x) { return x.id === id; })[0]; return f ? f.name : ''; };
      var clients = data.clients.slice().sort(function (a, b) {
        var ai = folder && a.folder_id === folder.id ? 0 : 1, bi = folder && b.folder_id === folder.id ? 0 : 1;
        return ai - bi || a.name.localeCompare(b.name);
      });
      box.innerHTML = '<h3>' + (folder ? 'Edit folder' : 'New folder') + '</h3>' +
        '<label>Name</label><input type="text" class="cf-name" maxlength="60" placeholder="e.g. Newmark Homes" value="' + esc(folder ? folder.name : '') + '">' +
        '<label>Colour</label><div class="ct-cf-sw">' + COLORS.map(function (c) {
          return '<button type="button" data-c="' + c + '" style="background:' + c + '" aria-label="Colour ' + c + '"></button>';
        }).join('') + '<input type="color" aria-label="Other colour"></div>' +
        '<label>Clients in this folder</label>' +
        (clients.length ? '<input type="search" class="cf-q" placeholder="Search clients" style="margin-bottom:6px">' +
          '<div class="ct-cf-cl">' + clients.map(function (c) {
            var other = c.folder_id && (!folder || c.folder_id !== folder.id) ? folderName(c.folder_id) : '';
            return '<label data-s="' + esc((c.name + ' ' + c.org + ' ' + c.emails.join(' ')).toLowerCase()) + '"><input type="checkbox" value="' + esc(c.id) + '"' +
              (folder && c.folder_id === folder.id ? ' checked' : '') + '><span>' + esc(c.name || c.emails[0]) +
              (other ? ' <span class="ct-cf-other">in ' + esc(other) + '</span>' : '') +
              (c.emails.length ? '<small>' + esc(c.emails.join(', ')) + '</small>' : '') + '</span></label>';
          }).join('') + '</div>' : '<div class="ct-cf-empty">No clients yet. They appear here when a work order has a client.</div>') +
        '<div class="ct-cf-act">' + (folder ? '<button type="button" class="del">Delete</button>' : '') +
        '<button type="button" class="no">Back</button><button type="button" class="go">Save</button></div><div class="ct-cf-msg"></div>';
      var sw = box.querySelector('.ct-cf-sw'), picker = sw.querySelector('input[type=color]'), msg = box.querySelector('.ct-cf-msg');
      function paint() {
        Array.prototype.forEach.call(sw.querySelectorAll('button'), function (b) { b.classList.toggle('on', b.dataset.c === color); });
        picker.value = color;
      }
      sw.onclick = function (e) { var b = e.target.closest('button'); if (b) { color = b.dataset.c; paint(); } };
      picker.oninput = function () { color = picker.value; paint(); };
      paint();
      var q = box.querySelector('.cf-q');
      if (q) q.oninput = function () {
        var t = q.value.trim().toLowerCase();
        Array.prototype.forEach.call(box.querySelectorAll('.ct-cf-cl label'), function (l) { l.style.display = !t || l.dataset.s.indexOf(t) >= 0 ? '' : 'none'; });
      };
      box.querySelector('.no').onclick = list;
      var del = box.querySelector('.del');
      if (del) del.onclick = function () {
        if (!confirm('Delete the folder "' + folder.name + '"? Its clients and work orders are kept; they just leave the folder.')) return;
        del.disabled = true;
        api('DELETE', base + '/' + encodeURIComponent(folder.id)).then(function (r) {
          if (!r.ok) { del.disabled = false; msg.textContent = r.error || 'Could not delete'; return; }
          changed = true; load();
        }).catch(function () { del.disabled = false; msg.textContent = 'Connection error. Try again.'; });
      };
      var go = box.querySelector('.go');
      go.onclick = function () {
        var name = box.querySelector('.cf-name').value.trim();
        if (!name) { msg.textContent = 'Give the folder a name.'; return; }
        var ids = Array.prototype.map.call(box.querySelectorAll('.ct-cf-cl input:checked'), function (i) { return i.value; });
        go.disabled = true; msg.textContent = '';
        var save = folder ? Promise.resolve({ok: true, folder: folder}) : api('POST', base, {name: name, color: color});
        save.then(function (r) {
          if (!r.ok) throw new Error(r.error || 'Could not save');
          return api('PATCH', base + '/' + encodeURIComponent(r.folder.id), {name: name, color: color, client_ids: ids});
        }).then(function (r) {
          if (!r.ok) throw new Error(r.error || 'Could not save');
          changed = true; return load();
        }).catch(function (e) {
          go.disabled = false; msg.textContent = /fetch|network/i.test(e.message) ? 'Connection error. Try again.' : e.message;
          if (!folder) load();
        });
      };
      if (!folder) box.querySelector('.cf-name').focus();
    }
    load();
  }

  /* Which folder a work order belongs to: by the client's email, then by the client's name. */
  function indexer(data) {
    var ok = {}, byEmail = {}, byName = {};
    (data.folders || []).forEach(function (f) { ok[f.id] = f; });
    (data.clients || []).forEach(function (c) {
      if (!c.folder_id || !ok[c.folder_id]) return;
      c.emails.forEach(function (e) { byEmail[e] = c.folder_id; });
      [c.name, c.org].forEach(function (n) { n = (n || '').trim().toLowerCase(); if (n && !byName[n]) byName[n] = c.folder_id; });
    });
    return function (job) {
      var e = (job.client_email || '').trim().toLowerCase(), n = (job.client_name || '').trim().toLowerCase();
      var id = (e && byEmail[e]) || (n && byName[n]);
      return id ? ok[id] : null;
    };
  }

  window.CTFolders = {open: open, indexer: indexer};
})();
