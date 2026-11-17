"""The small explicit project registry used by the CLI.

Register a future project here without changing another project's model/scenes.
No Manim import is needed to list projects or inspect their configuration.
"""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path


@dataclass(frozen=True)
class Project:
    slug: str
    package: str
    description: str
    scenes: dict[str, tuple[str, str]]
    camera_scenes: tuple[str, ...] = ()

    def scene_file(self) -> Path:
        module = import_module(self.package)
        return Path(module.__file__).with_name("scenes.py")

    def load_settings(self, path: Path | None = None):
        return import_module(self.package + ".model").load_settings(path)


PROJECTS = {
    "intro": Project(
        slug="intro",
        package="animoz.projects.intro",
        description="Scene composition, equation-driven motion, and shared camera views.",
        scenes={
            "welcome": (
                "Welcome",
                "Build an animation from a model, scene, and camera.",
            ),
            "motion": ("Motion", "Watch an equation drive position and velocity."),
            "cameras": (
                "Cameras",
                "Replay one trajectory from three fixed viewpoints.",
            ),
        },
    ),
    "puerta-court": Project(
        slug="puerta-court",
        package="animoz.projects.puerta_court",
        description="Measured corner geometry, explicit motion physics, and selectable camera views.",
        scenes={
            "survey": (
                "SurveyFilm",
                "Explain the measured dimensions and open constraints.",
            ),
            "survey-view": (
                "SurveyView",
                "Inspect the same measured site from a selected viewpoint.",
            ),
            "physics": (
                "PhysicsFilm",
                "Explain speeds, stops, creep, and the limits of the evidence.",
            ),
            "replay": ("Replay", "Replay one motion model from any configured camera."),
        },
        camera_scenes=("survey-view", "replay"),
    ),
}
