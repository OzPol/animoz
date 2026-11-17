# Dependency and execution boundaries

Use `uv sync --locked --extra manim` and run `make audit` before proposing a
dependency change. `uv.lock` records exact versions and distribution hashes.
`uv audit --locked` checks every locked extra and transitive dependency using
OSV, not just packages installed in the active environment. CI saves the audit
report and fails on findings or service errors; there are no ignored advisories.

Manim and Matplotlib require Pillow internally. Animoz does not import Pillow
or use its GIF exporter, but the environment contains it transitively. Removing
an explicit requirement does not remove that dependency. It stays in the lock
and audit scope. The previous GIFs are preserved; notebook exports use FFmpeg.
The Soup Sieve constraint in `pyproject.toml` excludes versions affected by
GHSA-mmhr-3c5m-f64f. The patched release also requires Python 3.11.5+.

Scenes and notebooks execute Python. Render trusted source code only. The CLI
parses numerical TOML settings with a strict schema, rejects unknown fields,
booleans and nonfinite inputs, and launches subprocesses with argument lists
rather than a shell. A validated snapshot supplies the same inputs to every
view. Configuration loading does not evaluate Python expressions.

The development image builds native prerequisites as root and runs rendering
as its unprivileged `vscode` user. Native package names are validated before
installation. CI uses read-only repository permissions, commit-pinned actions,
and checkout without persisted credentials. Dependency and container updates
are made manually and tested. Keep sensitive files and host credentials
out of the container's mounted workspace when executing third-party scenes.

The Python audit checks known published advisories; it does not prove the
absence of vulnerabilities or scan FFmpeg, Cairo, Pango, the operating system,
or the Docker daemon. The base image uses a version tag and verified digest.
Review and update that digest and rebuild native packages regularly.
The current project has no upload service or public rendering endpoint; adding
one would require resource limits and isolation designed for untrusted input.
