"""Shared rendering prerequisites, readable before Manim is installed."""

import re
import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    font_family: str
    font_package: str
    native_packages: tuple[str, ...]

    @property
    def system_packages(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((*self.native_packages, self.font_package)))


def load_runtime(path: Path | None = None) -> RuntimeSettings:
    text = (
        path.read_text(encoding="utf-8")
        if path is not None
        else files("animoz").joinpath("runtime.toml").read_text(encoding="utf-8")
    )
    data = tomllib.loads(text)
    if (
        set(data) != {"font", "system"}
        or not isinstance(data["font"], dict)
        or set(data["font"]) != {"family", "package"}
        or not isinstance(data["system"], dict)
        or set(data["system"]) != {"packages"}
    ):
        raise ValueError("Expected [font] family/package and [system] packages.")
    family = data["font"]["family"]
    packages = data["system"]["packages"]
    if not isinstance(family, str) or not family.strip():
        raise ValueError("The font family must be a nonempty string.")
    if not isinstance(packages, list) or not packages:
        raise ValueError("System packages must be a nonempty list.")
    for package in [*packages, data["font"]["package"]]:
        if not isinstance(package, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9+.-]*", package
        ):
            raise ValueError(f"Invalid Debian package name: {package!r}")
    return RuntimeSettings(family, data["font"]["package"], tuple(packages))
