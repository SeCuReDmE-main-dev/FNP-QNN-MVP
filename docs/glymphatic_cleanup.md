# Glymphatic Idle Cleanup

Purpose: low-noise idle-time inventory and reporting of resources that may be safe to release.

Triggers:
- Datadog monitor for >30 min inactivity on `service:fnp-qnn-local-research-simulator`
- sustained perf degradation monitor
- explicit maintainer request

Phases:
- `SCAN`
- `TAG` (`safe-to-close`, `confirm-required`, `human-only`)
- `DRAIN` (proposed plan only here in the repo)
- `REPORT`

Hard rule: this in-repo script performs SCAN only. It never kills processes, never closes tunnels, never touches Qiskit/IBM Quantum/PyTorch jobs, never modifies E2B sandboxes, never deletes files. All destructive steps are out of scope of this script and require human-in-the-loop approval through Datadog Case or Slack outside this repository.

Output: a JSON report under `reports/glymphatic/` with timestamped filename.
