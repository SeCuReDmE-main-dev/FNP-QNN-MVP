# QLC Wiring Pass 2

The Cerebrum runtime accepts QLC gateway mesh payloads as metadata-only simulator input.

- `/cerebrum/runtime/run` attaches `ffed.qlc.runtime_normalized_context.v1` when a CeLeBrUm/SWOP plugin context is present.
- The runtime summary includes media type, SWOP level, chunk mode, mesh fingerprint, and LVFM metadata.
- Raw image bytes, video bytes, OCR dumps, passwords, tokens, API keys, screenshots, browsing history, and full activity dumps are rejected.
- The E2B Datadog audit script can load `C:\Users\jeans\.openclaw\workspace\.env` and record only QLC bundle fingerprints.

Datadog observes pass/fail metadata. It is not a source of truth for QLC or Cerebrum.
