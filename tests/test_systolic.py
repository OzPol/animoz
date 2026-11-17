import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from animoz.projects.systolic_array.model import (
    boundary_words,
    cycle_counts,
    load_settings,
    measured_results,
    multiply,
    wavefront,
)


class SystolicTests(unittest.TestCase):
    def test_known_matrix_product_and_first_output_partial_sums(self):
        a, b = [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        self.assertEqual(multiply(a, b), ((19, 22), (43, 50)))
        events = [
            event
            for step in wavefront(a, b)
            for event in step
            if (event.row, event.column) == (0, 0)
        ]
        self.assertEqual([(e.before, e.after) for e in events], [(0, 5), (5, 19)])

    def test_rectangular_signed_matrices_and_matching_wavefront_indices(self):
        a = [[2, -1, 3], [0, 4, -2]]
        b = [[1, 2], [-3, 0], [2, 1]]
        self.assertEqual(multiply(a, b), ((11, 7), (-16, -2)))
        events = wavefront(a, b)
        self.assertEqual(sum(map(len, events)), 12)
        for step, group in enumerate(events):
            for e in group:
                self.assertEqual(step, e.row + e.column + e.inner)

    def test_every_saved_rtl_cycle_result_matches_independent_schedule(self):
        rows = measured_results()
        self.assertEqual(len(rows), 18)
        self.assertEqual(sum(int(row["cases_passed"]) for row in rows), 144)
        for row in rows:
            with self.subTest(config=row["config_id"]):
                counts = cycle_counts(int(row["N"]), int(row["P"]), int(row["B"]))
                for attribute, column in [
                    ("compute", "compute_cycles"),
                    ("total", "total_cycles"),
                    ("advances", "advance_cycles"),
                    ("stalls", "stall_cycles"),
                    ("captures", "capture_cycles"),
                ]:
                    self.assertEqual(getattr(counts, attribute), int(row[column]))

    def test_fill_full_boundary_and_drain_have_different_demands(self):
        self.assertEqual(boundary_words(0, 16, 8), 2)
        self.assertEqual(boundary_words(7, 16, 8), 16)
        self.assertEqual(boundary_words(22, 16, 8), 2)
        self.assertEqual(boundary_words(23, 16, 8), 0)
        self.assertEqual(cycle_counts(16, 8, 8).stalls, 60)
        self.assertEqual(cycle_counts(16, 8, 16).stalls, 0)

    def test_readout_and_complete_product_speedup_include_every_output(self):
        small, large = cycle_counts(16, 2, 16), cycle_counts(16, 8, 16)
        self.assertEqual(large.readout, 256)
        self.assertEqual(large.compute, 124)
        self.assertEqual(large.total, 380)
        self.assertAlmostEqual(small.compute / large.compute, 9.8064516129)
        self.assertAlmostEqual(small.total / large.total, 3.8736842105)

    def test_invalid_shapes_word_budgets_and_input_types_fail_early(self):
        for a, b in [
            ([], [[1]]),
            ([[1, 2], [3]], [[1], [2]]),
            ([[True]], [[1]]),
            ([[1]], [[1, 2], [3, 4]]),
        ]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                multiply(a, b)
        for args in [(8, 3, 8), (8, 16, 8), (8, 2, 0), (8, 2, True)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                cycle_counts(*args)

    def test_project_snapshot_preserves_the_example_and_schedule_inputs(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = load_settings()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.toml"
            path.write_text(settings.to_toml())
            self.assertEqual(load_settings(path), settings)
