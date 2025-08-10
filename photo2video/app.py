import os
import io
import tempfile
from typing import Tuple

import streamlit as st
from PIL import Image

from engine.kenburns import render_ken_burns
from engine.depth_parallax import render_depth_parallax, try_load_midas


def save_bytesio_to_tempfile(buf: io.BytesIO, suffix: str = "") -> str:
    buf.seek(0)
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(buf.read())
    return path


st.set_page_config(page_title="Photo → Video AI", page_icon="🎬", layout="wide")
st.title("Photo → Video AI")
st.caption("Turn any photo into a smooth video with cinematic motion.")

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Engine", ["Ken Burns (Fast)", "AI Depth Parallax (MiDaS)"])
    duration = st.slider("Duration (seconds)", 2.0, 12.0, 5.0, 0.5)
    fps = st.slider("FPS", 12, 60, 24)
    bitrate = st.selectbox("Bitrate", ["2M", "4M", "8M", "12M"], index=1)
    bg_color = st.color_picker("Letterbox color", "#000000")

    if mode.startswith("Ken Burns"):
        kb_zoom = st.slider("Zoom strength", 1.0, 1.6, 1.2, 0.01)
        kb_pan_x = st.slider("Pan X (left→right)", -1.0, 1.0, 0.15, 0.01)
        kb_pan_y = st.slider("Pan Y (top→bottom)", -1.0, 1.0, 0.0, 0.01)
    else:
        dp_intensity = st.slider("Parallax strength", 0.0, 1.0, 0.45, 0.01)
        dp_blur = st.slider("Edge smoothing", 0.0, 15.0, 6.0, 0.1)

uploaded = st.file_uploader("Upload a photo (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=False)

col1, col2 = st.columns([1, 1])

with col1:
    if uploaded is not None:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Input Photo", use_container_width=True)
    else:
        st.info("Upload an image to get started.")
        image = None

with col2:
    placeholder = st.empty()

run = st.button("Generate Video", type="primary", use_container_width=True, disabled=(image is None))

if run and image is not None:
    try:
        with st.spinner("Rendering video..."):
            width = 1080
            aspect = image.width / image.height
            height = int(width / aspect)

            if mode.startswith("Ken Burns"):
                clip = render_ken_burns(image=image, duration=duration, fps=fps, zoom_strength=kb_zoom, pan_x=kb_pan_x, pan_y=kb_pan_y, bg_color=bg_color, target_size=(width, height))
            else:
                midas = try_load_midas()
                if midas is None:
                    st.warning("MiDaS model could not be loaded. Falling back to Ken Burns.")
                    clip = render_ken_burns(image=image, duration=duration, fps=fps, zoom_strength=1.15, pan_x=0.12, pan_y=0.0, bg_color=bg_color, target_size=(width, height))
                else:
                    clip = render_depth_parallax(image=image, duration=duration, fps=fps, parallax_strength=dp_intensity, edge_blur=dp_blur, bg_color=bg_color, target_size=(width, height), midas=midas)

            buf = io.BytesIO()
            temp_mp4 = tempfile.mktemp(suffix=".mp4")
            clip.write_videofile(temp_mp4, fps=fps, codec="libx264", bitrate=bitrate, audio=False)
            with open(temp_mp4, "rb") as f:
                buf.write(f.read())
            os.remove(temp_mp4)

            placeholder.video(buf.getvalue())
            st.download_button("Download MP4", data=buf.getvalue(), file_name="photo2video.mp4", mime="video/mp4", use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render: {e}")