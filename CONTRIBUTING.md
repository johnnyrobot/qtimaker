# Contributing to QTI Maker

Thanks for your interest in contributing! QTI Maker is a fork and enhancement of
[text2qti](https://github.com/gpoore/text2qti) by Geoffrey M. Poore and Glenn
Horton-Smith. Contributions of all kinds are welcome — bug reports, fixes,
documentation, and features.

## Getting started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/qtimaker.git
   cd qtimaker
   ```
2. Install in editable mode with the development tools:
   ```bash
   python3 -m pip install -e ".[dev]"
   ```
   Requires Python 3.10 or higher. See the [README](README.md#installation) for
   full platform-specific setup.

## Before opening a pull request

- **Keep changes focused.** One logical change per pull request is easier to
  review.
- **Lint your code** with [Ruff](https://docs.astral.sh/ruff/):
  ```bash
  python3 -m ruff check .
  ```
- **Do not commit secrets or sample data.** Never commit a `.env` file, API
  keys, or anything under `uploads/` (these are gitignored — please keep them
  that way).
- **Match the surrounding style** and keep comments meaningful.
- **Preserve attribution.** The core QTI engine derives from text2qti under the
  BSD 3-Clause License; keep existing copyright notices intact.

## Reporting bugs

Open a [GitHub issue](https://github.com/johnnyrobot/qtimaker/issues) with steps
to reproduce, what you expected, and what actually happened. Include your OS and
Python version where relevant.

For **security vulnerabilities**, do not open a public issue — follow the
process in [SECURITY.md](SECURITY.md).

## Code of conduct

By participating in this project you agree to abide by our
[Code of Conduct](CODE_OF_CONDUCT.md).
