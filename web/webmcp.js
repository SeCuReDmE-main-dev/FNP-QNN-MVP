(async () => {
  const api = document.modelContext;
  if (!api || typeof api.registerTool !== "function") return;
  const response = await fetch("/webmcp/manifest", { credentials: "same-origin" });
  if (!response.ok) return;
  const manifest = await response.json();
  const root = document.documentElement;
  Object.entries((manifest.product.theme && manifest.product.theme.tokens) || {}).forEach(([key, value]) => root.style.setProperty(`--securedme-${key}`, value));
  root.dataset.securedmeProduct = manifest.product.slug;
  for (const descriptor of manifest.tools) {
    api.registerTool({ name: descriptor.name, description: descriptor.description, inputSchema: descriptor.inputSchema,
      execute: async (args = {}, context = {}) => {
        const result = await fetch("/webmcp/invoke", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-SecuredMe-WebMCP": "1" }, body: JSON.stringify({ name: descriptor.name, arguments: args, nonce: context.nonce }), signal: context.signal });
        const payload = await result.json();
        if (!result.ok) throw new Error(payload.error_code || "WEBMCP_REJECTED");
        return payload;
      } });
  }
})();
