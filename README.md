# Image Watermark App

A desktop application to add a text watermark to images, built with Python, Tkinter and Pillow.

## Contents

- [Overview](#overview)
- [Built with](#built-with)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Packaging](#packaging)
- [Future improvements](#future-improvements)

## Overview

Load an image from your computer, stamp a text watermark on it, preview the result and save it — all from a simple desktop window.

- Load images in PNG, JPEG, BMP, GIF, WebP and TIFF
- Watermark text is editable (default: `Crissis`)
- Watermark controls: opacity slider, position picker (five positions), text colour,
  font size (auto by default) and custom TTF/OTF font selection
- Visual placement: drag the watermark over the preview, tilt it (−180° to 180°)
  or tile it (repeat it across the whole image, panned by dragging)
- Live preview before exporting
- Save the result as PNG, JPEG, BMP, GIF, WebP or TIFF
- Friendly validation messages (no image loaded, empty text, missing font file, ...)

## Built with

| Technology | Role |
| --- | --- |
| [Python](https://www.python.org/) 3.14 | Programming language |
| Tkinter | Desktop GUI (standard library) |
| [Pillow](https://python-pillow.org/) | Image loading, watermarking and saving |
| [uv](https://docs.astral.sh/uv/) | Package and environment management |
| [Ruff](https://docs.astral.sh/ruff/) | Linter and formatter |
| [mypy](https://mypy.readthedocs.io/) | Static type checking (strict mode) |
| [pytest](https://docs.pytest.org/) | Test runner |
| [pre-commit](https://pre-commit.com/) | Git hooks for automatic checks |
| [PyInstaller](https://pyinstaller.org/) | Standalone executable packaging |

## Getting started

### Requirements

- [uv](https://docs.astral.sh/uv/) (it installs the correct Python version automatically)

### Installation

```bash
git clone <repository-url>
cd image_watermark_app
uv sync
```

This creates a virtual environment in `.venv` and installs the runtime and development dependencies.

## Usage

### Run the application

```bash
uv run image-watermark-app
```

### Step by step

1. **Load Image...** — pick a picture from your computer; it appears in the preview.
2. **Watermark** — type the text you want to stamp (defaults to `Crissis`).
3. **Watermark options** — tune the controls: opacity slider, position picker,
   text colour (**Choose...**), font size (blank = auto-scaled), custom font
   (**Browse...** for a TTF/OTF file, **Clear** to restore the default font),
   rotation and **Tile (repeat)**.
4. **Place it visually** — drag anywhere over the preview to move the watermark
   (the position switches to `custom` and the preview refreshes live); with
   **Tile** active, dragging pans the repeated pattern instead.
5. **Apply Watermark** (or press **Enter** in the text field) — the preview updates
   with the watermark rendered using the current controls.
6. **Save As...** — choose the destination; the suggested name is
   `original_watermarked.ext`.

### Programmatic usage

The watermarking logic can also be used without the GUI:

```python
from pathlib import Path

from image_watermark_app.application import WatermarkService
from image_watermark_app.domain import WatermarkRequest
from image_watermark_app.infrastructure import PillowImageRepository

service = WatermarkService(PillowImageRepository())
service.watermark_file(
    Path("input.png"),
    Path("output.png"),
    WatermarkRequest(
        text="Crissis",
        opacity=0.5,
        position="bottom-right",
        color="#FFFFFF",
        font_size=48,
        font_path=Path("brand.ttf"),
    ),
)
```

`color` accepts a hex string like `#RRGGBB`; `font_size=None` scales the text with
the image; `font_path=None` uses the built-in font (an unreadable file falls back
to it instead of failing). Placement is equally programmatic:

```python
WatermarkRequest(
    text="Crissis",
    position="custom",  # free placement
    x=0.25,
    y=0.75,  # fractions of width/height (centre of the text)
    rotation=30.0,  # counter-clockwise degrees, -180..180
    tiled=True,  # repeat across the image
    tile_gap=0.2,  # gap between repeats (fraction of the shorter side)
)
```

## Architecture

The project follows **clean architecture**: the code is split into layers that depend only
inwards, so the domain rules never depend on the GUI, the file system or Pillow's I/O.

```
                 ┌───────────────────────────┐
                 │      presentation/        │   Tkinter view + preview helpers
                 └─────────────┬─────────────┘
                               │  depends on the WatermarkUseCases protocol
                 ┌─────────────▼─────────────┐
                 │      application/         │   use cases, ports, validation
                 └───────┬─────────────┬─────┘
                         │             │  implements the ImageRepository port
              ┌──────────▼───┐   ┌─────▼────────────────┐
              │    domain/   │   │   infrastructure/    │
              │ pure rules   │   │   Pillow adapter     │
              └──────────────┘   └──────────────────────┘
```

| Layer | Responsibility | Modules |
| --- | --- | --- |
| `domain` | Entities and pure watermarking rules, no I/O or UI | `models.py` (`WatermarkRequest`), `watermark.py` (`stamp_image`) |
| `application` | Use cases and the interfaces they need | `ports.py`, `services.py`, `validation.py` |
| `infrastructure` | Concrete adapters (Pillow persistence) | `pillow_repository.py` |
| `presentation` | Tkinter window, event handlers, preview formatting | `app.py`, `preview.py` |

### SOLID in this project

| Principle | How it is applied |
| --- | --- |
| **S**ingle responsibility | Each module has one reason to change: entities, stamping, validation, persistence, orchestration and the view are all separate. |
| **O**pen/closed | New storage backends or formats are added by implementing `ImageRepository` without touching the view or the domain. |
| **L**iskov substitution | `PillowImageRepository` honours the `ImageRepository` contract, so it can be swapped freely. |
| **I**nterface segregation | The view depends on `WatermarkUseCases` (load/apply/save only), not on the full service API. |
| **D**ependency inversion | The view receives `WatermarkUseCases` by constructor injection; a fake implementation is used in tests. |

## Project structure

```
image_watermark_app/
├── README.md
├── REQUIREMENTS.md          # Original requirements
├── PROGRESS.md              # Phase-by-phase development log
├── pyproject.toml           # Project metadata + ruff/mypy/pytest config
├── image_watermark_app.spec # PyInstaller build config (one-file executable)
├── .pre-commit-config.yaml  # ruff, ruff-format and mypy hooks
├── .editorconfig
├── .zed/settings.json       # Zed editor settings
├── .vscode/settings.json    # VS Code settings
├── scripts/
│   └── generate_icon.py     # Regenerates the app icons deterministically
├── src/image_watermark_app/
│   ├── domain/
│   │   ├── models.py        # WatermarkRequest entity + errors
│   │   └── watermark.py     # Pure stamping logic
│   ├── application/
│   │   ├── ports.py         # ImageRepository / WatermarkUseCases protocols
│   │   ├── services.py      # WatermarkService use cases
│   │   └── validation.py    # User-facing input validation
│   ├── infrastructure/
│   │   └── pillow_repository.py
│   ├── presentation/
│   │   ├── app.py           # Tkinter view (entry point)
│   │   ├── assets.py        # Bundled-asset path resolution (dev and frozen)
│   │   └── preview.py       # Preview scaling/formatting helpers
│   └── assets/              # icon.png + icon.ico (window and build icon)
└── tests/                   # One test module per layer
```

## Development

### Commands

| Command | Description |
| --- | --- |
| `uv sync` | Install/update all dependencies |
| `uv run image-watermark-app` | Launch the desktop app |
| `uv run pytest` | Run the test suite |
| `uv run ruff check .` | Lint |
| `uv run ruff check --fix .` | Lint and apply automatic fixes |
| `uv run ruff format .` | Format the code |
| `uv run mypy` | Type check (strict) |
| `uv run pre-commit run --all-files` | Run every git hook on the whole repo |
| `uv run pyinstaller image_watermark_app.spec` | Build the standalone executable |
| `uv add <package>` | Add a runtime dependency |
| `uv add --dev <package>` | Add a development dependency |

### Code quality workflow

Git hooks are installed with `uv run pre-commit install` (done during setup) and run
**ruff**, **ruff-format** and **mypy** automatically on every commit. A commit only goes
through when all checks pass.

## Testing

```bash
uv run pytest
```

The suite mirrors the architecture: domain, repository, service, validation, preview and
GUI tests. GUI tests create a real Tk window and are skipped automatically when no display
is available.

## Packaging

Build a standalone executable with [PyInstaller](https://pyinstaller.org/) — the result
runs without Python installed:

```bash
uv sync
uv run pyinstaller image_watermark_app.spec
```

The single-file binary lands in `dist/` (`ImageWatermarkApp`, or
`ImageWatermarkApp.exe` on Windows):

- One-file, no console window, with the app icon embedded (Windows/macOS; on Linux
  the icon belongs to the file you assign it to in the desktop).
- The assets used for the window icon are bundled inside the executable.
- Builds are platform-specific: run the same spec on each OS you want to target.
- The window and file icons come from `src/image_watermark_app/assets/`
  (`icon.png` + `icon.ico`); regenerate both deterministically with
  `uv run python scripts/generate_icon.py`.

## Future improvements

- **Logo watermark**: stamp an image/logo in addition to text
- **Batch mode**: process a whole folder of images at once
- **Drag & drop** images onto the window and a "recent files" list
- **Side-by-side preview** (original vs. watermarked) before saving
- **CLI interface** for scripting (building on `WatermarkService`)
- **Persistent settings**: remember the last folder, opacity and position
- **Localization**: Spanish/English UI strings
- **CI pipeline**: GitHub Actions running lint, type check and tests with coverage
- **License**: add a `LICENSE` file to define reuse terms

## License

No license has been chosen yet.
