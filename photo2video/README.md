# Photo → Video AI

Turn any photo into a smooth video with cinematic motion.

## Features
- Ken Burns effect (fast, CPU-only)
- AI Depth Parallax using MiDaS (optional, better with GPU)
- Adjustable duration, FPS, bitrate, zoom/pan/parallax strength
- In-app preview and MP4 download

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the provided local URL in your browser. Upload a photo and click "Generate Video".

## Notes
- AI mode downloads the MiDaS model on first run via `torch.hub`.
- If MiDaS fails to load, the app automatically falls back to Ken Burns.
- Output is encoded with libx264; ensure ffmpeg is present (MoviePy will try to use an internal build if available).