from fastapi import FastAPI, Request
from collections import deque
from typing import List

app = FastAPI()
webhooks = deque(maxlen=50)


@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    webhooks.append(data)
    return {"message": "Webhook received"}


@app.get("/webhooks")
async def get_webhooks() -> List[dict]:
    return list(webhooks)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
