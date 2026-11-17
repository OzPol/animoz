"""Validate and save final videos and their narration for any registered project."""

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from animoz.registry import PROJECTS
from animoz.runtime import load_runtime


def verify(root: Path, save_to: Path | None = None, project: str = "intro") -> None:
    font = load_runtime().font_family
    latest = {}
    for path in sorted(root.glob(f"{project}/*/run.json")):
        record = json.loads(path.read_text())
        latest[(record["scene"], record.get("view"))] = (path, record)
    expected = set(PROJECTS[project].scenes)
    found = {alias for alias, _ in latest}
    if expected - found:
        raise RuntimeError(
            "Missing scene renders: " + ", ".join(sorted(expected - found))
        )
    exported = []
    for (alias, view), (path, record) in sorted(
        latest.items(), key=lambda item: str(item[0])
    ):
        if alias not in expected:
            continue
        if record["status"] != "completed" or record["exit_code"] != 0:
            raise RuntimeError(f"Render failed: {path}")
        if record.get("font") != font:
            raise RuntimeError(f"Render {alias} again using the current font ({font}).")
        if len(record["artifacts"]) != 1:
            raise RuntimeError(f"Expected one final MP4: {path}")
        relative = Path(record["artifacts"][0])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"Invalid artifact path: {relative}")
        video = path.parent / relative
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
        duration = float(metadata["format"]["duration"])
        if (
            stream["codec_name"] != "h264"
            or min(stream["width"], stream["height"]) <= 0
            or duration <= 0
        ):
            raise RuntimeError(f"Invalid or empty H.264 video: {video}")
        if project == "intro":
            model_time = record["settings"]["duration_seconds"]
            minimum = {"welcome": 4.0, "motion": model_time, "cameras": 3 * model_time}[
                alias
            ]
            if duration + 0.15 < minimum:
                raise RuntimeError(f"Video appears incomplete: {video}")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"],
            check=True,
            capture_output=True,
        )
        print(
            f"Verified {alias}{'/' + view if view else ''}: {stream['width']}x{stream['height']}, {duration:.2f}s"
        )
        exported.append((video, path.parent, record, stream, duration))
    if save_to is None:
        return
    save_to.mkdir(parents=True, exist_ok=True)
    info = {
        "project": project,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "videos": [],
    }
    for video, run_dir, record, stream, duration in exported:
        stem = record["scene"] + ("-" + record["view"] if record.get("view") else "")
        destination = save_to / (stem + ".mp4")
        shutil.copyfile(video, destination)
        entry = {
            key: record[key]
            for key in (
                "scene",
                "python",
                "manim",
                "renderer",
                "font",
                "quality",
                "settings",
            )
        }
        entry.update(
            file=destination.name,
            view=record.get("view"),
            width=stream["width"],
            height=stream["height"],
            frame_rate=stream["avg_frame_rate"],
            duration_seconds=duration,
            sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
            sidecars=[],
        )
        for name in ("captions.srt", "chapters.json", "transcript.md"):
            source = run_dir / name
            if source.exists():
                target = save_to / (stem + "-" + name)
                shutil.copyfile(source, target)
                entry["sidecars"].append(target.name)
        info["videos"].append(entry)
    (save_to / "render-info.json").write_text(json.dumps(info, indent=2) + "\n")
    print("Saved verified videos, narration, and metadata to " + str(save_to.resolve()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--project", choices=PROJECTS, default="intro")
    parser.add_argument("--save-to", type=Path)
    args = parser.parse_args()
    verify(args.root, args.save_to, args.project)
