"""Join verified project chapters with fades, captions, and source records."""

import hashlib
import json
import re
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

from animoz.registry import PROJECTS


def seconds(stamp: str) -> float:
    hours, minutes, remainder = stamp.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(remainder.replace(",", "."))


def timestamp(value: float) -> str:
    milliseconds = round(value * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    whole, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole:02},{milliseconds:03}"


def probe(video: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,avg_frame_rate:format=duration",
            "-of",
            "json",
            str(video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def assemble(project: str, directory: Path) -> Path:
    definition = PROJECTS[project]
    if not definition.film_scenes:
        raise ValueError(
            "This project has no assembled film; render its scenes directly."
        )
    info = json.loads((directory / "render-info.json").read_text())
    if info["project"] != project:
        raise ValueError("The saved render record belongs to a different project.")
    settings = definition.load_settings()
    views = list(getattr(settings, "data", {}).get("views", {}))
    clips = []
    for alias in definition.film_scenes:
        selected = [v for v in info["videos"] if v["scene"] == alias]
        if not selected:
            raise ValueError(f"Missing saved chapter: {alias}")
        selected.sort(
            key=lambda v: (
                views.index(v["view"]) if v.get("view") in views else len(views)
            )
        )
        clips.extend(selected)
    sources = []
    for clip in clips:
        if Path(clip["file"]).name != clip["file"]:
            raise ValueError(
                "A clip must be a filename within the saved project directory."
            )
        path = directory / clip["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != clip["sha256"]:
            raise ValueError(f"Clip differs from its verified render record: {path}")
        sources.append(path)
    dimensions = {(v["width"], v["height"]) for v in clips}
    rates = [float(Fraction(v["frame_rate"])) for v in clips]
    frame_rate = round(rates[0])
    if (
        len(dimensions) != 1
        or frame_rate <= 0
        or any(abs(rate - frame_rate) > 0.1 for rate in rates)
    ):
        raise ValueError(
            "Render the chapters at the same quality before assembling them."
        )
    output = directory / "presentation.mp4"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    filters = []
    for index, (source, clip) in enumerate(zip(sources, clips, strict=True)):
        command.extend(["-i", str(source)])
        duration = clip["duration_seconds"]
        fade = min(0.25, duration / 4)
        filters.append(
            f"[{index}:v]fps={frame_rate},settb=AVTB,setpts=PTS-STARTPTS,fade=t=in:st=0:d={fade}:color=0xF8FAFC,fade=t=out:st={duration - fade}:d={fade}:color=0xF8FAFC[v{index}]"
        )
    filters.append(
        "".join(f"[v{i}]" for i in range(len(clips)))
        + f"concat=n={len(clips)}:v=1:a=0[film]"
    )
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".film-", suffix=".mp4", dir=directory, delete=False
        ) as handle:
            temporary = Path(handle.name)
        command.extend(
            [
                "-filter_complex",
                ";".join(filters),
                "-map",
                "[film]",
                "-an",
                "-c:v",
                "libx264",
                "-crf",
                "18",
                "-preset",
                "medium",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(temporary),
            ]
        )
        subprocess.run(command, check=True)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(temporary), "-f", "null", "-"],
            check=True,
            capture_output=True,
        )
        duration = float(probe(temporary)["format"]["duration"])
        expected = sum(clip["duration_seconds"] for clip in clips)
        if abs(duration - expected) > 0.2:
            raise RuntimeError(
                "Assembled duration does not match its component chapters."
            )
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    offset = 0.0
    cues = []
    chapters = []
    transcript = []
    for clip in clips:
        stem = Path(clip["file"]).stem
        title = clip["scene"].replace("-", " ").title() + (
            " / " + clip["view"] if clip.get("view") else ""
        )
        chapters.append({"title": title, "start_seconds": offset})
        captions = directory / (stem + "-captions.srt")
        if captions.exists():
            for block in re.split(r"\n\s*\n", captions.read_text().strip()):
                lines = block.splitlines()
                if len(lines) < 3:
                    continue
                start, end = lines[1].split(" --> ")
                cues.append(
                    (
                        offset + seconds(start),
                        offset + min(seconds(end), clip["duration_seconds"]),
                        "\n".join(lines[2:]),
                    )
                )
        else:
            cues.append(
                (
                    offset + 0.25,
                    offset + clip["duration_seconds"] - 0.25,
                    f"Same motion replayed from {clip.get('view', title)}. The clock restarts at zero.",
                )
            )
        reading = directory / (stem + "-transcript.md")
        transcript.append(
            "## "
            + title
            + "\n\n"
            + (reading.read_text() if reading.exists() else cues[-1][2])
        )
        offset += clip["duration_seconds"]
    srt = "\n\n".join(
        f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{text}"
        for i, (start, end, text) in enumerate(cues, 1)
    )
    (directory / "presentation-captions.srt").write_text(srt + "\n")
    (directory / "presentation-chapters.json").write_text(
        json.dumps(chapters, indent=2) + "\n"
    )
    (directory / "presentation-transcript.md").write_text(
        "# " + project + "\n\n" + "\n\n".join(transcript) + "\n"
    )
    (directory / "presentation-info.json").write_text(
        json.dumps(
            {
                "project": project,
                "file": output.name,
                "duration_seconds": duration,
                "transition": "0.25-second fades between component chapters",
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "components": [
                    {
                        key: c[key]
                        for key in ("file", "sha256", "duration_seconds", "settings")
                    }
                    for c in clips
                ],
            },
            indent=2,
        )
        + "\n"
    )
    return output
