import json
import os
from datetime import date
from typing import Any, Dict, List

import streamlit as st

from app.azure_ml_client import AzureMLEndpointError, invoke_endpoint


APP_NAME = "BikeCast"
APP_EMOJI = "🚲"


def get_secret(name: str, default: str = "") -> str:
    # Prefer Streamlit secrets, then environment variables, then default
    if name in st.secrets:
        value = st.secrets[name]
        if isinstance(value, str):
            return value
    return os.environ.get(name, default)


def build_default_payload(columns: List[str], row_values: List[Any]) -> Dict[str, Any]:
    return {
        "input_data": {
            "columns": columns,
            "data": [row_values],
        }
    }


def main() -> None:
    st.set_page_config(page_title=f"{APP_NAME} | Azure ML", page_icon=APP_EMOJI)
    st.title(f"{APP_EMOJI} {APP_NAME}")
    st.caption("Bike rental demand prediction via your Azure ML real-time endpoint")

    with st.sidebar:
        st.header("Endpoint Settings")
        endpoint_url = st.text_input(
            label="Endpoint URL",
            value=get_secret("AZURE_ML_ENDPOINT_URL", ""),
            help="Your Azure ML real-time endpoint scoring URL",
            placeholder="https://<endpoint>.<region>.inference.ml.azure.com/score",
        )
        api_key = st.text_input(
            label="API Key",
            value=get_secret("AZURE_ML_API_KEY", ""),
            help="Primary/secondary key for the endpoint",
            type="password",
        )
        deployment_name = st.text_input(
            label="Deployment Name (optional)",
            value=get_secret("AZURE_ML_DEPLOYMENT_NAME", ""),
            help="Only set if your endpoint has multiple deployments",
        )
        st.divider()
        st.markdown(
            "You can set these via environment variables or Streamlit secrets: "
            "`AZURE_ML_ENDPOINT_URL`, `AZURE_ML_API_KEY`, `AZURE_ML_DEPLOYMENT_NAME`"
        )

    st.subheader("Input")
    input_mode = st.radio(
        "Choose input mode",
        options=["Guided form", "Raw JSON"],
        horizontal=True,
    )

    response_container = st.container()

    if input_mode == "Guided form":
        st.markdown("Customize and submit a single prediction request")

        col1, col2, col3 = st.columns(3)
        with col1:
            ride_date: date = st.date_input("Date", value=date.today())
            hour_of_day: int = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=12)
        with col2:
            season: str = st.selectbox("Season", ["spring", "summer", "fall", "winter"])  # adjust mapping as needed
            weather: str = st.selectbox("Weather", ["clear", "cloudy", "light_rain", "heavy_rain"])  # example
        with col3:
            is_holiday: bool = st.checkbox("Holiday", value=False)
            is_weekend: bool = st.checkbox("Weekend", value=False)

        # NOTE: Adjust to match your model's expected feature order and types
        feature_columns = [
            "date",
            "hour",
            "season",
            "weather",
            "is_holiday",
            "is_weekend",
        ]
        feature_values = [
            ride_date.isoformat(),
            int(hour_of_day),
            season,
            weather,
            int(is_holiday),
            int(is_weekend),
        ]

        payload = build_default_payload(feature_columns, feature_values)

        with st.expander("Show payload (edit before sending if needed)", expanded=False):
            payload_str = st.text_area(
                label="Request JSON",
                value=json.dumps(payload, indent=2),
                height=220,
            )
            # If the user modifies the JSON, respect their changes
            try:
                payload = json.loads(payload_str)
            except Exception:
                st.warning("Invalid JSON in the payload editor; using the generated payload instead.")

        submit = st.button("Predict", type="primary")

        if submit:
            if not endpoint_url or not api_key:
                st.error("Please provide both Endpoint URL and API Key in the sidebar.")
            else:
                with st.spinner("Calling endpoint..."):
                    try:
                        result = invoke_endpoint(
                            endpoint_url=endpoint_url,
                            api_key=api_key,
                            payload=payload,
                            deployment_name=deployment_name or None,
                        )
                        with response_container:
                            st.success("Success")
                            st.json(result)
                    except AzureMLEndpointError as e:
                        with response_container:
                            st.error(str(e))
    else:
        st.markdown("Paste the exact JSON your endpoint expects")
        default_raw = json.dumps(
            {
                "input_data": {
                    "columns": ["date", "hour", "season", "weather", "is_holiday", "is_weekend"],
                    "data": [["2024-01-01", 9, "winter", "clear", 0, 0]],
                }
            },
            indent=2,
        )
        raw_json = st.text_area("Request JSON", value=default_raw, height=260)
        submit = st.button("Predict", type="primary")
        if submit:
            try:
                payload = json.loads(raw_json)
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
                return

            if not endpoint_url or not api_key:
                st.error("Please provide both Endpoint URL and API Key in the sidebar.")
            else:
                with st.spinner("Calling endpoint..."):
                    try:
                        result = invoke_endpoint(
                            endpoint_url=endpoint_url,
                            api_key=api_key,
                            payload=payload,
                            deployment_name=deployment_name or None,
                        )
                        with response_container:
                            st.success("Success")
                            st.json(result)
                    except AzureMLEndpointError as e:
                        with response_container:
                            st.error(str(e))

    st.divider()
    st.caption(
        "Tip: If your endpoint expects a different schema, switch to Raw JSON mode or adjust the payload in the expander."
    )


if __name__ == "__main__":
    main()