"""One-dimensional kinematics, independent of the renderer."""

from dataclasses import dataclass
from math import isfinite


def elapsed_seconds(value: float) -> float:
    value = float(value)
    if not isfinite(value) or value < 0:
        raise ValueError("Elapsed time must be finite and nonnegative.")
    return value


@dataclass(frozen=True)
class LinearMotion:
    """Constant-acceleration motion: position = start + speed*t + 0.5*a*t*t."""

    start_feet: float = 0.0
    initial_speed_feet_per_second: float = 2.0
    acceleration_feet_per_second_squared: float = 0.25

    def __post_init__(self) -> None:
        for value in (
            self.start_feet,
            self.initial_speed_feet_per_second,
            self.acceleration_feet_per_second_squared,
        ):
            if not isfinite(value):
                raise ValueError("Motion parameters must be finite.")

    def position(self, time_seconds: float) -> float:
        t = elapsed_seconds(time_seconds)
        return (
            self.start_feet
            + self.initial_speed_feet_per_second * t
            + 0.5 * self.acceleration_feet_per_second_squared * t * t
        )

    def velocity(self, time_seconds: float) -> float:
        t = elapsed_seconds(time_seconds)
        return (
            self.initial_speed_feet_per_second
            + self.acceleration_feet_per_second_squared * t
        )

    def bounds(self, duration_seconds: float) -> tuple[float, float]:
        """Include an interior turning point if the signed velocity reverses."""
        duration = elapsed_seconds(duration_seconds)
        values = [self.position(0.0), self.position(duration)]
        if self.acceleration_feet_per_second_squared:
            turning_time = (
                -self.initial_speed_feet_per_second
                / self.acceleration_feet_per_second_squared
            )
            if 0 < turning_time < duration:
                values.append(self.position(turning_time))
        return min(values), max(values)
