"""RM Workbench V0 emit tool helper.

Extracts and validates contracts from the dedicated
``rm_workbench_emit_contract`` tool call, maps them to AG-UI events,
and returns a summary for the tool result.
"""

from __future__ import annotations

import logging
from typing import Any

from api.rm_workbench.adapter import map_rm_skill_contract_to_agui_events
from api.rm_workbench.contracts import validate_contract

logger = logging.getLogger(__name__)

EMIT_TOOL_NAME = "rm_workbench_emit_contract"


def extract_contract(tool_args: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(tool_args, dict):
        return None
    return tool_args.get("contract")


def process_emit_tool(
    tool_args: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate the contract and return (agui_events, tool_result_summary).

    Raises ``ValueError`` if the contract is missing or invalid.
    """
    contract = extract_contract(tool_args)
    if contract is None:
        raise ValueError("rm_workbench_emit_contract: missing contract in tool args")

    validate_contract(contract)
    events = map_rm_skill_contract_to_agui_events(contract)

    pending_ids = [pi["id"] for pi in contract.get("pending_interactions", [])]
    memory_prop_ids = [mp["id"] for mp in contract.get("memory_proposals", [])]

    summary: dict[str, Any] = {
        "ok": True,
        "contract_id": f"rmc_{contract.get('run_id', 'unknown')}",
        "emitted_events": len(events),
        "pending_interactions": pending_ids,
        "memory_proposals": memory_prop_ids,
    }
    return events, summary
