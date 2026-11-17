"""A small render entry point shared by every project."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from animoz.registry import PROJECTS
from animoz.runtime import load_runtime

QUALITIES = {"low": "-ql", "medium": "-qm", "high": "-qh"}


def output_directory(root: Path, project: str, scene: str) -> Path:
    """Create a fresh output directory; never overwrite an earlier render."""
    parent = root.expanduser().resolve() / project
    parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    return Path(tempfile.mkdtemp(prefix=f"{stamp}_{scene}_", dir=parent))


def doctor() -> int:
    ok = True
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    try:
        import manim
        import manimpango
        from packaging.requirements import Requirement

        print(f"Manim Community: {manim.__version__}")
        required_manim = next(
            Requirement(value)
            for value in metadata.requires("animoz") or []
            if Requirement(value).name == "manim"
        )
        if not required_manim.specifier.contains(manim.__version__):
            print("Use the locked environment: uv sync --locked --extra manim")
            ok = False
        runtime = load_runtime()
        font_found = runtime.font_family in manimpango.list_fonts()
        print(
            f"Font: {runtime.font_family} ({'available' if font_found else 'not installed'})"
        )
        if not font_found:
            print(
                f"Install {runtime.font_package} or rebuild the development container."
            )
            ok = False
    except (ImportError, OSError) as error:
        print(f"Manim: unavailable ({error})")
        print("Install the native prerequisites, then: uv sync --locked --extra manim")
        ok = False
    executable = shutil.which("ffmpeg")
    print("FFmpeg: " + (executable or "not found on PATH"))
    if executable is None:
        ok = False
    print("Intro scenes use text and vector shapes; LaTeX is optional.")
    return 0 if ok else 1


def render(args: argparse.Namespace) -> int:
    project = PROJECTS[args.project]
    if args.scene != "all" and args.scene not in project.scenes:
        print(
            f"Unknown scene {args.scene!r}. Choose: "
            + ", ".join(project.scenes)
            + ", all",
            file=sys.stderr,
        )
        return 2
    try:
        settings = project.load_settings(args.config)
        metadata.version("manim")
        import manimpango

        font = load_runtime().font_family
        if font not in manimpango.list_fonts():
            raise ValueError(f"Required font {font!r} is not installed.")
    except (ImportError, OSError, ValueError, metadata.PackageNotFoundError) as error:
        print(f"Cannot render: {error}", file=sys.stderr)
        print("Run 'animoz doctor' to check the environment.", file=sys.stderr)
        return 2
    aliases = project.scenes if args.scene == "all" else [args.scene]
    jobs = []
    try:
        camera_requested = args.view is not None or any(
            value is not None for value in (args.phi, args.theta, args.zoom)
        )
        for alias in aliases:
            if camera_requested and alias not in project.camera_scenes:
                if args.scene != "all":
                    raise ValueError(
                        "Camera controls apply to: " + ", ".join(project.camera_scenes)
                    )
                jobs.append((alias, settings, None))
                continue
            views = list(settings.data["views"]) if args.view == "all" else [args.view]
            for view in views:
                configured = (
                    settings.with_camera(view, args.phi, args.theta, args.zoom)
                    if camera_requested
                    else settings
                )
                name = configured.camera_id if alias in project.camera_scenes else None
                jobs.append((alias, configured, name))
    except (AttributeError, KeyError, ValueError) as error:
        print(f"Cannot configure render: {error}", file=sys.stderr)
        return 2
    for alias, settings, view in jobs:
        scene_class = project.scenes[alias][0]
        run_dir = output_directory(
            args.output_dir, project.slug, alias + ("_" + view if view else "")
        )
        manifest = {
            "project": project.slug,
            "scene": alias,
            "scene_class": scene_class,
            "view": view,
            "quality": args.quality,
            "python": sys.version.split()[0],
            "manim": metadata.version("manim"),
            "renderer": "cairo",
            "font": font,
            "settings": settings.as_dict(),
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "running",
        }
        # Snapshot the validated inputs so an edited source config cannot change a
        # render already in progress or give different inputs to later views.
        snapshot = run_dir / "settings.toml"
        snapshot.write_text(settings.to_toml(), encoding="utf-8")
        manifest_path = run_dir / "run.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        command = [
            sys.executable,
            "-m",
            "manim",
            "--renderer",
            "cairo",
            QUALITIES[args.quality],
            "--format",
            "mp4",
            "--verbosity",
            "WARNING",
            "--progress_bar",
            "none",
            "--media_dir",
            str(run_dir),
            str(project.scene_file()),
            scene_class,
        ]
        environment = os.environ.copy()
        environment["ANIMOZ_CONFIG"] = str(snapshot)
        print(f"Rendering {project.slug}/{alias} into {run_dir}", flush=True)
        try:
            result = subprocess.run(command, env=environment, check=False)
            code = result.returncode
        except KeyboardInterrupt:
            code = 130
        except OSError as error:
            print(f"Could not start Manim: {error}", file=sys.stderr)
            code = 1
        artifacts = [
            str(path.relative_to(run_dir))
            for path in sorted(run_dir.rglob("*.mp4"))
            if "partial_movie_files" not in path.parts
        ]
        if code == 0 and not artifacts:
            print("Manim exited without producing a final MP4.", file=sys.stderr)
            code = 1
        manifest.update(
            status="completed" if code == 0 else "failed",
            exit_code=code,
            finished_at_utc=datetime.now(timezone.utc).isoformat(),
            artifacts=artifacts,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        if code:
            return code
        for artifact in artifacts:
            print("Video: " + str(run_dir / artifact), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="animoz",
        description="List and render modular Manim Community projects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List the available projects and scenes.")
    subparsers.add_parser("doctor", help="Check Python, Manim, and FFmpeg.")
    views_parser = subparsers.add_parser(
        "views", help="List a project's camera presets."
    )
    views_parser.add_argument("project", choices=PROJECTS)
    assembly = subparsers.add_parser(
        "assemble", help="Join saved project chapters into one captioned film."
    )
    assembly.add_argument("project", choices=PROJECTS)
    assembly.add_argument("--directory", type=Path)
    explorer = subparsers.add_parser(
        "explore", help="Write an offline interactive Puerta Court viewer."
    )
    explorer.add_argument("project", choices=["puerta-court"])
    explorer.add_argument("--config", type=Path)
    explorer.add_argument(
        "--output", type=Path, default=Path("artifacts/puerta-court/viewer.html")
    )
    renderer = subparsers.add_parser(
        "render", help="Render a scene or a whole project."
    )
    renderer.add_argument("project", choices=PROJECTS)
    renderer.add_argument("scene", help="A listed scene alias, or 'all'.")
    renderer.add_argument("--quality", choices=QUALITIES, default="low")
    renderer.add_argument(
        "--config", type=Path, help="Override the project's TOML settings."
    )
    renderer.add_argument("--output-dir", type=Path, default=Path("media"))
    renderer.add_argument("--view", help="A camera preset, or all.")
    renderer.add_argument("--phi", type=float, help="Camera polar angle in degrees.")
    renderer.add_argument("--theta", type=float, help="Camera azimuth in degrees.")
    renderer.add_argument("--zoom", type=float, help="Positive camera zoom.")
    args = parser.parse_args(argv)
    if args.command == "list":
        for project in PROJECTS.values():
            print(f"{project.slug}: {project.description}")
            for alias, (_, description) in project.scenes.items():
                print(f"  {alias:10} {description}")
        return 0
    if args.command == "doctor":
        return doctor()
    if args.command == "views":
        settings = PROJECTS[args.project].load_settings()
        for name, pose in getattr(settings, "data", {}).get("views", {}).items():
            print(
                f"{name}: phi={pose['phi']:g}, theta={pose['theta']:g}, zoom={pose['zoom']:g}"
            )
        return 0
    if args.command == "assemble":
        from animoz.rendering.assemble import assemble

        try:
            video = assemble(
                args.project, args.directory or Path("videos") / args.project
            )
        except (
            OSError,
            ValueError,
            RuntimeError,
            subprocess.CalledProcessError,
        ) as error:
            print(f"Cannot assemble: {error}", file=sys.stderr)
            return 2
        print(video.resolve())
        return 0
    if args.command == "explore":
        from animoz.projects.puerta_court.explorer import write_viewer

        write_viewer(PROJECTS[args.project].load_settings(args.config), args.output)
        print(args.output.resolve())
        return 0
    return render(args)
