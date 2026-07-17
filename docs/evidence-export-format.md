# Evidence Export Format

The education review export is `fnp-qnn.education.review-export` version `1`.
It contains a shared run contract and redacted evidence records.

The exporter applies `sensitive-keys-and-private-paths-v1` recursively. Keys
containing `api_key`, `app_key`, `authorization`, `password`, `private_key`,
`secret`, or `token` are replaced with `[REDACTED]`. Windows user paths,
Unix home paths, `.env` markers, and private-key blocks are also redacted.

The Markdown output is a review summary, not a raw dump. It includes the lab,
seed, progress, export status, trace labels, claim boundary, and evidence count.
Source records are never mutated, and human review remains required.
