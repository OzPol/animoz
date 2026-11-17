"""A light canvas with dark text, shared across the introductory scenes."""

from manim import BOLD, Text, VGroup

from animoz.runtime import load_runtime

BACKGROUND = "#F8FAFC"
INK = "#17212B"
MUTED = "#536273"
GRID = "#CBD5E1"
TEAL = "#087F8C"
TEAL_LIGHT = "#D6F0F1"
GOLD = "#D59B24"
GOLD_LIGHT = "#FFF0CC"
PURPLE = "#7654AD"
PURPLE_LIGHT = "#ECE3F8"
FONT = load_runtime().font_family


def label(text: str, size: float = 24, color: str = INK, **kwargs) -> Text:
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def heading(title: str, subtitle: str) -> VGroup:
    title_mob = label(title, 38, weight=BOLD).move_to([0, 3.15, 0])
    subtitle_mob = label(subtitle, 20, MUTED).move_to([0, 2.55, 0])
    for item in (title_mob, subtitle_mob):
        if item.width > 12.5:
            item.scale_to_fit_width(12.5)
    return VGroup(title_mob, subtitle_mob)
