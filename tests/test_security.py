"""Security: sign-in, roles, PINs, rate limits, audit log, headers, retention, report and alerts.
Run:  python tests/test_security.py"""
import datetime as _dt

from harness import *  # noqa: F401,F403

seed()
anon = client()
own = as_user("owner@example.com")
mia = as_user("Mia")
crew = client()
assert crew.post("/api/users/verify-pin", json={"name": "Crew One", "pin": "4821"}).json["ok"]

# ── sign-in basics ──
check("right password signs in", login(client(), "Hana").status_code == 200)
check("wrong password refused", login(client(), "Hana", "nope").status_code == 401)
check("ERP pages need sign-in", anon.get("/api/users").status_code == 401)
check("default auth mode is enforce", A.ERP_AUTH_MODE == "enforce" if hasattr(A, "ERP_AUTH_MODE") else True)

# ── app_config is not an open door ──
check("config: unknown keys unreachable", own.get("/api/config/contractor_platform_admins").status_code == 404
      and own.post("/api/config/contractor_roles_hicons", json={"value": {"x": "admin"}}).status_code == 404)
check("config: anonymous blocked", anon.get("/api/config/role_permissions").status_code == 401
      and anon.post("/api/config/role_permissions", json={"value": {}}).status_code == 401)
check("config: crew lead can't write", crew.post("/api/config/role_permissions", json={"value": {}}).status_code == 403)
check("config: admin writes role_permissions", own.post("/api/config/role_permissions", json={"value": {"lead": {}}}).json["ok"])

# ── workers and PINs ──
check("workers: crew lead can't add", crew.post("/api/workers", json={"name": "Zed"}).status_code == 403)
r = own.post("/api/workers", json={"name": "Zed"})
w = [x for x in DB["workers"] if x.get("name") == "Zed"]
check("workers: admin adds, PIN shown once, stored hashed",
      r.json["ok"] and len(str(r.json["worker"]["pin"])) == 4 and w and str(w[0]["pin"]).startswith("h1:"))
zed_pin = r.json["worker"]["pin"]
check("PIN reset: someone else's -> 403", crew.post("/api/contractor/reset-pin", json={"name": "Zed"}).status_code == 403)
check("auto-checkout: anonymous and crew 403", anon.post("/api/auto-checkout").status_code == 403
      and crew.post("/api/auto-checkout").status_code == 403)
A.CRON_SECRET = "cron-s"
check("auto-checkout: cron key passes the guard", anon.post("/api/auto-checkout?key=cron-s").status_code != 403)
A.CRON_SECRET = ""
check("set-pin never creates accounts", anon.post("/api/users/set-pin", json={"name": "Nobody Here", "pin": "3333"}).status_code == 404
      and not any(u["name"] == "Nobody Here" for u in DB["app_users"]))
client().post("/api/users/set-pin", json={"name": "Crew New", "pin": "5555"})
row = [u for u in DB["app_users"] if u["name"] == "Crew New"][0]
check("PIN set from the pad is stored hashed", str(row["pin"]).startswith("h1:") and row["pin"] != "5555")
check("hashed PIN still signs in", client().post("/api/users/verify-pin", json={"name": "Crew New", "pin": "5555"}).json["ok"])
check("legacy plain PIN still signs in", client().post("/api/users/verify-pin", json={"name": "Crew One", "pin": "4821"}).json["ok"])
check("PIN uniqueness works with hashes", client().post("/api/users/set-pin", json={"name": "Crew One", "pin": "5555"}).status_code in (403, 409))
k = client()
check("kiosk: hashed worker PIN clocks in", k.post("/api/checkin/by-pin", json={"pin": zed_pin}).json.get("worker_name") == "Zed")
A._ip_hits.clear()
codes = [k.post("/api/checkin/by-pin", json={"pin": "%04d" % i}).status_code for i in range(9000, 9012)]
check("kiosk: 10 wrong PINs lock the tablet", codes[-1] == 429 and 429 not in codes[:10])
A._ip_hits.clear()
check("tablet: no default admin pass", A.KIOSK_PASS == "")

# ── password lockout ──
lc = client()
res = [login(lc, "Mia", "wrong%d" % i).status_code for i in range(11)]
check("login: 10 wrong passwords lock the account", res[-1] == 429 and res[0] == 401)
check("login: locked even with the right password", login(client(), "Mia").status_code == 429)
A._key_hits.clear()
A._ip_hits.clear()
check("login: works again after the lock clears", login(client(), "Mia").status_code == 200)

# ── audit log ──
acts = {x["action"] for x in DB["audit_log"]}
check("audit: logins, failures, PIN and config changes recorded",
      {"login.fail", "login.locked", "login.ok", "config.set", "worker.add", "pin.set"} <= acts)
check("audit rows carry no PIN or password", not any("5555" in str(x) or "pw-" in str(x) for x in DB["audit_log"]))

# ── headers ──
h = client().get("/login").headers
check("security headers", h.get("X-Frame-Options") == "SAMEORIGIN" and "frame-ancestors" in h.get("Content-Security-Policy", "")
      and h.get("X-Content-Type-Options") == "nosniff" and "geolocation=(self)" in h.get("Permissions-Policy", ""))
hs = client().get("/login", headers={"X-Forwarded-Proto": "https"}).headers
check("HSTS on https", "max-age" in hs.get("Strict-Transport-Security", ""))
r = client().get("/tablet", headers={"X-Forwarded-For": "<script>alert(1)</script>"})
check("tablet page escapes the IP", r.status_code == 403 and b"<script>alert(1)" not in r.data)

# ── passwords ──
m2 = client()
login(m2, "Mia")
check("own password change works", m2.patch("/api/contractor/password", json={"name": "Mia", "current_password": "pw-mia", "new_password": "pw-mia"}).json.get("ok"))
check("can't change someone else's password", m2.patch("/api/contractor/password", json={"name": "Hana", "current_password": "x", "new_password": "y"}).status_code == 403)
forget_sessions()  # the password change signed Mia out elsewhere
own = as_user("owner@example.com")
mia = as_user("Mia")

# ── client companies (bsynch_companies) ──
DB["bsynch_companies"] = [{"id": "c1", "name": "nnc", "slug": "nnc", "status": "active", "supabase_url": "", "supabase_key": "SECRETKEY1234",
                           "admin_username": "boss@nnc", "admin_password": "plainpass"}]
lst = own.get("/api/platform/companies").json
check("platform list hides keys and passwords", lst and "SECRETKEY" not in str(lst) and "plainpass" not in str(lst)
      and lst[0]["has_supabase_key"] and lst[0]["supabase_key"].endswith("1234"))
own.patch("/api/platform/companies/c1", json={"supabase_key": lst[0]["supabase_key"], "name": "NNC"})
check("masked key left as is keeps the real key", DB["bsynch_companies"][0]["supabase_key"] == "SECRETKEY1234" and DB["bsynch_companies"][0]["name"] == "NNC")
check("short admin password rejected", own.patch("/api/platform/companies/c1", json={"admin_password": "1234"}).status_code == 400)
r = own.patch("/api/platform/companies/c1", json={"reset_admin_password": True}).json
check("reset gives a random password once, stored hashed", r["ok"] and len(r["admin_password"]) >= 12
      and DB["bsynch_companies"][0]["admin_password"].startswith("$2"))
check("only platform admins edit companies", mia.patch("/api/platform/companies/c1", json={"name": "x"}).status_code in (401, 403))
A._ip_hits.clear()
DB["bsynch_companies"][0]["admin_password"] = "plainpass"
cl = client()
check("company login: legacy plain password works once and is upgraded",
      cl.post("/api/company-login", json={"username": "boss@nnc", "password": "plainpass"}, base_url="http://nnc.bsynch.com").json.get("ok")
      and DB["bsynch_companies"][0]["admin_password"].startswith("$2"))
check("company login: hashed password works",
      client().post("/api/company-login", json={"username": "boss@nnc", "password": "plainpass"}, base_url="http://nnc.bsynch.com").json.get("ok"))
codes = [client().post("/api/company-login", json={"username": "boss@nnc", "password": "bad%d" % i}, base_url="http://nnc.bsynch.com").status_code
         for i in range(11)]
check("company login: rate limited", codes[-1] == 429)
A._ip_hits.clear()
DB["bsynch_companies"] = []

# ── Home Lab (children's data) ──
DB["homelab_kids"].append({"id": "k1", "name": "Kid", "active": True, "company_id": None, "order_num": 0})
check("homelab API needs a sign-in", anon.get("/api/homelab/kids").status_code == 401 and anon.post("/api/homelab/kids", json={"name": "x"}).status_code == 401)
r = anon.get("/homelab/kids-checklist")
check("homelab page sends to login", r.status_code == 302 and "/login" in r.headers["Location"])
check("homelab works signed in", own.get("/api/homelab/kids").status_code == 200)
check("stop game stays public", anon.post("/api/stop/create-room", json={}).status_code != 401)
g = own.post("/api/homelab/guardians", json={"name": "Mom", "pin": "2468", "accept_terms": True}).json
gr = [x for x in DB["homelab_guardians"] if x.get("name") == "Mom"]
check("Home Lab guardian PIN stored hashed, not returned", g.get("ok") and gr and str(gr[0]["pin"]).startswith("h1:") and "pin" not in g["guardian"])
check("Home Lab guardian PIN verifies", own.post("/api/homelab/verify-pin", json={"pin": "2468"}).json.get("ok"))
A._ip_hits.clear()
for i in range(1000, 1011):
    own.post("/api/homelab/verify-pin", json={"pin": "%04d" % i})
check("Home Lab PIN locks after 10 wrong", not own.post("/api/homelab/verify-pin", json={"pin": "2468"}).json.get("ok"))
A._ip_hits.clear()

# ── public lists ──
lead_names = client().get("/api/public/leads").json
check("sign-up page gets lead names only", isinstance(lead_names, list) and all(set(x) <= {"name", "role"} for x in lead_names)
      and "email" not in str(lead_names))
check("full user list needs a sign-in", anon.get("/api/users").status_code == 401)

# ── retention: only location points older than 90 days are deleted ──
old = (_dt.datetime.utcnow() - _dt.timedelta(days=120)).isoformat()
new = _dt.datetime.utcnow().isoformat()
DB["contractor_locations"].extend([{"id": "L1", "recorded_at": old}, {"id": "L2", "recorded_at": new}])
DB["contractor_invoices"].append({"id": "I1", "created_at": old})
DB["audit_log"].append({"id": "AU1", "at": old, "action": "old"})
A._retention_purge(A._MASTER_URL, A.sb_headers())
check("retention: only old location points deleted",
      [x["id"] for x in DB["contractor_locations"] if x["id"] in ("L1", "L2")] == ["L2"]
      and any(x["id"] == "I1" for x in DB["contractor_invoices"]) and any(x.get("id") == "AU1" for x in DB["audit_log"]))

# ── legal pages ──
r1, r2 = anon.get("/privacy"), anon.get("/terms")
check("privacy and terms are public pages", r1.status_code == 200 and b"Privacy Policy" in r1.data and b"90 days" in r1.data
      and r2.status_code == 200 and b"Terms of Service" in r2.data)
check("login links to them", b'href="/privacy"' in anon.get("/login").data)

# ── manual check-ins (Texas time) ──
r = own.post("/api/checkin/manual", json={"caller_name": "Owner", "worker_name": "Zed", "checked_in_at": "07:30", "date": "2026-01-15"})
row = [c for c in DB["checkins"] if c.get("worker_name") == "Zed" and c.get("manual_entry")]
check("manual check-in saves who entered it (CST in winter = UTC-6)", r.json.get("ok") and row and row[-1]["entered_by"] == "Owner"
      and row[-1]["checked_in_at"] == "2026-01-15T13:30:00")
own.post("/api/checkin/manual", json={"caller_name": "Owner", "worker_name": "Yan", "checked_in_at": "07:30", "date": "2026-07-15"})
check("manual check-in in summer = UTC-5", [c for c in DB["checkins"] if c.get("worker_name") == "Yan"][-1]["checked_in_at"] == "2026-07-15T12:30:00")
check("crew lead can't make manual check-ins", crew.post("/api/checkin/manual", json={"worker_name": "Zed", "checked_in_at": "07:30"}).status_code == 403)

# ── monthly security report and alerts ──
MAIL.clear()
st, en, lab = A._sec_period("previous")
mid_ = (st + _dt.timedelta(days=3)).isoformat() + "T10:00:00"
DB["audit_log"] += [{"at": mid_, "actor": "", "action": "login.fail", "target": "renee", "ip": "203.0.113.9", "detail": {}} for _ in range(4)]
DB["audit_log"].append({"at": mid_, "actor": "", "action": "login.locked", "target": "renee", "ip": "203.0.113.9", "detail": {}})
DB["audit_log"].append({"at": mid_, "actor": "Hana", "action": "company.role_change", "target": "Mia", "ip": "198.51.100.1", "detail": {"company": "hicons", "to": "admin"}})
DB["auth_report"] += [{"day": st.isoformat(), "path": "/api/.env", "method": "GET", "page": ""},
                      {"day": st.isoformat(), "path": "/api/inventory", "method": "GET", "page": ""}]
rep = A._security_report(st, en, lab)
check("report counts attacks, IPs, targets and bot probes", rep["fail_total"] == 5 and rep["top_ips"][0] == ("203.0.113.9", 5)
      and rep["top_accounts"][0][0] == "renee" and rep["probes"] == 2 and rep["probe_hunting"] == 1)
check("report lists sensitive changes", any(c["action"] == "company.role_change" for c in rep["changes"]))
lv = {c["title"]: c["level"] for c in rep["checks"]}
check("health check flags missing backups and lockouts", lv.get("No confirmed database backups") == "red"
      and lv.get("Sign-in lockouts") == "amber" and lv.get("Every ERP screen requires sign-in") == "green")
html = A._security_report_html(rep)
check("report has no secrets", "pw-" not in html and "SECRETKEY" not in html and "h1:" not in html)
MAIL.clear()
A.DEFAULT_COMPANY_ADMIN_USER = "owner@example.com"
ok1, ok2 = A._security_report_send("previous"), A._security_report_send("previous")
check("monthly report sent once per month to the owner", ok1[0] and ok2 == (False, "already sent") and len(MAIL) == 1
      and MAIL[0]["to"] == ["owner@example.com"] and "security report" in MAIL[0]["subject"])
check("report page: anonymous to login, user 403, owner sees it", anon.get("/platform/security-report").status_code == 302
      and mia.get("/platform/security-report").status_code == 403 and b"BSynch security report" in own.get("/platform/security-report").data)
MAIL.clear()
r = own.post("/api/platform/security-report/send", json={"period": "current"}).json
check("send now (owner only)", r["ok"] and len(MAIL) == 1 and mia.post("/api/platform/security-report/send", json={}).status_code == 403)
MAIL.clear()
A._sec_alert_last.clear()
with A.app.test_request_context("/x"):
    A._audit("company.role_change", "Mia", {"company": "hicons", "to": "admin"}, actor="Hana")
    A._audit("company.role_change", "Bo", {"company": "hicons", "to": "admin"}, actor="Hana")
    A._audit("company.role_change", "Cy", {"company": "hicons", "to": "member"}, actor="Hana")
check("critical event emails right away, once per hour", len(MAIL) == 1 and "alert" in MAIL[0]["subject"].lower() and "Mia" in MAIL[0]["html"])
A._ip_hits.clear()
MAIL.clear()
A._sec_alert_last.clear()
k2 = client()
for i in range(8000, 8012):
    k2.post("/api/checkin/by-pin", json={"pin": "%04d" % i})
check("tablet lockout triggers an alert", any("Tablet locked" in m["subject"] for m in MAIL))
A._ip_hits.clear()

# ── pre-launch list ──
r = anon.get("/robots.txt")
check("robots.txt blocks crawlers", r.status_code == 200 and b"Disallow: /" in r.data)
check("every page says noindex", "noindex" in anon.get("/login").headers.get("X-Robots-Tag", ""))
r = anon.get("/no-such-page")
check("friendly 404 page", r.status_code == 404 and b"Page not found" in r.data and b"Go to BSynch" in r.data)
r = anon.get("/api/no-such")
check("API 404 stays JSON", r.status_code in (401, 404) and r.is_json)
DB["contractor_invoices"].append({"id": "INVOG", "company": "hicons", "invoice_number": "H009999", "public_token": "T" * 24,
                                  "company_snapshot": {"display_name": "Hicons, LLC"}, "total": 1234.5, "bill_address": "1 Secret St"})
r = anon.get("/i/" + "T" * 24)
check("invoice link preview: number, company, logo; no amount or address",
      b'og:title" content="Invoice H009999 from Hicons, LLC"' in r.data and b"icon-512.png" in r.data and b"1234" not in r.data and b"Secret St" not in r.data)
A._ip_hits.clear()
n0 = len(DB["app_users"])
r = anon.post("/api/register", json={"name": "Bot", "username": "bot1", "email": "b@example.com", "password": "x12345678", "consent": True, "website": "http://spam"})
check("honeypot: bot gets ok but nothing is saved", r.status_code == 200 and r.json.get("ok") and len(DB["app_users"]) == n0
      and any(a.get("action") == "spam.blocked" for a in DB["audit_log"]))
codes = [anon.post("/api/forgot-password", json={"email": "x@example.com"}).status_code for _ in range(7)]
check("public form rate limit", codes[-1] == 429 and 429 not in codes[:5])
A._ip_hits.clear()

done("security")
