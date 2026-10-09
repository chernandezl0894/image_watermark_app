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
- [x] 3.3 Watermark text field (default `"image_watermark_app"`)
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

## Phase 6 — Watermark controls

- [x] 6.1 Domain: `WatermarkRequest` gains `color` (hex `#RRGGBB`), `font_size` (optional, auto when `None`) and `font_path` (optional TTF/OTF) with invariants
- [x] 6.2 Domain: `stamp_image` honours colour, explicit font size and custom font file (falls back to the built-in font on unreadable files)
- [x] 6.3 Application: `validate_request` reports missing font files
- [x] 6.4 Presentation: opacity slider with percentage label, position combobox, colour picker with swatch, font-size spinbox (blank = auto) and font file browse/clear
- [x] 6.5 Presentation: shared `_current_request()` helper; apply/save catch invalid control values and warn the user
- [x] 6.6 Tests: domain (colour, font size, TTF rendering, fallback), validation (font file), view (control defaults, colour/font dialogs, invalid values, controls reaching the service)
- [x] 6.7 Update `README.md` (overview, usage, programmatic example) and drop the item from future improvements
- [x] 6.8 Run quality checks (pytest, ruff, mypy)

## Phase 7 — Visual placement

- [x] 7.1 Domain: `WatermarkRequest` gains `rotation` (−180..180), `tiled`, `tile_gap` and free placement via `position="custom"` with `x`/`y` fractions in 0..1
- [x] 7.2 Domain: `stamp_image` renders a tight text tile (optionally rotated), places it by preset/custom coordinates and repeats it in a pannable grid when tiled
- [x] 7.3 Presentation: pure helpers `centered_origin` and `point_to_fraction` map pointer coordinates to image fractions
- [x] 7.4 Presentation: rotation spinbox, tile checkbox, `custom` in the position combobox and live drag on the preview (re-renders on every move, silent on invalid input)
- [x] 7.5 Tests: domain (rotation, custom position, tiling, panning), preview (mapping/clamping), view (control defaults, drag behaviour, values reaching the service)
- [x] 7.6 Update `README.md` (overview, usage, programmatic placement) and drop the item from future improvements
- [x] 7.7 Run quality checks (pytest, ruff, mypy, pre-commit)

## Phase 8 — Packaging + app icon

- [x] 8.1 Assets: track `scripts/generate_icon.py`, `src/image_watermark_app/assets/` (icon.png + icon.ico) and `tests/test_assets.py`
- [x] 8.2 Presentation: `assets.py` resolves bundled asset paths in dev and frozen builds; the window shows the app icon (silent fallback if missing)
- [x] 8.3 PyInstaller: `image_watermark_app.spec` (one-file, windowed, app icon, bundled assets and Tcl/Tk libraries of the uv-managed Python)
- [x] 8.4 Add `pyinstaller` to the dev dependency group
- [x] 8.5 Tests: asset path resolution (dev/frozen/fallback), window icon applied, silent failures
- [x] 8.6 Build the Linux executable and smoke-test it
- [x] 8.7 Update `README.md` (packaging section, commands, structure) and drop the item from future improvements
- [x] 8.8 Run quality checks (pytest, ruff, mypy, pre-commit)

## Phase 9 — CI: Windows executable

- [x] 9.1 GitHub Actions workflow `.github/workflows/build-windows.yml` (uv with cache, frozen lockfile, tests, PyInstaller build)
- [x] 9.2 Upload the `.exe` as a run artifact; publish it to the GitHub Release on `v*` tags
- [x] 9.3 Validate the workflow (YAML + actionlint) and update `README.md` / `PROGRESS.md`

---

## Status

| Phase | State | Commit  |
| ----- | ----- | ------- |
| 1     | done  | 339159f |
| 2     | done  | 8f58be2 |
| 3     | done  | 022b31a |
| 4     | done  | 04bc1e9 |
| 5     | done  | f02d3c4 |
| 6     | done  | 50b0a17 |
| 7     | done  | 0825f7c |
| 8     | done  | c396a91 |
| 9     | done  | 1fbfae5 |
