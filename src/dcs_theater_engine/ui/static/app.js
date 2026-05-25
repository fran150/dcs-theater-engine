const state = {
  mapData: null,
  runtime: null,
  leafletMap: null,
  airbaseMarkers: new Map(),
  carrierGroupMarkers: new Map(),
  selectedAirbaseId: null,
  selectedCarrierGroupId: null,
  runtimePollId: null,
};

// Poll slowly because the engine advances in coarse campaign steps.
const RUNTIME_POLL_INTERVAL_MS = 2000;

const elements = {
  theaterName: document.querySelector("#theaterName"),
  airbaseCount: document.querySelector("#airbaseCount"),
  carrierGroupCount: document.querySelector("#carrierGroupCount"),
  islandCount: document.querySelector("#islandCount"),
  campaignClock: document.querySelector("#campaignClock"),
  timeScaleControls: document.querySelector("#timeScaleControls"),
  selectedName: document.querySelector("#selectedName"),
  selectedCoalition: document.querySelector("#selectedCoalition"),
  selectedType: document.querySelector("#selectedType"),
  selectedRunwaysLabel: document.querySelector("#selectedRunwaysLabel"),
  selectedRunways: document.querySelector("#selectedRunways"),
  selectedParkingLabel: document.querySelector("#selectedParkingLabel"),
  selectedParking: document.querySelector("#selectedParking"),
  selectedDamageLabel: document.querySelector("#selectedDamageLabel"),
  selectedDamage: document.querySelector("#selectedDamage"),
  selectedPosition: document.querySelector("#selectedPosition"),
  airbaseList: document.querySelector("#airbaseList"),
  carrierGroupList: document.querySelector("#carrierGroupList"),
  coordinateReadout: document.querySelector("#coordinateReadout"),
  zoomIn: document.querySelector("#zoomIn"),
  zoomOut: document.querySelector("#zoomOut"),
  fitMap: document.querySelector("#fitMap"),
  mapCanvas: document.querySelector("#mapCanvas"),
};

function clearNode(node) {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
}

function airbaseLatLng(airbase) {
  return [airbase.latitude, airbase.longitude];
}

function carrierGroupLatLng(group) {
  return [group.latitude, group.longitude];
}

function mapBoundsLatLngs() {
  const points = state.mapData.bounds?.outline ?? state.mapData.bounds?.corners ?? [];
  return points.map((point) => [point.latitude, point.longitude]);
}

function formatLatLon(airbase) {
  const ns = airbase.latitude >= 0 ? "N" : "S";
  const ew = airbase.longitude >= 0 ? "E" : "W";
  return `${Math.abs(airbase.latitude).toFixed(4)} ${ns}, ${Math.abs(airbase.longitude).toFixed(4)} ${ew}`;
}

function formatMouseLatLon(latlng) {
  const ns = latlng.lat >= 0 ? "N" : "S";
  const ew = latlng.lng >= 0 ? "E" : "W";
  return `${Math.abs(latlng.lat).toFixed(5)} ${ns}, ${Math.abs(latlng.lng).toFixed(5)} ${ew}`;
}

function runwayText(airbase) {
  if (!airbase.runways.length) {
    return "None";
  }
  return airbase.runways.map((runway) => runway.name).join(", ");
}

function airbaseById(airbaseId) {
  return state.mapData.airbases.find((airbase) => airbase.id === airbaseId);
}

function carrierGroupById(groupId) {
  return state.mapData.carrier_groups.find((group) => group.id === groupId);
}

function runtimeAirbaseByDefinitionId(definitionId) {
  return state.runtime?.airbases.find((airbase) => airbase.definition_id === definitionId);
}

function formatCoalition(coalition) {
  if (!coalition) {
    return "-";
  }
  return coalition.charAt(0).toUpperCase() + coalition.slice(1);
}

function formatDamage(value) {
  if (typeof value !== "number") {
    return "-";
  }
  return `${Math.round(value * 100)}%`;
}

function formatCarrierAirWing(group) {
  const leadShipType = group.ships[0]?.ship_type;
  if (!leadShipType) {
    return "-";
  }

  return `${leadShipType.plane_capacity} aircraft / ${leadShipType.helicopter_capacity} helicopters`;
}

function carrierGroupShortName(group) {
  return group.name
    .replace("Carrier Group ", "")
    .replace("Southeast", "SE")
    .replace("Northwest", "NW");
}

function formatCampaignTime(value) {
  if (!value) {
    return "--:--:--";
  }

  const date = new Date(value);
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: "UTC",
    timeZoneName: "short",
  }).format(date);
}

function fitMap() {
  const latLngs = mapBoundsLatLngs();
  if (!latLngs.length) {
    latLngs.push(...state.mapData.airbases.map(airbaseLatLng));
    latLngs.push(...state.mapData.carrier_groups.map(carrierGroupLatLng));
  }

  state.leafletMap.fitBounds(L.latLngBounds(latLngs), {
    padding: [64, 64],
    maxZoom: 9,
  });
}

function markerHtml(airbase) {
  const shortName = airbase.name
    .replace("Antonio B. Won Pat Intl", "Won Pat Intl")
    .replace("North West Field", "NW Field");

  return `
    <button class="airbase-marker ${airbase.category}" type="button" aria-label="${airbase.name}">
      <span class="marker-halo" aria-hidden="true">
        <span class="marker-core"></span>
      </span>
      <span class="marker-label">${shortName}</span>
    </button>
  `;
}

function createAirbaseMarker(airbase) {
  const icon = L.divIcon({
    className: "airbase-div-icon",
    html: markerHtml(airbase),
    iconSize: [1, 1],
    iconAnchor: [0, 0],
  });

  const marker = L.marker(airbaseLatLng(airbase), {
    icon,
    keyboard: true,
    title: airbase.name,
  }).addTo(state.leafletMap);

  marker.on("click", () => selectAirbase(airbase.id, { pan: false }));
  marker.bindTooltip(
    `${airbase.name}<br>${runwayText(airbase)}<br>${formatLatLon(airbase)}`,
    { direction: "top", opacity: 0.94 },
  );

  state.airbaseMarkers.set(airbase.id, marker);
}

function carrierGroupMarkerHtml(group) {
  return `
    <button class="carrier-marker ${group.coalition}" type="button" aria-label="${group.name}">
      <span class="carrier-symbol" aria-hidden="true"></span>
      <span class="marker-label">${carrierGroupShortName(group)}</span>
    </button>
  `;
}

function createCarrierGroupMarker(group) {
  const icon = L.divIcon({
    className: "carrier-div-icon",
    html: carrierGroupMarkerHtml(group),
    iconSize: [1, 1],
    iconAnchor: [0, 0],
  });

  const marker = L.marker(carrierGroupLatLng(group), {
    icon,
    keyboard: true,
    title: group.name,
  }).addTo(state.leafletMap);

  const leadShip = group.ships[0]?.ship_type.display_name ?? "Carrier";
  marker.on("click", () => selectCarrierGroup(group.id, { pan: false }));
  marker.bindTooltip(
    `${group.name}<br>${leadShip}<br>${formatLatLon(group)}`,
    { direction: "top", opacity: 0.94 },
  );

  state.carrierGroupMarkers.set(group.id, marker);
}

function createMapBoundsOverlay() {
  const latLngs = mapBoundsLatLngs();
  if (!latLngs.length) {
    return;
  }

  L.polygon(latLngs, {
    className: "map-limit-boundary",
    color: "#ff2f2f",
    fill: false,
    interactive: false,
    opacity: 0.95,
    weight: 3,
  }).addTo(state.leafletMap);
}

function renderAirbaseList() {
  clearNode(elements.airbaseList);

  state.mapData.airbases.forEach((airbase) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "airbase-row";
    row.dataset.airbaseId = airbase.id;
    row.setAttribute("aria-pressed", "false");
    row.innerHTML = `
      <span class="category-dot ${airbase.category}" aria-hidden="true"></span>
      <strong>${airbase.name}</strong>
      <span>${airbase.runways.length}</span>
      <small>${formatLatLon(airbase)}</small>
    `;
    row.addEventListener("click", () => selectAirbase(airbase.id, { pan: true }));
    elements.airbaseList.appendChild(row);
  });
}

function renderCarrierGroupList() {
  clearNode(elements.carrierGroupList);

  state.mapData.carrier_groups.forEach((group) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "carrier-row";
    row.dataset.carrierGroupId = group.id;
    row.setAttribute("aria-pressed", "false");
    row.innerHTML = `
      <span class="category-dot ${group.coalition}" aria-hidden="true"></span>
      <strong>${group.name}</strong>
      <span>${group.ships.length}</span>
      <small>${formatLatLon(group)}</small>
    `;
    row.addEventListener("click", () => selectCarrierGroup(group.id, { pan: true }));
    elements.carrierGroupList.appendChild(row);
  });
}

function selectAirbase(airbaseId, options = { pan: false }) {
  state.selectedAirbaseId = airbaseId;
  state.selectedCarrierGroupId = null;
  const airbase = airbaseById(airbaseId);

  state.airbaseMarkers.forEach((marker, markerAirbaseId) => {
    marker
      .getElement()
      ?.querySelector(".airbase-marker")
      ?.classList.toggle("is-selected", markerAirbaseId === airbaseId);
  });
  state.carrierGroupMarkers.forEach((marker) => {
    marker.getElement()?.querySelector(".carrier-marker")?.classList.remove("is-selected");
  });

  document.querySelectorAll(".airbase-row").forEach((node) => {
    node.setAttribute("aria-pressed", String(node.dataset.airbaseId === airbaseId));
  });
  document.querySelectorAll(".carrier-row").forEach((node) => {
    node.setAttribute("aria-pressed", "false");
  });

  if (!airbase) {
    elements.selectedName.textContent = "None";
    elements.selectedCoalition.textContent = "-";
    elements.selectedType.textContent = "-";
    elements.selectedRunwaysLabel.textContent = "Runways";
    elements.selectedRunways.textContent = "-";
    elements.selectedParkingLabel.textContent = "Parking";
    elements.selectedParking.textContent = "-";
    elements.selectedDamageLabel.textContent = "Damage";
    elements.selectedDamage.textContent = "-";
    elements.selectedPosition.textContent = "-";
    return;
  }

  const runtimeAirbase = runtimeAirbaseByDefinitionId(airbase.id);
  elements.selectedName.textContent = airbase.name;
  elements.selectedCoalition.textContent = formatCoalition(runtimeAirbase?.coalition);
  elements.selectedType.textContent =
    airbase.category.charAt(0).toUpperCase() + airbase.category.slice(1);
  elements.selectedRunwaysLabel.textContent = "Runways";
  elements.selectedRunways.textContent = runwayText(airbase);
  elements.selectedParkingLabel.textContent = "Parking";
  elements.selectedParking.textContent = `${airbase.parking_slots}`;
  elements.selectedDamageLabel.textContent = "Damage";
  elements.selectedDamage.textContent = formatDamage(runtimeAirbase?.runway_damage);
  elements.selectedPosition.textContent = formatLatLon(airbase);

  if (options.pan) {
    state.leafletMap.flyTo(airbaseLatLng(airbase), Math.max(state.leafletMap.getZoom(), 10), {
      duration: 0.45,
    });
  }
}

function selectCarrierGroup(groupId, options = { pan: false }) {
  state.selectedAirbaseId = null;
  state.selectedCarrierGroupId = groupId;
  const group = carrierGroupById(groupId);

  state.airbaseMarkers.forEach((marker) => {
    marker.getElement()?.querySelector(".airbase-marker")?.classList.remove("is-selected");
  });
  state.carrierGroupMarkers.forEach((marker, markerGroupId) => {
    marker
      .getElement()
      ?.querySelector(".carrier-marker")
      ?.classList.toggle("is-selected", markerGroupId === groupId);
  });

  document.querySelectorAll(".airbase-row").forEach((node) => {
    node.setAttribute("aria-pressed", "false");
  });
  document.querySelectorAll(".carrier-row").forEach((node) => {
    node.setAttribute("aria-pressed", String(node.dataset.carrierGroupId === groupId));
  });

  if (!group) {
    elements.selectedName.textContent = "None";
    elements.selectedCoalition.textContent = "-";
    elements.selectedType.textContent = "-";
    elements.selectedRunwaysLabel.textContent = "Runways";
    elements.selectedRunways.textContent = "-";
    elements.selectedParkingLabel.textContent = "Parking";
    elements.selectedParking.textContent = "-";
    elements.selectedDamageLabel.textContent = "Damage";
    elements.selectedDamage.textContent = "-";
    elements.selectedPosition.textContent = "-";
    return;
  }

  elements.selectedName.textContent = group.name;
  elements.selectedCoalition.textContent = formatCoalition(group.coalition);
  elements.selectedType.textContent = `${group.country} carrier group`;
  elements.selectedRunwaysLabel.textContent = "Lead";
  elements.selectedRunways.textContent = group.ships[0]?.ship_type.display_name ?? "-";
  elements.selectedParkingLabel.textContent = "Ships";
  elements.selectedParking.textContent = `${group.ships.length}`;
  elements.selectedDamageLabel.textContent = "Air Wing";
  elements.selectedDamage.textContent = formatCarrierAirWing(group);
  elements.selectedPosition.textContent = formatLatLon(group);

  if (options.pan) {
    state.leafletMap.flyTo(
      carrierGroupLatLng(group),
      Math.max(state.leafletMap.getZoom(), 8),
      { duration: 0.45 },
    );
  }
}

function initLeafletMap() {
  if (!window.L) {
    throw new Error("Leaflet failed to load. Check network access to the CDN.");
  }

  state.leafletMap = L.map(elements.mapCanvas, {
    zoomControl: false,
    attributionControl: true,
    preferCanvas: true,
  });

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(state.leafletMap);

  state.leafletMap.on("mousemove", (event) => {
    elements.coordinateReadout.textContent = formatMouseLatLon(event.latlng);
  });

  elements.zoomIn.addEventListener("click", () => state.leafletMap.zoomIn());
  elements.zoomOut.addEventListener("click", () => state.leafletMap.zoomOut());
  elements.fitMap.addEventListener("click", fitMap);
}

function renderTimeScaleControls() {
  clearNode(elements.timeScaleControls);

  [1, 2, 4, 16, 32, 64].forEach((timeScale) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${timeScale}x`;
    button.dataset.timeScale = String(timeScale);
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => setTimeScale(timeScale));
    elements.timeScaleControls.appendChild(button);
  });
}

function renderRuntime() {
  if (!state.runtime) {
    return;
  }

  elements.campaignClock.textContent = formatCampaignTime(state.runtime.campaign_time);
  document.querySelectorAll("[data-time-scale]").forEach((button) => {
    button.setAttribute(
      "aria-pressed",
      String(Number(button.dataset.timeScale) === state.runtime.time_scale),
    );
  });

  if (state.selectedAirbaseId) {
    selectAirbase(state.selectedAirbaseId);
  } else if (state.selectedCarrierGroupId) {
    selectCarrierGroup(state.selectedCarrierGroupId);
  }
}

async function loadRuntime() {
  const response = await fetch("/api/campaign/runtime");
  if (!response.ok) {
    throw new Error(`Runtime request failed: ${response.status}`);
  }

  state.runtime = await response.json();
  renderRuntime();
}

async function setTimeScale(timeScale) {
  const response = await fetch("/api/campaign/runtime/time-scale", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ time_scale: timeScale }),
  });
  if (!response.ok) {
    throw new Error(`Time scale request failed: ${response.status}`);
  }

  state.runtime = await response.json();
  renderRuntime();
}

function renderMap() {
  elements.theaterName.textContent = state.mapData.name;
  elements.airbaseCount.textContent = state.mapData.airbases.length;
  elements.carrierGroupCount.textContent = state.mapData.carrier_groups.length;
  elements.islandCount.textContent = state.mapData.islands.length;

  initLeafletMap();
  createMapBoundsOverlay();
  state.mapData.airbases.forEach(createAirbaseMarker);
  state.mapData.carrier_groups.forEach(createCarrierGroupMarker);
  renderAirbaseList();
  renderCarrierGroupList();
  renderTimeScaleControls();
  fitMap();
  selectAirbase("andersen-afb");
}

async function loadMap() {
  const response = await fetch("/api/theaters/marianas/map");
  if (!response.ok) {
    throw new Error(`Map request failed: ${response.status}`);
  }

  state.mapData = await response.json();
  renderMap();
}

async function init() {
  await Promise.all([loadMap(), loadRuntime()]);
  state.runtimePollId = window.setInterval(() => {
    loadRuntime().catch((error) => {
      elements.coordinateReadout.textContent = error.message;
    });
  }, RUNTIME_POLL_INTERVAL_MS);
}

init().catch((error) => {
  elements.theaterName.textContent = "Map unavailable";
  elements.coordinateReadout.textContent = error.message;
});
