function renderCanvasFallback(targetId, payload) {
  const container = document.getElementById(targetId);
  if (!container || !payload) return;
  const lines = [];
  (payload.nodes || []).forEach((node) => {
    lines.push(`• ${node.node_id} (${node.node_type || "node"})`);
  });
  container.dataset.summary = lines.join(" | ");
}

window.fnpNetworkCanvasRender = function (targetId, payload) {
  renderCanvasFallback(targetId, payload);
};
