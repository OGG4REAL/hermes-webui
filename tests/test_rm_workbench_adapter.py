"""Tests for the RM Workbench V0 backend adapter."""

from __future__ import annotations


def test_maps_fixture_to_agui_standard_event_types():
    from api.rm_workbench.adapter import (
        AG_UI_STANDARD_EVENT_TYPES,
        map_contract_to_agui_events,
    )
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())

    assert events
    assert {event["type"] for event in events} <= AG_UI_STANDARD_EVENT_TYPES
    assert events[0]["type"] == "RUN_STARTED"


def test_surfaces_are_carried_as_custom_a2ui_messages():
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())
    surface_events = [
        event for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    ]

    rm_surfaces = [e for e in surface_events if not e["value"]["surface_id"].startswith("generic_")]
    assert len(rm_surfaces) == 3
    for event in surface_events:
        messages = event["value"]["messages"]
        assert messages[0]["createSurface"]["surfaceId"] == event["value"]["surface_id"]
        assert "updateComponents" in messages[1]
        assert "updateDataModel" in messages[2]


def test_pending_interaction_is_custom_plus_state_delta():
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())

    assert any(
        event["type"] == "CUSTOM"
        and event["name"] == "rm.pending_interaction.created"
        for event in events
    )
    assert any(event["type"] == "STATE_DELTA" for event in events)


def test_validate_agui_event_types_rejects_non_standard():
    from api.rm_workbench.adapter import validate_agui_event_types

    import pytest
    with pytest.raises(ValueError):
        validate_agui_event_types([{"type": "MADE_UP_EVENT"}])


def test_validate_agui_event_types_accepts_standard():
    from api.rm_workbench.adapter import (
        map_contract_to_agui_events,
        validate_agui_event_types,
    )
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())
    validate_agui_event_types(events)


def test_map_rm_surface_to_a2ui_messages():
    from api.rm_workbench.adapter import map_rm_surface_to_a2ui_messages
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    contract = load_pre_meeting_brief_fixture()
    surface = contract["surfaces"][0]
    messages = map_rm_surface_to_a2ui_messages(contract, surface)

    assert len(messages) == 3
    assert "createSurface" in messages[0]
    assert "updateComponents" in messages[1]
    assert "updateDataModel" in messages[2]


def test_product_fit_table_action_uses_contract_pending_interaction_id():
    from api.rm_workbench.adapter import map_rm_surface_to_a2ui_messages
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    contract = load_pre_meeting_brief_fixture()
    contract["pending_interactions"][0]["id"] = "pi_custom"
    surface = contract["surfaces"][1]

    messages = map_rm_surface_to_a2ui_messages(contract, surface)
    components = messages[1]["updateComponents"]["components"]
    button = next(component for component in components if component["component"] == "Button")

    assert button["action"]["event"]["context"]["interaction_id"] == "pi_custom"


def test_generic_blocks_produce_a2ui_surface_messages():
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())
    surface_events = [
        event for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    ]

    generic_surfaces = {
        event["value"]["surface"]
        for event in surface_events
        if event["value"]["surface_id"].startswith("generic_")
    }
    assert generic_surfaces == {
        "MetricCard", "DataTable", "LineChart", "BarChart", "PieChart", "ChoiceList"
    }


def test_generic_block_a2ui_messages_have_correct_structure():
    from api.rm_workbench.adapter import map_generic_block_to_a2ui_messages

    block = {
        "id": "test_metric",
        "type": "MetricCard",
        "props": {"label": "AUM", "value": "100"},
    }
    messages = map_generic_block_to_a2ui_messages(block)

    assert len(messages) == 3
    assert messages[0]["createSurface"]["surfaceId"] == "generic_test_metric"
    assert messages[1]["updateComponents"]["surfaceId"] == "generic_test_metric"
    assert messages[1]["updateComponents"]["components"][0]["component"] == "MetricCard"
    assert messages[2]["updateDataModel"]["data"]["block_type"] == "MetricCard"
    assert messages[2]["updateDataModel"]["data"]["props"]["label"] == "AUM"


def test_generic_blocks_do_not_break_existing_surfaces():
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())
    surface_events = [
        event for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    ]

    rm_surfaces = {
        event["value"]["surface"]
        for event in surface_events
        if not event["value"]["surface_id"].startswith("generic_")
    }
    assert rm_surfaces == {"CustomerProfileCard", "ProductFitTable", "BriefExportPanel"}


def test_contract_without_ui_blocks_still_valid():
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    contract = load_pre_meeting_brief_fixture()
    contract.pop("ui", None)
    events = map_contract_to_agui_events(contract)

    surface_events = [
        event for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    ]
    assert len(surface_events) == 3


def test_contract_validation_rejects_unknown_block_type():
    from api.rm_workbench.contracts import validate_contract
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture
    import pytest

    contract = load_pre_meeting_brief_fixture()
    contract["ui"] = {"blocks": [{"id": "bad", "type": "ArbitraryJSX", "props": {}}]}
    with pytest.raises(ValueError, match="unknown generic block type"):
        validate_contract(contract)


def test_contract_validation_accepts_chart_with_incomplete_props():
    """Per ADR-010, Layer 0 validator is best-effort: per-type field strictness
    (chart series.key matching data row keys, empty data arrays, etc.) is the
    primitive's responsibility on the frontend, not the validator's. A chart
    block with empty data must validate successfully so that the frontend can
    render a clear empty-state placeholder.
    """
    from api.rm_workbench.contracts import validate_contract
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    contract = load_pre_meeting_brief_fixture()
    contract["ui"] = {"blocks": [{"id": "lc", "type": "LineChart", "props": {"xKey": "x", "series": [{"key": "y"}], "data": []}}]}
    validate_contract(contract)  # should not raise


def test_semantic_surface_data_models_include_chinese_demo_payloads():
    from api.rm_workbench.adapter import map_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_contract_to_agui_events(load_pre_meeting_brief_fixture())
    surfaces = {
        event["value"]["surface"]: event["value"]["messages"][2]["updateDataModel"]["data"]
        for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    }

    assert surfaces["CustomerProfileCard"]["customer"]["name"] == "模拟客户"
    assert surfaces["CustomerProfileCard"]["memory_references"][0]["summary"] == (
        "经历过高波动基金后，更偏好回撤较低的产品。"
    )
    assert surfaces["ProductFitTable"]["product_candidates"][0]["name"] == "稳健收益组合 A"
    assert surfaces["BriefExportPanel"]["brief"]["title"] == "模拟客户会前简报"
