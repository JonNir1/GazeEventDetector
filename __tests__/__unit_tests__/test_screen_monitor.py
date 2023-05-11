import unittest
from Utils.ScreenMonitor import ScreenMonitor


class TestUtils(unittest.TestCase):

    def test__calc_angle_between_pixels(self):
        # implausible values
        d = 1
        sm = ScreenMonitor(width=10, height=10, resolution=(10, 10), refresh_rate=60)
        self.assertEqual(45, sm.calc_angle_between_pixels(d=d, p1=(0, 0), p2=(0, 1), use_radians=False))
        self.assertEqual(45, sm.calc_angle_between_pixels(d=d, p1=(0, 0), p2=(1, 0), use_radians=False))
        self.assertAlmostEqual(70.528779366, sm.calc_angle_between_pixels(d=d, p1=(0, 0), p2=(2, 2), use_radians=False))

        # plausible values
        d = 65
        sm = ScreenMonitor(width=53.5, height=31, resolution=(1920, 1080), refresh_rate=60)
        self.assertAlmostEqual(0.0247416922, sm.calc_angle_between_pixels(d=d, p1=(0, 1), p2=(1, 1), use_radians=False))
        self.assertAlmostEqual(0.0247416922, sm.calc_angle_between_pixels(d=d, p1=(1, 2), p2=(1, 1), use_radians=False))
        self.assertAlmostEqual(0.0349900345, sm.calc_angle_between_pixels(d=d, p1=(0, 0), p2=(1, 1), use_radians=False))

    def test__calc_visual_angle_radius(self):
        # TODO: implement
        pass