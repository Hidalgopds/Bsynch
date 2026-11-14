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

# ── each company's own web address (hicons.bsynch.com) ──
pr = get("/api/contractor/hicons/profile", "Hana").json
check("web address: settings show the company's own address", pr["web_address"] == "https://hicons.bsynch.com/" and pr["web_ready"])
check("web address: a User can't turn it on", send("POST", "/api/contractor/hicons/profile", "Mia", {"web_address_on": True}).status_code == 403)
check("web address: other company can't touch it", send("POST", "/api/contractor/hicons/profile", "Bob", {"web_address_on": True}).status_code == 403)
MAIL.clear()
send("POST", "/api/contractor/invoices/" + inv2["id"] + "/send", "Hana", {"to": ["c@example.com"]})
check("web address off: invoice link stays on the current host", MAIL and "https://hicons.bsynch.com/i/" not in MAIL[0]["html"])
check("web address: Manager turns it on", send("POST", "/api/contractor/hicons/profile", "Hana", {"web_address_on": True}).json["ok"])
MAIL.clear()
send("POST", "/api/contractor/invoices/" + inv2["id"] + "/send", "Hana", {"to": ["c@example.com"]})
check("web address on: invoice email links to hicons.bsynch.com", MAIL and "https://hicons.bsynch.com/i/" + inv_row["public_token"] in MAIL[0]["html"])
check("web address on: invite link uses it too", get("/api/contractor/hicons/admin/invite", "Hana").json.get("url", "").startswith("https://hicons.bsynch.com/join/hicons/"))
check("web address on: the client's link opens there", A.app.test_client().get("/api/public/invoice/" + inv_row["public_token"],
                                                                                base_url="https://hicons.bsynch.com").status_code == 200)
DB["bsynch_companies"].append({"id": "co-x", "slug": "hicons", "status": "active", "supabase_url": "https://other-db.example.com", "supabase_key": "k"})
A._co_cache_ts = 0
check("web address: refused if that subdomain points to another database",
      send("POST", "/api/contractor/hicons/profile", "Hana", {"web_address_on": False}).json["ok"]
      and send("POST", "/api/contractor/hicons/profile", "Hana", {"web_address_on": True}).status_code == 409)
MAIL.clear()
send("POST", "/api/contractor/invoices/" + inv2["id"] + "/send", "Hana", {"to": ["c@example.com"]})
check("web address: miswired subdomain never used for links", MAIL and "hicons.bsynch.com" not in MAIL[0]["html"])
DB["bsynch_companies"][:] = [c for c in DB["bsynch_companies"] if c.get("id") != "co-x"]
A._co_cache, A._co_cache_ts = {}, 0

# ── sales tax, discount and due dates ──
import datetime as _d
_today = _d.date.today()
check("tax: over 30% refused", send("POST", "/api/contractor/hicons/profile", "Hana", {"tax_rate": 31}).status_code == 400)
check("tax: not a number refused", send("POST", "/api/contractor/hicons/profile", "Hana", {"tax_rate": "abc"}).status_code == 400)
check("tax: company rate and days to pay saved", send("POST", "/api/contractor/hicons/profile", "Hana", {"tax_rate": 8.25, "terms_days": 30}).json["ok"])
jt = send("POST", "/api/contractor/jobs", "Hana", {"title": "Tax job", "client_name": "Tess", "client_email": "tess@example.com"}).json["job"]
send("PATCH", "/api/contractor/jobs/" + jt["id"], "Hana", {"progress_pct": 100})
[x for x in DB["contractor_jobs"] if x["id"] == jt["id"]][0]["service_price"] = 1000
r = send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": jt["id"]})
it = [x for x in DB["contractor_invoices"] if x["id"] == r.json["invoice"]["id"]][0]
check("tax: new invoice adds the company's sales tax", it["subtotal"] == 1000 and it["tax_rate"] == 8.25 and it["tax"] == 82.5 and it["total"] == 1082.5)
check("due: new invoice due in the company's days to pay", it["due_date"] == (_today + _d.timedelta(days=30)).isoformat())
r = send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana", {"discount": 100})
check("discount: total = (subtotal − discount) + tax", r.json["ok"] and r.json["invoice"]["total"] == 974.25 and r.json["invoice"]["tax"] == 74.25)
check("discount: never more than the subtotal", send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana", {"discount": 5000}).json["invoice"]["total"] == 0)
send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana", {"discount": 100})
check("tax: invoice rate over 30% refused", send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana", {"tax_rate": 40}).status_code == 400)
check("discount: negative refused", send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana", {"discount": -5}).status_code == 400)
check("due: before the invoice date refused", send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana",
                                                    {"due_date": (_today - _d.timedelta(days=1)).isoformat()}).status_code == 400)
r = send("PATCH", "/api/contractor/invoices/" + it["id"], "Hana", {"invoice_date": (_today + _d.timedelta(days=2)).isoformat()})
check("due: a new invoice date moves the due date too", r.json["invoice"]["due_date"] == (_today + _d.timedelta(days=32)).isoformat())
check("tax: a User can't edit invoices", send("PATCH", "/api/contractor/invoices/" + it["id"], "Mia", {"tax_rate": 0}).status_code == 403)
it.update({"status": "sent", "sent_at": (_today - _d.timedelta(days=40)).isoformat() + "T12:00:00Z",
           "invoice_date": (_today - _d.timedelta(days=40)).isoformat(), "due_date": (_today - _d.timedelta(days=10)).isoformat(), "public_token": "t" * 24})
lst = {x["id"]: x for x in get("/api/contractor/hicons/invoices", "Hana").json}
check("overdue: past its due date shows days late", lst[it["id"]]["overdue_days"] in (9, 10, 11))
inv_row.update({"status": "sent", "sent_at": (_today - _d.timedelta(days=3)).isoformat() + "T12:00:00Z",
                "invoice_date": (_today - _d.timedelta(days=3)).isoformat(), "due_date": (_today - _d.timedelta(days=3)).isoformat()})
lst = {x["id"]: x for x in get("/api/contractor/hicons/invoices", "Hana").json}
check("overdue: due on receipt waits for the reminder days", lst[inv_row["id"]]["overdue_days"] is None)
inv_row["sent_at"] = (_today - _d.timedelta(days=20)).isoformat() + "T12:00:00Z"
lst = {x["id"]: x for x in get("/api/contractor/hicons/invoices", "Hana").json}
check("overdue: due on receipt, unpaid 15+ days after sending", lst[inv_row["id"]]["overdue_days"] == 20)
it["status"] = "paid"
check("overdue: paid invoices are never late", {x["id"]: x for x in get("/api/contractor/hicons/invoices", "Hana").json}[it["id"]]["overdue_days"] is None)
it["status"] = "sent"
dash = {x["id"]: x for x in get("/api/contractor/hicons/dashboard", "Hana").json["invoices"]}
check("overdue: the dashboard uses the same rule", dash[it["id"]]["overdue_days"] is not None)
pub = anon.get("/api/public/invoice/" + "t" * 24).json["invoice"]
check("tax: the client's link shows discount, tax and due date", pub["tax"] == 74.25 and pub["discount"] == 100 and pub["due_date"])
MAIL.clear()
send("POST", "/api/contractor/invoices/" + it["id"] + "/send", "Hana", {"to": ["tess@example.com"]})
check("tax: the invoice email lists discount and sales tax", MAIL and "Sales tax (8.25%)" in MAIL[0]["html"] and "Discount" in MAIL[0]["html"])

r = send("POST", "/api/contractor/hicons/estimates", "Hana", {"title": "Deck", "client_name": "Tess", "items": [{"description": "Deck boards", "qty": 2, "amount": 500}]})
est = [x for x in DB["contractor_estimates"] if x["id"] == r.json["estimate"]["id"]][0]
check("tax: new estimate starts with the company's rate", est["tax_rate"] == 8.25 and est["total"] == 1082.5)
r = send("PATCH", "/api/contractor/estimates/" + est["id"], "Hana", {"discount": 100})
check("discount: estimate total recomputed with its saved lines", r.json["ok"] and r.json["estimate"]["total"] == 974.25 and len(r.json["estimate"]["items"]) == 1)
est["status"] = "accepted"
r = send("POST", "/api/contractor/estimates/" + est["id"] + "/convert", "Hana", {})
jc = [x for x in DB["contractor_jobs"] if x["id"] == r.json["job"]["id"]][0]
check("estimate → work order keeps the price before tax", jc["service_price"] == 1000)
send("PATCH", "/api/contractor/jobs/" + jc["id"], "Hana", {"progress_pct": 100})
r = send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": jc["id"]})
ic = [x for x in DB["contractor_invoices"] if x["id"] == r.json["invoice"]["id"]][0]
check("estimate → invoice bills the same discount and tax the client accepted", ic["discount"] == 100 and ic["tax_rate"] == 8.25 and ic["total"] == 974.25)
send("POST", "/api/contractor/hicons/profile", "Hana", {"tax_rate": 0, "terms_days": 0})
jz = send("POST", "/api/contractor/jobs", "Hana", {"title": "No tax job", "client_name": "Zed"}).json["job"]
send("PATCH", "/api/contractor/jobs/" + jz["id"], "Hana", {"progress_pct": 100})
[x for x in DB["contractor_jobs"] if x["id"] == jz["id"]][0]["service_price"] = 300
iz_id = send("POST", "/api/contractor/hicons/invoices", "Hana", {"job_id": jz["id"]}).json["invoice"]["id"]
iz = [x for x in DB["contractor_invoices"] if x["id"] == iz_id][0]
check("tax 0%: invoice total unchanged, due on receipt", iz["total"] == 300 and iz["tax"] == 0 and iz["due_date"] == _today.isoformat())

# ── PWA opens on Projects ──
r = get("/contractor/hicons?source=pwa", "Hana")
check("app icon opens the Projects screen", r.status_code in (301, 302) and "/contractor/projects" in r.headers.get("Location", ""))

done("contractor")
