from collections.abc import Iterator, Mapping
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from f1_pipeline.config import ApiSettings


class JolpicaClient:
    """Small HTTP client for Jolpica's Ergast-compatible Formula 1 API."""

    def __init__(self, settings: ApiSettings | None = None, session: requests.Session | None = None):
        self.settings = settings or ApiSettings()
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": self.settings.user_agent, "Accept": "application/json"})

        retry = Retry(
            total=self.settings.max_retries,
            connect=self.settings.max_retries,
            read=self.settings.max_retries,
            status=self.settings.max_retries,
            backoff_factor=self.settings.backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_json(self, path: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.settings.base_url.rstrip('/')}/{path.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.settings.timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        if "MRData" not in payload:
            raise ValueError(f"Unexpected Jolpica response for {path}: missing MRData")
        return payload

    def iter_pages(self, path: str, params: Mapping[str, Any] | None = None) -> Iterator[dict[str, Any]]:
        """Yield all pages for an Ergast-compatible endpoint."""
        offset = 0
        base_params = dict(params or {})

        while True:
            page_params = {**base_params, "limit": self.settings.page_size, "offset": offset}
            payload = self.get_json(path, params=page_params)
            yield payload

            metadata = payload["MRData"]
            total = int(metadata.get("total", 0))
            returned_limit = int(metadata.get("limit", self.settings.page_size))
            if returned_limit <= 0:
                raise ValueError("Jolpica returned a non-positive pagination limit")

            offset += returned_limit
            if offset >= total:
                break
