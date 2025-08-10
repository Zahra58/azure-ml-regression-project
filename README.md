# 🚲 Azure ML Regression Project: Bike Rental Demand Prediction

This project demonstrates how to build, train, and deploy a **regression model** using **Microsoft Azure Machine Learning Studio** to predict the number of bikes rented based on various features like **date, time, weather, and season**.

## 🎯 Project Objective

To develop and deploy a machine learning model that predicts the **number of bike rentals** at different times of the day based on temporal and environmental factors.

## 🧠 What the Model Does

Given input features such as:
- Hour of the day
- Date
- Weather conditions
- Season
- Holiday/weekend status

The model predicts:
- Expected number of bikes to be rented

## 🚀 Deployment on Azure

- Platform: Azure Machine Learning Studio
- Endpoint Type: Real-time
- Provisioning: ✅ Succeeded
- Authentication: Key-based access
- Status: Live and working

### 🔗 Swagger URI
https://myproject1-rajsy.australiaeast.inference.ml.azure.com/swagger.json

## 📷 Screenshot


## 🧰 Tools & Technologies

- Python
- Azure Machine Learning Studio
- Scikit-learn / Pandas / Matplotlib
- Jupyter Notebooks
- GitHub

## 📂 Repo Structure

---

# Image → Video Service

A minimal FastAPI service and CLI to generate a short video from a single image.

- Provider "replicate": uses Replicate's API to run Stable Video Diffusion (configurable)
- Provider "local": fallback that creates a simple Ken-Burns-style zoom using MoviePy (works without GPU)

## Quickstart

1) Python env

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Run local fallback (no API keys or GPU needed)

```bash
python -m app.cli path/to/image.jpg --provider local --output outputs/demo.mp4
```

3) Start API server

```bash
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000/docs and use POST /generate.

## Replicate setup (optional, for higher quality)

- Create a token and export environment variable:

```bash
export REPLICATE_API_TOKEN=your_token_here
```

- Optionally override model owner/name:

```bash
export REPLICATE_MODEL_OWNER=stability-ai
export REPLICATE_MODEL_NAME=stable-video-diffusion
```

The service resolves the latest model version dynamically.

## Docker

```bash
docker build -t image2video:latest .
docker run -p 8000:8000 -e REPLICATE_API_TOKEN=$REPLICATE_API_TOKEN image2video:latest
```
