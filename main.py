from fastapi import FastAPI, Request
from collections import deque
from typing import List

app = FastAPI(
    title="Webhook Stream",
    description="A simple webhook stream service",
    version="0.1.0",
)
webhooks = deque(maxlen=50)


@app.post(
    "/webhook",
    summary="Receive a webhook",
    description="Receive a webhook and store it in memory",
)
async def receive_webhook(request: Request):
    data = await request.json()
    webhooks.append(data)
    return {"message": "Webhook received"}


@app.get(
    "/webhooks",
    summary="Get webhooks",
    description="Get the last 50 webhooks",
)
async def get_webhooks() -> List[dict]:
    return list(webhooks)


@app.get(
    "/health",
    summary="Health check",
    description="Health check endpoint",
)
async def health_check():
    return
