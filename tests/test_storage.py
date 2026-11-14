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

done("storage")
