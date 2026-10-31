#!/usr/bin/env python3
"""Keep each client's last 6 monthly archive pages live; replace older ones with a redirect to the live dashboard.

    python3 scripts/prune_archives.py 2026-10            # dry run: lists what would go
    python3 scripts/prune_archives.py 2026-10 --apply    # removes them (Chris's OK first)

<month> is the report month just published (2026-10 on 02/11/2026). Kept: that month and the 5 before it.
A pruned month's folder (encrypted page + its ad images) is deleted from public/ and public-encrypted/, and a
tiny unencrypted page holding no client data is left in its place, so old email links land on the live
dashboard instead of a 404. Deleted pages stay in git history. Never commits or pushes.
"""
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PUBLIC, PLAIN = REPO / "public", REPO / "public-encrypted"
KEEP = 6
STUB_MARK = "archive-pruned"
STUB = f"""<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="{STUB_MARK}">
<meta http-equiv="refresh" content="0; url=../"><title>Report moved</title>
<p>This monthly report is no longer kept online. <a href="../">Open the latest report</a>.</p>
"""
MONTH = re.compile(r"\d{4}-\d{2}")


def index(m):
    y, mo = map(int, m.split("-"))
    return y * 12 + mo - 1


def is_stub(folder):
    page = folder / "index.html"
    return page.is_file() and STUB_MARK in page.read_text(encoding="utf-8", errors="replace")


def due(month, keep=KEEP):
    """[(slug, YYYY-MM)] archive folders older than the last `keep` months, not already pruned."""
    cutoff = index(month) - keep + 1
    out = []
    for client in sorted(p for p in PUBLIC.iterdir() if p.is_dir()):
        for f in sorted(p for p in client.iterdir() if p.is_dir() and MONTH.fullmatch(p.name)):
            if index(f.name) < cutoff and not is_stub(f):
                out.append((client.name, f.name))
    return out


def prune(slug, m):
    shutil.rmtree(PUBLIC / slug / m)
    shutil.rmtree(PLAIN / slug / m, ignore_errors=True)
    (PUBLIC / slug / m).mkdir()
    (PUBLIC / slug / m / "index.html").write_text(STUB, encoding="utf-8")


def main(argv):
    args = [a for a in argv if a != "--apply"]
    if len(args) != 1 or not MONTH.fullmatch(args[0]):
        sys.exit(__doc__)
    todo = due(args[0])
    if not todo:
        print(f"Nothing to prune: every archive page is within the last {KEEP} months to {args[0]}.")
        return
    verb = "Pruned" if "--apply" in argv else "Would prune"
    for slug, m in todo:
        if "--apply" in argv:
            prune(slug, m)
        print(f"  {verb} {slug}/{m}/")
    if "--apply" not in argv:
        print(f"\n{len(todo)} page(s). Re-run with --apply after Chris's OK.")
    else:
        print("\nNext: git add -A public, commit with the month's dashboards, push only with Chris's OK.")


if __name__ == "__main__":
    main(sys.argv[1:])
