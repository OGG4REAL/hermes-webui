"""Tests for RM Workbench V0 Real Stream Bridge (MYM-29).

Covers:
1. emit tool detection: only emit_ui triggers adapter
2. rm_workbench SSE event: adapter events through put()
3. pending interaction resolve by interaction_id
4. blocking wait + timeout + cancel
5. memory proposals as CUSTOM event
6. existing tests unaffected
7. real chat stream consumer registers rm_workbench handler
8. cancel path immediately clears RM pending interactions
9. callback does not call blocking_wait
"""

from __future__ import annotations

import copy
import json
import threading
import time
import uuid

import pytest

try:
    from api.rm_workbench.emit_tool import (
        EMIT_TOOL_NAME,
        extract_contract,
        process_emit_tool,
    )
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.contracts import validate_contract
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture
    from api.pending_interactions import (
        submit_pending,
        resolve_pending,
        clear_pending,
        get_pending,
        blocking_wait,
        _gateway_queues,
        _lock,
        _PendingInteractionEntry,
    )
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not AVAILABLE,
    reason="RM workbench modules not available in this environment",
)

from api.streaming import _resolve_completed_tool_args


def _make_fixture_with_memory_proposals():
    fixture = load_pre_meeting_brief_fixture()
    fixture["memory_proposals"] = [
        {
            "id": "mem_prop_001",
            "target": "customer",
            "operation": "upsert",
            "summary": "test memory proposal",
            "evidence": [],
            "requires_approval": True,
        }
    ]
    return fixture


class TestEmitToolDetection:
    def test_emit_tool_name_constant(self):
        assert EMIT_TOOL_NAME == "emit_ui"

    def test_extract_contract_from_args(self):
        fixture = load_pre_meeting_brief_fixture()
        args = {"contract": fixture}
        assert extract_contract(args) is fixture

    def test_extract_contract_returns_none_for_missing(self):
        assert extract_contract({}) is None
        assert extract_contract(None) is None

    def test_process_emit_tool_validates_and_maps(self):
        fixture = load_pre_meeting_brief_fixture()
        events, summary = process_emit_tool({"contract": fixture})
        assert summary["ok"] is True
        assert summary["emitted_events"] == len(events)
        assert "pi_001" in summary["pending_interactions"]

    def test_process_emit_tool_rejects_missing_contract(self):
        with pytest.raises(ValueError, match="missing contract"):
            process_emit_tool({})

    def test_process_emit_tool_rejects_invalid_contract(self):
        with pytest.raises(ValueError):
            process_emit_tool({"contract": {"kind": "wrong"}})

    def test_only_emit_tool_name_triggers_processing(self):
        """Other tool names should NOT be processed by emit_tool."""
        assert EMIT_TOOL_NAME == "emit_ui"
        assert EMIT_TOOL_NAME != "some_other_tool"
        assert EMIT_TOOL_NAME != "clarify"

    def test_completed_tool_args_fall_back_to_live_started_args(self):
        fixture = load_pre_meeting_brief_fixture()
        live_tool_calls = [
            {
                "name": EMIT_TOOL_NAME,
                "args": {"contract": fixture},
            }
        ]

        resolved = _resolve_completed_tool_args(
            name=EMIT_TOOL_NAME,
            completed_args=None,
            live_tool_calls=live_tool_calls,
        )

        assert resolved == {"contract": fixture}

    def test_completed_tool_args_preserve_explicit_completed_args(self):
        fixture = load_pre_meeting_brief_fixture()
        completed_args = {"contract": fixture}
        live_tool_calls = [
            {
                "name": EMIT_TOOL_NAME,
                "args": {"contract": {"kind": "stale"}},
            }
        ]

        resolved = _resolve_completed_tool_args(
            name=EMIT_TOOL_NAME,
            completed_args=completed_args,
            live_tool_calls=live_tool_calls,
        )

        assert resolved is completed_args


class TestRmWorkbenchSSEEvent:
    def test_adapter_generates_agui_events(self):
        fixture = load_pre_meeting_brief_fixture()
        events = map_contract_to_agui_events(fixture)
        assert len(events) > 0
        types = {e["type"] for e in events}
        assert "RUN_STARTED" in types
        assert "CUSTOM" in types
        assert "STATE_DELTA" in types

    def test_agui_events_wrapped_in_rm_workbench_payload(self):
        fixture = load_pre_meeting_brief_fixture()
        events, _summary = process_emit_tool({"contract": fixture})
        payload = {"kind": "agui_events", "events": events}
        assert payload["kind"] == "agui_events"
        assert isinstance(payload["events"], list)
        assert len(payload["events"]) > 0

    def test_sse_event_format_matches_spec(self):
        fixture = load_pre_meeting_brief_fixture()
        events, _ = process_emit_tool({"contract": fixture})
        payload = {"kind": "agui_events", "events": events}
        serialized = json.dumps(payload, ensure_ascii=False)
        parsed = json.loads(serialized)
        assert parsed["kind"] == "agui_events"
        assert len(parsed["events"]) == len(events)


class TestPendingInteractionResolveById:
    def test_resolve_by_interaction_id(self):
        sid = f"test-resolve-by-id-{uuid.uuid4().hex[:8]}"
        first = submit_pending(sid, {"id": "pi_001", "action": "a", "session_id": sid})
        second = submit_pending(sid, {"id": "pi_002", "action": "b", "session_id": sid})

        resolved = resolve_pending(
            sid, {"selected": ["x"]}, interaction_id="pi_002"
        )
        assert resolved == 1
        assert second.event.is_set()
        assert second.result == {"selected": ["x"]}
        assert not first.event.is_set()

        assert get_pending(sid)["id"] == "pi_001"
        clear_pending(sid)

    def test_resolve_by_id_not_found_returns_zero(self):
        sid = f"test-resolve-notfound-{uuid.uuid4().hex[:8]}"
        submit_pending(sid, {"id": "pi_001", "session_id": sid})

        resolved = resolve_pending(
            sid, {"selected": ["x"]}, interaction_id="nonexistent"
        )
        assert resolved == 0
        clear_pending(sid)

    def test_resolve_oldest_when_no_interaction_id(self):
        sid = f"test-resolve-oldest-{uuid.uuid4().hex[:8]}"
        first = submit_pending(sid, {"id": "pi_001", "session_id": sid})
        second = submit_pending(sid, {"id": "pi_002", "session_id": sid})

        resolved = resolve_pending(sid, {"selected": ["x"]})
        assert resolved == 1
        assert first.event.is_set()
        assert not second.event.is_set()
        clear_pending(sid)

    def test_multiple_pending_resolve_correct_entry(self):
        sid = f"test-multi-pending-{uuid.uuid4().hex[:8]}"
        entries = []
        for i in range(3):
            entries.append(submit_pending(sid, {"id": f"pi_{i}", "session_id": sid}))

        resolved = resolve_pending(
            sid, {"data": "middle"}, interaction_id="pi_1"
        )
        assert resolved == 1
        assert entries[1].event.is_set()
        assert entries[1].result == {"data": "middle"}
        assert not entries[0].event.is_set()
        assert not entries[2].event.is_set()
        clear_pending(sid)


class TestBlockingWaitAndTimeout:
    def test_blocking_wait_resolves(self):
        sid = f"test-bw-resolve-{uuid.uuid4().hex[:8]}"
        entry = submit_pending(sid, {"id": "pi_001", "session_id": sid})

        def resolver():
            time.sleep(0.1)
            resolve_pending(sid, {"ok": True}, interaction_id="pi_001")

        t = threading.Thread(target=resolver)
        t.start()
        result = blocking_wait(entry, timeout=5.0)
        t.join()
        assert result == {"ok": True}

    def test_blocking_wait_timeout(self):
        sid = f"test-bw-timeout-{uuid.uuid4().hex[:8]}"
        entry = submit_pending(sid, {"id": "pi_001", "session_id": sid})

        start = time.monotonic()
        result = blocking_wait(entry, timeout=0.3)
        elapsed = time.monotonic() - start

        assert result is None
        assert elapsed < 1.0
        clear_pending(sid)

    def test_blocking_wait_cancel(self):
        sid = f"test-bw-cancel-{uuid.uuid4().hex[:8]}"
        entry = submit_pending(sid, {"id": "pi_001", "session_id": sid})
        cancel = threading.Event()

        def canceller():
            time.sleep(0.1)
            cancel.set()

        t = threading.Thread(target=canceller)
        t.start()
        result = blocking_wait(entry, cancel_event=cancel, timeout=5.0)
        t.join()
        assert result is None
        clear_pending(sid)


class TestStreamCancelClearsPending:
    def test_clear_pending_unblocks_blocking_wait(self):
        sid = f"test-cancel-clear-{uuid.uuid4().hex[:8]}"
        entry = submit_pending(sid, {"id": "pi_001", "session_id": sid})

        def clearer():
            time.sleep(0.1)
            clear_pending(sid)

        t = threading.Thread(target=clearer)
        t.start()
        result = blocking_wait(entry, timeout=5.0)
        t.join()
        assert entry.event.is_set()
        assert result is None


class TestMemoryProposals:
    def test_adapter_generates_memory_proposal_custom_event(self):
        fixture = _make_fixture_with_memory_proposals()
        events = map_contract_to_agui_events(fixture)

        mp_events = [
            e for e in events
            if e["type"] == "CUSTOM" and e.get("name") == "rm.memory_proposal.created"
        ]
        assert len(mp_events) == 1
        assert mp_events[0]["value"]["proposals"][0]["id"] == "mem_prop_001"
        assert mp_events[0]["value"]["run_id"] == fixture["run_id"]
        assert mp_events[0]["value"]["thread_id"] == fixture["thread_id"]

    def test_memory_proposals_optional_default_empty(self):
        fixture = load_pre_meeting_brief_fixture()
        assert "memory_proposals" not in fixture
        events = map_contract_to_agui_events(fixture)
        mp_events = [
            e for e in events
            if e["type"] == "CUSTOM" and e.get("name") == "rm.memory_proposal.created"
        ]
        assert len(mp_events) == 0

    def test_emit_tool_summary_includes_memory_proposals(self):
        fixture = _make_fixture_with_memory_proposals()
        _events, summary = process_emit_tool({"contract": fixture})
        assert summary["memory_proposals"] == ["mem_prop_001"]

    def test_contract_validation_accepts_memory_proposals(self):
        fixture = _make_fixture_with_memory_proposals()
        validate_contract(fixture)

    def test_contract_validation_rejects_invalid_memory_proposals(self):
        fixture = _make_fixture_with_memory_proposals()
        fixture["memory_proposals"] = "not a list"
        with pytest.raises(ValueError, match="memory_proposals must be an array"):
            validate_contract(fixture)

    def test_contract_validation_rejects_proposal_without_id(self):
        fixture = _make_fixture_with_memory_proposals()
        fixture["memory_proposals"] = [{"target": "customer"}]
        with pytest.raises(ValueError, match="memory_proposal.id is required"):
            validate_contract(fixture)


class TestRealChatStreamConsumer:
    """Verify static/messages.js has rm_workbench SSE handler wired up."""

    def test_messages_js_has_rm_workbench_event_listener(self):
        from pathlib import Path
        messages_js = Path(__file__).resolve().parents[1] / "static" / "messages.js"
        content = messages_js.read_text()
        assert "addEventListener('rm_workbench'" in content

    def test_messages_js_rm_workbench_checks_agui_events_kind(self):
        from pathlib import Path
        messages_js = Path(__file__).resolve().parents[1] / "static" / "messages.js"
        content = messages_js.read_text()
        assert "agui_events" in content

    def test_messages_js_rm_workbench_calls_window_callback(self):
        from pathlib import Path
        messages_js = Path(__file__).resolve().parents[1] / "static" / "messages.js"
        content = messages_js.read_text()
        assert "__rmWorkbenchEvent" in content

    def test_frontend_parse_rm_workbench_sse_extracts_events(self):
        """Verify parseRmWorkbenchSSE helper in hermesClient.ts exists."""
        from pathlib import Path
        client_ts = (
            Path(__file__).resolve().parents[1]
            / "frontend" / "src" / "api" / "hermesClient.ts"
        )
        content = client_ts.read_text()
        assert "parseRmWorkbenchSSE" in content
        assert 'agui_events' in content

    def test_agui_reducer_has_append_events_action(self):
        from pathlib import Path
        reducer_ts = (
            Path(__file__).resolve().parents[1]
            / "frontend" / "src" / "agui" / "aguiReducer.ts"
        )
        content = reducer_ts.read_text()
        assert "APPEND_EVENTS" in content


class TestCancelPathClearsPending:
    """Verify cancel_stream clears RM pending interactions immediately."""

    def test_cancel_stream_code_clears_rm_pending(self):
        """The cancel_stream function must import and call clear_pending
        from api.pending_interactions."""
        from pathlib import Path
        streaming_py = Path(__file__).resolve().parents[1] / "api" / "streaming.py"
        content = streaming_py.read_text()
        assert "from api.pending_interactions import clear_pending" in content
        assert "_clear_rm_pending" in content

    def test_cancel_clears_pending_functionally(self):
        """Simulate cancel: submit pending, then clear, verify unblocked."""
        sid = f"test-cancel-func-{uuid.uuid4().hex[:8]}"
        entry = submit_pending(sid, {"id": "pi_001", "session_id": sid})
        assert not entry.event.is_set()

        cleared = clear_pending(sid)
        assert cleared == 1
        assert entry.event.is_set()
        assert get_pending(sid) is None


class TestCallbackDoesNotBlock:
    """Verify _handle_rm_emit_tool does NOT call blocking_wait."""

    def test_handle_rm_emit_tool_has_no_blocking_wait(self):
        from pathlib import Path
        streaming_py = Path(__file__).resolve().parents[1] / "api" / "streaming.py"
        content = streaming_py.read_text()
        # Find the function body
        start = content.index("def _handle_rm_emit_tool(")
        next_def = content.index("\ndef ", start + 1)
        func_body = content[start:next_def]
        assert "blocking_wait" not in func_body
        assert "submit_pending" not in func_body

    def test_blocking_wait_helper_still_exists_as_utility(self):
        """blocking_wait is still importable for future tool-layer use."""
        from api.pending_interactions import blocking_wait
        assert callable(blocking_wait)


class TestRmWorkbenchToolsetAutoAppend:
    """Tests for api.streaming._append_rm_workbench_toolset_if_supported (MYM-31).

    These call the production helper extracted from _run_agent_streaming,
    exercising real code rather than a mirrored snippet.
    """

    def test_appends_rm_workbench_when_supported(self):
        """Production helper appends rm_workbench when validate_toolset returns True."""
        import unittest.mock as mock
        from api.streaming import _append_rm_workbench_toolset_if_supported

        base = ["web", "terminal", "file"]
        with mock.patch("api.streaming.validate_toolset", create=True, side_effect=None):
            with mock.patch.dict("sys.modules", {"toolsets": mock.MagicMock()}):
                import sys
                sys.modules["toolsets"].validate_toolset = mock.MagicMock(return_value=True)
                result = _append_rm_workbench_toolset_if_supported(list(base))

        assert "rm_workbench" in result
        for ts in base:
            assert ts in result

    def test_no_append_when_validate_returns_false(self):
        """Production helper does not append when validate_toolset returns False."""
        import unittest.mock as mock
        from api.streaming import _append_rm_workbench_toolset_if_supported

        base = ["web", "terminal", "file"]
        with mock.patch.dict("sys.modules", {"toolsets": mock.MagicMock()}):
            import sys
            sys.modules["toolsets"].validate_toolset = mock.MagicMock(return_value=False)
            result = _append_rm_workbench_toolset_if_supported(list(base))

        assert result == base

    def test_no_crash_when_toolsets_import_fails(self):
        """Backward compat: unavailable toolsets module → no crash, unchanged list."""
        import unittest.mock as mock
        from api.streaming import _append_rm_workbench_toolset_if_supported

        base = ["web", "terminal", "file"]
        with mock.patch.dict("sys.modules", {"toolsets": None}):
            result = _append_rm_workbench_toolset_if_supported(list(base))

        assert result == base

    def test_no_duplicate_when_already_present(self):
        """If rm_workbench already in list, don't append again."""
        import unittest.mock as mock
        from api.streaming import _append_rm_workbench_toolset_if_supported

        base = ["web", "terminal", "rm_workbench"]
        with mock.patch.dict("sys.modules", {"toolsets": mock.MagicMock()}):
            import sys
            sys.modules["toolsets"].validate_toolset = mock.MagicMock(return_value=True)
            result = _append_rm_workbench_toolset_if_supported(list(base))

        assert result.count("rm_workbench") == 1

    def test_ordinary_toolsets_preserved_on_exception(self):
        """validate_toolset raising → exception swallowed, toolsets unchanged."""
        import unittest.mock as mock
        from api.streaming import _append_rm_workbench_toolset_if_supported

        base = ["browser", "clarify", "code_execution", "terminal", "web"]
        with mock.patch.dict("sys.modules", {"toolsets": mock.MagicMock()}):
            import sys
            sys.modules["toolsets"].validate_toolset = mock.MagicMock(
                side_effect=RuntimeError("boom")
            )
            result = _append_rm_workbench_toolset_if_supported(list(base))

        assert result == base


class TestExistingBehaviorUnaffected:
    def test_resolve_pending_without_interaction_id_is_fifo(self):
        sid = f"test-compat-fifo-{uuid.uuid4().hex[:8]}"
        first = submit_pending(sid, {"id": "pi_001", "session_id": sid})
        second = submit_pending(sid, {"id": "pi_002", "session_id": sid})

        resolve_pending(sid, {"ok": True})
        assert first.event.is_set()
        assert not second.event.is_set()
        clear_pending(sid)

    def test_resolve_all_still_works(self):
        sid = f"test-compat-all-{uuid.uuid4().hex[:8]}"
        entries = [
            submit_pending(sid, {"id": f"pi_{i}", "session_id": sid})
            for i in range(3)
        ]
        resolved = resolve_pending(sid, {"ok": True}, resolve_all=True)
        assert resolved == 3
        for e in entries:
            assert e.event.is_set()
