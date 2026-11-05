# ChromoPlas Desktop

Windows GUI and automatic WSL2 engine setup, using the existing ChromoPlas CLI.

**Start with the [complete build and installation guide](../docs/windows-desktop.md).**

- Build on Windows: `desktop/windows/build.ps1`.
- Automatic Windows build: `.github/workflows/windows-desktop.yml`.
- GUI/backend: `desktop/app.py`, `desktop/core.py`.
- Linux setup/worker: `desktop/linux/`.
- Tests: `python -m pytest -q tests/test_desktop.py`.

For source development, prepare bundled resources with
`python desktop/prepare_payload.py`, then run `python -m desktop.app` on Windows.

This preview still needs a clean Windows first-install test and a real-genome
comparison against the CLI before public release. The Windows CI build tests
GUI packaging and installation, not live WSL or biological correctness.
