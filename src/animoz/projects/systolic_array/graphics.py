"""Native Manim objects using the supplied deck's geometry and palette."""

import numpy as np
from manim import BOLD, Arrow, Line, Rectangle, RoundedRectangle, VGroup

from animoz.projects.systolic_array.model import source_slides
from animoz.rendering.theme import label

PAPER = "#F6F8F6"
MINT = "#71DFCF"
AMBER = "#F2BA5F"
BLUE = "#75B8EA"
SOFT = "#A7B8BC"
EDGE = "#3B5961"
PANEL = "#112A34"


def text(value: str, size=24, color=PAPER, **kwargs):
    return label(value, size, color, **kwargs)


def native_slide(number: int, *, shell=False, substitutions=None) -> VGroup:
    """Recreate the original slide objects, never a screenshot of the slide."""
    source = source_slides()
    slide = source["slides"][number - 1]
    factor = (128 / 9) / source["width_emu"]
    result = VGroup()
    for sp in slide["shapes"]:
        if shell and not (sp["y"] < 2.24 * 914400 or sp["y"] > 6.95 * 914400):
            continue
        w, h = sp["w"] * factor, sp["h"] * factor
        location = np.array(
            [
                (sp["x"] + sp["w"] / 2) * factor - 64 / 9,
                4 - (sp["y"] + sp["h"] / 2) * factor,
                0,
            ]
        )
        if sp["geometry"] == "line" or min(w, h) < 0.005:
            result.add(
                Line(
                    location + [-w / 2, h / 2, 0],
                    location + [w / 2, -h / 2, 0],
                    color=EDGE,
                    stroke_width=1,
                )
            )
        elif sp["fill"]:
            constructor = (
                RoundedRectangle if sp["geometry"] == "roundRect" else Rectangle
            )
            kwargs = (
                {"corner_radius": min(w, h) * 0.12}
                if constructor is RoundedRectangle
                else {}
            )
            result.add(
                constructor(
                    width=w,
                    height=h,
                    fill_color=sp["fill"],
                    fill_opacity=1,
                    stroke_width=0,
                    **kwargs,
                ).move_to(location)
            )
        content = sp["text"].strip()
        for original, replacement in (substitutions or {}).items():
            content = content.replace(original, replacement)
        if content and w > 0 and h > 0:
            item = text(
                content,
                sp["font_pt"],
                sp["text_color"],
                weight=BOLD if sp["bold"] else "NORMAL",
            )
            if item.width > w:
                item.scale_to_fit_width(w)
            if item.height > h:
                item.scale_to_fit_height(h)
            item.move_to(location)
            result.add(item)
    return result


class MatrixVisual(VGroup):
    def __init__(self, values, name, *, cell=0.75, number_size=28):
        super().__init__()
        self.rows, self.columns = len(values), len(values[0])
        self.entries = []
        for i, row in enumerate(values):
            self.entries.append([])
            for j, value in enumerate(row):
                entry = text(str(value), number_size).move_to(
                    [
                        (j - (self.columns - 1) / 2) * cell,
                        ((self.rows - 1) / 2 - i) * cell,
                        0,
                    ]
                )
                if entry.width > cell * 0.85:
                    entry.scale_to_fit_width(cell * 0.85)
                self.entries[-1].append(entry)
                self.add(entry)
        width, height = self.columns * cell, self.rows * cell
        for sign in (-1, 1):
            x = sign * (width / 2 + 0.12)
            self.add(
                Line([x, -height / 2, 0], [x, height / 2, 0], color=SOFT),
                Line([x, height / 2, 0], [x - sign * 0.15, height / 2, 0], color=SOFT),
                Line(
                    [x, -height / 2, 0], [x - sign * 0.15, -height / 2, 0], color=SOFT
                ),
            )
        self.add(text(name, 25).move_to([0, height / 2 + 0.42, 0]))

    def at(self, i, j):
        return self.entries[i][j]


class PEGrid(VGroup):
    def __init__(self, rows, columns=None, *, cell=1.2, gap=0.55, show_sums=True):
        super().__init__()
        columns = columns if columns is not None else rows
        self.cells = []
        self.sums = []
        for i in range(rows):
            self.cells.append([])
            self.sums.append([])
            for j in range(columns):
                center = np.array(
                    [
                        (j - (columns - 1) / 2) * (cell + gap),
                        ((rows - 1) / 2 - i) * (cell + gap),
                        0,
                    ]
                )
                box = Rectangle(
                    width=cell,
                    height=cell,
                    color=MINT,
                    stroke_width=1.5,
                    fill_color=PANEL,
                    fill_opacity=1,
                ).move_to(center)
                value = text("0", 26).move_to(center + [0, -0.12, 0])
                self.cells[-1].append(box)
                self.sums[-1].append(value)
                self.add(box)
                if show_sums:
                    self.add(
                        text(f"PE[{i},{j}]", 13, SOFT).move_to(
                            center + [0, cell * 0.3, 0]
                        ),
                        value,
                    )
        for i in range(rows):
            for j in range(columns):
                if j + 1 < columns and gap >= 0.22:
                    self.add(
                        Arrow(
                            self.cells[i][j].get_right(),
                            self.cells[i][j + 1].get_left(),
                            buff=0.07,
                            color=EDGE,
                            stroke_width=1.6,
                        )
                    )
                if i + 1 < rows and gap >= 0.22:
                    self.add(
                        Arrow(
                            self.cells[i][j].get_bottom(),
                            self.cells[i + 1][j].get_top(),
                            buff=0.07,
                            color=EDGE,
                            stroke_width=1.6,
                        )
                    )


def operand(value, color):
    box = RoundedRectangle(
        width=0.48,
        height=0.34,
        corner_radius=0.055,
        color=color,
        fill_color=PANEL,
        fill_opacity=1,
        stroke_width=1.5,
    )
    return VGroup(box, text(str(value), 18, color))
