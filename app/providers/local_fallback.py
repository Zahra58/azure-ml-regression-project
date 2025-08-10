from __future__ import annotations

from pathlib import Path
from typing import Tuple

import imageio
from PIL import Image
import numpy as np


def _center_crop_or_pad(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    tw, th = target_size
    iw, ih = img.size
    if iw == tw and ih == th:
        return img
    if iw >= tw and ih >= th:
        # Crop center
        left = (iw - tw) // 2
        top = (ih - th) // 2
        return img.crop((left, top, left + tw, top + th))
    # Pad on black background
    bg = Image.new("RGB", (tw, th), (0, 0, 0))
    left = (tw - iw) // 2
    top = (th - ih) // 2
    bg.paste(img, (left, top))
    return bg


def generate_zoom_video(
    image_path: str,
    output_path: str,
    duration_seconds: int = 4,
    fps: int = 6,
    zoom_factor: float = 1.15,
) -> str:
    img = Image.open(image_path).convert("RGB")
    base_w, base_h = img.size
    total_frames = max(int(duration_seconds * fps), 1)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(output_path, fps=fps, quality=8, codec="libx264")
    try:
        for i in range(total_frames):
            t = i / max(total_frames - 1, 1)
            scale = 1.0 + (zoom_factor - 1.0) * t
            sw, sh = max(1, int(base_w * scale)), max(1, int(base_h * scale))
            scaled = img.resize((sw, sh), resample=Image.BICUBIC)
            framed = _center_crop_or_pad(scaled, (base_w, base_h))
            frame = np.array(framed)
            writer.append_data(frame)
    finally:
        writer.close()
    return output_path