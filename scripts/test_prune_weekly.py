import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prune_weekly


def mondays(n):
    d = date(2026, 11, 9)
    return [(d - timedelta(weeks=i)).isoformat() for i in range(n)]


def test_select_old_keeps_newest_13():
    ds = mondays(15)
    assert prune_weekly.select_old(list(reversed(ds)), 13) == sorted(ds)[:2]


def test_select_old_ignores_non_dates_and_small_sets():
    assert prune_weekly.select_old(["2026-11-09", "live", "2026-11"], 13) == []


def test_apply_replaces_with_stub_and_dry_run_does_not(tmp_path):
    pub = tmp_path / "public"
    for d in mondays(15) + ["assets"]:
        (pub / "s" / d).mkdir(parents=True)
        (pub / "s" / d / "index.html").write_text("SECRET")
    old = sorted(mondays(15))[:2]
    assert prune_weekly.run("s", 13, False, pub) == old
    assert all((pub / "s" / d / "index.html").read_text() == "SECRET" for d in old)
    prune_weekly.run("s", 13, True, pub)
    for d in old:
        t = (pub / "s" / d / "index.html").read_text()
        assert 'http-equiv="refresh"' in t and "SECRET" not in t and 'url=../"' in t
    assert (pub / "s" / "assets" / "index.html").read_text() == "SECRET"
    assert prune_weekly.run("s", 13, True, pub) == []  # stubs are not re-pruned
