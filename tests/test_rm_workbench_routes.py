"""Tests for RM Workbench pending interaction routes."""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid

from api import routes
from tests._pytest_port import BASE


def get(path):
    url = BASE + path
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


def post(path, body=None):
    url = BASE + path
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


class _FakeHandler:
    def __init__(self, client_ip: str):
        self.client_address = (client_ip, 12345)
        self.headers = {}
        self.wfile = io.BytesIO()
        self.status = None

    def send_response(self, status):
        self.status = status

    def send_header(self, _name, _value):
        return None

    def end_headers(self):
        return None


class TestRMWorkbenchPendingEndpoints:
    def test_pending_requires_session_id(self):
        result, status = get("/api/rm-workbench/pending")
        assert status == 400
        assert "session_id" in result["error"]

    def test_resolve_requires_session_id(self):
        result, status = post(
            "/api/rm-workbench/pending/resolve",
            {"payload": {"selected_product_ids": ["prod-1"]}},
        )
        assert status == 400
        assert "session_id" in result["error"]

    def test_resolve_requires_object_payload(self):
        sid = f"rm-route-payload-{uuid.uuid4().hex[:8]}"
        result, status = post(
            "/api/rm-workbench/pending/resolve",
            {"session_id": sid, "payload": ["prod-1"]},
        )
        assert status == 400
        assert "payload" in result["error"]

    def test_inject_creates_pending_and_resolve_clears_it(self):
        sid = f"rm-route-pending-{uuid.uuid4().hex[:8]}"
        inject, inject_status = get(
            f"/api/rm-workbench/inject_test?session_id={urllib.parse.quote(sid)}"
        )
        assert inject_status == 200
        assert inject["ok"] is True

        data, status = get(f"/api/rm-workbench/pending?session_id={urllib.parse.quote(sid)}")
        assert status == 200
        assert data["pending"] is not None
        assert data["pending"]["session_id"] == sid
        assert data["pending"]["kind"] == "pending_interaction"

        interaction_id = data["pending"]["id"]

        result, resolve_status = post(
            "/api/rm-workbench/pending/resolve",
            {
                "session_id": sid,
                "interaction_id": interaction_id,
                "payload": {"selected_product_ids": ["prod-1", "prod-2"]},
            },
        )
        assert resolve_status == 200
        assert result == {"ok": True, "resolved": 1}

        data2, status2 = get(f"/api/rm-workbench/pending?session_id={urllib.parse.quote(sid)}")
        assert status2 == 200
        assert data2["pending"] is None

    def test_inject_requires_loopback(self):
        handler = _FakeHandler("203.0.113.10")
        parsed = urllib.parse.urlparse("/api/rm-workbench/inject_test?session_id=test-session")

        routes.handle_get(handler, parsed)

        handler.wfile.seek(0)
        payload = json.loads(handler.wfile.read().decode("utf-8"))
        assert handler.status == 404
        assert payload == {"error": "not found"}
