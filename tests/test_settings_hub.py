"""Settings hub: one Settings tile; each person sees only what they can manage.
Run:  python tests/test_settings_hub.py"""
from harness import *  # noqa: F401,F403

import app as A

seed()
DB["contractor_companies"] = [
    {"slug": "acme-paint", "name": "Acme Paint LLC", "status": "active", "hubs": ["contractor"], "billing_status": "trial"}]
A.CONTRACTOR_COMPANIES.reload()


def cards(user):
    return {c["title"]: c for c in get("/api/me/settings", user).json["cards"]}


check("anonymous is sent to sign in", client().get("/settings-hub").status_code == 302
      and client().get("/api/me/settings").status_code == 401)
check("settings page opens for anyone signed in", get("/settings-hub", "Mia").status_code == 200)

mia = cards("Mia")
check("a plain User sees only My account", list(mia) == ["My account"])

hana = cards("Hana")
check("a Hicons Manager sees her company's people and profile", "People of Hicons" in hana and "Company profile" in hana
      and hana["People of Hicons"]["href"] == "/contractor/hicons/admin")
check("Hicons has no Billing card (never billed)", "Billing" not in hana)
check("a Manager sees nothing of the platform", not any(c["group"] == "platform" for c in hana.values()))

own = cards("owner@example.com")
check("the owner sees the platform cards", {"Platform Admin", "Security report", "Dedicated databases (advanced)"} <= set(own))
check("the owner (ERP admin) sees ERP settings", "ERP settings" in own)

# a client company's Manager: own company + Billing, never ERP or platform
DB["app_users"].append({"id": "lola", "name": "Lola Test", "username": "lola@example.com", "email": "lola@example.com", "approved": True,
                        "role": "admin", "contractor_company": "acme-paint", "password": A.hash_password("longpass1")})
A._ct_set_config("contractor_roles_acme-paint", {"Lola Test": "admin"})
lola = client()
login(lola, "lola@example.com", "longpass1")
lc = {c["title"]: c for c in lola.get("/api/me/settings").json["cards"]}
check("client Manager: people, profile and Billing of her company", {"People of Acme Paint LLC", "Company profile", "Billing"} <= set(lc))
check("client Manager: no ERP settings even with an admin role", "ERP settings" not in lc)
check("client Manager: no platform cards", not any(c["group"] == "platform" for c in lc.values()))
check("client's home shows Settings too", lola.get("/api/me/hubs").json["tiles"] == ["contractor", "settings"])
check("client can open the settings hub", lola.get("/settings-hub").status_code == 200)

# the old dedicated-databases page is for platform operators only
check("dedicated-databases page: owner yes", get("/platform-settings", "owner@example.com").status_code == 200)
check("dedicated-databases page: a Manager is sent back", get("/platform-settings", "Hana").status_code == 302)

done("settings_hub")
