FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential pkg-config libcairo2-dev libpango1.0-dev \
       ffmpeg fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir uv==0.13.6

WORKDIR /workspaces/animoz
RUN chown vscode:vscode /workspaces/animoz
COPY --chown=vscode:vscode pyproject.toml uv.lock README.md ./
COPY --chown=vscode:vscode src ./src
USER vscode
RUN uv sync --locked --extra manim

ENV PATH="/workspaces/animoz/.venv/bin:$PATH"
CMD ["animoz", "list"]
