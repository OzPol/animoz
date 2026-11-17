# Intro: model, scene, and camera

The intro is a self-contained teaching project. Its numbers are generic examples.

| File | What to change |
| --- | --- |
| `src/animoz/projects/intro/project.toml` | Duration, starting position, initial velocity, and acceleration |
| `src/animoz/projects/intro/model.py` | Validate settings and construct the shared motion model |
| `src/animoz/projects/intro/scenes.py` | Presentation, camera angles, and graphical objects |
| `src/animoz/core/motion.py` | Shared kinematics |
| `src/animoz/rendering/clock.py` | Advance model time at one second per second of animated motion |

## 1. Welcome

`animoz render intro welcome`

Three animated cards introduce the model, scene, and camera layers. This is a
small example of composing text, shapes, and timed transitions.

## 2. Equation-driven motion

`animoz render intro motion`

The shared model calculates:

$$
s(t) = s_0 + v_0t + \frac{1}{2}at^2,\qquad v(t) = v_0 + at.
$$

The defaults are `s0 = 0 ft`, `v0 = 2 ft/s`, `a = 0.25 ft/s²`,
and `duration = 4 s`. At four seconds, position is **10 ft** and velocity is
**3 ft/s**. The marker, position readout, and velocity readout all use the
same model time.

The clip includes a short hold before and after the four-second motion.
Video playback time therefore includes those explanatory pauses.

## 3. One trajectory, three viewpoints

`animoz render intro cameras`

The same four-second trajectory is replayed from overhead, oblique, and side
views. Landmarks and the moving marker keep the same world coordinates.
One scale is used for all three spatial axes. The clock is reset before
each replay; camera transitions happen between replays.

## Change the example

Edit `project.toml`, then render again. A changed frame rate affects the
number of drawn frames, not the numerical trajectory.

You can also keep a separate settings file:

```toml
[motion]
duration_seconds = 3.0
start_feet = 0.0
initial_speed_feet_per_second = 3.0
acceleration_feet_per_second_squared = 0.0
```

```bash
animoz render intro motion --config my-settings.toml
```

That example travels **9 feet in 3 seconds**. Settings are validated before
Manim starts, and a copy is placed beside the output video. Every invocation
creates a new output directory automatically.

## Saved examples

The finished intro clips are committed under [videos/intro](../videos/intro/).
Their [render record](../videos/intro/render-info.json) contains the exact
settings, font, software versions, video dimensions, frame rates, and durations.
To create a different quality, use `--quality low`, `medium`, or `high`.

## Font sample

The scenes use **CMU Serif**. Uppercase, title case, lowercase, bold, and italic
examples appear in [the rendered font sample](images/cmu-serif.png).
Regenerate it from the repository root:

```bash
uv run --locked --extra manim python scripts/render_font_sample.py
```
