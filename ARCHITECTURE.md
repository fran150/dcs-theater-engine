# Architecture

This document is a practical map of the codebase: where things live, what each
folder owns, and which directions dependencies should flow.

For the higher-level campaign design, see
`docs/campaign-system-components.md`.

## Source Layout

### `src/dcs_theater_engine/api`

FastAPI application and HTTP endpoints.

This layer exposes campaign state, runtime controls, theater data, and future
save/load operations to the browser UI or other clients. It should stay thin:
API code can call into campaign, data, persistence, and DCS services, but it
should not own campaign rules.

### `src/dcs_theater_engine/campaign`

Authoritative campaign state and campaign-time behavior.

This package owns mutable campaign data, campaign clock advancement, scenario
initialization, and simulation systems that update campaign state over time. The
campaign layer should not depend on FastAPI, browser UI code, or DCS mission
file details.

### `src/dcs_theater_engine/commander`

Doctrine, AI commander behavior, and command interfaces.

The commander layer decides what a coalition wants to do. It should create
mission intent or mission requests, while leaving validation, scheduling, and
route/package details to the mission planner.

### `src/dcs_theater_engine/data`

Static definitions used to build and interpret campaigns.

This includes theater facts, airbases, aircraft definitions, unit metadata,
map geometry, and DCS type mappings. Data definitions describe reusable facts;
they should not store mutable per-campaign state.

### `src/dcs_theater_engine/dcs`

DCS-specific import and export boundaries.

This layer translates campaign concepts into DCS mission artifacts and imports
results back into campaign-level events or state updates. DCS-specific names,
templates, payload mappings, and result parsing should live here rather than
inside the campaign core.

### `src/dcs_theater_engine/intelligence`

Fog of war and coalition knowledge.

This package should distinguish ground truth from what each side knows,
suspects, or has lost track of. Detection, stale contacts, confidence, and
known-position views belong here.

### `src/dcs_theater_engine/mission`

Campaign mission planning and scheduling.

This layer turns commander intent into executable campaign missions. It should
validate requests, assign assets, schedule missions, track mission lifecycle,
and eventually generate route/package structures used by both simulation and
DCS export.

### `src/dcs_theater_engine/persistence`

Save/load code for campaign state.

Persistence should preserve campaign IDs, current time, mutable state, active
missions, completed missions, and event history. Save format migration can live
here once the on-disk schema starts evolving.

### `src/dcs_theater_engine/reporting`

Debug output, summaries, and future reports.

This package is for human-readable campaign summaries, debug views, after-action
reports, and other reporting helpers. It should consume campaign state rather
than mutate it.

### `src/dcs_theater_engine/ui`

Static browser UI assets served by the API.

The UI talks to the API over HTTP. It should not know Python internals directly.
For now this is a simple static frontend; if it grows into a built frontend, the
same boundary still applies.

### `tests`

Unit, integration, and API tests.

Tests should cover campaign rules close to the campaign layer, API contracts
close to the API layer, and DCS import/export behavior at the boundary where it
is translated.

## Dependency Direction

- `api` may call `campaign`, `data`, `dcs`, `persistence`, and reporting code.
- `ui` talks to `api`, not directly to Python internals.
- `campaign` owns mutable state and runtime behavior.
- `campaign` should not import FastAPI, browser UI code, or DCS mission-file
  details.
- `data` should stay mostly dependency-free and should not depend on mutable
  campaign state.
- `commander` decides intent; `mission` validates, schedules, and shapes that
  intent into campaign missions.
- `dcs` translates campaign concepts to and from DCS-specific artifacts.
- `persistence` serializes campaign state; it should not decide campaign rules.
- `reporting` reads campaign state and events; it should avoid mutating them.

## Current Runtime Model

The campaign runtime is not a frame-precision or second-precision simulation.
It should advance the authoritative campaign clock in coarse steps chosen by the
engine, scenario, or system being updated.

Wall-clock time is only pacing. If a campaign step represents 10 seconds,
several minutes, or a scheduled event window, it is acceptable for that step to
take slightly more or less real time to execute. Campaign outcomes should remain
driven by campaign state, rules, statistics, and random resolution, not by
matching real elapsed seconds exactly.

For example, an abstract BVR encounter between F-16s and MiG-29s should evaluate
conditions such as aircraft, loadout, fuel, readiness, sensors, doctrine,
position, support, and current intelligence, then resolve the result
probabilistically. The engine does not need to simulate that encounter multiple
times per real second.

The server owns the authoritative campaign time, and the UI renders snapshots or
updates from the API. The UI should not drive campaign ticks. It can poll at a
slow cadence, such as every few seconds, or receive updates when the engine has
new state to publish. Full snapshots are useful for initial load, refresh, and
debugging; routine UI refresh should eventually move toward smaller update
messages once the campaign has many entities.

Supported time scales currently are:

- `1x`
- `2x`
- `4x`
- `16x`
- `32x`
- `64x`

Time scale is a campaign pacing control, not a promise that runtime calculations
operate at wall-clock precision.

Campaign systems are update hooks called as campaign time advances. Mission
scheduling, intelligence, repairs, movement, combat, logistics, and future
simulation behavior should grow as systems in the runtime pipeline rather than
as UI-driven turns.
