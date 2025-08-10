import json
from typing import Any, Dict, Optional

import requests


class AzureMLEndpointError(Exception):
    """Raised when the Azure ML endpoint returns a non-successful response."""


def invoke_endpoint(
    *,
    endpoint_url: str,
    api_key: str,
    payload: Dict[str, Any],
    deployment_name: Optional[str] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """
    Invoke an Azure ML real-time endpoint using key-based authentication.

    Parameters
    ----------
    endpoint_url: str
        The endpoint scoring URL.
    api_key: str
        The primary/secondary key for the endpoint.
    payload: Dict[str, Any]
        The JSON payload to send to the endpoint.
    deployment_name: Optional[str]
        Optional specific deployment name to target (header: azureml-model-deployment).
    timeout_seconds: int
        HTTP timeout in seconds.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the endpoint.
    """
    if not endpoint_url:
        raise ValueError("endpoint_url is required")
    if not api_key:
        raise ValueError("api_key is required")

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if deployment_name:
        headers["azureml-model-deployment"] = deployment_name

    try:
        response = requests.post(
            endpoint_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=timeout_seconds,
        )
    except requests.RequestException as request_error:
        raise AzureMLEndpointError(f"Failed to call endpoint: {request_error}") from request_error

    if not response.ok:
        # Attempt to include response text for easier diagnosis
        message = (
            f"Endpoint returned {response.status_code}: "
            f"{response.text.strip() if response.text else 'No body'}"
        )
        raise AzureMLEndpointError(message)

    try:
        return response.json()
    except ValueError as parse_error:
        # Not JSON; return raw text wrapped in a dict for visibility
        return {"raw_text": response.text}