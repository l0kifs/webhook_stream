import json
from dataclasses import dataclass
from collections import deque
from typing import List
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.params import Query

app = FastAPI(
    title="Webhook Stream",
    description="A simple webhook stream service",
    version="0.1.0",
)
webhooks = deque(maxlen=50)


@dataclass
class Webhook:
    id: str
    method: str
    url: str
    headers: dict
    body: dict


def format_request_curl(
        method: str,
        url: str,
        params: dict = None,
        headers: dict = None,
        data: dict = None,
):
    """Format request to curl command.

    Example:
        curl -X POST -H "Content-Type: application/json" -d '{"key": "value"}' http://example.com

    Args:
        method (str): HTTP method
        url (str): URL
        params (dict, optional): URL parameters. Defaults to None.
        headers (dict, optional): Headers. Defaults to None.
        data (dict, optional): Data. Defaults to None.

    Returns:
        str: curl command
    """
    curl_command = f"curl -X {method}"
    if headers:
        curl_command = curl_command + ' -H ' + ' -H '.join([f'\'{k}: {v}\'' for k, v in headers.items()])
    if data:
        json_data = json.dumps(data, separators=(',', ':'))
        curl_command = curl_command + f" -d \'{json_data}\'"
    curl_command = curl_command + f" {url}"
    if params:
        params_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        curl_command += f'?{params_string}'
    return curl_command


@app.api_route(
    "/webhook",
    methods=["POST"],
    summary="Receive a webhook",
    description="Receive a webhook and store it in memory",
)
async def receive_webhook(request: Request):
    webhook_id = str(uuid4())
    webhook = Webhook(
        id=webhook_id,
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        body=await request.json()
    )
    webhooks.append(webhook)
    return {"message": "Webhook received"}


@app.get(
    "/webhooks",
    summary="Get webhooks",
    description="Get the last 50 webhooks",
)
async def get_webhooks() -> List[dict]:
    return [webhook.__dict__ for webhook in webhooks]


@app.get(
    "/webhooks/{webhook_id}",
    summary="Get a webhook",
    description="Get a specific webhook",
)
async def get_webhook(
    webhook_id: str,
    format: str = Query("json", enum=["json", "curl"], description="Response format")
):
    for webhook in webhooks:
        if webhook.id == webhook_id:
            if format == "curl":
                curl_string = format_request_curl(
                    method=webhook.method,
                    url=webhook.url,
                    headers=webhook.headers,
                    data=webhook.body,
                )
                return PlainTextResponse(content=curl_string)
            return webhook.__dict__
    return {"message": "Webhook not found"}


@app.api_route(
    "/health",
    methods=["GET", "HEAD"],
    summary="Health check",
    description="Health check endpoint",
)
async def health_check():
    return
