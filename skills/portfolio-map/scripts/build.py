#!/usr/bin/env python3
"""Build the portfolio map: map-data.json + template -> one self-contained HTML file.

    python3 build.py path/to/map-data.json [path/to/portfolio-map.html]
    python3 build.py --selftest

Output defaults to portfolio-map.html next to the data file. Stdlib only.

At build time, for every project with a "repo" (absolute, ~, or relative to the
data file) it reads from git: the repo's last commit date and the last commit
of <repo>/architecture-map.html, so the card can say "not built" or "stale".
It also fills each person's "days" from "last", and derives "urgency" when the
data does not set one.
"""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
ARCH_FILE = "architecture-map.html"


def last_commit(repo, path=None):
    args = ["git", "-C", str(repo), "log", "-1", "--format=%cs"] + (["--", path] if path else [])
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def days_since(day, today):
    try:
        return (today - date.fromisoformat(day)).days
    except (TypeError, ValueError):
        return None


def urgency(status, days):
    """act: booked or nudge overdue · warm: live thread ≤14d · wait: sent ≤14d or unknown · cold: >21d or closed."""
    if status == "booked":
        return "act"
    if status == "closed" or (days is not None and days > 21):
        return "cold"
    if days is None:
        return "wait"
    if days > 14:
        return "act"  # no reply after 14 days: one nudge is due
    return "warm" if status in ("warm", "replied") else "wait"


def build(data, base, today):
    data["generated"] = today.isoformat()
    for p in data["projects"]:
        repo = Path(p["repo"]).expanduser() if p.get("repo") else None
        if repo and not repo.is_absolute():
            repo = base / repo
        arch = repo / ARCH_FILE if repo else None
        p["repo_found"] = bool(repo and repo.is_dir())
        p["repo_last"] = last_commit(repo) if p["repo_found"] else None
        p["arch_url"] = arch.resolve().as_uri() if arch and arch.exists() else None
        p["arch_last"] = last_commit(repo, ARCH_FILE) if p["arch_url"] else None
    for person in data["people"]:
        person["days"] = days_since(person.get("last"), today)
        person.setdefault("urgency", urgency(person.get("status"), person["days"]))
    known = {p["id"] for p in data["projects"]} | {p["id"] for p in data["people"]}
    for e in data["edges"]:
        if e["s"] not in known or e["t"] not in known:
            print(f"warning: edge {e['s']} -> {e['t']} names an unknown person or project", file=sys.stderr)
    # "</" would close the <script> tag early if a note contained "</script>".
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.read_text().replace("__DATA__", payload)


def selftest():
    assert urgency("booked", 40) == "act"
    assert urgency("closed", 1) == "cold"
    assert urgency("warm", 30) == "cold"
    assert urgency("sent", 20) == "act"
    assert urgency("replied", 3) == "warm"
    assert urgency("sent", 3) == "wait"
    assert urgency("sent", None) == "wait"
    d = {"projects": [{"id": "x", "repo": "does-not-exist"}],
         "people": [{"id": "A", "status": "sent", "last": "2026-01-01", "note": "</script>"}],
         "edges": [{"s": "A", "t": "x"}]}
    html = build(d, Path("/nonexistent"), date(2026, 1, 11))
    assert d["people"][0]["days"] == 10 and d["projects"][0]["repo_found"] is False
    assert "</script>\"" not in html and "__DATA__" not in html
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit()
    if not 1 <= len(sys.argv) - 1 <= 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name("portfolio-map.html")
    out.write_text(build(json.loads(src.read_text()), src.parent, date.today()))
    print(out)
