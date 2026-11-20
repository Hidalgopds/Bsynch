"""Storefront hub (being built): only platform operators see it for now.
Run:  python tests/test_storefront.py"""
from harness import *  # noqa: F401,F403

seed()

check("owner opens the Storefront hub", get("/storefront-hub", "owner@example.com").status_code == 200)
check("owner's home shows the Storefront tile", get("/api/me/hubs", "owner@example.com").json["preview"] == ["storefront"])
check("a Hicons Manager doesn't see it yet", get("/storefront-hub", "Hana").status_code == 302
      and get("/api/me/hubs", "Hana").json["preview"] == [])
check("anonymous goes to sign in", client().get("/storefront-hub").status_code == 302)
check("storefront names can't be company ids",
      all(send("POST", "/api/platform/contractor-companies", "owner@example.com", {"slug": s, "name": "X"}).status_code == 400
          for s in ("storefront", "store", "shop", "tienda", "catalog")))

done("storefront")
