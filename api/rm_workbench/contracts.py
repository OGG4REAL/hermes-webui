"""Layer 0 contract validation for the structured UI subsystem.

Per ADR-010 and ADR-011, this validator only checks **minimal recognizability**
of the contract envelope:

- The contract must have non-empty ``ui.blocks`` or non-empty ``surfaces``
  (at least one path; both is fine).
- Each ``ui.blocks`` entry must have a non-empty string ``id``, a ``type`` that
  appears in :data:`ALLOWED_GENERIC_BLOCKS`, and a ``props`` object (may be empty).
- Each ``surfaces`` entry (transitional Layer 1 path) must have an ``id`` and
  ``props`` object. Surface name is *not* enforced here; the adapter falls
  back to a generic Card for unknown surface types.
- ``memory_proposals`` and ``pending_interactions`` only get structural sanity
  checks (must be arrays; proposals must have an ``id``).

Per-type strict checks (chart series.key matching data row keys, PieChart
labelKey/valueKey, DataTable columns, ChoiceList options non-empty, etc.) are
**deliberately removed**. Missing fields are tolerated; primitives in the
frontend render an empty state with a console warning. Business-level schema
strictness (e.g. RM requires customer/product_candidates) belongs in the
business Skill's own validator, not in this Layer 0 path (ADR-010).

``kind`` is *not* a routing gate. ``run_id`` / ``thread_id`` / ``skill`` /
``version`` are all optional metadata; ``emit_tool`` fills sensible defaults.
"""

from __future__ import annotations

from typing import Any

ALLOWED_GENERIC_BLOCKS = {
    "MetricCard",
    "DataTable",
    "LineChart",
    "BarChart",
    "PieChart",
    "ChoiceList",
}


def _validate_ui_blocks(blocks: list[Any]) -> None:
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("each ui.block must be an object")
        bid = block.get("id")
        if not isinstance(bid, str) or not bid:
            raise ValueError("each ui.block must have a non-empty string id")
        btype = block.get("type")
        if btype not in ALLOWED_GENERIC_BLOCKS:
            raise ValueError(f"unknown generic block type: {btype}")
        props = block.get("props")
        if not isinstance(props, dict):
            raise ValueError(f"ui.block '{bid}' must include props object")


def _validate_surfaces(surfaces: list[Any]) -> None:
    """Transitional Layer 1 path. Will be removed in Issue 9 once RM migrates
    to Skill-driven composition. We only check that each surface has a
    minimum identifiable shape; surface type names are not enforced.
    """
    for surface in surfaces:
        if not isinstance(surface, dict):
            raise ValueError("each surface must be an object")
        sid = surface.get("id")
        if not isinstance(sid, str) or not sid:
            raise ValueError("each surface must have a non-empty string id")
        if "surface" in surface and not isinstance(surface["surface"], str):
            raise ValueError(f"surface '{sid}' surface name must be a string")
        if not isinstance(surface.get("props"), dict):
            raise ValueError(f"surface '{sid}' must include props object")


def validate_contract(contract: dict[str, Any]) -> None:
    """Minimal Layer 0 envelope validation. See module docstring."""
    if not isinstance(contract, dict):
        raise ValueError("contract must be an object")

    ui = contract.get("ui")
    surfaces = contract.get("surfaces")

    has_blocks = (
        isinstance(ui, dict)
        and isinstance(ui.get("blocks"), list)
        and len(ui["blocks"]) > 0
    )
    has_surfaces = isinstance(surfaces, list) and len(surfaces) > 0

    if not has_blocks and not has_surfaces:
        raise ValueError("contract must have non-empty ui.blocks or surfaces")

    if ui is not None:
        if not isinstance(ui, dict):
            raise ValueError("ui must be an object")
        blocks = ui.get("blocks")
        if blocks is not None:
            if not isinstance(blocks, list):
                raise ValueError("ui.blocks must be an array")
            _validate_ui_blocks(blocks)

    if surfaces is not None:
        if not isinstance(surfaces, list):
            raise ValueError("surfaces must be an array")
        _validate_surfaces(surfaces)

    interactions = contract.get("pending_interactions")
    if interactions is not None and not isinstance(interactions, list):
        raise ValueError("pending_interactions must be an array")

    memory_proposals = contract.get("memory_proposals")
    if memory_proposals is not None:
        if not isinstance(memory_proposals, list):
            raise ValueError("memory_proposals must be an array")
        for mp in memory_proposals:
            if not isinstance(mp, dict):
                raise ValueError("each memory_proposal must be an object")
            if not isinstance(mp.get("id"), str):
                raise ValueError("memory_proposal.id is required")
