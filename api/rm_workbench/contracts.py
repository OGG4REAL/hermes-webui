"""Lightweight contract validation for RM Workbench V0.

No external jsonschema dependency. Validates structural assumptions that the
adapter relies on.
"""

from __future__ import annotations

from typing import Any

ALLOWED_SURFACES = {
    "CustomerProfileCard",
    "ProductFitTable",
    "PerformanceChart",
    "MemoryDiffCard",
    "BriefExportPanel",
}

ALLOWED_GENERIC_BLOCKS = {
    "MetricCard",
    "DataTable",
    "LineChart",
    "BarChart",
    "PieChart",
    "ChoiceList",
}


def _require_object(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    if not isinstance(child, dict):
        raise ValueError(f"{key} must be an object")
    return child


def _require_list(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    if not isinstance(child, list) or not child:
        raise ValueError(f"{key} must be a non-empty array")
    return child


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

        if btype in ("LineChart", "BarChart"):
            data = props.get("data")
            if not isinstance(data, list) or not data:
                raise ValueError(f"{btype} '{bid}' props.data must be a non-empty array")
            x_key = props.get("xKey")
            if not isinstance(x_key, str):
                raise ValueError(f"{btype} '{bid}' props.xKey is required")
            series = props.get("series")
            if not isinstance(series, list) or not series:
                raise ValueError(f"{btype} '{bid}' props.series must be a non-empty array")
            for row in data:
                if not isinstance(row, dict):
                    raise ValueError(f"{btype} '{bid}' each data row must be an object")
                if x_key not in row:
                    raise ValueError(f"{btype} '{bid}' xKey '{x_key}' missing from data row")
                for s in series:
                    if not isinstance(s, dict):
                        raise ValueError(f"{btype} '{bid}' each series entry must be an object")
                    skey = s.get("key")
                    if not isinstance(skey, str):
                        raise ValueError(f"{btype} '{bid}' series entry missing key")
                    if skey not in row:
                        raise ValueError(f"{btype} '{bid}' series key '{skey}' missing from data row")

        elif btype == "PieChart":
            data = props.get("data")
            if not isinstance(data, list) or not data:
                raise ValueError(f"PieChart '{bid}' props.data must be a non-empty array")
            label_key = props.get("labelKey")
            value_key = props.get("valueKey")
            if not isinstance(label_key, str):
                raise ValueError(f"PieChart '{bid}' props.labelKey is required")
            if not isinstance(value_key, str):
                raise ValueError(f"PieChart '{bid}' props.valueKey is required")
            for row in data:
                if not isinstance(row, dict):
                    raise ValueError(f"PieChart '{bid}' each data row must be an object")
                if label_key not in row:
                    raise ValueError(f"PieChart '{bid}' labelKey '{label_key}' missing from data row")
                if value_key not in row:
                    raise ValueError(f"PieChart '{bid}' valueKey '{value_key}' missing from data row")

        elif btype == "DataTable":
            columns = props.get("columns")
            if not isinstance(columns, list) or not columns:
                raise ValueError(f"DataTable '{bid}' props.columns must be a non-empty array")
            rows = props.get("rows")
            if not isinstance(rows, list):
                raise ValueError(f"DataTable '{bid}' props.rows must be an array")

        elif btype == "ChoiceList":
            options = props.get("options")
            if not isinstance(options, list) or not options:
                raise ValueError(f"ChoiceList '{bid}' props.options must be a non-empty array")

        elif btype == "MetricCard":
            pass


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("kind") != "rm.pre_meeting_brief":
        raise ValueError("contract.kind must be rm.pre_meeting_brief")
    if contract.get("version") != "0.1.0":
        raise ValueError("contract.version must be 0.1.0")
    if not isinstance(contract.get("run_id"), str):
        raise ValueError("run_id is required")
    if not isinstance(contract.get("thread_id"), str):
        raise ValueError("thread_id is required")

    customer = _require_object(contract, "customer")
    for key in ("id", "risk_level", "aum"):
        if key not in customer:
            raise ValueError(f"customer.{key} is required")

    products = _require_list(contract, "product_candidates")
    product_ids = {p.get("id") for p in products if isinstance(p, dict)}
    if len(product_ids) != len(products):
        raise ValueError("product_candidates must have unique ids")

    surfaces = _require_list(contract, "surfaces")
    for surface in surfaces:
        if not isinstance(surface, dict):
            raise ValueError("each surface must be an object")
        if surface.get("surface") not in ALLOWED_SURFACES:
            raise ValueError(f"unknown RM semantic surface: {surface.get('surface')}")
        if not isinstance(surface.get("props"), dict):
            raise ValueError(f"{surface.get('surface')} must include props object")

    surface_ids = {s["id"] for s in surfaces if isinstance(s, dict) and isinstance(s.get("id"), str)}

    interactions = _require_list(contract, "pending_interactions")
    for interaction in interactions:
        if not isinstance(interaction, dict):
            raise ValueError("each pending interaction must be an object")
        if not isinstance(interaction.get("id"), str) or not interaction["id"]:
            raise ValueError("each pending interaction must have a non-empty string id")
        if not isinstance(interaction.get("surface_id"), str):
            raise ValueError("each pending interaction must reference a surface_id")
        if interaction["surface_id"] not in surface_ids:
            raise ValueError(f"pending interaction references unknown surface_id: {interaction['surface_id']}")
        if interaction.get("blocking") is not True:
            raise ValueError("V0 expects blocking pending interaction")
        if interaction.get("action") != "select_products":
            raise ValueError("V0 only validates select_products action")
        _require_object(interaction, "schema")

    ui = contract.get("ui")
    if ui is not None:
        if not isinstance(ui, dict):
            raise ValueError("ui must be an object")
        blocks = ui.get("blocks")
        if blocks is not None:
            if not isinstance(blocks, list):
                raise ValueError("ui.blocks must be an array")
            _validate_ui_blocks(blocks)

    memory_proposals = contract.get("memory_proposals")
    if memory_proposals is not None:
        if not isinstance(memory_proposals, list):
            raise ValueError("memory_proposals must be an array")
        for mp in memory_proposals:
            if not isinstance(mp, dict):
                raise ValueError("each memory_proposal must be an object")
            if not isinstance(mp.get("id"), str):
                raise ValueError("memory_proposal.id is required")
