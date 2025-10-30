#!/usr/bin/env bash
python -m uvicorn iacp_core.app:app --reload --host 0.0.0.0 --port 8000
