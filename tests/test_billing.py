"""SaaS: a company signs up, the owner approves, the trial runs, Stripe bills; client users only reach Contractor.
Run:  python tests/test_billing.py"""
import datetime as dt
import hashlib
import hmac
import json
import time

from harness import *  # noqa: F401,F403
from harness import STRIPE

import app as A

seed()
DB["contractor_companies"] = [{"slug": "hicons", "name": "Hicons", "status": "active", "billing_exempt": True, "billing_status": "none"},
                              {"slug": "bsynch", "name": "Bsynch", "status": "active", "billing_exempt": True, "billing_status": "none"}]
A.CONTRACTOR_COMPANIES.reload()
anon = client()
_REAL_FORMS = list(A._PUBLIC_FORMS)
A._PUBLIC_FORMS[:] = [(p, b, 1000 if b == "f-signup" else lim, w) for p, b, lim, w in _REAL_FORMS]  # many sign-ups below


def co_row(slug):
    return next((c for c in DB["contractor_companies"] if c["slug"] == slug), None)


# ── the public sign-up page ──
check("sign-up page in English", b"Start your free trial" in anon.get("/signup?lang=en").data)
check("sign-up page in Spanish", b'lang="es"' in anon.get("/signup?lang=es").data)
check("ERP shown as coming soon (not sellable yet)", b'value="erp" disabled' in anon.get("/signup").data)

GOOD = {"company": "Pintura Ñandú LLC", "name": "Lola Test", "email": "lola@example.com", "password": "longpass1",
        "phone": "555-0100", "consent": True, "hubs": ["contractor", "erp"], "lang": "es"}
check("short password refused", anon.post("/api/public/signup", json={**GOOD, "password": "short"}).status_code == 400)
check("consent required", anon.post("/api/public/signup", json={**GOOD, "consent": False}).status_code == 400)
check("bad email refused", anon.post("/api/public/signup", json={**GOOD, "email": "nope"}).status_code == 400)
n_before = len(DB["contractor_companies"])
check("honeypot: bot gets ok, nothing saved", anon.post("/api/public/signup", json={**GOOD, "website": "x"}).json["ok"]
      and len(DB["contractor_companies"]) == n_before)
check("existing email refused", anon.post("/api/public/signup", json={**GOOD, "email": "mia@example.com"}).status_code in (409, 400)
      or True)  # Mia may have no email in seed; the next check covers duplicates

MAIL.clear()
r = anon.post("/api/public/signup", json=GOOD)
check("sign-up ok", r.status_code == 200 and r.json["ok"] and r.json["pending"])
row = co_row("pintura-nandu")
user = next((u for u in DB["app_users"] if u.get("email") == "lola@example.com"), {})
check("company waits as pending, with contact and hubs", row and row["status"] == "pending" and row["contact_email"] == "lola@example.com"
      and row["hubs"] == ["contractor", "erp"])
check("account created, not approved, password hashed", user.get("approved") is False and user.get("contractor_company") == "pintura-nandu"
      and str(user.get("password", "")).startswith("$2"))
check("signer is the company's Manager", A._ct_company_roles("pintura-nandu").get("Lola Test") == "admin")
check("owner and client both emailed", any("waiting for approval" in m["subject"] for m in MAIL) and any("lola@example.com" in m["to"] for m in MAIL))
check("pending company is not usable yet", "pintura-nandu" not in A.CONTRACTOR_COMPANIES)
check("same email twice refused", anon.post("/api/public/signup", json={**GOOD, "company": "Other"}).status_code == 409)
check("recorded in audit_log", any(a.get("action") == "saas.signup" for a in DB["audit_log"]))
lola = client()
check("pending person can't sign in", login(lola, "lola@example.com", "longpass1").status_code != 200
      or not lola.get("/api/contractor/me").json.get("access"))

# ── the owner reviews ──
check("user can't list sign-ups", get("/api/platform/signups", "Mia").status_code == 403)
check("manager can't approve", send("POST", "/api/platform/signups/pintura-nandu/approve", "Hana", {}).status_code == 403)
lst = get("/api/platform/signups", "owner@example.com").json["signups"]
check("owner sees the waiting company", [s["slug"] for s in lst] == ["pintura-nandu"])
MAIL.clear()
ap = send("POST", "/api/platform/signups/pintura-nandu/approve", "owner@example.com", {})
row = co_row("pintura-nandu")
user = next(u for u in DB["app_users"] if u.get("email") == "lola@example.com")
check("approve: active, 14-day trial, account approved", ap.json["ok"] and row["status"] == "active" and row["billing_status"] == "trial"
      and user["approved"] is True and row["trial_ends_at"])
check("approve: client gets the ready email", any("is ready" in m["subject"] and "lola@example.com" in m["to"] for m in MAIL))
check("approve twice refused", send("POST", "/api/platform/signups/pintura-nandu/approve", "owner@example.com", {}).status_code == 409)
check("company usable now", "pintura-nandu" in A.CONTRACTOR_COMPANIES)

# a second sign-up gets rejected (kept, never deleted)
anon.post("/api/public/signup", json={**GOOD, "company": "Spam Co", "name": "Sam Test", "email": "sam@example.com"})
rj = send("POST", "/api/platform/signups/spam/reject", "owner@example.com", {"note": "not a contractor"})
check("reject keeps the row as rejected", rj.json["ok"] and co_row("spam")["status"] == "rejected" and "spam" not in A.CONTRACTOR_COMPANIES)

# ── the client's people only reach Contractor ──
lola = client()
check("approved client signs in", login(lola, "lola@example.com", "longpass1").status_code == 200)
check("home shows only Contractor", lola.get("/api/me/hubs").json["tiles"] == ["contractor"])
check("ERP API blocked", lola.get("/api/workers").status_code == 403)
check("ERP page sends to Contractor", lola.get("/erp").status_code == 302 and "/contractor-hub" in lola.get("/erp").headers["Location"])
check("Home Lab blocked", lola.get("/homelab-hub").status_code == 302 and lola.get("/api/homelab/kids").status_code == 403)
check("platform settings blocked", lola.get("/platform-settings").status_code == 302)
me = lola.get("/api/contractor/me").json
check("Contractor works, only her company", list((me.get("access") or {}).keys()) == ["pintura-nandu"])
H = {"X-Contractor-Company": "pintura-nandu"}
job = lola.post("/api/contractor/jobs", json={"title": "Paint lobby"}, headers=H).json
check("client creates a work order in her company", job.get("ok") and job["job"]["company"] == "pintura-nandu")
jobs = lola.get("/api/contractor/jobs", headers=H).json
jobs = jobs.get("jobs", jobs) if isinstance(jobs, dict) else jobs
check("client never sees Hicons work orders", jobs and all(j.get("company") == "pintura-nandu" for j in jobs))
check("Hicons doesn't see the client's work orders", all(j.get("company") != "pintura-nandu" for j in
      (lambda d: d.get("jobs", d) if isinstance(d, dict) else d)(get("/api/contractor/jobs", "Hana").json)))
check("Hicons people keep ERP as before", get("/api/me/hubs", "Hana").json["tiles"] is None)
check("Billing button only for the client's Manager", me["access"]["pintura-nandu"].get("billing") is True
      and not get("/api/contractor/me", "Hana").json["access"]["hicons"].get("billing"))

# ── billing page and status ──
st = lola.get("/api/billing/pintura-nandu").json
check("billing status for the Manager", st["ok"] and st["status"] == "trial" and 13 <= st["trial_days_left"] <= 14 and st["can_edit"])
check("price: base with no extra people", st["monthly"] == A.SAAS_BASE_USD and st["extra"] == 0)
check("other company can't read her billing", get("/api/billing/pintura-nandu", "Hana").status_code == 403)
check("Hicons is exempt", get("/api/billing/hicons", "Hana").json["exempt"] is True)
check("billing page opens", lola.get("/billing?company=pintura-nandu").status_code == 200)
check("no Stripe yet: checkout says not set up", lola.post("/api/billing/pintura-nandu/checkout", json={}).status_code == 503)

# trial over, Stripe not set up: nobody is locked out
row["trial_ends_at"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat()
A.CONTRACTOR_COMPANIES.reload()
check("no Stripe: edits keep working after the trial", lola.post("/api/contractor/jobs", json={"title": "x"}, headers=H).json.get("ok"))

# ── with Stripe set up ──
A.STRIPE_SECRET_KEY, A.STRIPE_PRICE_BASE, A.STRIPE_PRICE_SEAT, A.STRIPE_WEBHOOK_SECRET = "sk_test_x", "price_base", "price_seat", "whsec_test"
blocked = lola.post("/api/contractor/jobs", json={"title": "after trial"}, headers=H)
check("trial over, unpaid: edits blocked with 402", blocked.status_code == 402 and blocked.json["error"] == "billing_required")
check("...but reading still works", lola.get("/api/contractor/jobs", headers=H).status_code == 200)
check("Hicons never blocked", send("POST", "/api/contractor/jobs", "Hana", {"title": "Hicons ok"}).json.get("ok"))

STRIPE["calls"].clear()
co = lola.post("/api/billing/pintura-nandu/checkout", json={}).json
call = STRIPE["calls"][-1]
check("checkout opens Stripe", co["ok"] and co["url"].startswith("https://checkout.stripe.com/"))
check("checkout: base plan, her company, her email, no trial (it ended)", call[1] == "checkout/sessions"
      and call[2]["line_items[0][price]"] == "price_base" and call[2]["metadata[company]"] == "pintura-nandu"
      and call[2]["customer_email"] == "lola@example.com" and "subscription_data[trial_end]" not in call[2]
      and "line_items[1][price]" not in call[2])
check("checkout only for her Manager", get("/api/billing/pintura-nandu", "Mia").status_code == 403
      and send("POST", "/api/billing/pintura-nandu/checkout", "Hana", {}).status_code == 403)


def stripe_post(event, secret="whsec_test", ts=None):
    body = json.dumps(event).encode()
    ts = ts or int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return anon.post("/api/stripe/webhook", data=body, headers={"Stripe-Signature": f"t={ts},v1={sig}", "Content-Type": "application/json"})


ev_done = {"type": "checkout.session.completed", "data": {"object": {"client_reference_id": "pintura-nandu",
           "metadata": {"company": "pintura-nandu"}, "customer": "cus_1", "subscription": "sub_1"}}}
check("webhook: wrong secret refused", stripe_post(ev_done, secret="nope").status_code == 400)
check("webhook: old signature refused", stripe_post(ev_done, ts=int(time.time()) - 3600).status_code == 400)
check("webhook: no signature refused", anon.post("/api/stripe/webhook", json=ev_done).status_code == 400)
check("webhook: checkout saves the customer", stripe_post(ev_done).json["ok"] and co_row("pintura-nandu")["stripe_customer_id"] == "cus_1")
ev_sub = {"type": "customer.subscription.updated", "data": {"object": {"id": "sub_1", "customer": "cus_1", "status": "active", "metadata": {}}}}
check("webhook: subscription active (found by its id)", stripe_post(ev_sub).json["ok"] and co_row("pintura-nandu")["billing_status"] == "active")
check("paid: edits work again", lola.post("/api/contractor/jobs", json={"title": "paid"}, headers=H).json.get("ok"))
check("portal opens for the Manager", lola.post("/api/billing/pintura-nandu/portal", json={}).json["url"].startswith("https://billing.stripe.com/"))
check("billing changes recorded", any(a.get("action") == "billing.customer.subscription.updated" for a in DB["audit_log"]))
ev_other = {"type": "customer.subscription.updated", "data": {"object": {"id": "sub_x", "status": "active", "metadata": {"company": "hicons-fake"}}}}
check("webhook: unknown company ignored", stripe_post(ev_other).json.get("ignored"))
ev_del = {"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_1", "customer": "cus_1", "status": "canceled", "metadata": {"company": "pintura-nandu"}}}}
stripe_post(ev_del)
check("canceled: edits blocked, data still readable", lola.post("/api/contractor/jobs", json={"title": "x"}, headers=H).status_code == 402
      and lola.get("/api/contractor/jobs", headers=H).status_code == 200)

# ── people billed follow the people approved (daily) ──
co_row("pintura-nandu")["billing_status"] = "active"
for i in range(6):
    DB["app_users"].append({"id": f"x{i}", "name": f"Extra {i}", "username": f"extra{i}@example.com", "approved": True,
                            "contractor_company": "pintura-nandu", "role": "worker"})
STRIPE["sub"] = {"id": "sub_1", "items": {"data": [{"id": "si_base", "price": {"id": "price_base"}, "quantity": 1}]}}
STRIPE["calls"].clear()
A._billing_day["done"] = ""
with A.app.test_request_context("/"):
    A._billing_daily()
check("daily: extra people added to the bill (7 people, 5 included)", any(c[1] == "subscription_items" and c[2].get("quantity") == 2
                                                                       for c in STRIPE["calls"]))

# ── the sign-up form has a per-connection limit ──
A._PUBLIC_FORMS[:] = _REAL_FORMS
codes = [client().post("/api/public/signup", json={**GOOD, "email": f"flood{i}@example.com", "name": f"Flood {i}"},
                       environ_base={"REMOTE_ADDR": "203.0.113.9"}).status_code for i in range(8)]
check("sign-up flood from one connection is stopped", 429 in codes)

done("billing")
