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

```
/workspace
├── app/
│   ├── azure_ml_client.py
│   └── streamlit_app.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## 🖥️ Web App (BikeCast)

A lightweight Streamlit app to interact with your Azure ML real-time endpoint and predict bike rental demand.

### Run locally

1. Python 3.11+
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (or use Streamlit secrets):
   ```bash
   cp .env.example .env
   # Edit .env to add your values
   export $(grep -v '^#' .env | xargs)
   ```
4. Start the app:
   ```bash
   streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
   ```
5. Open the URL printed by Streamlit (default `http://localhost:8501`).

### Configure

- Required: `AZURE_ML_ENDPOINT_URL`, `AZURE_ML_API_KEY`
- Optional: `AZURE_ML_DEPLOYMENT_NAME` if targeting a specific deployment

Use the sidebar to enter or override values at runtime.

### Deploy and share

- Docker:
  ```bash
  docker build -t bikecast .
  docker run -p 8501:8501 --env-file .env bikecast
  ```
- Azure App Service (Container): push the image to ACR and create a Web App for Containers.
- Streamlit Community Cloud: connect this repo, set secrets `AZURE_ML_ENDPOINT_URL`, `AZURE_ML_API_KEY`, `AZURE_ML_DEPLOYMENT_NAME`.
- Render/Heroku/Fly.io: use the Dockerfile or install Python and run the Streamlit command.

### Notes on request schema

By default, the app builds a payload like:
```json
{
  "input_data": {
    "columns": ["date", "hour", "season", "weather", "is_holiday", "is_weekend"],
    "data": [["2024-01-01", 9, "winter", "clear", 0, 0]]
  }
}
```
If your endpoint expects a different schema, switch to Raw JSON mode in the app or edit the payload in the expander before sending.

### 🔗 Swagger URI

The endpoint's Swagger (if enabled) is listed above. You can consult it to confirm the exact input schema.
