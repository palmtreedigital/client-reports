import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "encrypt"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import encrypt_public as E  # noqa: E402
import publish_dashboard as P  # noqa: E402


def test_mid_month_page_uses_dashboard_key():
    assert E.password_key("arcaa-xgm0sb/mid-month/index.html") == "arcaa-xgm0sb/index.html"


def test_other_paths_unchanged():
    assert E.password_key("arcaa-xgm0sb/index.html") == "arcaa-xgm0sb/index.html"
    assert E.password_key("arcaa-xgm0sb/other/index.html") == "arcaa-xgm0sb/other/index.html"


def test_same_password_for_both_pages():
    s = "test-secret-not-real"
    a = E.derive_password(s, E.password_key("a-1/index.html"))
    b = E.derive_password(s, E.password_key("a-1/mid-month/index.html"))
    assert a == b


def test_publish_target_paths():
    assert P.target("a-1", None) == "a-1/index.html"
    assert P.target("a-1", "mid-month") == "a-1/mid-month/index.html"


def test_password_is_readable_passphrase():
    import re
    pw = E.derive_password("test-secret-not-real", "a-1/index.html")
    assert re.fullmatch(r"[a-z]{3,5}-[a-z]{3,5}-[a-z]{3,5}-\d\d", pw)


def test_passwords_differ_per_client():
    s = "test-secret-not-real"
    assert E.derive_password(s, "a-1/index.html") != E.derive_password(s, "b-2/index.html")


def test_archive_page_uses_dashboard_key():
    assert E.password_key("arcaa-xgm0sb/2026-10/index.html") == "arcaa-xgm0sb/index.html"
    assert E.password_key("arcaa-xgm0sb/2026-10/other.html") == "arcaa-xgm0sb/2026-10/other.html"


def test_archive_publish_target():
    assert P.target("a-1", "2026-10") == "a-1/2026-10/index.html"


def _site(tmp_path, monkeypatch, months, stub=()):
    import prune_archives as A
    pub, plain = tmp_path / "public", tmp_path / "public-encrypted"
    for m in months:
        (pub / "a-1" / m / "assets").mkdir(parents=True)
        (pub / "a-1" / m / "index.html").write_text(A.STUB if m in stub else "encrypted")
        (plain / "a-1" / m).mkdir(parents=True)
    (pub / "a-1" / "mid-month").mkdir(parents=True)
    monkeypatch.setattr(A, "PUBLIC", pub)
    monkeypatch.setattr(A, "PLAIN", plain)
    return A, pub, plain


def test_prune_keeps_last_six_months(tmp_path, monkeypatch):
    A, _, _ = _site(tmp_path, monkeypatch, ["2026-04", "2026-05", "2026-10", "2027-01"])
    assert A.due("2027-03") == [("a-1", "2026-04"), ("a-1", "2026-05")]
    assert A.due("2026-10") == [("a-1", "2026-04")]  # kept: May to October
    assert A.due("2026-09") == []


def test_prune_crosses_year_end(tmp_path, monkeypatch):
    A, _, _ = _site(tmp_path, monkeypatch, ["2026-07", "2026-08"])
    assert A.due("2027-01") == [("a-1", "2026-07")]


def test_prune_leaves_redirect_and_skips_it_next_time(tmp_path, monkeypatch):
    A, pub, plain = _site(tmp_path, monkeypatch, ["2026-04"])
    A.prune("a-1", "2026-04")
    assert not (pub / "a-1" / "2026-04" / "assets").exists()
    assert not (plain / "a-1" / "2026-04").exists()
    assert 'url=../' in (pub / "a-1" / "2026-04" / "index.html").read_text()
    assert A.due("2027-03") == []
