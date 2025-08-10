from typing import Optional, Tuple

import numpy as np
import torch
from PIL import Image, ImageFilter
from moviepy.editor import ImageClip


_MIDAS_MODEL = None
_MIDAS_TRANSFORM = None


def _hex_to_rgb_tuple(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(ch * 2 for ch in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def try_load_midas():
    global _MIDAS_MODEL, _MIDAS_TRANSFORM
    if _MIDAS_MODEL is not None:
        return _MIDAS_MODEL
    try:
        _MIDAS_MODEL = torch.hub.load('intel-isl/MiDaS', 'DPT_Hybrid')
        _MIDAS_MODEL.eval()
        _MIDAS_TRANSFORM = torch.hub.load('intel-isl/MiDaS', 'transforms').dpt_transform
        return _MIDAS_MODEL
    except Exception:
        _MIDAS_MODEL = None
        _MIDAS_TRANSFORM = None
        return None


def _estimate_depth(image: Image.Image, device: Optional[str] = None) -> np.ndarray:
    assert _MIDAS_MODEL is not None and _MIDAS_TRANSFORM is not None
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = _MIDAS_MODEL.to(device)

    input_batch = _MIDAS_TRANSFORM(image).to(device)
    with torch.no_grad():
        prediction = model(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=image.size[::-1],
            mode='bicubic',
            align_corners=False,
        ).squeeze()
    depth = prediction.cpu().numpy()
    depth = (depth - depth.min()) / max(depth.max() - depth.min(), 1e-6)
    return depth


def render_depth_parallax(
    image: Image.Image,
    duration: float,
    fps: int,
    parallax_strength: float = 0.5,
    edge_blur: float = 6.0,
    bg_color: str = "#000000",
    target_size: Tuple[int, int] = (1080, 1080),
    midas=None,
):
    if midas is not None:
        # ensure globals are set if passed in
        global _MIDAS_MODEL, _MIDAS_TRANSFORM
        _MIDAS_MODEL = midas
        if _MIDAS_TRANSFORM is None:
            try:
                _MIDAS_TRANSFORM = torch.hub.load('intel-isl/MiDaS', 'transforms').dpt_transform
            except Exception:
                pass

    width, height = target_size

    img_np = np.array(image.convert('RGB'))
    img_h, img_w = img_np.shape[:2]

    depth = _estimate_depth(Image.fromarray(img_np))

    # Normalize and create per-pixel offsets based on depth map
    max_offset = parallax_strength * 20.0

    bg_rgb = _hex_to_rgb_tuple(bg_color)

    def make_frame(t):
        progress = t / max(duration, 1e-6)
        # simple camera move: pan and slight zoom according to depth
        pan_x = (progress - 0.5) * 2.0  # -1 .. 1
        pan_y = (progress - 0.5) * 1.2

        # Compute pixel offsets: closer pixels move more in opposite direction
        offset_x = (0.5 - depth) * max_offset * pan_x
        offset_y = (0.5 - depth) * max_offset * pan_y

        grid_y, grid_x = np.mgrid[0:img_h, 0:img_w].astype(np.float32)
        map_x = np.clip(grid_x + offset_x, 0, img_w - 1)
        map_y = np.clip(grid_y + offset_y, 0, img_h - 1)

        # Bilinear sampling
        x0 = np.floor(map_x).astype(np.int32)
        x1 = np.clip(x0 + 1, 0, img_w - 1)
        y0 = np.floor(map_y).astype(np.int32)
        y1 = np.clip(y0 + 1, 0, img_h - 1)

        wa = (x1 - map_x) * (y1 - map_y)
        wb = (map_x - x0) * (y1 - map_y)
        wc = (x1 - map_x) * (map_y - y0)
        wd = (map_x - x0) * (map_y - y0)

        warped = (
            img_np[y0, x0] * wa[..., None]
            + img_np[y0, x1] * wb[..., None]
            + img_np[y1, x0] * wc[..., None]
            + img_np[y1, x1] * wd[..., None]
        )
        warped = warped.astype(np.uint8)

        # Resize/crop to target with letterboxing
        aspect_src = img_w / img_h
        aspect_dst = width / height
        if aspect_src > aspect_dst:
            new_w = width
            new_h = int(width / aspect_src)
        else:
            new_h = height
            new_w = int(height * aspect_src)
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:, :] = bg_rgb
        resized = np.array(Image.fromarray(warped).resize((new_w, new_h), Image.LANCZOS))
        y_off = (height - new_h) // 2
        x_off = (width - new_w) // 2
        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized

        if edge_blur > 0:
            canvas = np.array(Image.fromarray(canvas).filter(ImageFilter.GaussianBlur(radius=edge_blur)))
        return canvas

    clip = ImageClip(img_np).set_duration(duration)
    animated = clip.fl_image(lambda _: None).set_make_frame(make_frame)
    return animated.set_fps(fps)