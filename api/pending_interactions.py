"""Structured pending interaction state for the RM Workbench backend."""

from __future__ import annotations

import threading
from typing import Optional


_lock = threading.Lock()
_pending: dict[str, dict] = {}
_gateway_queues: dict[str, list] = {}
_gateway_notify_cbs: dict[str, object] = {}


class _PendingInteractionEntry:
    """One pending interaction request inside a session."""

    __slots__ = ("event", "data", "result")

    def __init__(self, data: dict):
        self.event = threading.Event()
        self.data = data
        self.result: Optional[dict] = None


def register_gateway_notify(session_key: str, cb) -> None:
    """Register a per-session callback for sending pending interactions to the UI."""
    with _lock:
        _gateway_notify_cbs[session_key] = cb


def _clear_queue_locked(session_key: str) -> list[_PendingInteractionEntry]:
    entries = _gateway_queues.pop(session_key, [])
    _pending.pop(session_key, None)
    return entries


def unregister_gateway_notify(session_key: str) -> None:
    """Unregister the callback and unblock any waiting pending interactions."""
    with _lock:
        _gateway_notify_cbs.pop(session_key, None)
        entries = _clear_queue_locked(session_key)
    for entry in entries:
        entry.event.set()


def clear_pending(session_key: str) -> int:
    """Clear pending interactions without removing the registered callback."""
    with _lock:
        entries = _clear_queue_locked(session_key)
    for entry in entries:
        entry.event.set()
    return len(entries)


def submit_pending(session_key: str, data: dict) -> _PendingInteractionEntry:
    """Queue a pending interaction and notify the UI callback if registered."""
    entry = _PendingInteractionEntry(dict(data))
    with _lock:
        queue = _gateway_queues.setdefault(session_key, [])
        queue.append(entry)
        _pending[session_key] = queue[0].data
        cb = _gateway_notify_cbs.get(session_key)
    if cb:
        try:
            cb(dict(entry.data))
        except Exception:
            pass
    return entry


def get_pending(session_key: str) -> dict | None:
    """Return the oldest pending interaction for this session, if any."""
    with _lock:
        queue = _gateway_queues.get(session_key) or []
        if queue:
            return dict(queue[0].data)
        pending = _pending.get(session_key)
        return dict(pending) if pending else None


def resolve_pending(
    session_key: str,
    payload: dict,
    resolve_all: bool = False,
    interaction_id: str | None = None,
) -> int:
    """Resolve pending interaction(s) for a session.

    When *interaction_id* is given, only the entry whose ``data["id"]``
    matches is resolved.  Otherwise falls back to oldest-first (legacy).
    """
    resolved_payload = dict(payload)
    with _lock:
        queue = _gateway_queues.get(session_key)
        if not queue:
            _pending.pop(session_key, None)
            return 0
        if resolve_all:
            entries = _clear_queue_locked(session_key)
        elif interaction_id is not None:
            idx = None
            for i, e in enumerate(queue):
                if e.data.get("id") == interaction_id:
                    idx = i
                    break
            if idx is None:
                return 0
            entries = [queue.pop(idx)]
            if queue:
                _pending[session_key] = queue[0].data
            else:
                _clear_queue_locked(session_key)
        else:
            entries = [queue.pop(0)]
            if queue:
                _pending[session_key] = queue[0].data
            else:
                _clear_queue_locked(session_key)
    count = 0
    for entry in entries:
        entry.result = dict(resolved_payload)
        entry.event.set()
        count += 1
    return count


DEFAULT_BLOCKING_TIMEOUT = 300


def blocking_wait(
    entry: _PendingInteractionEntry,
    cancel_event: "threading.Event | None" = None,
    timeout: float | None = None,
) -> dict | None:
    """Block until the entry is resolved, cancelled, or timed out.

    Returns the resolved payload dict, or ``None`` on timeout/cancel.
    """
    deadline_seconds = timeout if timeout is not None else DEFAULT_BLOCKING_TIMEOUT
    import time

    deadline = time.monotonic() + deadline_seconds
    while True:
        if cancel_event is not None and cancel_event.is_set():
            return None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        if entry.event.wait(timeout=min(1.0, remaining)):
            return entry.result
