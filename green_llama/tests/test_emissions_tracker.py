import unittest
from green_llama.metrics.energy_tracker import EnergyTracker
from green_llama.metrics.emissions import EmissionsTracker


class TestEmissionsTracker(unittest.TestCase):
    def test_emissions_tracking(self):
        # Test emissions tracking with EnergyTracker and EmissionsTracker
        energy_tracker = EnergyTracker()
        emissions_tracker = EmissionsTracker(country_iso_code="USA")

        with energy_tracker:
            # Simulate a workload
            for _ in range(10**6):
                pass

        energy = energy_tracker.stop()
        emissions = emissions_tracker.compute_emissions(energy.total)

        self.assertGreater(energy.total, 0.0, "Total energy should be greater than 0.")
        self.assertGreater(emissions.emissions, 0.0, "Emissions should be greater than 0.")
