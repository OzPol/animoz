import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from animoz.cli import main, output_directory
from animoz.projects.intro.model import load_settings
from animoz.registry import PROJECTS


class ProjectTests(unittest.TestCase):
    def test_default_settings_match_the_published_example(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
        self.assertEqual(settings.duration_seconds, 4.0)
        self.assertAlmostEqual(settings.motion().position(4), 10.0)

    def test_explicit_settings_override_packaged_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "custom.toml"
            path.write_text(
                "[motion]\nduration_seconds = 2\n"
                "initial_speed_feet_per_second = 3\n"
                "acceleration_feet_per_second_squared = 0\n"
            )
            self.assertEqual(load_settings(path).motion().position(2), 6)

    def test_settings_snapshot_preserves_the_trajectory(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.toml"
            path.write_text(settings.to_toml())
            restored = load_settings(path)
        self.assertEqual(restored, settings)
        for time in (0, 0.5, 2, 4):
            self.assertEqual(
                restored.motion().position(time), settings.motion().position(time)
            )

    def test_configuration_typos_and_invalid_values_fail_early(self):
        for content in (
            "[motion]\nduraton_seconds = 4",
            "[motion]\nduration_seconds = -1",
            "[motion]\nduration_seconds = true",
            "[motion]\nduration_seconds = 'four'",
            "[motion]\nduration_seconds = nan",
            "[other]\nduration_seconds = 4",
        ):
            with (
                self.subTest(content=content),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = Path(directory) / "bad.toml"
                path.write_text(content)
                with self.assertRaises(ValueError):
                    load_settings(path)

    def test_listing_and_unknown_scene_do_not_need_renderer_imports(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(["list"]), 0)
        self.assertIn("cameras", output.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["render", "intro", "missing"]), 2)

    def test_every_registered_project_has_a_scene_file(self):
        for project in PROJECTS.values():
            self.assertTrue(project.scene_file().is_file())

    def test_new_renders_never_overwrite_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            first = output_directory(Path(directory), "intro", "motion")
            existing = first / "existing.mp4"
            existing.write_bytes(b"previous render")
            second = output_directory(Path(directory), "intro", "motion")
            self.assertNotEqual(first, second)
            self.assertEqual(existing.read_bytes(), b"previous render")
