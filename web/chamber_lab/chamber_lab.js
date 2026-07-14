(function () {
  window.fnpChamberRender = function (targetOrId, scene) {
    const target = typeof targetOrId === 'string' ? document.getElementById(targetOrId) : targetOrId;
    if (!target || !scene || !scene.display_style) return;
    target.innerHTML = '<div style="padding:16px;color:#dff7ff">Loading local Three.js renderer…</div>';
    import('/web/vendor/three.module.min.js').then(function (THREE) {
      const style = scene.display_style;
      const width = Math.max(target.clientWidth, 360), height = Math.max(target.clientHeight, 430);
      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2)); renderer.setSize(width, height); renderer.setClearColor(style.environment === 'warm-studio' ? 0x21160e : style.environment === 'cool-lab' ? 0x081a26 : 0x050916, 1);
      target.innerHTML = ''; target.appendChild(renderer.domElement);
      const camera = new THREE.PerspectiveCamera(42, width / height, .1, 100); camera.position.set(0, 1.3, 8);
      const world = new THREE.Scene(), sculpture = new THREE.Group(); world.add(sculpture);
      const ambient = new THREE.HemisphereLight(0xaeeeff, 0x101020, .9); world.add(ambient);
      const key = new THREE.PointLight(style.color, style.light_intensity * 5, 30, 2); key.position.set(3.4, 3, 4); world.add(key);
      const core = new THREE.Mesh(new THREE.IcosahedronGeometry(1.45, 5), new THREE.MeshPhysicalMaterial({ color: style.color, roughness: style.roughness, metalness: style.metallic, transmission: style.translucency, transparent: true, opacity: Math.max(.24, 1 - style.translucency * .55), thickness: .9, clearcoat: .42 })); sculpture.add(core);
      const layers = scene.semantic_layers || [];
      layers.forEach(function (layer, index) { const tension = ((layer.carriers || []).reduce((sum, item) => sum + Number(item.tension || 0), 0) / Math.max(1, (layer.carriers || []).length)); const ring = new THREE.Mesh(new THREE.TorusGeometry(1.8 + index * .22, .028 + tension * .07, 12, 84), new THREE.MeshStandardMaterial({ color: index % 2 ? 0xfdaa37 : 0x55d9ff, metalness: .38, roughness: .26 })); ring.rotation.set(index * .58, index * .71, index * .37); sculpture.add(ring); });
      const floor = new THREE.Mesh(new THREE.CircleGeometry(5, 96), new THREE.MeshStandardMaterial({ color: 0x06101c, roughness: .5, metalness: .15 })); floor.rotation.x = -Math.PI / 2; floor.position.y = -2.25; world.add(floor);
      let dragging = false, lightDrag = false, previous = { x: 0, y: 0 };
      function pointerDown(event) { dragging = true; lightDrag = event.shiftKey; previous = { x: event.clientX, y: event.clientY }; target.setPointerCapture(event.pointerId); }
      function pointerMove(event) { if (!dragging) return; const dx = event.clientX - previous.x, dy = event.clientY - previous.y; previous = { x: event.clientX, y: event.clientY }; if (lightDrag) { key.position.x += dx * .025; key.position.y = Math.min(6, Math.max(-1, key.position.y - dy * .025)); } else { sculpture.rotation.y += dx * .008; sculpture.rotation.x += dy * .008; } }
      function pointerUp(event) { dragging = false; target.releasePointerCapture(event.pointerId); }
      target.addEventListener('pointerdown', pointerDown); target.addEventListener('pointermove', pointerMove); target.addEventListener('pointerup', pointerUp);
      function render() { renderer.render(world, camera); requestAnimationFrame(render); } render();
      new ResizeObserver(function () { const w = Math.max(target.clientWidth, 360), h = Math.max(target.clientHeight, 430); camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); }).observe(target);
    }).catch(function () { target.innerHTML = '<div style="padding:16px;color:#fff">Local Three.js asset unavailable. Start Panel with <code>--static-dirs web=web</code>.</div>'; });
  };
})();
