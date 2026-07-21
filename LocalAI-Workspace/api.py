"""
Web API server for the Local AI Workspace.
Run with: uvicorn api:app --reload
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.logger import get_logger
from core.orchestrator import Orchestrator
from registry.tool_registry import ToolRegistry

log = get_logger("api")

# Global instances
registry: ToolRegistry | None = None
orchestrator: Orchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global registry, orchestrator
    
    # Initialize registry and orchestrator on startup
    registry = ToolRegistry()
    await registry.__aenter__()
    
    if not registry.list_tools():
        log.warning("No tools connected on startup.")
        
    orchestrator = Orchestrator(registry)
    log.info("API server is ready and connected to MCP tools.")
    
    yield  # Server runs here
    
    # Clean up on shutdown
    log.info("Shutting down API server...")
    if registry:
        await registry.__aexit__(None, None, None)


app = FastAPI(title="Local AI Workspace API", lifespan=lifespan)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator is not initialized.")
    
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    try:
        log.info(f"Received query: {req.message}")
        answer = await orchestrator.run(req.message)
        return ChatResponse(reply=answer)
    except Exception as e:
        log.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools")
async def get_tools():
    if not registry:
        return {"tools": []}
    # list_tools returns ToolSpec objects, we need to convert them to dicts for JSON
    tools = [{"server": t.server, "name": t.name, "description": t.description} for t in registry.list_tools()]
    return {"tools": tools}


# Mount the frontend directory at the root URL
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)
    
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
