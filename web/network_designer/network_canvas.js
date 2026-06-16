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
};
