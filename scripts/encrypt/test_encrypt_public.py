"""password_key only. The function is loaded on its own (via ast) so the test never runs the module's top level,
which reads the workspace secrets file into the environment."""
import ast, re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "encrypt_public.py"


def _password_key():
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "password_key")
    ns = {"re": re}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(SRC), "exec"), ns)
    return ns["password_key"]


password_key = _password_key()


def test_archives_share_the_dashboard_key():
    base = password_key("slug/index.html")
    assert base == "slug/index.html"
    for p in ("slug/2026-10/index.html", "slug/mid-month/index.html", "slug/2026-11-09/index.html"):
        assert password_key(p) == base, p


def test_unrelated_paths_keep_their_own_key():
    for p in ("other/index.html", "slug/2026-1/index.html", "slug/2026-10-9/index.html", "slug/2026-10-091/index.html",
              "slug/x2026-10/index.html", "slug/2026-11-09/assets/logo.html", "slug/2026-11-09/page.html",
              "a/slug/2026-11-09/index.html", "slug/weekly/index.html"):
        assert password_key(p) == p, p
