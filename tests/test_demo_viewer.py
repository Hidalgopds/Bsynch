"""Demo accounts (outside reviewers, sales demos) see every hub, but only example companies; and the signed
agreement is only for real paying companies.  Run:  python tests/test_demo_viewer.py"""
from harness import *  # noqa: F401,F403
from harness import _hash

import uuid
import app as A

seed()
DB["contractor_companies"] = [
    {"slug": "hicons", "name": "Hicons", "status": "active", "hubs": ["contractor"], "billing_exempt": True},
    {"slug": "bsynch", "name": "Bsynch", "status": "active", "hubs": ["contractor"], "billing_exempt": True},
    {"slug": "tdg", "name": "TDG Energy Services", "status": "active", "hubs": ["erp"], "billing_exempt": True},
    {"slug": "mbr", "name": "MBR (Test)", "status": "paused", "hubs": ["erp"], "is_demo": True},
    {"slug": "demo-construction", "name": "Demo Construction Co", "status": "active", "hubs": ["contractor"], "is_demo": True,
     "billing_exempt": True},
    {"slug": "demo-marketing", "name": "Demo Marketing Co", "status": "active", "hubs": ["marketing"], "is_demo": True},
    {"slug": "demo-store", "name": "Demo Store", "status": "active", "hubs": ["storefront"], "is_demo": True},
    {"slug": "acme", "name": "Acme", "status": "active", "hubs": ["contractor", "marketing"], "billing_status": "trial"},
    {"slug": "paidco", "name": "Paid Co", "status": "active", "hubs": ["contractor"], "billing_status": "active"}]
A.CONTRACTOR_COMPANIES.reload()
A.ERP_COMPANIES.reload()
for name, co in (("Rev", "demo-construction"), ("Tina", "acme"), ("Pat", "paidco")):
    DB["app_users"].append({"id": str(uuid.uuid4()), "name": name, "username": name.lower(), "email": name.lower() + "@example.com",
                            "role": "worker", "approved": True, "password": _hash(pw(name)), "totp_enabled": False,
                            "contractor_company": co})
    DB["app_config"].append({"key": f"contractor_roles_{co}", "value": {name: "admin"}})

# ── every hub, only example companies ──
h = get("/api/me/hubs", "Rev").json
check("demo account: every hub tile", h.get("demo") and {"erp", "contractor", "marketing", "storefront"} <= set(h["tiles"]))
check("demo account: ERP tile goes to the preview, never to the ERP screens", h["links"]["erp"] == "/hub/erp")
for hub in ("erp", "marketing", "storefront"):
    check(f"demo account: {hub} preview opens", get(f"/hub/{hub}", "Rev").status_code == 200)
    d = get(f"/api/hub/{hub}", "Rev").json
    check(f"demo account: {hub} lists only example companies, no Platform Admin",
          d["ok"] and not d["operator"] and all(c["is_demo"] for c in d["companies"]))
names = [c["slug"] for c in get("/api/hub/erp", "Rev").json["companies"]]
check("demo account never sees TDG", "tdg" not in names and "mbr" in names)
check("demo account: Storefront preview opens", get("/storefront-hub", "Rev").status_code == 200)
r = get("/erp", "Rev")
check("demo account: the real ERP screens stay closed", r.status_code == 302 and "/erp" not in r.headers["Location"].replace("/erp-hub", ""))
check("demo account: ERP data API stays closed", get("/api/erp-hub", "Rev").status_code in (302, 401, 403))
check("demo account: Platform Admin closed", get("/api/platform/hub-companies", "Rev").status_code == 403)

# ── a normal trial client still sees only Contractor ──
t = get("/api/me/hubs", "Tina").json
check("trial client: Contractor only", t["tiles"] == ["contractor", "settings"] and not t.get("demo"))
check("trial client: hub previews closed", get("/hub/marketing", "Tina").status_code == 302 and get("/api/hub/erp", "Tina").status_code == 403)

# ── the signed agreement: only real paying companies ──
check("demo company: no agreement to sign", get("/api/contractor/agreement", "Rev").json["signed"] is True)
check("free trial: no agreement to sign", get("/api/contractor/agreement", "Tina").json["required"] is False)
a = get("/api/contractor/agreement", "Pat").json
check("paying company: agreement required until signed", a["required"] is True and a["signed"] is False)
check("Hicons keeps the agreement", get("/api/contractor/agreement", "Mia").json["required"] is True)

done("demo_viewer")
