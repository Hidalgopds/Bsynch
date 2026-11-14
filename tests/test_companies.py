"""Contractor companies come from a table, not the code: add one, isolation, bad ids, outages.
Run:  python tests/test_companies.py"""
from harness import *  # noqa: F401,F403

import app as A

seed()
DB["contractor_companies"] = []
A.CONTRACTOR_COMPANIES.reload()

check("built-in companies always there", "hicons" in A.CONTRACTOR_COMPANIES and "bsynch" in A.CONTRACTOR_COMPANIES)

# ── only the platform owner adds companies ──
body = {"slug": "acme-paint", "name": "Acme  Paint LLC"}
check("user can't add a company", send("POST", "/api/platform/contractor-companies", "Mia", body).status_code == 403)
check("manager can't add a company", send("POST", "/api/platform/contractor-companies", "Hana", body).status_code == 403)
check("anonymous can't add a company", client().post("/api/platform/contractor-companies", json=body).status_code == 401)
r = send("POST", "/api/platform/contractor-companies", "owner@example.com", body)
check("owner adds a company", r.status_code == 200 and r.json["slug"] == "acme-paint" and r.json["name"] == "Acme Paint LLC")
check("new company works right away", A.CONTRACTOR_COMPANIES.get("acme-paint") == "Acme Paint LLC")
check("recorded in audit_log", any(a.get("action") == "company.contractor_added" for a in DB["audit_log"]))
check("listed for the owner", "acme-paint" in get("/api/platform/contractor-companies", "owner@example.com").json["companies"])
check("list hidden from others", get("/api/platform/contractor-companies", "Hana").status_code == 403)

page = get("/contractor/platform", "owner@example.com")
check("platform page has the add-company form and lists the new company",
      page.status_code == 200 and b'id="newCo"' in page.data and b"acme-paint" in page.data)

# ── bad or taken ids ──
for bad in ("A", "1abc", "has space", "www", "admin", "x" * 40, "ab_c", "dashboard", "workorders", "invoice"):
    check(f"bad id refused: {bad!r}", send("POST", "/api/platform/contractor-companies", "owner@example.com",
                                           {"slug": bad, "name": "X"}).status_code == 400)
check("taken id refused", send("POST", "/api/platform/contractor-companies", "owner@example.com",
                               {"slug": "hicons", "name": "Copy"}).status_code == 409)
check("name required", send("POST", "/api/platform/contractor-companies", "owner@example.com",
                            {"slug": "noname", "name": "  "}).status_code == 400)

# ── a new company is isolated like the others ──
check("Hicons manager can't open the new company", get("/api/contractor/acme-paint/client-folders", "Hana").status_code == 403)
me = get("/api/contractor/me", "Hana").json
check("Hicons hub doesn't show the new company", "acme-paint" not in (me.get("access") or {}))

# ── table unreachable: last good list stays, nobody locked out ──
DB.pop("contractor_companies")
real_get = A.requests.get
A.requests.get = lambda url, *a, **k: (_ for _ in ()).throw(OSError("down")) if "contractor_companies" in url else real_get(url, *a, **k)
A.CONTRACTOR_COMPANIES.reload()
A.requests.get = real_get
check("outage keeps the last good list", "acme-paint" in A.CONTRACTOR_COMPANIES and "hicons" in A.CONTRACTOR_COMPANIES)

done("companies")
