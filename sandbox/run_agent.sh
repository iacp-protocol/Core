#!/usr/bin/env bash
# Usage:
#   AGENT_ID=agent_A PEER_INBOX_URL=http://localhost:8002/inbox PORT=8001 sandbox/run_agent.sh
#   AGENT_ID=agent_B PEER_INBOX_URL=http://localhost:8001/inbox PORT=8002 sandbox/run_agent.sh

set -euo pipefail

PORT="${PORT:-8001}"

# --app-dir . permet d'importer "sandbox.agents.app" depuis la racine du repo
python -m uvicorn --app-dir . sandbox.agents.app:app --host 0.0.0.0 --port "${PORT}" --reload
