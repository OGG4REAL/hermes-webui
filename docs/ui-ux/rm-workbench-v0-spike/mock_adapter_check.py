#!/usr/bin/env python3
"""Executable mock for the RM Workbench V0 adapter boundary.

This is intentionally not production code. It checks whether a structured RM
Skill contract can be mapped into an AG-UI-compatible event transcript and a
blocking pending interaction can be resolved with structured UI input.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
CONTRACT_PATH = FIXTURES / "rm-pre-meeting-brief.valid.json"
RESOLVE_PATH = FIXTURES / "product-selection.resolve.json"

ALLOWED_SURFACES = {
    "CustomerProfileCard",
    "ProductFitTable",
    "PerformanceChart",
    "MemoryDiffCard",
    "BriefExportPanel",
}

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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} must contain a JSON object")
    return value


def require_object(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    if not isinstance(child, dict):
        raise AssertionError(f"{key} must be an object")
    return child


def require_list(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    if not isinstance(child, list) or not child:
        raise AssertionError(f"{key} must be a non-empty array")
    return child


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("kind") != "rm.pre_meeting_brief":
        raise AssertionError("contract.kind must be rm.pre_meeting_brief")
    if contract.get("version") != "0.1.0":
        raise AssertionError("contract.version must be 0.1.0")
    if not isinstance(contract.get("run_id"), str):
        raise AssertionError("run_id is required")
    if not isinstance(contract.get("thread_id"), str):
        raise AssertionError("thread_id is required")

    customer = require_object(contract, "customer")
    for key in ("id", "risk_level", "aum"):
        if key not in customer:
            raise AssertionError(f"customer.{key} is required")

    products = require_list(contract, "product_candidates")
    product_ids = {product.get("id") for product in products if isinstance(product, dict)}
    if len(product_ids) != len(products):
        raise AssertionError("product_candidates must have unique ids")

    surfaces = require_list(contract, "surfaces")
    for surface in surfaces:
        if not isinstance(surface, dict):
            raise AssertionError("each surface must be an object")
        if surface.get("surface") not in ALLOWED_SURFACES:
            raise AssertionError(f"unknown RM semantic surface: {surface.get('surface')}")
        if not isinstance(surface.get("props"), dict):
            raise AssertionError(f"{surface.get('surface')} must include props object")

    interactions = require_list(contract, "pending_interactions")
    for interaction in interactions:
        if not isinstance(interaction, dict):
            raise AssertionError("each pending interaction must be an object")
        if interaction.get("blocking") is not True:
            raise AssertionError("V0 spike expects blocking pending interaction")
        if interaction.get("action") != "select_products":
            raise AssertionError("V0 spike only validates select_products action")
        require_object(interaction, "schema")


def build_a2ui_surface(contract: dict[str, Any], surface: dict[str, Any]) -> list[dict[str, Any]]:
    surface_id = surface["id"]
    surface_type = surface["surface"]
    products = contract["product_candidates"]
    customer = contract["customer"]

    if surface_type == "CustomerProfileCard":
        components = [
            {
                "id": f"{surface_id}_root",
                "component": "Card",
                "children": [f"{surface_id}_name", f"{surface_id}_risk", f"{surface_id}_aum"],
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
                            "interaction_id": "pi_001",
                            "surface_id": surface_id,
                        },
                    }
                },
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
                "data": {
                    "customer": customer,
                    "product_candidates": products,
                    "surface_props": surface["props"],
                },
            },
        },
    ]


def map_to_events(contract: dict[str, Any]) -> list[dict[str, Any]]:
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
                    "messages": build_a2ui_surface(contract, surface),
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

    events.append(
        {
            "type": "STATE_DELTA",
            "delta": [
                {
                    "op": "add",
                    "path": f"/pending_interactions/{contract['pending_interactions'][0]['id']}",
                    "value": {
                        "status": "waiting",
                        "action": contract["pending_interactions"][0]["action"],
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


def validate_events(events: list[dict[str, Any]]) -> None:
    for event in events:
        if event["type"] not in AG_UI_STANDARD_EVENT_TYPES:
            raise AssertionError(f"non-standard AG-UI event type: {event['type']}")
        if event["type"] == "CUSTOM":
            if not isinstance(event.get("name"), str):
                raise AssertionError("CUSTOM event requires name")
            if "value" not in event:
                raise AssertionError("CUSTOM event requires value")


def validate_resolve(contract: dict[str, Any], resolve: dict[str, Any]) -> None:
    if resolve.get("type") != "pending_interaction.resolve":
        raise AssertionError("resolve.type must be pending_interaction.resolve")
    if resolve.get("run_id") != contract["run_id"]:
        raise AssertionError("resolve.run_id must match contract.run_id")
    if resolve.get("thread_id") != contract["thread_id"]:
        raise AssertionError("resolve.thread_id must match contract.thread_id")

    interaction_ids = {item["id"] for item in contract["pending_interactions"]}
    if resolve.get("interaction_id") not in interaction_ids:
        raise AssertionError("resolve.interaction_id must match a pending interaction")

    product_ids = {item["id"] for item in contract["product_candidates"]}
    payload = require_object(resolve, "payload")
    selected = payload.get("selected_product_ids")
    if not isinstance(selected, list):
        raise AssertionError("payload.selected_product_ids must be an array")
    if not 1 <= len(selected) <= 3:
        raise AssertionError("payload.selected_product_ids must contain 1 to 3 products")
    unknown = [product_id for product_id in selected if product_id not in product_ids]
    if unknown:
        raise AssertionError(f"selected unknown product ids: {unknown}")


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    resolve = load_json(RESOLVE_PATH)

    validate_contract(contract)
    print("OK: validated RM Skill contract")

    events = map_to_events(contract)
    validate_events(events)
    surface_count = sum(
        1
        for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    )
    print(f"OK: mapped {surface_count} surfaces")

    expected_event_types = [
        "RUN_STARTED",
        "STEP_STARTED",
        "CUSTOM",
        "STATE_DELTA",
        "STEP_FINISHED",
    ]
    event_types = {event["type"] for event in events}
    missing = [event_type for event_type in expected_event_types if event_type not in event_types]
    if missing:
        raise AssertionError(f"missing event types: {missing}")
    print(f"OK: produced {len(events)} AG-UI-compatible events")

    validate_resolve(contract, resolve)
    selected_count = len(resolve["payload"]["selected_product_ids"])
    print(
        "OK: resolved pending interaction "
        f"{resolve['interaction_id']} with {selected_count} selected products"
    )


if __name__ == "__main__":
    main()
