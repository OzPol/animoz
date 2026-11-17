# Set up animoz

## GitHub Codespaces

1. On GitHub, select `main` for merged work, or the working branch of the PR
   you want to try.
2. Select **Code > Codespaces > Create codespace on this branch**.
3. Wait for the container setup to finish.
4. Run `animoz doctor`.
5. Run `make preview`.
6. Open the printed MP4 from the file explorer, or download it to play locally.

The container uses Python 3.12, Manim Community 0.22.1, FFmpeg, Cairo, Pango,
and CMU Serif fonts from the `fonts-cmu` system package. The Python dependency
versions come from `uv.lock`.
The intro scenes use text and vector shapes, so they do not need LaTeX.
Start with a 2-core / 8 GB codespace and low-quality previews; measure the
actual rendering time before increasing the machine size.

The shared font and its system package are selected together in
`src/animoz/runtime.toml`. Docker and CI use the same dependency installer.
`animoz doctor` checks that **CMU Serif** is installed. For an existing Codespace
or Dev Container, run **Dev Containers: Rebuild Container** to install the new
system font package. [View the font sample](images/cmu-serif.png).

Codespaces compute and storage use your GitHub allowance or billing settings.
Stopping a codespace stops compute usage; stored files still consume storage.

## Local VS Code Dev Container

1. Install Docker and VS Code's Dev Containers extension.
2. Clone the repository and check out the branch you want to use.
3. Open the repository in VS Code.
4. Run **Dev Containers: Reopen in Container**.
5. Run `animoz doctor`, then `make preview`.

Codespaces and local Dev Containers use the same Dockerfile and lock file.

## Docker from a terminal

Build from the repository root:

```bash
docker build -t animoz .
```

List the examples:

```bash
docker run --rm animoz animoz list
```

Save a render on your computer by mounting an output directory:

```bash
docker run --rm --mount type=bind,source="/absolute/path/to/output",target=/renders animoz animoz render intro motion --output-dir /renders
```

Create that output directory first. The container's user must have permission
to write to it. The image uses the `vscode` user; on Linux, match its UID/GID
to your output directory's ownership if necessary.

## Native Linux environment

On Debian 12+ or Ubuntu 24.04+, install the native dependencies (the bootstrap
script needs Python 3.11+):

```bash
sudo python3 scripts/install_system_dependencies.py
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```bash
CC=gcc CXX=g++ uv sync --locked --extra manim
uv run --locked --extra manim animoz doctor
uv run --locked --extra manim animoz render intro motion
```

`.python-version` selects Python 3.12. To explicitly use an existing 3.11
interpreter (3.11.5 or newer), add `--python 3.11` to `uv sync` and `uv run`.
For Windows and macOS, the Dev Container is the common setup path. Native
installation is also supported by [Manim's own instructions](https://docs.manim.community/en/stable/installation/uv.html).

## Existing notebooks

For notebooks, prefer the same locked environment:

```bash
uv sync --locked --extra notebooks
uv run --locked --extra notebooks jupyter notebook
```

The original unlocked installation command remains available:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` selects the `notebooks` extra in `pyproject.toml` so the
dependency list has one source. FFmpeg is a separate system executable used
by the notebook GIF exporters. Saved GIF files remain in their existing paths.
