"""One Gmail draft per client (Gravity + NED + Sollos combined) with the new report password. Never sends.
Prints only 'DRAFTED <clients> <draft id>' - the password goes into the draft and nowhere else.
Run after a password change has been pushed and deployed (each run makes a fresh set of drafts):

    OP_REF_FILE="$HOME/.claude/secrets-client-reports.op" . ~/.claude/bin/load-secrets.sh >/dev/null 2>&1
    python3 scripts/password_notice.py
"""
import os, sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/client-dashboard/engine"))
import monthly_email as ME  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {
    "arcaa-xgm0sb": "ARCAA", "basil-bangs-vz4yzd": "Basil Bangs", "dometic-3e0fdn": "Dometic",
    "dometic-marine-fyukgm": "Dometic Marine", "dreamy-moons-adchz8": "Dreamy Moons",
    "dreamy-moons-eu-uk-03by8e": "Dreamy Moons EU/UK", "gravity-8xflfa": "Gravity", "hank-z8ctq3": "Hank",
    "hepburn-hardware-dnb8ms": "Hepburn Hardware", "luxury-boat-detailing-5rllus": "Luxury Boat Detailing",
    "ned-41xu0v": "NED", "nine-lives-bazaar-3rvnhq": "Nine Lives Bazaar", "saint-somebody-w66ki4": "Saint Somebody",
    "sollos-jgdl6w": "Sollos",
}
GROUPS = [["gravity-8xflfa", "ned-41xu0v", "sollos-jgdl6w"]]


def links(slug):
    out = []
    if os.path.exists(f"{REPO}/public/{slug}/index.html"):
        out.append(f"Monthly report: {ME.report_url(slug)}")
    if os.path.exists(f"{REPO}/public/{slug}/mid-month/index.html"):
        out.append(f"Mid-month update: {ME.PAGES}/{slug}/mid-month/")
    return out


def block(slug, label_name):
    head = [f"{NAMES[slug]}:"] if label_name else []
    return head + [f"Password: {ME.password_for(slug)}", *links(slug), ""]


def body(slugs):
    many = len(slugs) > 1
    what = "passwords for your report pages have" if many else "password for your report page has"
    lines = ["Hi team,", "",
             f"Quick heads-up: the {what} changed. A few of you found the old long random passwords hard to "
             "copy and paste, so the new ones are a few short words instead, all lowercase.", ""]
    for s in slugs:
        lines += block(s, many)
    lines += ["The old password no longer works. If you ticked Keep me signed in, you'll be asked for the new "
              "one once, then it remembers you again.", "", "Cheers,", "Chris"]
    return "\n".join(lines)


def main():
    unnamed = sorted(d for d in os.listdir(f"{REPO}/public") if os.path.isdir(f"{REPO}/public/{d}") and d not in NAMES)
    if unnamed:
        sys.exit(f"add a display name to NAMES for {unnamed}")
    grouped = {s for g in GROUPS for s in g}
    jobs = [g for g in GROUPS] + [[s] for s in NAMES if s not in grouped]
    for slugs in jobs:
        missing = [s for s in slugs if not links(s)]
        if missing:
            sys.exit(f"no published page for {missing}")
        who = " + ".join(NAMES[s] for s in slugs)
        subject = f"{', '.join(NAMES[s] for s in slugs)}: new password for your reports"
        heads = [f"{NAMES[s]}:" for s in slugs] if len(slugs) > 1 else []
        print(f"DRAFTED {who} {ME.draft(subject, body(slugs), heads)}", flush=True)


if __name__ == "__main__":
    main()
