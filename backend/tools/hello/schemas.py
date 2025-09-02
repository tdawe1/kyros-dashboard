from pydantic import BaseModel


class PingRequest(BaseModel):
    message: str = "Hello"


class PingResponse(BaseModel):
    message: str
    timestamp: str
    tool: str
    status: str


class InfoResponse(BaseModel):
    tool: str
    name: str
    description: str
    version: str
    features: list[str]
