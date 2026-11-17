"""Exact matrix arithmetic, wavefront events, and the RTL boundary-step schedule."""

import copy
import csv
import io
import json
from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from math import ceil, isfinite
from pathlib import Path

from animoz.core.config import load_project_config, to_toml


def matrix(value) -> tuple[tuple[int, ...], ...]:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("A matrix must have at least one row.")
    if any(not isinstance(row, (list, tuple)) or not row for row in value):
        raise ValueError("Matrix rows must be nonempty sequences.")
    width = len(value[0])
    if any(len(row) != width for row in value):
        raise ValueError("Matrix rows must have equal length.")
    for row in value:
        for entry in row:
            if isinstance(entry, bool) or not isinstance(entry, int):
                raise ValueError("The teaching example uses exact integer operands.")
            if not -32768 <= entry <= 32767:
                raise ValueError(
                    "Operands must fit the source design's signed 16-bit inputs."
                )
    return tuple(tuple(row) for row in value)


def multiply(a, b) -> tuple[tuple[int, ...], ...]:
    a, b = matrix(a), matrix(b)
    if len(a[0]) != len(b):
        raise ValueError("A column count must equal B row count.")
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0])))
        for i in range(len(a))
    )


@dataclass(frozen=True)
class MAC:
    row: int
    column: int
    inner: int
    a: int
    b: int
    before: int
    after: int


def wavefront(a, b) -> tuple[tuple[MAC, ...], ...]:
    a, b = matrix(a), matrix(b)
    product = multiply(a, b)
    rows, columns, inner = len(a), len(b[0]), len(b)
    accum = [[0] * columns for _ in range(rows)]
    steps = []
    for step in range(inner + rows + columns - 2):
        events = []
        for i in range(rows):
            for j in range(columns):
                k = step - i - j
                if 0 <= k < inner:
                    before = accum[i][j]
                    accum[i][j] += a[i][k] * b[k][j]
                    events.append(MAC(i, j, k, a[i][k], b[k][j], before, accum[i][j]))
        steps.append(tuple(events))
    if tuple(tuple(row) for row in accum) != product:
        raise AssertionError(
            "Wavefront schedule did not reproduce matrix multiplication."
        )
    return tuple(steps)


@dataclass(frozen=True)
class CycleCounts:
    order: int
    grid: int
    budget: int
    tiles: int
    advances: int
    stalls: int
    captures: int
    readout: int

    @property
    def compute(self) -> int:
        return self.advances + self.stalls + self.captures

    @property
    def total(self) -> int:
        return self.compute + self.readout

    @property
    def utilization(self) -> float:
        return self.order**3 / (self.grid**2 * self.compute)


def boundary_words(step: int, order: int, grid: int) -> int:
    return 2 * sum(0 <= step - edge < order for edge in range(grid))


def cycle_counts(order: int, grid: int, budget: int) -> CycleCounts:
    if any(
        isinstance(v, bool) or not isinstance(v, int) or v <= 0
        for v in (order, grid, budget)
    ):
        raise ValueError("Order, grid size, and word budget must be positive integers.")
    if grid > order or order % grid:
        raise ValueError(
            "The source RTL schedule assumes square output tiles with P dividing N."
        )
    tiles = (order // grid) ** 2
    advances = order + 2 * grid - 2
    stalls = sum(
        max(1, ceil(boundary_words(step, order, grid) / budget)) - 1
        for step in range(advances)
    )
    return CycleCounts(
        order, grid, budget, tiles, tiles * advances, tiles * stalls, tiles, order**2
    )


@cache
def measured_results() -> tuple[dict, ...]:
    text = files(__package__).joinpath("source-simulation.csv").read_text()
    return tuple(csv.DictReader(io.StringIO(text)))


@cache
def source_slides() -> dict:
    return json.loads(files(__package__).joinpath("source-slides.json").read_text())


@dataclass(frozen=True)
class Settings:
    data: dict

    def __post_init__(self) -> None:
        a, b = self.a, self.b
        multiply(a, b)
        if max(len(a), len(a[0]), len(b[0])) > 4:
            raise ValueError(
                "Keep the displayed teaching matrices at most 4 by 4 for legibility."
            )
        p = self.data["presentation"]
        cycle_counts(p["workload_order"], p["grid_size"], p["input_budget"])
        for name in ("word_seconds", "animation_seconds"):
            value = p[name]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or value <= 0
            ):
                raise ValueError(f"{name} must be a positive finite number.")
        if p["tiling_order"] not in (8, 16):
            raise ValueError("Tiling uses one of the two source workloads: 8 or 16.")
        if (
            p["workload_order"] not in (8, 16)
            or p["grid_size"] not in (2, 4, 8)
            or p["input_budget"] not in (4, 8, 16)
        ):
            raise ValueError(
                "The evidence comparison uses N=8/16, P=2/4/8, and B=4/8/16."
            )

    @property
    def a(self):
        return matrix(self.data["example"]["a"])

    @property
    def b(self):
        return matrix(self.data["example"]["b"])

    @property
    def c(self):
        return multiply(self.a, self.b)

    def as_dict(self) -> dict:
        return copy.deepcopy(self.data)

    def to_toml(self) -> str:
        return to_toml(self.data)


def load_settings(path: Path | None = None) -> Settings:
    return Settings(load_project_config(__package__, path))
