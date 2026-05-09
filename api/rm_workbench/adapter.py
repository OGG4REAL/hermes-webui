"""RM Workbench V0 adapter: maps structured RM Skill contracts to AG-UI events."""

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


def _pending_interaction_id_for_surface(
    contract: dict[str, Any], surface_id: str
) -> str:
    for interaction in contract["pending_interactions"]:
        if interaction.get("surface_id") == surface_id:
            return interaction["id"]
    raise ValueError(f"no pending interaction for surface: {surface_id}")


def map_surface_to_a2ui_messages(
    contract: dict[str, Any], surface: dict[str, Any]
) -> list[dict[str, Any]]:
    surface_id = surface["id"]
    surface_type = surface["surface"]
    products = contract["product_candidates"]
    customer = contract["customer"]
    data_model: dict[str, Any] = {
        "customer": customer,
        "product_candidates": products,
        "surface_props": surface["props"],
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
                "text": customer["name"],
            },
            {
                "id": f"{surface_id}_risk",
                "component": "Text",
                "text": f"Risk level: {customer['risk_level']}",
            },
            {
                "id": f"{surface_id}_aum",
                "component": "Text",
                "text": f"AUM: {customer['aum']}",
            },
        ]
    elif surface_type == "ProductFitTable":
        interaction_id = _pending_interaction_id_for_surface(contract, surface_id)
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
                "action": {
                    "event": {
                        "name": "pending_interaction.resolve",
                        "context": {
                            "interaction_id": interaction_id,
                            "surface_id": surface_id,
                        },
                    }
                },
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
                "text": contract.get("brief", {}).get("title", surface_type),
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
                "text": surface_type,
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


def map_rm_skill_contract_to_agui_events(
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
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
            "step_name": f"skill:{contract['skill']}",
        },
        {
            "type": "CUSTOM",
            "name": "rm.skill.output",
            "value": {
                "run_id": run_id,
                "thread_id": thread_id,
                "skill": contract["skill"],
                "contract_kind": contract["kind"],
                "contract_version": contract["version"],
            },
        },
    ]

    for surface in contract["surfaces"]:
        events.append(
            {
                "type": "CUSTOM",
                "name": "a2ui.surface.messages",
                "value": {
                    "run_id": run_id,
                    "thread_id": thread_id,
                    "surface_id": surface["id"],
                    "surface": surface["surface"],
                    "messages": map_surface_to_a2ui_messages(contract, surface),
                },
            }
        )

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

    for interaction in contract["pending_interactions"]:
        events.append(
            {
                "type": "CUSTOM",
                "name": "rm.pending_interaction.created",
                "value": {
                    "run_id": run_id,
                    "thread_id": thread_id,
                    "interaction_id": interaction["id"],
                    "surface_id": interaction["surface_id"],
                    "action": interaction["action"],
                    "blocking": interaction["blocking"],
                    "schema": interaction["schema"],
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

    for interaction in contract["pending_interactions"]:
        events.append(
            {
                "type": "STATE_DELTA",
                "delta": [
                    {
                        "op": "add",
                        "path": f"/pending_interactions/{interaction['id']}",
                        "value": {
                            "status": "waiting",
                            "action": interaction["action"],
                        },
                    }
                ],
            }
        )
    events.append(
        {
            "type": "STEP_FINISHED",
            "step_name": f"skill:{contract['skill']}",
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
