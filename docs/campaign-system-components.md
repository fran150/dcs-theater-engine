# Campaign System Components

This document defines the high-level components of the DCS dynamic campaign
engine. The guiding idea is that the campaign engine is the source of truth,
while DCS is used to render a focused flyable mission based on the current
campaign state.

The system should support a full loop:

1. Maintain persistent campaign state.
2. Generate campaign-level missions for both sides.
3. Simulate the campaign outside DCS.
4. Let the player select or receive a mission.
5. Generate a tailored DCS mission from that campaign mission.
6. Import the DCS result.
7. Update the persistent campaign state.

## Design Principles

- The external campaign engine owns the authoritative world state.
- DCS missions are temporary playable snapshots of the campaign.
- Only units relevant to the player mission should be spawned in DCS.
- Units that appear in DCS should map back to persistent campaign entities when
  possible.
- Campaign simulation should continue outside DCS, even when no player mission
  is being flown.
- The first implementation should be simple but built around extensible
  boundaries.

## Components

### Campaign Core

The campaign core is the authoritative runtime data model for the war. It stores
what is currently true in this campaign instance. It should reference static
data definitions rather than duplicating them.

Responsibilities:

- Store the campaign clock and current campaign phase.
- Represent coalitions, factions, and command ownership.
- Represent campaign instances of theaters, regions, airbases, FARPs,
  objectives, depots, ports, factories, SAM sites, radar sites, and other
  strategic locations.
- Represent units, formations, squadrons, aircraft inventories, ground forces,
  naval groups, and support assets.
- Track readiness, supply, fuel, ammunition, damage, repair state, morale, and
  availability where relevant.
- Provide stable IDs for all campaign entities.
- Expose clean APIs for reading and mutating campaign state.

Examples of campaign core data:

- Blue Squadron 1 currently has 10 available F/A-18C aircraft.
- Kutaisi runway is damaged until a specific campaign time.
- A red SAM battery is currently deployed near a known objective.
- A strike mission is scheduled to launch at 14:30.
- Blue intelligence last detected an enemy flight at a specific location.

Phase 1 scope:

- Basic campaign clock.
- Basic coalitions.
- Airbases and objectives.
- Squadrons and aircraft counts.
- Simple ground or strategic target entities.
- Stable campaign IDs.

### Persistence And Save System

The persistence layer stores and restores the campaign.

Responsibilities:

- Save campaign state to disk.
- Load campaign state from disk.
- Preserve all campaign entity IDs.
- Store current time, active missions, completed missions, losses, damage, and
  event history.
- Support versioning or migration once save formats begin to evolve.

Phase 1 scope:

- Human-readable JSON or YAML save files.
- Save and load the full campaign state.
- Preserve enough history to debug what happened.

### Data Definition Layer

The data definition layer contains reusable static definitions used to build and
interpret a campaign. It stores facts about unit types, DCS mappings, and the
theater that are not themselves the mutable state of a specific campaign run.

Responsibilities:

- Define aircraft types, ground unit types, ship types, weapons, sensors, and
  mission roles.
- Define unit templates and package templates.
- Define theater metadata such as map boundaries, coordinate systems, land and
  sea polygons, roads, rivers, bridges, valleys, mountain regions, terrain
  restrictions, flight corridors, route points, airbases, ports, objectives,
  regions, and named areas.
- Map campaign abstractions to DCS-specific unit names, payloads, liveries, and
  mission editor objects.
- Allow new campaigns and theaters to be created without changing core code.

Examples of data definition data:

- The Caucasus theater has specific land and sea polygons.
- This road connects two towns and crosses this bridge.
- This valley is a known low-level flight corridor.
- This DCS aircraft type name corresponds to the campaign aircraft type
  `F/A-18C`.
- This airbase has these parking spots, runways, taxi constraints, and
  approximate approach/departure routes.

The campaign core can then create a campaign instance that references these
definitions and adds mutable state on top of them.

Phase 1 scope:

- Small hand-authored data files for one tiny test theater.
- Aircraft type definitions.
- Airbase and objective definitions.
- Basic theater metadata, including land and sea areas.
- Basic DCS unit mapping data.

### Campaign Simulation

The campaign simulation advances the authoritative state outside DCS.

Responsibilities:

- Advance campaign time.
- Execute campaign-level missions.
- Move units and mission packages along planned routes.
- Resolve abstract air-to-air, air-to-ground, and air-defense interactions.
- Apply losses, damage, repairs, fuel usage, supply changes, and mission
  outcomes.
- Emit campaign events for the UI and save history.

Phase 1 scope:

- Time ticks.
- Simple movement along routes.
- Simple strike resolution.
- Simple intercept or CAP engagement resolution.
- Basic target damage and aircraft losses.

### Intelligence And Fog Of War

The intelligence system controls what each side knows, suspects, or has lost
track of.

Responsibilities:

- Distinguish ground truth from known information.
- Maintain separate intelligence views per coalition.
- Track last known positions, confidence, detection time, source, and staleness.
- Feed mission planning with imperfect information.
- Drive fog-of-war presentation in the UI.

Phase 1 scope:

- Known vs unknown entities.
- Last known position.
- Simple confidence value.
- Simple detection updates from radar sites, recon, or proximity.

### Event System

The event system records meaningful changes in the campaign.

Responsibilities:

- Provide a common event language for simulation, mission generation, DCS result
  import, and UI updates.
- Record what happened and when.
- Support debugging and campaign history playback.
- Allow the UI to show a timeline of important actions.

Example events:

- `MissionPlanned`
- `MissionLaunched`
- `UnitDetected`
- `UnitMoved`
- `AirbaseDamaged`
- `AircraftDestroyed`
- `ObjectiveStruck`
- `MissionCompleted`
- `IntelUpdated`

Phase 1 scope:

- Append-only event log.
- Basic event types for missions, movement, detection, losses, and damage.

### Doctrine And Scriptable AI Commander

The doctrine and commander layer decides what each side wants to do. It should
support built-in doctrine rules, but it should also be scriptable so users and
the community can contribute strategic and tactical behavior without modifying
the campaign engine itself.

Responsibilities:

- Evaluate strategic priorities.
- Choose objectives.
- Decide when to attack, defend, intercept, conserve forces, or reinforce.
- Generate requests for campaign-level missions and follow-up actions.
- Model different behavior per coalition, faction, or campaign scenario.
- Run user-provided decision scripts for strategic and tactical choices.
- Expose safe APIs that let scripts inspect only the information known to their
  coalition, not omniscient ground truth unless explicitly running in a debug or
  scenario-author mode.
- Allow scripts to request actions such as recon, strike, CAP, intercept,
  reinforcement, repair priority changes, or follow-up battle damage assessment.
- Validate script outputs before they become missions, so scripts cannot assign
  unavailable aircraft, exceed range limits, or use unknown target information.

Example scripted behaviors:

- Send a recon flight to assess airbase damage after a strike.
- Frag a second strike if battle damage assessment suggests the first strike did
  not achieve enough damage.
- Increase CAP coverage near an airbase after repeated enemy attacks.
- Hold aircraft in reserve when readiness or supply is low.
- Redirect strike priority after a newly detected SAM site threatens planned
  routes.

The commander should think in terms of intent and requests. It should not need
to manually build every route, timing detail, or package assignment. That is the
mission planner's job.

Phase 1 scope:

- Simple rule-based commander.
- Basic scripting extension point or interface design.
- Objective priorities.
- Basic mission requests for strike, CAP, and intercept missions.

### Campaign Mission Planner

The campaign mission planner turns commander intent into executable campaign
missions. It owns mission generation, scheduling, coordination, cancellation,
and replanning because those concerns are tightly linked.

Responsibilities:

- Build the frag order or mission list for all relevant units.
- Assign aircraft, flights, packages, escorts, interceptors, and support assets.
- Generate mission routes, timing, target assignments, and expected threats.
- Respect aircraft availability, range, readiness, intelligence, doctrine, and
  objective priority.
- Track mission lifecycle state.
- Launch missions when their scheduled time arrives.
- Cancel, delay, or retask missions when campaign conditions change.
- Replan missions when critical assumptions change, such as a target being
  captured, destroyed, repaired, abandoned, or discovered to be different from
  expected intelligence.
- Coordinate mission timing so packages and opposing missions can interact.
- Produce missions that can be simulated abstractly or converted into DCS
  flyable missions.

Phase 1 scope:

- Generate simple strike, CAP, and intercept missions.
- Assign flights from available squadrons.
- Produce basic routes and scheduled times.
- Generate missions for both coalitions.
- Planned, active, completed, and cancelled states.
- Launch by campaign time.
- Basic cancellation and replanning when a target is no longer valid.
- Basic mission completion handling.

### DCS Mission Generator

The DCS mission generator converts one selected campaign mission into a flyable
DCS mission. It also generates the DCS-side trigger and scripting logic needed
for dynamic spawning during that mission, because the external campaign engine
cannot spawn units after the mission has already started inside DCS.

Responsibilities:

- Generate the player package and briefing.
- Place relevant targets, friendly forces, threats, and support assets.
- Include only units needed for the player mission.
- Decide which units are pre-spawned, trigger-spawned, abstract-only, or omitted
  from the DCS mission.
- Generate DCS triggers or mission scripts for interceptors, bombers,
  reinforcements, SAMs, or other units that should appear only when relevant.
- Spawn units at plausible locations, headings, altitudes, speeds, and fuel
  states based on campaign context.
- Avoid making dynamic spawns feel random or unfair.
- Attach campaign IDs to generated groups and units where possible.
- Add scripts or triggers needed to report mission results.

Phase 1 scope:

- Generate a basic flyable strike mission.
- Place the player aircraft, target, nearby defenses, and one possible enemy
  response.
- Generate one simple distance-based or time-based dynamic spawn trigger.
- Include campaign IDs in generated metadata.
- Add a simple result-reporting script hook.

### DCS Result Importer

The DCS result importer reconciles a completed DCS mission back into the
campaign state.

Responsibilities:

- Read mission result files or DCS event logs.
- Identify destroyed, damaged, surviving, or expended campaign-linked entities.
- Update aircraft inventories, unit status, target damage, mission success, and
  campaign time.
- Record events for everything that should affect future simulation.
- Handle cases where DCS spawned temporary units that do not correspond to
  persistent campaign entities.

Phase 1 scope:

- Import mission success or failure.
- Import destroyed campaign-linked units.
- Import player aircraft survived or lost.
- Apply target damage.
- Append result events to campaign history.

### UI And Campaign Viewer

The UI lets the player inspect the campaign, understand the war, and choose or
receive missions.

Responsibilities:

- Show a campaign map.
- Display airbases, objectives, known units, contacts, and mission routes.
- Apply fog of war based on the selected coalition's intelligence view.
- Show order of battle, aircraft availability, unit readiness, target status,
  and logistics summaries.
- Show planned, active, and completed missions.
- Show event timeline and campaign history.
- Present mission briefings and allow the player to generate or launch a DCS
  mission.

Phase 1 scope:

- Map view.
- Airbases and objectives.
- Known units and contacts.
- Current mission list.
- Basic OOB panel.
- Event timeline.
- Selected mission briefing.

### Reporting And Debug Tools

Debugging tools make the campaign understandable while the simulation is still
evolving.

Responsibilities:

- Inspect raw campaign state.
- Show why missions were generated.
- Show why outcomes happened.
- Compare ground truth against each coalition's intelligence view.
- Replay recent events.
- Validate generated DCS mission data.

Phase 1 scope:

- Simple debug views or command-line reports.
- Event log inspection.
- Ground truth vs known-state toggle for development.

## Phase 1 Target

Phase 1 should produce a small but complete vertical slice:

- A tiny theater with two airbases per side.
- A few squadrons with limited aircraft inventories.
- A small set of strategic objectives.
- Basic fog of war.
- Campaign-level strike, CAP, and intercept missions.
- Abstract simulation that advances time and resolves simple outcomes.
- A UI map showing units, objectives, missions, and events.
- A DCS mission generator that creates one flyable strike mission.
- A DCS result importer that updates the campaign after the mission.

The desired outcome is not a sophisticated campaign yet. The desired outcome is
a working loop that proves the architecture.
