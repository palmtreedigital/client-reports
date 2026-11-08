#!/usr/bin/env python3
"""Keep the newest N weekly archive pages of a slug live; replace older ones with a redirect to the live page.

    python3 scripts/prune_weekly.py <slug> --keep 13            # dry run: lists what would go
    python3 scripts/prune_weekly.py <slug> --keep 13 --apply    # replaces them

Only public/<slug>/YYYY-MM-DD/ folders are candidates. A pruned folder (encrypted page + its images) is deleted from
public/ and public-encrypted/ and a tiny unencrypted redirect (no client data) is left in its place. Same stub as
prune_archives.py. Never commits or pushes.
"""
import argparse
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PUBLIC, PLAIN = REPO / "public", REPO / "public-encrypted"
STUB_MARK = "archive-pruned"
STUB = f"""<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="{STUB_MARK}">
<meta http-equiv="refresh" content="0; url=../"><title>Report moved</title>
<p>This weekly report is no longer kept online. <a href="../">Open the latest report</a>.</p>
"""
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def select_old(dates, keep):
    """Dates older than the newest `keep` (oldest first). Non YYYY-MM-DD names are ignored."""
    ds = sorted({d for d in dates if DATE.fullmatch(d)}, reverse=True)
    return sorted(ds[keep:])


def is_stub(folder):
    page = folder / "index.html"
    return page.is_file() and STUB_MARK in page.read_text(encoding="utf-8", errors="replace")


def run(slug, keep, apply, public=PUBLIC, plain=PLAIN):
    base = Path(public) / slug
    if not base.is_dir():
        return []
    live = [p.name for p in base.iterdir() if p.is_dir() and DATE.fullmatch(p.name) and not is_stub(p)]
    old = select_old(live, keep)
    if apply:
        for d in old:
            shutil.rmtree(base / d)
            shutil.rmtree(Path(plain) / slug / d, ignore_errors=True)
            (base / d).mkdir()
            (base / d / "index.html").write_text(STUB, encoding="utf-8")
    return old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--keep", type=int, default=13)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.keep < 1:
        print("--keep must be at least 1")
        raise SystemExit(2)
    old = run(a.slug, a.keep, a.apply)
    if not old:
        print(f"Nothing to prune: {a.slug} has no more than {a.keep} weekly archive pages.")
        return
    verb = "Pruned" if a.apply else "Would prune"
    for d in old:
        print(f"  {verb} {a.slug}/{d}/")
    print("\nNext: git add -A public." if a.apply else f"\n{len(old)} page(s). Re-run with --apply.")


if __name__ == "__main__":
    main()
