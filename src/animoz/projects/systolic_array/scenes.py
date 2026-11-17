"""The supplied presentation, explained through matrix and hardware state changes."""

import numpy as np
from manim import (
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    Rectangle,
    SurroundingRectangle,
    Transform,
    TransformFromCopy,
    ValueTracker,
    VGroup,
    always_redraw,
    linear,
)

from animoz.projects.systolic_array.graphics import (
    AMBER,
    BLUE,
    EDGE,
    MINT,
    PAPER,
    SOFT,
    MatrixVisual,
    PEGrid,
    native_slide,
    operand,
    text,
)
from animoz.projects.systolic_array.model import (
    cycle_counts,
    load_settings,
    measured_results,
    source_slides,
    wavefront,
)
from animoz.rendering.story import ExplainedScene


class SystolicStory(ExplainedScene):
    def setup(self):
        super().setup()
        self.settings = load_settings()
        self.camera.background_color = source_slides()["slides"][0]["background"]
        self.caption_color = PAPER
        self.caption_bottom = 0.78
        self.frame = None
        self.anim = self.settings.data["presentation"]["animation_seconds"]

    def explain(self, message, *animations, seconds=None):
        if seconds is None:
            seconds = max(
                2.7,
                len(message.split())
                * self.settings.data["presentation"]["word_seconds"],
            )
        super().explain(message, *animations, seconds=seconds)

    def slide(self, number, *, full=False):
        source = source_slides()["slides"][number - 1]
        headline = max(
            (s for s in source["shapes"] if s["text"].strip()),
            key=lambda s: s["font_pt"],
        )["text"]
        self.chapter(f"Source slide {number}: " + headline.replace("\n", " "))
        if self.frame is not None:
            self.clear_diagram(keep=(self.frame,))
        config = self.settings.data["presentation"]
        substitutions = {
            "16×16 matrix on the 8×8 grid": f"{config['workload_order']}×{config['workload_order']} matrix on the {config['grid_size']}×{config['grid_size']} grid",
            "16×16 product, full input supply": f"{config['workload_order']}×{config['workload_order']} product, full input supply",
            "The 8×8 grid can outgrow its input supply": (
                "The grid can outgrow its input supply"
                if 2 * config["grid_size"] > config["input_budget"]
                else "The grid fits its input supply"
            ),
            "up to 16 combined A/B words": f"up to {2 * config['grid_size']} combined A/B words",
        }
        new = native_slide(number, shell=not full, substitutions=substitutions)
        if self.frame is None:
            self.frame = new
            self.play(FadeIn(self.frame), run_time=0.6)
        else:
            self.play(Transform(self.frame, new), run_time=0.75)

    def introduction(self):
        self.slide(1, full=True)
        self.explain(
            "A systolic array is a team of small arithmetic units. We will follow the numbers first, then see why adding units does not guarantee proportional speedup."
        )
        self.slide(2)
        grids = (
            VGroup(
                *(PEGrid(p, cell=0.22, gap=0.045, show_sums=False) for p in (2, 4, 8))
            )
            .arrange(buff=1.4)
            .move_to([0, -0.2, 0])
        )
        labels = VGroup(
            *(
                text(f"{p} × {p}: {p * p} PEs", 22, MINT).next_to(
                    g, np.array([0, -1, 0]), buff=0.35
                )
                for p, g in zip((2, 4, 8), grids)
            )
        )
        self.explain(
            "Our source project compares 2 by 2, 4 by 4, and 8 by 8 grids. Each must complete the same matrix product.",
            FadeIn(grids),
            FadeIn(labels),
        )
        self.explain(
            "A processing element, or PE, repeatedly multiplies two numbers and adds the product to its local running sum. We can understand the entire machine from that one operation."
        )

    def matrices(self):
        self.slide(4)
        a, b, c = self.settings.a, self.settings.b, self.settings.c
        cell = min(0.75, 2.1 / max(len(a), len(b), len(b[0])))
        av = MatrixVisual(a, f"A ({len(a)} × {len(b)})", cell=cell).move_to(
            [-4.3, -0.1, 0]
        )
        bv = MatrixVisual(b, f"B ({len(b)} × {len(b[0])})", cell=cell).move_to(
            [-0.9, -0.1, 0]
        )
        cv = MatrixVisual(
            [["·"] * len(b[0]) for _ in a], f"C ({len(a)} × {len(b[0])})", cell=cell
        ).move_to([3.5, -0.1, 0])
        signs = VGroup(
            text("×", 35).move_to([-2.6, -0.1, 0]),
            text("=", 35).move_to([1.3, -0.1, 0]),
        )
        self.explain(
            "A matrix is a table of numbers. Multiplication pairs one row of A with one column of B to produce one entry of C.",
            FadeIn(av),
            FadeIn(bv),
            FadeIn(cv),
            FadeIn(signs),
        )
        rule = text("C[i,j] = Σ A[i,k] × B[k,j]", 27).move_to([0, -1.6, 0])
        index_label = text(f"k = 0, …, {len(b) - 1}", 18, SOFT).move_to([0, -2.1, 0])
        self.explain(
            f"A's columns must match B's rows. Here the shared length is {len(b)}, so each output sum contains {len(b)} products.",
            FadeIn(index_label),
        )
        self.explain(
            "The index k walks through the matching entries. The summation sign means that we add every matched product.",
            FadeIn(rule),
        )
        first = True
        for i in range(len(a)):
            for j in range(len(b[0])):
                row = VGroup(*(av.at(i, k) for k in range(len(b))))
                column = VGroup(*(bv.at(k, j) for k in range(len(b))))
                hr = SurroundingRectangle(row, color=MINT, buff=0.14)
                hc = SurroundingRectangle(column, color=AMBER, buff=0.14)
                self.play(Create(hr), Create(hc), run_time=0.45)
                running = 0
                for k in range(len(b)):
                    next_sum = running + a[i][k] * b[k][j]
                    expression = text(
                        f"C[{i},{j}]:  {running} + {a[i][k]} × {b[k][j]} = {next_sum}",
                        28,
                    ).move_to(rule)
                    if first:
                        self.explain(
                            f"The running sum is {running}. Multiply {a[i][k]} by {b[k][j]}, then add that product. The new sum is {next_sum}.",
                            Indicate(av.at(i, k), color=MINT),
                            Indicate(bv.at(k, j), color=AMBER),
                            Transform(rule, expression),
                            Transform(
                                index_label,
                                text(
                                    f"k = {k}    A[{i},{k}] × B[{k},{j}]", 18, SOFT
                                ).move_to(index_label),
                            ),
                        )
                    else:
                        self.play(
                            Indicate(av.at(i, k), color=MINT),
                            Indicate(bv.at(k, j), color=AMBER),
                            Transform(rule, expression),
                            Transform(
                                index_label,
                                text(
                                    f"k = {k}    A[{i},{k}] × B[{k},{j}]", 18, SOFT
                                ).move_to(index_label),
                            ),
                            run_time=self.anim,
                        )
                    running = next_sum
                self.play(
                    Transform(
                        cv.at(i, j), text(str(c[i][j]), 28, MINT).move_to(cv.at(i, j))
                    ),
                    run_time=0.5,
                )
                if first:
                    self.explain(
                        "That completes one output entry. It stays in C while the same row-column rule fills the other positions."
                    )
                self.play(FadeOut(hr), FadeOut(hc), run_time=0.25)
                first = False
        self.explain(
            "The completed matrix contains every row-column dot product. The arithmetic rule is simple; the architectural challenge is delivering each matching pair at the right time."
        )

    def dataflow(self):
        self.slide(3)
        a, b = self.settings.a, self.settings.b
        rows, columns = len(a), len(b[0])
        grid = PEGrid(
            rows, columns, cell=min(1.15, 3.8 / max(rows, columns) - 0.5), gap=0.5
        ).move_to([0, -0.4, 0])
        self.explain(
            "Now place each output in one processing element. A operands move right. B operands move down. The partial sum stays where it is.",
            FadeIn(grid),
        )
        tags = VGroup(
            text("A moves right", 21, MINT).move_to([-4.7, 0.4, 0]),
            text("B moves down", 21, AMBER).move_to([3.8, 0.4, 0]),
        )
        self.add(tags)
        schedule = wavefront(a, b)
        clock_text = text("Logical step 0", 23, SOFT).move_to([0, -2.35, 0])
        self.add(clock_text)
        self.explain(
            "The inputs are staggered at the edges. A matching pair meets at PE[i,j] when step = i + j + k. This creates a diagonal wave of useful work."
        )
        self.explain(
            "Each multiply-and-add is one MAC. A PE without a matching operand pair on this step keeps its current sum."
        )
        for step, events in enumerate(schedule):
            tokens = VGroup()
            moves = []
            for i in range(rows):
                for k in range(len(b)):
                    j = step - i - k
                    if 0 <= j < columns:
                        end = grid.cells[i][j].get_center() + [-0.29, 0.05, 0]
                        start = (
                            grid.cells[i][j - 1].get_center()
                            if j
                            else grid.cells[i][0].get_center() + [-1.8, 0, 0]
                        ) + [-0.29, 0.05, 0]
                        chip = operand(a[i][k], MINT).move_to(start)
                        tokens.add(chip)
                        moves.append(chip.animate.move_to(end))
            for j in range(columns):
                for k in range(len(b)):
                    i = step - j - k
                    if 0 <= i < rows:
                        end = grid.cells[i][j].get_center() + [0.29, 0.05, 0]
                        start = (
                            grid.cells[i - 1][j].get_center()
                            if i
                            else np.array(
                                [
                                    grid.cells[0][j].get_center()[0],
                                    min(grid.get_top()[1] + 0.12, 1.1),
                                    0,
                                ]
                            )
                        ) + [0.29, 0.05, 0]
                        chip = operand(b[k][j], AMBER).move_to(start)
                        tokens.add(chip)
                        moves.append(chip.animate.move_to(end))
            self.add(tokens)
            self.play(
                *moves,
                Transform(
                    clock_text,
                    text(
                        f"Logical step {step}: {len(events)} useful MACs", 23, SOFT
                    ).move_to(clock_text),
                ),
                run_time=self.anim,
            )
            self.play(
                *(
                    Transform(
                        grid.sums[e.row][e.column],
                        text(str(e.after), 26).move_to(grid.sums[e.row][e.column]),
                    )
                    for e in events
                ),
                *(Indicate(grid.cells[e.row][e.column], color=MINT) for e in events),
                run_time=self.anim,
            )
            if step == 0:
                self.explain(
                    "Only the first PE has matching inputs initially. Its first product enters the local accumulator. Later steps activate more PEs together."
                )
            self.play(FadeOut(tokens), run_time=0.25)
        self.explain(
            f"At the final step the {rows * columns} accumulators hold the same answers as ordinary matrix multiplication. Passing operands locally did not change the mathematics."
        )
        result = MatrixVisual(self.settings.c, "C").scale(0.75).move_to([4.4, -0.45, 0])
        self.explain(
            "Once a tile finishes, its outputs are captured. The accumulators can then be cleared for the next tile.",
            FadeIn(result),
            *(
                TransformFromCopy(grid.sums[i][j], result.at(i, j))
                for i in range(rows)
                for j in range(columns)
            ),
        )

    def scaling(self):
        self.slide(5)
        grid = PEGrid(2, cell=0.62, gap=0.12, show_sums=False).move_to([-1.8, -0.3, 0])
        facts = text("P = 2    P² = 4 PEs    up to 2P = 4 input words", 25).move_to(
            [1, -2.1, 0]
        )
        self.add(grid, facts)
        self.explain(
            "A P by P grid contains P squared processing elements. Doubling P gives four times as many arithmetic units."
        )
        for p in (4, 8):
            next_grid = PEGrid(
                p,
                cell=0.62 if p == 4 else 0.31,
                gap=0.12 if p == 4 else 0.06,
                show_sums=False,
            ).move_to(grid)
            self.explain(
                f"For P equal to {p}, that is {p * p} PEs. But a fully supplied boundary step may also need {2 * p} combined A and B words.",
                Transform(grid, next_grid),
                Transform(
                    facts,
                    text(
                        f"P = {p}    P² = {p * p} PEs    up to 2P = {2 * p} input words",
                        25,
                    ).move_to(facts),
                ),
            )
        self.explain(
            "Compute capacity grows with area, P squared. Peak boundary demand grows with edge length, 2P. We must compare both with the available input budget."
        )

    def bandwidth(self):
        self.slide(6)
        p = self.settings.data["presentation"]["grid_size"]
        budget = self.settings.data["presentation"]["input_budget"]
        grid = PEGrid(
            p, cell=min(0.37, (2.8 - (p - 1) * 0.06) / p), gap=0.06, show_sums=False
        ).move_to([2, -0.25, 0])
        count = 2 * p
        staged = VGroup(
            *(
                operand(
                    f"{'A' if i % 2 == 0 else 'B'}{i // 2}",
                    MINT if i % 2 == 0 else AMBER,
                ).scale(0.8)
                for i in range(count)
            )
        )
        staged.arrange_in_grid(rows=2, cols=p, buff=0.09).move_to([-2.65, -0.1, 0])
        staged.set_opacity(0.15)
        status = text("Grid holds its state", 23, AMBER).move_to([2, -2.1, 0])
        progress = text(f"0 / {count} words staged", 23).move_to([-2.65, -1.6, 0])
        self.add(grid, staged, status, progress)
        register = text("5", 32, MINT).move_to([5.1, -0.25, 0])
        inset = VGroup(
            Rectangle(width=1.8, height=1.3, color=MINT, stroke_width=1.5).move_to(
                register
            ),
            text("One PE register", 18, SOFT).move_to([5.1, 0.65, 0]),
            register,
            text("Illustrative values", 15, SOFT).move_to([5.1, -1.1, 0]),
        )
        self.add(inset)
        self.explain(
            f"Consider one full boundary step for a {p} by {p} grid. It needs {count} combined operand words. Our configured interface supplies at most {budget} words per physical clock."
        )
        received = 0
        for clock in range(1, (count + budget - 1) // budget + 1):
            stop = min(count, received + budget)
            self.explain(
                f"Physical clock {clock}: {stop} of {count} words are now staged. "
                + (
                    "The grid still holds all its registers."
                    if stop < count
                    else "The complete step is ready, so the grid can advance."
                ),
                *(staged[i].animate.set_opacity(1) for i in range(received, stop)),
                Transform(
                    progress,
                    text(f"{stop} / {count} words staged", 23).move_to(progress),
                ),
            )
            received = stop
        self.play(
            Transform(status, text("One logical advance", 23, MINT).move_to(status)),
            *(Indicate(row_cell, color=MINT) for row in grid.cells for row_cell in row),
            Transform(register, text("19", 32, MINT).move_to(register)),
            run_time=self.anim,
        )
        self.explain(
            "A clock is a hardware tick. The example register stayed at 5 while waiting. Only the completed input step allowed 5 plus 2 times 7 to become 19."
        )
        self.explain(
            "This example uses a full interior boundary step. Actual demand is smaller during fill and drain, so the complete cycle model counts every step separately."
        )

    def system_view(self):
        self.slide(7)
        a = operand("A", MINT).scale(1.5).move_to([-4, 0.2, 0])
        b = operand("B", AMBER).scale(1.5).move_to([-4, -0.6, 0])
        grid = PEGrid(2, cell=0.7, gap=0.2, show_sums=False).move_to([0, -0.2, 0])
        out = MatrixVisual(
            [["C00", "C01"], ["C10", "C11"]], "C", cell=0.7, number_size=18
        ).move_to([4, -0.2, 0])
        self.add(grid, out, a, b)
        self.explain(
            "The complete system must supply operands, perform arithmetic, and deliver results. Improving only the arithmetic leaves the other costs in the path.",
            a.animate.move_to([-1.2, 0.2, 0]),
            b.animate.move_to([-0.4, 1.2, 0]),
        )
        self.explain(
            "We will separate these costs: input stalls, the finite matrix schedule, tile capture, and serial readout. That makes the performance comparison explainable."
        )

    def tiling(self):
        self.slide(8)
        n = self.settings.data["presentation"]["tiling_order"]
        cell = 2.8 / n
        cells = VGroup(
            *(
                Rectangle(
                    width=cell * 0.92,
                    height=cell * 0.92,
                    color=EDGE,
                    stroke_width=0.8,
                    fill_opacity=0,
                ).move_to(
                    [
                        -2.3 + (j - (n - 1) / 2) * cell,
                        -0.55 + ((n - 1) / 2 - i) * cell,
                        0,
                    ]
                )
                for i in range(n)
                for j in range(n)
            )
        )
        self.add(cells, text(f"Complete C: {n} × {n}", 24).move_to([-2.3, 1.2, 0]))
        for p in (2, 4, 8):
            if p > n:
                continue
            tile = SurroundingRectangle(
                VGroup(*(cells[i * n + j] for i in range(p) for j in range(p))),
                color=MINT,
                buff=0.04,
            )
            explanation = text(
                f"{p} × {p} PEs\n{(n // p) ** 2} output tiles\nFull inner dimension K = {n}",
                25,
            ).move_to([3, 0.2, 0])
            self.explain(
                f"A {p} by {p} grid stores one output tile at a time. A complete {n} by {n} product requires {(n // p) ** 2} such tiles.",
                Create(tile),
                FadeIn(explanation),
            )
            if p == 2:
                self.explain(
                    "The tiles proceed across each row. Green entries have been captured and stay stored while the processing elements move on."
                )
            for row in range(0, n, p):
                for column in range(0, n, p):
                    active = VGroup(
                        *(
                            cells[i * n + j]
                            for i in range(row, row + p)
                            for j in range(column, column + p)
                        )
                    )
                    target = SurroundingRectangle(active, color=MINT, buff=0.04)
                    self.play(
                        Transform(tile, target),
                        *(cell.animate.set_fill(MINT, opacity=0.4) for cell in active),
                        run_time=0.22 if p == 2 else 0.4,
                    )
            if p == 2:
                self.explain(
                    "Each tile still streams the full inner dimension. Capture its results, clear the accumulators, then start the next output tile."
                )
            self.play(FadeOut(tile), FadeOut(explanation), run_time=0.3)
            if p != 8:
                self.play(
                    *(square.animate.set_fill(opacity=0) for square in cells),
                    run_time=0.3,
                )
        self.explain(
            "Tiling lets smaller hardware compute the same full answer. It changes scheduling and overhead; it does not discard matrix entries."
        )

    def correctness(self):
        self.slide(9)
        source = measured_results()
        dots = VGroup()
        for r, row in enumerate(source):
            for k in range(int(row["cases_passed"])):
                dots.add(
                    Dot(
                        [
                            -0.0 + (k - 3.5) * 0.22 + (r % 3 - 1) * 3.4,
                            1.25 - (r // 3) * 0.48,
                            0,
                        ],
                        radius=0.055,
                        color=SOFT,
                    )
                )
        self.add(dots)
        total = sum(int(row["cases_passed"]) for row in source)
        self.explain(
            f"The source RTL project records {len(source)} configurations, with eight numerical cases each: {total} passing cases. The reported results come from the saved source experiment.",
            *(d.animate.set_color(MINT) for d in dots),
        )
        self.explain(
            "Our animation model independently checks the matrix outputs and reproduces every recorded cycle schedule. It does not rerun Vivado or claim new FPGA measurements."
        )
        self.explain(
            "The word budget is a controlled RTL input model. It is not a measurement of physical KV260 memory bandwidth."
        )

    def results(self):
        self.slide(10)
        n = self.settings.data["presentation"]["workload_order"]
        p = self.settings.data["presentation"]["grid_size"]
        counts = [cycle_counts(n, p, b) for b in (4, 8, 16)]
        maximum = max(c.compute for c in counts)
        scale = 9.3 / maximum
        legend = (
            VGroup(
                text("Advance", 18, MINT),
                text("Stall", 18, BLUE),
                text("Capture", 18, AMBER),
            )
            .arrange(buff=0.55)
            .move_to([0, 1.15, 0])
        )
        self.add(legend)
        bars = VGroup()
        for row, c in enumerate(counts):
            y = 0.35 - row * 1.1
            cursor = -4.4
            group = VGroup()
            for value, color in (
                (c.advances, MINT),
                (c.stalls, BLUE),
                (c.captures, AMBER),
            ):
                if value:
                    rect = Rectangle(
                        width=value * scale,
                        height=0.35,
                        color=color,
                        fill_color=color,
                        fill_opacity=0.85,
                        stroke_width=0,
                    ).move_to([cursor + value * scale / 2, y, 0])
                    group.add(rect)
                    cursor += value * scale
            group.add(
                text(f"{c.budget} words/clock", 19).move_to([-5.5, y, 0]),
                text(str(c.compute), 24).move_to([cursor + 0.45, y, 0]),
            )
            bars.add(group)
        self.explain(
            f"Keep the same {p} by {p} grid and the same {n} by {n} product. The useful arithmetic does not change; only the input word budget changes.",
            FadeIn(bars),
        )
        reduction = (counts[0].compute - counts[-1].compute) / counts[0].compute * 100
        self.explain(
            f"The computed schedules are {counts[0].compute}, {counts[1].compute}, and {counts[2].compute} clocks. The blue stall segment shrinks as more operands arrive per clock."
        )
        self.explain(
            f"From the smallest to largest input budget, latency falls by {reduction:.0f} percent. The mint advance work and gold capture work remain unchanged."
        )

    def readout(self):
        self.slide(11)
        n = self.settings.data["presentation"]["workload_order"]
        p = self.settings.data["presentation"]["grid_size"]
        baseline = cycle_counts(n, 2, 16)
        candidate = cycle_counts(n, p, 16)
        matrix_grid = VGroup(
            *(
                Rectangle(
                    width=0.10,
                    height=0.10,
                    color=MINT,
                    fill_color=MINT,
                    fill_opacity=0.4,
                    stroke_width=0.4,
                ).move_to([-3.8 + j * 0.13, 1.0 - i * 0.13, 0])
                for i in range(n)
                for j in range(n)
            )
        )
        port = Line([-0.6, 1.15, 0], [-0.6, -1.2, 0], color=AMBER, stroke_width=4)
        counter = ValueTracker(0)
        count_text = always_redraw(
            lambda: text(
                f"{min(n * n, int(counter.get_value()))} / {n * n} outputs read", 26
            ).move_to([2.8, 0.25, 0])
        )
        self.add(matrix_grid, port, count_text)
        self.explain(
            "Computation finishing does not mean the whole answer has left the accelerator. The source design reads one output element per clock."
        )
        for index in range(min(4, n * n)):
            chip = Dot(matrix_grid[index].get_center(), radius=0.065, color=AMBER)
            self.add(chip)
            self.play(
                chip.animate.move_to([1.0, 0.25, 0]),
                counter.animate.set_value(index + 1),
                run_time=0.45,
                rate_func=linear,
            )
            self.remove(chip)
        self.explain(
            f"A complete {n} by {n} output has {n * n} elements. Serial delivery adds exactly {candidate.readout} clocks after compute. The counter now fast-forwards through the remaining outputs."
        )
        self.play(counter.animate.set_value(n * n), run_time=3, rate_func=linear)
        self.explain(
            f"At full supply, {candidate.compute} compute clocks become {candidate.total} clocks for the complete product. The same {n * n}-clock readout cost is included in the smaller-grid baseline."
        )
        self.play(
            FadeOut(matrix_grid), FadeOut(port), FadeOut(count_text), run_time=0.4
        )
        ratios = (
            VGroup(
                text(
                    f"{baseline.compute} / {candidate.compute} = {baseline.compute / candidate.compute:.2f}× compute speedup",
                    28,
                    MINT,
                ),
                text(
                    f"{baseline.total} / {candidate.total} = {baseline.total / candidate.total:.2f}× complete-product speedup",
                    28,
                    AMBER,
                ),
                text(f"{p * p} / 4 = {p * p / 4:g}× as many PEs and DSPs", 24, SOFT),
            )
            .arrange(np.array([0, -1, 0]), buff=0.45)
            .move_to([0, -0.2, 0])
        )
        self.explain(
            "Speedup means baseline clocks divided by candidate clocks. Including readout changes the result substantially, even though the arithmetic hardware is identical.",
            FadeIn(ratios),
        )

    def conclusion(self):
        self.slide(12)
        grid = PEGrid(4, cell=0.38, gap=0.07, show_sums=False).move_to([0, -0.2, 0])
        self.add(grid)
        self.explain(
            "Larger grids were fastest in the recorded sweep, but extra PEs did not produce proportional speedup. Operand supply, finite scheduling, and result delivery each limited the gain."
        )
        self.explain(
            "A smaller grid can be a deliberate choice when DSP resources matter more than minimum latency. The right answer depends on the complete workload and system constraints."
        )
        end = text(
            "Follow the operands. Count useful work. Include completion.", 28, MINT
        ).move_to([0, -2.1, 0])
        self.explain(
            "The matrix rule never changed. What changed was how quickly the system could feed, execute, and finish that rule.",
            FadeIn(end),
        )


class Presentation(SystolicStory):
    def construct(self):
        self.introduction()
        self.matrices()
        self.dataflow()
        self.scaling()
        self.bandwidth()
        self.system_view()
        self.tiling()
        self.correctness()
        self.results()
        self.readout()
        self.conclusion()


class Matrices(SystolicStory):
    def construct(self):
        self.matrices()


class Dataflow(SystolicStory):
    def construct(self):
        self.dataflow()
