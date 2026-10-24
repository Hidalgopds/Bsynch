/* "Needs another visit": a job was worked but isn't finished.
   CTReturn.open(job, {people: [...], reasons: [...]}, done) asks what is pending and, if known,
   the day of the next visit. With a day it moves there; without one it waits in the calendar's
   "Waiting to return" box. done(updatedJob) runs after it is saved. */
(function () {
  var REASONS = ['Waiting for materials', "Client wasn't there", 'Next phase', 'Weather', 'Needs more time'];
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); }
  function ensureStyle() {
    if (document.getElementById('ct-ret-style')) return;
    var st = document.createElement('style'); st.id = 'ct-ret-style';
    st.textContent =
      '.ct-ret{position:fixed;inset:0;background:rgba(15,23,42,.45);display:flex;align-items:center;justify-content:center;padding:16px;z-index:400;font-family:"Segoe UI",system-ui,sans-serif}' +
      '.ct-ret-box{background:#fff;color:#0f172a;border-radius:16px;padding:20px;width:100%;max-width:440px;max-height:92vh;overflow:auto}' +
      '.ct-ret-box h3{font-size:17px;margin:0 0 2px}.ct-ret-sub{font-size:13px;color:#64748b;margin-bottom:12px}' +
      '.ct-ret-chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}' +
      '.ct-ret-chips button{padding:6px 11px;border-radius:20px;border:1px solid #cbd5e1;background:#fff;color:#334155;font-size:12.5px;font-weight:600;cursor:pointer}' +
      '.ct-ret-chips button.on{background:#e3f3ef;border-color:#1e9484;color:#0f766e}' +
      '.ct-ret label{display:block;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.4px;font-weight:700;margin:10px 0 4px}' +
      '.ct-ret textarea,.ct-ret input,.ct-ret select{width:100%;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:9px;padding:9px 11px;font-size:14px;font-family:inherit;background:#fff;color:#0f172a}' +
      '.ct-ret-two{display:grid;grid-template-columns:1fr 1fr;gap:10px}' +
      '.ct-ret-hint{font-size:12px;color:#64748b;margin-top:4px}' +
      '.ct-ret-act{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}' +
      '.ct-ret-act button{padding:9px 16px;border-radius:9px;font-weight:700;font-size:14px;cursor:pointer;border:1px solid #8fcfc2;background:#fff;color:#0f766e}' +
      '.ct-ret-act button.go{background:#1e9484;border-color:#1e9484;color:#fff}.ct-ret-act button:disabled{opacity:.6}' +
      '.ct-ret-msg{color:#b91c1c;font-size:13px;margin-top:8px;min-height:16px;text-align:right}';
    document.head.appendChild(st);
  }
  function open(job, opts, done) {
    opts = opts || {};
    ensureStyle();
    var reasons = (opts.reasons && opts.reasons.length) ? opts.reasons : REASONS, people = opts.people || [];
    var wrap = document.createElement('div');
    wrap.className = 'ct-ret'; wrap.setAttribute('role', 'dialog'); wrap.setAttribute('aria-modal', 'true');
    wrap.innerHTML = '<div class="ct-ret-box"><h3>&#9208;&#65039; Needs another visit</h3>' +
      '<div class="ct-ret-sub">' + esc((job.job_number ? job.job_number + ' · ' : '') + (job.title || '')) + '</div>' +
      '<label>What is still pending?</label><div class="ct-ret-chips">' + reasons.map(function (r) { return '<button type="button">' + esc(r) + '</button>'; }).join('') + '</div>' +
      '<textarea rows="2" maxlength="300" placeholder="e.g. Tile arrives Thursday, grout and caulk left"></textarea>' +
      '<div class="ct-ret-two"><div><label>Next visit</label><input type="date"></div>' +
      '<div><label>Time</label><select><option value="">Any time</option><option value="morning">Morning</option><option value="afternoon">Afternoon</option></select></div></div>' +
      (people.length ? '<label>Who goes</label><select class="ct-ret-who"><option value="">Same person</option>' + people.map(function (p) { return '<option>' + esc(p) + '</option>'; }).join('') + '</select>' : '') +
      '<div class="ct-ret-hint">No date yet? Leave it empty: the job leaves the calendar and waits in <b>Waiting to return</b> until someone gives it a day.</div>' +
      '<div class="ct-ret-act"><button type="button" class="no">Cancel</button><button type="button" class="go">Save</button></div><div class="ct-ret-msg"></div></div>';
    document.body.appendChild(wrap);
    var ta = wrap.querySelector('textarea'), date = wrap.querySelector('input[type=date]'), slot = wrap.querySelectorAll('select')[0], who = wrap.querySelector('.ct-ret-who');
    var msg = wrap.querySelector('.ct-ret-msg'), go = wrap.querySelector('.go');
    slot.value = job.time_slot || '';
    wrap.querySelector('.ct-ret-chips').onclick = function (e) {
      var b = e.target.closest('button'); if (!b) return;
      b.classList.toggle('on');
      var picked = Array.prototype.filter.call(this.children, function (x) { return x.classList.contains('on'); }).map(function (x) { return x.textContent; });
      var extra = ta.value.split(' — ').slice(1).join(' — ');
      ta.value = picked.join(', ') + (extra ? ' — ' + extra : (picked.length ? ' — ' : ''));
      ta.focus();
    };
    function close() { wrap.remove(); }
    wrap.querySelector('.no').onclick = close;
    wrap.addEventListener('click', function (e) { if (e.target === wrap) close(); });
    go.onclick = function () {
      var reason = ta.value.replace(/\s*—\s*$/, '').trim();
      if (reason.length < 2) { msg.textContent = 'Say what is still pending.'; ta.focus(); return; }
      go.disabled = true; msg.textContent = '';
      var body = {reason: reason, date: date.value || '', time_slot: slot.value};
      if (who && who.value) body.assigned_to = who.value;
      fetch('/api/contractor/jobs/' + encodeURIComponent(job.id) + '/return', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
        .then(function (r) { return r.json(); }).then(function (res) {
          go.disabled = false;
          if (!res.ok) { msg.textContent = res.error || 'Could not save'; return; }
          close(); if (done) done(res.job);
        }).catch(function () { go.disabled = false; msg.textContent = 'Connection error. Try again.'; });
    };
    ta.focus();
  }
  window.CTReturn = {open: open};
})();
