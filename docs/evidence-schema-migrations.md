# Evidence Schema Migrations

The education suite uses `fnp-qnn.education.evidence` version `1` for local
evidence records. The migration code is intentionally conservative: it maps
known legacy aliases, requires the critical claim/provenance fields, and
rejects unknown future versions.

## Version 0 to version 1

| Version 0 field | Version 1 field | Rule |
| --- | --- | --- |
| `id` | `record_id` | Required, trimmed string |
| `experiment_id` | `run_id` | Required, trimmed string |
| `evidence` | `text` | Required, trimmed string |
| `source` | `provenance` | Required, trimmed string |
| `status` | `approval_state` | Must be `pending`, `approved`, `rejected`, or `quarantined` |
| `subject`, `claim` | unchanged | Required, trimmed strings |

Migration is read-time normalization only. It does not promote pending or
quarantined evidence, and it does not rewrite legacy files automatically.
Future schema versions must be handled by an explicit migration before they
can enter the alpha-local review path.
