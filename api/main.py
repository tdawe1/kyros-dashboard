from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime

app = FastAPI(title="Kyros Repurposer API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class GenerateRequest(BaseModel):
    input_text: str
    channels: List[str] = ["linkedin", "twitter"]
    tone: str = "professional"
    preset: str = "default"


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    variants: Dict[str, List[Dict[str, Any]]]
    token_usage: Dict[str, int]


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


# Mock data
mock_jobs = [
    {
        "id": "1",
        "client": "TechCorp Inc.",
        "words": 1250,
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z",
        "source_url": "https://techcorp.com/blog/ai-trends",
    },
    {
        "id": "2",
        "client": "StartupXYZ",
        "words": 890,
        "status": "processing",
        "created_at": "2024-01-15T09:15:00Z",
        "source_url": "https://startupxyz.com/news/product-launch",
    },
    {
        "id": "3",
        "client": "Enterprise Ltd.",
        "words": 2100,
        "status": "pending",
        "created_at": "2024-01-15T08:45:00Z",
        "source_url": "https://enterprise.com/insights/market-analysis",
    },
]

mock_presets = [
    {
        "id": "1",
        "name": "Default",
        "description": "Standard repurposing settings",
        "config": {"tone": "professional", "length": "medium"},
    },
    {
        "id": "2",
        "name": "Marketing",
        "description": "Marketing-focused content",
        "config": {"tone": "engaging", "length": "short"},
    },
    {
        "id": "3",
        "name": "Technical",
        "description": "Technical documentation style",
        "config": {"tone": "formal", "length": "long"},
    },
]


# Routes
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/kpis")
async def get_kpis():
    return {
        "jobs_processed": 12,
        "hours_saved": 24.5,
        "avg_edit_min": 18,
        "export_bundles": 9,
    }


@app.get("/api/jobs")
async def get_jobs():
    return mock_jobs


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = next((job for job in mock_jobs if job["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    if len(request.input_text) < 100:
        raise HTTPException(
            status_code=400, detail="Input text must be at least 100 characters"
        )

    job_id = str(uuid.uuid4())

    # Mock variants based on channels
    variants = {}
    for channel in request.channels:
        if channel == "linkedin":
            variants[channel] = [
                {
                    "id": f"{job_id}_linkedin_1",
                    "text": f"LinkedIn post 1: {request.input_text[:100]}...",
                    "length": 150,
                    "readability": "Good",
                    "tone": request.tone,
                },
                {
                    "id": f"{job_id}_linkedin_2",
                    "text": f"LinkedIn post 2: {request.input_text[50:150]}...",
                    "length": 200,
                    "readability": "Excellent",
                    "tone": request.tone,
                },
            ]
        elif channel == "twitter":
            variants[channel] = [
                {
                    "id": f"{job_id}_twitter_1",
                    "text": f"Twitter thread 1: {request.input_text[:50]}...",
                    "length": 280,
                    "readability": "Good",
                    "tone": request.tone,
                }
            ]
        elif channel == "newsletter":
            variants[channel] = [
                {
                    "id": f"{job_id}_newsletter_1",
                    "text": f"Newsletter section: {request.input_text[:200]}...",
                    "length": 500,
                    "readability": "Excellent",
                    "tone": request.tone,
                }
            ]
        elif channel == "blog":
            variants[channel] = [
                {
                    "id": f"{job_id}_blog_1",
                    "text": f"Blog post: {request.input_text[:300]}...",
                    "length": 800,
                    "readability": "Good",
                    "tone": request.tone,
                }
            ]

    return GenerateResponse(
        job_id=job_id,
        status="completed",
        variants=variants,
        token_usage={"input_tokens": 150, "output_tokens": 300, "total_cost": 0.05},
    )


@app.post("/api/export", response_model=ExportResponse)
async def export_content(request: ExportRequest):
    # Mock export - in real implementation, this would generate actual files
    filename = f"export_{request.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}"
    file_url = f"/downloads/{filename}"

    return ExportResponse(file_url=file_url, filename=filename)


@app.get("/api/presets")
async def get_presets():
    return mock_presets


@app.post("/api/presets")
async def create_preset(request: PresetRequest):
    new_preset = {
        "id": str(uuid.uuid4()),
        "name": request.name,
        "description": request.description,
        "config": request.config,
    }
    mock_presets.append(new_preset)
    return new_preset


@app.get("/api/presets/{preset_id}")
async def get_preset(preset_id: str):
    preset = next(
        (preset for preset in mock_presets if preset["id"] == preset_id), None
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@app.put("/api/presets/{preset_id}")
async def update_preset(preset_id: str, request: PresetRequest):
    preset = next(
        (preset for preset in mock_presets if preset["id"] == preset_id), None
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    preset["name"] = request.name
    preset["description"] = request.description
    preset["config"] = request.config

    return preset


@app.delete("/api/presets/{preset_id}")
async def delete_preset(preset_id: str):
    global mock_presets
    mock_presets = [preset for preset in mock_presets if preset["id"] != preset_id]
    return {"message": "Preset deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
