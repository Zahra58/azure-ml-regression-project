import os
from pydantic import BaseModel


class Settings(BaseModel):
    replicate_api_token: str | None = os.getenv("REPLICATE_API_TOKEN")
    replicate_model_owner: str = os.getenv("REPLICATE_MODEL_OWNER", "stability-ai")
    replicate_model_name: str = os.getenv("REPLICATE_MODEL_NAME", "stable-video-diffusion")
    # Optional generation params
    default_fps: int = int(os.getenv("DEFAULT_FPS", "6"))
    default_duration_seconds: int = int(os.getenv("DEFAULT_DURATION_SECONDS", "4"))


settings = Settings()