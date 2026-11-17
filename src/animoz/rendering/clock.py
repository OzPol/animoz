"""Advance model time explicitly, independently of frame rate and camera pose."""

from manim import Scene, ValueTracker, linear

from animoz.core.motion import elapsed_seconds


def run_clock(scene: Scene, clock: ValueTracker, duration_seconds: float) -> None:
    duration = elapsed_seconds(duration_seconds)
    if duration <= 0:
        raise ValueError("An animated replay requires a positive duration.")
    clock.set_value(0)
    scene.play(
        clock.animate.set_value(duration),
        run_time=duration,
        rate_func=linear,
    )
