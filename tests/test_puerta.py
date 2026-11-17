import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from animoz.projects.puerta_court.explorer import write_viewer
from animoz.projects.puerta_court.model import Survey, load_settings


class PuertaTests(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {}, clear=True):
            self.settings = load_settings()

    def test_known_corner_constraints_and_open_closure(self):
        survey = Survey.load()
        self.assertEqual(survey.corner["A"], (0, 60))
        self.assertEqual(survey.corner["B"], (94, 0))
        self.assertEqual(survey.corner["Q1"], (55, 39))
        self.assertEqual(survey.corner["Q2"], (58, 22))
        self.assertEqual(survey.corner["Q3"], (68, 1))
        self.assertEqual(survey.closure_residual_in, 1.5)
        self.assertEqual(survey.sidewalk_edges, (-90, -31))

    def test_position_derivative_matches_signed_velocity(self):
        for t in (0.4, 1.4, 3.4, 4.4):
            dt = 1e-5
            derivative = (
                self.settings.state(t + dt).front_x_in
                - self.settings.state(t - dt).front_x_in
            ) / (2 * dt)
            self.assertAlmostEqual(
                derivative, -self.settings.state(t).car_speed_in_s, places=5
            )
            acceleration = -(
                self.settings.state(t + dt).car_speed_in_s
                - self.settings.state(t - dt).car_speed_in_s
            ) / (2 * dt)
            self.assertAlmostEqual(
                acceleration, self.settings.state(t).car_acceleration_in_s2, places=5
            )

    def test_stop_and_creep_are_continuous_and_forward_only(self):
        values = [
            self.settings.state(i * self.settings.duration_seconds / 700)
            for i in range(701)
        ]
        self.assertTrue(
            all(
                a.front_x_in >= b.front_x_in - 1e-10 for a, b in zip(values, values[1:])
            )
        )
        for t in (2, 2.5, 3, 5, 6):
            self.assertAlmostEqual(self.settings.state(t).car_speed_in_s, 0)
        for t in (2, 3, 5):
            a = self.settings.state(t - 1e-7)
            b = self.settings.state(t + 1e-7)
            self.assertAlmostEqual(a.front_x_in, b.front_x_in, places=5)
        self.assertEqual(self.settings.state(5).front_x_in, 0)

    def test_camera_changes_never_change_physical_states(self):
        changed = self.settings.with_camera("beneva", 45, -130, 1.25)
        for t in (0, 1, 2.5, 4, 5, 7):
            self.assertEqual(changed.state(t), self.settings.state(t))

    def test_contact_offset_remains_an_interval_when_unregistered(self):
        lo, hi = self.settings.state(5).bicycle_y_interval_in
        self.assertEqual(lo, 0)
        self.assertAlmostEqual(hi, 36.4)
        self.assertFalse(self.settings.data["registration"]["enabled"])

    def test_snapshot_and_offline_viewer_are_self_contained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "settings.toml"
            snapshot.write_text(self.settings.to_toml())
            self.assertEqual(load_settings(snapshot), self.settings)
            output = root / "viewer.html"
            write_viewer(self.settings, output)
            html = output.read_text()
            self.assertNotIn("__MODEL_DATA__", html)
            self.assertNotIn("<script src=", html)

    def test_unknown_inputs_and_nonfinite_camera_are_rejected(self):
        with self.assertRaises(ValueError):
            self.settings.with_camera("missing", None, None, None)
        with self.assertRaises(ValueError):
            self.settings.with_camera(None, float("nan"), None, None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.toml"
            path.write_text("[motion]\ncar_peak_mph=true")
            with self.assertRaises(ValueError):
                load_settings(path)
