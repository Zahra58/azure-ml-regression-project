from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.schemas import GenerationRequest, GenerationResponse
from app.providers.replicate_client import ReplicateClient, ReplicateError
from app.providers.local_fallback import generate_zoom_video

app = FastAPI(title="Image to Video Service", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerationResponse)
async def generate(
    file: UploadFile = File(...),
    provider: str = Form(default="auto"),
    prompt: Optional[str] = Form(default=None),
    fps: Optional[int] = Form(default=None),
    duration_seconds: Optional[int] = Form(default=None),
):
    try:
        file_bytes = await file.read()
        fname = file.filename or "image.png"
        selected_provider = provider
        if selected_provider == "auto":
            selected_provider = "replicate" if settings.replicate_api_token else "local"

        if selected_provider == "replicate":
            client = ReplicateClient()
            input_overrides = {}
            # Some I2V models may accept fps/duration; many ignore extra fields, so keep minimal
            prediction = await client.acreate_prediction(
                image_bytes=file_bytes,
                filename=fname,
                input_overrides=input_overrides,
            )
            output = prediction.get("output")
            if isinstance(output, str):
                urls = [output]
            elif isinstance(output, list):
                urls = [u for u in output if isinstance(u, str)]
            else:
                urls = None
            return GenerationResponse(status="succeeded", output_urls=urls, provider="replicate")

        elif selected_provider == "local":
            # Save and synthesize a simple pan/zoom video as a placeholder
            with tempfile.TemporaryDirectory() as td:
                in_path = Path(td) / (fname or "image.png")
                out_path = Path(td) / "output.mp4"
                with open(in_path, "wb") as f:
                    f.write(file_bytes)
                video_path = generate_zoom_video(
                    image_path=str(in_path),
                    output_path=str(out_path),
                    duration_seconds=duration_seconds or settings.default_duration_seconds,
                    fps=fps or settings.default_fps,
                )
                final_path = Path("outputs") / "latest.mp4"
                final_path.parent.mkdir(parents=True, exist_ok=True)
                Path(video_path).replace(final_path)
                return GenerationResponse(status="succeeded", download_url=str(final_path), provider="local")
        else:
            raise HTTPException(status_code=400, detail="Unknown provider")

    except ReplicateError as re:
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))