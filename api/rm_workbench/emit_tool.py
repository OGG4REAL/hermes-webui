"""Layer 0 emit_ui tool helper.

Extracts and validates contracts from the dedicated ``emit_ui`` tool call,
fills in optional metadata defaults, maps the contract to AG-UI events, and
returns a summary for the tool result.

Per ADR-011, ``kind`` / ``version`` / ``run_id`` / ``thread_id`` / ``skill``
are all optional in the Layer 0 envelope. Defaults are applied here so the
adapter can rely on these fields being present without forcing the model to
emit them.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from api.rm_workbench.adapter import map_contract_to_agui_events
from api.rm_workbench.contracts import validate_contract

logger = logging.getLogger(__name__)

EMIT_TOOL_NAME = "emit_ui"

# Layer 0 contract envelope schema version. Bump when the structural shape
# of ui.blocks / surfaces / pending_interactions changes in a way models
# must observe.
LAYER0_CONTRACT_VERSION = "0.1"


def extract_contract(tool_args: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(tool_args, dict):
        return None
    contract = tool_args.get("contract")
    if isinstance(contract, str):
        try:
            contract = json.loads(contract)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(contract, dict):
        return None
    return contract


def _fill_default_metadata(contract: dict[str, Any]) -> None:
    """Per ADR-011: kind/version/run_id/thread_id/skill are optional. Fill
    defaults in-place so downstream adapter code can rely on their presence.
    """
    contract.setdefault("kind", "ui")
    contract.setdefault("version", LAYER0_CONTRACT_VERSION)
    contract.setdefault("run_id", f"run-{uuid.uuid4().hex[:12]}")
    contract.setdefault("thread_id", f"thread-{uuid.uuid4().hex[:12]}")
    contract.setdefault("skill", "")


def process_emit_tool(
    tool_args: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate the contract and return ``(agui_events, tool_result_summary)``.

    Raises ``ValueError`` if the contract is missing or fails minimal Layer 0
    validation.
    """
    contract = extract_contract(tool_args)
    if contract is None:
        raise ValueError("emit_ui: missing contract in tool args")

    _fill_default_metadata(contract)
    validate_contract(contract)
    events = map_contract_to_agui_events(contract)

    pending_ids = [
        pi["id"]
        for pi in contract.get("pending_interactions", [])
        if isinstance(pi, dict) and "id" in pi
    ]
    memory_prop_ids = [
        mp["id"]
        for mp in contract.get("memory_proposals", [])
        if isinstance(mp, dict) and "id" in mp
    ]

    summary: dict[str, Any] = {
        "ok": True,
        "contract_id": f"rmc_{contract['run_id']}",
        "emitted_events": len(events),
        "pending_interactions": pending_ids,
        "memory_proposals": memory_prop_ids,
    }
    return events, summary
