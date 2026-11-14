"""Test harness: runs the real app against an in-memory imitation of Supabase (PostgREST).

Nothing here talks to the internet or to a real database. Every test file does
    from harness import *
and then uses client(), login(), get(), send(), check() and the DB dict.
"""
import copy
import datetime as _dt
import json
import os
import re
import sys
import uuid
from urllib.parse import parse_qsl, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

# A safe, fake environment: no real database, no mail, no AI, no schedulers
os.environ.update({
    "SUPABASE_URL": "http://fake-supabase.local", "SUPABASE_KEY": "fake-service-key",
    "SECRET_KEY": "test-secret-key", "CT_SCHEDULER": "0", "ERP_AUTH_MODE": "enforce",
    "DEFAULT_COMPANY_ADMIN_USER": "owner@example.com", "ADMIN_EMAIL": "admin@example.com",
})
for _k in ("CT_TRUST_HEADER", "RESEND_API_KEY", "SMTP_EMAIL", "SMTP_PASSWORD", "CONTRACTOR_SMTP_HOST",
           "CONTRACTOR_SMTP_USER", "CONTRACTOR_SMTP_PASSWORD", "ANTHROPIC_API_KEY", "KIOSK_ADMIN_PASS",
           "SECURITY_REPORT_TO", "BACKUPS_CONFIRMED", "PIN_PEPPER", "CRON_SECRET"):
    os.environ.pop(_k, None)

import requests  # noqa: E402

DB = {}
UNIQUE = {  # columns that must be unique, like the real tables
    "app_config": [("key",)], "app_settings": [("key",)], "app_users": [("name",), ("username",)],
    "workers": [("name",), ("pin",)], "safety_meetings": [("worker_name", "date")],
    "notification_reads": [("notification_id", "worker_name")],
}
CALLS = []  # (method, table) of every fake database call, for tests that need to look


class Resp:
    def __init__(self, data, status=200, headers=None):
        self._d = data
        self.status_code = status
        self.ok = 200 <= status < 300
        self.text = json.dumps(data) if not isinstance(data, str) else data
        self.headers = headers or {}
        self.content = self.text.encode()

    def json(self):
        if isinstance(self._d, str):
            raise ValueError("not json")
        return self._d


def _now():
    return _dt.datetime.utcnow().isoformat() + "Z"


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _split_top(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def _cmp(val, rest):
    neg = False
    if rest.startswith("not."):
        neg, rest = True, rest[4:]
    res = _cmp1(val, rest)
    return (not res) if neg else res


def _cmp1(val, rest):
    if rest == "is.null":
        return val is None
    if rest == "is.true":
        return val is True
    if rest == "is.false":
        return val is False
    if rest.startswith("in.(") and rest.endswith(")"):
        return str(val) in [x.strip().strip('"') for x in _split_top(rest[4:-1])]
    op, _, arg = rest.partition(".")
    arg = arg.strip('"')
    if op == "eq":
        if isinstance(val, bool):
            return str(val).lower() == arg.lower()
        a, b = _num(val), _num(arg)
        if a is not None and b is not None and not isinstance(val, str):
            return a == b
        return str(val) == arg
    if op == "neq":
        return str(val) != arg
    if op in ("like", "ilike"):
        if val is None:
            return False
        pat = "^" + re.escape(arg).replace(r"\*", ".*").replace("%", ".*") + "$"
        return re.match(pat, str(val), re.I if op == "ilike" else 0) is not None
    if op == "cs":
        try:
            want = json.loads(arg)
        except ValueError:
            want = [x.strip('"') for x in arg.strip("{}").split(",") if x]
        have = val or []
        return all(w in have for w in (want if isinstance(want, list) else [want]))
    if val is None:
        return False
    a, b = _num(val), _num(arg)
    if a is not None and b is not None and not isinstance(val, str):
        x, y = a, b
    else:
        x, y = str(val), arg
    return {"gt": x > y, "gte": x >= y, "lt": x < y, "lte": x <= y}.get(op, True)


def _cond(row, expr):
    expr = expr.strip()
    for op in ("and", "or"):
        if expr.startswith(op + "(") and expr.endswith(")"):
            parts = _split_top(expr[len(op) + 1:-1])
            res = [_cond(row, p) for p in parts]
            return all(res) if op == "and" else any(res)
    col, rest = expr.split(".", 1)
    return _cmp(row.get(col), rest)


_SKIP = {"select", "order", "limit", "offset", "on_conflict", "columns"}


def _match(row, filters):
    for k, v in filters:
        if k in _SKIP:
            continue
        if k in ("or", "and"):
            if not _cond(row, k + v):
                return False
            continue
        if not _cmp(row.get(k), v):
            return False
    return True


def _parse(url, params=None):
    u = urlparse(url)
    path = u.path.split("/rest/v1/", 1)[-1]
    filters = parse_qsl(u.query, keep_blank_values=True)
    if params:
        filters += list(params.items()) if isinstance(params, dict) else list(params)
    return path, filters


def _project(rows, filters):
    sel = dict(filters).get("select")
    if not sel or sel.strip() == "*":
        return [dict(r) for r in rows]
    cols = []
    for c in _split_top(sel):
        c = c.strip()
        if "(" in c:  # embedded resource: give an empty list
            name = c.split("(", 1)[0].split(":")[-1].split("!")[0]
            cols.append(("__embed__", name))
        elif c == "*":
            cols.append(("*", "*"))
        else:
            cols.append((c.split(":")[0], c.split(":")[-1]))
    out = []
    for r in rows:
        o = {}
        for alias, c in cols:
            if alias == "*":
                o.update(r)
            elif alias == "__embed__":
                o[c] = list(r.get(c) or [])
            else:
                o[alias] = r.get(c)
        out.append(o)
    return out


def _order(rows, filters):
    order = dict(filters).get("order")
    if not order:
        return rows
    for part in reversed(order.split(",")):
        bits = part.split(".")
        col, desc = bits[0], "desc" in bits[1:]
        rows = sorted(rows, key=lambda r: (r.get(col) is None, str(r.get(col)) if _num(r.get(col)) is None or isinstance(r.get(col), str) else _num(r.get(col))),
                      reverse=desc)
    return rows


def _page(rows, filters, headers):
    f = dict(filters)
    off = int(f.get("offset") or 0)
    rng = (headers or {}).get("Range")
    if rng and "-" in rng:
        a, b = rng.split("-")
        return rows[int(a):int(b) + 1]
    lim = f.get("limit")
    return rows[off:off + int(lim)] if lim else rows[off:]


def _prefer(headers):
    return (headers or {}).get("Prefer", "")


STORAGE = {}  # "bucket/path" -> (bytes, mime): a fake Supabase Storage
STORAGE_DOWN = {"on": False}  # tests flip this to see the fallback to the database


def _storage_key(url):
    p = url.split("/storage/v1/object/", 1)[1].split("?", 1)[0]
    for pre in ("authenticated/", "public/"):
        if p.startswith(pre):
            p = p[len(pre):]
    return p


def fake_get(url, params=None, headers=None, timeout=None, **kw):
    if "/storage/v1/object/" in url:
        hit = None if STORAGE_DOWN["on"] else STORAGE.get(_storage_key(url))
        if not hit:
            return Resp({"error": "not found"}, 404)
        r = Resp("", 200, {"Content-Type": hit[1]})
        r.content = hit[0]
        return r
    if "/rest/v1/" not in url:
        return Resp({"error": "offline in tests"}, 404)
    path, filters = _parse(url, params)
    CALLS.append(("GET", path))
    rows = [r for r in DB.get(path, []) if _match(r, filters)]
    total = len(rows)
    rows = _page(_order(rows, filters), filters, headers)
    h = {}
    if "count=exact" in _prefer(headers):
        h["Content-Range"] = f"0-{max(len(rows) - 1, 0)}/{total}"
    return Resp(copy.deepcopy(_project(rows, filters)), 200, h)


def _dup(table, row, rows):
    for cols in UNIQUE.get(table, []):
        if all(row.get(c) is not None for c in cols):
            for r in rows:
                if r is not row and all(r.get(c) == row.get(c) for c in cols):
                    return r, cols
    return None, None


def fake_post(url, json=None, data=None, headers=None, timeout=None, params=None, **kw):
    if "/storage/v1/object/" in url:
        key = _storage_key(url)
        if STORAGE_DOWN["on"]:
            return Resp({"error": "storage down"}, 503)
        if key in STORAGE:
            return Resp({"error": "Duplicate"}, 409)
        STORAGE[key] = (data, (headers or {}).get("Content-Type"))
        return Resp({"Key": key}, 200)
    if "/rest/v1/" not in url:
        return Resp({"ok": True}, 200)  # storage uploads, outside services
    path, filters = _parse(url, params)
    CALLS.append(("POST", path))
    if path.startswith("rpc/"):
        fn = path[4:]
        if fn == "security_self_check":
            return Resp({"tables_without_rls": [], "anon_policies": [], "public_buckets": [], "anon_functions": []})
        return Resp([])
    pref = _prefer(headers)
    rows = DB.setdefault(path, [])
    items = json if isinstance(json, list) else [json or {}]
    out = []
    for it in items:
        row = {"id": str(uuid.uuid4()), "created_at": _now(), **copy.deepcopy(it)}
        if path in ("app_config", "app_settings"):
            row.pop("id", None)
        old, cols = _dup(path, row, rows)
        if old is not None:
            if "merge-duplicates" in pref:
                old.update({k: v for k, v in it.items()})
                out.append(old)
                continue
            if "ignore-duplicates" in pref:
                continue
            return Resp({"code": "23505", "message": "duplicate key value violates unique constraint"}, 409)
        rows.append(row)
        out.append(row)
    if "return=minimal" in pref:
        return Resp("", 201)
    return Resp(copy.deepcopy(out), 201)


def fake_patch(url, json=None, data=None, headers=None, timeout=None, params=None, **kw):
    if "/rest/v1/" not in url:
        return Resp({}, 200)
    path, filters = _parse(url, params)
    CALLS.append(("PATCH", path))
    rows = DB.get(path, [])
    hit = [r for r in rows if _match(r, filters)]
    for r in hit:
        new = dict(r, **copy.deepcopy(json or {}))
        old, _ = _dup(path, new, [x for x in rows if x is not r])
        if old is not None:
            return Resp({"code": "23505", "message": "duplicate key value violates unique constraint"}, 409)
    for r in hit:
        r.update(copy.deepcopy(json or {}))
    if "return=minimal" in _prefer(headers):
        return Resp("", 204)
    return Resp(copy.deepcopy(hit), 200)


def fake_delete(url, headers=None, timeout=None, params=None, json=None, **kw):
    if "/storage/v1/object/" in url:
        bucket = url.split("/storage/v1/object/", 1)[1].strip("/")
        gone = [p for p in (json or {}).get("prefixes", []) if STORAGE.pop(f"{bucket}/{p}", None)]
        return Resp([{"name": p} for p in gone], 200)
    if "/rest/v1/" not in url:
        return Resp({}, 200)
    path, filters = _parse(url, params)
    CALLS.append(("DELETE", path))
    rows = DB.get(path, [])
    gone = [r for r in rows if _match(r, filters)]
    DB[path] = [r for r in rows if r not in gone]
    return Resp(copy.deepcopy(gone), 200)


STRIPE = {"calls": [], "fail": False, "sub": None}  # a fake Stripe API: tests read the calls the app made


def fake_request(method, url, **kw):
    if "api.stripe.com" in url:
        path = url.split("/v1/", 1)[1]
        STRIPE["calls"].append((method.upper(), path, dict(kw.get("data") or {})))
        if STRIPE["fail"]:
            return Resp({"error": {"message": "card_declined"}}, 402)
        if path == "checkout/sessions":
            return Resp({"id": "cs_test_1", "url": "https://checkout.stripe.com/c/pay/cs_test_1"})
        if path == "billing_portal/sessions":
            return Resp({"id": "bps_1", "url": "https://billing.stripe.com/p/session/test_1"})
        if path.startswith("subscriptions/"):
            return Resp(STRIPE["sub"] or {"id": path.split("/")[1], "items": {"data": []}})
        return Resp({"id": "si_new", "deleted": method.upper() == "DELETE"})
    return {"GET": fake_get, "POST": fake_post, "PATCH": fake_patch, "PUT": fake_patch,
            "DELETE": fake_delete}[method.upper()](url, **kw)


requests.get, requests.post, requests.patch, requests.put, requests.delete = (
    fake_get, fake_post, fake_patch, fake_patch, fake_delete)
requests.request = fake_request

import bcrypt  # noqa: E402

import app as A  # noqa: E402  (the real app, now talking to the fake database)

A.app.config.update(TESTING=True, AUDIT_SYNC=True, TESTING_NO_PIN_MIGRATE=True)
A._ct_bg = lambda fn, *a, **k: fn(*a, **k)  # background jobs run inline in tests
A._ct_digest_day["checked"] = 1e18           # no daily digests during tests
MAIL = []                                     # every email the app tries to send


def _fake_mail(to, cc, subject, html, reply_to=None, from_name=None):
    MAIL.append({"to": list(to or []), "cc": list(cc or []), "subject": subject, "html": html, "from": from_name})
    return True, None


A._ct_send_email = _fake_mail


def pw(name):
    return "pw-" + name.lower()


def _hash(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt(4)).decode()


def seed():
    """Fake companies and people. Hicons: Hana (Manager), Mia (User). Bsynch: Bob (Leader).
    Owner: the platform owner account. Crew One / Crew New: ERP crew with PINs."""
    DB.clear()
    MAIL.clear()
    for d in (A._ip_hits, A._key_hits, A._pin_fails, A._sec_alert_last):
        d.clear()
    users = [
        {"name": "Hana", "username": "hana", "email": "hana@example.com", "role": "worker", "contractor_company": "hicons"},
        {"name": "Mia", "username": "mia", "email": "mia@example.com", "role": "worker", "contractor_company": "hicons"},
        {"name": "Bob", "username": "bob", "email": "bob@example.com", "role": "worker", "contractor_company": "bsynch"},
        {"name": "Newbie", "username": "newbie", "email": "newbie@example.com", "role": "worker", "contractor_company": None},
    ]
    for u in users:
        u.update(approved=True, password=_hash(pw(u["name"])), totp_enabled=False)
    users.append({"name": "Owner", "username": "owner@example.com", "email": "owner@example.com", "role": "admin",
                  "approved": True, "password": _hash("pw-owner"), "totp_enabled": False, "contractor_company": None})
    users.append({"name": "Crew One", "role": "lead", "approved": True, "pin": "4821", "password": None})
    users.append({"name": "Crew New", "role": "lead", "approved": True, "pin": None, "password": None})
    DB["app_users"] = [dict(id=str(uuid.uuid4()), **u) for u in users]
    future = "2099-01-01T00:00:00Z"
    DB["app_config"] = [
        {"key": "contractor_platform_admins", "value": []},
        {"key": "contractor_roles_hicons", "value": {"Hana": "admin", "Mia": "member"}},
        {"key": "contractor_roles_bsynch", "value": {"Bob": "lead"}},
        {"key": "contractor_support_hicons", "value": {"until": future, "by": "Hana"}},
        {"key": "contractor_support_bsynch", "value": {"until": future, "by": "Bob"}},
        {"key": "contractor_company_hicons", "value": {"display_name": "Hicons, LLC", "invoice_prefix": "H", "emails": ["office@example.com"]}},
    ]
    DB["contractor_agreements"] = [{"id": str(uuid.uuid4()), "user_name": n, "company": c, "version": A.CONTRACTOR_AGREEMENT_VERSION,
                                    "signed_at": _now()} for n, c in (("Hana", "hicons"), ("Mia", "hicons"), ("Bob", "bsynch"))]
    DB["contractor_projects"] = [{"id": "p1", "name": "Hicons tower", "company": "hicons"},
                                 {"id": "p2", "name": "Bsynch mall", "company": "bsynch"}]
    DB["contractor_jobs"] = [{"id": "j1", "job_number": "WO-001", "title": "Roof", "company": "hicons", "project_id": "p1",
                              "status": "open", "progress_pct": 0, "created_by": "Hana", "created_at": _now()},
                             {"id": "j2", "job_number": "B-1", "title": "Mall floor", "company": "bsynch", "project_id": "p2",
                              "status": "open", "progress_pct": 0, "created_by": "Bob", "created_at": _now()}]
    for t in ("contractor_contacts", "contractor_client_folders", "contractor_invoices", "contractor_estimates", "job_steps",
              "job_photos", "job_visits", "job_materials", "job_receipts", "contractor_expenses", "contractor_mail_log",
              "contractor_support_log", "contractor_locations", "audit_log", "auth_report", "workers", "checkins",
              "attendance_reports", "notifications", "notification_reads", "safety_meetings", "bsynch_companies",
              "homelab_kids", "homelab_guardians", "homelab_kid_photos", "worker_location_history", "app_settings"):
        DB.setdefault(t, [])


def client():
    return A.app.test_client()


def login(cl, user, password=None):
    return cl.post("/api/login", json={"username": user, "password": password or pw(user)})


_CLIENTS = {}


def as_user(name):
    """A signed-in client for a seeded person (cached)."""
    if name not in _CLIENTS:
        cl = client()
        r = login(cl, name, "pw-owner" if name == "owner@example.com" else None)
        assert r.status_code == 200, f"sign-in failed for {name}: {r.status_code} {r.data[:200]}"
        _CLIENTS[name] = cl
    return _CLIENTS[name]


def forget_sessions():
    _CLIENTS.clear()


def get(path, user, company=None):
    h = {"X-Contractor-Company": company} if company else {}
    return as_user(user).get(path, headers=h)


def send(method, path, user, body=None, company=None):
    h = {"X-Contractor-Company": company} if company else {}
    return getattr(as_user(user), method.lower())(path, json=body, headers=h)


RESULTS = {"pass": 0, "fail": []}


def check(label, cond):
    if cond:
        RESULTS["pass"] += 1
    else:
        RESULTS["fail"].append(label)
        print("FAIL", label)


def done(name):
    ok = not RESULTS["fail"]
    print(f"{name}: {RESULTS['pass']} passed, {len(RESULTS['fail'])} failed" + ("" if ok else " -> " + "; ".join(RESULTS["fail"])))
    sys.exit(0 if ok else 1)
