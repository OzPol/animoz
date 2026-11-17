# Modular projects

Animoz separates numerical models from the library that draws them.

| Layer | Role | Imports Manim? |
| --- | --- | --- |
| `core/` | Unit conversions and reusable numerical models | No |
| `rendering/` | Clock animation, text styling, and presentation helpers | Yes |
| `projects/<name>/model.py` | Project settings and numerical state | No |
| `projects/<name>/scenes.py` | Draw the model from a selected viewpoint | Yes |
| `registry.py` | Project names, scene aliases, and scene file locations | No |
| `cli.py` | Validate settings, launch renders, and record their inputs | Only for environment diagnosis |

## Configuration ownership

| Change | Source of truth | Consumers |
| --- | --- | --- |
| Font family and font package | `src/animoz/runtime.toml` | Theme, doctor, Docker, and CI |
| Native prerequisites | `src/animoz/runtime.toml` | Shared Debian/Ubuntu installer |
| Python dependencies and compatibility | `pyproject.toml` | Packaging, lock generation, doctor |
| Exact resolved versions and hashes | `uv.lock` | Local environment, container, and CI |
| uv bootstrap version | `requirements-tools.txt` | Docker and CI |
| Project numerical defaults | `projects/<name>/project.toml` | Settings loader and all project views |

The intro settings loader merges partial overrides into the packaged TOML.
Python dataclasses have no copies of the teaching defaults. Core motion models
require explicit parameters and contain no project-specific assumptions.
Shared presentation helpers consume the font setting without each scene
choosing a font independently.

Source changes still require rebuilding the relevant output: rerender saved
videos and the font specimen after visual changes, rebuild the container after
native dependency changes, and regenerate `uv.lock` after dependency changes.
The saved MP4s are generated artifacts, not a second configuration system.

## Add a project

1. Create `src/animoz/projects/<name>/` with `__init__.py`.
2. Add `model.py` containing `load_settings(path=None)`. Its returned object
   provides `as_dict()` for the run record and `to_toml()` for a validated
   configuration snapshot.
3. Add a TOML configuration and declare its package data in `pyproject.toml`.
4. Add Manim scene classes in `scenes.py`.
5. Register the project and its scene aliases in `registry.py`.
6. Add tests for its units, geometry, timing, or other numerical invariants.
7. Render the scenes and inspect the resulting frames.
8. Update the documentation and save selected final videos under `videos/<name>/`.

The CLI writes a TOML snapshot of validated settings and provides its path
through `ANIMOZ_CONFIG`. A project's loader uses that snapshot, so every
view in a render sees the same settings. The introductory loader demonstrates
this interface; future projects can use their own settings schema.

The source is an installable Python package. The registry and packaged TOML
files work from an installed wheel as well as an editable checkout.

## Planned development order

1. **manim-intro:** Environment, shared core, CLI, CI, and the introductory scenes.
2. **puerta-court:** Measured site geometry and the event's motion/visibility study.
3. **systolic-array:** Matrix multiplication, processing-element flow, and array examples.

Each stage uses its own branch and PR. The latter two projects will extend this
foundation in their own development stages.
