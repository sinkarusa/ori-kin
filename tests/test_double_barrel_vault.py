"""Regression tests for the double-centered barrel vault (thesis §3.2)."""

import math
import unittest

from app.utils.barrel_vault_double import generate_double_barrel_vault_pattern
from app.utils.calculations import (
    calculate_alpha1_angle,
    calculate_alpha2_angle,
    calculate_beta_angle,
    calculate_height,
    calculate_segment_length,
)


def diagonal_segments(traces):
    return [t for t in traces if abs(t.x[1] - t.x[0]) > 1e-9
            and abs(t.y[1] - t.y[0]) > 1e-9]


def segment_key(trace, y_offset=0):
    points = sorted((round(float(x), 8), round(float(y) - y_offset, 8))
                    for x, y in zip(trace.x, trace.y))
    return tuple(points)


class DoubleBarrelVaultTests(unittest.TestCase):
    def test_thesis_table_3_10_obtuse_arch(self):
        r, a, n = 3, 2, 3
        theta = math.degrees(math.acos(a / (2 * r))) / n
        s = calculate_segment_length(r, theta)
        alpha1 = calculate_alpha1_angle(a, r, n)
        beta2 = calculate_beta_angle(a, r, n)
        alpha2 = calculate_alpha2_angle(beta2)
        self.assertAlmostEqual(theta, 23.5096, places=3)
        self.assertAlmostEqual(s, 1.222, places=3)
        self.assertAlmostEqual(alpha1, 11.7548, places=3)
        self.assertAlmostEqual(beta2, 117.548, places=3)
        self.assertAlmostEqual(alpha2, 31.226, places=3)

    def test_diagonals_have_one_apex_per_row_and_symmetric_positions(self):
        for a in (0, 1, 2, 3, 5.9):
            for n in (2, 3, 4):
                with self.subTest(a=a, n=n):
                    r = 3
                    theta = math.degrees(math.acos(a / (2 * r))) / n
                    s = calculate_segment_length(r, theta)
                    alpha1 = calculate_alpha1_angle(a, r, n)
                    alpha2 = calculate_alpha2_angle(calculate_beta_angle(a, r, n))
                    traces = generate_double_barrel_vault_pattern(r, n, 1, 180, a)
                    diagonals = diagonal_segments(traces)
                    self.assertEqual(len(diagonals), 2 * (2 * n - 1))
                    for k in range(1, 2 * n):
                        pair = [t for t in diagonals if math.isclose(
                            (t.x[0] + t.x[1]) / 2, k * s, abs_tol=1e-8)]
                        self.assertEqual(len(pair), 2)
                        target = alpha2 if k == n else alpha1
                        for t in pair:
                            angle = math.degrees(math.atan2(abs(t.y[1] - t.y[0]),
                                                            abs(t.x[1] - t.x[0])))
                            self.assertAlmostEqual(angle, target, places=7)
                        reflected = {tuple(sorted((round(float(x), 8), round(-float(y), 8))
                                                  for x, y in zip(t.x, t.y))) for t in pair}
                        self.assertEqual(reflected, {segment_key(t) for t in pair})
                    self.assertAlmostEqual(max(float(x) for t in traces for x in t.x), 2 * n * s)
                    self.assertGreaterEqual(min(float(x) for t in traces for x in t.x), -1e-9)

    def test_repeated_cells_and_outer_boundaries(self):
        r, a, n = 3, 2, 3
        s = calculate_segment_length(r, math.degrees(math.acos(a / (2 * r))) / n)
        h = calculate_height(s, calculate_alpha1_angle(a, r, n))
        single = diagonal_segments(generate_double_barrel_vault_pattern(r, n, 1, 180, a))
        for m in (1, 2, 3):
            with self.subTest(m=m):
                traces = generate_double_barrel_vault_pattern(r, n, m, 180, a)
                actual = {segment_key(t) for t in diagonal_segments(traces)}
                expected = {segment_key(t, -4 * h * i) for t in single
                            for i in range(-(m - 1), m)}
                self.assertEqual(actual, expected)
                self.assertEqual(len(actual), len(single) * (2 * m - 1))
                self.assertAlmostEqual(max(float(y) for t in traces for y in t.y), 2 * h * (2 * m - 1))
                self.assertAlmostEqual(min(float(y) for t in traces for y in t.y), -2 * h * (2 * m - 1))

    def test_invalid_geometry_and_segment_counts(self):
        for r, n, m, a in ((0, 3, 1, 2), (-1, 3, 1, 1), (3, 3, 1, -1),
                            (3, 3, 1, 6), (3, 3, 1, 7), (3, 0, 1, 2), (3, 1, 1, 2),
                            (3, 1.5, 1, 2), (3, 3, 0, 2), (3, 3, 1.5, 2)):
            with self.subTest(r=r, n=n, m=m, a=a):
                with self.assertRaises(ValueError):
                    generate_double_barrel_vault_pattern(r, n, m, 180, a)

    def test_omega_does_not_change_pointed_arch(self):
        a = generate_double_barrel_vault_pattern(3, 3, 1, 90, 2)
        b = generate_double_barrel_vault_pattern(3, 3, 1, 180, 2)
        self.assertEqual({segment_key(t) for t in a}, {segment_key(t) for t in b})


if __name__ == '__main__':
    unittest.main()
