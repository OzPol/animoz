"""Explicit conversions at the boundary of a model.

The introductory model uses feet and seconds internally. Conversion functions
also accept negative values, so signed velocities retain their direction.
"""

from math import isfinite


def _finite(value: float) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError("A unit conversion requires a finite number.")
    return value


def mph_to_feet_per_second(mph: float) -> float:
    return _finite(mph) * 5280.0 / 3600.0


def feet_per_second_to_mph(feet_per_second: float) -> float:
    return _finite(feet_per_second) * 3600.0 / 5280.0


def inches_to_feet(inches: float) -> float:
    return _finite(inches) / 12.0


def feet_to_inches(feet: float) -> float:
    return _finite(feet) * 12.0
