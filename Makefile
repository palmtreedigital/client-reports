# ENCRYPT_SECRET comes from 1Password via the loader; encrypt_public.py still falls back to a
# local key file if one exists, so this works on a machine without the loader too.
LOAD = OP_REF_FILE="$$HOME/.claude/secrets-client-reports.op"; [ -f "$$HOME/.claude/bin/load-secrets.sh" ] && . "$$HOME/.claude/bin/load-secrets.sh";

encrypt:
	@$(LOAD) python3 scripts/encrypt/encrypt_public.py

encrypt-show:
	@$(LOAD) python3 scripts/encrypt/encrypt_public.py --show

# make publish CLIENT=saint-somebody-w66ki4 SRC=../client-saint-somebody/drafts/dashboard
# make publish CLIENT=arcaa-xgm0sb SRC=../client-arcaa/drafts/mid-month SUB=mid-month   (same password as the dashboard)
publish:
	@$(LOAD) python3 scripts/publish_dashboard.py "$(CLIENT)" "$(SRC)" "$(SUB)"
