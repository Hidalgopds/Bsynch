"""Error tracking: crashes are recorded, shown only to platform admins, emailed (grouped) and never leak secrets.
Run:  python tests/test_errors.py"""
from harness import *  # noqa: F401,F403

import app as A

seed()


# A screen that breaks on purpose (added before the first request, as Flask requires)
@A.app.route("/__boom")
def __boom():
    raise ValueError("database said no; apikey=eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZSJ9.abcdefghijk")


A.app.config["PROPAGATE_EXCEPTIONS"] = False   # behave like production: the person sees the error page

r = client().get("/__boom")
check("a broken screen shows the error page", r.status_code == 500)
check("the error page gives a short code to report", b"send us this code" in r.data)

rows = get("/api/platform/errors", "owner@example.com").json["errors"]
check("the error is listed for the owner", len(rows) == 1 and rows[0]["type"] == "ValueError" and rows[0]["path"] == "/__boom")
check("it names the line of code", "test_errors.py" in rows[0]["where"])
check("keys and tokens are hidden in the message", "eyJ" not in rows[0]["message"] and "[hidden]" in rows[0]["message"])
check("an email went out", any("BSynch error" in (m.get("subject") or "") for m in MAIL))

sent = len([m for m in MAIL if "BSynch error" in (m.get("subject") or "")])
client().get("/__boom"); client().get("/__boom")
rows = get("/api/platform/errors", "owner@example.com").json["errors"]
check("the same error is grouped and counted", len(rows) == 1 and rows[0]["count"] == 3)
check("no second email for the same error within the hour",
      len([m for m in MAIL if "BSynch error" in (m.get("subject") or "")]) == sent)

check("a Manager can't see errors", get("/api/platform/errors", "Hana").status_code == 403)
check("anonymous can't see errors", client().get("/api/platform/errors").status_code == 401)

ref = A._record_error(RuntimeError("scheduler hiccup"), "background: billing")
rows = get("/api/platform/errors", "owner@example.com").json["errors"]
check("background jobs are recorded too", rows[0]["path"] == "background: billing" and len(ref) == 6)

done("errors")
