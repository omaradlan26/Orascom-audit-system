import os
from typing import Any

import requests


DEFAULT_API_URL = "http://127.0.0.1:8000"


class ApiClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("AUDIT_API_URL") or DEFAULT_API_URL).rstrip("/")

    def _headers(self, token: str | None = None) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        if response.ok:
            if response.status_code == 204:
                return None
            return response.json()
        try:
            payload = response.json()
            message = payload.get("detail", response.text)
        except ValueError:
            message = response.text
        raise RuntimeError(message)

    def guest_login(self) -> dict[str, Any]:
        response = requests.post(f"{self.base_url}/auth/guest", timeout=10)
        return self._handle_response(response)

    def admin_login(self, username: str, password: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        return self._handle_response(response)

    def logout(self, token: str) -> None:
        response = requests.post(
            f"{self.base_url}/auth/logout",
            headers=self._headers(token),
            timeout=10,
        )
        self._handle_response(response)

    def get_summary(self, token: str) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/audits/summary", headers=self._headers(token), timeout=10)
        return self._handle_response(response)

    def get_filter_options(self, token: str) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/audits/filters", headers=self._headers(token), timeout=10)
        return self._handle_response(response)

    def list_audits(self, token: str, filters: dict[str, str]) -> list[dict[str, Any]]:
        active_filters = {key: value for key, value in filters.items() if value and value != "All"}
        response = requests.get(
            f"{self.base_url}/audits",
            headers=self._headers(token),
            params=active_filters,
            timeout=10,
        )
        return self._handle_response(response)

    def create_audit(self, token: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/audits",
            headers=self._headers(token),
            json=payload,
            timeout=10,
        )
        return self._handle_response(response)

    def update_audit(self, token: str, audit_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/audits/{audit_id}",
            headers=self._headers(token),
            json=payload,
            timeout=10,
        )
        return self._handle_response(response)

    def delete_audit(self, token: str, audit_id: int) -> None:
        response = requests.delete(
            f"{self.base_url}/audits/{audit_id}",
            headers=self._headers(token),
            timeout=10,
        )
        self._handle_response(response)
