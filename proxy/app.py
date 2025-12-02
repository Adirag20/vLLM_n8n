import os
import httpx
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI(title="vLLM Proxy")

TARGET_HOST = os.environ.get("TARGET_HOST", "192.168.28.137")
TARGET_PORT = int(os.environ.get("TARGET_PORT", 11458))
TARGET_BASE = f"http://{TARGET_HOST}:{TARGET_PORT}"

PROXY_API_KEY = os.environ.get("PROXY_API_KEY")  # optional

@app.get("/")
async def root():
    return {"status": "proxy online", "forwarding_to": TARGET_BASE}

@app.post("/v1/generate")
async def proxy_generate(req: Request, authorization: Optional[str] = Header(None)):
    # optional API key protection
    if PROXY_API_KEY:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = authorization.split(" ", 1)[1]
        if token != PROXY_API_KEY:
            raise HTTPException(status_code=403, detail="Invalid API key")

    # Read incoming JSON body (works for any shape)
    try:
        body = await req.json()
    except Exception:
        # if no JSON body, treat it as empty dict
        body = {}

    forward_url = f"{TARGET_BASE}/v1/generate"

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(forward_url, json=body)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Upstream request failed: {str(e)}")

    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        except Exception:
            # fallback if upstream returns invalid json
            return JSONResponse(status_code=resp.status_code, content={"raw": resp.text})
    else:
        return JSONResponse(status_code=resp.status_code, content={"raw": resp.text})
