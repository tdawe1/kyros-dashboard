from fastapi import APIRouter
from datetime import datetime
from .schemas import PingRequest, PingResponse, InfoResponse

router = APIRouter()


@router.post("/ping", response_model=PingResponse)
async def ping(request: PingRequest):
    """
    Simple ping endpoint that echoes back a message.
    """
    return PingResponse(
        message=f"Hello! You said: {request.message}",
        timestamp=datetime.now().isoformat(),
        tool="hello",
        status="success",
    )


@router.get("/ping", response_model=PingResponse)
async def ping_get():
    """
    Simple GET ping endpoint.
    """
    return PingResponse(
        message="Hello from the Hello World tool!",
        timestamp=datetime.now().isoformat(),
        tool="hello",
        status="success",
    )


@router.get("/info", response_model=InfoResponse)
async def get_info():
    """
    Get information about the Hello World tool.
    """
    return InfoResponse(
        tool="hello",
        name="Hello World",
        description="A simple demonstration tool that shows the modular architecture",
        version="1.0.0",
        features=[
            "Simple ping/pong functionality",
            "Demonstrates tool isolation",
            "Shows dynamic tool loading",
            "Example of minimal tool implementation",
        ],
    )


@router.get("/config")
async def get_config():
    """
    Get Hello World tool configuration.
    """
    return {
        "tool": "hello",
        "name": "Hello World",
        "description": "A simple demonstration tool",
        "version": "1.0.0",
        "endpoints": {
            "ping": "/api/tools/hello/ping",
            "info": "/api/tools/hello/info",
            "config": "/api/tools/hello/config",
        },
        "features": {
            "ping": "Echo back messages",
            "info": "Get tool information",
            "config": "Get tool configuration",
        },
    }
