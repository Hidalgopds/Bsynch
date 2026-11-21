"""ERP Home: the ERP tile lists the ERP companies (owner); others go straight to their own ERP.
Run:  python tests/test_erp_hub.py"""
from harness import *  # noqa: F401,F403

import app as A

seed()
DB["contractor_companies"] = [
    {"slug": "tdg", "name": "TDG Energy Services", "status": "active", "hubs": ["erp"], "billing_exempt": True},
    {"slug": "mbr", "name": "MBR (Test)", "status": "paused", "hubs": ["erp"], "is_demo": True, "billing_exempt": True},
    {"slug": "demo-erp", "name": "Demo Field Services", "status": "paused", "hubs": [], "is_demo": True},
    {"slug": "hicons", "name": "Hicons", "status": "active", "hubs": ["contractor"]}]
A.CONTRACTOR_COMPANIES.reload()
A.ERP_COMPANIES.reload()

check("ERP tile goes to the ERP Home", b'href="/erp-hub"' in get("/home", "owner@example.com").data)
check("owner sees the ERP Home", get("/erp-hub", "owner@example.com").status_code == 200)
lst = get("/api/erp-hub", "owner@example.com").json["companies"]
names = {c["slug"]: c for c in lst}
check("ERP Home lists TDG and MBR (Test) only", set(names) == {"tdg", "mbr"})
check("TDG opens; MBR waits until the ERP separates companies", names["tdg"]["ready"] and not names["mbr"]["ready"])
own = as_user("owner@example.com")
r = own.get("/erp-hub/tdg")
check("opening TDG goes to the ERP screens", r.status_code == 302 and r.headers["Location"].endswith("/erp"))
check("MBR can't be opened yet (it would show TDG's data)", own.get("/erp-hub/mbr").headers["Location"].endswith("/erp-hub"))
check("unknown company refused", own.get("/erp-hub/hicons").headers["Location"].endswith("/erp-hub"))
with A.app.test_request_context("/"):
    check("default ERP company is TDG", A.ERP_DEFAULT_COMPANY == "tdg")

# when the ERP separates companies, MBR opens
A.ERP_SEPARATED = True
DB["contractor_companies"][1]["status"] = "active"
A.ERP_COMPANIES.reload()
check("after ERP step 2, MBR (Test) opens", own.get("/erp-hub/mbr").headers["Location"].endswith("/erp"))
A.ERP_SEPARATED = False

# everyone else: straight to their own ERP; the list is owner-only
r = get("/erp-hub", "Hana")
check("non-owners go straight to the ERP", r.status_code == 302 and r.headers["Location"].endswith("/erp"))
check("ERP company list is owner-only", get("/api/erp-hub", "Hana").status_code == 403)
check("anonymous goes to sign in", client().get("/erp-hub").status_code == 302 and "login" in client().get("/erp-hub").headers["Location"])

done("erp_hub")
