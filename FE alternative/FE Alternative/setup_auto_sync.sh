#!/bin/bash
# setup_auto_sync.sh
# One-time setup: enters Confluence credentials and schedules hourly auto-sync.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_from_confluence.py"

echo ""
echo "═══ FE Alternatives — Auto-Sync Setup ═══════════════════════════"
echo ""

# Step 1: Credentials
echo "Step 1/3: Confluence credentials"
python3 "$SYNC_SCRIPT" --setup
if [ $? -ne 0 ]; then
  echo "✗ Setup failed. Exiting."
  exit 1
fi

echo ""
echo "Step 2/3: Running first sync..."
python3 "$SYNC_SCRIPT" --force
if [ $? -ne 0 ]; then
  echo "✗ First sync failed. Check your credentials."
  exit 1
fi

echo ""
echo "Step 3/3: Setting up hourly auto-sync..."

CRON_CMD="/usr/bin/python3 \"$SYNC_SCRIPT\" >> /tmp/fe_sync.log 2>&1"
CRON_JOB="0 * * * * $CRON_CMD"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -qF "sync_from_confluence.py"; then
  echo "  ✓ Cron job already exists (no change needed)"
else
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "  ✓ Added hourly cron job"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Done! The HTML file will auto-update every hour when Confluence changes."
echo ""
echo "Useful commands:"
echo "  Manual sync:   python3 \"$SYNC_SCRIPT\""
echo "  Force sync:    python3 \"$SYNC_SCRIPT\" --force"
echo "  View sync log: tail -f /tmp/fe_sync.log"
echo "  Remove cron:   crontab -e  (then delete the sync line)"
echo ""
