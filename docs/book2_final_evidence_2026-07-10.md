# Book II Final Evidence - FNP-QNN

## Scope

This public-safe register maps the bounded computation used by *Fractal
NeutroGeometry: Mapping the Invisible Infinite*, Chapters 8-14. It is a
software-evidence record, not experimental neutrino evidence.

## Non-negotiable boundaries

```text
maximum_proof_state = P2_internal_repeatability
physical_model_validated = false
simulation != detection
candidate != proof
dL_lex != dF
PenroseRulePacket != physical_substrate
Synthia before FNP-QNN
```

## Chapter map

| Chapter | FNP-QNN surface | Public status |
| --- | --- | --- |
| 8 | run-permission reader | permission is not proof |
| 9 | source/experiment choice reader | not T2K reproduction or CP measurement |
| 10 | chamber and run contract | declared container only |
| 11 | passage readout | conditional software candidate |
| 12 | weighted ten-carrier validation engine | `P2_internal_repeatability` ceiling |
| 13 | distributed worker with bounded p046/p114 routing | fault tolerance and replay, not physics validation |
| 14 | matrix threshold engine | bounded `A_adj`, `S_sub`, `P_phason`, and `q_t` calculation |

## Reproduction commands

```powershell
python -m fnp_qnn_cli --json neutrino chapter12-validate --input tests/fixtures/neutrino_chapter12_valid_admission.json
python -m fnp_qnn_cli --json neutrino chapter14-threshold --input tests/fixtures/neutrino_chapter14_threshold.json
python -m unittest discover -s tests
python scripts/validate_alpha_readiness.py
```

For Chapter 13, use `scripts/run_chapter13_distributed_worker.py` with the
checked-in public-safe fixture and a maintainer-supplied pluginpack path. The
distributed worker refuses missing revision pins, invalid manifest hashes,
unbounded chaos, manual randomness overrides, or FNP execution before Synthia
and p114 consensus.

## Frozen evidence summary

| Chapter | Result | Evidence SHA-256 |
| --- | --- | --- |
| 12 | 128/128 E2B tasks, 32 workers; deterministic and seeded replay passed | `b719a00baeb2588be9ec0f15b69f704be9509fb2d7c812931ea2a595f03549d2` |
| 13 | 4 complete runs x 67 sandbox lifecycles; 1072 task results; expected outcomes matched | `ac2bf96322110a89d91eaf083a70cd191b7c17923e70a15f15d54b9e6a127428` |
| 14 | 400 unittest results passed, 2 skipped, readiness passed at commit `9d7d8017189259552bf0f00b178de742f9e1fb50` | `96fd1af8b90d6c1834d2283de71db7d2c7d9fbda544e19461b68795710ee0cb1` |

The hashes identify private audit reports retained by the project. They permit
integrity checks without publishing private conversations, cloud IDs, or the
full manuscript.

## Chapter 14 computation boundary

After Synthia admission, the threshold engine validates exactly ten weighted
carriers and square finite matrices. It computes a bounded state transition,
`D_f`, `D_f_hat`, `dF`, and `i_fractal_candidate`, then emits a canonical
SHA-256 fingerprint. These are deterministic simulator outputs. They are not a
physical substrate, detector evidence, or proof that neutrinos are fractal.

## Python environment note

The current Windows operator environment can emit a PyTorch warning when a
PyTorch build compiled against NumPy 1.x is imported under NumPy 2.x. Use the
repository virtual environment and its pinned dependencies. If that warning
appears, install a compatible NumPy/PyTorch pair before treating the full
readiness run as clean; do not suppress the warning in evidence logs.

## Interim release note

The public websites are intentionally unchanged during this release. A website
sweep is planned separately. Until then, this file and the repository README
are the maintained public description of the Book II software evidence.
