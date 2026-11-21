"""Work-order photos in Supabase Storage: upload, view, lightbox, delete, fallback and moving old ones.
Run:  python tests/test_storage.py"""
import base64

from harness import *  # noqa: F401,F403
from harness import STORAGE, STORAGE_DOWN

seed()
JPG = b"\xff\xd8\xff\xe0" + b"fake-jpeg-bytes" * 50
URI = "data:image/jpeg;base64," + base64.b64encode(JPG).decode()
JOB = send("POST", "/api/contractor/jobs", "Hana", {"title": "Storage test"}).json["job"]["id"]  # real UUID: the company guard checks those

# ── new photos go to Storage, not the database ──
r = send("POST", f"/api/contractor/jobs/{JOB}/photos", "Mia", {"photo_data": URI, "caption": "Roof before"})
check("upload ok", r.status_code == 200 and r.json["ok"])
pid = r.json["photo"]["id"]
row = next(p for p in DB["job_photos"] if p["id"] == pid)
check("database keeps no image, only the path", row.get("photo_data") is None and row["storage_path"].startswith(JOB + "/"))
check("file is in the private bucket", STORAGE.get("job-photos/" + row["storage_path"], (None,))[0] == JPG)
check("upload answer never shows the storage path", "storage_path" not in r.json["photo"])

img = get(f"/api/contractor/jobs/{JOB}/photos/{pid}/img", "Hana")
check("image served by the app", img.status_code == 200 and img.data == JPG and img.mimetype == "image/jpeg")
check("image not cached by shared caches", "private" in img.headers.get("Cache-Control", ""))
one = get(f"/api/contractor/jobs/{JOB}/photos/{pid}", "Hana").json
check("lightbox gets the app route, never a storage URL",
      one["photo_data"] == f"/api/contractor/jobs/{JOB}/photos/{pid}/img" and "storage_path" not in one and "supabase" not in str(one))

# ── company isolation ──
check("other company can't see the image", get(f"/api/contractor/jobs/{JOB}/photos/{pid}/img", "Bob").status_code == 404)
check("anonymous can't see the image", client().get(f"/api/contractor/jobs/{JOB}/photos/{pid}/img").status_code in (401, 403, 404))
check("other company can't upload to it", send("POST", f"/api/contractor/jobs/{JOB}/photos", "Bob", {"photo_data": URI}).status_code == 404)

# ── only images we accept ──
bad = send("POST", f"/api/contractor/jobs/{JOB}/photos", "Mia", {"photo_data": "data:text/html;base64,PGgxPmhpPC9oMT4="})
check("non-image refused", bad.status_code == 400)
check("non-image never reaches Storage", all(not k.endswith(".html") for k in STORAGE) and len(STORAGE) == 1)

# ── Storage down: photo kept in the database, nothing lost ──
STORAGE_DOWN["on"] = True
r = send("POST", f"/api/contractor/jobs/{JOB}/photos", "Mia", {"photo_data": URI, "caption": "fallback"})
STORAGE_DOWN["on"] = False
fb = next(p for p in DB["job_photos"] if p["id"] == r.json["photo"]["id"])
check("fallback keeps the photo in the database", r.json["ok"] and fb["photo_data"] == URI and not fb.get("storage_path"))
check("old-style photo still served", get(f"/api/contractor/jobs/{JOB}/photos/{fb['id']}/img", "Hana").data == JPG)

# ── moving old photos (owner only) ──
check("move: user refused", send("POST", "/api/platform/storage/move-photos", "Mia", {}).status_code == 403)
check("move: manager refused", send("POST", "/api/platform/storage/move-photos", "Hana", {}).status_code == 403)
mv = send("POST", "/api/platform/storage/move-photos", "owner@example.com", {}).json
fb = next(p for p in DB["job_photos"] if p["id"] == fb["id"])
check("move: old photo moved and cleared from the database", mv["ok"] and mv["moved"] >= 1 and mv["left"] == 0
      and fb.get("photo_data") is None and STORAGE.get("job-photos/" + fb["storage_path"], (None,))[0] == JPG)
check("move: still viewable after moving", get(f"/api/contractor/jobs/{JOB}/photos/{fb['id']}/img", "Hana").data == JPG)
check("move: recorded in audit_log", any(a.get("action") == "storage.photos_moved" for a in DB["audit_log"]))

# ── deleting a photo removes its file too ──
path = row["storage_path"]
d = send("DELETE", f"/api/contractor/jobs/{JOB}/photos/{pid}", "Hana")
check("delete removes row and file", d.json["ok"] and not any(p["id"] == pid for p in DB["job_photos"])
      and ("job-photos/" + path) not in STORAGE)

# ── ERP issue photos: private bucket, images only, served by the app with a session ──
import io

owner = as_user("owner@example.com")
up = owner.post("/api/issues/upload-photo", data={"photo": (io.BytesIO(JPG), "site.jpg")}, content_type="multipart/form-data")
url = up.json.get("url", "")
check("issue photo saved, app link (never a storage URL)", up.json["ok"] and url.startswith("/api/issues/photo/") and "supabase" not in url)
name = url.rsplit("/", 1)[-1]
check("stored in the issue-photos bucket", STORAGE.get("issue-photos/" + name, (None,))[0] == JPG)
pic = owner.get(url)
check("photo served to a signed-in person", pic.status_code == 200 and pic.data == JPG and "private" in pic.headers.get("Cache-Control", ""))
check("photo hidden from anonymous", client().get(url).status_code in (401, 403, 302))
html = owner.post("/api/issues/upload-photo", data={"photo": (io.BytesIO(b"<script>alert(1)</script>"), "evil.html")},
                  content_type="multipart/form-data")
check("non-image refused (no web pages in the bucket)", html.status_code == 400 and not any(k.endswith(".html") for k in STORAGE))
fake = owner.post("/api/issues/upload-photo", data={"photo": (io.BytesIO(b"<svg onload=x>"), "x.jpg")}, content_type="multipart/form-data")
check("a file named .jpg that isn't a JPG is refused", fake.status_code == 400)
check("odd names can't be read", owner.get("/api/issues/photo/..%2Fjob-photos%2Fx.jpg").status_code == 404
      and owner.get("/api/issues/photo/x.html").status_code == 404)
qc = owner.post("/api/qc/upload-drawing", data={"drawing": (io.BytesIO(JPG), "plan.jpg"), "type": "plan"}, content_type="multipart/form-data")
check("QC drawing replaces itself and is served by the app", qc.json["ok"] and qc.json["url"] == "/api/issues/photo/qc-plan.jpg"
      and owner.post("/api/qc/upload-drawing", data={"drawing": (io.BytesIO(JPG), "plan.jpg"), "type": "plan"},
                     content_type="multipart/form-data").json["ok"])
check("debug storage route removed", owner.get("/api/test-storage").status_code == 404)

# ── Storage autopilot: images still in the database move to Storage on their own ──
for t in ("homelab_kids", "homelab_kid_photos", "homelab_blocks", "homelab_tasks", "contractor_expenses"):
    DB.setdefault(t, [])
kid = owner.post("/api/homelab/kids", json={"name": "Niño Storage"}).json["kid"]["id"]
DB["homelab_kids"][-1]["active"] = True
kp = owner.post(f"/api/homelab/kids/{kid}/photos", json={"photo_data": URI}).json["photo_id"]
blk = owner.post("/api/homelab/blocks", json={"name": "Mañana"}).json["block"]["id"]
DB["homelab_blocks"][-1]["active"] = True
task = owner.post("/api/homelab/tasks", json={"block_id": blk, "title": "Cepillarse", "task_image": URI}).json["task"]["id"]
DB["homelab_tasks"][-1]["active"] = True
rc = send("POST", f"/api/contractor/jobs/{JOB}/receipts", "Hana", {"photo_data": URI, "amount": 12.5, "vendor": "Store"}).json
rid = rc["receipt"]["id"]
STORAGE_DOWN["on"] = True
legacy = send("POST", f"/api/contractor/jobs/{JOB}/photos", "Mia", {"photo_data": URI, "caption": "old style"}).json["photo"]["id"]
STORAGE_DOWN["on"] = False
for row in DB["job_photos"] + DB["homelab_kid_photos"] + DB["homelab_tasks"] + DB["contractor_expenses"]:
    row.setdefault("created_at", "2026-11-01T00:00:00Z")

with A.app.test_request_context("/"):
    moved = A._storage_autopilot()
kp_row = next(r for r in DB["homelab_kid_photos"] if r["id"] == kp)
task_row = next(r for r in DB["homelab_tasks"] if r["id"] == task)
rc_row = next(r for r in DB["contractor_expenses"] if r["id"] == rid)
lg_row = next(r for r in DB["job_photos"] if r["id"] == legacy)
check("autopilot moved every kind of image", moved >= 4 and not kp_row.get("photo_data") and kp_row["photo_path"]
      and not task_row.get("task_image") and task_row["task_image_path"]
      and not rc_row.get("photo_data") and rc_row["photo_path"] and not lg_row.get("photo_data") and lg_row["storage_path"])
check("kids' photos go to their own family bucket", ("family-photos/" + kp_row["photo_path"]) in STORAGE
      and ("family-photos/" + task_row["task_image_path"]) in STORAGE and ("job-photos/" + rc_row["photo_path"]) in STORAGE)
check("autopilot recorded in audit_log", any(a.get("action") == "storage.autopilot" for a in DB["audit_log"]))
with A.app.test_request_context("/"):
    check("nothing left to move: a second run moves nothing", A._storage_autopilot() == 0)

check("kid photo still shows after moving", owner.get(f"/api/homelab/kids/{kid}/photos/{kp}/img").data == JPG)
check("task picture still shows after moving", owner.get(f"/api/homelab/tasks/{task}/image").data == JPG)
from harness import Resp  # noqa: E402
_real_get = A.requests.get
A.requests.get = lambda url, *a, **k: (Resp([{"id": blk, "name": "Mañana", "homelab_tasks": [dict(task_row, active=True)]}])
                                       if "/homelab_blocks?" in url else _real_get(url, *a, **k))
blocks = owner.get("/api/homelab/blocks").json
A.requests.get = _real_get
tl = [t for b in blocks for t in b["tasks"] if t["id"] == task][0]
check("task list sends the picture's link, never the image itself", tl["task_image"] == f"/api/homelab/tasks/{task}/image"
      and "task_image_path" not in tl)
ph = get(f"/api/contractor/jobs/{JOB}/receipts/{rid}", "Hana").json["photo_data"]
check("receipt lightbox gets the app link", ph == f"/api/contractor/jobs/{JOB}/receipts/{rid}/img")
check("receipt photo served from Storage", get(ph, "Hana").data == JPG)
check("other company can't see the receipt photo", get(ph, "Bob").status_code == 404)
check("old job photo still shows after moving", get(f"/api/contractor/jobs/{JOB}/photos/{legacy}/img", "Hana").data == JPG)

# deleting removes the file too
kpath = kp_row["photo_path"]
owner.delete(f"/api/homelab/kids/{kid}/photos/{kp}")
check("deleting a kid photo removes its file", ("family-photos/" + kpath) not in STORAGE)
rpath = rc_row["photo_path"]
send("DELETE", f"/api/contractor/jobs/{JOB}/receipts/{rid}", "Hana")
check("deleting a receipt removes its file", ("job-photos/" + rpath) not in STORAGE)

# an image that can't be decoded stays in the database (never lost) and isn't retried forever
DB["homelab_kid_photos"].append({"id": "weird", "kid_id": kid, "photo_data": "data:image/heic;base64,AAAA", "created_at": "2026-01-01"})
with A.app.test_request_context("/"):
    A._storage_autopilot()
check("an image Storage can't take stays in the database", next(r for r in DB["homelab_kid_photos"] if r["id"] == "weird")["photo_data"])

done("storage")
