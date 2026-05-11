"""Tests for GET /api/rm-workbench/mock-stream SSE endpoint."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from api import routes
from tests._pytest_port import BASE
from tests.test_rm_workbench_routes import _FakeHandler


def _read_sse_events(path: str) -> list[dict]:
    url = BASE + path
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read().decode("utf-8")
    events: list[dict] = []
    for line in body.splitlines():
        if not line.startswith("data: "):
            continue
        payload = line[len("data: "):]
        if payload == "[DONE]":
            continue
        events.append(json.loads(payload))
    return events


class TestRMWorkbenchMockStream:
    def test_returns_sse_content_type(self):
        url = BASE + "/api/rm-workbench/mock-stream"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            ct = r.headers.get("Content-Type", "")
            assert "text/event-stream" in ct

    def test_all_events_have_standard_agui_types(self):
        from api.rm_workbench.adapter import AG_UI_STANDARD_EVENT_TYPES

        events = _read_sse_events("/api/rm-workbench/mock-stream")
        assert len(events) > 0
        for event in events:
            assert event["type"] in AG_UI_STANDARD_EVENT_TYPES

    def test_contains_a2ui_surface_messages(self):
        events = _read_sse_events("/api/rm-workbench/mock-stream")
        surface_events = [
            e for e in events
            if e["type"] == "CUSTOM" and e.get("name") == "a2ui.surface.messages"
        ]
        assert len(surface_events) >= 1

    def test_contains_pending_interaction_created(self):
        events = _read_sse_events("/api/rm-workbench/mock-stream")
        pi_events = [
            e for e in events
            if e["type"] == "CUSTOM" and e.get("name") == "rm.pending_interaction.created"
        ]
        assert len(pi_events) >= 1

    def test_event_order_matches_adapter(self):
        from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture
        from api.rm_workbench.adapter import map_contract_to_agui_events

        expected = map_contract_to_agui_events(load_pre_meeting_brief_fixture())
        actual = _read_sse_events("/api/rm-workbench/mock-stream")
        assert len(actual) == len(expected)
        for a, e in zip(actual, expected):
            assert a["type"] == e["type"]
            if a["type"] == "CUSTOM":
                assert a.get("name") == e.get("name")

    def test_stream_surface_payloads_are_chinese_first_and_include_brief(self):
        events = _read_sse_events("/api/rm-workbench/mock-stream")
        surfaces = {
            event["value"]["surface"]: event["value"]["messages"][2]["updateDataModel"]["data"]
            for event in events
            if event["type"] == "CUSTOM" and event.get("name") == "a2ui.surface.messages"
        }

        assert surfaces["CustomerProfileCard"]["customer"]["name"] == "模拟客户"
        assert surfaces["CustomerProfileCard"]["memory_references"][1]["type"] == "关系"
        assert surfaces["ProductFitTable"]["product_candidates"][1]["asset_class"] == "多资产"
        assert surfaces["BriefExportPanel"]["brief"]["summary"].startswith("本次沟通重点关注")

    def test_stream_contains_generic_block_surfaces(self):
        events = _read_sse_events("/api/rm-workbench/mock-stream")
        generic_surfaces = {
            e["value"]["surface"]
            for e in events
            if e["type"] == "CUSTOM"
            and e.get("name") == "a2ui.surface.messages"
            and e["value"]["surface_id"].startswith("generic_")
        }
        assert generic_surfaces == {
            "MetricCard", "DataTable", "LineChart", "BarChart", "PieChart", "ChoiceList"
        }

    def test_generic_block_events_have_a2ui_message_structure(self):
        events = _read_sse_events("/api/rm-workbench/mock-stream")
        generic_events = [
            e for e in events
            if e["type"] == "CUSTOM"
            and e.get("name") == "a2ui.surface.messages"
            and e["value"]["surface_id"].startswith("generic_")
        ]
        assert len(generic_events) == 6
        for e in generic_events:
            messages = e["value"]["messages"]
            assert "createSurface" in messages[0]
            assert "updateComponents" in messages[1]
            assert "updateDataModel" in messages[2]

    def test_stream_ends_with_done_sentinel(self):
        url = BASE + "/api/rm-workbench/mock-stream"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8")
        assert "data: [DONE]" in body

    def test_mock_stream_requires_loopback(self):
        handler = _FakeHandler("203.0.113.10")
        parsed = urllib.parse.urlparse("/api/rm-workbench/mock-stream")

        routes.handle_get(handler, parsed)

        handler.wfile.seek(0)
        payload = json.loads(handler.wfile.read().decode("utf-8"))
        assert handler.status == 404
        assert payload == {"error": "not found"}
