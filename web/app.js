const API_BASE = window.location.origin;
const MODALITIES = ["audio", "video", "text", "stimuli"];

function showToast(message, kind = "info", timeoutMs = 3200) {
  const region = document.getElementById("toast-region");
  if (!region) return;
  const node = document.createElement("div");
  node.className = `toast ${kind}`;
  node.textContent = String(message);
  region.appendChild(node);
  requestAnimationFrame(() => node.classList.add("show"));
  window.setTimeout(() => {
    node.classList.remove("show");
    window.setTimeout(() => node.remove(), 220);
  }, timeoutMs);
}

const demoPayload = {
  label: 1,
  epochs: 12,
  run_qnn: true,
  memories: [
    {
      modality: "audio",
      starting_time: 0.0,
      ending_time: 1.4,
      value: 0.73,
      label: "rhythm",
      source: "dashboard-demo",
      payload_ref: "audio-001"
    },
    {
      modality: "video",
      starting_time: 0.8,
      ending_time: 2.2,
      value: 0.61,
      label: "motion",
      source: "dashboard-demo",
      payload_ref: "video-001"
    },
    {
      modality: "text",
      starting_time: 1.6,
      ending_time: 2.9,
      value: 0.54,
      label: "caption",
      source: "dashboard-demo",
      payload_ref: "text-001"
    },
    {
      modality: "stimuli",
      starting_time: 2.4,
      ending_time: 3.0,
      value: 0.82,
      label: "trigger",
      source: "dashboard-demo",
      payload_ref: "stimuli-001"
    }
  ]
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function formatNumber(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

function setPill(selector, text, kind = "muted") {
  const node = $(selector);
  if (!node) return;
  node.textContent = text;
  node.className = `pill ${kind}`;
}

function setText(selector, text) {
  const node = $(selector);
  if (node) node.textContent = text;
}

function setPanelState(node, hasData) {
  if (!node) return;
  node.classList.toggle("has-data", hasData);
  node.classList.toggle("empty-state", !hasData);
}

function setSkeleton(selectors, on) {
  for (const sel of selectors) {
    const node = document.querySelector(sel);
    if (!node) continue;
    node.classList.toggle("skeleton", !!on);
  }
}

function prettyJson(data) {
  return JSON.stringify(data ?? {}, null, 2);
}

function writeJson(data) {
  $("#json-output").textContent = prettyJson(data);
}

function writeCommand(text, data) {
  const suffix = data === undefined ? "" : `\n\n${prettyJson(data)}`;
  $("#command-output").textContent = `${new Date().toLocaleTimeString()}  ${text}${suffix}`;
}

function resetPayload() {
  $("#payload-editor").value = prettyJson(demoPayload);
  $("#label-input").value = String(demoPayload.label);
  $("#epochs-input").value = String(demoPayload.epochs);
  $("#run-qnn-input").checked = demoPayload.run_qnn;
}

function parseEditorPayload() {
  const raw = $("#payload-editor").value.trim();
  const payload = raw ? JSON.parse(raw) : {};
  payload.label = Number($("#label-input").value || payload.label || 1);
  payload.epochs = Number.parseInt($("#epochs-input").value || payload.epochs || 12, 10);
  payload.run_qnn = $("#run-qnn-input").checked;
  return payload;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (_error) {
    data = { raw: text };
  }
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : prettyJson(data.detail || data);
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }
  return data;
}

async function refreshStatus() {
  const heroMetrics = ["#metric-api-status", "#metric-bridge", "#metric-backend", "#metric-phi"];
  setPill("#system-indicator", "loading", "busy");
  setSkeleton(heroMetrics, true);
  try {
    const [health, runtime, candidates] = await Promise.all([
      apiRequest("/health"),
      apiRequest("/cerebrum/runtime/status"),
      apiRequest("/qnn/candidates")
    ]);

    setText("#metric-api-status", health.status || "ok");
    setText("#metric-bridge", runtime.bridge || runtime.status || "—");
    setText("#metric-backend", runtime.qnn_backend || health.qnn_backend || "—");
    setText("#metric-phi", formatNumber(health.golden_ratio, 12));
    setSkeleton(heroMetrics, false);
    setPill("#system-indicator", "online", "ok");
    renderCandidates(candidates.candidates || []);
    writeCommand("Status refreshed.", { health, runtime, candidates });
    showToast("Status refreshed.", "success");
  } catch (error) {
    setSkeleton(heroMetrics, false);
    setPill("#system-indicator", "offline", "error");
    writeCommand(`Status refresh failed: ${error.message}`);
    showToast(error.message || "Request failed.", "error");
  }
}

function renderCandidates(candidates) {
  const target = $("#candidate-list");
  target.innerHTML = "";
  if (!candidates.length) {
    target.innerHTML = '<span class="chip">no candidates</span>';
    return;
  }
  for (const candidate of candidates) {
    const chip = document.createElement("span");
    chip.className = `chip ${candidate.available ? "ok" : ""}`;
    chip.textContent = `${candidate.name} · ${candidate.available ? "available" : "optional"}`;
    chip.title = candidate.notes || candidate.backend || "";
    target.appendChild(chip);
  }
}

async function runSimulation() {
  setPill("#run-indicator", "running", "busy");
  try {
    const payload = parseEditorPayload();
    const response = await apiRequest("/cerebrum/runtime/run", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    renderRuntime(response.runtime);
    writeJson(response);
    writeCommand("Simulation completed.", {
      events: response.runtime?.events?.length ?? 0,
      pairs: response.runtime?.pairs?.length ?? 0,
      feature_dimension: response.runtime?.feature_dimension,
      qnn_backend: response.runtime?.qnn_result?.backend || "not-run"
    });
    setPill("#run-indicator", "complete", "ok");
    showToast("Simulation completed.", "success");
  } catch (error) {
    setPill("#run-indicator", "error", "error");
    writeCommand(`Simulation failed: ${error.message}`);
    showToast(error.message || "Request failed.", "error");
  }
}

async function encodePayload() {
  setPill("#run-indicator", "encoding", "busy");
  try {
    const payload = parseEditorPayload();
    const observations = payload.observations || payload.memories || payload.events || [];
    const response = await apiRequest("/cerebrum/encode", {
      method: "POST",
      body: JSON.stringify({ observations })
    });
    renderEncoded(response.encoded);
    writeJson(response);
    writeCommand("Encoding completed.", response.encoded?.summary || {});
    setPill("#run-indicator", "encoded", "ok");
    showToast("Encoding completed.", "success");
  } catch (error) {
    setPill("#run-indicator", "error", "error");
    writeCommand(`Encoding failed: ${error.message}`);
    showToast(error.message || "Request failed.", "error");
  }
}

async function runQnnSmoke() {
  setPill("#run-indicator", "qnn smoke", "busy");
  try {
    const payload = parseEditorPayload();
    const observations = payload.observations || payload.memories || payload.events || [];
    const response = await apiRequest("/qnn/smoke", {
      method: "POST",
      body: JSON.stringify({
        samples: observations.length ? [observations, observations] : undefined,
        labels: observations.length ? [0, 1] : undefined,
        epochs: payload.epochs,
        test_size: 0
      })
    });
    renderBenchmark(response.benchmark || []);
    if (response.result?.bundle) {
      renderEncoded({
        feature_vector: response.result.feature_vector,
        feature_dimension: response.result.feature_dimension,
        transition_matrix: response.result.bundle.transition_matrix,
        summary: response.result.bundle.summary
      });
    }
    setText("#metric-feature-dim", formatNumber(response.result?.feature_dimension, 0));
    setText("#metric-probability", formatNumber(response.result?.predicted_probability, 4));
    writeJson(response);
    writeCommand("QNN smoke completed.", response.result || {});
    setPill("#run-indicator", "qnn complete", "ok");
    showToast("QNN smoke completed.", "success");
  } catch (error) {
    setPill("#run-indicator", "error", "error");
    writeCommand(`QNN smoke failed: ${error.message}`);
    showToast(error.message || "Request failed.", "error");
  }
}

async function runLegacyDemo() {
  setPill("#run-indicator", "legacy demo", "busy");
  try {
    const response = await apiRequest("/cerebrum/runtime/legacy-demo");
    renderRuntime(response.runtime);
    writeJson(response);
    writeCommand("Legacy fixture replay completed.", {
      legacy_cerebrum_path_exists: response.runtime?.legacy_cerebrum_path_exists,
      events: response.runtime?.events?.length ?? 0,
      pairs: response.runtime?.pairs?.length ?? 0
    });
    setPill("#run-indicator", "legacy complete", "ok");
    showToast("Legacy fixture replay completed.", "success");
  } catch (error) {
    setPill("#run-indicator", "error", "error");
    writeCommand(`Legacy demo failed: ${error.message}`);
    showToast(error.message || "Request failed.", "error");
  }
}

async function runCommand(commandName) {
  try {
    const body = commandName === "cerebrum-runtime-run"
      ? { payload: parseEditorPayload() }
      : commandName === "qnn-smoke"
        ? { epochs: Number.parseInt($("#epochs-input").value || "12", 10), test_size: 0 }
        : {};
    const response = await apiRequest(`/commands/${commandName}`, {
      method: "POST",
      body: JSON.stringify(body)
    });
    writeCommand(response.output || `${commandName} complete.`, response.data || response);
    writeJson(response);
    if (commandName === "cerebrum-runtime-run" && response.data) {
      renderRuntime(response.data);
    }
    showToast(`${commandName} complete.`, "success");
  } catch (error) {
    writeCommand(`${commandName} failed: ${error.message}`);
    showToast(error.message || "Request failed.", "error");
  }
}

function renderRuntime(runtime = {}) {
  const events = runtime.events || [];
  const pairs = runtime.pairs || [];
  setText("#metric-events", formatNumber(events.length, 0));
  setText("#metric-pairs", formatNumber(pairs.length, 0));
  setText("#metric-feature-dim", formatNumber(runtime.feature_dimension, 0));
  setText("#metric-probability", formatNumber(runtime.qnn_result?.predicted_probability, 4));

  renderTimeline(events);
  renderPairs(pairs);
  renderFeatureVector(runtime.feature_vector || []);
  renderTransitionMatrix(runtime.bundle?.transition_matrix || []);
  renderBenchmark(runtime.benchmark || []);
}

function renderEncoded(encoded = {}) {
  setText("#metric-events", formatNumber(encoded.sequence_length || encoded.summary?.sequence_length, 0));
  setText("#metric-pairs", "—");
  setText("#metric-feature-dim", formatNumber(encoded.feature_dimension, 0));
  setText("#metric-probability", "—");
  renderFeatureVector(encoded.feature_vector || []);
  renderTransitionMatrix(encoded.transition_matrix || []);
}

function renderTimeline(events) {
  const target = $("#timeline");
  target.innerHTML = "";
  setPanelState(target, events.length > 0);
  if (!events.length) {
    target.textContent = "Run the simulator to render event intervals.";
    return;
  }
  const maxEnd = Math.max(1, ...events.map((event) => Number(event.ending_time ?? event.timestamp ?? 0)));
  for (const event of events) {
    const start = Number(event.starting_time ?? event.timestamp ?? 0);
    const end = Number(event.ending_time ?? start + 1);
    const width = Math.max(3, ((end - start) / maxEnd) * 100);
    const left = Math.max(0, (start / maxEnd) * 100);

    const row = document.createElement("div");
    row.className = "timeline-row";
    row.innerHTML = `
      <span>${escapeHtml(event.modality || "event")}</span>
      <span class="timeline-track"><span class="timeline-segment" style="left:${left}%;width:${Math.min(width, 100 - left)}%"></span></span>
      <span>${formatNumber(start, 2)}→${formatNumber(end, 2)}</span>
    `;
    target.appendChild(row);
  }
}

function renderFeatureVector(vector) {
  const target = $("#feature-vector");
  target.innerHTML = "";
  setPanelState(target, vector.length > 0);
  if (!vector.length) {
    target.textContent = "No vector yet.";
    return;
  }
  const maxAbs = Math.max(1e-9, ...vector.map((value) => Math.abs(Number(value))));
  vector.slice(0, 64).forEach((value, index) => {
    const numeric = Number(value);
    const percent = Math.max(1, Math.min(100, (Math.abs(numeric) / maxAbs) * 100));
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <span>f${index}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${percent}%"></span></span>
      <span>${formatNumber(numeric, 3)}</span>
    `;
    target.appendChild(row);
  });
}

function renderTransitionMatrix(matrix) {
  const target = $("#transition-matrix");
  target.innerHTML = "";
  const hasData = Array.isArray(matrix) && matrix.length > 0;
  setPanelState(target, hasData);
  if (!hasData) {
    target.textContent = "No matrix yet.";
    return;
  }

  target.appendChild(labelCell(""));
  MODALITIES.forEach((modality) => target.appendChild(labelCell(modality)));
  matrix.slice(0, MODALITIES.length).forEach((row, rowIndex) => {
    target.appendChild(labelCell(MODALITIES[rowIndex] || `m${rowIndex}`));
    row.slice(0, MODALITIES.length).forEach((value) => {
      const cell = document.createElement("span");
      const alpha = Math.max(0.06, Math.min(0.42, Number(value) * 0.7 + 0.06));
      cell.className = "matrix-cell";
      cell.style.background = `rgba(112, 225, 245, ${alpha})`;
      cell.textContent = formatNumber(value, 2);
      target.appendChild(cell);
    });
  });
}

function labelCell(text) {
  const cell = document.createElement("span");
  cell.className = "matrix-label";
  cell.textContent = text;
  return cell;
}

function renderPairs(pairs) {
  const target = $("#pairs-table");
  target.innerHTML = "";
  setPanelState(target, pairs.length > 0);
  if (!pairs.length) {
    target.textContent = "No pairs yet.";
    return;
  }
  const table = document.createElement("table");
  table.innerHTML = `
    <thead>
      <tr><th>Direction</th><th>Source</th><th>Target</th><th>Overlap</th></tr>
    </thead>
    <tbody></tbody>
  `;
  const body = table.querySelector("tbody");
  for (const pair of pairs.slice(0, 14)) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(pair.direction || "—")}</td>
      <td>${escapeHtml(pair.source_modality || "—")} @ ${formatNumber(pair.timestamp1, 2)}</td>
      <td>${escapeHtml(pair.target_modality || "—")} @ ${formatNumber(pair.timestamp2, 2)}</td>
      <td>${formatNumber(pair.overlap_score, 3)}</td>
    `;
    body.appendChild(row);
  }
  target.appendChild(table);
}

function renderBenchmark(benchmark) {
  const target = $("#benchmark");
  target.innerHTML = "";
  setPanelState(target, benchmark.length > 0);
  if (!benchmark.length) {
    target.textContent = "No benchmark yet.";
    return;
  }
  benchmark.forEach((item) => {
    const card = document.createElement("article");
    card.className = "benchmark-card";
    card.innerHTML = `
      <strong>${escapeHtml(item.candidate || item.backend || "candidate")}</strong>
      <span>${escapeHtml(item.backend || "backend unknown")} · ${item.available ? "available" : "not available"}</span>
      <span>train=${formatNumber(item.train_accuracy, 3)} test=${formatNumber(item.test_accuracy, 3)} prob=${formatNumber(item.predicted_probability, 3)}</span>
      <span>${escapeHtml(item.notes || "")}</span>
    `;
    target.appendChild(card);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindUi() {
  $("#refresh-status").addEventListener("click", refreshStatus);
  $("#reset-demo").addEventListener("click", resetPayload);
  $("#run-simulation").addEventListener("click", runSimulation);
  $("#encode-payload").addEventListener("click", encodePayload);
  $("#qnn-smoke").addEventListener("click", runQnnSmoke);
  $("#legacy-demo").addEventListener("click", runLegacyDemo);
  $$("[data-command]").forEach((button) => {
    button.addEventListener("click", () => runCommand(button.dataset.command));
  });
}

document.addEventListener("DOMContentLoaded", () => {
  resetPayload();
  bindUi();
  refreshStatus();
});
