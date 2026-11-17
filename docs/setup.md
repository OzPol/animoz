# Set up animoz

## GitHub Codespaces

1. On GitHub, select the branch you want to use. While the intro PR is open,
   select `manim-intro`.
2. Select **Code > Codespaces > Create codespace on this branch**.
3. Wait for the container setup to finish.
4. Run `animoz doctor`.
5. Run `make preview`.
6. Open the printed MP4 from the file explorer, or download it to play locally.

The container uses Python 3.12, Manim Community 0.22.1, FFmpeg, Cairo, Pango,
and DejaVu fonts. The Python dependency versions come from `uv.lock`.
The intro scenes use text and vector shapes, so they do not need LaTeX.
Start with a 2-core / 8 GB codespace and low-quality previews; measure the
actual rendering time before increasing the machine size.

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

On Debian or Ubuntu, install the native dependencies:

```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libcairo2-dev libpango1.0-dev ffmpeg fonts-dejavu-core
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```bash
CC=gcc CXX=g++ uv sync --locked --extra manim
uv run --locked --extra manim animoz doctor
uv run --locked --extra manim animoz render intro motion
```

`.python-version` selects Python 3.12. To explicitly use an existing 3.11
interpreter, add `--python 3.11` to `uv sync` and `uv run`.
For Windows and macOS, the Dev Container is the common setup path. Native
installation is also supported by [Manim's own instructions](https://docs.manim.community/en/stable/installation/uv.html).

## Existing notebooks

The original notebook installation command remains available:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` selects the `notebooks` extra in `pyproject.toml` so the
dependency list has one source. FFmpeg is a separate system executable used
by the notebook GIF exporters. Saved GIF files remain in their existing paths.
