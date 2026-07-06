# Novak-Anderson Phi/Pi Source Ledger

This ledger maps the Novak-Anderson phi/pi work to a bounded simulator module.
It is an educational mathematical layer, not a physical quantum, clinical,
security, cosmology, or consciousness validation.

## Sources

| Source id | Source | Role |
| --- | --- | --- |
| `ANDERSON_NOVAK_PHI_PI_2008` | `https://hascmathart.weebly.com/uploads/7/6/8/7/7687070/a_connection_between_the_numbers_phi_and_pi_2.pdf` | Primary public source for odd-polygon `pseudopi`, `pseudophi`, and inverse pseudopi formulas. |
| `ANDERSON_NOVAK_FIBONACCI_VECTOR_POLYGONS_2009` | `https://www.researchgate.net/profile/Stuart-Anderson-2/publication/228768410_Fibonacci_vector_sequences_and_regular_polygons/links/54b5ec8c0cf26833efd345f7/Fibonacci-vector-sequences-and-regular-polygons.pdf` | Primary public source for Fibonacci-vector sequences and Golden Numbers. |
| `DANI_NOVAK_PHI_HIGHER_DIMENSIONS_SHEET_REDACTED` | `https://docs.google.com/spreadsheets/d/1LICbMOdp689MwMvwToTQJkKf0SQNVKMNoRMKeRP1WFw/edit` | Private-provenance teaching sheet titled `Phi in Higher Dimensions`; no email body or message id is tracked. |
| `GENESIS_ECHOES_PAPER_I_DRIVE_DOC` | `https://docs.google.com/document/d/1kDqt3WML2ev0uBNH9OKseIb7XF5k6H9ScRzusJ47gf4/edit` | Interpretive Drive document tying the theorem to the user's Phi Framework; not primary proof. |
| `PRIVATE_DANI_NOVAK_GMAIL_PROVENANCE_REDACTED` | `[private Gmail provenance redacted]` | Confirms the Sheet was shared in the `my homage to you and Anderson` thread; content remains private. |

## Implemented Claims

- `golden_number(2, 2)` equals the golden ratio.
- `pseudopi(2)` equals `5 / phi`.
- `inverse_pseudopi(2)` equals `phi / 5`.
- `pseudopi(n)` approaches `pi` as the odd polygon order grows.
- Fibonacci-vector component ratios approximate the polygon Golden Numbers.

## Not Claimed

- No proof of a physical quantum computer.
- No proof of cosmology, consciousness, cryptography, or clinical behavior.
- No autonomous scientific conclusion beyond the implemented formulas and tests.
- No private Gmail body, message id, attachment id, or display URL is stored in tracked files.

## Simulator Surface

- Core module: `core/novak_anderson_phi_pi.py`
- Status endpoint: `GET /fnp-qnn/novak-anderson/status`
- Convergence endpoint: `POST /fnp-qnn/novak-anderson/convergence`
- Command router: `/commands/novak-anderson-phi-pi`
- Compatibility shim: `/execute-command` with `command=novak-anderson-phi-pi`
- Tests: `tests/test_novak_anderson_phi_pi.py`, `tests/test_api_novak_anderson_phi_pi.py`
