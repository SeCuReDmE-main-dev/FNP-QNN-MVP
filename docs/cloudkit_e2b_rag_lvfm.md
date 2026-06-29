# CloudKit E2B RAG LVFM Bridge

This document records the current simulator-side contract for connecting E2B,
approved external data, a small persistent RAG layer, and the LVFM runtime.

## Purpose

The bridge lets an external tool such as Codex, OpenClaw, Antigravity, or the
gateway use E2B as an isolated compute lane for data inspection, then admit only
a sanitized summary into the simulator. The simulator remains the owner of
Cerebrum event normalization and `LVFMRuntimeGraph` ingestion.

## Flow

```text
approved external data source
-> E2B sandbox normalization/inspection
-> sanitized RAG admission
-> optional Fernet encrypted envelope
-> simulator decrypts inside approved boundary
-> Cerebrum text memory event
-> LVFM runtime snapshot and QNN-ready feature vector
```

## Commands

Status:

```powershell
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit status
```

Real E2B smoke using the OpenClaw workspace dotenv:

```powershell
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit e2b-smoke --env-file ".env"
```

Plan external data ingestion:

```powershell
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit e2b-ingest-plan --source https://example.com/data.csv --title "External data" --tool-route codex
```

Generate an encryption key:

```powershell
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit rag-keygen
```

Encrypt an admitted summary:

```powershell
$env:FNP_QNN_RAG_ENCRYPTION_KEY = "<generated-fernet-key>"
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit rag-encrypt --title "E2B normalized data" --source "e2b://sandbox/result" --tool-route codex --content-file .\summary.md
```

Convert an admitted summary directly into a runtime result:

```powershell
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit rag-runtime --title "Admitted summary" --source "manual://operator-note" --tool-route codex --content "Sanitized summary only."
```

Decrypt an encrypted envelope and feed LVFM:

```powershell
.\.venv\Scripts\python.exe -m fnp_qnn_cli --json cloud-kit rag-decrypt-runtime --envelope .\envelope.json
```

## HTTP Endpoints

- `GET /cloud-kit/status`
- `POST /cloud-kit/e2b/ingest-plan`
- `GET /cloud-kit/rag/keygen`
- `POST /cloud-kit/rag/encrypt`
- `POST /cloud-kit/rag/runtime`
- `POST /cloud-kit/rag/decrypt-runtime`

## Security Boundary

- `E2B_API_KEY` may be loaded from `[local maintainer path redacted]` or
  the process environment.
- The simulator never prints or serializes the E2B key.
- `FNP_QNN_RAG_ENCRYPTION_KEY` is a Fernet key used only for local envelope
  encryption/decryption.
- The encrypted envelope stores ciphertext and a SHA-256 digest, not the raw
  key.
- CloudKit must not upload secrets, private documents, raw images, clinical
  data, or private CeLeBrUm material without explicit operator approval.

## Codex Handoff

Codex can use this bridge as a native Codex workflow:

1. Inspect or normalize a user-approved source in E2B.
2. Produce a sanitized summary.
3. Admit that summary through the gateway or simulator CLI.
4. Let the simulator convert it into Cerebrum/LVFM events.

Codex remains Codex. The simulator remains the simulator. The bridge gives
Codex a controlled capability surface instead of merging the two systems.
