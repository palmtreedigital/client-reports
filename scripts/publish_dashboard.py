#!/usr/bin/env python3
"""Stage one client's dashboard for publishing: plaintext page -> public-encrypted/, images -> public/,
encrypt that page, verify no plaintext reached public/. Never commits or pushes, never prints a password.

    python3 scripts/publish_dashboard.py <client-folder> <built-dashboard-dir>
    python3 scripts/publish_dashboard.py saint-somebody-w66ki4 "../client-saint-somebody/drafts/dashboard"

<built-dashboard-dir> is the build output: index.html plus an optional assets/ folder.
Then review `git status`, commit (the lefthook hook re-checks encryption) and push with Chris's OK.
Get the client's password in your own Terminal app with `make encrypt-show` - never in a chat.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = "staticryptEncryptedMsgUniqueVariableName"


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    client, src = argv[0].strip("/"), Path(argv[1]).expanduser().resolve()
    page = src / "index.html"
    if not re.fullmatch(r"[a-z0-9-]+", client):
        sys.exit(f"ERROR: client folder must be lowercase-with-hyphens, got {client!r}")
    if not page.is_file():
        sys.exit(f"ERROR: {page} not found - build the dashboard first")

    plain = REPO / "public-encrypted" / client / "index.html"
    plain.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(page, plain)
    print(f"  page    -> public-encrypted/{client}/index.html (git-ignored, never pushed)")
    if (src / "assets").is_dir():
        shutil.copytree(src / "assets", REPO / "public" / client / "assets", dirs_exist_ok=True)
        print(f"  assets  -> public/{client}/assets/")

    # Encrypt just this page; keep encrypt_public.py's password table out of the output.
    r = subprocess.run([sys.executable, "scripts/encrypt/encrypt_public.py", "--file", f"{client}/index.html"],
                       cwd=REPO, capture_output=True, text=True)
    status = [l.strip() for l in r.stdout.splitlines() if re.search(r"\.\.\. (OK|FAILED)$", l)]
    print("  encrypt ", *(status or ["no status line"]))
    if r.returncode != 0:
        sys.exit(f"ERROR: encryption failed: {r.stderr.strip()[:300]}")

    out = (REPO / "public" / client / "index.html").read_text(encoding="utf-8", errors="replace")
    title = re.search(r"<title>(.*?)</title>", plain.read_text(encoding="utf-8", errors="replace"), re.S)
    leaked = bool(title and title.group(1).strip() and title.group(1).strip() in out)
    if MARKER not in out or leaked:
        sys.exit(f"ERROR: public/{client}/index.html is not safely encrypted (marker={MARKER in out}, "
                 f"title leaked={leaked}) - do not commit")
    print(f"  verify   public/{client}/index.html encrypted, source title not present")
    print("\nNext: git status, commit (Add:/Update: prefix), push only with Chris's OK.")


if __name__ == "__main__":
    main(sys.argv[1:])
