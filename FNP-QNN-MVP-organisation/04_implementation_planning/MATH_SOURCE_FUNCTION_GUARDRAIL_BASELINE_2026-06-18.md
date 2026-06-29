# FNP-QNN Math Source Of Truth Baseline

Date: 2026-06-18

Status: clean baseline for the professor-facing thread, the codebase, and future append-only math updates.

Boundary: alpha-local educational research simulator only. This is not clinical, diagnostic, therapeutic, emergency, safety-critical, security, production-public, or validated physical quantum behavior.

## Objective

This document is the full baseline of mathematical sources currently embedded in the FNP-QNN simulator. After this baseline, future updates should not repeat the whole history. They should append only new source URLs, new functions, new endpoints, and new tests.

This document is also the local source-of-truth artifact for the Gmail thread:

- Thread subject: `i have another project i need to declared as i use your math heavely`
- Thread id: `19ed1c9896026bde`
- Participants by role: Jean-Sebastien Beaulieu, Prof. Florentin Smarandache, Maikel review context
- Gmail action status: no draft was created and no message was sent from this document.

## Evidence Classes

- Confirmed by primary sources: source URLs supplied in the Gmail thread, local git log, public GitHub commit page, current repo files, and local test execution.
- Confirmed by local source files: local PDF/manuscript paths that exist on this machine and are cited by the repo.
- Inferred from implementation: exact simulator purpose of a function when the source gives a mathematical concept and the code uses a bounded educational mapping.
- Forbidden inference: do not convert any local simulator mapping into a claim of physical quantum construction, clinical utility, security, encryption, or production validation.

## Correct Thread Summary

The correct Gmail thread starts with the simulator repository link:

- Original repo link in thread: `https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-`
- Current repo link later declared in the same thread: `https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP`

Prof. Smarandache replied with these sources:

1. `https://fs.unm.edu/NeutrosophicQuantumComputer.pdf`
2. `https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf`
3. `https://fs.unm.edu/IPW/`
4. `https://fs.unm.edu/NSS/39Infinitesimally.pdf`
5. `https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf`
6. `https://fs.unm.edu/IPW/IPW-to-FPW.pdf`
7. `https://fs.unm.edu/NSS/1QuantumTheory.pdf`

The previous professor-facing update in the thread declared this earlier state:

- neutrobit `|0>`, `|1>`, `|I>`;
- non-projective T/I/F measurement;
- coherent and decoherent neutrosophic states;
- finite `puncture_delta` punctured wave;
- 2D punctured surface grid;
- partial entanglement T/I/F profile;
- partial observer effect T/I/F profile;
- neutrosophic logic algebra `not`, `and`, `or`, `if_then`;
- NeuroBit gate metadata;
- optional `state_basis="neutrobit"` QNN expansion;
- 88 unit/API tests, alpha-local validation, deterministic fallback without Qiskit.

The current repo has advanced beyond that summary. The verified current baseline is 117 tests passing, Nidus Idearum II endpoints, Plithogenic runtime fusion, FFeD plugin hook, native CPAI mesh profile, fractal carrier profile, source ledgers, and README trace markers.

## Git And GitHub Evidence

Confirmed by local git and public GitHub commit history on branch `FNP_QNN`:

| Commit | Public evidence | Main math/runtime contribution |
| --- | --- | --- |
| `962c6c6` | Public GitHub commit history | First math source guardrail baseline and append-only update rules. This document replaces that compact baseline with a deeper source-of-truth version. |
| `cbacd3f` | Public GitHub commit history | Plithogenic runtime fusion layer: `core/plithogenic_logic.py`, runtime bridge integration, QNN feature injection when opt-in, API endpoint, tests, organization report. |
| `3c1c7c8` | Public GitHub commit history | Nidus Idearum II math layer: `core/nidus_idearum_math.py`, Nidus request schemas, `/fnp-qnn/nidus/*` endpoints, tests, organization report. |
| `9cfad7d` | Local git log | Native CPAI mesh state in `core/cpai_mesh.py`, API/schema/runtime/QNN integration, tests. |
| `7bfe559` | Local git log | FFeD plugin bridge in `core/ffed_plugin_bridge.py`, plugin hook payload, QNN/NeuroBit/API integration, tests. |
| `8302ef8` | Local git log | Fractal carrier features and normalization: `normalize_fractal_dimension()`, `fractal_carrier_profile()`, QNN/runtime/API/NeuroBit integration. |
| `7fc1036` | Local git log | Core neutrosophic quantum primitives and QNN functionality: neutrobit, measurement, punctured wave, partial entanglement, QNN opt-in path. |

Public GitHub page checked: `https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP/commits/FNP_QNN`

## Selected Source Volumes And URLs

### Prof. Smarandache Thread Sources

| Source | URL | Current simulator binding |
| --- | --- | --- |
| Neutrosophic Quantum Computer | `https://fs.unm.edu/NeutrosophicQuantumComputer.pdf` | Neutrobit basis, local `|I>` marker, gate grammar, reversibility metadata. |
| Neutrosophic Logic Based Quantum Computing | `https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf` | Coherent/decoherent state wrappers, non-projective T/I/F measurement, logic algebra. |
| Infinitesimally Punctured Wave program | `https://fs.unm.edu/IPW/` | Finite educational punctured wave/surface analogies. |
| Infinitesimally Punctured Wave article | `https://fs.unm.edu/NSS/39Infinitesimally.pdf` | IPW topic support for puncture sequence/grid mapping. |
| Infinitesimally Punctured comparison article | `https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf` | IPW/surface/space topic support for finite grid readout. |
| From IPW to FPW | `https://fs.unm.edu/IPW/IPW-to-FPW.pdf` | Practical finite `puncture_delta > 0` parameter. |
| Neutrosophic Quantum Theory: Partial Entanglement, Partial Effect of the Observer, and Teleportation | `https://fs.unm.edu/NSS/1QuantumTheory.pdf` | Partial entanglement and partial observer effect T/I/F profiles. |

### Later Added FS Sources

| Source | URL | Current simulator binding |
| --- | --- | --- |
| Nidus Idearum. Scilogs, II: de rerum consectatione, 2nd ed. | `https://fs.unm.edu/NidusIdearum2-ed2.pdf` | Dynamic T/I/F quality, source-weighted incomplete fusion, partial membership mean. |
| Introduction to Plithogenic Logic as generalization of MultiVariate Logic | `https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf` | Opt-in runtime attribute truth, weight, dependence/contradiction, cumulative plithogenic truth. |

### Local Manuscript Sources

| Source | Local path | Current simulator binding |
| --- | --- | --- |
| Fractal NeutroGeometry local manuscript | `[local maintainer path redacted]` | `D_f`, `D_min`, `D_max`, normalized `D_f_hat`, `dF_carrier`, `i_fractal_candidate`. |
| Complain of Quantum Node #734 local manuscript | `[local maintainer path redacted]}} .pdf` | Local baton/FFeD/fractal carrier wording and boundary discipline. |

Both local paths existed when this baseline was rebuilt.

## Exact Source-To-Code Map

| Layer | Source relationship | Exact code | API/runtime entry | Tests |
| --- | --- | --- | --- | --- |
| Neutrobit basis and T/I/F measurement | `NeutrosophicQuantumComputer.pdf`, `NeutrosophicLogicBasedQuantum.pdf` | `core/neutrosophic_quantum_primitives.py`: `NeutrobitState`, `CoherentNeutroState`, `DecoherentNeutroState`, `neutrosophic_measurement()` | `/qnn/smoke`, `/fnp-qnn/neurobit/gates/run`, `state_basis="neutrobit"` | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| Neutrosophic logic algebra | Same Prof FS quantum/neutrosophic sources | `core/neutrosophic_quantum_primitives.py`: `neutrosophic_gate_algebra()` | Used as pure primitive and in source ledger; bounded educational gate readout | `tests/test_neutrosophic_quantum_primitives.py` |
| NeuroBit gate runtime | Neutrobit/source-backed local gate grammar | `core/neurobit_gate_tunnel.py`: `NeuroBitProfile`, `build_neurobit_gate_sequence()`, `gate_semantics()`, `reversibility_profile()`, `run_neurobit_gates()`, `run_neurobit_tunnel_demo()`; `core/neurobit_gates.py`: `build_neutrosophic_gate_sequence()`, `gate_matrix_json()`, `to_torchquantum_ops()` | `GET /fnp-qnn/neurobit/status`, `POST /fnp-qnn/neurobit/gates/run`, `POST /fnp-qnn/neurobit/tunnel/demo`, command routes | `tests/test_neurobit_gate_tunnel.py`, `tests/test_neurobit_gates.py`, `tests/test_api_qnn_smoke.py` |
| IPW/FPW finite puncture modeling | `IPW/`, `39Infinitesimally.pdf`, `6InfinitesimallyPunctured.pdf`, `IPW-to-FPW.pdf` | `core/neutrosophic_quantum_primitives.py`: `punctured_wave_state()`, `punctured_surface_state()` | Optional `puncture_delta` in QNN, NeuroBit, runtime command schema | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| Partial entanglement and observer effect | `1QuantumTheory.pdf` | `core/neutrosophic_quantum_primitives.py`: `partial_entanglement_profile()`, `observer_effect_profile()` | Optional `observer_strength` in QNN/NeuroBit/runtime schemas | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_cerebrum_qnn.py` |
| Fractal carrier | Local Fractal NeutroGeometry source and local Node #734 framing | `core/neutrosophic_quantum_primitives.py`: `normalize_fractal_dimension()`, `fractal_carrier_profile()` | API aliases `D_f`, `D_min`, `D_max`; outputs `D_f_hat`, `dF_carrier`, `i_fractal_candidate`; appears in QNN, NeuroBit, LVFM runtime metadata | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| QNN source-backed feature expansion | Composite of neutrobit, puncture, observer, fractal carrier | `core/neutrosophic_quantum_primitives.py`: `neutrobit_features_from_vector()`; `core/qnn_nucleus.py`: QNN feature expansion and optional plugin/plithogenic feature intake | `POST /qnn/smoke`, `POST /cerebrum/runtime/run` | `tests/test_cerebrum_qnn.py`, `tests/test_api_qnn_smoke.py`, `tests/test_cerebrum_runtime_bridge.py` |
| Cerebrum runtime and LVFM entry point | Local clean-room runtime contract | `core/cerebrum_runtime_bridge.py`: `CerebrumRuntimeBridge.ingest()`, `build_pairs()`, `build_state()`, `_build_lvfm_snapshot()`; `core/lvfm_runtime_graph.py` | `/cerebrum/runtime/ingest`, `/cerebrum/runtime/pairs`, `/cerebrum/runtime/run`, `/cerebrum/runtime/state/latest` | `tests/test_cerebrum_runtime_bridge.py`, `tests/test_lvfm_runtime_graph.py` |
| Nidus Idearum II layer | `NidusIdearum2-ed2.pdf` | `core/nidus_idearum_math.py`: `triplet_quality_profile()`, `source_weighted_triplet_fusion()`, `partial_membership_mean()` | `GET /fnp-qnn/nidus/status`, `POST /fnp-qnn/nidus/triplet/profile`, `POST /fnp-qnn/nidus/fusion/profile`, `POST /fnp-qnn/nidus/partial-membership/mean` | `tests/test_nidus_idearum_math.py`, `tests/test_api_qnn_smoke.py` |
| Plithogenic runtime fusion | `IntroductionPlithogenicLogic1.pdf` | `core/plithogenic_logic.py`: `plithogenic_attribute_profile()`, `plithogenic_contradiction_degree()`, `plithogenic_neutrosophic_conjunction()`, `plithogenic_weighted_cumulative_truth()`, `plithogenic_runtime_fusion_profile()` | `RuntimeRunRequest.plithogenic_enabled`; `POST /fnp-qnn/plithogenic/runtime/profile`; LVFM key `plithogenic_fusion_profile`; QNN payload key `plithogenic_fusion_profile` | `tests/test_plithogenic_logic.py`, `tests/test_cerebrum_runtime_bridge.py` |
| FFeD plugin hook | Local pluginpack / Node #734 / fractal carrier context | `core/ffed_plugin_bridge.py`: `FfeDPluginBridge`, `build_plugin_payload_from_results()`, `numeric_series_from_events()`, `consensus_items_from_events()` | Optional `plugin_hook_enabled`, `plugin_context`, `plugin_set`, `include_plugin_trace`; emitted plugin feature vector and `plugin_fractal_carrier` | `tests/test_ffed_plugin_bridge.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| Native CPAI mesh | Local runtime mesh contract | `core/cpai_mesh.py`: `CPAIMeshState`, `cpai_mesh_profile()` | Optional `cpai_context`; outputs routing decision, service check, Datadog metric contract | `tests/test_cpai_mesh.py`, `tests/test_ffed_plugin_bridge.py`, `tests/test_api_qnn_smoke.py` |
| Amplitude/phase transforms | Local MVP transfer contract | `core/quantum_feature_transforms.py`: `complex_wavefunction_to_amplitude_phase_features()`, `structure_vector_to_phi_scaled_state()` | Pure QNN candidate utility; no public physical quantum claim | `tests/test_quantum_feature_transforms.py` |

## Current API Surface For Math Inspection

- `POST /qnn/smoke`
- `GET /cerebrum/runtime/status`
- `POST /cerebrum/runtime/ingest`
- `POST /cerebrum/runtime/pairs`
- `POST /cerebrum/runtime/run`
- `GET /cerebrum/runtime/state/latest`
- `GET /fnp-qnn/neurobit/status`
- `POST /fnp-qnn/neurobit/gates/run`
- `POST /fnp-qnn/neurobit/tunnel/demo`
- `GET /fnp-qnn/nidus/status`
- `POST /fnp-qnn/nidus/triplet/profile`
- `POST /fnp-qnn/nidus/fusion/profile`
- `POST /fnp-qnn/nidus/partial-membership/mean`
- `POST /fnp-qnn/plithogenic/runtime/profile`

## What Changed Since The Previous Professor Summary

The previous thread summary said 88 tests and listed the first neutrosophic quantum layer. The current verified implementation adds:

1. Nidus Idearum II math layer:
   - dynamic triplet quality metadata;
   - source-weighted fusion that preserves incomplete/intersection uncertainty as local `I_system_component`;
   - partial membership mean supporting membership below, equal to, and above 1;
   - four opt-in `/fnp-qnn/nidus/*` endpoints.

2. Plithogenic runtime fusion layer:
   - correct entry point is `CerebrumRuntimeBridge.build_state()`;
   - runtime events become plithogenic `P(V1, V2, ..., Vn)` attributes;
   - event weights, pair overlap, dependence, contradiction, cumulative truth, and feature vector are computed;
   - disabled by default; enabled only with `plithogenic_enabled=true`.

3. Fractal carrier:
   - `D_f_hat = (D_f - D_min) / (D_max - D_min)`, clamped to `[0, 1]`;
   - preserved as local carrier under `I -> I_system^S -> D_f -> dF -> i_fractal`;
   - not collapsed into generic `I`.

4. FFeD/CPAI runtime hook:
   - optional allowlisted plugin payload through `FfeDPluginBridge`;
   - native CPAI mesh state through `CPAIMeshState`;
   - plugin and CPAI features can reach QNN/LVFM metadata when explicitly enabled.

5. Documentation and guardrails:
   - source ledger;
   - code-facing math registry;
   - README trace marker;
   - organization reports for Nidus and Plithogenic.

## Validation Baseline

Commands required after this baseline:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
```

Latest known target: 117 tests passing and alpha-local readiness passing.

## Guardrail Rules From This Baseline Forward

- Append only new mathematical sources and new function rows after 2026-06-18.
- Do not re-claim already implemented sources as new work.
- Every new source-backed function must identify the exact URL or local source path.
- Every new endpoint must map to a function row and a test row.
- Keep default simulator behavior unchanged unless an opt-in flag or endpoint is explicitly called.
- Preserve `I -> I_system^S -> D_f -> dF -> i_fractal`.
- Do not collapse `D_f_hat`, `dF`, or `i_fractal_candidate` into generic `I`.
- Keep non-clinical, non-security, non-production wording.

## Complete Professor-Thread Message

The following text is the complete internal record of the message the maintainer intends to post manually in Gmail. It has not been drafted in Gmail and has not been sent by Codex.

Subject: `Re: i have another project i need to declared as i use your math heavely`

```text
Cher Professeur Smarandache,

Je veux reprendre ce fil comme source de verite pour l'etat actuel du simulateur FNP-QNN et expliquer precisement quelles parties de vos mathematiques neutrosophiques sont maintenant implantees dans le moteur.

Le depot actuel est ici:
https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP

Le projet reste un simulateur local alpha de recherche et d'education. Il ne revendique pas de systeme clinique, diagnostic, therapeutique, securite, production, ni preuve physique d'un ordinateur quantique neutrosophique.

Voici l'etat precis des implantations.

1. Neutrosophic Quantum Computer
Source:
https://fs.unm.edu/NeutrosophicQuantumComputer.pdf

Implante dans:
- core/neutrosophic_quantum_primitives.py
- core/neurobit_gate_tunnel.py
- core/neurobit_gates.py

Fonctions/classes implantees:
- NeutrobitState
- NeutrobitState.from_tif()
- NeutrobitState.from_probabilities()
- neutrosophic_measurement()
- neutrosophic_gate_algebra()
- build_neurobit_gate_sequence()
- build_neutrosophic_gate_sequence()
- gate_matrix()
- gate_matrix_json()
- build_gate_parameters()
- run_neurobit_gates()

Utilisation dans le simulateur:
- base locale |0>, |1>, |I>;
- mesure T/I/F non projective;
- gate W comme marqueur local de |I>;
- profil de gates NeuroBit;
- sortie deterministe meme sans Qiskit.

2. Neutrosophic Logic Based Quantum Computing
Source:
https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf

Implante dans:
- core/neutrosophic_quantum_primitives.py

Fonctions/classes implantees:
- CoherentNeutroState
- DecoherentNeutroState
- neutrosophic_measurement()
- neutrosophic_gate_algebra()

Operations neutrosophiques disponibles:
- not
- and
- or
- if_then

Utilisation dans le simulateur:
- etats coherents et decoherents;
- mesure T/I/F sans forcer une reduction binaire;
- logique neutrosophique bornee pour inspection educative.

3. Infinitesimally / Finitesimally Punctured Wave
Sources:
https://fs.unm.edu/IPW/
https://fs.unm.edu/NSS/39Infinitesimally.pdf
https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf
https://fs.unm.edu/IPW/IPW-to-FPW.pdf

Implante dans:
- core/neutrosophic_quantum_primitives.py
- core/neurobit_gate_tunnel.py
- core/qnn_nucleus.py

Fonctions implantees:
- punctured_wave_state()
- punctured_surface_state()
- neutrobit_features_from_vector()

Parametre expose:
- puncture_delta

Utilisation dans le simulateur:
- onde puncturee finie;
- surface puncturee 2D;
- ajout optionnel de features IPW/FPW dans le chemin QNN;
- metadonnees IPW/FPW dans les sorties NeuroBit.

4. Neutrosophic Quantum Theory: Partial Entanglement, Partial Effect of the Observer, and Teleportation
Source:
https://fs.unm.edu/NSS/1QuantumTheory.pdf

Implante dans:
- core/neutrosophic_quantum_primitives.py
- core/neurobit_gate_tunnel.py
- core/qnn_nucleus.py

Fonctions implantees:
- partial_entanglement_profile()
- observer_effect_profile()
- neutrobit_features_from_vector()

Parametre expose:
- observer_strength

Utilisation dans le simulateur:
- profil T/I/F d'entanglement partiel;
- profil T/I/F d'effet partiel de l'observateur;
- augmentation controlee de l'indetermination quand l'observateur est active.

5. Fractal NeutroGeometry / hierarchie I_system
Source locale utilisee dans mon travail:
- Fractal_NeutroGeometry_Livre_V2_chapters_1_to_7.pdf

Implante dans:
- core/neutrosophic_quantum_primitives.py
- core/cerebrum_runtime_bridge.py
- core/qnn_nucleus.py
- core/neurobit_gate_tunnel.py

Fonctions implantees:
- normalize_fractal_dimension()
- fractal_carrier_profile()

Parametres exposes:
- D_f
- D_min
- D_max
- fractal_dimension
- fractal_dimension_min
- fractal_dimension_max
- fractal_admissible
- fractal_measurement_method
- fractal_scale

Utilisation dans le simulateur:
- calcul de D_f_hat = (D_f - D_min) / (D_max - D_min);
- D_f_hat borne entre 0 et 1;
- dF_carrier;
- i_fractal_candidate;
- integration dans QNN, NeuroBit et LVFM.

Je conserve explicitement la hierarchie:

I -> I_system^S -> D_f -> dF -> i_fractal

Je ne reduis pas D_f, dF ou i_fractal a un simple I generique.

6. Nidus Idearum II
Source:
https://fs.unm.edu/NidusIdearum2-ed2.pdf

Implante dans:
- core/nidus_idearum_math.py
- api/main.py
- api/schemas.py

Fonctions implantees:
- triplet_quality_profile()
- source_weighted_triplet_fusion()
- partial_membership_mean()

Endpoints:
- GET /fnp-qnn/nidus/status
- POST /fnp-qnn/nidus/triplet/profile
- POST /fnp-qnn/nidus/fusion/profile
- POST /fnp-qnn/nidus/partial-membership/mean

Utilisation dans le simulateur:
- T/I/F comme triplet dynamique;
- score, accuracy, certainty, positiveness, negativeness;
- contradiction_load;
- indeterminacy_load;
- incomplete_load;
- overdefined_load;
- fusion ponderee par source;
- preservation de l'indetermination dans I_system_component;
- moyenne avec appartenance partielle, incluant membership sous 1, egal a 1, ou au-dessus de 1.

7. Introduction to Plithogenic Logic
Source:
https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf

Implante dans:
- core/plithogenic_logic.py
- core/cerebrum_runtime_bridge.py
- core/qnn_nucleus.py
- api/main.py
- api/schemas.py

Fonctions implantees:
- plithogenic_attribute_profile()
- plithogenic_contradiction_degree()
- plithogenic_neutrosophic_conjunction()
- plithogenic_weighted_cumulative_truth()
- plithogenic_runtime_fusion_profile()

Endpoint:
- POST /fnp-qnn/plithogenic/runtime/profile

Option runtime:
- plithogenic_enabled=true

Utilisation dans le simulateur:
- transformation des evenements runtime en proposition P(V1, V2, ..., Vn);
- triplets T/I/F par attribut;
- poids par source, duree ou evenement;
- degre de dependance entre attributs;
- degre de contradiction local;
- conjonction neutrosophique cumulative min(T), max(I), max(F);
- ajout optionnel d'un vecteur plithogenique dans le chemin QNN;
- ajout d'un profil plithogenique dans LVFM.

Cette couche corrige une lacune precise: avant, le simulateur pouvait croiser des evenements multimodaux, mais il ne mesurait pas explicitement la contradiction ou dependance entre valeurs d'attributs avant LVFM/QNN.

8. Runtime Cerebrum / LVFM avec T, dF, F
Implante dans:
- core/cerebrum_runtime_bridge.py
- core/lvfm_runtime_graph.py

Fonctions/classes reliees:
- CerebrumRuntimeBridge.ingest()
- CerebrumRuntimeBridge.build_state()
- LVFMRuntimeGraph
- RegisterBit

Utilisation dans le simulateur:
- evenements memoire multimodaux;
- paires crossmodales;
- construction de snapshot LVFM;
- registre T / dF / F;
- integration de la couche fractale;
- integration optionnelle de la plithogenie;
- passage vers QNN.

9. QNN avec extension neutrosophique
Implante dans:
- core/qnn_nucleus.py
- core/neutrosophic_quantum_primitives.py

Fonctions/champs relies:
- neutrobit_features_from_vector()
- state_basis="binary"
- state_basis="neutrobit"
- puncture_delta
- observer_strength
- fractal_dimension
- plithogenic_features
- plithogenic_payload

Utilisation dans le simulateur:
- le chemin QNN normal reste binaire par defaut;
- le chemin neutrobit est optionnel;
- les features T/I/F, puncture_delta, observer_strength, D_f_hat et plithogenic peuvent etre ajoutees seulement quand demande.

10. NeuroBit tunnel et metadonnees
Implante dans:
- core/neurobit_gate_tunnel.py

Fonctions reliees:
- run_neurobit_gates()
- run_neurobit_tunnel_demo()
- gate_semantics()
- reversibility_profile()
- counts_to_expectation_vector()

Utilisation dans le simulateur:
- demo locale de gates NeuroBit;
- mesure T/I/F;
- entanglement partiel;
- effet observateur;
- onde/surface puncturee;
- carrier fractal;
- metadonnees de reversibilite;
- demo tunnel locale.

Important: le tunnel NeuroBit n'est pas declare comme encryption ou securite.

11. FFeD / CPAI / carrier fractal local
Sources locales:
- Complain-of-Quantum-Node-734{{ final }} .pdf
- Fractal_NeutroGeometry_Livre_V2_chapters_1_to_7.pdf

Implante dans:
- core/ffed_plugin_bridge.py
- core/cpai_mesh.py
- core/qnn_nucleus.py
- core/neurobit_gate_tunnel.py

Fonctions/classes implantees:
- FfeDPluginBridge
- FfeDPluginBridge.run_mvp5()
- build_plugin_payload_from_results()
- numeric_series_from_events()
- consensus_items_from_events()
- CPAIMeshState
- cpai_mesh_profile()

Utilisation dans le simulateur:
- hook optionnel vers plugins locaux;
- extraction de signaux fractals;
- plugin_fractal_carrier;
- plugin_gate_profile;
- I_system_component;
- CPAI mesh profile;
- decision locale de routage;
- metriques Datadog locales sans secrets.

Ces composants restent optionnels et ne remplacent pas la couche neutrosophique principale.

Endpoints principaux lies a ces couches:
- POST /qnn/smoke
- POST /cerebrum/runtime/run
- POST /cerebrum/runtime/ingest
- POST /cerebrum/runtime/pairs
- GET /fnp-qnn/neurobit/status
- POST /fnp-qnn/neurobit/gates/run
- POST /fnp-qnn/neurobit/tunnel/demo
- GET /fnp-qnn/nidus/status
- POST /fnp-qnn/nidus/triplet/profile
- POST /fnp-qnn/nidus/fusion/profile
- POST /fnp-qnn/nidus/partial-membership/mean
- POST /fnp-qnn/plithogenic/runtime/profile

Etat verifie:
- branche locale: FNP_QNN
- dernier etat public du repo: FNP-QNN-MVP
- tests actuels: 117 tests passent
- validation alpha-local: passe
- Qiskit reste optionnel;
- le fallback deterministe fonctionne sans Qiskit.

A partir de maintenant, je vais garder ce fil comme source de verite. Apres ce message complet, les prochains messages n'ajouteront que les nouvelles sources, les nouvelles fonctions, les nouveaux endpoints et les nouveaux tests. Je ne repeterai plus tout l'historique a chaque fois.

Bien a vous,

Jean-Sebastien Beaulieu
```

## Nota Bene

The current README is intentionally serving as a maintainer trace marker during pre-alpha. It is larger than the final public README should be. Before soft launch / alpha, the README should be condensed into a cleaner user-facing README, while this document and the code ledger remain the detailed source/function registry.
