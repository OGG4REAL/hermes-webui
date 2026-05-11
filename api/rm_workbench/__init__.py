"""Layer 0 structured UI subsystem backend adapter package.

Directory name retained as ``rm_workbench`` for historical reasons
(deprecation queue, ADR-012).
"""

from api.rm_workbench.adapter import (
    AG_UI_STANDARD_EVENT_TYPES,
    map_contract_to_agui_events,
    map_generic_block_to_a2ui_messages,
    map_rm_surface_to_a2ui_messages,
    validate_agui_event_types,
)

__all__ = [
    "AG_UI_STANDARD_EVENT_TYPES",
    "map_contract_to_agui_events",
    "map_generic_block_to_a2ui_messages",
    "map_rm_surface_to_a2ui_messages",
    "validate_agui_event_types",
]
