"""Pure geometry and kinematics. No camera-dependent physical coordinates."""

import copy
import json
from dataclasses import dataclass, replace
from functools import cache
from importlib.resources import files
from math import isfinite, pi, sin
from pathlib import Path

from animoz.core.config import load_project_config, to_toml


def positive(name: str, value: float, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be numeric.")
    if not isfinite(value) or value < 0 or (not allow_zero and value == 0):
        raise ValueError(
            f"{name} must be finite and {'nonnegative' if allow_zero else 'positive'}."
        )
    return float(value)


@dataclass(frozen=True)
class Survey:
    evidence: dict

    @classmethod
    @cache
    def load(cls) -> "Survey":
        return cls(
            json.loads(files(__package__).joinpath("measurements.json").read_text())
        )

    def value(self, source_id: str) -> float:
        return float(self.evidence["source_measurements"][source_id]["value_in"])

    @property
    def corner(self) -> dict[str, tuple[float, float]]:
        x = self.value("05a")
        height = self.value("04b") - self.value("07d")
        return {
            "O": (0.0, 0.0),
            "A": (0.0, height),
            "Q1": (x + self.value("06b"), height - self.value("06a")),
            "Q2": (x + self.value("05c"), height - self.value("05b")),
            "Q3": (x + self.value("07b"), height - self.value("07a")),
            "B": (x + self.value("07c"), 0.0),
        }

    @property
    def post(self) -> tuple[float, float, float]:
        return (
            self.value("05a"),
            self.corner["A"][1] - self.value("04a"),
            self.corner["A"][1] - self.value("04b"),
        )

    @property
    def sidewalk_edges(self) -> tuple[float, float]:
        east = -self.value("10d")
        return east - self.value("15a"), east

    @property
    def slab_joints(self) -> tuple[float, ...]:
        pole_north = self.pole_interval[1] + self.value("13e")
        north_s0 = (
            pole_north - self.value("13f") - self.value("15d") - self.value("15c")
        )
        return (
            north_s0 - self.value("15b"),
            north_s0,
            north_s0 + self.value("15c"),
            north_s0 + self.value("15c") + self.value("15d"),
            pole_north,
            pole_north + self.value("13g"),
            pole_north + self.value("13g") + self.value("13h"),
        )

    @property
    def closure_residual_in(self) -> float:
        return self.slab_joints[1] - self.post[1] - self.value("15h")

    @property
    def pole_interval(self) -> tuple[float, float]:
        lower = self.corner["A"][1] + self.value("13b") + self.value("13d")
        return lower, lower + self.value("13a") - self.value("13c") - self.value("13d")

    @property
    def wall_north(self) -> float:
        return self.corner["A"][1] + self.value("13b") + self.value("13a")

    @property
    def height_rulers(self) -> tuple:
        """Graphic ruler positions for local heights, not registered measurement locations."""
        return (
            (0, sum(self.pole_interval) / 2, self.value("11a")),
            (160, 0, self.value("07e")),
        )


@dataclass(frozen=True)
class State:
    time: float
    front_x_in: float
    car_speed_in_s: float
    car_acceleration_in_s2: float
    bicycle_y_interval_in: tuple[float, float]
    phase: str


@dataclass(frozen=True)
class Settings:
    data: dict

    def __post_init__(self) -> None:
        motion = self.data["motion"]
        positive(
            "replay_inches_per_scene_unit",
            self.data["presentation"]["replay_inches_per_scene_unit"],
        )
        for name, value in motion.items():
            positive(
                name, value, allow_zero=name in {"stop_seconds", "continuation_seconds"}
            )
        camera = self.data["camera"]
        if camera["view"] not in self.data["views"]:
            raise ValueError("Unknown camera view: " + str(camera["view"]))
        for pose in [camera, *self.data["views"].values()]:
            for name in ("phi", "theta", "zoom"):
                value = pose[name]
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not isfinite(value)
                ):
                    raise ValueError(f"Camera {name} must be finite and numeric.")
            if not 0 <= pose["phi"] <= 180 or pose["zoom"] <= 0:
                raise ValueError(
                    "Camera phi must be in [0,180] and zoom must be positive."
                )
        registration = self.data["registration"]
        if not isinstance(registration["enabled"], bool) or not isinstance(
            camera["custom"], bool
        ):
            raise ValueError("enabled and custom must be booleans.")
        for key in ("car_center_north_in", "contact_lateral_in"):
            value = registration[key]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise ValueError(f"{key} must be a finite number.")
        if (
            registration["enabled"]
            and not 0
            < registration["contact_lateral_in"]
            < Survey.load().value("V2") / 2
        ):
            raise ValueError(
                "A registered contact must be on the passenger half of the front bumper."
            )

    def with_camera(
        self,
        view: str | None,
        phi: float | None,
        theta: float | None,
        zoom: float | None,
    ) -> "Settings":
        data = copy.deepcopy(self.data)
        camera = data["camera"]
        if not camera["custom"]:
            camera.update(data["views"][camera["view"]])
        if view is not None:
            if view not in data["views"]:
                raise ValueError("Choose a view: " + ", ".join(data["views"]))
            camera.update(data["views"][view], view=view, custom=False)
        for name, value in (("phi", phi), ("theta", theta), ("zoom", zoom)):
            if value is not None:
                camera[name] = value
                camera["custom"] = True
        return replace(self, data=data)

    @property
    def camera(self) -> dict:
        camera = self.data["camera"]
        return camera if camera["custom"] else self.data["views"][camera["view"]]

    @property
    def camera_id(self) -> str:
        if not self.data["camera"]["custom"]:
            return self.data["camera"]["view"]
        pose = self.camera
        return f"custom-p{pose['phi']:g}-t{pose['theta']:g}-z{pose['zoom']:g}"

    @property
    def contact_time(self) -> float:
        m = self.data["motion"]
        return m["entry_seconds"] + m["stop_seconds"] + m["creep_seconds"]

    @property
    def duration_seconds(self) -> float:
        return self.contact_time + self.data["motion"]["continuation_seconds"]

    def state(self, time: float) -> State:
        if not isfinite(time) or time < 0 or time > self.duration_seconds:
            raise ValueError("Time is outside the modeled interval.")
        m = self.data["motion"]
        speed = m["car_peak_mph"] * 5280 * 12 / 3600
        bike = m["bicycle_mph"] * 5280 * 12 / 3600
        entry, hold, creep = m["entry_seconds"], m["stop_seconds"], m["creep_seconds"]
        distance = speed * creep / 2
        if time <= entry:
            u = time / entry
            x = distance + speed * entry * (0.5 - u + u**3 - 0.5 * u**4)
            v = speed * (1 - 3 * u * u + 2 * u * u * u)
            a = speed / entry * (-6 * u + 6 * u * u)
            phase = "Approach and brake"
        elif time <= entry + hold:
            x, v, a, phase = distance, 0.0, 0.0, "Stopped"
        elif time < self.contact_time:
            u = (time - entry - hold) / creep
            x = distance - speed * creep * (u / 2 - sin(2 * pi * u) / (4 * pi))
            v = speed * sin(pi * u) ** 2
            a = speed * pi / creep * sin(2 * pi * u)
            phase = "Creep, then stop"
        else:
            x, v, a, phase = 0.0, 0.0, 0.0, "Car stopped; kinematic continuation"
        r = self.data["registration"]
        if r["enabled"]:
            x += sum(Survey.load().sidewalk_edges) / 2
            lower = upper = r["car_center_north_in"] + r["contact_lateral_in"]
        else:
            lower, upper = 0.0, Survey.load().value("V2") / 2
        interval = (
            lower + bike * (self.contact_time - time),
            upper + bike * (self.contact_time - time),
        )
        # East is +x. Speed is a nonnegative westbound magnitude, so x
        # acceleration has the opposite sign from the derivative of that speed.
        return State(time, x, v, -a, interval, phase)

    def as_dict(self) -> dict:
        return copy.deepcopy(self.data)

    def to_toml(self) -> str:
        return to_toml(self.data)


def load_settings(path: Path | None = None) -> Settings:
    return Settings(load_project_config(__package__, path))
