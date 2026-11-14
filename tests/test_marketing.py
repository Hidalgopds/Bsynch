"""Marketing: public sales landing in English and Spanish.
Run:  python tests/test_marketing.py"""
import re

from harness import *  # noqa: F401,F403

seed()
anon = client()

# ── public, no login needed ──
r = anon.get("/marketing")
check("landing is public", r.status_code == 200 and r.mimetype == "text/html")
html = r.get_data(as_text=True)
check("defaults to English", '<html lang="en">' in html and "Request a demo" in html)

# ── language: ?lang= wins, then the browser ──
es = anon.get("/marketing?lang=es").get_data(as_text=True)
check("Spanish with ?lang=es", '<html lang="es">' in es and "Pide una demostración" in es)
br = anon.get("/marketing", headers={"Accept-Language": "es-MX,es;q=0.9"}).get_data(as_text=True)
check("Spanish from the browser language", '<html lang="es">' in br)
bad = anon.get("/marketing?lang=xx", headers={"Accept-Language": "fr"}).get_data(as_text=True)
check("unknown language falls back to English", '<html lang="en">' in bad)
check("cache varies by language", "Accept-Language" in anon.get("/marketing").headers.get("Vary", ""))

# ── the switcher and the ways in ──
check("both languages linked", 'href="/marketing?lang=en"' in html and 'href="/marketing?lang=es"' in html)
check("sign-in link", 'href="/login"' in html)
check("terms and privacy linked", 'href="/terms"' in html and 'href="/privacy"' in html)
check("demo buttons go to the form", 'href="#demo"' in html and 'id="leadForm"' in html)
check("form has the hidden trap field", 'name="website"' in html)

# ── nothing sensitive in a public page ──
low = html.lower()
check("no Supabase details", "supabase" not in low and "service_role" not in low)
check("price set by the owner: $149/month, 14-day trial", "$149" in html and "14-day free trial" in html)
check("same price in Spanish", "$149" in es and "14 días gratis" in es and "/ mes por empresa" in es)
check("no other prices", set(re.findall(r"\$\d+", html)) == {"$149"} and set(re.findall(r"\$\d+", es)) == {"$149"})
check("security headers still on", r.headers.get("X-Content-Type-Options") == "nosniff")

# ── leads: the public form ──
import app as A  # noqa: E402
URL = "/api/public/marketing/lead"


def post_lead(body, cl=None):
    return (cl or anon).post(URL, json=body)


A._ip_hits.clear()
MAIL.clear()
r = post_lead({"name": "Pat Builder", "company": "Pat Roofing", "email": "Pat@Example.com", "phone": "",
               "trade": "Roofing", "crew_size": "6-15", "message": "Need timesheets", "lang": "es"})
check("lead saved", r.status_code == 200 and r.json["ok"])
rows = DB.get("marketing_leads", [])
check("one row in marketing_leads", len(rows) == 1)
lead = rows[0]
check("lead fields stored", lead["name"] == "Pat Builder" and lead["email"] == "pat@example.com"
      and lead["crew_size"] == "6-15" and lead["lang"] == "es" and lead["status"] == "new" and lead["source"] == "landing")
check("owner gets an email with reply-to the lead", len(MAIL) == 1 and MAIL[0]["to"] == ["owner@example.com"]
      and "Pat Builder" in MAIL[0]["subject"])
check("lead creation is audited", any(a["action"] == "marketing.lead_created" for a in DB.get("audit_log", [])))

r = post_lead({"name": "<script>x</script>", "phone": "(281) 555-0100", "crew_size": "999", "status": "won"})
check("phone only is enough", r.status_code == 200)
last = DB["marketing_leads"][-1]
check("bad crew size dropped, status forced to new", last["crew_size"] == "" and last["status"] == "new")
check("email body escapes what the visitor typed", "<script>" not in MAIL[-1]["html"])

check("name required", post_lead({"email": "a@example.com"}).status_code == 400)
check("email or phone required", post_lead({"name": "No Contact"}).status_code == 400)
check("bad email refused", post_lead({"name": "X", "email": "not-an-email"}).status_code == 400)
es_err = post_lead({"name": "X", "lang": "es"}).json["error"]
check("errors in the visitor's language", "correo" in es_err)
check("refused leads not saved", len(DB["marketing_leads"]) == 2)

# honeypot: a bot fills 'website' → looks fine, nothing saved
r = post_lead({"name": "Bot", "email": "bot@example.com", "website": "http://spam.example.com"})
check("honeypot answers ok", r.status_code == 200 and r.json["ok"])
check("honeypot saves nothing", len(DB["marketing_leads"]) == 2)

# per-IP limit: 10 per hour
A._ip_hits.clear()
codes = [post_lead({"name": f"Flood {i}", "email": f"f{i}@example.com"}).status_code for i in range(11)]
check("11th lead in an hour is blocked", codes[:10] == [200] * 10 and codes[10] == 429)
A._ip_hits.clear()

# ── leads: only the platform owner sees and edits them ──
OWNER = "owner@example.com"
lst = get("/api/marketing/leads", OWNER)
check("owner sees the leads, newest first", lst.status_code == 200 and lst.json["ok"] and len(lst.json["leads"]) == 12)
check("anonymous can't list leads", anon.get("/api/marketing/leads").status_code in (401, 403))
for who in ("Hana", "Mia", "Bob"):
    check(f"{who} can't list leads", get("/api/marketing/leads", who).status_code in (401, 403))
check("company user can't edit a lead", send("PATCH", f"/api/marketing/leads/{lead['id']}", "Hana", {"status": "won"}).status_code in (401, 403))

u = send("PATCH", f"/api/marketing/leads/{lead['id']}", OWNER, {"status": "contacted", "notes": "Called Monday"})
check("owner updates status and notes", u.status_code == 200 and u.json["lead"]["status"] == "contacted"
      and u.json["lead"]["notes"] == "Called Monday")
check("update is audited", any(a["action"] == "marketing.lead_updated" for a in DB["audit_log"]))
check("bad status refused", send("PATCH", f"/api/marketing/leads/{lead['id']}", OWNER, {"status": "deleted"}).status_code == 400)
check("unknown lead is 404", send("PATCH", "/api/marketing/leads/00000000-0000-0000-0000-000000000000", OWNER, {"status": "won"}).status_code == 404)
flt = get("/api/marketing/leads?status=contacted", OWNER).json["leads"]
check("filter by status", len(flt) == 1 and flt[0]["id"] == lead["id"])
check("no delete route: leads are never deleted",
      send("DELETE", f"/api/marketing/leads/{lead['id']}", OWNER).status_code == 405 and len(DB["marketing_leads"]) == 12)

done("marketing")
