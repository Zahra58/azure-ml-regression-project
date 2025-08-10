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

## Deploy

### Docker (any VM or local)

```bash
# Build
docker build -t photo2video:latest /workspace/photo2video

# Run (mapped to localhost:8501)
docker run --rm -p 8501:8501 photo2video:latest
```

Then open `http://localhost:8501`.

### Hugging Face Spaces (Streamlit)

1. Push this folder as a public repo on GitHub
2. Create a new Space: Type = Streamlit, Repo = your repo
3. Ensure `requirements.txt` and `packages.txt` are present (we added ffmpeg)
4. Optional: enable GPU for faster AI depth mode

The Space will auto-build and serve the app.

### Render (Docker)

1. Push to GitHub
2. On Render, create a new Web Service from repo (Docker)
3. It will use the `Dockerfile` and `render.yaml`
4. Set PORT env var to 10000 or leave Dockerfile default 8501

### Other platforms
- Railway/Fly.io/DigitalOcean Apps: use the provided Dockerfile.
- K8s: build and push the image, then expose port 8501 via a Service/Ingress.