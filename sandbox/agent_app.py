# sandbox/agent_app.py  (IACP v0.3)
from fastapi import FastAPI, Body, HTTPException
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone
import os, json
import httpx
from pathlib import Path

# ====== Config ======
IACP_VERSION = "0.3"
AGENT_ID = os.getenv("AGENT_ID", "agent_X")
PEER_INBOX_URL = os.getenv("PEER_INBOX_URL", "http://localhost:8000/inbox")

LOG_DIR = Path(os.getenv("LOG_DIR", "/app/sandbox/logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = LOG_DIR / f"agent_{AGENT_ID}.audit.jsonl"

# ====== Utils: logging JSONL ======
def log_event(event: str, data: Dict[str, Any]) -> None:
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": AGENT_ID,
        "event": event,
        "data": data,
    }
    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception:
        pass

# ====== IACP v0.3 Model ======
class IACPMessage(BaseModel):
    intent: str = Field(..., min_length=1)
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None   # <— NOUVEAU en v0.3
    message_id: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    timestamp: Optional[str] = None
    reply_to: Optional[str] = None
    version: str = IACP_VERSION

    def ensure_defaults(self, default_sender: Optional[str] = None, default_receiver: Optional[str] = None):
        if not self.message_id:
            self.message_id = str(uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if default_sender and not self.sender:
            self.sender = default_sender
        if default_receiver and not self.receiver:
            self.receiver = default_receiver
        if not self.version:
            self.version = IACP_VERSION
        if self.headers is None:
            self.headers = {}
        # toujours un trace-id côté émetteur
        self.headers.setdefault("x-trace-id", str(uuid4()))
        return self

CAPABILITIES: List[str] = [
    "ping",
    "echo",
    "whoami",
    "caps",         # annoncer ses capacités
    "headers:v1",   # support des entêtes user-defined
]

# ====== App ======
app = FastAPI(title="IACP Sandbox Agent", version=IACP_VERSION)

@app.get("/health")
async def health():
    return {"status": "ok", "agent": AGENT_ID, "peer": PEER_INBOX_URL, "version": IACP_VERSION}

# ---- Capacités
@app.get("/caps")
async def caps():
    return {"agent": AGENT_ID, "version": IACP_VERSION, "capabilities": CAPABILITIES}

# ---- Handshake simple (interroge le /caps du pair)
@app.post("/handshake")
async def handshake():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(PEER_INBOX_URL.rsplit("/inbox", 1)[0] + "/caps")
        r.raise_for_status()
        peer_caps = r.json()
    return {"self": {"agent": AGENT_ID, "capabilities": CAPABILITIES}, "peer": peer_caps}

# ---------- /send ----------
@app.post("/send")
async def send_message(body: Dict[str, Any] = Body(...)):
    try:
        default_receiver = "agent_B" if AGENT_ID == "agent_A" else "agent_A"
        msg = IACPMessage(**body).ensure_defaults(default_sender=AGENT_ID, default_receiver=default_receiver)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"IACP schema error: {e}")

    log_event("outbox_send", msg.model_dump())

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(PEER_INBOX_URL, json=msg.model_dump())
        r.raise_for_status()
        peer_resp = r.json()

    log_event("outbox_response", peer_resp)
    return {"status": "sent", "response": peer_resp}

# ---------- /inbox ----------
@app.post("/inbox")
async def inbox(body: Dict[str, Any] = Body(...)):
    try:
        msg = IACPMessage(**body).ensure_defaults()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"IACP schema error: {e}")

    log_event("inbox_received", msg.model_dump())

    # Routeur minimal
    if msg.intent == "ping":
        reply = IACPMessage(
            intent="pong",
            payload={"received": True, "hello": "world"},
            headers={**(msg.headers or {}), "x-routed-by": AGENT_ID},
            reply_to=msg.message_id,
            sender=AGENT_ID,
            receiver=msg.sender
        ).ensure_defaults()

    elif msg.intent == "echo":
        reply = IACPMessage(
            intent="echo_ok",
            payload=msg.payload or {},
            headers={**(msg.headers or {}), "x-routed-by": AGENT_ID},
            reply_to=msg.message_id,
            sender=AGENT_ID,
            receiver=msg.sender
        ).ensure_defaults()

    elif msg.intent == "whoami":
        reply = IACPMessage(
            intent="whoami_ok",
            payload={"agent": AGENT_ID, "version": IACP_VERSION, "caps": CAPABILITIES},
            headers={**(msg.headers or {}), "x-routed-by": AGENT_ID},
            reply_to=msg.message_id,
            sender=AGENT_ID,
            receiver=msg.sender
        ).ensure_defaults()

    elif msg.intent == "caps":
        reply = IACPMessage(
            intent="caps_ok",
            payload={"capabilities": CAPABILITIES, "version": IACP_VERSION},
            headers={**(msg.headers or {}), "x-routed-by": AGENT_ID},
            reply_to=msg.message_id,
            sender=AGENT_ID,
            receiver=msg.sender
        ).ensure_defaults()

    else:
        reply = IACPMessage(
            intent="error",
            payload={"error": f"unknown_intent:{msg.intent}"},
            headers={**(msg.headers or {}), "x-routed-by": AGENT_ID},
            reply_to=msg.message_id,
            sender=AGENT_ID,
            receiver=msg.sender
        ).ensure_defaults()

    log_event("inbox_reply", reply.model_dump())
    return reply.model_dump()

