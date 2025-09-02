from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class GenerateRequest(BaseModel):
    input_text: str
    channels: List[str] = ["linkedin", "twitter"]
    tone: str = "professional"
    preset: str = "default"
    user_id: str = "anonymous"  # Default for demo purposes
    model: Optional[str] = None  # Optional model parameter


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    variants: Dict[str, List[Dict[str, Any]]]
    token_usage: Dict[str, int]
    model: str
    api_mode: str


class ExportRequest(BaseModel):
    job_id: str
    format: str = "csv"
    selected_variants: List[str] = []


class ExportResponse(BaseModel):
    file_url: str
    filename: str


class PresetRequest(BaseModel):
    name: str
    description: str
    config: Dict[str, Any]


class PresetResponse(BaseModel):
    id: str
    name: str
    description: str
    config: Dict[str, Any]
