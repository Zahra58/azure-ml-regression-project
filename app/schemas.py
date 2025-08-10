from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List


class GenerationRequest(BaseModel):
    prompt: Optional[str] = Field(default=None, description="Optional text prompt, ignored by some models")
    fps: Optional[int] = None
    duration_seconds: Optional[int] = None


class GenerationResponse(BaseModel):
    status: str
    output_urls: Optional[List[str]] = None
    download_url: Optional[str] = None
    provider: str