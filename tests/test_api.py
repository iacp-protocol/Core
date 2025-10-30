from pathlib import Path
import sys
# Rendre importable le code sous ./src avec layout "src/"
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient  # type: ignore
from iacp_core.app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_ping_pong():
    payload = {
        "message_id": "00000000-0000-0000-0000-000000000000",
        "sender": "agent_A",
        "receiver": "agent_B",
        "intent": "ping",
        "payload": {"hello": "world"},
    }
    r = client.post("/iacp", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "pong"
    assert data["sender"] == "agent_B"
    assert data["receiver"] == "agent_A"
    assert data["payload"]["received"] is True
