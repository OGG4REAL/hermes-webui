"""Mock data loader for RM Workbench V0 testing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_PATH = (
    _REPO_ROOT
    / "docs"
    / "ui-ux"
    / "rm-workbench-v0-spike"
    / "fixtures"
    / "rm-pre-meeting-brief.valid.json"
)


def load_pre_meeting_brief_fixture() -> dict[str, Any]:
    with _FIXTURE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("fixture must be a JSON object")
    return data
