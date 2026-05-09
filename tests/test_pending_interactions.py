"""Tests for RM Workbench pending interaction state."""

from __future__ import annotations

import uuid

import pytest

try:
    from api.pending_interactions import (
        register_gateway_notify,
        unregister_gateway_notify,
        resolve_pending,
        clear_pending,
        get_pending,
        _gateway_queues,
        _gateway_notify_cbs,
        _lock,
        _PendingInteractionEntry,
        submit_pending,
    )
    PENDING_INTERACTIONS_AVAILABLE = True
except ImportError:
    PENDING_INTERACTIONS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PENDING_INTERACTIONS_AVAILABLE,
    reason="api.pending_interactions not available in this environment",
)


class TestPendingInteractionQueue:
    def test_resolve_pending_sets_event_and_structured_payload(self):
        sid = f"unit-pending-resolve-{uuid.uuid4().hex[:8]}"
        data = {"id": "pi-1", "action": "select_products", "session_id": sid}
        entry = _PendingInteractionEntry(data)
        payload = {"selected_product_ids": ["prod-1", "prod-2"]}
        with _lock:
            _gateway_queues.setdefault(sid, []).append(entry)

        resolved = resolve_pending(sid, payload, resolve_all=False)
        assert resolved == 1
        assert entry.event.is_set()
        assert entry.result == payload

    def test_register_and_submit_notify_callback(self):
        sid = f"unit-pending-notify-{uuid.uuid4().hex[:8]}"
        fired = []
        register_gateway_notify(sid, lambda d: fired.append(d))

        with _lock:
            cb = _gateway_notify_cbs.get(sid)
        assert cb is not None

        data = {"id": "pi-1", "action": "select_products", "session_id": sid}
        submit_pending(sid, data)
        assert fired == [data]

        unregister_gateway_notify(sid)

    def test_clear_pending_unblocks_waiters(self):
        sid = f"unit-pending-clear-{uuid.uuid4().hex[:8]}"
        entry = _PendingInteractionEntry({"id": "pi-1", "session_id": sid})
        with _lock:
            _gateway_queues.setdefault(sid, []).append(entry)

        cleared = clear_pending(sid)
        assert cleared == 1
        assert entry.event.is_set()
        with _lock:
            assert sid not in _gateway_queues

    def test_resolve_all_unblocks_multiple_entries(self):
        sid = f"unit-pending-resolve-all-{uuid.uuid4().hex[:8]}"
        entries = [
            _PendingInteractionEntry({"id": f"pi-{idx}", "session_id": sid})
            for idx in range(3)
        ]
        with _lock:
            _gateway_queues[sid] = list(entries)

        resolved = resolve_pending(
            sid,
            {"selected_product_ids": ["prod-1"]},
            resolve_all=True,
        )
        assert resolved == 3
        for entry in entries:
            assert entry.event.is_set()
            assert entry.result == {"selected_product_ids": ["prod-1"]}
        with _lock:
            assert sid not in _gateway_queues
        assert get_pending(sid) is None

    def test_get_pending_returns_oldest_entry(self):
        sid = f"unit-pending-order-{uuid.uuid4().hex[:8]}"
        first = {"id": "pi-1", "action": "select_products", "session_id": sid}
        second = {"id": "pi-2", "action": "select_products", "session_id": sid}

        first_entry = submit_pending(sid, first)
        second_entry = submit_pending(sid, second)

        assert get_pending(sid) == first

        resolved = resolve_pending(sid, {"selected_product_ids": ["prod-1"]})
        assert resolved == 1
        assert first_entry.event.is_set()
        assert first_entry.result == {"selected_product_ids": ["prod-1"]}
        assert not second_entry.event.is_set()
        assert get_pending(sid) == second

        clear_pending(sid)

    def test_unregister_gateway_notify_clears_queue_and_callback(self):
        sid = f"unit-pending-unregister-{uuid.uuid4().hex[:8]}"
        register_gateway_notify(sid, lambda d: None)
        entry = _PendingInteractionEntry({"id": "pi-1", "session_id": sid})
        with _lock:
            _gateway_queues.setdefault(sid, []).append(entry)

        unregister_gateway_notify(sid)

        assert entry.event.is_set()
        with _lock:
            assert sid not in _gateway_notify_cbs
            assert sid not in _gateway_queues
