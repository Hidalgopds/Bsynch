/* Contractor job receipts: photo of the ticket + store + amount.
   Uses openJobId / esc() from the projects page. */
var rcPhoto = null;

function rcMoney(n) { return '$' + (parseFloat(n) || 0).toFixed(2); }

function rcShrink(file) {
  return new Promise(function (resolve, reject) {
    var reader = new FileReader();
    reader.onerror = reject;
    reader.onload = function (e) {
      var img = new Image();
      img.onerror = reject;
      img.onload = function () {
        var max = 1400, w = img.width, h = img.height, k = Math.min(1, max / Math.max(w, h));
        var cv = document.createElement('canvas');
        cv.width = Math.round(w * k); cv.height = Math.round(h * k);
        cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
        resolve(cv.toDataURL('image/jpeg', 0.72));
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function loadReceipts() {
  var body = document.getElementById('jpBody');
  body.innerHTML = '<div class="spinner">Loading...</div>';
  fetch('/api/contractor/jobs/' + openJobId + '/receipts').then(function (r) { return r.json(); }).then(renderReceipts);
}

function renderReceipts(list) {
  list = Array.isArray(list) ? list : [];
  rcPhoto = null;
  var total = list.reduce(function (s, r) { return s + (parseFloat(r.amount) || 0); }, 0);
  var today = new Date().toISOString().slice(0, 10);
  var html = '<div class="rc-form">'
    + '<h4 style="margin:0 0 4px">Add a purchase receipt</h4>'
    + '<div class="rc-hint">Things you bought for this job (store tickets). Materials you used go in the Materials tab.</div>'
    + '<label class="rc-photo" id="rcPhotoBox"><input type="file" accept="image/*" capture="environment" id="rcFile" hidden>'
    + '<span id="rcPhotoLbl">&#128247; Take photo of the ticket</span><img id="rcPreview" alt="" style="display:none"></label>'
    + '<button class="btn-add-step" id="rcReadBtn" style="display:none;width:100%;margin-bottom:8px;">&#129302; Read store and total from photo</button>'
    + '<div class="rc-row"><input class="form-input" id="rcVendor" placeholder="Store (e.g. Home Depot)" maxlength="120">'
    + '<input class="form-input" id="rcAmount" type="number" min="0" step="0.01" inputmode="decimal" placeholder="Total $"></div>'
    + '<div class="rc-row"><input class="form-input" id="rcDate" type="date" value="' + today + '">'
    + '<input class="form-input" id="rcNotes" placeholder="What was it for? (optional)" maxlength="500"></div>'
    + '<button class="btn-save" id="rcSave" style="width:100%">Save receipt</button>'
    + '<div class="rc-msg" id="rcMsg"></div></div>';
  html += '<div class="rc-total"><span>Purchases on this job</span><b>' + rcMoney(total) + '</b></div>';
  if (!list.length) {
    html += '<div style="text-align:center;padding:20px;color:#64748b;font-size:13px;">No receipts yet.</div>';
  } else {
    list.forEach(function (r) {
      html += '<div class="rc-item" id="rc-' + r.id + '">'
        + '<button class="rc-thumb" onclick="rcView(\'' + r.id + '\')" title="View photo">&#129534;</button>'
        + '<div class="rc-info"><b>' + esc(r.vendor || 'Receipt') + '</b><span>' + esc(r.receipt_date || '') + (r.notes ? ' &middot; ' + esc(r.notes) : '') + (r.added_by ? ' &middot; ' + esc(r.added_by) : '') + '</span></div>'
        + '<div class="rc-amt">' + rcMoney(r.amount) + '</div>'
        + '<button class="step-del" onclick="rcDelete(\'' + r.id + '\')" title="Delete">&#215;</button></div>';
    });
  }
  document.getElementById('jpBody').innerHTML = html;

  document.getElementById('rcFile').onchange = function () {
    var f = this.files && this.files[0];
    if (!f) return;
    document.getElementById('rcPhotoLbl').textContent = 'Processing photo...';
    rcShrink(f).then(function (data) {
      rcPhoto = data;
      var img = document.getElementById('rcPreview');
      img.src = data; img.style.display = 'block';
      document.getElementById('rcPhotoLbl').textContent = 'Tap to retake';
      document.getElementById('rcReadBtn').style.display = '';
    }).catch(function () { document.getElementById('rcPhotoLbl').textContent = 'Could not read that image. Try again.'; });
  };
  document.getElementById('rcReadBtn').onclick = function () {
    if (!rcPhoto) return;
    var btn = this; btn.disabled = true; btn.textContent = 'Reading receipt...';
    fetch('/api/contractor/receipt-read', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({image_data: rcPhoto})})
      .then(function (r) { return r.json(); }).then(function (d) {
        btn.disabled = false; btn.innerHTML = '&#129302; Read store and total from photo';
        if (!d.ok) { rcMsg(d.error || 'Could not read it. Type the amount.', false); return; }
        if (d.vendor) document.getElementById('rcVendor').value = d.vendor;
        if (d.total) document.getElementById('rcAmount').value = d.total.toFixed(2);
        if (/^\d{4}-\d{2}-\d{2}$/.test(d.date)) document.getElementById('rcDate').value = d.date;
        rcMsg('Check the values and tap Save.', true);
      }).catch(function () { btn.disabled = false; btn.innerHTML = '&#129302; Read store and total from photo'; rcMsg('Connection error.', false); });
  };
  document.getElementById('rcSave').onclick = function () {
    var btn = this, amount = parseFloat(document.getElementById('rcAmount').value || 0);
    if (!rcPhoto && !(amount > 0)) { rcMsg('Add a photo or the total.', false); return; }
    btn.disabled = true; btn.textContent = 'Saving...';
    fetch('/api/contractor/jobs/' + openJobId + '/receipts', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
      vendor: document.getElementById('rcVendor').value, amount: amount,
      receipt_date: document.getElementById('rcDate').value || null,
      notes: document.getElementById('rcNotes').value, photo_data: rcPhoto
    })}).then(function (r) { return r.json(); }).then(function (d) {
      btn.disabled = false; btn.textContent = 'Save receipt';
      if (!d.ok) { rcMsg(d.error || 'Could not save.', false); return; }
      loadReceipts();
    }).catch(function () { btn.disabled = false; btn.textContent = 'Save receipt'; rcMsg('Connection error.', false); });
  };
}

function rcMsg(t, ok) { var m = document.getElementById('rcMsg'); if (m) { m.textContent = t; m.style.color = ok ? '#22c55e' : '#f87171'; } }

function rcView(id) {
  fetch('/api/contractor/jobs/' + openJobId + '/receipts/' + id).then(function (r) { return r.json(); }).then(function (d) {
    if (!d.photo_data) { alert('This receipt has no photo.'); return; }
    var lb = document.getElementById('lightbox'), img = document.getElementById('lightboxImg');
    if (lb && img) { img.src = d.photo_data; lb.classList.add('open'); }
  });
}

function rcDelete(id) {
  if (!confirm('Delete this receipt?')) return;
  fetch('/api/contractor/jobs/' + openJobId + '/receipts/' + id, {method: 'DELETE'}).then(function () { loadReceipts(); });
}

/* Visits: each trip to the job with a description of what was done. */
function loadVisits() {
  document.getElementById('jpBody').innerHTML = '<div class="spinner">Loading...</div>';
  fetch('/api/contractor/jobs/' + openJobId + '/visits').then(function (r) { return r.json(); }).then(renderVisits);
}

function renderVisits(list) {
  list = Array.isArray(list) ? list : [];
  var today = new Date().toISOString().slice(0, 10);
  var html = '<div class="rc-form">'
    + '<h4 style="margin:0 0 4px">Add a visit</h4>'
    + '<div class="rc-hint">Each time you go to this job, write what you did.</div>'
    + '<div class="rc-row"><input class="form-input" id="vDate" type="date" value="' + today + '">'
    + '<input class="form-input" id="vHours" type="number" min="0" max="24" step="0.25" inputmode="decimal" placeholder="Hours (optional)"></div>'
    + '<textarea class="form-input" id="vDesc" rows="3" maxlength="2000" placeholder="What was done on this visit?" style="margin-bottom:8px;"></textarea>'
    + '<button class="btn-save" id="vSave" style="width:100%">Save visit</button>'
    + '<div class="rc-msg" id="vMsg"></div></div>';
  var hours = list.reduce(function (s, v) { return s + (parseFloat(v.hours) || 0); }, 0);
  html += '<div class="rc-total"><span>' + list.length + ' visit' + (list.length === 1 ? '' : 's') + '</span><b>' + (hours ? hours + ' h' : '') + '</b></div>';
  if (!list.length) html += '<div style="text-align:center;padding:20px;color:#64748b;font-size:13px;">No visits yet.</div>';
  list.slice().reverse().forEach(function (v, i) {
    var n = list.length - i;
    html += '<div class="visit"><div class="visit-top"><b>Visit ' + n + '</b><span>' + esc(v.visit_date || '') + (v.hours ? ' &middot; ' + esc(v.hours) + ' h' : '') + (v.created_by ? ' &middot; ' + esc(v.created_by) : '') + '</span>'
      + '<button class="step-del" onclick="deleteVisit(\'' + v.id + '\')" title="Delete">&#215;</button></div>'
      + '<div class="visit-desc">' + esc(v.description) + '</div></div>';
  });
  document.getElementById('jpBody').innerHTML = html;
  document.getElementById('vSave').onclick = function () {
    var btn = this, desc = document.getElementById('vDesc').value.trim(), m = document.getElementById('vMsg');
    if (desc.length < 3) { m.style.color = '#f87171'; m.textContent = 'Write what was done.'; return; }
    var body = {visit_date: document.getElementById('vDate').value || null, hours: document.getElementById('vHours').value, description: desc};
    var pos = window.CT && CT.lastPos;
    if (pos) { body.lat = pos.lat; body.lng = pos.lng; }
    btn.disabled = true; btn.textContent = 'Saving...';
    fetch('/api/contractor/jobs/' + openJobId + '/visits', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
      .then(function (r) { return r.json(); }).then(function (d) {
        btn.disabled = false; btn.textContent = 'Save visit';
        if (!d.ok) { m.style.color = '#f87171'; m.textContent = d.error || 'Could not save.'; return; }
        if (openJobData && openJobData.status === 'open') openJobData.status = 'in_progress';
        loadVisits();
      }).catch(function () { btn.disabled = false; btn.textContent = 'Save visit'; m.style.color = '#f87171'; m.textContent = 'Connection error.'; });
  };
}

function deleteVisit(id) {
  if (!confirm('Delete this visit?')) return;
  fetch('/api/contractor/jobs/' + openJobId + '/visits/' + id, {method: 'DELETE'}).then(function () { loadVisits(); });
}
