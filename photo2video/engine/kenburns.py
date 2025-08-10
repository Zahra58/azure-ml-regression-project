from typing import Tuple

import numpy as np
from PIL import Image
from moviepy.editor import ImageClip


def _hex_to_rgb_tuple(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    if lv == 3:
        hex_color = ''.join(ch * 2 for ch in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def render_ken_burns(
    image: Image.Image,
    duration: float,
    fps: int,
    zoom_strength: float = 1.2,
    pan_x: float = 0.1,
    pan_y: float = 0.0,
    bg_color: str = "#000000",
    target_size: Tuple[int, int] = (1080, 1080),
):
    width, height = target_size
    rgb = _hex_to_rgb_tuple(bg_color)

    img_np = np.array(image)
    img_h, img_w = img_np.shape[:2]

    clip = ImageClip(img_np).set_duration(duration)

    def make_frame(t):
        progress = t / max(duration, 1e-6)
        scale = 1.0 + (zoom_strength - 1.0) * progress

        pan_offset_x = pan_x * (img_w * 0.2) * progress
        pan_offset_y = pan_y * (img_h * 0.2) * progress

        scaled_w = int(img_w * scale)
        scaled_h = int(img_h * scale)

        scaled = np.array(Image.fromarray(img_np).resize((scaled_w, scaled_h), Image.LANCZOS))

        cx = scaled_w // 2 + int(pan_offset_x)
        cy = scaled_h // 2 + int(pan_offset_y)

        left = max(0, cx - width // 2)
        top = max(0, cy - height // 2)
        right = min(scaled_w, left + width)
        bottom = min(scaled_h, top + height)

        if right - left < width or bottom - top < height:
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            canvas[:, :] = rgb
            crop = scaled[top:bottom, left:right]
            y_off = (height - crop.shape[0]) // 2
            x_off = (width - crop.shape[1]) // 2
            canvas[y_off:y_off+crop.shape[0], x_off:x_off+crop.shape[1]] = crop
            return canvas
        else:
            return scaled[top:bottom, left:right]

    animated = clip.fl_image(lambda _: None).set_make_frame(make_frame)
    return animated.set_fps(fps)