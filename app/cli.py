from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import httpx

from app.config import settings
from app.providers.local_fallback import generate_zoom_video
from app.providers.replicate_client import ReplicateClient


async def run_replicate(image_path: str) -> None:
    client = ReplicateClient()
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    prediction = await client.acreate_prediction(image_bytes=image_bytes, filename=Path(image_path).name)
    output = prediction.get("output")
    print("status=succeeded provider=replicate output=", output)


def run_local(image_path: str, output: str) -> None:
    generate_zoom_video(image_path=image_path, output_path=output)
    print(f"status=succeeded provider=local output={output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Image to Video CLI")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("--output", default="outputs/cli_output.mp4")
    parser.add_argument("--provider", choices=["replicate", "local", "auto"], default="auto")
    args = parser.parse_args()

    provider = args.provider
    if provider == "auto":
        provider = "replicate" if settings.replicate_api_token else "local"

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    if provider == "replicate":
        asyncio.run(run_replicate(args.image))
    else:
        run_local(args.image, args.output)


if __name__ == "__main__":
    main()