"""Strict TOML overrides and portable configuration snapshots."""

import copy
import json
import os
import tomllib
from importlib.resources import files
from pathlib import Path


def load_project_config(package: str, path: Path | None = None) -> dict:
    defaults = tomllib.loads(files(package).joinpath("project.toml").read_text())
    if path is None and os.environ.get("ANIMOZ_CONFIG"):
        path = Path(os.environ["ANIMOZ_CONFIG"])
    if path is None:
        return defaults
    override = tomllib.loads(path.read_text(encoding="utf-8"))

    def merge(base: dict, patch: dict, prefix: str = "") -> dict:
        result = copy.deepcopy(base)
        for key, value in patch.items():
            name = f"{prefix}.{key}" if prefix else key
            if key not in base:
                raise ValueError(f"Unknown setting: {name}")
            if isinstance(base[key], dict):
                if not isinstance(value, dict):
                    raise ValueError(f"{name} must be a table.")
                result[key] = merge(base[key], value, name)
            else:
                result[key] = value
        return result

    return merge(defaults, override)


def to_toml(data: dict) -> str:
    lines = []

    def table(values: dict, prefix: tuple[str, ...]) -> None:
        if prefix:
            lines.append("[" + ".".join(json.dumps(key) for key in prefix) + "]")
        for key, value in values.items():
            if not isinstance(value, dict):
                lines.append(
                    f"{json.dumps(key)} = {json.dumps(value, ensure_ascii=False, allow_nan=False)}"
                )
        lines.append("")
        for key, value in values.items():
            if isinstance(value, dict):
                table(value, (*prefix, key))

    table(data, ())
    return "\n".join(lines)
