# Contributing

This repository is in an active crafting phase. Contributions are welcome only
through maintainer-guided, public-safe discussion while this notice remains in
place.

Before proposing changes, read:

- `AGENTS.md`
- `DESIGN.md`
- `EDUCATION.md`
- `ROADMAP.md`
- `SECURITY_MODEL.md`

Good contributions are small, tested, and preserve the alpha-local non-clinical
boundary. Please avoid broad rewrites, heavyweight dependencies, copied
third-party assets/code, or any clinical/security/encryption claims.

Local validation work should use:

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
```
