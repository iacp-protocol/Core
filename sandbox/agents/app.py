import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
import httpx

AGENT_ID = os.getenv("AGENT_ID", "agent_A")
PEER_INBOX_URL = os.getenv("PEER_INBOX_URL", "http://localhost:8002/inbox")
LOG_DIR = Path("sandbox/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"agent_{AGENT_ID}.log"

app = FastAPI(title=f"IACP Sandbox Agent ({AGENT_ID})", version="0.0.1")

class IACPMessage(BaseModel):
    message_id: str
    sender: str
    receiver: str
    intent: str
    payload: Dict[str, Any]

def _log(event: str, data: Dict[str, Any]):
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "agent": AGENT_ID,
        "event": event,
        "data": data,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_ID}

@app.post("/inbox")
def inbox(msg: IACPMessage):
    # Log réception
    _log("inbox_received", msg.model_dump())

    # Règle S0 : ping → pong (echo)
    if msg.intent.lower() == "ping" and msg.receiver == AGENT_ID:
        reply = IACPMessage(
            message_id=str(uuid.uuid4()),
            sender=AGENT_ID,
            receiver=msg.sender,
            intent="pong",
            payload={"received": True, **msg.payload},
        )
        _log("inbox_reply", reply.model_dump())
        return reply

    # Sinon, on log un unsupported
    _log("inbox_unsupported", msg.model_dump())
    return {"error": "unsupported_or_wrong_receiver", "agent": AGENT_ID}

@app.post("/send")
def send():
    """Envoie un ping à l'agent pair et retourne sa réponse."""
    ping = {
        "message_id": "00000000-0000-0000-0000-000000000000",
        "sender": AGENT_ID,
        "receiver": "agent_B" if AGENT_ID == "agent_A" else "agent_A",
        "intent": "ping",
        "payload": {"hello": "world"},
    }
    _log("outbox_send", ping)
    with httpx.Client(timeout=5.0) as client:
        r = client.post(PEER_INBOX_URL, json=ping)
        r.raise_for_status()
        data = r.json()
        _log("outbox_response", data)
        return data
