"""Home Lab (Family Hub): kids checklist, guardians, games wheel, parent approval, Stop and Hermaniland.
Only invented names here: no real children's data.  Run:  python tests/test_homelab.py"""
import time as _t

from harness import *  # noqa: F401,F403

seed()
anon = client()
own = as_user("owner@example.com")
for t in ("homelab_blocks", "homelab_tasks", "homelab_task_completions", "homelab_games", "homelab_game_history",
          "homelab_settings", "homelab_block_approvals", "homelab_approval_notifications"):
    DB.setdefault(t, [])

# ── pages: private ones need a sign-in, public games stay open ──
for p in ("/homelab-hub", "/homelab/kids-checklist", "/homelab/games-hub", "/homelab/games/sugar-quest", "/homelab/tball"):
    r = anon.get(p)
    check(f"page {p} sends anonymous to login", r.status_code == 302 and "/login" in r.headers["Location"])
    check(f"page {p} opens signed in", own.get(p).status_code == 200)
for p in ("/homelab/legal", "/homelab/games/stop", "/games", "/hermaniland"):
    check(f"public page {p} opens", anon.get(p).status_code == 200)

# ── bsynch.com: the family is the owner's alone; other accounts are kept out ──
DB["homelab_kids"].append({"id": "kx", "name": "Niño Ajeno", "active": True, "company_id": None, "order_num": 0})
crew = client()
crew.post("/api/users/verify-pin", json={"name": "Crew One", "pin": "4821"})
for who, cl in (("Hicons user", as_user("Mia")), ("Bsynch leader", as_user("Bob")), ("no company", as_user("Newbie")),
                ("crew PIN", crew)):
    check(f"{who} can't read the family's kids", cl.get("/api/homelab/kids").status_code == 403)
    check(f"{who} can't add a kid", cl.post("/api/homelab/kids", json={"name": "x"}).status_code == 403)
    check(f"{who} can't rename a kid", cl.patch("/api/homelab/kids/kx", json={"name": "x"}).status_code == 403)
    r = cl.get("/homelab/kids-checklist")
    check(f"{who} sent away from the checklist page", r.status_code == 302 and r.headers["Location"].endswith("/home"))
check("no one else changed the kid", DB["homelab_kids"][-1]["name"] == "Niño Ajeno" and len(DB["homelab_kids"]) == 1)
check("anonymous still gets 401", anon.get("/api/homelab/kids").status_code == 401)
check("owner reads the family's kids", [k["name"] for k in own.get("/api/homelab/kids").json] == ["Niño Ajeno"])
DB["homelab_kids"].clear()

# ── first guardian = family account: needs the legal notice accepted ──
r = own.post("/api/homelab/guardians", json={"name": "Tutor Uno", "pin": "1357"})
check("first guardian refused without accepting terms", r.status_code == 400 and not DB["homelab_guardians"])
r = own.post("/api/homelab/guardians", json={"name": "Tutor Uno", "pin": "13a7", "accept_terms": True})
check("guardian PIN must be 4 digits", r.status_code == 400)
r = own.post("/api/homelab/guardians", json={"name": "Tutor Uno", "relationship": "papá", "pin": "1357", "accept_terms": True})
g1 = DB["homelab_guardians"][0] if DB["homelab_guardians"] else {}
check("first guardian created, terms date saved, PIN hashed",
      r.json.get("ok") and g1.get("terms_accepted_at") and str(g1.get("pin")).startswith("h1:"))
check("guardian answer never carries the PIN", "pin" not in r.json["guardian"])
r = own.post("/api/homelab/guardians", json={"name": "Tutor Dos", "pin": "2468"})
check("second guardian needs an existing guardian's PIN", r.status_code == 403)
r = own.post("/api/homelab/guardians", json={"name": "Tutor Dos", "pin": "1357", "current_pin": "1357"})
check("two guardians can't share a PIN", r.status_code == 409)
r = own.post("/api/homelab/guardians", json={"name": "Tutor Dos", "relationship": "mamá", "pin": "2468", "current_pin": "1357"})
check("second guardian added with a valid PIN", r.json.get("ok"))
g2_id = r.json["guardian"]["id"]
lst = own.get("/api/homelab/guardians").json
check("guardian list has names but no PINs", len(lst) == 2 and all("pin" not in x for x in lst))
check("guardian edit needs a PIN", own.patch(f"/api/homelab/guardians/{g2_id}", json={"name": "X"}).status_code == 403)
r = own.patch(f"/api/homelab/guardians/{g2_id}", json={"new_pin": "99", "current_pin": "2468"})
check("guardian new PIN must be 4 digits", r.status_code == 400)
check("guardian renamed with PIN", own.patch(f"/api/homelab/guardians/{g2_id}", json={"name": "Tutora Dos", "current_pin": "2468"}).json.get("ok"))
check("guardian delete needs a PIN", own.delete(f"/api/homelab/guardians/{g2_id}", json={}).status_code == 403)
check("guardian deleted with PIN", own.delete(f"/api/homelab/guardians/{g2_id}", json={"current_pin": "1357"}).json.get("ok"))
g1_id = g1["id"]
r = own.delete(f"/api/homelab/guardians/{g1_id}", json={"current_pin": "1357"})
check("the last guardian can't be deleted", r.status_code == 400 and len(DB["homelab_guardians"]) == 1)
r = own.post("/api/homelab/verify-pin", json={"pin": "1357"})
check("verify-pin gives the guardian, without the PIN", r.json.get("ok") and r.json["guardian"]["name"] == "Tutor Uno"
      and "pin" not in r.json["guardian"])
A._ip_hits.clear()

# ── kids ──
check("kid needs a name", own.post("/api/homelab/kids", json={"name": " "}).status_code == 400)
r = own.post("/api/homelab/kids", json={"name": "Niño Prueba", "avatar_emoji": "🦖", "fecha_nacimiento": "2018-03-01"})
check("kid created", r.json.get("ok"))
kid = r.json["kid"]["id"]
DB["homelab_kids"][-1]["active"] = True  # the real table defaults active to true
kids = own.get("/api/homelab/kids").json
check("kid listed with photo ids", [k["name"] for k in kids] == ["Niño Prueba"] and kids[0]["photo_ids"] == [])
check("kid renamed", own.patch(f"/api/homelab/kids/{kid}", json={"name": "Niño Editado", "id": "hack"}).json.get("ok")
      and DB["homelab_kids"][-1]["name"] == "Niño Editado" and DB["homelab_kids"][-1]["id"] == kid)
check("kid edit with nothing valid refused", own.patch(f"/api/homelab/kids/{kid}", json={"id": "x"}).status_code == 400)

# ── kid photos: max 5, served only for a kid of this family ──
PNG = "data:image/png;base64,iVBORw0KGgo="
check("photo needs data", own.post(f"/api/homelab/kids/{kid}/photos", json={}).status_code == 400)
ids = [own.post(f"/api/homelab/kids/{kid}/photos", json={"photo_data": PNG}).json.get("photo_id") for _ in range(5)]
check("5 photos stored", all(ids) and len(DB["homelab_kid_photos"]) == 5)
check("6th photo refused", own.post(f"/api/homelab/kids/{kid}/photos", json={"photo_data": PNG}).status_code == 400)
r = own.get(f"/api/homelab/kids/{kid}/photos/{ids[0]}/img")
check("photo served as a private image", r.status_code == 200 and r.mimetype == "image/png"
      and r.headers["Cache-Control"].startswith("private"))
check("photo list has no image data", all("photo_data" not in p for p in own.get(f"/api/homelab/kids/{kid}/photos").json))
check("photos need a sign-in", anon.get(f"/api/homelab/kids/{kid}/photos/{ids[0]}/img").status_code == 401)
check("unknown kid's photos: 404", own.get(f"/api/homelab/kids/nokid/photos/{ids[0]}/img").status_code == 404)
check("photo deleted", own.delete(f"/api/homelab/kids/{kid}/photos/{ids[4]}").json.get("ok") and len(DB["homelab_kid_photos"]) == 4)

# ── routine blocks and tasks ──
check("block needs a name", own.post("/api/homelab/blocks", json={}).status_code == 400)
blk = own.post("/api/homelab/blocks", json={"name": "Mañana", "icon": "🌅"}).json["block"]["id"]
DB["homelab_blocks"][-1]["active"] = True
check("task needs block and title", own.post("/api/homelab/tasks", json={"block_id": blk}).status_code == 400)
check("task on an unknown block: 404", own.post("/api/homelab/tasks", json={"block_id": "nope", "title": "x"}).status_code == 404)
t1 = own.post("/api/homelab/tasks", json={"block_id": blk, "title": "Cepillarse", "order_num": 1,
                                          "task_image": PNG}).json["task"]["id"]
t2 = own.post("/api/homelab/tasks", json={"block_id": blk, "title": "Juego mental", "order_num": 2,
                                          "is_mental_game": True}).json["task"]["id"]
for t in DB["homelab_tasks"]:
    t.setdefault("active", True)
check("task image served", own.get(f"/api/homelab/tasks/{t1}/image").status_code == 200)
check("task without image: 404", own.get(f"/api/homelab/tasks/{t2}/image").status_code == 404)
check("task moved to unknown block refused", own.patch(f"/api/homelab/tasks/{t1}", json={"block_id": "nope"}).status_code == 404)
check("unknown task edit: 404", own.patch("/api/homelab/tasks/nope", json={"title": "x"}).status_code == 404)

# ── daily checklist: tick, block complete, PIN to untick, parent approval ──
DB["homelab_blocks"][0]["homelab_tasks"] = DB["homelab_tasks"]  # the fake database doesn't join tables: give the block its tasks
check("checklist needs kid_id", own.get("/api/homelab/checklist").status_code == 400)
check("checklist of unknown kid: 404", own.get("/api/homelab/checklist?kid_id=nope").status_code == 404)
today = A._hl_today()
r = own.post("/api/homelab/checklist/toggle", json={"kid_id": kid, "task_id": t1})
check("task ticked", r.json.get("completed") is True)
cl = own.get(f"/api/homelab/checklist?kid_id={kid}").json
b = cl["blocks"][0] if cl.get("blocks") else {}
check("checklist shows progress 1/2", b.get("done") == 1 and b.get("total") == 2 and not b.get("complete"))
check("checklist strips the task image", all("task_image" not in t for t in b.get("tasks", []))
      and [t["has_image"] for t in b["tasks"]] == [True, False])
r = own.post("/api/homelab/checklist/toggle", json={"kid_id": kid, "task_id": t1})
check("untick without PIN refused (enforced on the server)", r.status_code == 403
      and len(DB["homelab_task_completions"]) == 1)
r = own.post("/api/homelab/checklist/toggle", json={"kid_id": kid, "task_id": t1, "pin": "1357"})
check("untick with a guardian PIN", r.json.get("completed") is False and not DB["homelab_task_completions"])
check("toggle of unknown task: 404", own.post("/api/homelab/checklist/toggle", json={"kid_id": kid, "task_id": "nope"}).status_code == 404)
own.post("/api/homelab/checklist/toggle", json={"kid_id": kid, "task_id": t1})

# games pool: free accounts (client families) are capped; this master family is unlimited
check("game needs a title", own.post("/api/homelab/games", json={}).status_code == 400)
game_ids = [own.post("/api/homelab/games", json={"title": f"Juego {i}", "min_age": 3, "max_age": 12}).json["game"]["id"]
            for i in range(3)]
own.post("/api/homelab/games", json={"title": "Para grandes", "min_age": 15})
for gm in DB["homelab_games"]:
    gm.setdefault("active", True)
pool = own.get(f"/api/homelab/games?kid_id={kid}").json
check("games filtered by the kid's age", sorted(g["title"] for g in pool) == ["Juego 0", "Juego 1", "Juego 2"])
r = own.post("/api/homelab/games/spin", json={"kid_id": kid, "task_id": t2})
check("wheel picks a game and completes the task", r.json.get("ok") and r.json["game"]["id"] in game_ids
      and len(DB["homelab_task_completions"]) == 2 and DB["homelab_game_history"])
check("block complete -> one parent notification", len(DB["homelab_approval_notifications"]) == 1)
b = own.get(f"/api/homelab/checklist?kid_id={kid}").json["blocks"][0]
check("checklist says block complete, not yet approved", b["complete"] and not b["approved"])
r = own.post("/api/homelab/games/pick-manual", json={"kid_id": kid, "task_id": t2, "game_id": "nope"})
check("manual pick outside the pool refused", r.status_code == 400)
check("approval needs a PIN", own.post(f"/api/homelab/blocks/{blk}/approve", json={"kid_id": kid}).status_code == 400)
check("approval with wrong PIN refused", own.post(f"/api/homelab/blocks/{blk}/approve",
                                                  json={"kid_id": kid, "pin": "0000"}).status_code == 403)
A._ip_hits.clear()
r = own.post(f"/api/homelab/blocks/{blk}/approve", json={"kid_id": kid, "pin": "1357"})
check("guardian approves the block", r.json.get("ok") and r.json.get("guardian_name") == "Tutor Uno"
      and len(DB["homelab_block_approvals"]) == 1)
own.post("/api/homelab/checklist/toggle", json={"kid_id": kid, "task_id": t1, "pin": "1357"})
check("unticking a task takes the approval back", not DB["homelab_block_approvals"]
      and not DB["homelab_approval_notifications"])

# ── settings ──
check("settings change needs a PIN", own.patch("/api/homelab/settings", json={"game_repeat_cooldown": 1}).status_code == 403)
check("cooldown must be a number", own.patch("/api/homelab/settings",
                                             json={"game_repeat_cooldown": "x", "current_pin": "1357"}).status_code == 400)
own.patch("/api/homelab/settings", json={"game_repeat_cooldown": 1, "parent_email": "tutor@example.com", "current_pin": "1357"})
own.patch("/api/homelab/settings", json={"game_repeat_cooldown": 2, "current_pin": "1357"})
s = own.get("/api/homelab/settings").json
check("settings saved once per key", s["game_repeat_cooldown"] == 2 and s["parent_email"] == "tutor@example.com"
      and len(DB["homelab_settings"]) == 2)

# ── another family (client subdomain) can't see or touch this family's kids ──
A._co_cache["famdos"] = {"id": "co-fam2", "slug": "famdos", "supabase_url": None, "homelab_plan": "free"}
A._co_cache_ts = _t.time() + 10 ** 6  # keep the fake company list from refreshing
FAM = "https://famdos.bsynch.com"
_fam = A.app.test_client()
with _fam.session_transaction(base_url=FAM) as s:
    s["co_admin"] = "famdos"  # signed in with that family's own company login


class _Fam:  # the other family's browser, always on its own subdomain
    def __getattr__(self, method):
        return lambda path, **kw: getattr(_fam, method)(path, base_url=FAM, **kw)


fam = _Fam()
_mods = A._client_modules
A._client_modules = lambda: {"homelab": True}
check("other family sees no kids", fam.get("/api/homelab/kids").json == [])
check("other family can't open this family's checklist", fam.get(f"/api/homelab/checklist?kid_id={kid}").status_code == 404)
check("other family can't see this family's photos", fam.get(f"/api/homelab/kids/{kid}/photos/{ids[0]}/img").status_code == 404)
fam.patch(f"/api/homelab/kids/{kid}", json={"name": "Hackeado"})
check("other family can't rename this family's kid", DB["homelab_kids"][0]["name"] == "Niño Editado")
check("other family can't tick this family's tasks", fam.post("/api/homelab/checklist/toggle",
                                                              json={"kid_id": kid, "task_id": t1}).status_code == 404)
check("this family's PIN doesn't work in the other family", not fam.post("/api/homelab/verify-pin", json={"pin": "1357"}).json.get("ok"))
A._ip_hits.clear()
r = fam.post("/api/homelab/kids", json={"name": "Niña Dos"})
check("other family's kid saved under its own company", r.json.get("ok") and r.json["kid"]["company_id"] == "co-fam2")
# free plan: no premium games and at most HL_FREE_GAME_LIMIT wheel games
check("free family can't add premium games", fam.post("/api/homelab/games", json={"title": "P", "is_premium": True}).status_code == 403)
for i in range(A.HL_FREE_GAME_LIMIT):
    fam.post("/api/homelab/games", json={"title": f"F{i}"})
for gm in DB["homelab_games"]:
    gm.setdefault("active", True)
check("free family capped at the game limit", fam.post("/api/homelab/games", json={"title": "Extra"}).status_code == 403)
check("free family can't flip a game to premium", fam.patch(f"/api/homelab/games/{game_ids[0]}",
                                                            json={"is_premium": True}).status_code == 403)
A._client_modules = _mods
A._co_cache.pop("famdos", None)

check("kid removed (soft delete, data kept)", own.delete(f"/api/homelab/kids/{kid}").json.get("ok")
      and DB["homelab_kids"][0]["active"] is False and own.get("/api/homelab/kids").json == [])

# ── Stop: public rooms, no personal data ──
r = anon.post("/api/stop/create-room", json={"admin_name": "Anfitrión", "time_limit": 5, "categories": ["Animal", "Fruta"]})
code, host = r.json["room_code"], r.json["player_id"]
room = A.STOP_GAMES[code]
check("Stop time limit kept between 30 and 300", room["time_limit"] == 30)
check("Stop: unknown room 404", anon.post("/api/stop/join-room", json={"room_code": "ZZZZ", "player_name": "B"}).status_code == 404)
guest = anon.post("/api/stop/join-room", json={"room_code": code.lower(), "player_name": "Invitado"}).json["player_id"]
check("Stop: repeated name refused", anon.post("/api/stop/join-room", json={"room_code": code, "player_name": "Invitado"}).status_code == 400)
r = anon.get(f"/api/stop/room/{code}")
check("Stop lobby status works (guests poll it to start)", r.status_code == 200 and len(r.json["players"]) == 2)
check("Stop lobby never reveals the players' secret ids", host not in r.get_data(as_text=True)
      and guest not in r.get_data(as_text=True))
check("Stop: a guest can't start the game", anon.post(f"/api/stop/start/{code}", json={"player_id": guest}).status_code == 403)
check("Stop: no id, no start", anon.post(f"/api/stop/start/{code}").status_code == 403 and room["status"] == "waiting")
r = anon.post(f"/api/stop/start/{code}", json={"player_id": host})
check("Stop start answer has no secret ids", host not in r.get_data(as_text=True) and guest not in r.get_data(as_text=True))
letter = r.json["letter"]
check("Stop starts with a letter", r.status_code == 200 and letter.isalpha() and r.json["categories"] == ["Animal", "Fruta"])
r = anon.get(f"/api/stop/room/{code}").json
check("Stop lobby gives guests the time and categories", r["status"] == "playing" and r["time_limit"] == 30
      and r["categories"] == ["Animal", "Fruta"])
check("Stop: can't join once started", anon.post("/api/stop/join-room", json={"room_code": code, "player_name": "Tarde"}).status_code == 400)
check("Stop: stranger can't submit", anon.post(f"/api/stop/submit/{code}", json={"player_id": "x"}).status_code == 404)
anon.post(f"/api/stop/submit/{code}", json={"player_id": host, "responses": ["Gato", "Pera"], "completion_time": 10})
anon.post(f"/api/stop/submit/{code}", json={"player_id": guest, "responses": ["Gato", ""], "completion_time": 5})
r = anon.get(f"/api/stop/results/{code}").json
check("Stop results: full answers + unique word win", r["all_completed"] and r["winner_name"] == "Anfitrión"
      and [x["name"] for x in r["rankings"]] == ["Anfitrión", "Invitado"])
check("Stop scoring: shared word counts less", A.calculate_smart_score("gato", ["gato", "gato"]) < A.calculate_smart_score("gato", ["gato"]))
r = anon.post("/api/stop/create-room", json={"admin_name": "N" * 200, "categories": ["C" * 99] * 50,
                                             "time_limit": "abc", "victory_message": "V" * 500})
big = A.STOP_GAMES[r.json["room_code"]]
check("Stop trims long names, categories and messages", len(big["admin"]) == 30 and len(big["categories"]) == 12
      and all(len(c) == 40 for c in big["categories"]) and len(big["victory_message"]) == 80 and big["time_limit"] == 120)
check("Stop: empty request doesn't crash", anon.post("/api/stop/create-room").status_code == 200
      and anon.post("/api/stop/join-room").status_code == 404)
page = anon.get("/homelab/games/stop").get_data(as_text=True)
check("Stop page shows names as text, not HTML", "function esc(" in page and "${player.name}" not in page
      and "${winnerName}" not in page and "${pregunta.text}" not in page)
check("Stop scoring: empty or non-word gets 0", A.calculate_smart_score("", []) == 0 and A.calculate_smart_score("x1", ["x1"]) == 0)

# ── Hermaniland: draft game ──
check("Hermaniland data loads", len(anon.get("/api/hermaniland/players").json["players"]) > 100
      and anon.get("/api/hermaniland/coaches").json["coaches"] and anon.get("/api/hermaniland/formations").json["formations"])
r = anon.post("/api/hermaniland/create-room", json={"admin_name": "Jugador", "num_players": 1, "time_per_pick": 5})
hc, admin = r.json["room_code"], r.json["admin_id"]
hroom = A.HERMANILAND_GAMES[hc]
check("Hermaniland solo room gets an AI rival", r.status_code == 201 and len(hroom["participants"]) == 2
      and hroom["time_per_pick"] == 20)
check("Hermaniland: full room refused", anon.post("/api/hermaniland/join-room", json={"room_code": hc}).status_code == 400)
check("Hermaniland: only admin pauses", anon.post(f"/api/hermaniland/toggle-pause/{hc}", json={"player_id": "x"}).status_code == 403)
check("Hermaniland: only admin starts setup", anon.post(f"/api/hermaniland/begin-team-setup/{hc}", json={"player_id": "x"}).status_code == 403)
check("Hermaniland: draft can't start before setup", anon.post(f"/api/hermaniland/start-draft/{hc}").status_code == 400)
anon.post(f"/api/hermaniland/begin-team-setup/{hc}", json={"player_id": admin})
check("Hermaniland: AI picks formation and coach", anon.get(f"/api/hermaniland/team-setup-status/{hc}").json["participants"]
      and not anon.get(f"/api/hermaniland/team-setup-status/{hc}").json["all_ready"])
check("Hermaniland: unknown player can't pick a formation",
      anon.post(f"/api/hermaniland/select-formation/{hc}", json={"player_id": "nope"}).status_code == 404)
r = anon.post(f"/api/hermaniland/select-formation/{hc}", json={"player_id": admin, "formation": "4-3-3",
                                                               "coach_name": A.COACHES[0]["name"]})
check("Hermaniland: everyone ready after the human picks", r.json["all_ready"])
check("Hermaniland: draft starts", anon.post(f"/api/hermaniland/start-draft/{hc}").status_code == 200
      and hroom["status"] == "drafting")
# Draft until both teams have 11: the human always takes the first free player, the AI picks on its own
for _ in range(40):
    if hroom["status"] != "drafting":
        break
    me = hroom["pick_order"][hroom["current_pick_index"]]
    if me == admin:
        if len(hroom["participants"][admin]["players"]) < 11:
            free = next(p["name"] for p in hroom["available_players"] if p["name"] not in hroom["drafted_players"])
            taken = next(iter(hroom["drafted_players"]), None)
            if taken:
                check("Hermaniland: drafted player can't be taken twice", anon.post(
                    f"/api/hermaniland/draft-player/{hc}", json={"player_id": admin, "player_name": taken}).status_code == 400)
            anon.post(f"/api/hermaniland/draft-player/{hc}", json={"player_id": admin, "player_name": free})
        if hroom["status"] != "drafting":
            break
    anon.post(f"/api/hermaniland/next-pick/{hc}")
check("Hermaniland: draft ends in the review round", hroom["status"] == "review")
check("Hermaniland: results wait for the match", anon.get(f"/api/hermaniland/results/{hc}").status_code == 400)
check("Hermaniland: review turn is the human's", anon.post(f"/api/hermaniland/review-turn/{hc}",
                                                           json={"player_id": "x"}).status_code == 400)
anon.post(f"/api/hermaniland/review-turn/{hc}", json={"player_id": admin, "action": "keep"})
r = anon.get(f"/api/hermaniland/results/{hc}")
check("Hermaniland: results with a winner", hroom["status"] == "playing" and r.status_code == 200
      and r.json["winner"] and len(r.json["results"]) == 2)

done("test_homelab")
