/* ============================================================
   Contractor Receipt OCR — multi-WO split
   Depends on: openJobId, userName, ocrAllJobs, esc(), flash(), loadMaterials()
   ============================================================ */

var ocrImageData = null;
var ocrItems = [];
var ocrAllJobs = [];
var ocrRowCount = {};

/* ── Open / Close ── */
function openReceiptModal() {
  ocrImageData = null;
  ocrItems = [];
  ocrAllJobs = [];
  ocrRowCount = {};
  var fi = document.getElementById('ocrFileInput');
  if (fi) fi.value = '';
  show('ocrUploadHint'); hide('ocrPreview'); hide('ocrScanBtn');
  hide('ocrScanning'); hide('ocrAddBtn');
  document.getElementById('ocrResults').innerHTML = '';
  document.getElementById('receiptModal').classList.add('open');
  // Pre-load all active WOs for the picker (best-effort; runOcr also fetches)
  fetch('/api/contractor/jobs')
    .then(function(r) { return r.json(); })
    .then(function(res) {
      var list = Array.isArray(res) ? res : (res.jobs || []);
      ocrAllJobs = list.filter(function(j) {
        return j.status !== 'cancelled' && j.status !== 'completed';
      });
    });
}

function closeReceiptModal() {
  document.getElementById('receiptModal').classList.remove('open');
}

function show(id) { var e = document.getElementById(id); if (e) e.style.display = 'block'; }
function hide(id) { var e = document.getElementById(id); if (e) e.style.display = 'none'; }

/* ── File selected ── */
function ocrFileSelected(e) {
  var file = e.target.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(ev) {
    ocrImageData = ev.target.result;
    var img = document.getElementById('ocrPreview');
    img.src = ocrImageData;
    show('ocrPreview'); hide('ocrUploadHint'); show('ocrScanBtn');
    document.getElementById('ocrResults').innerHTML = '';
    hide('ocrAddBtn');
  };
  reader.readAsDataURL(file);
}

/* ── Run OCR ── */
function runOcr() {
  if (!ocrImageData) return;
  hide('ocrScanBtn');
  show('ocrScanning');
  document.getElementById('ocrResults').innerHTML = '';
  hide('ocrAddBtn');

  // Fetch OCR + jobs list in parallel — both must complete before render
  var ocrPromise = fetch('/api/contractor/jobs/' + openJobId + '/receipt-ocr', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_data: ocrImageData })
  }).then(function(r) { return r.json(); });

  var jobsPromise = fetch('/api/contractor/jobs')
    .then(function(r) { return r.json(); })
    .then(function(res) {
      // Endpoint returns a raw array, not {jobs:[...]}
      var list = Array.isArray(res) ? res : (res.jobs || []);
      return list.filter(function(j) {
        return j.status !== 'cancelled' && j.status !== 'completed';
      });
    });

  Promise.all([ocrPromise, jobsPromise])
    .then(function(results) {
      var ocrRes = results[0];
      ocrAllJobs = results[1];
      hide('ocrScanning');
      if (ocrRes.error) {
        document.getElementById('ocrResults').innerHTML =
          '<div style="color:#ef4444;padding:12px;">Error: ' + esc(ocrRes.error) + '</div>';
        return;
      }
      ocrItems = ocrRes.items || [];
      ocrRowCount = {};
      renderOcrResults();
    })
    .catch(function() {
      hide('ocrScanning');
      document.getElementById('ocrResults').innerHTML =
        '<div style="color:#ef4444;padding:12px;">Connection error. Try again.</div>';
    });
}

/* ── Render results with multi-WO split ── */
function renderOcrResults() {
  if (!ocrItems.length) {
    document.getElementById('ocrResults').innerHTML =
      '<div style="color:#64748b;text-align:center;padding:16px;">No line items found.</div>';
    return;
  }

  var container = document.getElementById('ocrResults');
  container.innerHTML = '';

  var hdr = document.createElement('div');
  hdr.style.cssText = 'font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.4px;margin-bottom:10px;';
  hdr.textContent = 'Found ' + ocrItems.length + ' item(s) — assign quantities per Work Order:';
  container.appendChild(hdr);

  ocrItems.forEach(function(item, i) {
    var itemDiv = document.createElement('div');
    itemDiv.className = 'ocr-item';
    itemDiv.id = 'ocrItem_' + i;

    var total = (parseFloat(item.unit_cost || 0) * parseFloat(item.qty || 1)).toFixed(2);
    var unit = item.unit || 'ea';

    // Name + detail
    var name = document.createElement('div');
    name.className = 'ocr-item-name';
    name.textContent = item.name || 'Item';
    itemDiv.appendChild(name);

    var detail = document.createElement('div');
    detail.className = 'ocr-item-detail';
    detail.innerHTML = 'Total: <strong>' + item.qty + ' ' + esc(unit) + '</strong>' +
      ' @ $' + parseFloat(item.unit_cost || 0).toFixed(2) + ' ea' +
      ' = $' + parseFloat(item.total || total).toFixed(2);
    itemDiv.appendChild(detail);

    // WO rows container
    var assignDiv = document.createElement('div');
    assignDiv.id = 'ocrAssign_' + i;
    assignDiv.style.cssText = 'margin:8px 0;display:flex;flex-direction:column;gap:6px;';
    assignDiv.appendChild(buildWoRow(i, 0, openJobId, item.qty, unit));
    itemDiv.appendChild(assignDiv);

    // Bottom row: "+ Add WO" + Stock
    var foot = document.createElement('div');
    foot.style.cssText = 'display:flex;gap:8px;align-items:center;margin-top:6px;flex-wrap:wrap;';

    var addBtn = document.createElement('button');
    addBtn.className = 'btn-add-step';
    addBtn.style.cssText = 'font-size:11px;padding:4px 10px;';
    addBtn.textContent = '+ Add WO';
    (function(idx, u) {
      addBtn.onclick = function() { ocrAddWoRow(idx, u); };
    }(i, unit));
    foot.appendChild(addBtn);

    var spacer = document.createElement('div');
    spacer.style.flex = '1';
    foot.appendChild(spacer);

    var stockLbl = document.createElement('label');
    stockLbl.style.cssText = 'font-size:11px;color:#94a3b8;font-weight:700;';
    stockLbl.textContent = '📦 Stock:';
    foot.appendChild(stockLbl);

    var stockInput = document.createElement('input');
    stockInput.type = 'number';
    stockInput.id = 'ocrStock_' + i;
    stockInput.value = '0';
    stockInput.min = '0';
    stockInput.step = '0.01';
    stockInput.style.cssText = 'width:70px;padding:5px 8px;background:#0f1117;border:1px solid #2a2d3e;border-radius:7px;color:#e2e8f0;font-size:13px;text-align:center;';
    (function(idx) { stockInput.oninput = function() { ocrUpdateBadge(idx); }; }(i));
    foot.appendChild(stockInput);

    var unitSpan = document.createElement('span');
    unitSpan.style.cssText = 'font-size:11px;color:#64748b;';
    unitSpan.textContent = unit;
    foot.appendChild(unitSpan);
    itemDiv.appendChild(foot);

    // Badge
    var badge = document.createElement('div');
    badge.id = 'ocrBadge_' + i;
    badge.style.cssText = 'font-size:11px;margin-top:6px;text-align:right;';
    itemDiv.appendChild(badge);

    container.appendChild(itemDiv);
    ocrUpdateBadge(i);
  });

  show('ocrAddBtn');
}

/* ── Build a WO assignment row ── */
function buildWoRow(itemIdx, rowIdx, selectedJobId, qty, unit) {
  var rid = 'r' + itemIdx + '_' + rowIdx;
  var row = document.createElement('div');
  row.id = 'ocrRow_' + rid;
  row.style.cssText = 'display:flex;align-items:center;gap:6px;';

  // Job selector
  var sel = document.createElement('select');
  sel.id = 'ocrJob_' + rid;
  sel.style.cssText = 'flex:1;padding:5px 8px;background:#1a1d27;border:1px solid #2a2d3e;border-radius:7px;color:#e2e8f0;font-size:12px;';
  ocrAllJobs.forEach(function(j) {
    var opt = document.createElement('option');
    opt.value = j.id;
    opt.textContent = (j.job_number || '') + ' – ' + (j.title || '');
    if (j.id === selectedJobId) opt.selected = true;
    sel.appendChild(opt);
  });
  (function(idx) { sel.onchange = function() { ocrUpdateBadge(idx); }; }(itemIdx));
  row.appendChild(sel);

  // Qty input
  var qtyInput = document.createElement('input');
  qtyInput.type = 'number';
  qtyInput.id = 'ocrQty_' + rid;
  qtyInput.value = qty;
  qtyInput.min = '0';
  qtyInput.step = '0.01';
  qtyInput.style.cssText = 'width:70px;padding:5px 8px;background:#0f1117;border:1px solid #2a2d3e;border-radius:7px;color:#e2e8f0;font-size:13px;text-align:center;';
  (function(idx) { qtyInput.oninput = function() { ocrUpdateBadge(idx); }; }(itemIdx));
  row.appendChild(qtyInput);

  // Unit label
  var unitSpan = document.createElement('span');
  unitSpan.style.cssText = 'font-size:11px;color:#64748b;white-space:nowrap;';
  unitSpan.textContent = unit;
  row.appendChild(unitSpan);

  // Delete button (only for rows > 0)
  if (rowIdx > 0) {
    var delBtn = document.createElement('button');
    delBtn.style.cssText = 'background:none;border:none;color:#475569;font-size:16px;cursor:pointer;line-height:1;padding:0 4px;';
    delBtn.textContent = '×';
    (function(r, idx) {
      delBtn.onclick = function() {
        var el = document.getElementById('ocrRow_' + r);
        if (el) el.remove();
        ocrUpdateBadge(idx);
      };
    }(rid, itemIdx));
    row.appendChild(delBtn);
  } else {
    var ph = document.createElement('div');
    ph.style.width = '24px';
    row.appendChild(ph);
  }

  return row;
}

function ocrAddWoRow(itemIdx, unit) {
  if (!ocrRowCount[itemIdx]) ocrRowCount[itemIdx] = 1;
  else ocrRowCount[itemIdx]++;
  var rowIdx = ocrRowCount[itemIdx];
  var container = document.getElementById('ocrAssign_' + itemIdx);
  if (container) container.appendChild(buildWoRow(itemIdx, rowIdx, '', 0, unit));
  ocrUpdateBadge(itemIdx);
}

/* ── Badge: show remaining unassigned ── */
function ocrUpdateBadge(i) {
  var item = ocrItems[i];
  if (!item) return;
  var total = parseFloat(item.qty || 0);
  var assigned = 0;
  var container = document.getElementById('ocrAssign_' + i);
  if (container) {
    container.querySelectorAll('input[type=number]').forEach(function(inp) {
      assigned += parseFloat(inp.value || 0);
    });
  }
  var stock = parseFloat((document.getElementById('ocrStock_' + i) || {}).value || 0);
  var remaining = total - assigned - stock;
  var badge = document.getElementById('ocrBadge_' + i);
  if (!badge) return;
  var unit = item.unit || 'ea';
  if (Math.abs(remaining) < 0.001) {
    badge.innerHTML = '<span style="color:#22c55e;">✓ Fully allocated (' + total + ' ' + esc(unit) + ')</span>';
  } else if (remaining > 0) {
    badge.innerHTML = '<span style="color:#f59e0b;">⚠ ' + remaining.toFixed(2) + ' ' + esc(unit) + ' unassigned</span>';
  } else {
    badge.innerHTML = '<span style="color:#ef4444;">↑ Over-assigned by ' + Math.abs(remaining).toFixed(2) + ' ' + esc(unit) + '</span>';
  }
}

/* ── Submit: POST to each WO ── */
function addOcrMaterials() {
  if (!ocrItems.length) return;
  var promises = [];
  var stockSummary = [];

  ocrItems.forEach(function(item, i) {
    var container = document.getElementById('ocrAssign_' + i);
    if (container) {
      container.querySelectorAll('[id^=ocrRow_]').forEach(function(row) {
        var rid = row.id.replace('ocrRow_', '');
        var jobSel = document.getElementById('ocrJob_' + rid);
        var qtyInp = document.getElementById('ocrQty_' + rid);
        if (!jobSel || !qtyInp) return;
        var jobId = jobSel.value;
        var qty = parseFloat(qtyInp.value || 0);
        if (jobId && qty > 0) {
          promises.push(
            fetch('/api/contractor/jobs/' + jobId + '/materials', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                material_name: item.name,
                qty: qty,
                unit: item.unit || 'each',
                unit_cost: item.unit_cost || 0,
                added_by: userName
              })
            })
          );
        }
      });
    }
    var stockQty = parseFloat((document.getElementById('ocrStock_' + i) || {}).value || 0);
    if (stockQty > 0) {
      stockSummary.push(stockQty.toFixed(2) + ' ' + (item.unit || 'ea') + ' of ' + (item.name || 'item') + ' → Stock');
    }
  });

  Promise.all(promises).then(function() {
    closeReceiptModal();
    loadMaterials();
    var msg = promises.length + ' material assignment' + (promises.length !== 1 ? 's' : '') + ' saved.';
    if (stockSummary.length) msg += ' Stock noted: ' + stockSummary.join(', ');
    flash(msg);
  });
}
