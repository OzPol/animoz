"""Three complete introductory scenes. No LaTeX installation is required."""

from math import ceil, floor

from manim import (
    DEGREES,
    DOWN,
    ORIGIN,
    UP,
    Arrow,
    Create,
    Cube,
    Dot,
    FadeIn,
    LaggedStart,
    NumberLine,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Scene,
    Sphere,
    ThreeDAxes,
    ThreeDScene,
    TracedPath,
    Transform,
    ValueTracker,
    VGroup,
    always_redraw,
)

from animoz.projects.intro.model import load_settings
from animoz.rendering.clock import run_clock
from animoz.rendering.theme import (
    BACKGROUND,
    GOLD,
    GOLD_LIGHT,
    GRID,
    MUTED,
    PURPLE,
    PURPLE_LIGHT,
    TEAL,
    TEAL_LIGHT,
    heading,
    label,
)


def extent(settings) -> tuple[float, float, float]:
    """One range calculated from the model, shared by both motion scenes."""
    lower, upper = settings.motion().bounds(settings.duration_seconds)
    span = max(upper - lower, 1.0)
    tick = max(1.0, ceil(span / 5.0))
    return floor(lower / tick) * tick, ceil(upper / tick) * tick + tick, tick


class Welcome(Scene):
    """Compose an explanatory video from three reusable layers."""

    def construct(self) -> None:
        self.camera.background_color = BACKGROUND
        title = heading("animoz", "An introduction to programmed animation")
        self.play(FadeIn(title), run_time=0.6)
        cards = VGroup()
        for x, name, detail, color in (
            (-4.4, "MODEL", "Units + equations", TEAL_LIGHT),
            (0, "SCENE", "Geometry + time", GOLD_LIGHT),
            (4.4, "CAMERA", "A chosen viewpoint", PURPLE_LIGHT),
        ):
            box = RoundedRectangle(
                width=3.6,
                height=1.8,
                corner_radius=0.18,
                stroke_color=GRID,
                fill_color=color,
                fill_opacity=1,
            ).move_to([x, 0, 0])
            name_mob = label(name, 28).move_to([x, 0.35, 0])
            detail_mob = label(detail, 19).move_to([x, -0.3, 0])
            cards.add(VGroup(box, name_mob, detail_mob))
        self.play(LaggedStart(*(FadeIn(card) for card in cards), lag_ratio=0.25))
        arrows = VGroup(
            Arrow([-2.5, 0, 0], [-1.9, 0, 0], buff=0, color=MUTED),
            Arrow([1.9, 0, 0], [2.5, 0, 0], buff=0, color=MUTED),
        )
        self.play(Create(arrows), run_time=0.5)
        footer = label("Change an input. Render the result.", 29).move_to([0, -2.05, 0])
        self.play(FadeIn(footer), run_time=0.5)
        self.wait(1.5)
        example = label("Next: let an equation move an object.", 23, MUTED)
        example.move_to([0, -2.85, 0])
        self.play(FadeIn(example), run_time=0.5)
        self.wait(1.5)


class Motion(Scene):
    """Use one numerical model to drive the marker and all displayed values."""

    def construct(self) -> None:
        self.camera.background_color = BACKGROUND
        settings = load_settings()
        motion = settings.motion()
        lower, upper, tick = extent(settings)
        title = heading(
            "Motion from an equation", "Feet and seconds, sampled on one clock"
        )
        equation = label("s(t) = s₀ + v₀t + ½at²", 34).move_to([0, 1.55, 0])
        parameters = label(
            f"s₀ = {motion.start_feet:g} ft     "
            f"v₀ = {motion.initial_speed_feet_per_second:g} ft/s     "
            f"a = {motion.acceleration_feet_per_second_squared:g} ft/s²",
            20,
            MUTED,
        ).move_to([0, 0.9, 0])
        line = NumberLine(
            x_range=[lower, upper, tick],
            length=10.8,
            include_numbers=False,
            include_tip=True,
            color=MUTED,
            stroke_width=2,
        ).shift(DOWN * 0.65)
        ticks = VGroup()
        for number in range(int(lower), int(upper) + 1, int(tick)):
            ticks.add(label(f"{number} ft", 18).move_to(line.n2p(number) + DOWN * 0.45))
        clock = ValueTracker(0)
        marker = Dot(radius=0.14, color=TEAL)
        marker.add_updater(
            lambda mob: mob.move_to(
                line.n2p(motion.position(clock.get_value())) + UP * 0.25
            )
        )
        marker.update()
        trail = TracedPath(marker.get_center, stroke_color=TEAL, stroke_width=5)
        readouts = VGroup(
            always_redraw(
                lambda: label(f"TIME\n{clock.get_value():.2f} s", 24).move_to(
                    [-4, -2.25, 0]
                )
            ),
            always_redraw(
                lambda: label(
                    f"POSITION\n{motion.position(clock.get_value()):.2f} ft", 24
                ).move_to([0, -2.25, 0])
            ),
            always_redraw(
                lambda: label(
                    f"VELOCITY\n{motion.velocity(clock.get_value()):.2f} ft/s", 24
                ).move_to([4, -2.25, 0])
            ),
        )
        footer = label("The marker and readouts use the same model time.", 18, MUTED)
        footer.move_to([0, -3.3, 0])
        self.add(
            title, equation, parameters, line, ticks, trail, marker, readouts, footer
        )
        self.wait(0.6)
        run_clock(self, clock, settings.duration_seconds)
        marker.clear_updaters()
        self.wait(1.0)


class Cameras(ThreeDScene):
    """Replay exactly the same model from overhead, oblique, and side views."""

    def construct(self) -> None:
        self.camera.background_color = BACKGROUND
        settings = load_settings()
        motion = settings.motion()
        lower, upper, tick = extent(settings)
        world_scale = 9 / (upper - lower)
        axes = ThreeDAxes(
            x_range=[lower, upper, tick],
            y_range=[-2, 2, 1],
            z_range=[0, 2, 1],
            x_length=9,
            y_length=4 * world_scale,
            z_length=2 * world_scale,
            axis_config={"color": GRID, "include_tip": False, "stroke_width": 1.5},
        )
        axes.shift(-axes.c2p((lower + upper) / 2, 0, 0))
        floor_mob = Polygon(
            axes.c2p(lower, -2, 0),
            axes.c2p(upper, -2, 0),
            axes.c2p(upper, 2, 0),
            axes.c2p(lower, 2, 0),
            fill_color="#E8EEF3",
            fill_opacity=0.65,
            stroke_color=GRID,
            stroke_width=1,
        )
        guide = Polygon(
            axes.c2p(lower, -0.1, 0.02),
            axes.c2p(upper, -0.1, 0.02),
            axes.c2p(upper, 0.1, 0.02),
            axes.c2p(lower, 0.1, 0.02),
            fill_color=TEAL_LIGHT,
            fill_opacity=1,
            stroke_width=0,
        )
        span = upper - lower
        landmarks = VGroup(
            Cube(
                side_length=0.7 * world_scale,
                fill_color=GOLD,
                fill_opacity=0.8,
                stroke_width=0.5,
            ).move_to(axes.c2p(lower + span * 0.28, 1.15, 0.35)),
            Cube(
                side_length=0.7 * world_scale,
                fill_color=PURPLE,
                fill_opacity=0.8,
                stroke_width=0.5,
            ).move_to(axes.c2p(lower + span * 0.72, -1.15, 0.35)),
        )
        clock = ValueTracker(0)
        marker = Sphere(radius=0.17 * world_scale, resolution=(8, 8), color=TEAL)
        marker.add_updater(
            lambda mob: mob.move_to(
                axes.c2p(motion.position(clock.get_value()), 0, 0.22)
            )
        )
        marker.update()
        self.add(floor_mob, guide, axes, landmarks, marker)
        title = heading(
            "One model. Three views.", "Only the camera changes between replays"
        )
        title_background = Rectangle(
            width=14.3,
            height=1.45,
            fill_color=BACKGROUND,
            fill_opacity=1,
            stroke_width=0,
        ).move_to([0, 3.2, 0])
        view_label = label("OVERHEAD", 26).move_to([-3.7, -2.75, 0])
        time_label = always_redraw(
            lambda: label(
                f"t = {clock.get_value():.2f} s     s = {motion.position(clock.get_value()):.2f} ft",
                22,
            ).move_to([2.5, -2.75, 0])
        )
        note = label(
            "Landmarks, dimensions, equations, and duration stay fixed.", 18, MUTED
        )
        note.move_to([0, -3.4, 0])
        self.add_fixed_in_frame_mobjects(
            title_background, title, view_label, time_label, note
        )
        views = (
            ("OVERHEAD", 0, -90),
            ("OBLIQUE", 65, -55),
            ("SIDE", 90, -90),
        )
        for i, (name, phi, theta) in enumerate(views):
            clock.set_value(0)
            marker.update()
            if i == 0:
                self.set_camera_orientation(
                    phi=phi * DEGREES,
                    theta=theta * DEGREES,
                    zoom=0.9,
                    frame_center=ORIGIN,
                )
            else:
                replacement = label(name, 26).move_to(view_label)
                self.play(Transform(view_label, replacement), run_time=0.25)
                self.move_camera(phi=phi * DEGREES, theta=theta * DEGREES, run_time=0.8)
            self.wait(0.35)
            run_clock(self, clock, settings.duration_seconds)
            self.wait(0.35)
        marker.clear_updaters()
