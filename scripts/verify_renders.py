"""Check that each intro scene produced a playable, complete MP4.

Run after a fresh render of all introductory scenes:
    python scripts/verify_renders.py media
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from animoz.registry import PROJECTS
from animoz.runtime import load_runtime


def verify(root: Path, save_to: Path | None = None) -> None:
    font = load_runtime().font_family
    records = sorted(root.glob("intro/*/run.json"))
    latest = {}
    for path in records:
        record = json.loads(path.read_text())
        latest[record["scene"]] = (path, record)
    exported = []
    for alias in PROJECTS["intro"].scenes:
        if alias not in latest:
            raise RuntimeError(f"No render record for intro/{alias}.")
        path, record = latest[alias]
        if record["status"] != "completed" or record["exit_code"] != 0:
            raise RuntimeError(f"Render failed: {path}")
        if record.get("font") != font:
            raise RuntimeError(f"Render {alias} again using the current font ({font}).")
        if len(record["artifacts"]) != 1:
            raise RuntimeError(f"Expected one final MP4: {path}")
        video = path.parent / record["artifacts"][0]
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,width,height,avg_frame_rate:format=duration",
                "-of",
                "json",
                str(video),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        metadata = json.loads(probe.stdout)
        stream = metadata["streams"][0]
        if stream["codec_name"] != "h264":
            raise RuntimeError(f"Expected H.264 video: {video}")
        if stream["width"] <= 0 or stream["height"] <= 0:
            raise RuntimeError(f"Invalid video dimensions: {video}")
        duration = float(metadata["format"]["duration"])
        model_time = record["settings"]["duration_seconds"]
        minimum = {"welcome": 4.0, "motion": model_time, "cameras": 3 * model_time}[
            alias
        ]
        if duration + 0.15 < minimum:
            raise RuntimeError(f"Video appears incomplete: {video} ({duration}s)")
        print(
            f"Verified {alias}: {stream['width']}x{stream['height']}, {duration:.2f}s"
        )
        exported.append((video, record, stream, duration))
    # Copy only after all scenes pass. Partial Manim clips are never exported.
    if save_to is not None:
        save_to.mkdir(parents=True, exist_ok=True)
        info = {
            "project": "intro",
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "videos": [],
        }
        for video, record, stream, duration in exported:
            destination = save_to / (record["scene"] + ".mp4")
            shutil.copyfile(video, destination)
            info["videos"].append(
                {
                    "file": destination.name,
                    "scene": record["scene"],
                    "python": record["python"],
                    "manim": record["manim"],
                    "renderer": record["renderer"],
                    "font": record["font"],
                    "quality": record["quality"],
                    "settings": record["settings"],
                    "width": stream["width"],
                    "height": stream["height"],
                    "frame_rate": stream["avg_frame_rate"],
                    "duration_seconds": duration,
                    "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                }
            )
        (save_to / "render-info.json").write_text(json.dumps(info, indent=2) + "\n")
        print("Saved final videos and render-info.json to " + str(save_to.resolve()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument(
        "--save-to", type=Path, help="Copy the verified final clips here."
    )
    args = parser.parse_args()
    verify(args.root, args.save_to)
