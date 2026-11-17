import math
import unittest

from animoz.core.motion import LinearMotion
from animoz.core.units import (
    feet_per_second_to_mph,
    feet_to_inches,
    inches_to_feet,
    mph_to_feet_per_second,
)


class UnitTests(unittest.TestCase):
    def test_known_speed_and_length_conversions(self):
        self.assertAlmostEqual(mph_to_feet_per_second(15), 22.0)
        self.assertAlmostEqual(mph_to_feet_per_second(-10), -44 / 3)
        self.assertAlmostEqual(feet_per_second_to_mph(22), 15.0)
        self.assertAlmostEqual(inches_to_feet(59), 59 / 12)
        self.assertAlmostEqual(feet_to_inches(5), 60.0)

    def test_nonfinite_units_are_rejected(self):
        for value in (math.inf, -math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                mph_to_feet_per_second(value)


class MotionTests(unittest.TestCase):
    def test_accelerated_trajectory_matches_independent_expected_values(self):
        motion = LinearMotion(0.0, 2.0, 0.25)
        self.assertEqual(motion.position(0), 0)
        self.assertAlmostEqual(motion.position(2), 4.5)
        self.assertAlmostEqual(motion.position(4), 10.0)
        self.assertAlmostEqual(motion.velocity(4), 3.0)

    def test_signed_motion_bounds_include_interior_reversal(self):
        motion = LinearMotion(0, 4, -2)
        self.assertEqual(motion.bounds(4), (0, 4))
        self.assertEqual(motion.position(4), 0)

    def test_negative_or_nonfinite_time_is_rejected(self):
        for time in (-0.1, math.inf, math.nan):
            with self.subTest(time=time), self.assertRaises(ValueError):
                LinearMotion(0, 2, 0.25).position(time)

    def test_nonfinite_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            LinearMotion(0, 2, math.nan)
