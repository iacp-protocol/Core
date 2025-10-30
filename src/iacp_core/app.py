from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI(title="IACP Core (S0)", version="0.0.1")

class IACPMessage(BaseModel):
    message_id: str
    sender: str
    receiver: str
    intent: str
    payload: dict

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/iacp")
def iacp_endpoint(msg: IACPMessage):
    # S0: ping -> pong (echo minimal)
    if msg.intent.lower() == "ping":
        return {
            "message_id": str(uuid.uuid4()),
            "sender": msg.receiver,
            "receiver": msg.sender,
            "intent": "pong",
            "payload": {"received": True, **msg.payload},
        }
    return {"error": "unsupported_intent"}
