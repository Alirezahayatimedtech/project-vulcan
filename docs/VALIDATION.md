# Validation

Project Vulcan v0.2 is validated with deterministic unit, safety, interoperability, and golden-workflow tests. CI runs `pytest -q` and `ruff check src tests` on pushes and pull requests.

The ROP proof uses synthetic data and a HAPI FHIR sandbox only; passing tests do not constitute clinical validation or regulatory clearance.
