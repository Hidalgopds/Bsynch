"""Platform Admin (one page for the whole app) and the hubs listed by company.
Run:  python tests/test_platform.py"""
from harness import *  # noqa: F401,F403

import app as A

seed()
DB["contractor_companies"] = [
    {"slug": "hicons", "name": "Hicons", "status": "active", "hubs": ["contractor"], "billing_exempt": True},
    {"slug": "bsynch", "name": "Bsynch", "status": "active", "hubs": ["contractor"], "billing_exempt": True},
    {"slug": "tdg", "name": "TDG Energy Services", "status": "active", "hubs": ["erp"], "billing_exempt": True},
    {"slug": "mbr", "name": "MBR (Test)", "status": "paused", "hubs": ["erp"], "is_demo": True},
    {"slug": "demo-construction", "name": "Demo Construction Co", "status": "active", "hubs": ["contractor"], "is_demo": True},
    {"slug": "demo-marketing", "name": "Demo Marketing Co", "status": "active", "hubs": ["marketing"], "is_demo": True},
    {"slug": "demo-store", "name": "Demo Store", "status": "active", "hubs": ["storefront"], "is_demo": True},
    {"slug": "acme", "name": "Acme", "status": "active", "hubs": ["contractor"]},
    {"slug": "waiting", "name": "Waiting Co", "status": "pending", "hubs": ["contractor"]},
    {"slug": "nope", "name": "Rejected Co", "status": "rejected", "hubs": ["contractor"]}]
A.CONTRACTOR_COMPANIES.reload()
A.ERP_COMPANIES.reload()

# ── access ──
check("platform page: owner yes", get("/platform", "owner@example.com").status_code == 200)
check("platform page: a Manager is sent back", get("/platform", "Hana").status_code == 302)
check("platform API: Manager refused", get("/api/platform/hub-companies", "Hana").status_code == 403)
check("platform API: anonymous refused", client().get("/api/platform/hub-companies").status_code == 401)

rows = {c["slug"]: c for c in get("/api/platform/hub-companies", "owner@example.com").json["companies"]}
check("lists active, paused and waiting companies; never rejected ones", {"hicons", "tdg", "mbr", "waiting"} <= set(rows)
      and "nope" not in rows)
check("platform companies are marked fixed", rows["hicons"]["fixed_hub"] == "contractor" and rows["tdg"]["fixed_hub"] == "erp")

# ── hubs on/off, pause ──
r = send("PATCH", "/api/platform/hub-companies/acme", "owner@example.com", {"hubs": ["contractor", "erp", "homelab"]})
acme = next(c for c in DB["contractor_companies"] if c["slug"] == "acme")
check("turn ERP on for a company (unknown hubs ignored)", r.json["ok"] and acme["hubs"] == ["contractor", "erp"])
check("audited", any(a.get("action") == "company.platform_update" and a.get("target") == "acme" for a in DB["audit_log"]))
send("PATCH", "/api/platform/hub-companies/acme", "owner@example.com", {"hubs": ["erp"]})
A.CONTRACTOR_COMPANIES.reload()
check("Contractor off: the company leaves the Contractor list (data untouched)", "acme" not in A.CONTRACTOR_COMPANIES)
check("can't take Contractor away from Hicons", send("PATCH", "/api/platform/hub-companies/hicons", "owner@example.com",
                                                    {"hubs": ["erp"]}).status_code == 400)
check("can't pause TDG", send("PATCH", "/api/platform/hub-companies/tdg", "owner@example.com", {"status": "paused"}).status_code == 400)
check("pause and re-activate a company", send("PATCH", "/api/platform/hub-companies/acme", "owner@example.com", {"status": "paused"}).json["ok"]
      and send("PATCH", "/api/platform/hub-companies/acme", "owner@example.com", {"status": "active"}).json["ok"])
check("waiting companies use Approve/Reject instead", send("PATCH", "/api/platform/hub-companies/waiting", "owner@example.com",
                                                          {"status": "active"}).status_code == 400)
check("a Manager can't change hubs", send("PATCH", "/api/platform/hub-companies/acme", "Hana", {"hubs": ["contractor"]}).status_code == 403)
check("rejected companies can't be touched", send("PATCH", "/api/platform/hub-companies/nope", "owner@example.com",
                                                  {"status": "active"}).status_code == 404)

# ── add a company with hubs ──
r = send("POST", "/api/platform/contractor-companies", "owner@example.com", {"slug": "shop-co", "name": "Shop Co", "hubs": ["storefront", "marketing"]})
shop = next(c for c in DB["contractor_companies"] if c["slug"] == "shop-co")
check("new company gets the hubs picked", r.json["ok"] and shop["hubs"] == ["marketing", "storefront"])
send("POST", "/api/platform/contractor-companies", "owner@example.com", {"slug": "plain-co", "name": "Plain Co"})
check("no hubs given: Contractor, as before", next(c for c in DB["contractor_companies"] if c["slug"] == "plain-co")["hubs"] == ["contractor"])

# ── hub pages listed by company ──
for hub, demo in (("marketing", "demo-marketing"), ("storefront", "demo-store")):
    check(f"{hub} hub page opens for the owner", get(f"/hub/{hub}", "owner@example.com").status_code == 200)
    lst = [c["slug"] for c in get(f"/api/hub/{hub}", "owner@example.com").json["companies"]]
    check(f"{hub} hub lists its example company only for that hub", demo in lst and "hicons" not in lst)
    check(f"{hub} hub list is for platform admins", get(f"/api/hub/{hub}", "Hana").status_code == 403)
check("Marketing for others: their usual page", get("/hub/marketing", "Hana").headers["Location"].endswith("/marketing-hub"))
check("unknown hub refused", get("/hub/homelab", "owner@example.com").headers["Location"].endswith("/home"))
check("demo sign-in only for Contractor demos", send("POST", "/api/platform/demo-companies/demo-store/login", "owner@example.com", {}).status_code == 409)

# ── tiles point to the right places ──
home = get("/home", "owner@example.com").data
check("home: Marketing and Storefront tiles go to their hubs", b'href="/hub/marketing"' in home and b'href="/hub/storefront"' in home)
check("contractor hub: Platform Admin goes to the single platform page", b'/platform?hub=contractor' in get("/contractor-hub", "owner@example.com").data)
check("settings: Platform Admin card goes to /platform", any(c["href"] == "/platform" for c in get("/api/me/settings", "owner@example.com").json["cards"]))

done("platform")
