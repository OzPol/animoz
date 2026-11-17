"""Source-constrained geometry, explained kinematics, and camera-independent replays."""

import numpy as np
from manim import (
    DEGREES,
    Arrow,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Polygon,
    Rectangle,
    ThreeDScene,
    Transform,
    ValueTracker,
    VGroup,
    always_redraw,
)

from animoz.projects.puerta_court.model import Survey, load_settings
from animoz.rendering.clock import run_clock
from animoz.rendering.story import ExplainedScene
from animoz.rendering.theme import (
    BACKGROUND,
    GOLD,
    GRID,
    INK,
    MUTED,
    PURPLE,
    TEAL,
    TEAL_LIGHT,
    heading,
    label,
)


def point(x: float, y: float, scale: float, center=(0, 0), z=0) -> np.ndarray:
    return np.array([(x - center[0]) * scale, (y - center[1]) * scale, z * scale])


def dimension(start, end, text: str, color=MUTED, offset=(0, 0.18, 0)) -> VGroup:
    return VGroup(
        Line(start, end, color=color, stroke_width=1.5),
        label(text, 18, color).move_to((start + end) / 2 + np.array(offset)),
    )


def corner_diagram(scale=0.06, center=(47, 34)) -> tuple[VGroup, dict]:
    survey = Survey.load()
    points = {name: point(*xy, scale, center) for name, xy in survey.corner.items()}
    group = VGroup()
    group.add(
        DashedLine(points["O"], points["A"], color=GRID),
        DashedLine(points["O"], points["B"], color=GRID),
    )
    for left, right in zip(
        ("A", "Q1", "Q2", "Q3"), ("Q1", "Q2", "Q3", "B"), strict=True
    ):
        group.add(DashedLine(points[left], points[right], color=TEAL, dash_length=0.09))
    for name, p in points.items():
        group.add(
            Dot(p, radius=0.055, color=TEAL), label(name, 19).move_to(p + [0.2, 0.2, 0])
        )
    return group, points, lambda x, y: point(x, y, scale, center)


def site_world(scale=0.013, center=(35, 150)) -> VGroup:
    """All geometry uses the same inches-to-scene mapping in every view."""
    survey = Survey.load()

    def p(x, y, z=0):
        return point(x, y, scale, center, z)

    west, east = survey.sidewalk_edges
    joints = survey.slab_joints
    walk = Polygon(
        p(west, joints[0]),
        p(east, joints[0]),
        p(east, joints[-1]),
        p(west, joints[-1]),
        fill_color=TEAL_LIGHT,
        fill_opacity=0.65,
        stroke_color=GRID,
    )
    group = VGroup(walk)
    for y in joints:
        group.add(Line(p(west, y), p(east, y), color=GRID, stroke_width=1))
    for lower, upper in zip(joints[:-1], joints[1:], strict=True):
        group.add(
            label(f"{upper - lower:g} in", 15, MUTED).move_to(
                p((west + east) / 2, (lower + upper) / 2)
            )
        )
    a = survey.corner["A"][1]
    north = survey.wall_north
    group.add(Line(p(0, a), p(0, north), color=INK, stroke_width=3))
    group.add(Line(p(*survey.corner["B"]), p(240, 0), color=INK, stroke_width=3))
    names = ("A", "Q1", "Q2", "Q3", "B")
    for left, right in zip(names[:-1], names[1:], strict=True):
        group.add(
            DashedLine(
                p(*survey.corner[left]),
                p(*survey.corner[right]),
                color=TEAL,
                dash_length=0.06,
            )
        )
    for name in names:
        group.add(Dot(p(*survey.corner[name]), radius=0.035, color=TEAL))
    x, north_post, south_post = survey.post
    group.add(Line(p(x, north_post), p(x, south_post), color=GOLD, stroke_width=5))
    group.add(label("STOP post faces", 15, GOLD).move_to(p(x + 57, south_post - 14)))
    # Height rulers are measured local references, not an invented opaque wall.
    for x, y, height in survey.height_rulers:
        group.add(Line(p(x, y), p(x, y, height), color=PURPLE, stroke_width=2.5))
        group.add(
            label(f"{height:g} in height", 15, PURPLE).move_to(p(x + 25, y, height))
        )
    group.add(
        label("BENEVA (west)", 17, MUTED)
        .rotate(90 * DEGREES)
        .move_to(p(west - 24, 160))
    )
    group.add(label("PUERTA / ACCESS ROAD (east)", 16, MUTED).move_to(p(100, -36)))
    return group


class SurveyFilm(ExplainedScene):
    def construct(self) -> None:
        survey = Survey.load()
        self.chapter("One coordinate frame")
        title = heading(
            "Puerta Court: the measured corner",
            "East is right. North is up. Every view uses the same inches.",
        )
        diagram, points, map_xy = corner_diagram()
        self.add(title)
        self.explain(
            "Begin with the corner itself. A and B are the ends of the sampled bend. O is the intersection of the projected straight wall lines.",
            Create(diagram),
        )
        ew = dimension(
            points["O"] + [0, -0.5, 0], points["B"] + [0, -0.5, 0], "16 + 78 = 94 in"
        )
        ns = dimension(
            points["O"] + [-0.65, 0, 0],
            points["A"] + [-0.65, 0, 0],
            "68 − 8 = 60 in",
            offset=(-1.1, 0, 0),
        )
        self.explain(
            "The corner spans 94 inches east to west and 60 inches north to south. Those are perpendicular projections, not lengths along the bend.",
            FadeIn(ew),
            FadeIn(ns),
        )
        self.chapter("Measured samples and unresolved curvature")
        for name in ("Q1", "Q2", "Q3"):
            xy = survey.corner[name]
            anchor = map_xy(survey.post[0], xy[1])
            top = map_xy(survey.post[0], survey.corner["A"][1])
            offsets = VGroup(
                dimension(
                    anchor, points[name], f"{xy[0] - survey.post[0]:g} in E", GOLD
                ),
                dimension(
                    top,
                    anchor,
                    f"{survey.corner['A'][1] - xy[1]:g} in S",
                    GOLD,
                    offset=(-0.45, 0, 0),
                ),
            )
            marker = Dot(points[name], radius=0.10, color=GOLD)
            note = label(f"{name} = ({xy[0]:g}, {xy[1]:g}) in", 22, GOLD).move_to(
                [2.5, 1.85, 0]
            )
            self.explain(
                f"{name} is {xy[0] - survey.post[0]:g} inches east of the post reference and {survey.corner['A'][1] - xy[1]:g} inches south of A's level. The pair locates one sample, not a circular radius.",
                FadeIn(marker),
                FadeIn(note),
                FadeIn(offsets),
            )
            self.play(FadeOut(marker), FadeOut(note), FadeOut(offsets), run_time=0.25)
        self.explain(
            "The dotted connections only show the sample order. The exact curve, wall thickness, and wall returns remain unregistered. A smooth wall here would invent geometry."
        )
        self.chapter("Sidewalk and closure")
        full = site_world()
        self.explain(
            "Now widen the view to the straight wall and sidewalk. The marked slab lengths retain their measured proportions.",
            FadeOut(ew),
            FadeOut(ns),
            Transform(diagram, full),
        )
        residual = label(
            f"Open closure: {survey.closure_residual_in:g} in", 29, GOLD
        ).move_to([3, -1.55, 0])
        self.explain(
            "The 59-inch sidewalk width is measured. Its east-west placement here uses the documented 31-inch wall-face interpretation.",
            FadeIn(residual),
        )
        self.explain(
            "The wall and slab chain disagrees with the separate 12-inch post reference by 1.5 inches. We preserve that residual rather than shifting the drawing to hide it."
        )
        self.chapter("Scale and limits of visibility")
        self.play(FadeOut(residual), run_time=0.3)
        car = Rectangle(
            width=survey.value("V1") * 0.013,
            height=survey.value("V2") * 0.013,
            color=PURPLE,
            fill_color=PURPLE,
            fill_opacity=0.15,
        ).move_to([3, -0.8, 0])
        car_label = label("Avalon envelope\n197.2 × 72.8 in", 20, PURPLE).move_to(
            [3, -1.7, 0]
        )
        self.explain(
            "For scale, this car envelope uses the Toyota dimensions at the same inch scale. It is a size comparison inset, not a registered accident position.",
            FadeIn(car),
            FadeIn(car_label),
        )
        self.explain(
            "The driver is on the south side of a westbound car. The reported contact is on the front bumper near the passenger side of its centerline."
        )
        self.explain(
            "Driver-eye position, lane position, and the complete wall surface are still needed for a credible first-visibility calculation. Changing a camera cannot supply those measurements."
        )


class SurveyView(ThreeDScene):
    def construct(self) -> None:
        settings = load_settings()
        self.camera.background_color = BACKGROUND
        pose = settings.camera
        self.set_camera_orientation(
            phi=pose["phi"] * DEGREES, theta=pose["theta"] * DEGREES, zoom=pose["zoom"]
        )
        self.add(site_world())
        title = heading(
            "One measured site, different viewpoints",
            f"View: {settings.camera_id}   •   1 inch has one scale on every axis",
        )
        note = label(
            "Dotted bend = sample connections. Height lines = local measured references.",
            19,
            MUTED,
        ).move_to([0, -3.2, 0])
        self.add_fixed_in_frame_mobjects(title, note)
        self.wait(3)


class PhysicsFilm(ExplainedScene):
    def construct(self) -> None:
        settings = load_settings()
        m = settings.data["motion"]
        self.chapter("Speed is distance per second")
        title = heading(
            "Puerta Court: motion and timing",
            "An explicit motion hypothesis, separate from the measured site",
        )
        self.add(title)
        speed = m["car_peak_mph"] * 17.6
        bike = m["bicycle_mph"] * 17.6
        equation = label("1 mph = 17.6 inches per second", 32).move_to([0, 1.7, 0])
        self.explain(
            "A speed becomes meaningful when we translate it into distance covered in one second.",
            FadeIn(equation),
        )
        values = (
            VGroup(
                label(
                    f"Car peak: {m['car_peak_mph']:g} mph = {speed:g} in/s", 27, TEAL
                ),
                label(f"Bicycle: {m['bicycle_mph']:g} mph = {bike:g} in/s", 27, PURPLE),
            )
            .arrange(direction=np.array([0, -1, 0]), buff=0.35)
            .move_to([0, 0.3, 0])
        )
        self.explain(
            "These speeds are configurable hypotheses, not recovered accident measurements. At these settings the bicycle can cover much more distance during the same short interval.",
            FadeIn(values),
        )
        self.explain(
            "We now use one continuous clock: approach and brake, a full stop, a short creep, then another stop. Position follows the integral of velocity."
        )
        self.clear_diagram(keep=(title,))
        self.chapter("One clock controls position, speed and acceleration")
        axes = Axes(
            x_range=[0, settings.duration_seconds, 1],
            y_range=[0, max(speed, bike) * 1.1, 40],
            x_length=10.3,
            y_length=2.65,
            tips=False,
            axis_config={"color": GRID, "include_numbers": False},
        ).move_to([0, 0.4, 0])
        car_curve = axes.plot(
            lambda t: settings.state(t).car_speed_in_s,
            x_range=[0, settings.duration_seconds],
            color=TEAL,
            use_smoothing=False,
        )
        bike_curve = axes.plot(
            lambda t: bike, x_range=[0, settings.duration_seconds], color=PURPLE
        )
        labels = VGroup(
            label("speed (in/s)", 19, MUTED).move_to([-4.9, 2.1, 0]),
            label("elapsed seconds", 19, MUTED).move_to([4.3, -1.55, 0]),
            label(f"Bicycle: {m['bicycle_mph']:g} mph", 18, PURPLE).move_to(
                [3.4, 1.9, 0]
            ),
            label(f"Car peak: {m['car_peak_mph']:g} mph", 18, TEAL).move_to(
                [-3.4, -0.3, 0]
            ),
        )
        for t in range(int(settings.duration_seconds) + 1):
            labels.add(label(str(t), 15, MUTED).move_to(axes.c2p(t, 0) + [0, -0.22, 0]))
        for value in range(0, int(max(speed, bike) * 1.1) + 1, 40):
            labels.add(
                label(str(value), 15, MUTED).move_to(axes.c2p(0, value) + [-0.34, 0, 0])
            )
        self.add(axes, car_curve, bike_curve, labels)
        clock = ValueTracker(0)
        marker = always_redraw(
            lambda: Line(
                axes.c2p(clock.get_value(), 0),
                axes.c2p(clock.get_value(), bike * 1.05),
                color=GOLD,
            )
        )
        readout = always_redraw(
            lambda: label(
                f"t = {clock.get_value():.2f} s    car = {settings.state(clock.get_value()).car_speed_in_s / 17.6:.2f} mph",
                23,
            ).move_to([0, -1.75, 0])
        )
        self.add(marker, readout)
        self.explain(
            "The car-speed curve reaches zero during the stop. The bicycle continues to advance. The gold cursor keeps both motions synchronized."
        )
        run_clock(self, clock, settings.duration_seconds / m["playback_rate"]) if m[
            "playback_rate"
        ] == 1 else self.play(
            clock.animate.set_value(settings.duration_seconds),
            run_time=settings.duration_seconds / m["playback_rate"],
            rate_func=lambda t: t,
        )
        self.explain(
            "Acceleration changes the slope of the velocity curve. Braking and creep are smooth in this chosen model; their durations and peak speed come from the configuration."
        )
        self.chapter("Contact and visibility require geometry")
        self.explain(
            "The replay uses a band for the unmeasured contact offset. It does not silently choose a six-inch offset, a driver-eye position, or a bicycle length."
        )
        self.explain(
            "This is a kinematic study. It does not calculate impact forces, deformation, responsibility, or first visibility from incomplete geometry."
        )


class Replay(ThreeDScene):
    def construct(self) -> None:
        settings = load_settings()
        survey = Survey.load()
        self.camera.background_color = BACKGROUND
        pose = settings.camera
        self.set_camera_orientation(
            phi=pose["phi"] * DEGREES, theta=pose["theta"] * DEGREES, zoom=pose["zoom"]
        )
        scale = 1 / settings.data["presentation"]["replay_inches_per_scene_unit"]
        center = (
            survey.value("V1") / 2,
            settings.data["presentation"]["replay_center_north_in"],
        )

        def p(x, y, z=0):
            return point(x, y, scale, center, z)

        clock = ValueTracker(0)
        lane = (
            settings.data["registration"]["car_center_north_in"]
            if settings.data["registration"]["enabled"]
            else 0
        )
        length, width, height = (survey.value(k) for k in ("V1", "V2", "V3"))

        def car_shape():
            x = settings.state(clock.get_value()).front_x_in
            corners = [
                (x, lane - width / 2),
                (x + length, lane - width / 2),
                (x + length, lane + width / 2),
                (x, lane + width / 2),
            ]
            shape = VGroup(
                Polygon(
                    *(p(a, b) for a, b in corners),
                    color=TEAL,
                    fill_color=TEAL_LIGHT,
                    fill_opacity=0.7,
                )
            )
            for a, b in corners:
                shape.add(Line(p(a, b), p(a, b, height), color=TEAL, stroke_width=1))
            shape.add(
                Polygon(
                    *(p(a, b, height) for a, b in corners), color=TEAL, fill_opacity=0
                )
            )
            shape.add(
                Line(p(x, lane), p(x, lane + width / 2), color=GOLD, stroke_width=5)
            )
            return shape

        def bike_band():
            s = settings.state(clock.get_value())
            target = (
                sum(survey.sidewalk_edges) / 2
                if settings.data["registration"]["enabled"]
                else 0
            )
            lo, hi = s.bicycle_y_interval_in
            if hi == lo:
                return Dot(p(target, lo), radius=0.06, color=PURPLE)
            return VGroup(
                Line(p(target, lo), p(target, hi), color=PURPLE, stroke_width=7),
                Arrow(p(target, hi + 60), p(target, hi + 5), buff=0, color=PURPLE),
            )

        self.add(always_redraw(car_shape), always_redraw(bike_band))
        self.add(DashedLine(p(0, -340), p(0, 850), color=GRID, dash_length=0.08))
        title = heading(
            "Synchronized motion replay",
            f"{settings.camera_id} view   •   physical coordinates do not change with the camera",
        )
        status = always_redraw(
            lambda: label(
                f"t = {clock.get_value():.2f} s   |   {settings.state(clock.get_value()).phase}",
                22,
            ).move_to([0, -2.65, 0])
        )
        readout = always_redraw(
            lambda: label(
                f"Car: {settings.state(clock.get_value()).car_speed_in_s / 17.6:.2f} mph   Bicycle hypothesis: {settings.data['motion']['bicycle_mph']:g} mph",
                20,
                MUTED,
            ).move_to([0, -3.15, 0])
        )
        note = label(
            "Relative frame; site/lane pose unregistered. Purple band preserves the unknown contact offset.",
            17,
            MUTED,
        ).move_to([0, 2.02, 0])
        if settings.data["registration"]["enabled"]:
            note = label(
                "Site placement uses the explicit registration inputs; impact response and first visibility are not inferred.",
                17,
                MUTED,
            ).move_to([0, 2.02, 0])
        top_mask = Rectangle(
            width=128 / 9,
            height=2.25,
            fill_color=BACKGROUND,
            fill_opacity=1,
            stroke_width=0,
        ).move_to([0, 2.875, 0])
        bottom_mask = Rectangle(
            width=128 / 9,
            height=1.65,
            fill_color=BACKGROUND,
            fill_opacity=1,
            stroke_width=0,
        ).move_to([0, -3.175, 0])
        self.add_fixed_in_frame_mobjects(
            top_mask, bottom_mask, title, status, readout, note
        )
        self.wait(0.5)
        self.play(
            clock.animate.set_value(settings.duration_seconds),
            run_time=settings.duration_seconds
            / settings.data["motion"]["playback_rate"],
            rate_func=lambda t: t,
        )
        self.wait(1.0)
