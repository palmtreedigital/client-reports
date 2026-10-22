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
