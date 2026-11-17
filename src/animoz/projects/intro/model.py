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
    duration_seconds: float = 4.0
    start_feet: float = 0.0
    initial_speed_feet_per_second: float = 2.0
    acceleration_feet_per_second_squared: float = 0.25

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


def load_settings(path: Path | None = None) -> IntroSettings:
    """An explicit config path overrides the packaged teaching defaults."""
    if path is None and os.environ.get("ANIMOZ_CONFIG"):
        path = Path(os.environ["ANIMOZ_CONFIG"])
    if path is None:
        text = files(__package__).joinpath("project.toml").read_text()
    else:
        text = path.read_text(encoding="utf-8")
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
    return IntroSettings(**values)
