function safeParseJson(text) {
  if (!text || typeof text !== "string") {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    return null;
  }
}

function renderCanvasFallback(targetId, payload) {
  const container = document.getElementById(targetId);
  if (!container || !payload) return;

  const outputs = payload.outputs || {};
  const nodes = Array.isArray(payload.nodes) ? payload.nodes : [];
  const edges = Array.isArray(payload.edges) ? payload.edges : [];

  if (nodes.length === 0) {
    container.innerHTML = '<div class="placeholder">No graph data yet.</div>';
    container.dataset.summary = "nodes:0,edges:0";
    return;
  }

  const lines = [];
  container.innerHTML = "";

  nodes.forEach(function (node) {
    const value = outputs[node.node_id];
    const valueText = typeof value === "number" ? value.toFixed(6) : "n/a";
    const nodeLine = `<article class="fnp-node"><h4>${escapeHtml(
      node.label || node.node_id
    )}</h4><p><span class="meta">id:</span> ${escapeHtml(
      node.node_id || ""
    )}</p><p><span class="meta">type:</span> ${escapeHtml(
      node.node_type || ""
    )}</p><p><span class="meta">family:</span> ${escapeHtml(
      node.family || ""
    )}</p><p><span class="meta">value:</span> ${valueText}</p></article>`;
    lines.push(nodeLine);
  });

  container.innerHTML = lines.join("");
  container.dataset.summary = `nodes:${nodes.length},edges:${edges.length}`;
}

function createNodeCard(node, valueText) {
  const label = escapeHtml(node.label || node.node_id || "node");
  const nodeId = escapeHtml(node.node_id || "node");
  const value = typeof valueText === "number" ? valueText.toFixed(6) : "n/a";
  return (
    '<article class="fnp-node fnp-node-instance">' +
    "<h4>" +
    label +
    "</h4>" +
    '<p><span class="meta">id:</span> ' +
    nodeId +
    "</p>" +
    '<p><span class="meta">type:</span> ' +
    escapeHtml(node.node_type || "") +
    "</p>" +
    '<p><span class="meta">family:</span> ' +
    escapeHtml(node.family || "") +
    "</p>" +
    '<p><span class="meta">value:</span> ' +
    value +
    "</p>" +
    "</article>"
  );
}

function ensureDragAndDrop(targetId, payload) {
  const container = document.getElementById(targetId);
  if (!container) return;

  const palette = document.querySelector("#fnp-network-designer-palette");
  const state = container.querySelector(".fnp-canvas-state");
  if (!palette || !state) return;

  if (!palette.dataset.ddInit) {
    palette.dataset.ddInit = "1";
    palette.addEventListener("dragover", function (event) {
      event.preventDefault();
      event.stopPropagation();
      palette.classList.remove("drag-over");
      if (container) {
        container.classList.add("drag-target");
      }
    });
  }

  if (container.dataset.ddInit) return;
  container.dataset.ddInit = "1";

  const updateState = function () {
    const parsed = safeParseJson(state.value || "{}") || {};
    container.innerHTML = "";
    const nodes = Array.isArray(parsed.nodes) ? parsed.nodes : [];
    const outputs = (parsed.outputs && typeof parsed.outputs === "object") ? parsed.outputs : {};
    const lines = [];
    nodes.forEach(function (node) {
      const value = outputs[node.node_id];
      lines.push(createNodeCard(node, typeof value === "number" ? value : undefined));
    });
    container.innerHTML = lines.join("");
    if (nodes.length === 0) {
      container.innerHTML = '<div class="placeholder">Drag a preset from the palette to populate the canvas.</div>';
    }
    renderCanvasFallback(targetId, payload);
  };

  const registerPaletteItem = function (item) {
    item.addEventListener("dragstart", function (event) {
      event.dataTransfer.setData(
        "application/json",
        JSON.stringify({
          nodeType: item.dataset.nodeType || "node",
          family: item.dataset.family || "custom_network",
          label: item.dataset.label || item.textContent || "node",
        })
      );
      event.dataTransfer.effectAllowed = "copy";
    });
  };

  Array.prototype.slice.call(palette.querySelectorAll(".fnp-palette-item")).forEach(registerPaletteItem);

  container.addEventListener("dragover", function (event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    container.classList.add("drag-target");
  });

  container.addEventListener("dragleave", function () {
    container.classList.remove("drag-target");
  });

  container.addEventListener("drop", function (event) {
    event.preventDefault();
    container.classList.remove("drag-target");
    const data = safeParseJson(event.dataTransfer.getData("application/json"));
    if (!data) return;

    const parsed = safeParseJson(state.value || "{}") || {};
    const nodes = Array.isArray(parsed.nodes) ? parsed.nodes : [];
    const nodeId = `${data.nodeType}-${nodes.length + 1}`;
    const count = nodes.filter(function (entry) {
      return String(entry.node_id || "").startsWith(`${data.nodeType}-`);
    }).length;
    const nextId = `${data.nodeType}-${count + 1}`;
    nodes.push({
      node_id: nextId,
      family: data.family,
      node_type: data.nodeType,
      label: data.label,
      ports: [
        { port_id: "in", direction: "input", label: "Input", metadata: {} },
        { port_id: "out", direction: "output", label: "Output", metadata: {} },
      ],
      metadata: {},
    });
    parsed.nodes = nodes;
    state.value = JSON.stringify({
      nodes: nodes,
      edges: Array.isArray(parsed.edges) ? parsed.edges : [],
      family: parsed.family || "custom_network",
      outputs: parsed.outputs || {},
      metadata: parsed.metadata || {},
    });
    updateState();
  });
}

function escapeHtml(value) {
  if (value === undefined || value === null) return "";
  const text = String(value);
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

window.fnpNetworkCanvasRender = function (targetId, payload) {
  renderCanvasFallback(targetId, payload);
  ensureDragAndDrop(targetId, payload);
};
