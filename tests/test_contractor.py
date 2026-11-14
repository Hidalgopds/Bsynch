"""Contractor area: work orders, company isolation, client folders, invoices and the archive copy.
Run:  python tests/test_contractor.py"""
from harness import *  # noqa: F401,F403

seed()
anon = client()

# ── work orders and company isolation ──
r = send("POST", "/api/contractor/jobs", "Hana", {"title": "Fix fence", "client_name": "Lee", "client_email": "lee@example.com"})
check("manager creates a work order in her company", r.json["ok"] and r.json["job"]["company"] == "hicons")
check("empty title refused", send("POST", "/api/contractor/jobs", "Hana", {"title": " "}).status_code == 400)
mine = get("/api/contractor/jobs", "Hana").json
mine = mine.get("jobs", mine) if isinstance(mine, dict) else mine
check("Hicons sees its own work orders", any(j["id"] == "j1" for j in mine))
check("Hicons never sees Bsynch work orders", not any(j.get("company") == "bsynch" for j in mine))
theirs = get("/api/contractor/jobs", "Bob").json
theirs = theirs.get("jobs", theirs) if isinstance(theirs, dict) else theirs
check("Bsynch never sees Hicons work orders", not any(j.get("company") == "hicons" for j in theirs))
check("anonymous can't list work orders", anon.get("/api/contractor/jobs").status_code in (401, 403))
check("new client remembered in contacts", any(c.get("company") == "hicons" and c.get("name") == "Lee" for c in DB["contractor_contacts"]))
check("Newbie without a company can't create", send("POST", "/api/contractor/jobs", "Newbie", {"title": "x"}).status_code == 403)

# ── client folders (client master) ──
for nm, em in [("Dana", "dana@newmark.example"), ("Zack", "zack@newmark.example"), ("Joe", "joe@gmail.com")]:
    send("POST", "/api/contractor/jobs", "Hana", {"title": "CF " + nm, "client_name": nm, "client_email": em})
cf = get("/api/contractor/hicons/client-folders", "Mia").json
check("folders: user can read, not edit", cf["ok"] and cf["folders"] == [] and cf["can_edit"] is False and any(c["name"] == "Dana" for c in cf["clients"]))
check("folders: user cannot create", send("POST", "/api/contractor/hicons/client-folders", "Mia", {"name": "X", "color": "#ff0000"}).status_code == 403)
check("folders: other company blocked", get("/api/contractor/hicons/client-folders", "Bob").status_code == 403)
r = send("POST", "/api/contractor/hicons/client-folders", "Hana", {"name": "  Newmark   Homes ", "color": "#2563EB"})
check("folders: manager creates", r.json["ok"] and r.json["folder"]["name"] == "Newmark Homes" and r.json["folder"]["color"] == "#2563eb")
fid = r.json["folder"]["id"]
check("folders: duplicate name", send("POST", "/api/contractor/hicons/client-folders", "Hana", {"name": "newmark homes"}).status_code == 409)
check("folders: bad colour", send("POST", "/api/contractor/hicons/client-folders", "Hana", {"name": "Y", "color": "red"}).status_code == 400)
check("folders: empty name", send("POST", "/api/contractor/hicons/client-folders", "Hana", {"name": "  "}).status_code == 400)
cl = {c["name"]: c["id"] for c in get("/api/contractor/hicons/client-folders", "Hana").json["clients"]}
r = send("PATCH", "/api/contractor/hicons/client-folders/" + fid, "Hana", {"name": "Newmark", "color": "#7c3aed", "client_ids": [cl["Dana"], "not-mine"]})
cf = get("/api/contractor/hicons/client-folders", "Hana").json
check("folders: rename + recolour + assign", r.json["ok"] and cf["folders"][0]["name"] == "Newmark" and cf["folders"][0]["color"] == "#7c3aed"
      and [c["name"] for c in cf["clients"] if c["folder_id"] == fid] == ["Dana"] and cf["can_edit"])
send("PATCH", "/api/contractor/hicons/client-folders/" + fid, "Hana", {"client_ids": [cl["Zack"]]})
cf = get("/api/contractor/hicons/client-folders", "Hana").json
check("folders: assignment replaces", [c["name"] for c in cf["clients"] if c["folder_id"] == fid] == ["Zack"])
send("POST", "/api/contractor/jobs", "Hana", {"title": "CF new", "client_name": "Pham", "client_email": "pham@newmark.example"})
send("POST", "/api/contractor/jobs", "Hana", {"title": "CF new2", "client_name": "Ann", "client_email": "ann@gmail.com"})
byn = {c["name"]: c["folder_id"] for c in get("/api/contractor/hicons/client-folders", "Hana").json["clients"]}
check("folders: new client with same company domain is filed", byn.get("Pham") == fid)
check("folders: gmail client not guessed", byn.get("Ann") is None)
check("folders: user cannot edit", send("PATCH", "/api/contractor/hicons/client-folders/" + fid, "Mia", {"name": "Z"}).status_code == 403)
check("folders: unknown folder 404", send("PATCH", "/api/contractor/hicons/client-folders/nope", "Hana", {"name": "Z"}).status_code == 404)
check("folders: delete keeps clients", send("DELETE", "/api/contractor/hicons/client-folders/" + fid, "Hana", None).json["ok"]
      and get("/api/contractor/hicons/client-folders", "Hana").json["folders"] == []
      and all(c.get("folder_id") is None for c in DB["contractor_contacts"] if c.get("company") == "hicons"))

# ── invoices ──
check("invoice: unfinished job refused", send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": "j1"}).status_code == 409)
send("PATCH", "/api/contractor/jobs/j1", "Hana", {"progress_pct": 100})
j1 = [j for j in DB["contractor_jobs"] if j["id"] == "j1"][0]
j1["service_price"] = 0
check("invoice: no price refused", send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": "j1"}).status_code == 409)
j1["service_price"] = 850
check("invoice: user without invoicing permission refused", send("POST", "/api/contractor/hicons/invoices", "Mia", {"job_id": "j1"}).status_code == 403)
check("invoice: other company refused", send("POST", "/api/contractor/hicons/invoices", "Bob", {"job_id": "j1"}).status_code == 403)
r = send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": "j1"})
check("invoice: finished, priced job gets a numbered invoice", r.json.get("ok") and r.json["invoice"]["invoice_number"].startswith("H"))
inv2 = r.json["invoice"]
check("invoice: second invoice for the same job refused", send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": "j1"}).status_code == 409)
check("invoice: Bsynch can't open a Hicons invoice", get("/api/contractor/invoices/" + inv2["id"], "Bob").status_code == 403)

# ── archive copy of sent invoices ──
check("archive email validated", send("POST", "/api/contractor/hicons/profile", "Hana", {"archive_email": "not-an-email"}).status_code == 400)
check("archive email saved", send("POST", "/api/contractor/hicons/profile", "Hana", {"archive_email": "Archive@Hicons.example"}).json["ok"])
MAIL.clear()
r = send("POST", "/api/contractor/invoices/" + inv2["id"] + "/send", "Hana", {"to": ["c@example.com"], "cc": ["a@example.com"]})
cp = [m for m in MAIL if m["to"] == ["archive@hicons.example"]]
check("sent invoice copied to the archive inbox, client never sees it",
      r.json["ok"] and len(cp) == 1 and "[Copy] Invoice" in cp[0]["subject"] and "c@example.com" in cp[0]["html"]
      and all("archive@hicons.example" not in (m["to"] + m["cc"]) for m in MAIL if m not in cp))
inv_row = [x for x in DB["contractor_invoices"] if x["id"] == inv2["id"]][0]
check("sent invoice is marked sent with a public link", inv_row.get("status") == "sent" and inv_row.get("public_token"))
pub = anon.get("/api/public/invoice/" + inv_row["public_token"])
check("client opens the invoice from the link without signing in", pub.status_code == 200 and pub.json.get("ok", True))
check("a made-up link finds nothing", anon.get("/api/public/invoice/" + "x" * 24).status_code == 404)
send("POST", "/api/contractor/hicons/profile", "Hana", {"archive_email": ""})
MAIL.clear()
send("POST", "/api/contractor/invoices/" + inv2["id"] + "/send", "Hana", {"to": ["c@example.com"]})
check("no archive email, no copy", len(MAIL) == 1)

# ── PWA opens on Projects ──
r = get("/contractor/hicons?source=pwa", "Hana")
check("app icon opens the Projects screen", r.status_code in (301, 302) and "/contractor/projects" in r.headers.get("Location", ""))

done("contractor")
