import os
import sys
from datetime import date, timedelta

import requests


API_URL = os.getenv("AUDIT_API_URL", "http://127.0.0.1:8000").rstrip("/")


def assert_status(response: requests.Response, expected: int) -> None:
    if response.status_code != expected:
        raise AssertionError(f"Expected {expected}, got {response.status_code}: {response.text}")


def main() -> int:
    health = requests.get(f"{API_URL}/health", timeout=10)
    assert_status(health, 200)

    guest = requests.post(f"{API_URL}/auth/guest", timeout=10).json()
    guest_token = guest["token"]

    guest_list = requests.get(f"{API_URL}/audits", headers={"Authorization": f"Bearer {guest_token}"}, timeout=10)
    assert_status(guest_list, 200)

    guest_create = requests.post(
        f"{API_URL}/audits",
        headers={"Authorization": f"Bearer {guest_token}"},
        json={
            "title": "Guest should not create",
            "department": "IT",
            "observation": "N/A",
            "risk": "Low",
            "grade": "A",
            "action": "N/A",
            "owner": "N/A",
            "due_date": date.today().isoformat(),
            "status": "Open",
        },
        timeout=10,
    )
    assert_status(guest_create, 403)

    admin_username = os.getenv("AUDIT_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("AUDIT_ADMIN_PASSWORD", "admin123")
    admin = requests.post(
        f"{API_URL}/auth/login",
        json={"username": admin_username, "password": admin_password},
        timeout=10,
    )
    assert_status(admin, 200)
    admin_token = admin.json()["token"]

    created = requests.post(
        f"{API_URL}/audits",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Smoke test audit",
            "department": "Finance",
            "observation": "Created by automated smoke test.",
            "risk": "Medium",
            "grade": "B",
            "action": "Verify CRUD works end-to-end.",
            "owner": "Test Owner",
            "due_date": (date.today() + timedelta(days=3)).isoformat(),
            "status": "Open",
        },
        timeout=10,
    )
    assert_status(created, 201)
    audit = created.json()
    audit_id = audit["id"]

    updated = requests.put(
        f"{API_URL}/audits/{audit_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            **{k: audit[k] for k in ["title", "department", "observation", "risk", "grade", "action", "owner", "due_date", "status"]},
            "status": "Closed",
        },
        timeout=10,
    )
    assert_status(updated, 200)
    if updated.json()["status"] != "Closed":
        raise AssertionError("Update did not apply")

    deleted = requests.delete(
        f"{API_URL}/audits/{audit_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10,
    )
    assert_status(deleted, 204)

    print("smoke-test-ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

