import os
import sys
from pathlib import Path

# Ensure project root is on sys.path when running from tools/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image
from engine.kenburns import render_ken_burns
from engine.depth_parallax import render_depth_parallax, try_load_midas


def main():
    img_path = os.environ.get("IMG", str(ROOT / "sample.jpg"))
    assert os.path.exists(img_path), f"Image not found: {img_path}"

    image = Image.open(img_path).convert("RGB")

    # Ken Burns
    kb = render_ken_burns(
        image=image,
        duration=3.0,
        fps=24,
        zoom_strength=1.15,
        pan_x=0.12,
        pan_y=0.0,
        bg_color="#000000",
        target_size=(1080, int(1080 * image.height / image.width)),
    )
    kb.write_videofile("out_kenburns.mp4", fps=24, codec="libx264", bitrate="4M", audio=False)

    # Depth Parallax (if MiDaS loads)
    midas = try_load_midas()
    if midas is not None:
        dp = render_depth_parallax(
            image=image,
            duration=3.0,
            fps=24,
            parallax_strength=0.45,
            edge_blur=4.0,
            bg_color="#000000",
            target_size=(1080, int(1080 * image.height / image.width)),
            midas=midas,
        )
        dp.write_videofile("out_depth.mp4", fps=24, codec="libx264", bitrate="4M", audio=False)
        print("Depth parallax: OK")
    else:
        print("MiDaS not available; skipped depth mode")

    print("Ken Burns: OK")


if __name__ == "__main__":
    main()