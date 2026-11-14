"""ERP area: inventory, quality issues, purchase orders, material requests, supplier receipts and timesheet.
Run:  python tests/test_erp.py"""
from harness import *  # noqa: F401,F403
from harness import _hash

seed()
anon = client()
# An inventory clerk: may edit stock, is not an admin
DB["app_users"].append({"id": "u-ivy", "name": "Ivy", "username": "ivy", "email": "ivy@example.com", "role": "inventory",
                        "approved": True, "password": _hash("pw-ivy"), "totp_enabled": False, "contractor_company": None})
OWN = "owner@example.com"
crew = client()
assert crew.post("/api/users/verify-pin", json={"name": "Crew One", "pin": "4821"}).json["ok"]


def row(table, rid):
    return next((r for r in DB.get(table, []) if str(r.get("id")) == str(rid)), None)


# ── everything needs a session ──
for path in ("/api/inventory", "/api/issues/all", "/api/po", "/api/facturas", "/api/material-requests",
             "/api/checkins/week", "/api/workers/hours"):
    check("anonymous blocked: " + path, anon.get(path).status_code == 401)
check("crew PIN session can read inventory", crew.get("/api/inventory").status_code == 200)

# ── inventory ──
r = send("POST", "/api/inventory", OWN, {"editor": "Owner", "name": "Tek screw", "category": "Fasteners",
                                          "unit": "box", "qty_on_hand": 20, "safe_qty": 5})
check("admin adds an inventory item and gets a SKU", r.json.get("ok") and r.json["sku"].startswith("MSG-FST-"))
screw = next(i for i in DB["inventory_items"] if i["name"] == "Tek screw")
check("SKU saved on the item", screw.get("sku") == r.json["sku"])
check("plain worker can't add items", send("POST", "/api/inventory", "Mia", {"editor": "Mia", "name": "X"}).status_code == 403)
check("signed-in admin needs no name in the request", send("POST", "/api/inventory", OWN, {"name": "Washer"}).json.get("ok")
      and next(i for i in DB["inventory_items"] if i["name"] == "Washer")["created_by"] == "Owner")
check("inventory role may edit", send("PUT", "/api/inventory/" + screw["id"], "Ivy", {"editor": "Ivy", "notes": "aisle 3"}).json.get("ok"))
check("plain worker can't edit", send("PUT", "/api/inventory/" + screw["id"], "Mia", {"editor": "Mia", "qty_on_hand": 0}).status_code == 403)
check("refused edit changed nothing", row("inventory_items", screw["id"])["qty_on_hand"] == 20)

# the editor is whoever is signed in, never the name the page sends
check("worker pretending to be Dispatcher can't edit",
      send("PUT", "/api/inventory/" + screw["id"], "Mia", {"editor": "Dispatcher", "qty_on_hand": 0}).status_code == 403
      and row("inventory_items", screw["id"])["qty_on_hand"] == 20)
check("crew PIN pretending to be Dispatcher can't delete",
      crew.delete("/api/inventory/" + screw["id"], json={"editor": "Dispatcher"}).status_code == 403 and row("inventory_items", screw["id"]))
check("crew PIN can't add items either", crew.post("/api/inventory", json={"editor": "Owner", "name": "Y"}).status_code == 403)
check("SKU backfill needs a real editor", send("POST", "/api/inventory/sku-backfill", "Mia", {"editor": "Dispatcher"}).status_code == 403)
send("PUT", "/api/inventory/" + screw["id"], "Ivy", {"editor": "Owner", "updated_by": "Owner", "notes": "checked"})
check("change is recorded under the signed-in editor", row("inventory_items", screw["id"])["updated_by"] == "Ivy")
DB["app_users"].append({"id": "u-disp", "name": "Dispatcher", "role": "worker", "approved": True, "pin": "7311", "password": None})
pad = client()
check("editor PIN pad signs in Dispatcher", pad.post("/api/users/verify-pin", json={"name": "Dispatcher", "pin": "7311"}).json["ok"])
check("Dispatcher via the PIN pad may edit", pad.put("/api/inventory/" + screw["id"], json={"notes": "from pad"}).json.get("ok")
      and row("inventory_items", screw["id"])["updated_by"] == "Dispatcher")

send("PUT", "/api/inventory/" + screw["id"], "Ivy", {"editor": "Ivy", "qty_on_hand": 30})
check("more stock marks the restock date", row("inventory_items", screw["id"]).get("last_restocked_at"))
DB["notifications"].clear()
send("PUT", "/api/inventory/" + screw["id"], "Ivy", {"editor": "Ivy", "qty_on_hand": 4})
n = [x for x in DB["notifications"] if "Tek screw" in x.get("title", "")]
check("below safe level warns the supervisor", len(n) == 1 and "LOW" in n[0]["title"] and n[0]["target"] == "supervisor")
low = get("/api/inventory/low-stock", "Mia").json
check("low-stock list shows the item", any(i["id"] == screw["id"] for i in low))

r = send("POST", "/api/inventory", OWN, {"editor": "Owner", "name": "Gutter", "category": "Drainage", "qty_on_hand": 50})
gutter = next(i for i in DB["inventory_items"] if i["name"] == "Gutter")
check("item with plenty of stock is not on the low list", not any(i["id"] == gutter["id"] for i in get("/api/inventory/low-stock", "Mia").json))
check("plain worker can't delete items", send("DELETE", "/api/inventory/" + gutter["id"], "Mia", {"editor": "Mia"}).status_code == 403
      and row("inventory_items", gutter["id"]))

# ── quality issues ──
check("issue needs unit and title", send("POST", "/api/issues", "Mia", {"unit": "A-101"}).status_code == 400)
r = send("POST", "/api/issues", "Mia", {"unit": "A-101", "title": "Cracked panel", "pin_x": 0.2, "pin_y": 0.4})
i1 = r.json["id"]
check("issue created Open, with its first pin", r.json["ok"] and row("unit_issues", i1)["status"] == "Open"
      and row("unit_issues", i1)["pins"] == [{"x": 0.2, "y": 0.4, "drawing_type": "plan"}])
i2 = send("POST", "/api/issues", "Mia", {"unit": "A-101", "title": "Same crack", "pin_x": 0.6, "pin_y": 0.1}).json["id"]
send("POST", "/api/issues", "Mia", {"unit": "B-202", "title": "Loose trim"})
check("unit page shows only that unit", {x["unit"] for x in get("/api/issues/A-101", "Mia").json} == {"A-101"})
check("add pin needs x and y", send("PATCH", f"/api/issues/{i1}/add-pin", "Mia", {"x": 1}).status_code == 400)
check("add pin to a missing issue is 404", send("PATCH", "/api/issues/nope/add-pin", "Mia", {"x": 1, "y": 1}).status_code == 404)
check("add pin appends", len(send("PATCH", f"/api/issues/{i1}/add-pin", "Mia", {"x": 0.3, "y": 0.3}).json["pins"]) == 2)
r = send("POST", f"/api/issues/{i2}/merge-into/{i1}", "Mia")
check("merge joins the pins into one issue", r.json["ok"] and len(row("unit_issues", i1)["pins"]) == 3 and row("unit_issues", i2) is None)
check("status change needs a status", send("PATCH", f"/api/issues/{i1}/status", "Mia", {}).status_code == 400)
send("PATCH", f"/api/issues/{i1}/status", "Mia", {"status": "Resolved", "resolution": "Panel replaced"})
check("issue resolved with its note", row("unit_issues", i1)["status"] == "Resolved" and row("unit_issues", i1)["resolution"] == "Panel replaced")
check("filter by status", [x["title"] for x in get("/api/issues/all?status=Resolved", "Mia").json] == ["Cracked panel"])
check("edit with nothing to change is refused", send("PATCH", f"/api/issues/{i1}/edit", "Mia", {"bogus": 1}).status_code == 400)

# ── purchase orders: receive into stock, then send to a job ──
check("PO needs a number", send("POST", "/api/po", "Ivy", {"supplier": "ACME"}).status_code == 400)
r = send("POST", "/api/po", "Ivy", {"po_number": " po-77 ", "supplier": "ACME", "created_by": "Ivy",
                                    "items": [{"item_id": gutter["id"], "item_name": "Gutter", "qty_expected": 10}]})
po = r.json["po"]
check("PO created pending, number cleaned up", r.json["ok"] and po["po_number"] == "PO-77" and po["status"] == "pending")
check("receive with no items refused", send("POST", f"/api/po/{po['id']}/receive", "Ivy", {"items": []}).status_code == 400)
check("receive a missing PO is 404", send("POST", "/api/po/nope/receive", "Ivy", {"items": [{"item_id": "x", "qty_received": 1}]}).status_code == 404)
r = send("POST", f"/api/po/{po['id']}/receive", "Ivy", {"received_by": "Ivy", "items": [{"item_id": gutter["id"], "qty_received": 4}]})
check("short delivery leaves the PO partial", r.json["status"] == "partial" and row("purchase_orders", po["id"])["status"] == "partial")
check("received goods go into stock", row("inventory_items", gutter["id"])["qty_on_hand"] == 54)
gr = [d for d in DB.get("material_documents", []) if d["mvt_type"] == "GR"]
check("goods receipt written with the PO number", len(gr) == 1 and gr[0]["ref_id"] == "PO-77" and gr[0]["qty"] == 4)
r = send("POST", f"/api/po/{po['id']}/receive", "Ivy", {"received_by": "Ivy", "items": [{"item_id": gutter["id"], "qty_received": 10}]})
check("full delivery closes the PO", r.json["status"] == "received")
check("only received POs listed when filtered", [p["po_number"] for p in get("/api/po?status=received", "Mia").json["pos"]] == ["PO-77"])
check("allocate needs a job", send("POST", f"/api/po/{po['id']}/allocate", "Ivy", {"items": [{"item_id": gutter["id"], "qty_allocated": 1}]}).status_code == 400)
before = row("inventory_items", gutter["id"])["qty_on_hand"]
r = send("POST", f"/api/po/{po['id']}/allocate", "Ivy", {"job_name": "Tower B", "items": [{"item_id": gutter["id"], "qty_allocated": 7}]})
check("allocation takes it out of stock and is kept on the PO",
      r.json["ok"] and row("inventory_items", gutter["id"])["qty_on_hand"] == before - 7 and len(row("purchase_orders", po["id"])["allocations"]) == 1)
send("POST", f"/api/po/{po['id']}/allocate", "Ivy", {"job_name": "Tower C", "items": [{"item_id": gutter["id"], "qty_allocated": 999}]})
check("stock never goes below zero", row("inventory_items", gutter["id"])["qty_on_hand"] == 0)

# ── material requests: request, approve, deliver ──
check("request needs who, what and how many", send("POST", "/api/material-requests", "Mia", {"item_name": "Tek screw"}).status_code == 400)
send("PUT", "/api/inventory/" + screw["id"], "Ivy", {"editor": "Ivy", "qty_on_hand": 40})
send("POST", "/api/material-requests", "Mia", {"requester_name": "Mia", "item_name": "Tek screw", "item_id": screw["id"],
                                               "qty_needed": 6, "job_name": "Tower B"})
mr = next(m for m in DB["material_requests"] if m["item_name"] == "Tek screw")
check("request starts Pending", mr["status"] == "Pending")
check("plain worker can't approve", send("POST", f"/api/material-requests/{mr['id']}/approve", "Mia", {"approved_by": "Mia"}).status_code == 403)
check("worker pretending to be an editor can't approve",
      send("POST", f"/api/material-requests/{mr['id']}/approve", "Mia", {"approved_by": "Dispatcher"}).status_code == 403)
check("admin approves, recorded under the signed-in name",
      send("POST", f"/api/material-requests/{mr['id']}/approve", OWN, {"approved_by": "Fabio"}).json["ok"]
      and row("material_requests", mr["id"])["status"] == "Approved" and row("material_requests", mr["id"])["approved_by"] == "Owner")
check("delivery needs who delivered", send("POST", f"/api/material-requests/{mr['id']}/deliver", "Ivy", {}).status_code == 400)
send("POST", f"/api/material-requests/{mr['id']}/deliver", "Ivy", {"delivered_by": "Ivy", "pickup_by": "Mia"})
check("delivery takes it out of stock", row("inventory_items", screw["id"])["qty_on_hand"] == 34
      and row("material_requests", mr["id"])["status"] == "Delivered")
gi = [d for d in DB["material_documents"] if d["mvt_type"] == "GI"]
check("goods issue written for the job", len(gi) == 1 and gi[0]["job_name"] == "Tower B" and gi[0]["qty"] == 6)
check("plain worker can't delete a request", send("DELETE", f"/api/material-requests/{mr['id']}", "Mia", {}).status_code == 403
      and row("material_requests", mr["id"]))
r = send("DELETE", f"/api/material-requests/{mr['id']}", OWN, {})
check("admin delete of a delivered request puts the stock back",
      r.json.get("ok") and r.json["qty_restored"] == 6 and row("inventory_items", screw["id"])["qty_on_hand"] == 40)

# ── supplier receipts (facturas) ──
r = send("POST", "/api/facturas", "Mia", {"numero": " F-9 ", "proveedor": "ACME", "monto": "120.50"})
check("receipt saved, cleaned, default uploader", r.json["ok"] and r.json["factura"]["numero"] == "F-9" and r.json["factura"]["uploader"] == "Unknown")
check("receipts listed", [f["numero"] for f in get("/api/facturas", "Mia").json["facturas"]] == ["F-9"])

# ── timesheet hours ──
DB["checkins"] = [
    {"id": "c1", "worker_name": "Zed", "position": "A-101", "date": "2026-11-02",
     "checked_in_at": "2026-11-02T07:00:00", "checked_out_at": "2026-11-02T15:30:00"},
    {"id": "c2", "worker_name": "Zed", "position": "A-101", "date": "2026-11-03",
     "checked_in_at": "2026-11-03T07:00:00", "checked_out_at": None},
    {"id": "c3", "worker_name": "Amy", "position": "B-202", "date": "2026-11-03",
     "checked_in_at": "2026-11-03T07:00:00", "checked_out_at": "2026-11-05T07:00:00"},
    {"id": "c4", "worker_name": "Amy", "position": "B-202", "date": "2026-10-20",
     "checked_in_at": "2026-10-20T07:00:00", "checked_out_at": "2026-10-20T08:00:00"},
]
wk = {(x["worker_name"], x["date"]): x["hours"] for x in get("/api/checkins/week?start=2026-11-01&end=2026-11-07", OWN).json}
check("timesheet: in and out gives the hours", wk.get(("Zed", "2026-11-02")) == 8.5)
check("timesheet: still clocked in has no hours yet", ("Zed", "2026-11-03") in wk and wk[("Zed", "2026-11-03")] is None)
check("timesheet: impossible shift (over 24h) is not counted", wk.get(("Amy", "2026-11-03"), 0) is None)
check("timesheet: dates outside the week left out", ("Amy", "2026-10-20") not in wk)
check("crew PIN session can open the timesheet", crew.get("/api/checkins/week").status_code == 200)

done("erp")
