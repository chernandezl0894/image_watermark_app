# PROGRESS

> Phase-by-phase plan for the Image Watermarking App.
> Code, commit messages and documentation in English.
> Check off each task as it is completed.

## Phase 1 — Project setup + tooling

- [x] 1.1 `git init`, `.gitignore`, initial commit with `REQUIREMENTS.md`
- [x] 1.2 `uv init --package`; `uv add pillow`; `uv add --dev pytest ruff mypy pre-commit`
- [x] 1.3 Configure `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` in `pyproject.toml`
- [x] 1.4 Create `.pre-commit-config.yaml` and install hooks
- [x] 1.5 Create `.editorconfig`, `.zed/settings.json`, `.vscode/settings.json`
- [x] 1.6 Create `src/` skeleton and `tests/test_smoke.py`
- [x] 1.7 Run all quality checks (ruff, mypy, pytest, pre-commit)
- [x] 1.8 Commit: `chore: initialize project with uv, ruff, mypy, pytest and pre-commit`

## Phase 2 — Watermark core + tests

- [ ] 2.1 Implement `watermark.py` with `add_watermark(input, output, text, opacity, position)`
- [ ] 2.2 Semi-transparent text (~50% alpha), bottom-right corner with margin
- [ ] 2.3 Error handling: missing file, invalid image, empty text
- [ ] 2.4 Tests: output exists, dimensions preserved, pixels changed, errors raised
- [ ] 2.5 Run quality checks
- [ ] 2.6 Commit: `feat: add watermark core logic with Pillow`

## Phase 3 — Tkinter GUI + tests

- [ ] 3.1 Implement `app.py`: main window with image preview
- [ ] 3.2 "Load Image" button (`filedialog`)
- [ ] 3.3 Watermark text field (default `"Crissis"`)
- [ ] 3.4 "Apply Watermark" button (updates preview) and "Save As..." button (`asksaveasfilename`)
- [ ] 3.5 Error dialogs with `messagebox`
- [ ] 3.6 Tests: window smoke test + GUI helper tests
- [ ] 3.7 Run quality checks
- [ ] 3.8 Commit: `feat: add Tkinter GUI with load, preview and save`

## Phase 4 — Integration, polish, validations + tests

- [ ] 4.1 GUI validations (no image loaded, empty text)
- [ ] 4.2 UX polish (minimum window size, title, resizable)
- [ ] 4.3 Tests for validations
- [ ] 4.4 Run quality checks + manual test
- [ ] 4.5 Commit: `test: add validations and polish UX`

## Phase 5 — Documentation

- [ ] 5.1 Create `README.md` (install, usage, quality commands)
- [ ] 5.2 Add final improvements list to `PROGRESS.md`
- [ ] 5.3 Commit: `docs: add README and future improvements list`

---

## Status

| Phase | State  | Commit |
| ----- | ------ | ------ |
| 1     | done   | (this commit) |
| 2     | pending | —      |
| 3     | pending | —      |
| 4     | pending | —      |
| 5     | pending | —      |
