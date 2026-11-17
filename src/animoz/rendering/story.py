"""Timed explanations, captions, chapter marks, and coherent scene changes."""

import json
import textwrap
from pathlib import Path

from manim import DOWN, FadeIn, FadeOut, Scene, VGroup, config

from animoz.rendering.theme import BACKGROUND, INK, label


class ExplainedScene(Scene):
    """Animation cues also generate the video's SRT and reading transcript."""

    def setup(self) -> None:
        super().setup()
        self.camera.background_color = BACKGROUND
        self.caption = VGroup()
        self.cues: list[dict] = []
        self.chapters: list[dict] = []

    def explain(self, text: str, *animations, seconds: float | None = None) -> None:
        start = self.time
        if len(self.caption):
            self.play(FadeOut(self.caption), run_time=0.15)
        lines = textwrap.fill(text, width=94)
        self.caption = VGroup(
            label(lines, 21, getattr(self, "caption_color", INK))
        ).to_edge(DOWN, buff=0.28)
        self.play(FadeIn(self.caption), run_time=0.2)
        duration = seconds if seconds is not None else max(2.5, len(text.split()) / 2.7)
        if animations:
            animation_time = min(2.0, duration)
            self.play(*animations, run_time=animation_time)
            self.wait(max(0, duration - animation_time))
        else:
            self.wait(duration)
        self.cues.append({"start": start, "end": self.time, "text": text})

    def chapter(self, title: str) -> None:
        self.chapters.append({"title": title, "start_seconds": self.time})

    def clear_diagram(self, *, keep=()) -> None:
        keep = (*keep, self.caption)
        old = [m for m in self.mobjects if not any(m is item for item in keep)]
        if old:
            self.play(*(FadeOut(m) for m in old), run_time=0.55)

    def tear_down(self) -> None:
        destination = Path(config.media_dir)
        destination.mkdir(parents=True, exist_ok=True)

        def stamp(seconds: float) -> str:
            milliseconds = round(seconds * 1000)
            hours, milliseconds = divmod(milliseconds, 3600000)
            minutes, milliseconds = divmod(milliseconds, 60000)
            whole, milliseconds = divmod(milliseconds, 1000)
            return f"{hours:02}:{minutes:02}:{whole:02},{milliseconds:03}"

        subtitles = "\n\n".join(
            f"{i}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n{cue['text']}"
            for i, cue in enumerate(self.cues, 1)
        )
        (destination / "captions.srt").write_text(subtitles + "\n", encoding="utf-8")
        (destination / "chapters.json").write_text(
            json.dumps(self.chapters, indent=2) + "\n"
        )
        (destination / "transcript.md").write_text(
            "# "
            + self.__class__.__name__
            + "\n\n"
            + "\n\n".join(c["text"] for c in self.cues)
            + "\n"
        )
        super().tear_down()
