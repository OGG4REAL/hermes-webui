"""Static host checks for RM Workbench frontend embedding (MYM-38)."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_INDEX = REPO_ROOT / "static" / "index.html"
STATIC_MESSAGES = REPO_ROOT / "static" / "messages.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_index_contains_rm_workbench_island_mount_and_bundle():
    html = _read(STATIC_INDEX)

    assert 'id="rmWorkbenchIslandRoot"' in html
    assert "rm-workbench-island.js" in html


def test_messages_listener_preserves_rm_workbench_protocol_and_buffers_pre_mount_events():
    js = _read(STATIC_MESSAGES)

    assert "source.addEventListener('rm_workbench'" in js
    assert "d.kind==='agui_events'&&Array.isArray(d.events)" in js
    assert "__rmWorkbenchEventQueue" in js
    assert "__rmWorkbenchEvent(e.data)" in js
