"""Render a reproducible CMU Serif specimen for the documentation."""

from pathlib import Path

from manim import BOLD, ITALIC, Scene, tempconfig

from animoz.rendering.theme import BACKGROUND, FONT, INK, label


class FontSample(Scene):
    def construct(self) -> None:
        self.camera.background_color = BACKGROUND
        samples = (
            (FONT, 58, 3.15, {"weight": BOLD}),
            ("MANIM COMMUNITY EDITION", 42, 1.85, {}),
            ("Manim Community Edition", 46, 0.85, {}),
            ("manim community edition", 46, -0.15, {}),
            ("Manim Community Edition  |  Bold", 40, -1.45, {"weight": BOLD}),
            ("Manim Community Edition  |  Italic", 40, -2.45, {"slant": ITALIC}),
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZ   abcdefghijklmnopqrstuvwxyz", 22, -3.45, {}),
        )
        for text, size, y, style in samples:
            item = label(text, size, color=INK, **style).move_to([0, y, 0])
            if item.width > 13:
                item.scale_to_fit_width(13)
            self.add(item)


def main() -> None:
    destination = Path(__file__).resolve().parents[1] / "docs/images/cmu-serif.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempconfig(
        {
            "renderer": "cairo",
            "pixel_width": 1600,
            "pixel_height": 900,
            "format": "png",
            "output_file": str(destination),
            "media_dir": str(destination.parents[2] / "media/font-sample"),
            "verbosity": "WARNING",
        }
    ):
        FontSample().render()
    if not destination.exists():
        raise RuntimeError(f"Font sample was not created: {destination}")
    print(destination)


if __name__ == "__main__":
    main()
