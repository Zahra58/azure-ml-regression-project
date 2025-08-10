from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class ReplicateError(Exception):
    pass


class ReplicateClient:
    def __init__(self, api_token: Optional[str] = None) -> None:
        self.api_token = api_token or settings.replicate_api_token
        if not self.api_token:
            raise ReplicateError("REPLICATE_API_TOKEN not set")
        self._headers = {
            "Authorization": f"Bearer {self.api_token}",
        }
        self._base_url = "https://api.replicate.com/v1"

    async def _aget(self, path: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(f"{self._base_url}{path}", headers=self._headers)
            if resp.status_code >= 400:
                raise ReplicateError(f"GET {path} failed: {resp.status_code} {resp.text}")
            return resp.json()

    async def _apost(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=600) as client:
            resp = await client.post(
                f"{self._base_url}{path}", headers={**self._headers, "Content-Type": "application/json"}, json=json
            )
            if resp.status_code >= 400:
                raise ReplicateError(f"POST {path} failed: {resp.status_code} {resp.text}")
            return resp.json()

    async def _aupload_file_bytes(self, data: bytes, filename: str) -> str:
        # Upload raw bytes to Replicate Files API to get a temporary URL
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{self._base_url}/files",
                headers={**self._headers, "Content-Type": "application/octet-stream"},
                content=data,
            )
            if resp.status_code >= 400:
                raise ReplicateError(f"Upload failed: {resp.status_code} {resp.text}")
            payload = resp.json()
            url = payload.get("urls", {}).get("get") or payload.get("url")
            if not url:
                raise ReplicateError(f"Unexpected upload response: {payload}")
            return url

    async def aget_latest_version_id(self, owner: str, name: str) -> str:
        doc = await self._aget(f"/models/{owner}/{name}")
        latest = doc.get("latest_version") or {}
        version_id = latest.get("id")
        if not version_id:
            # Fallback to versions list
            versions = await self._aget(f"/models/{owner}/{name}/versions")
            items = versions.get("results", [])
            if not items:
                raise ReplicateError("No model versions found")
            version_id = items[0].get("id")
        return version_id

    async def acreate_prediction(
        self,
        image_bytes: bytes,
        filename: str,
        input_overrides: Optional[Dict[str, Any]] = None,
        owner: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        owner = owner or settings.replicate_model_owner
        name = name or settings.replicate_model_name
        version = await self.aget_latest_version_id(owner, name)
        image_url = await self._aupload_file_bytes(image_bytes, filename)
        # Only send minimal inputs to maximize compatibility
        inputs: Dict[str, Any] = {"image": image_url}
        if input_overrides:
            inputs.update({k: v for k, v in input_overrides.items() if v is not None})
        prediction = await self._apost("/predictions", json={"version": version, "input": inputs})
        # Poll until completed
        prediction_url = prediction.get("urls", {}).get("get")
        status = prediction.get("status")
        async with httpx.AsyncClient(timeout=600) as client:
            while status in {"starting", "processing", "queued"}:
                await asyncio.sleep(2)
                resp = await client.get(prediction_url, headers=self._headers)
                if resp.status_code >= 400:
                    raise ReplicateError(f"Polling failed: {resp.status_code} {resp.text}")
                prediction = resp.json()
                status = prediction.get("status")
        if status != "succeeded":
            raise ReplicateError(f"Prediction failed: {status} {prediction}")
        return prediction