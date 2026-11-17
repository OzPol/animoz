"""Load the same model for the flat scene and every 3D camera view."""

import os
import tomllib
from dataclasses import asdict, dataclass
from importlib.resources import files
from math import isfinite
from pathlib import Path

from animoz.core.motion import LinearMotion


@dataclass(frozen=True)
class IntroSettings:
    duration_seconds: float
    start_feet: float
    initial_speed_feet_per_second: float
    acceleration_feet_per_second_squared: float

    def __post_init__(self) -> None:
        if not isfinite(self.duration_seconds) or self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive and finite.")
        self.motion()

    def motion(self) -> LinearMotion:
        return LinearMotion(
            self.start_feet,
            self.initial_speed_feet_per_second,
            self.acceleration_feet_per_second_squared,
        )

    def as_dict(self) -> dict[str, float]:
        return asdict(self)

    def to_toml(self) -> str:
        """Serialize this project's settings without assumptions in the CLI."""
        return "[motion]\n" + "".join(
            f"{key} = {value!r}\n" for key, value in self.as_dict().items()
        )


def _motion_values(text: str) -> dict[str, float]:
    data = tomllib.loads(text)
    if set(data) != {"motion"} or not isinstance(data["motion"], dict):
        raise ValueError("The configuration must contain exactly one [motion] table.")
    fields = set(IntroSettings.__dataclass_fields__)
    unknown = set(data["motion"]) - fields
    if unknown:
        raise ValueError("Unknown motion setting(s): " + ", ".join(sorted(unknown)))
    values = {}
    for name, value in data["motion"].items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number.")
        values[name] = float(value)
    return values


def load_settings(path: Path | None = None) -> IntroSettings:
    """Merge a partial override into defaults defined only in project.toml."""
    defaults = files(__package__).joinpath("project.toml").read_text(encoding="utf-8")
    values = _motion_values(defaults)
    if set(values) != set(IntroSettings.__dataclass_fields__):
        raise ValueError("The packaged project.toml must define every motion setting.")
    if path is None and os.environ.get("ANIMOZ_CONFIG"):
        path = Path(os.environ["ANIMOZ_CONFIG"])
    if path is not None:
        values.update(_motion_values(path.read_text(encoding="utf-8")))
    return IntroSettings(**values)
