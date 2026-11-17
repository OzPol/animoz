"""Export the Python model to an offline camera/time explorer without a server."""

import json
from importlib.resources import files
from pathlib import Path

from animoz.projects.puerta_court.model import Settings, Survey


def write_viewer(settings: Settings, output: Path) -> None:
    survey = Survey.load()
    count = max(2, round(settings.duration_seconds * 60))
    frames = []
    for i in range(count + 1):
        s = settings.state(settings.duration_seconds * i / count)
        frames.append(
            {
                "t": s.time,
                "x": s.front_x_in,
                "lo": s.bicycle_y_interval_in[0],
                "hi": s.bicycle_y_interval_in[1],
                "v": s.car_speed_in_s / 17.6,
                "a": s.car_acceleration_in_s2,
                "phase": s.phase,
            }
        )
    data = {
        "frames": frames,
        "views": settings.data["views"],
        "camera": settings.data["camera"],
        "duration": settings.duration_seconds,
        "presentation": settings.data["presentation"],
        "corner": survey.corner,
        "post": survey.post,
        "sidewalk": survey.sidewalk_edges,
        "joints": survey.slab_joints,
        "vehicle": {
            k: survey.value(v)
            for k, v in (("length", "V1"), ("width", "V2"), ("height", "V3"))
        },
        "residual": survey.closure_residual_in,
        "registered": settings.data["registration"]["enabled"],
        "lane": settings.data["registration"]["car_center_north_in"]
        if settings.data["registration"]["enabled"]
        else 0,
        "cross_x": sum(survey.sidewalk_edges) / 2
        if settings.data["registration"]["enabled"]
        else 0,
        "wall_north": survey.wall_north,
        "heights": survey.height_rulers,
    }
    template = files(__package__).joinpath("viewer.html").read_text()
    # Escape '<' even though the payload contains only validated model data.
    encoded = json.dumps(data, allow_nan=False).replace("<", "\\u003c")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("__MODEL_DATA__", encoded), encoding="utf-8")
