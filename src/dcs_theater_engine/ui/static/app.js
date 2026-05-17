const state = {
  mapData: null,
  leafletMap: null,
  airbaseMarkers: new Map(),
  selectedAirbaseId: null,
};

const elements = {
  theaterName: document.querySelector("#theaterName"),
  airbaseCount: document.querySelector("#airbaseCount"),
  islandCount: document.querySelector("#islandCount"),
  selectedName: document.querySelector("#selectedName"),
  selectedType: document.querySelector("#selectedType"),
  selectedRunways: document.querySelector("#selectedRunways"),
  selectedParking: document.querySelector("#selectedParking"),
  selectedPosition: document.querySelector("#selectedPosition"),
  airbaseList: document.querySelector("#airbaseList"),
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

function fitMap() {
  const latLngs = state.mapData.airbases.map(airbaseLatLng);
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

function selectAirbase(airbaseId, options = { pan: false }) {
  state.selectedAirbaseId = airbaseId;
  const airbase = airbaseById(airbaseId);

  state.airbaseMarkers.forEach((marker, markerAirbaseId) => {
    marker
      .getElement()
      ?.querySelector(".airbase-marker")
      ?.classList.toggle("is-selected", markerAirbaseId === airbaseId);
  });

  document.querySelectorAll(".airbase-row").forEach((node) => {
    node.setAttribute("aria-pressed", String(node.dataset.airbaseId === airbaseId));
  });

  if (!airbase) {
    elements.selectedName.textContent = "None";
    elements.selectedType.textContent = "-";
    elements.selectedRunways.textContent = "-";
    elements.selectedParking.textContent = "-";
    elements.selectedPosition.textContent = "-";
    return;
  }

  elements.selectedName.textContent = airbase.name;
  elements.selectedType.textContent =
    airbase.category.charAt(0).toUpperCase() + airbase.category.slice(1);
  elements.selectedRunways.textContent = runwayText(airbase);
  elements.selectedParking.textContent = `${airbase.parking_slots}`;
  elements.selectedPosition.textContent = formatLatLon(airbase);

  if (options.pan) {
    state.leafletMap.flyTo(airbaseLatLng(airbase), Math.max(state.leafletMap.getZoom(), 10), {
      duration: 0.45,
    });
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

function renderMap() {
  elements.theaterName.textContent = state.mapData.name;
  elements.airbaseCount.textContent = state.mapData.airbases.length;
  elements.islandCount.textContent = state.mapData.islands.length;

  initLeafletMap();
  state.mapData.airbases.forEach(createAirbaseMarker);
  renderAirbaseList();
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

loadMap().catch((error) => {
  elements.theaterName.textContent = "Map unavailable";
  elements.coordinateReadout.textContent = error.message;
});
