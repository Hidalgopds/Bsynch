"""Marketing: public sales landing in English and Spanish.
Run:  python tests/test_marketing.py"""
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
check("demo goes to the business contact", "mailto:" in html)

# ── nothing sensitive in a public page ──
low = html.lower()
check("no Supabase details", "supabase" not in low and "service_role" not in low)
check("no invented prices", "$" not in html)
check("security headers still on", r.headers.get("X-Content-Type-Options") == "nosniff")

done("marketing")
