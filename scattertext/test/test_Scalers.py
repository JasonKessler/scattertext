from unittest import TestCase
import numpy as np

from scattertext import stretch_0_to_1


class TestScalers(TestCase):
    def test_stretch_0_to_1(self):
        a = np.array([0.8, 0.5, 0., -0.2, -0.3, 0.4])
        out = stretch_0_to_1(a)
        np.testing.assert_almost_equal(out, np.array([1., 0.8125, 0.5, 0.16666667, 0., 0.75, ]))
        np.testing.assert_almost_equal(a, np.array([0.8, 0.5, 0., -0.2, -0.3, 0.4]))

        out = stretch_0_to_1(np.array([]))
        np.testing.assert_almost_equal(out, np.array([]))

        out = stretch_0_to_1(np.array([1, .5]))
        np.testing.assert_almost_equal(out, np.array([1., 0.75]))

        out = stretch_0_to_1(np.array([-1, -.5]))
        np.testing.assert_almost_equal(out, np.array([0, 0.25]))
