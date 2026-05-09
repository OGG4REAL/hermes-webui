# RM Workbench V0 Adapter Implementation Plan

> **Status:** `reference / historical implementation plan`
> **Current source of truth:** Architecture = `rm-workbench-v0-architecture.md`; ADR = `rm-workbench-v0-adr.md`; sequencing = `rm-workbench-v0-roadmap.md`.
> **Note:** This plan records the original V0 vertical-slice implementation shape. Do not use it as the current default issue plan without checking the core docs first.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first executable RM Workbench V0 vertical slice: RM Skill structured contract -> Hermes-webui adapter -> AG-UI-compatible event stream carrying A2UI surface messages -> React workbench renderer -> pending interaction resolve.

**Architecture:** Hermes Agent remains the runtime and hermes-webui remains the backend source of truth. The V0 adapter only maps structured RM Skill contracts into AG-UI standard events plus `CUSTOM` payloads carrying A2UI messages; pending UI interactions use a new backend abstraction instead of reusing clarify semantics.

**Tech Stack:** Python standard library backend first, existing hermes-webui SSE/routes/session stack, JSON Schema drafts as contract artifacts, React + TypeScript + Vite for the new workbench host after backend adapter smoke tests pass.

**V0 Docs Entry:** `docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. Current Inputs

Planning docs already created:

- `docs/ui-ux/rm-workbench-v0-technical-skeleton.md`
- `docs/ui-ux/rm-workbench-v0-protocol-examples.md`
- `docs/ui-ux/rm-workbench-v0-adapter-spike-plan.md`
- `docs/ui-ux/rm-workbench-v0-agui-a2ui-alignment.md`

Executable spike harness already created:

- `docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py`
- `docs/ui-ux/rm-workbench-v0-spike/fixtures/rm-pre-meeting-brief.valid.json`
- `docs/ui-ux/rm-workbench-v0-spike/fixtures/product-selection.resolve.json`
- `docs/ui-ux/rm-workbench-v0-spike/schemas/rm.pre_meeting_brief.v0.1.0.schema.json`
- `docs/ui-ux/rm-workbench-v0-spike/schemas/pending_interaction.resolve.v0.1.0.schema.json`

Current verified command:

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
```

Expected output:

```text
OK: validated RM Skill contract
OK: mapped 3 surfaces
OK: produced 9 AG-UI-compatible events
OK: resolved pending interaction pi_001 with 2 selected products
```

---

## 1. Implementation Shape

V0 should be implemented in four slices:

1. Backend adapter library with tests.
2. Pending interaction backend state and routes.
3. Mock RM workbench stream endpoint for vertical-slice testing.
4. React workbench host with minimal A2UI renderer.

The first two slices should not require Node, package installs, or CopilotKit. The React slice is where Node/Vite dependencies enter.

---

## 2. Files To Create Or Modify

### Backend Adapter

- Create: `api/rm_workbench/__init__.py`
  - Package marker and public exports.

- Create: `api/rm_workbench/contracts.py`
  - Lightweight contract validation helpers for V0.
  - No external `jsonschema` dependency in V0.
  - Loads fixture/schema-adjacent assumptions into explicit Python validation.

- Create: `api/rm_workbench/adapter.py`
  - `map_rm_skill_contract_to_agui_events(contract: dict) -> list[dict]`
  - `map_surface_to_a2ui_messages(contract: dict, surface: dict) -> list[dict]`
  - `validate_agui_event_types(events: list[dict]) -> None`

- Create: `api/rm_workbench/mock_data.py`
  - Loads the existing spike fixture for local testing.
  - Keeps mock data out of runtime code paths unless explicit test/dev route is used.

### Pending Interaction

- Create: `api/pending_interactions.py`
  - Modeled after `api/clarify.py` but with structured payload result.
  - Exposes `submit_pending`, `get_pending`, `resolve_pending`, `clear_pending`, `register_gateway_notify`, `unregister_gateway_notify`.

- Modify: `api/routes.py`
  - Add `GET /api/rm-workbench/pending`.
  - Add `POST /api/rm-workbench/pending/resolve`.
  - Add loopback-only `GET /api/rm-workbench/inject_test` for automated/manual local testing.

- Modify: `api/streaming.py`
  - Register pending interaction notify callback next to approval/clarify registration.
  - Emit SSE event `rm_workbench` when a pending interaction is created by the backend adapter.

### Test Coverage

- Create: `tests/test_rm_workbench_adapter.py`
  - Validates event mapping from fixture.
  - Asserts every top-level AG-UI `type` is official.
  - Asserts A2UI messages are carried only inside `CUSTOM name = a2ui.surface.messages`.

- Create: `tests/test_pending_interactions.py`
  - Validates queue semantics.
  - Validates structured resolve payload.
  - Validates cancel/clear behavior unblocks waiting entries.

- Create: `tests/test_rm_workbench_routes.py`
  - Validates pending GET/POST routes.
  - Validates loopback-only inject route behavior.

### React Workbench Host

Only start this slice after backend tests pass.

- Create: `frontend/package.json`
  - Vite + React + TypeScript app for workbench host.

- Create: `frontend/index.html`
  - React mount target.

- Create: `frontend/src/main.tsx`
  - Bootstraps the app.

- Create: `frontend/src/api/hermesClient.ts`
  - Starts chat streams and pending interaction resolve requests.

- Create: `frontend/src/agui/aguiReducer.ts`
  - Reduces AG-UI standard events and `CUSTOM` events into UI state.

- Create: `frontend/src/a2ui/types.ts`
  - Minimal V0 A2UI message and component types.

- Create: `frontend/src/a2ui/A2UISurfaceRenderer.tsx`
  - Renders V0 A2UI-like surfaces.

- Create: `frontend/src/rm/surfaces/CustomerProfileCard.tsx`
  - RM semantic surface shell.

- Create: `frontend/src/rm/surfaces/ProductFitTable.tsx`
  - Table + selection interaction.

- Create: `frontend/src/rm/surfaces/BriefExportPanel.tsx`
  - Export panel shell for the vertical slice.

- Create: `frontend/src/App.tsx`
  - Minimal workbench layout for the V0 vertical slice.

### React Serving

- Modify: `server.py`
  - Only after React build exists: serve built assets or route `/workbench` to build output.

- Modify: `.gitignore`
  - Ignore `frontend/dist/` and package-manager cache if needed.

---

## 3. Task 1: Backend Adapter Library

**Files:**

- Create: `api/rm_workbench/__init__.py`
- Create: `api/rm_workbench/contracts.py`
- Create: `api/rm_workbench/adapter.py`
- Create: `api/rm_workbench/mock_data.py`
- Create: `tests/test_rm_workbench_adapter.py`

- [ ] **Step 1: Write adapter tests first**

Create `tests/test_rm_workbench_adapter.py` with tests for:

```python
def test_maps_fixture_to_agui_standard_event_types():
    from api.rm_workbench.adapter import (
        AG_UI_STANDARD_EVENT_TYPES,
        map_rm_skill_contract_to_agui_events,
    )
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_rm_skill_contract_to_agui_events(load_pre_meeting_brief_fixture())

    assert events
    assert {event["type"] for event in events} <= AG_UI_STANDARD_EVENT_TYPES
    assert events[0]["type"] == "RUN_STARTED"


def test_surfaces_are_carried_as_custom_a2ui_messages():
    from api.rm_workbench.adapter import map_rm_skill_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_rm_skill_contract_to_agui_events(load_pre_meeting_brief_fixture())
    surface_events = [
        event for event in events
        if event["type"] == "CUSTOM" and event["name"] == "a2ui.surface.messages"
    ]

    assert len(surface_events) == 3
    for event in surface_events:
        messages = event["value"]["messages"]
        assert messages[0]["createSurface"]["surfaceId"] == event["value"]["surface_id"]
        assert "updateComponents" in messages[1]
        assert "updateDataModel" in messages[2]


def test_pending_interaction_is_custom_plus_state_delta():
    from api.rm_workbench.adapter import map_rm_skill_contract_to_agui_events
    from api.rm_workbench.mock_data import load_pre_meeting_brief_fixture

    events = map_rm_skill_contract_to_agui_events(load_pre_meeting_brief_fixture())

    assert any(
        event["type"] == "CUSTOM"
        and event["name"] == "rm.pending_interaction.created"
        for event in events
    )
    assert any(event["type"] == "STATE_DELTA" for event in events)
```

- [ ] **Step 2: Run the new failing tests**

Run:

```bash
pytest tests/test_rm_workbench_adapter.py -q
```

Expected before implementation:

```text
FAILED tests/test_rm_workbench_adapter.py
```

- [ ] **Step 3: Implement minimal adapter code**

Move the logic proven in `docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py` into `api/rm_workbench/adapter.py`.

Implementation requirements:

- Top-level event `type` values must come from AG-UI official event names.
- RM-specific semantics must use `CUSTOM`.
- A2UI messages must stay inside `CUSTOM name = a2ui.surface.messages`.
- No natural-language parsing.
- No external package dependency.

- [ ] **Step 4: Add fixture loader**

Create `api/rm_workbench/mock_data.py` that reads:

```text
docs/ui-ux/rm-workbench-v0-spike/fixtures/rm-pre-meeting-brief.valid.json
```

The loader should use `Path(__file__).resolve().parents[2]` to reach repo root, so tests work from any cwd.

- [ ] **Step 5: Run adapter tests**

Run:

```bash
pytest tests/test_rm_workbench_adapter.py -q
```

Expected after implementation:

```text
3 passed
```

---

## 4. Task 2: Pending Interaction Backend

**Files:**

- Create: `api/pending_interactions.py`
- Create: `tests/test_pending_interactions.py`

- [ ] **Step 1: Write queue tests first**

Create `tests/test_pending_interactions.py` with:

```python
def test_submit_get_and_resolve_pending_interaction():
    from api.pending_interactions import clear_pending, get_pending, resolve_pending, submit_pending

    session_id = "test-session"
    clear_pending(session_id)
    entry = submit_pending(session_id, {
        "id": "pi_test",
        "kind": "pending_interaction",
        "action": "select_products",
        "schema": {"type": "object"},
    })

    assert get_pending(session_id)["id"] == "pi_test"
    assert resolve_pending(session_id, {"selected_product_ids": ["prod_001"]}) == 1
    assert entry.result == {"selected_product_ids": ["prod_001"]}
    assert get_pending(session_id) is None


def test_clear_pending_unblocks_entries():
    from api.pending_interactions import clear_pending, submit_pending

    session_id = "test-session-clear"
    entry = submit_pending(session_id, {
        "id": "pi_clear",
        "kind": "pending_interaction",
        "action": "select_products",
        "schema": {"type": "object"},
    })

    assert clear_pending(session_id) == 1
    assert entry.event.is_set()
```

- [ ] **Step 2: Run the new failing tests**

Run:

```bash
pytest tests/test_pending_interactions.py -q
```

Expected before implementation:

```text
FAILED tests/test_pending_interactions.py
```

- [ ] **Step 3: Implement `api/pending_interactions.py`**

Use `api/clarify.py` as the implementation pattern, but change the result type from string to dict.

Implementation requirements:

- Keep `_lock`, `_pending`, `_gateway_queues`, `_gateway_notify_cbs`.
- Queue per session.
- `get_pending(session_key)` returns the oldest unresolved entry data.
- `resolve_pending(session_key, payload, resolve_all=False)` resolves oldest by default.
- `clear_pending(session_key)` unblocks all entries and returns count.
- `register_gateway_notify` and `unregister_gateway_notify` mirror clarify behavior.

- [ ] **Step 4: Run pending interaction tests**

Run:

```bash
pytest tests/test_pending_interactions.py -q
```

Expected after implementation:

```text
2 passed
```

---

## 5. Task 3: Pending Interaction Routes

**Files:**

- Modify: `api/routes.py`
- Create: `tests/test_rm_workbench_routes.py`

- [ ] **Step 1: Write route tests**

Create tests that call route helpers directly or use the existing test server harness pattern in nearby route tests.

Required route behavior:

```text
GET /api/rm-workbench/pending?session_id=<sid>
  -> {"pending": null}
  -> {"pending": {...}}

POST /api/rm-workbench/pending/resolve
  body: {"session_id": "...", "payload": {...}}
  -> {"ok": true, "resolved": 1}
```

Loopback-only route:

```text
GET /api/rm-workbench/inject_test?session_id=<sid>
  -> {"ok": true, "session_id": "..."}
```

- [ ] **Step 2: Add imports in `api/routes.py`**

Add next to clarify imports:

```python
try:
    from api.pending_interactions import (
        submit_pending as submit_rm_pending,
        get_pending as get_rm_pending,
        resolve_pending as resolve_rm_pending,
    )
except ImportError:
    submit_rm_pending = lambda *a, **k: None
    get_rm_pending = lambda *a, **k: None
    resolve_rm_pending = lambda *a, **k: 0
```

- [ ] **Step 3: Add GET route dispatch**

Add in `handle_get` near clarify routes:

```python
if parsed.path == "/api/rm-workbench/pending":
    return _handle_rm_workbench_pending(handler, parsed)

if parsed.path == "/api/rm-workbench/inject_test":
    return _handle_rm_workbench_inject(handler, parsed)
```

- [ ] **Step 4: Add POST route dispatch**

Add in `handle_post` near clarify respond:

```python
if parsed.path == "/api/rm-workbench/pending/resolve":
    return _handle_rm_workbench_pending_resolve(handler, body)
```

- [ ] **Step 5: Add route handlers**

Implement:

```python
def _handle_rm_workbench_pending(handler, parsed):
    sid = parse_qs(parsed.query).get("session_id", [""])[0]
    if not sid:
        return bad(handler, "session_id is required")
    pending = get_rm_pending(sid)
    return j(handler, {"pending": pending})


def _handle_rm_workbench_inject(handler, parsed):
    qs = parse_qs(parsed.query)
    sid = qs.get("session_id", [""])[0]
    if not sid:
        return bad(handler, "session_id is required")
    submit_rm_pending(sid, {
        "id": "pi_test",
        "kind": "pending_interaction",
        "action": "select_products",
        "surface_id": "surface_product_fit_001",
        "blocking": True,
        "schema": {"type": "object"},
    })
    return j(handler, {"ok": True, "session_id": sid})


def _handle_rm_workbench_pending_resolve(handler, body):
    sid = body.get("session_id", "")
    if not sid:
        return bad(handler, "session_id is required")
    payload = body.get("payload")
    if not isinstance(payload, dict):
        return bad(handler, "payload object is required")
    resolved = resolve_rm_pending(sid, payload, resolve_all=False)
    return j(handler, {"ok": True, "resolved": resolved})
```

- [ ] **Step 6: Run route tests**

Run:

```bash
pytest tests/test_rm_workbench_routes.py -q
```

Expected after implementation:

```text
passed
```

---

## 6. Task 4: Streaming Integration For Backend Events

**Files:**

- Modify: `api/streaming.py`
- Create or extend: `tests/test_rm_workbench_adapter.py`

- [ ] **Step 1: Register pending interaction notify callback**

In `_run_agent_streaming`, next to approval/clarify callback registration, register RM pending interaction notification:

```python
try:
    from api.pending_interactions import (
        register_gateway_notify as _reg_rm_pending_notify,
        unregister_gateway_notify as _unreg_rm_pending_notify,
    )

    def _rm_pending_notify_cb(interaction_data):
        put("rm_workbench", {
            "kind": "pending_interaction",
            "event": "created",
            "data": interaction_data,
        })

    _reg_rm_pending_notify(session_id, _rm_pending_notify_cb)
    _rm_pending_registered = True
except ImportError:
    logger.debug("RM pending interaction module not available")
```

Also unregister in the same `finally` block style used by clarify.

- [ ] **Step 2: Add a mock adapter emission point**

Do not wire real Hermes Skill output yet. Add a clearly dev-only helper route or test-only path that uses `api.rm_workbench.mock_data.load_pre_meeting_brief_fixture()` and `map_rm_skill_contract_to_agui_events(...)`.

V0 acceptance is a backend smoke stream, not production skill invocation.

- [ ] **Step 3: Verify existing clarify tests still pass**

Run:

```bash
pytest tests/test_clarify_unblock.py tests/test_cancel_interrupt.py -q
```

Expected:

```text
passed
```

---

## 7. Task 5: Frontend Smoke Workbench

Status: next recommended implementation slice after MYM-24 and MYM-25.

This task should produce the first user-auditable UI. It is intentionally a smoke workbench, not the full Hermes chat replacement.

### Scope

The smoke workbench should:

- Render a mock AG-UI/A2UI transcript.
- Display `CustomerProfileCard`, `ProductFitTable`, and `BriefExportPanel`.
- Allow selecting 1-3 products in `ProductFitTable`.
- POST the structured selection to `/api/rm-workbench/pending/resolve`.
- Show visible pending/resolved/error states.

The smoke workbench should not:

- Connect to real Hermes chat.
- Use CopilotKit runtime.
- Implement a real RM Skill.
- Use real customer or product data.
- Implement Memory writes.

### Suggested Files

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/api/hermesClient.ts`
- Create: `frontend/src/agui/aguiReducer.ts`
- Create: `frontend/src/a2ui/types.ts`
- Create: `frontend/src/a2ui/A2UISurfaceRenderer.tsx`
- Create: `frontend/src/fixtures/rmWorkbenchTranscript.ts`
- Create: `frontend/src/rm/surfaces/CustomerProfileCard.tsx`
- Create: `frontend/src/rm/surfaces/ProductFitTable.tsx`
- Create: `frontend/src/rm/surfaces/BriefExportPanel.tsx`

- [ ] **Step 1: Confirm dependency approval before installing**

This task requires Node dependencies. Run install only after explicit approval because it will write `frontend/package-lock.json` or equivalent lockfile.

Preferred package manager should be decided in the Multica issue before implementation. If the repo has no existing frontend package manager convention, default to `npm` for the smoke slice.

Recommended dependencies:

```json
{
  "dependencies": {
    "@vitejs/plugin-react": "latest",
    "vite": "latest",
    "typescript": "latest",
    "react": "latest",
    "react-dom": "latest",
    "lucide-react": "latest"
  },
  "devDependencies": {}
}
```

- [ ] **Step 2: Implement AG-UI reducer**

Reducer behavior:

```text
RUN_STARTED -> set running state
RUN_FINISHED -> clear running state
RUN_ERROR -> set error
TEXT_MESSAGE_* -> update assistant message
CUSTOM a2ui.surface.messages -> append/update surfaces
CUSTOM rm.pending_interaction.created -> register pending interaction
STATE_DELTA -> patch pending interaction state
```

For the smoke slice, the reducer can consume a static transcript from `frontend/src/fixtures/rmWorkbenchTranscript.ts`. It does not need to connect to `/api/chat/stream`.

- [ ] **Step 3: Implement minimal A2UI renderer**

Renderer supports:

```text
Card
Text
Table
Button
```

It should ignore unknown components with a small fallback block, not crash the workbench.

- [ ] **Step 4: Implement ProductFitTable selection**

The table should:

- Read product rows from surface data model.
- Allow selecting 1-3 products.
- Disable confirm until at least 1 product is selected.
- POST to `/api/rm-workbench/pending/resolve` with:

```json
{
  "session_id": "<session id>",
  "payload": {
    "selected_product_ids": ["prod_001", "prod_002"]
  }
}
```

- [ ] **Step 5: Add smoke UI states**

The user should be able to visually audit:

- initial transcript loaded
- surfaces rendered
- products selected
- pending interaction submit in progress
- resolve success
- resolve error

- [ ] **Step 6: Run frontend verification**

Run:

```bash
cd frontend
npm run build
```

Expected:

```text
built
```

- [ ] **Step 7: Manual audit note**

The issue completion comment should include:

```text
Local URL:
What the user can click:
What is mocked:
What is not connected yet:
Screenshots if available:
```

---

## 8. Task 6: Backend Mock Stream Integration

Status: completed as `MYM-27` / `1b30919c-e851-4c18-a513-f42f4980fdf5`; passed Codex acceptance review.

This task should replace the frontend's default static transcript with a backend mock stream generated by the production RM Workbench adapter. It is still a smoke path, not real Hermes chat integration.

### Scope

The backend mock stream should:

- Load the mock RM Skill contract through `api.rm_workbench.mock_data.load_pre_meeting_brief_fixture`.
- Generate AG-UI/A2UI events through `api.rm_workbench.adapter.map_rm_skill_contract_to_agui_events`.
- Expose those events through a dev/test-only stream endpoint.
- Use the same event shape that the frontend reducer already understands.

The frontend should:

- Consume the backend mock stream by default.
- Keep static transcript fallback only as a dev fallback.
- Continue to submit product selection through `/api/rm-workbench/pending/resolve`.
- Keep all user-visible smoke UI Chinese-first.

This task should not:

- Connect to real `/api/chat/stream`.
- Connect to CopilotKit runtime.
- Implement real RM Skill execution.
- Use real customer/product data.
- Implement Memory writes.

### Suggested Files

Backend:

- Modify: `api/routes.py`
- Create or modify: `tests/test_rm_workbench_mock_stream.py`

Frontend:

- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/api/hermesClient.ts`
- Modify: `frontend/src/agui/aguiReducer.ts` only if the stream envelope requires it.
- Keep: `frontend/src/fixtures/rmWorkbenchTranscript.ts` as fallback/reference.

- [ ] **Step 1: Add backend mock stream route test**

The test should verify:

```text
GET /api/rm-workbench/mock-stream returns streamable AG-UI/A2UI events.
Every top-level event type is official AG-UI or CUSTOM.
At least one CUSTOM a2ui.surface.messages event exists.
At least one CUSTOM rm.pending_interaction.created event exists.
```

- [ ] **Step 2: Add dev/test-only backend route**

Suggested route:

```text
GET /api/rm-workbench/mock-stream
```

Implementation rule:

```text
load_pre_meeting_brief_fixture()
  -> map_rm_skill_contract_to_agui_events(...)
  -> stream or return events in the same order
```

If true SSE is too much for this slice, returning an ordered JSON transcript is acceptable only if the issue comment explains why. The preferred path is SSE/EventSource because the next real integration will be streaming.

- [ ] **Step 3: Update frontend client**

Add a client function such as:

```text
loadWorkbenchMockStream()
```

It should consume the backend mock stream and return the ordered event list to the reducer.

- [ ] **Step 4: Replace default static transcript load**

`App.tsx` should default to backend mock stream:

```text
backend mock stream succeeds -> render streamed events
backend mock stream fails -> show warning and optionally fall back to static transcript
```

The UI must make the fallback visible; it should not silently pretend backend streaming succeeded.

- [ ] **Step 5: Preserve pending interaction behavior**

Product selection should still:

```text
seed pending interaction if needed
POST /api/rm-workbench/pending/resolve
treat resolved: 0 as error
show resolved success only after backend confirms
```

- [ ] **Step 6: Run verification**

Run:

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_adapter.py tests/test_pending_interactions.py tests/test_rm_workbench_routes.py tests/test_rm_workbench_mock_stream.py -q
cd frontend
npm run build
```

- [ ] **Step 7: Manual audit note**

The issue completion comment should include:

```text
Local backend command:
Local frontend command:
How to confirm the UI used backend mock stream rather than static transcript:
What remains mocked:
What is still not connected:
```

### Codex Acceptance Record

Codex accepted `MYM-27` after local review plus small follow-up fixes:

- `GET /api/rm-workbench/mock-stream` is loopback-only.
- Mock stream data is generated from `api.rm_workbench.mock_data.load_pre_meeting_brief_fixture` and `api.rm_workbench.adapter.map_rm_skill_contract_to_agui_events`.
- Frontend default load path consumes backend mock stream, with static transcript only as visible fallback.
- Product selection resolves through `/api/rm-workbench/pending/resolve`.
- User-facing smoke UI and demo data are Chinese-first.
- Browser smoke confirmed backend-stream source, localized surfaces, product selection, and resolved state.

Verified results:

```text
mock_adapter_check.py -> passed with expected four OK lines
pytest adapter/pending/routes/mock_stream -> 27 passed in 1.81s
npm run build -> passed, vite built in 303ms
browser smoke -> passed
```

Residual risk:

```text
Mock stream sends all SSE events synchronously. This is acceptable for V0 smoke integration; future real Hermes integration should stream progressively.
```

---

## 9. Task 7: Real Hermes Stream Boundary Evaluation

Status: next recommended planning/evaluation slice after `MYM-27`.

This task should not implement the real integration. It should decide where the real integration belongs and produce a precise implementation plan for the next issue.

Reference:

- `docs/ui-ux/rm-workbench-v0-real-hermes-stream-boundary.md`

**Files:**

- Create: `docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`

- [ ] **Step 1: Inspect current stream and pending interaction seams**

Read these files:

```text
api/routes.py
api/streaming.py
api/pending_interactions.py
api/rm_workbench/adapter.py
api/rm_workbench/contracts.py
frontend/src/api/hermesClient.ts
frontend/src/agui/aguiReducer.ts
frontend/src/App.tsx
/Users/hywl/hermes-agent/run_agent.py
/Users/hywl/hermes-agent/skills/
```

The inspection should focus on:

```text
/api/chat/start
/api/chat/stream
api.streaming._run_agent_streaming
clarify_callback
pending interaction notify callback
POST /api/rm-workbench/pending/resolve
GET /api/rm-workbench/mock-stream
```

- [ ] **Step 2: Choose the real stream architecture**

Compare:

```text
A. Preserve existing /api/chat/stream SSE events and add rm_workbench events carrying AG-UI payloads.
B. Rewrite /api/chat/stream to emit AG-UI top-level events.
C. Add a separate real /api/rm-workbench/stream route.
```

Default recommendation should be `A` unless inspection proves a concrete blocker.

- [ ] **Step 3: Define the RM Skill.md and emit tool seam**

The result doc must reject natural-language parsing and define the split between RM Skill.md and the dedicated emit tool:

```text
RM Skill.md guides Agent
  -> Agent calls rm_workbench_emit_contract
  -> api.streaming detects that tool completion
  -> api.rm_workbench.adapter maps contract
  -> rm_workbench SSE event carries AG-UI events
```

- [ ] **Step 4: Define pending interaction resume semantics**

The result doc must answer:

```text
Should resolve require interaction_id?
Should resolve_pending resolve oldest or by id?
Where does the running emit tool block?
How does cancel_stream clear and unblock pending interactions?
What timeout should V0 use?
What exact payload returns to the emit tool?
```

- [ ] **Step 5: Define Memory proposal boundary**

The result doc must keep V0 proposal-first:

```text
CUSTOM name = rm.memory_proposal.created
MemoryDiffCard renders proposals
No automatic writes to Hermes memory, Codex memory, or banking source of truth
```

- [ ] **Step 6: Define CopilotKit boundary**

The result doc must classify CopilotKit as:

```text
use now
reference only
defer
requires runtime takeover
```

The default should remain `reference only` unless there is a narrowly scoped frontend utility that does not introduce CopilotKit runtime state.

- [ ] **Step 7: Write acceptance criteria for the next implementation issue**

The result doc must include tests for:

```text
1. real-stream bridge emits rm_workbench SSE event when rm_workbench_emit_contract submits structured contract
2. frontend reducer can consume rm_workbench payload containing AG-UI events
3. pending interaction resolve by interaction_id resumes waiting entry
4. stream cancel clears pending interaction and unblocks wait
5. no Memory write happens when memory proposals are emitted
6. existing clarify/approval/cancel tests still pass
```

---

## 10. Task 8: CopilotKit Boundary Evaluation

**Files:**

- Create: `docs/ui-ux/rm-workbench-v0-copilotkit-evaluation.md`

- [ ] **Step 1: Evaluate without runtime takeover**

Check whether CopilotKit frontend utilities can consume:

```text
AG-UI standard events
CUSTOM a2ui.surface.messages
CUSTOM rm.pending_interaction.created
```

- [ ] **Step 2: Record capabilities that require CopilotKit runtime**

The output doc must classify each capability as:

```text
use now
reference only
defer
requires runtime takeover
```

- [ ] **Step 3: Keep V0 main path unchanged**

Do not route Hermes runtime through CopilotKit runtime unless this evaluation proves a concrete simplification that outweighs the second runtime state cost.

---

## 11. Acceptance Checklist

V0 implementation is acceptable when:

- [ ] Backend adapter maps the mock RM Skill contract to official AG-UI top-level event types only.
- [ ] A2UI messages are carried via `CUSTOM name = a2ui.surface.messages`.
- [ ] RM pending interaction is separate from clarify.
- [ ] Pending interaction resolve accepts structured JSON payloads.
- [ ] Mock vertical slice runs without touching real customer data.
- [ ] React renderer can display `CustomerProfileCard`, `ProductFitTable`, and `BriefExportPanel`.
- [ ] Product selection returns structured selected product IDs.
- [ ] Frontend smoke workbench can consume backend-generated mock AG-UI/A2UI events.
- [ ] Real Hermes stream boundary evaluation has selected a stream architecture before implementation.
- [ ] Pending interaction resume semantics are defined before real Skill integration.
- [ ] Memory proposal remains proposal-first with no automatic write.
- [ ] Existing clarify and approval tests still pass.
- [ ] No CopilotKit runtime takeover is introduced in V0 without a separate decision.

---

## 12. Verification Commands

Run after backend slices:

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
pytest tests/test_rm_workbench_adapter.py tests/test_pending_interactions.py tests/test_rm_workbench_routes.py -q
pytest tests/test_clarify_unblock.py tests/test_approval_unblock.py tests/test_cancel_interrupt.py -q
```

Run after React slice:

```bash
cd frontend
npm run build
```

---

## 13. Decision Gates Before Real Hermes Stream Implementation

The user should explicitly approve these before any real Hermes stream implementation starts:

1. Whether the real integration preserves existing `/api/chat/stream` SSE event names and carries AG-UI payloads inside `rm_workbench` events.
2. Whether pending interaction resolve must target by `interaction_id`, replacing the current oldest-entry default for production RM interactions.
3. Whether the first real integration can expose `rm_workbench_emit_contract` entirely from hermes-webui before modifying Hermes Agent runtime.
4. Whether `memory_proposals` enter the V0 contract now, with UI proposal rendering only and no automatic write.
5. Whether CopilotKit remains reference-only until the real Hermes stream boundary is verified.

Current recommendation:

```text
Do not start real stream implementation yet.
First complete docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md.
Default architecture: preserve existing /api/chat/stream and carry AG-UI events inside rm_workbench SSE payloads.
Default pending interaction rule: resolve by interaction_id for production RM interactions.
Default Memory rule: proposal-first, no automatic write.
Default CopilotKit rule: reference-only, no runtime takeover.
```
