"""Fill the STAGING database with fake data for load tests. Never touches production.

    STAGING_SUPABASE_URL=https://<staging-ref>.supabase.co \
    STAGING_SERVICE_KEY=<staging service_role key> \
    python3 loadtest/seed_staging.py --jobs 300 --users 5

It prints the test accounts and their passwords (random each run); keep them out of the repository.
Everything it creates is fake: names like "LoadTest Worker 3", clients like "Client 042".
"""
import argparse, base64, io, json, os, random, re, secrets, sys, uuid, datetime as dt

import bcrypt
import requests

PRODUCTION_REFS = {"wanfpiogchwttsippekm", "fhkfpqgfzegqcyajvjlo"}  # Hidalgo ops, NNC


def die(msg):
    print("STOP:", msg)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", default="hicons")
    ap.add_argument("--jobs", type=int, default=300)
    ap.add_argument("--users", type=int, default=5)
    ap.add_argument("--photos", type=int, default=60, help="jobs that get 2 photos each (~240 KB each, like real ones)")
    a = ap.parse_args()

    url = (os.environ.get("STAGING_SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("STAGING_SERVICE_KEY") or ""
    if not url or not key:
        die("set STAGING_SUPABASE_URL and STAGING_SERVICE_KEY (the staging project's, never production's)")
    ref = re.sub(r"^https://([^.]+)\..*$", r"\1", url)
    if ref in PRODUCTION_REFS or url.endswith("bsynch.com"):
        die("that is a production database. Seed only the staging project.")
    H = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "return=representation"}

    def post(table, rows):
        out = []
        for i in range(0, len(rows), 200):
            r = requests.post(f"{url}/rest/v1/{table}", headers=H, json=rows[i:i + 200], timeout=60)
            if not r.ok:
                die(f"{table}: {r.status_code} {r.text[:300]}")
            out += r.json()
        return out

    def config(k, v):
        r = requests.post(f"{url}/rest/v1/app_config", json={"key": k, "value": v},
                          headers={**H, "Prefer": "resolution=merge-duplicates,return=minimal"}, timeout=30)
        if not r.ok:
            die(f"app_config {k}: {r.text[:200]}")

    co = a.company
    agreement_version = re.search(r'CONTRACTOR_AGREEMENT_VERSION = "([^"]+)"',
                                  open(os.path.join(os.path.dirname(__file__), "..", "app.py")).read()).group(1)
    # people
    creds, users, roles = [], [], {}
    for i in range(1, a.users + 1):
        name = f"LoadTest {'Manager' if i == 1 else 'Worker'} {i}"
        pw = secrets.token_urlsafe(12)
        creds.append((f"loadtest{i}", pw, "Manager" if i == 1 else "User"))
        users.append({"name": name, "username": f"loadtest{i}", "email": f"loadtest{i}@example.com",
                      "password": bcrypt.hashpw(pw.encode(), bcrypt.gensalt(10)).decode(), "role": "worker",
                      "approved": True, "contractor_company": co, "totp_enabled": False})
        roles[name] = "admin" if i == 1 else "member"
    requests.delete(f"{url}/rest/v1/app_users?username=like.loadtest*", headers=H, timeout=30)
    post("app_users", users)
    config(f"contractor_roles_{co}", roles)
    config(f"contractor_company_{co}", {"display_name": "LoadTest Co", "invoice_prefix": "LT", "emails": []})
    sig = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\n").decode()
    post("contractor_agreements", [{"user_name": u["name"], "company": co, "version": agreement_version,
                                    "agreement_text": "staging", "signer_name": u["name"], "signature_png": sig} for u in users])
    # clients, folders, projects
    folders = post("contractor_client_folders", [{"company": co, "name": f"Builder {c}", "color": col}
                                                 for c, col in zip("ABC", ("#0f766e", "#2563eb", "#7c3aed"))])
    clients = [f"Client {i:03d}" for i in range(1, 41)]
    post("contractor_contacts", [{"company": co, "kind": "client", "name": c, "emails": [f"{c.replace(' ', '').lower()}@example.com"],
                                  "folder_id": folders[i % 3]["id"] if i % 4 else None} for i, c in enumerate(clients)])
    projects = post("contractor_projects", [{"name": f"Project {i}", "company": co, "created_by": users[0]["name"]} for i in range(1, 6)])
    # work orders
    today = dt.date.today()
    jobs = []
    for i in range(1, a.jobs + 1):
        c = random.choice(clients)
        jobs.append({"company": co, "job_number": f"LT{i:05d}", "title": random.choice(["Warranty", "Paint touch up", "Drywall repair", "Leak check", "Punch list"]),
                     "description": "Load-test work order with fake data.", "client_name": c,
                     "client_email": f"{c.replace(' ', '').lower()}@example.com", "location": f"{100 + i} Test Street",
                     "status": random.choice(["open", "open", "in_progress", "completed"]), "priority": "normal",
                     "progress_pct": random.choice([0, 25, 50, 100]), "created_by": random.choice(users)["name"],
                     "assigned_to": random.choice(users)["name"], "project_id": random.choice(projects)["id"] if i % 5 == 0 else None,
                     "scheduled_date": (today + dt.timedelta(days=random.randint(-20, 20))).isoformat(),
                     "time_slot": random.choice(["morning", "afternoon", None]), "est_hours": random.choice([1, 2, 4, 8])})
    jobs = post("contractor_jobs", jobs)
    post("job_steps", [{"job_id": j["id"], "step_name": n, "order_num": k, "progress_pct": random.choice([0, 50, 100])}
                       for j in jobs for k, n in enumerate(random.sample(["Prep", "Repair", "Paint", "Clean up"], 2))])
    # photos of a realistic size (~240 KB)
    try:
        from PIL import Image
        buf = io.BytesIO()
        Image.frombytes("RGB", (900, 700), os.urandom(900 * 700 * 3)).save(buf, "JPEG", quality=35)
        photo = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        photo = "data:image/jpeg;base64," + base64.b64encode(os.urandom(180000)).decode()
    pj = random.sample(jobs, min(a.photos, len(jobs)))
    for i in range(0, len(pj), 10):
        post("job_photos", [{"job_id": j["id"], "photo_data": photo, "caption": "staging", "photo_type": "progress",
                             "uploaded_by": users[0]["name"]} for j in pj[i:i + 10] for _ in range(2)])
    print(f"Seeded {len(jobs)} work orders, {len(pj) * 2} photos, {len(users)} accounts in {ref} (company {co}).")
    print("Test accounts (keep them out of the repository):")
    for u, p, r in creds:
        print(f"  {u}:{p}   ({r})")
    print('k6:  -e LT_USERS="' + ",".join(f"{u}:{p}" for u, p, _ in creds) + '"')


if __name__ == "__main__":
    main()
