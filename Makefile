# ENCRYPT_SECRET comes from 1Password via the loader; encrypt_public.py still falls back to a
# local key file if one exists, so this works on a machine without the loader too.
LOAD = OP_REF_FILE="$$HOME/.claude/secrets-client-reports.op"; [ -f "$$HOME/.claude/bin/load-secrets.sh" ] && . "$$HOME/.claude/bin/load-secrets.sh";

encrypt:
	@$(LOAD) python3 scripts/encrypt/encrypt_public.py

encrypt-show:
	@$(LOAD) python3 scripts/encrypt/encrypt_public.py --show

# make publish CLIENT=saint-somebody-w66ki4 SRC=../client-saint-somebody/drafts/dashboard
# make publish CLIENT=arcaa-xgm0sb SRC=../client-arcaa/drafts/mid-month SUB=mid-month   (same password as the dashboard)
# make publish CLIENT=arcaa-xgm0sb SRC=../client-arcaa/drafts/dashboard SUB=2026-10     (monthly archive, same password)
publish:
	@$(LOAD) python3 scripts/publish_dashboard.py "$(CLIENT)" "$(SRC)" "$(SUB)"

# make prune MONTH=2026-10            lists monthly archive pages older than 6 months (dry run)
# make prune MONTH=2026-10 APPLY=1    replaces them with a redirect to the live dashboard (Chris's OK first)
prune:
	@python3 scripts/prune_archives.py $(MONTH) $(if $(APPLY),--apply)

# make prune-weekly SLUG=topanga-shbdnj KEEP=13            lists weekly archive pages beyond the newest 13 (dry run)
# make prune-weekly SLUG=topanga-shbdnj KEEP=13 APPLY=1    replaces them with a redirect to the live page
prune-weekly:
	@python3 scripts/prune_weekly.py "$(SLUG)" --keep $(or $(KEEP),13) $(if $(APPLY),--apply)
