/* Dictate a work order: speech-to-text in the browser, then Claude fills the form.
   Uses setWoMode / addWoStepField / esc from the projects page. */
var woMaterials = [];
var dictRec = null, dictOn = false, dictBase = '';

function dictMsg(t, ok) {
  var m = document.getElementById('dictMsg');
  m.textContent = t; m.style.color = ok === false ? '#dc2626' : ok ? '#15803d' : '#64748b';
}

function renderWoMaterials() {
  var box = document.getElementById('dictMats');
  if (!woMaterials.length) { box.innerHTML = ''; return; }
  box.innerHTML = '<div class="dict-mats-title">Materials to bring</div>' + woMaterials.map(function (m, i) {
    return '<span class="dict-mat">' + esc(m.qty) + ' ' + esc(m.unit) + ' ' + esc(m.name) +
      '<button type="button" onclick="woMaterials.splice(' + i + ',1);renderWoMaterials()" aria-label="Remove">&#215;</button></span>';
  }).join('');
}

function resetDictation() {
  if (dictRec && dictOn) dictRec.stop();
  woMaterials = []; renderWoMaterials();
  document.getElementById('dictText').value = '';
  dictMsg('');
}

function uploadWoMaterials(jobId) {
  var list = woMaterials.slice(); woMaterials = []; renderWoMaterials();
  return list.reduce(function (p, m) {
    return p.then(function () {
      return fetch('/api/contractor/jobs/' + jobId + '/materials', {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({material_name: m.name, qty: m.qty, unit: m.unit, unit_cost: 0, added_by: (window.CT && CT.user) || ''})});
    });
  }, Promise.resolve());
}

function fillFromDictation() {
  var text = document.getElementById('dictText').value.trim(), btn = document.getElementById('dictFill');
  if (text.length < 5) { dictMsg('Say or type what the job is first.', false); return; }
  btn.disabled = true; dictMsg('✨ Filling the form...');
  fetch('/api/contractor/wo-from-text', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: text})})
    .then(function (r) { return r.json(); }).then(function (d) {
      btn.disabled = false;
      if (!d.ok) { dictMsg(d.error || 'Could not fill the form.', false); return; }
      var set = function (id, v) { if (v) document.getElementById(id).value = v; };
      set('woTitle', d.title); set('woDesc', d.description); set('woClient', d.client_name);
      set('woSite', d.location); set('woClientEmail', d.client_email);
      if (d.location && window.autofillFrom) autofillFrom('location');
      document.getElementById('woPriority').value = d.priority || 'normal';
      if (d.date) { document.getElementById('woStart').value = d.date; window._woSchedDate = d.date; if (!window.woDueTouched) document.getElementById('woDue').value = d.date; }
      if (d.time_slot && window.setWoSlot) setWoSlot(d.time_slot);
      if (d.est_hours && window.setWoHours) setWoHours(d.est_hours);
      setWoMode(d.mode === 'steps' ? 'steps' : 'simple');
      if (d.mode === 'steps' && d.steps.length) {
        var c = document.getElementById('woStepFields'); c.innerHTML = ''; woStepCount = 0;
        d.steps.forEach(function (st) { addWoStepField(st); });
      }
      woMaterials = d.materials || []; renderWoMaterials();
      dictMsg('Done. Check everything and tap Create Work Order.', true);
    }).catch(function () { btn.disabled = false; dictMsg('Connection error.', false); });
}

(function () {
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var btn = document.getElementById('dictBtn'), lang = document.getElementById('dictLang');
  try { var saved = localStorage.getItem('ctDictLang'); if (saved) lang.value = saved; } catch (e) {}
  lang.onchange = function () { try { localStorage.setItem('ctDictLang', lang.value); } catch (e) {} };
  document.getElementById('dictFill').onclick = fillFromDictation;
  if (!SR) {
    btn.style.display = 'none';
    document.getElementById('dictHint').textContent = 'Tap the box below, then the 🎤 on your phone keyboard and speak. Then tap Fill the form.';
    return;
  }
  var autoStart = false;
  window.startDictation = function () { autoStart = true; btn.click(); };
  btn.onclick = function () {
    if (dictOn) { dictRec.stop(); return; }
    dictRec = new SR();
    dictRec.lang = lang.value; dictRec.continuous = true; dictRec.interimResults = true;
    var ta = document.getElementById('dictText');
    dictBase = ta.value ? ta.value.trim() + ' ' : '';
    dictRec.onresult = function (e) {
      var fin = '', interim = '';
      for (var i = 0; i < e.results.length; i++) {
        if (e.results[i].isFinal) fin += e.results[i][0].transcript + ' ';
        else interim += e.results[i][0].transcript;
      }
      ta.value = (dictBase + fin + interim).replace(/\s+/g, ' ').trimStart();
    };
    dictRec.onerror = function (e) {
      if ((e.error === 'not-allowed' || e.error === 'service-not-allowed') && autoStart) { dictMsg('Tap the green button and speak.', true); btn.focus(); }
      else if (e.error === 'not-allowed' || e.error === 'service-not-allowed') dictMsg('Allow the microphone for this site, or use the 🎤 on your keyboard.', false);
      else if (e.error === 'network') dictMsg('Dictation needs internet. Type it, or try again with signal.', false);
      else if (e.error !== 'no-speech' && e.error !== 'aborted') dictMsg('Dictation stopped (' + e.error + ').', false);
    };
    dictRec.onend = function () {
      autoStart = false;
      dictOn = false; btn.classList.remove('rec'); btn.innerHTML = '&#127908; Tap and speak';
      if (document.getElementById('dictText').value.trim().length >= 5) fillFromDictation();
    };
    try { dictRec.start(); } catch (err) { dictMsg(autoStart ? 'Tap the green button and speak.' : 'Could not start the microphone.', autoStart); autoStart = false; return; }
    dictOn = true; btn.classList.add('rec'); btn.innerHTML = '&#9209;&#65039; Listening... tap to stop';
    dictMsg('Speak: what to do, client, address, materials, when.');
  };
})();
