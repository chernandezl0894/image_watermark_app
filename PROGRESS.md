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

- [x] 2.1 Implement `watermark.py` with `add_watermark(input, output, text, opacity, position)`
- [x] 2.2 Semi-transparent text (~50% alpha), bottom-right corner with margin
- [x] 2.3 Error handling: missing file, invalid image, empty text
- [x] 2.4 Tests: output exists, dimensions preserved, pixels changed, errors raised
- [x] 2.5 Run quality checks
- [x] 2.6 Commit: `feat: add watermark core logic with Pillow`

## Phase 3 — Tkinter GUI + tests

- [x] 3.1 Implement `app.py`: main window with image preview
- [x] 3.2 "Load Image" button (`filedialog`)
- [x] 3.3 Watermark text field (default `"Crissis"`)
- [x] 3.4 "Apply Watermark" button (updates preview) and "Save As..." button (`asksaveasfilename`)
- [x] 3.5 Error dialogs with `messagebox`
- [x] 3.6 Tests: window smoke test + GUI helper tests
- [x] 3.7 Run quality checks
- [x] 3.8 Commit: `feat: add Tkinter GUI with load, preview and save`

## Phase 4 — Clean architecture, validations, polish + tests

- [x] 4.1 Domain layer (`domain/`): `WatermarkRequest` entity with invariants, pure `stamp_image`
- [x] 4.2 Application layer (`application/`): `ImageRepository` and `WatermarkUseCases` ports, `WatermarkService`, `validate_request`
- [x] 4.3 Infrastructure layer (`infrastructure/`): `PillowImageRepository` (load/save, colour-model policy)
- [x] 4.4 Presentation layer (`presentation/`): view depends only on the `WatermarkUseCases` protocol (constructor injection), pure preview helpers
- [x] 4.5 GUI validations (no image loaded, empty text, all problems reported at once)
- [x] 4.6 UX polish (Enter applies the watermark, status bar feedback)
- [x] 4.7 Tests per layer: domain, repository, service, validation, preview, view (incl. fake-service DIP test)
- [x] 4.8 Run quality checks + manual launch test
- [x] 4.9 Commit: `refactor: adopt clean architecture layers and GUI validation`

## Phase 5 — Documentation

- [x] 5.1 Create `README.md`: overview, technologies, installation, usage, architecture (clean architecture + SOLID), project structure, development commands, testing
- [x] 5.2 Add future improvements list to `README.md`
- [x] 5.3 Commit: `docs: add README with architecture and future improvements`

---

## Status

| Phase | State  | Commit |
| ----- | ------ | ------ |
| 1     | done   | 339159f |
| 2     | done   | 8f58be2 |
| 3     | done   | 022b31a |
| 4     | done   | 04bc1e9 |
| 5     | done   | (this commit) |
