"""Layer 0 adapter: maps structured UI contracts to AG-UI events.

Per ADR-009/010/011:

- The Layer 0 path (``ui.blocks`` → generic primitives) does **not** access
  any business-specific contract fields.
- The Layer 1 transitional path (``surfaces`` → RM semantic surfaces) is
  marked transitional and will be removed in the Skill-driven Layer 1
  migration issue (ADR-013). Until then, ``map_rm_surface_to_a2ui_messages``
  uses ``.get(...)`` so missing RM fields don't raise.
"""

from __future__ import annotations

from typing import Any

AG_UI_STANDARD_EVENT_TYPES = {
    "RUN_STARTED",
    "RUN_FINISHED",
    "RUN_ERROR",
    "STEP_STARTED",
    "STEP_FINISHED",
    "TEXT_MESSAGE_START",
    "TEXT_MESSAGE_CONTENT",
    "TEXT_MESSAGE_END",
    "TOOL_CALL_START",
    "TOOL_CALL_ARGS",
    "TOOL_CALL_END",
    "TOOL_CALL_RESULT",
    "STATE_SNAPSHOT",
    "STATE_DELTA",
    "MESSAGES_SNAPSHOT",
    "ACTIVITY_SNAPSHOT",
    "ACTIVITY_DELTA",
    "RAW",
    "CUSTOM",
    "REASONING_START",
    "REASONING_MESSAGE_START",
    "REASONING_MESSAGE_CONTENT",
    "REASONING_MESSAGE_END",
    "REASONING_MESSAGE_CHUNK",
    "REASONING_END",
    "REASONING_ENCRYPTED_VALUE",
}


# ─────────────────────────────────────────────────────────────────────────────
# Layer 0: generic block → A2UI message
# ─────────────────────────────────────────────────────────────────────────────


def map_generic_block_to_a2ui_messages(
    block: dict[str, Any],
) -> list[dict[str, Any]]:
    block_id = block["id"]
    block_type = block["type"]
    props = block["props"]
    surface_id = f"generic_{block_id}"

    components = [
        {
            "id": f"{surface_id}_root",
            "component": block_type,
            "props": props,
        }
    ]

    return [
        {
            "version": "v0.9",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": "rm-workbench-v0",
            },
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": components,
            },
        },
        {
            "version": "v0.9",
            "updateDataModel": {
                "surfaceId": surface_id,
                "path": "/",
                "data": {"block_type": block_type, "props": props},
            },
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 (TRANSITIONAL — see ADR-013): RM semantic surface → A2UI message
#
# This entire section will be deleted in the Skill-driven Layer 1 migration
# issue. RM workflows will then express CustomerProfileCard / ProductFitTable
# / BriefExportPanel as compositions of Layer 0 primitives via Skill prompts,
# not as code branches here.
#
# DO NOT add new surface types or new business-domain branches in this
# section. New consumers should drive Layer 0 ``ui.blocks`` from their Skill.
# ─────────────────────────────────────────────────────────────────────────────


def _pending_interaction_id_for_surface(
    contract: dict[str, Any], surface_id: str
) -> str | None:
    """Find a pending_interaction.id matching the given surface_id, or None.

    Returns None gracefully when no matching interaction exists. Layer 0
    contracts may carry surfaces without pending_interactions, so this must
    not raise.
    """
    for interaction in contract.get("pending_interactions", []):
        if isinstance(interaction, dict) and interaction.get("surface_id") == surface_id:
            iid = interaction.get("id")
            if isinstance(iid, str):
                return iid
    return None


def map_rm_surface_to_a2ui_messages(
    contract: dict[str, Any], surface: dict[str, Any]
) -> list[dict[str, Any]]:
    """TRANSITIONAL: map an RM semantic surface to A2UI messages.

    Will be removed once RM migrates to Skill-driven Layer 0 composition
    (see ADR-013). All RM-specific contract fields (customer,
    product_candidates, memory_references, brief) are accessed via .get()
    so a missing field never crashes Layer 0 emission.
    """
    surface_id = surface["id"]
    surface_type = surface.get("surface", "")
    products = contract.get("product_candidates", [])
    customer = contract.get("customer", {})
    data_model: dict[str, Any] = {
        "customer": customer,
        "product_candidates": products,
        "surface_props": surface.get("props", {}),
    }

    if surface_type == "CustomerProfileCard":
        data_model["memory_references"] = contract.get("memory_references", [])
        components = [
            {
                "id": f"{surface_id}_root",
                "component": "Card",
                "children": [
                    f"{surface_id}_name",
                    f"{surface_id}_risk",
                    f"{surface_id}_aum",
                ],
            },
            {
                "id": f"{surface_id}_name",
                "component": "Text",
                "text": customer.get("name", ""),
            },
            {
                "id": f"{surface_id}_risk",
                "component": "Text",
                "text": f"Risk level: {customer.get('risk_level', '')}",
            },
            {
                "id": f"{surface_id}_aum",
                "component": "Text",
                "text": f"AUM: {customer.get('aum', '')}",
            },
        ]
    elif surface_type == "ProductFitTable":
        interaction_id = _pending_interaction_id_for_surface(contract, surface_id)
        action: dict[str, Any] = {
            "event": {
                "name": "pending_interaction.resolve",
                "context": {
                    "surface_id": surface_id,
                },
            }
        }
        if interaction_id is not None:
            action["event"]["context"]["interaction_id"] = interaction_id
        components = [
            {
                "id": f"{surface_id}_root",
                "component": "Table",
                "data": {"path": "/product_candidates"},
                "columns": ["name", "asset_class", "risk_level", "fit_score"],
            },
            {
                "id": f"{surface_id}_submit",
                "component": "Button",
                "text": "Confirm selection",
                "action": action,
            },
        ]
    elif surface_type == "BriefExportPanel":
        data_model["brief"] = contract.get("brief")
        components = [
            {
                "id": f"{surface_id}_root",
                "component": "Card",
                "children": [f"{surface_id}_title"],
            },
            {
                "id": f"{surface_id}_title",
                "component": "Text",
                "text": (contract.get("brief") or {}).get("title", surface_type),
            },
        ]
    else:
        components = [
            {
                "id": f"{surface_id}_root",
                "component": "Card",
                "children": [f"{surface_id}_title"],
            },
            {
                "id": f"{surface_id}_title",
                "component": "Text",
                "text": surface_type or "Surface",
            },
        ]

    return [
        {
            "version": "v0.9",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": "rm-workbench-v0",
            },
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": components,
            },
        },
        {
            "version": "v0.9",
            "updateDataModel": {
                "surfaceId": surface_id,
                "path": "/",
                "data": data_model,
            },
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Top-level dispatcher (Layer 0 scaffold + Layer 0 blocks + Layer 1 surfaces)
# ─────────────────────────────────────────────────────────────────────────────


def map_contract_to_agui_events(
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Map a Layer 0 contract envelope to a list of AG-UI events.

    Assumes the caller (``emit_tool.process_emit_tool``) has already filled
    in default metadata (kind/version/run_id/thread_id/skill).
    """
    run_id = contract["run_id"]
    thread_id = contract["thread_id"]

    events: list[dict[str, Any]] = [
        {
            "thread_id": thread_id,
            "run_id": run_id,
            "type": "RUN_STARTED",
        },
        {
            "type": "STEP_STARTED",
            "step_name": f"skill:{contract.get('skill', '')}",
        },
        {
            "type": "CUSTOM",
            "name": "rm.skill.output",
            "value": {
                "run_id": run_id,
                "thread_id": thread_id,
                "skill": contract.get("skill", ""),
                "contract_kind": contract.get("kind", "ui"),
                "contract_version": contract.get("version", ""),
            },
        },
    ]

    # Layer 1 transitional path
    for surface in contract.get("surfaces", []):
        events.append(
            {
                "type": "CUSTOM",
                "name": "a2ui.surface.messages",
                "value": {
                    "run_id": run_id,
                    "thread_id": thread_id,
                    "surface_id": surface["id"],
                    "surface": surface.get("surface", ""),
                    "messages": map_rm_surface_to_a2ui_messages(contract, surface),
                },
            }
        )

    # Layer 0 generic block path
    for block in contract.get("ui", {}).get("blocks", []):
        surface_id = f"generic_{block['id']}"
        events.append(
            {
                "type": "CUSTOM",
                "name": "a2ui.surface.messages",
                "value": {
                    "run_id": run_id,
                    "thread_id": thread_id,
                    "surface_id": surface_id,
                    "surface": block["type"],
                    "messages": map_generic_block_to_a2ui_messages(block),
                },
            }
        )

    for interaction in contract.get("pending_interactions", []):
        if not isinstance(interaction, dict):
            continue
        events.append(
            {
                "type": "CUSTOM",
                "name": "rm.pending_interaction.created",
                "value": {
                    "run_id": run_id,
                    "thread_id": thread_id,
                    "interaction_id": interaction.get("id"),
                    "surface_id": interaction.get("surface_id"),
                    "action": interaction.get("action"),
                    "blocking": interaction.get("blocking"),
                    "schema": interaction.get("schema"),
                },
            }
        )

    for proposal in contract.get("memory_proposals", []):
        events.append(
            {
                "type": "CUSTOM",
                "name": "rm.memory_proposal.created",
                "value": {
                    "run_id": run_id,
                    "thread_id": thread_id,
                    "proposals": [proposal],
                },
            }
        )

    for interaction in contract.get("pending_interactions", []):
        if not isinstance(interaction, dict):
            continue
        events.append(
            {
                "type": "STATE_DELTA",
                "delta": [
                    {
                        "op": "add",
                        "path": f"/pending_interactions/{interaction.get('id')}",
                        "value": {
                            "status": "waiting",
                            "action": interaction.get("action"),
                        },
                    }
                ],
            }
        )

    events.append(
        {
            "type": "STEP_FINISHED",
            "step_name": f"skill:{contract.get('skill', '')}",
        }
    )

    return events


def validate_agui_event_types(events: list[dict[str, Any]]) -> None:
    for event in events:
        if event["type"] not in AG_UI_STANDARD_EVENT_TYPES:
            raise ValueError(f"non-standard AG-UI event type: {event['type']}")
        if event["type"] == "CUSTOM":
            if not isinstance(event.get("name"), str):
                raise ValueError("CUSTOM event requires name")
            if "value" not in event:
                raise ValueError("CUSTOM event requires value")
