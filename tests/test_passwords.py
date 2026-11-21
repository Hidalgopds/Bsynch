"""Passwords: one-time links to set or reset them (never a password made up, emailed or shown),
a Manager invited when the owner adds a company, and the owner seeing every company (logged).
Run:  python tests/test_passwords.py"""
import re

from harness import *  # noqa: F401,F403

import app as A

seed()
DB["contractor_companies"] = []
DB["password_links"] = []
A.CONTRACTOR_COMPANIES.reload()
anon = client()


def link_in(mail):
    m = re.search(r'href="[^"]*/set-password/([A-Za-z0-9_-]+)"', mail["html"])
    return m.group(1) if m else None


def user(name):
    return next((u for u in DB["app_users"] if u["name"] == name), None)


# ── forgot password: never changes the password, never shows one, same answer for any email ──
hana = user("Hana")
hana["email"] = "hana@example.com"
old_hash = hana["password"]
MAIL.clear()
r1 = anon.post("/api/forgot-password", json={"email": "hana@example.com"})
r2 = anon.post("/api/forgot-password", json={"email": "nobody@example.com"})
check("same answer whether the email exists or not", r1.status_code == r2.status_code == 200 and r1.json == r2.json)
check("no password in the answer", "temp_pw" not in r1.json and "password" not in str(r1.json).lower().replace("reset the password", ""))
check("password NOT changed by asking", user("Hana")["password"] == old_hash)
check("one email with a link, only to the owner of the account", len(MAIL) == 1 and MAIL[0]["to"] == ["hana@example.com"])
token = link_in(MAIL[0])
check("only a hash of the link is stored", token and DB["password_links"] and all(token not in str(row) for row in DB["password_links"]))
check("reset link page opens", b"Choose your password" in anon.get(f"/set-password/{token}?lang=en").data)
check("short password refused", anon.post("/api/public/set-password", json={"token": token, "password": "short"}).status_code == 400)
ok = anon.post("/api/public/set-password", json={"token": token, "password": "brand-new-pass"})
check("new password saved", ok.json["ok"] and user("Hana")["password"] != old_hash)
cl = client()
check("signs in with the new password", login(cl, "Hana", "brand-new-pass").status_code == 200)
check("link works only once", anon.post("/api/public/set-password", json={"token": token, "password": "another-pass"}).status_code == 410)
check("used link page says it no longer works", b"no longer works" in anon.get(f"/set-password/{token}?lang=en").data)
check("bad token refused", anon.post("/api/public/set-password", json={"token": "x" * 40, "password": "whatever-123"}).status_code == 410)
check("recorded in audit_log", any(a.get("action") == "password.set_by_link" and a.get("target") == "Hana" for a in DB["audit_log"]))

# a newer link cancels the older one; an expired link fails
MAIL.clear()
anon.post("/api/forgot-password", json={"email": "hana@example.com"})
t1 = link_in(MAIL[-1])
anon.post("/api/forgot-password", json={"email": "hana@example.com"})
t2 = link_in(MAIL[-1])
check("older link stops working when a new one is sent", anon.post("/api/public/set-password", json={"token": t1, "password": "pass-pass-1"}).status_code == 410)
row = next(r for r in DB["password_links"] if r["token_hash"] == A._pw_token_hash(t2))
row["expires_at"] = "2000-01-01T00:00:00+00:00"
check("expired link refused", anon.post("/api/public/set-password", json={"token": t2, "password": "pass-pass-1"}).status_code == 410)

# ── owner adds a company with its Manager: the Manager chooses the password ──
MAIL.clear()
r = send("POST", "/api/platform/contractor-companies", "owner@example.com",
         {"slug": "roofs-r-us", "name": "Roofs R Us", "manager_name": "Rita Roof", "manager_email": "rita@example.com"})
rita = user("Rita Roof")
check("company + Manager created, link emailed", r.json["ok"] and r.json["invited"] and rita and rita["approved"] is True
      and rita["contractor_company"] == "roofs-r-us" and A._ct_company_roles("roofs-r-us").get("Rita Roof") == "admin"
      and any("rita@example.com" in m["to"] for m in MAIL))
check("company created with its free trial (not locked when billing starts)",
      next(c for c in DB["contractor_companies"] if c["slug"] == "roofs-r-us")["billing_status"] == "trial")
cl = client()
check("nobody knows the Manager's first password", login(cl, "rita@example.com", "").status_code != 200)
tok = link_in(next(m for m in MAIL if "rita@example.com" in m["to"]))
check("Manager sets her password with the link", anon.post("/api/public/set-password", json={"token": tok, "password": "rita-secret-1"}).json["ok"])
cl = client()
check("Manager signs in and sees only her company", login(cl, "rita@example.com", "rita-secret-1").status_code == 200
      and list((cl.get("/api/contractor/me").json.get("access") or {}).keys()) == ["roofs-r-us"])
check("Manager fields must come together", send("POST", "/api/platform/contractor-companies", "owner@example.com",
      {"slug": "half-co", "name": "Half", "manager_name": "Only Name"}).status_code == 400)
check("existing email can't be invited again", send("POST", "/api/platform/contractor-companies", "owner@example.com",
      {"slug": "dup-co", "name": "Dup", "manager_name": "Other Rita", "manager_email": "rita@example.com"}).status_code == 409)

# ── the owner sees every company's data; each visit is logged for that company ──
DB["contractor_support_log"] = []
A._ct_support_seen.clear()
jobs = get("/api/contractor/jobs", "owner@example.com", company="hicons").json
jobs = jobs.get("jobs", jobs) if isinstance(jobs, dict) else jobs
check("owner sees Hicons work orders without support access", any(j.get("company") == "hicons" for j in jobs))
check("owner's visit written to Hicons' support log", any(s.get("company") == "hicons" and s.get("user_name") == "Owner"
                                                       for s in DB["contractor_support_log"]))
me = get("/api/contractor/me", "owner@example.com").json
check("owner's hub lists every company, none locked", {"hicons", "bsynch", "roofs-r-us"} <= set(me["access"]) and not me["private"]
      and me["role_label"] == "Platform owner")
A._ct_set_config("contractor_platform_admins", ["Newbie"])
other = get("/api/contractor/me", "Newbie").json  # (Hicons/Bsynch gave support access in the test seed; Roofs R Us didn't)
check("a platform admin who isn't the owner still needs support access", other.get("is_super")
      and "roofs-r-us" not in other["access"] and "roofs-r-us" in other["private"])

# ── an ERP admin resets someone's password: a link, never a typed password ──
MAIL.clear()
before = user("Hana")["password"]
r = send("POST", "/api/reset-password", "owner@example.com", {"name": "Hana", "password": "1234"})
check("admin reset sends a link to the person's email", r.json["ok"] and r.json["sent_to"].endswith("@example.com")
      and "link" not in r.json and any("hana@example.com" in m["to"] for m in MAIL))
check("admin can no longer set a password directly", user("Hana")["password"] == before)
crew = send("POST", "/api/reset-password", "owner@example.com", {"name": "Crew One"})
check("crew without email: admin gets a one-time link to hand over", crew.json["ok"] and "/set-password/" in crew.json["link"])
user("Owner")["email"] = ""
check("an admin account without email never gets a hand-over link",
      send("POST", "/api/reset-password", "owner@example.com", {"name": "Owner"}).status_code == 400)
user("Owner")["email"] = "owner@example.com"
check("non-admins can't start a reset", send("POST", "/api/reset-password", "Mia", {"name": "Hana"}).status_code == 403)
check("client-company people are out of reach of ERP admins",
      send("POST", "/api/reset-password", "owner@example.com", {"name": "Rita Roof"}).status_code == 403)

# ── Log out really ends the session (the sign-in page can't put the person back in) ──
lo = client()
login(lo, "Hana", "brand-new-pass")
check("signed in before logging out", lo.get("/api/auth/whoami").status_code == 200)
page = lo.get("/logout")
check("/logout clears the browser's saved name and goes to sign-in", page.status_code == 200 and b"bsynchAuth" in page.data
      and b'location.replace("/login")' in page.data and page.headers.get("Cache-Control") == "no-store")
check("after /logout the session no longer works", lo.get("/api/auth/whoami").status_code == 401)
check("logout recorded", any(a.get("action") == "logout" and a.get("target") == "Hana" for a in DB["audit_log"]))

# ── no public "create account": people join by invitation, companies by /signup ──
n0 = len(DB["app_users"])
reg = client().post("/api/register", json={"name": "Loose Person", "username": "loose", "email": "loose@example.com",
                                            "password": "whatever-123", "consent": True})
check("public account creation is closed", reg.status_code == 410 and len(DB["app_users"]) == n0)
lp = client().get("/login").data
check("login page has no 'Create an account', points to /signup", b"Create an account" not in lp and b'href="/signup"' in lp
      and b"screen-register" not in lp)

done("passwords")
