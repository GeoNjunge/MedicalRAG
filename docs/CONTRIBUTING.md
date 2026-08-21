# CONTRIBUTING.md

Thank you for your interest in contributing to MedicalRAG!

Quick status
- Project status: prototype / experimental. Core pipeline and integration examples exist but some components are stubs or require heavy model files (local LLMs, HF weights). See docs/LOCAL_ARCHITECTURE.md for architecture.
- CI runs fast unit tests only; integration tests that require model files are marked with @pytest.mark.integration.

How to get started (fast path)
1. Fork the repo and create a branch from main.
2. Install Python (3.11+) and Node (18+) for local runs.
3. Create a virtualenv:
   python -m venv .venv
   source .venv/bin/activate
4. Install dev dependencies:
   pip install -r requirements-dev.txt

Run tests
- Run the fast unit tests (CI-style):
  pytest -q -m "not integration" 

- Run integration tests locally (requires model files / environment):
  pytest -q -m "integration"

Testing conventions
- Unit tests: fast, no external model downloads, nothing > 30s.
- Integration tests: require models (llama_cpp, HuggingFace weights, Ollama) and are marked @pytest.mark.integration.

How to add a test
- Put new tests under ml_core/tests/ or apps/api/app/tests/.
- If a test needs heavy models, add: @pytest.mark.integration
- Aim to mock external services (S3, Groq) using unittest.mock or pytest fixtures.

Style & linting
- The repo uses ruff/flake8 and black. Please run linters before submitting:
  ruff check .
  black --check .

Making a PR
1. Open a PR from your branch to main.
2. Add a clear title and short description of what changed.
3. Link any related issues or test failures.
4. CI will run automatically; if it fails, please iterate on the branch.

Good first issues
- Look for issues labeled good-first-issue. If none exist, consider proposing a small enhancement (test, doc, or CI) and open an issue first.

Code of conduct & contributor expectations
- Be respectful and respond to review feedback promptly.
- Keep changes small and focused — one logical change per PR.

Contact / help
- If you’re stuck, open an issue describing the problem and include error logs and environment details (OS, Python version).