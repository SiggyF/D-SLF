import unittest

import numpy as np

from pyzsf import ZSFUnsteady


class TestSaltLoadUnsteady(unittest.TestCase):
    def setUp(self):
        self.parameters = {
            "lock_length": 240.0,
            "lock_width": 12.0,
            "lock_bottom": -4.0,
            "num_cycles": 24.0,
            "door_time_to_open": 300.0,
            "leveling_time": 300.0,
            "calibration_coefficient": 1.0,
            "symmetry_coefficient": 1.0,
            "ship_volume_sea_to_lake": 0.0,
            "ship_volume_lake_to_sea": 0.0,
            "head_sea": 0.0,
            "salinity_sea": 25.0,
            "temperature_sea": 15.0,
            "head_lake": 0.0,
            "salinity_lake": 5.0,
            "temperature_lake": 15.0,
            "flushing_discharge_high_tide": 0.0,
            "flushing_discharge_low_tide": 0.0,
            "density_current_factor_sea": 1.0,
            "density_current_factor_lake": 1.0,
        }

    @staticmethod
    def assert_allclose_loose(*args, **kwargs):
        return np.testing.assert_allclose(*args, **kwargs, rtol=0.01, atol=0.01)

    @staticmethod
    def assert_allclose_tight(*args, **kwargs):
        # For when results are supposed to be the same, but might be slightly
        # different due to the convergence criterion and/or numerical
        # inaccuries.
        return np.testing.assert_allclose(*args, **kwargs, rtol=1e-5, atol=1e-5)

    def test_flush_doors_closed(self):
        init_sal = 15.0

        c = ZSFUnsteady(init_sal, 0.0, **self.parameters)

        # Sanity check when flushing with no discharge
        duration = 1000.0
        c.step_flush_doors_closed(duration)
        self.assert_allclose_tight(c.state["salinity_lock"], init_sal)

        # Flushing with 1.0 m3/s for 0.0 seconds
        duration = 0.0
        c.step_flush_doors_closed(
            duration, flushing_discharge_low_tide=1.0, flushing_discharge_high_tide=1.0
        )
        self.assert_allclose_tight(c.state["salinity_lock"], init_sal)

        # Continue flushing with 1.0 m3/s, but for an insanely long amount of time
        duration = 1e9
        c.step_flush_doors_closed(duration)
        self.assert_allclose_tight(c.state["salinity_lock"], self.parameters["salinity_lake"])

    @unittest.expectedFailure
    def test_flush_doors_closed_rate_independent_of_absolute_salinity(self):
        # The salinity in a lock flushed with the doors closed should decay
        # as a well-mixed tank: c(t) = S_lake + (c0 - S_lake) * exp(-(Q/V) * t).
        # The decay rate Q/V does not depend on the absolute salinity, only on
        # the flushing discharge and the volume of water in the lock.
        #
        # Known bug: step_flush_doors_closed (src/zsf.c) computes the decay
        # rate as `flushing_discharge * sal_diff / saltmass_lock` instead of
        # `flushing_discharge / volume_water_in_lock`, so the rate incorrectly
        # scales with (sal_diff / sal_lock), making it decay too slowly
        # whenever salinity_lake > 0.
        def frac_removed(sal_lock, sal_lake):
            z = ZSFUnsteady(
                sal_lock,
                0.0,
                lock_length=100.0,
                lock_width=10.0,
                lock_bottom=-5.0,
                salinity_lake=sal_lake,
                salinity_sea=30.0,
                head_lake=0.0,
                head_sea=0.0,
            )
            z.step_flush_doors_closed(
                5000.0, flushing_discharge_low_tide=1.0, flushing_discharge_high_tide=1.0
            )
            c = z.state["salinity_lock"]
            return (sal_lock - c) / (sal_lock - sal_lake)

        # Same salinity difference (10), same V, Q and t in both cases, so the
        # fraction of excess salt removed should be identical.
        frac_low_absolute_salinity = frac_removed(sal_lock=10.0, sal_lake=0.0)
        frac_high_absolute_salinity = frac_removed(sal_lock=20.0, sal_lake=10.0)

        self.assert_allclose_tight(frac_low_absolute_salinity, frac_high_absolute_salinity)
