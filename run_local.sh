#!/usr/bin/env bash
# Lance l'app en indiquant explicitement où se trouve le code (./src)
python -m uvicorn --app-dir src iacp_core.app:app --reload --host 0.0.0.0 --port 8000
