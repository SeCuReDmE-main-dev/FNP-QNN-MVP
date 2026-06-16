# DESIGN.md

## Purpose

This file is the practical design and repair guide for the FNP-QNN Panel UI.

The current Panel exists and runs as a local operator dashboard, but it needs stronger visual hierarchy, cleaner asset usage, better cropping/framing rules, and a more coherent layout before the future Network Designer is added.

Use this document when improving:

```text
panel_app.py
assets/*
assets/generated/*
future ui/network_designer.py
future assets/network_designer/*
reports and public-facing screenshots
```

The goal is not to preserve every current Panel decision. The goal is to use the real assets already present in `/assets` to rebuild the Panel into a cleaner, more professional FNP-QNN research control room.

---

## Product Boundary

FNP-QNN is an alpha-local, non-clinical research simulator.

Every screen must visually and textually reinforce this boundary:

```text
local research simulator
alpha-local
non-clinical
fixture-backed where applicable
deterministic fallback where applicable
optional candidate lanes
```

Do not design the Panel like:

```text
clinical dashboard
hospital product
medical triage UI
emergency console
production safety system
diagnostic system
```

The design should feel like a research cockpit, not a medical product.

Recommended boundary copy:

```text
Alpha-local research simulator. Not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software. Results are local simulation evidence only.
```

---

## Verified Asset Inventory

The current `panel_app.py` references assets from two locations:

```text
assets/
assets/generated/
```

### Root assets verified or referenced

```text
assets/logo1.png
assets/mascoote qbit.png
assets/qbits stancil.png
assets/mural fnp-qnn.png
assets/vector template.png
assets/template tasse bleu.png
assets/tshirt vert template.png
```

### Generated UI assets referenced by Panel

```text
assets/generated/logo-ui-thumb.png
assets/generated/qbit-stencil-ui-thumb.png
assets/generated/qbit-stencil-main.png
assets/generated/qbit-stencil-lab.png
assets/generated/qbit-stencil-orbit.png
assets/generated/qbit-stencil-guide.png
assets/generated/qbit-stencil-avatar-strip.png
assets/generated/atom-normalized-dark.png
assets/generated/atom-back-logo-dark.png
assets/generated/vector-01-brain-network.png
assets/generated/vector-02-orbit-head.png
assets/generated/vector-03-circuit-brain.png
assets/generated/vector-04-wave-brain.png
assets/generated/vector-05-cube-research.png
assets/generated/mural-ui-thumb.png
assets/generated/mug-blue-ui-thumb.png
assets/generated/shirt-green-ui-thumb.png
```

---

## Asset Roles

### `logo1.png`

Role: primary brand source.

Use for:

```text
hero brand identity
about/cover sections
larger landing visual
```

Do not overuse it in small cards. Use generated thumbnails for UI.

---

### `mascoote qbit.png`

Role: friendly mascot source.

Use for:

```text
onboarding
guide/help states
empty states
future assistant hints
```

Avoid using the mascot as the main dashboard logo if it reduces professional clarity.

---

### `qbits stancil.png` and generated stencil assets

Role: quantum identity marker.

Use for:

```text
QNN candidate sections
Network Designer hero
sidebar guide image
empty-state illustration
```

Preferred generated versions:

```text
qbit-stencil-main.png
qbit-stencil-lab.png
qbit-stencil-orbit.png
qbit-stencil-guide.png
qbit-stencil-avatar-strip.png
```

---

### `atom-normalized-dark.png`

Role: compact application mark.

Use for:

```text
FastListTemplate logo
header identity
small UI mark
```

This is the best current asset for the top application shell.

---

### Vector assets

The vector assets are the strongest current functional UI assets.

```text
vector-01-brain-network.png  -> memory stream / graph / encoding
vector-02-orbit-head.png     -> QNN candidate / neural orbit / run path
vector-03-circuit-brain.png  -> logic / circuit / network designer
vector-04-wave-brain.png     -> runtime pulse / signal flow / waveform
vector-05-cube-research.png  -> research core / reports / legacy fixture
```

Use these to give each major function a consistent visual identity.

---

### `mural fnp-qnn.png` and `mural-ui-thumb.png`

Role: high-energy street-lab identity.

Use sparingly.

Good use:

```text
landing strip
identity/about card
project story section
```

Bad use:

```text
main controls
small buttons
critical runtime results
benchmark display
```

The mural is emotionally strong but can visually overpower the operator workflow.

---

### Product template assets

```text
template tasse bleu.png
mug-blue-ui-thumb.png
tshirt vert template.png
shirt-green-ui-thumb.png
```

Role: product palette / brand extension.

These should not appear in the main research dashboard by default. They can stay in an optional brand/gallery section, but they should not compete with runtime controls.

---

# Asset Cropping, Framing, and Panel Transfer Rules

## Why this ruling exists

Some current assets are visually strong but messy for UI integration. Several need cleaner cuts, better framing, more consistent centering, and a stable invisible safety layer before they are placed in the Panel.

The Panel must not directly depend on raw, messy, unevenly cropped assets.

A raw asset is source material. A Panel asset is a prepared UI component.

---

## Official asset pipeline

Every important visual asset should move through this pipeline:

```text
source asset
→ cut asset
→ framed asset
→ panel-ready asset
```

### Source asset

Original creative file.

Examples:

```text
assets/logo1.png
assets/mascoote qbit.png
assets/qbits stancil.png
assets/mural fnp-qnn.png
```

### Cut asset

Clean subject extraction.

Naming:

```text
*-cut.png
```

Example:

```text
qbit-stencil-cut.png
```

### Framed asset

The subject is placed into a coherent frame or visual support.

Naming:

```text
*-framed.png
```

Example:

```text
qbit-stencil-framed.png
```

### Panel-ready asset

Final PNG with transparent safety margin and stable dimensions.

Naming:

```text
*-panel.png
```

Example:

```text
qbit-stencil-panel.png
```

Panel code should prefer `*-panel.png` assets over raw source assets.

---

## Three-layer model

Every Panel-ready asset must be designed as three logical layers:

```text
Layer 1: visible subject cut
Layer 2: visible or subtle frame/backplate
Layer 3: invisible transparent safety cut layer
```

### Layer 1 — visible subject cut

This is the real object:

```text
logo
mascot
qbit stencil
brain vector
orbit head
circuit brain
wave brain
cube research
future spiderweb node
```

Rules:

```text
- remove dirty background
- clean the silhouette
- preserve important visual identity
- avoid jagged or accidental edges
- do not crop into the subject
```

### Layer 2 — frame/backplate

This gives the asset a stable UI container.

Allowed frame families:

```text
soft rounded square
rounded rectangle
vertical lab plate
capsule badge
light card support
soft glow plate
```

Use frame/backplate when the raw silhouette is too irregular for clean Panel placement.

### Layer 3 — invisible transparent safety cut layer

This is a transparent margin around the framed subject.

It prevents:

```text
- subject touching the card edge
- inconsistent visual weight
- assets feeling randomly cropped
- hover/click states looking unstable
- tight collisions with Panel containers
```

This layer is invisible, but required.

---

## Transparent safety margin rules

Add transparent margin around the visible subject or frame.

Recommended margins:

```text
small tile icons: 8% to 12%
medium UI assets: 10% to 14%
large hero assets: 12% to 18%
brand gallery assets: 10% to 16%
```

Hard rule:

```text
No visible subject should touch the final PNG boundary.
```

---

## Optical centering rules

Center by visual weight, not just pixel geometry.

If an asset has a large element on one side, adjust position until it feels centered to the eye.

Examples:

```text
A mascot with a large head may need to sit slightly lower.
A stencil with a wide gesture may need more side margin.
A circuit-brain asset may need horizontal correction because the active detail is not evenly distributed.
```

Panel-ready exports must look centered when displayed at:

```text
64px
96px
150px
220px
```

---

## Export size rules

Use larger export sizes than display sizes.

### Tile icons

```text
export size: 512x512 or 640x640
Panel display: 64px to 96px
```

### Hero assets

```text
export size: 1200x900 or 1400x1000
Panel display: 120px to 220px high
```

### Sidebar guide assets

```text
export size: 700x900
Panel display: 120px to 180px high
```

### Brand gallery assets

```text
export size: 1200x900 minimum
Panel display: 160px to 220px high
```

---

## Background rules

Preferred final format:

```text
PNG with transparent background
```

The asset must work on:

```text
light cards
navy cards
gradient hero blocks
white operator cards
network designer canvas
```

If a background is needed, it must be intentional:

```text
soft glow plate
rounded square badge
vertical lab plate
subtle light card support
```

Do not keep accidental source background artifacts.

---

## Frame/backplate rules

Use a frame/backplate to stabilize messy assets.

Recommended backplates:

### Soft glow plate

Best for:

```text
quantum
orbit
signal
QNN candidate
```

### Rounded square badge

Best for:

```text
action tiles
small cards
network node icons
```

### Vertical lab plate

Best for:

```text
sidebar guide
mascot
helper state
```

### Light card support

Best for:

```text
brand gallery
mural preview
product preview
```

---

## Asset family coherence

Assets in the same UI family must share:

```text
same output dimensions
same safety margin logic
same backplate style
same visual density
same centering logic
same brightness/contrast range
```

The functional vector assets should become a coherent family:

```text
vector-01-brain-network-panel.png
vector-02-orbit-head-panel.png
vector-03-circuit-brain-panel.png
vector-04-wave-brain-panel.png
vector-05-cube-research-panel.png
```

They should not vary randomly in scale, padding, or visual weight.

---

## Panel transfer checklist

An asset is transferable to the Panel only if:

```text
[ ] the subject is cleanly cut
[ ] there are no dirty borders
[ ] the subject does not touch the final boundary
[ ] transparent safety margin exists
[ ] optical centering is corrected
[ ] frame/backplate is coherent with asset family
[ ] readable at 64px to 96px
[ ] readable on light background
[ ] readable on navy/dark background
[ ] filename uses clean panel-ready naming
```

If any item fails, do not use the asset in `panel_app.py` yet.

---

## Priority assets for recut and framing

Treat these first:

```text
1. logo1.png
2. mascoote qbit.png
3. qbits stancil.png
4. vector-01-brain-network.png
5. vector-02-orbit-head.png
6. vector-03-circuit-brain.png
7. vector-04-wave-brain.png
8. vector-05-cube-research.png
```

Then treat:

```text
9. mural-ui-thumb.png
10. qbit-stencil-avatar-strip.png
11. atom-back-logo-dark.png
```

Product assets are secondary:

```text
mug-blue-ui-thumb.png
shirt-green-ui-thumb.png
```

They should remain below the operational workflow or inside a collapsed brand section.

---

## New asset naming rules

Existing asset names with spaces may stay for compatibility. New assets should be lowercase and hyphen-separated.

Good:

```text
qbit-stencil-panel.png
vector-03-circuit-brain-panel.png
network-designer-hero-panel.png
spiderweb-hub-panel.png
```

Avoid:

```text
new qbit final 2.png
better logo crop.png
panel final use this.png
```

---

## Panel usage rule

Panel code should prefer prepared assets:

```text
assets/generated/*-panel.png
```

Raw assets should be used only as creative sources.

Bad:

```python
pn.pane.Image(str(ASSET_DIR / "qbits stancil.png"), height=150)
```

Better:

```python
pn.pane.Image(str(GENERATED_ASSET_DIR / "qbit-stencil-panel.png"), height=150)
```

---

## Current Panel Problems To Fix

The current Panel has useful ingredients but needs redesign.

### Problem 1: Too many decorative assets in the main flow

The Panel currently mixes logo, stencil, mural, mug, shirt, and vector cards. This makes the dashboard feel more like a brand gallery than a research operator UI.

Fix:

```text
Keep primary runtime UI focused.
Move brand/product visuals lower or into a collapsed Brand Assets section.
Use only one hero image and one compact app mark above the fold.
```

---

### Problem 2: The sidebar is too visually heavy

The sidebar currently contains status, guide image, shirt image, payload controls, and command output. This makes controls compete with decorative assets.

Fix:

```text
Sidebar should prioritize:
1. Runtime status
2. Payload controls
3. Command output
4. Optional collapsed visual guide
```

Remove product visuals from the default sidebar.

---

### Problem 3: Main actions are not yet organized as a workflow

Current actions are:

```text
Run
Encode
Legacy
```

They are useful, but the intended operator flow should be clearer:

```text
1. Prepare Payload
2. Encode Features
3. Run Simulation
4. Inspect Benchmark
5. Export / Review Evidence
6. Open Network Designer
```

Fix:

Use a step-based layout or grouped action tiles.

---

### Problem 4: Runtime evidence is below visual identity

The dashboard should show current runtime state, last run summary, and benchmark evidence early.

Fix:

Place this near the top:

```text
Runtime Status
Latest Run Summary
Backend / Feature Dimension / Probability
Validation Boundary
```

Then show tabs.

---

### Problem 5: Future Network Designer needs a stronger visual grammar

The future drag-and-drop designer needs consistent node colors, card hierarchy, and canvas style. These should be defined now.

Fix:

Use the design tokens, node category rules, and asset framing rules in this document.

---

## Design Direction

The target Panel should feel like:

```text
FNP-QNN Research Control Room
```

Not:

```text
asset gallery
medical product
unfinished notebook
random demo board
```

Desired qualities:

```text
clean
technical
bounded
visual but not noisy
research-forward
operator-friendly
modular
ready for network design
```

---

## Core Color Tokens

Use these existing CSS variables as the source of truth:

```css
:root {
  --fnp-navy: #0d183d;
  --fnp-blue: #1e3aba;
  --fnp-cyan: #55d9ff;
  --fnp-green: #36837e;
  --fnp-orange: #fdaa37;
  --fnp-paper: #f2f6fa;
  --fnp-ink: #081225;
}
```

### Primary colors

| Token | Role |
|---|---|
| `--fnp-navy` | Header, shell, deep background, serious identity. |
| `--fnp-blue` | Primary action, QNN/neural emphasis. |
| `--fnp-cyan` | Signal, highlight, input, active graph edges. |
| `--fnp-green` | Encode, validated state, memory stream. |
| `--fnp-orange` | Warning, quantum accent, important boundary marker. |
| `--fnp-paper` | Main content background. |
| `--fnp-ink` | Text and high-contrast foreground. |

### Usage rule

Use color as information, not decoration.

```text
Blue   -> primary compute / QNN / run
Green  -> encoding / valid / memory stream
Cyan   -> signal / active / input
Orange -> quantum / warning / boundary / legacy
Navy   -> shell / anchor / serious structure
Paper  -> content canvas
```

---

## Recommended Panel Layout

### Top structure

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: FNP-QNN Control Room                                 │
├───────────────┬──────────────────────────────────────────────┤
│ Sidebar       │ Main                                          │
│               │                                              │
│ Runtime       │ 1. Compact hero/status strip                  │
│ Controls      │ 2. Action workflow tiles                      │
│ Payload       │ 3. Latest run summary                         │
│ Output        │ 4. Evidence tabs                              │
│               │ 5. Optional brand/gallery section             │
└───────────────┴──────────────────────────────────────────────┘
```

---

## Recommended Main Panel Order

Use this order in `template.main`:

```python
main=[
    _compact_hero_status(),
    _operator_action_grid(),
    _latest_run_overview(),
    _evidence_tabs(),
    _collapsed_brand_assets(),
]
```

Avoid putting a large brand gallery before runtime evidence.

---

## Recommended Sidebar Order

Use this order in `template.sidebar`:

```python
sidebar=[
    status_pane,
    controls,
    pn.Card(command_output, title="Command output"),
    pn.Card(_small_visual_guide(), title="Visual guide", collapsed=True),
]
```

Do not place shirt/mug product assets in the default sidebar.

---

## Hero Section Redesign

Use a compact status hero:

```text
FNP-QNN Control Room
Local alpha research simulator for Cerebrum memory streams, feature encoding, and QNN candidate lanes.
[Runtime healthy] [Torch fallback ready] [Qiskit optional] [Non-clinical]
```

Recommended assets:

```text
Left/mark: atom-normalized-dark.png or atom-normalized-dark-panel.png
Right/accent: vector-03-circuit-brain-panel.png or qbit-stencil-panel.png
```

Do not use more than two images in the hero.

---

## Action Tiles Redesign

The action tiles should become a workflow grid.

### Required action tiles

```text
1. Encode Features
2. Run Simulation
3. QNN Benchmark
4. Legacy Fixture
5. Network Designer
6. Export Evidence
```

### Asset mapping

| Action | Preferred asset | Tone |
|---|---|---|
| Encode Features | `vector-01-brain-network-panel.png` | green/cyan |
| Run Simulation | `vector-02-orbit-head-panel.png` | blue |
| QNN Benchmark | `vector-04-wave-brain-panel.png` | cyan/blue |
| Legacy Fixture | `vector-05-cube-research-panel.png` | orange/navy |
| Network Designer | `vector-03-circuit-brain-panel.png` | blue/orange |
| Export Evidence | `atom-back-logo-dark-panel.png` or `vector-05-cube-research-panel.png` | navy |

### Tile design rule

Each tile should include:

```text
small prepared panel asset
short title
one-sentence function
button
```

No tile should contain long explanations.

---

## Evidence Tabs Redesign

Recommended tabs:

```text
Events
Pairs
QNN Benchmark
Network Designer
Raw JSON
```

Future tabs:

```text
Graph Config
Validation
Export
Reports
```

The `Network Designer` tab should not be decorative. It should contain the real canvas/workflow builder.

---

## Brand Assets Section

Create a collapsed or lower-page section:

```text
Brand / Visual Identity
```

Include only prepared assets:

```text
mural-panel-gallery.png
qbit-stencil-avatar-strip-panel.png
mug-blue-panel.png
shirt-green-panel.png
```

Keep this section below operational controls and evidence.

---

## Card Pattern

Use three main card families.

### Operator Card

For runtime, controls, and results.

```css
.operator-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(13, 24, 61, 0.12);
  box-shadow: 0 10px 28px rgba(13, 24, 61, 0.10);
}
```

### Signal Card

For active compute/network/QNN elements.

```css
.signal-card {
  border-radius: 18px;
  background:
    radial-gradient(circle at 16% 12%, rgba(85, 217, 255, 0.20), transparent 7rem),
    linear-gradient(145deg, rgba(13, 24, 61, 0.98), rgba(19, 53, 111, 0.96));
  border: 1px solid rgba(85, 217, 255, 0.28);
  box-shadow: 0 16px 34px rgba(8, 18, 37, 0.22);
}
```

### Boundary Card

For non-clinical warnings and limits.

```css
.boundary-card {
  border-radius: 14px;
  background: rgba(253, 170, 55, 0.12);
  border: 1px solid rgba(253, 170, 55, 0.46);
  color: var(--fnp-ink);
}
```

---

## Image Usage Rules

### Maximum image density above the fold

```text
1 compact logo/mark
1 hero/accent image
3-6 small tile icons
```

Avoid:

```text
large mural + logo + mascot + shirt + mug all in first screen
```

### Image sizing

```text
Header mark: 36-56px
Hero accent: 120-170px
Tile icon: 64-90px
Brand gallery image: 160-220px
```

---

## Network Designer Visual Rules

The future Network Designer should follow the same design system.

### Canvas layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Network Designer                                             │
├───────────────┬─────────────────────────────┬────────────────┤
│ Palette       │ Canvas                      │ Inspector      │
│ Presets       │ Nodes + ports + edges       │ Config JSON    │
│ Categories    │ Drag/drop area              │ Validation     │
└───────────────┴─────────────────────────────┴────────────────┘
```

### Node category colors

| Node category | Color family |
|---|---|
| Input | cyan |
| Encoder | green |
| Neural | blue |
| Quantum | orange |
| Spiderweb | navy/cyan |
| Memory graph | green/navy |
| Logic/Decision | orange |
| Output | paper/navy |

### Node structure

Each node should show:

```text
category badge
title
short config summary
input/output ports
selection border when active
```

### Edge style

Edges should use SVG curves.

```text
normal edge: navy/cyan low opacity
selected edge: cyan high opacity
invalid edge: orange
```

---

## Network Designer Asset Mapping

Use prepared assets:

```text
Network Designer main icon: vector-03-circuit-brain-panel.png
Neural preset: vector-02-orbit-head-panel.png
QNN preset: qbit-stencil-panel.png
Spiderweb preset: vector-01-brain-network-panel.png or future spiderweb-hub-panel.png
Memory graph preset: vector-01-brain-network-panel.png
Crossmodal preset: vector-04-wave-brain-panel.png
Research/export preset: vector-05-cube-research-panel.png
```

Do not use KNIME assets, names, colors, icons, or node visual language.

---

## Suggested `template.main` After Refactor

```python
template = pn.template.FastListTemplate(
    title="FNP-QNN Control Room",
    site="SeCuReDMe",
    logo=str(ATOM_ASSET),
    sidebar=[
        status_pane,
        controls,
        pn.Card(command_output, title="Command output"),
        pn.Card(_small_visual_guide(), title="Visual guide", collapsed=True),
    ],
    main=[
        _compact_hero_status(),
        _operator_action_grid(),
        pn.Row(summary_pane, css_classes=["operator-card"]),
        _evidence_tabs(),
        pn.Card(_brand_gallery(), title="Brand / Visual Identity", collapsed=True),
    ],
    accent_base_color="#2f6f9f",
    header_background="#0d183d",
    background_color="#f2f6fa",
    neutral_color="#0d183d",
    main_max_width="1480px",
    sidebar_width=370,
)
```

---

## Screenshot / Demo Readiness Rules

Before using a screenshot externally, verify:

```text
- boundary copy is visible
- no clinical claim appears
- runtime status is clear
- backend is identified
- raw JSON or evidence tabs are available
- visual assets do not overpower results
- every visible image is panel-ready or intentionally marked as raw/demo
```

---

## Future Asset Generation Targets

The current asset set is enough to fix the Panel, but the Network Designer will benefit from dedicated assets.

Recommended future generated assets:

```text
assets/generated/network-designer-hero-panel.png
assets/generated/network-node-input-panel.png
assets/generated/network-node-neural-panel.png
assets/generated/network-node-quantum-panel.png
assets/generated/network-node-spiderweb-panel.png
assets/generated/network-node-output-panel.png
assets/generated/spiderweb-hub-panel.png
assets/generated/spiderweb-leg-panel.png
```

---

## Do Not Do

```text
Do not turn the dashboard into a product gallery.
Do not place mug/shirt assets above runtime evidence.
Do not inject messy raw assets directly into the Panel.
Do not use assets that lack transparent safety margin.
Do not use clinical colors/layouts that imply hospital software.
Do not use KNIME assets, naming, or code.
Do not make the Network Designer look like a copied external product.
Do not add heavy UI dependencies before the backend graph contract exists.
```

---

## Final Design Target

The corrected Panel should communicate this immediately:

```text
This is a local FNP-QNN research control room.
The user can prepare memory payloads, encode features, run candidate QNN/Torch paths, inspect evidence, and open a future visual Network Designer.
The brand is energetic and original, but the workflow remains disciplined and evidence-first.
Every asset is cut, framed, visually centered, and transferable to Panel containers.
```
