FROM mcr.microsoft.com/devcontainers/python:3.3.3-3.12-bookworm@sha256:10717c456fb0ac3a9a78c7d9d405599b589d8faf59865f7596a4b26995b7b14c

USER root
COPY src/animoz/__init__.py src/animoz/runtime.py src/animoz/runtime.toml /tmp/animoz-bootstrap/src/animoz/
COPY scripts/install_system_dependencies.py /tmp/animoz-bootstrap/scripts/
# The base image includes an unused Yarn source with an outdated signing key.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources \
    && python /tmp/animoz-bootstrap/scripts/install_system_dependencies.py \
    && rm -rf /var/lib/apt/lists/* /tmp/animoz-bootstrap
COPY requirements-tools.txt /tmp/requirements-tools.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements-tools.txt \
    && rm /tmp/requirements-tools.txt

WORKDIR /workspaces/animoz
RUN chown vscode:vscode /workspaces/animoz
COPY --chown=vscode:vscode pyproject.toml uv.lock README.md ./
COPY --chown=vscode:vscode src ./src
USER vscode
RUN uv sync --locked --extra manim

ENV PATH="/workspaces/animoz/.venv/bin:$PATH"
CMD ["animoz", "list"]
