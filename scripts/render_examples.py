"""Render and verify every registered project without a duplicated CI project list."""

import argparse
from pathlib import Path

from verify_renders import verify

from animoz.cli import main
from animoz.registry import PROJECTS


def render_examples(quality: str, output: Path) -> None:
    for project in PROJECTS.values():
        command = ["render", project.slug, "all", "--quality", quality]
        if project.camera_scenes:
            command += ["--view", "all"]
        code = main(command)
        if code:
            raise SystemExit(code)
        verify(Path("media"), output / project.slug, project.slug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=["low", "medium", "high"], default="low")
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    render_examples(args.quality, args.output)
