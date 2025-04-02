import unittest
import numpy as np
from green_llama.metrics.hardware import RAM
from green_llama.metrics.energy_tracker import EnergyTracker
from codecarbon import EmissionsTracker

class TestRAMHardware(unittest.TestCase):
    def setUp(self) -> None:
        self.ram = RAM()

    def test_ram_power_measurement(self):
        # Test RAM power measurement using EnergyTracker
        energy_tracker = EnergyTracker()
        emissions_tracker = EmissionsTracker()
        emissions_tracker.start()

        with energy_tracker:
            # Simulate memory allocation
            array = np.ones((1000, 1000), dtype=np.float32)
        ram_energy = energy_tracker.stop().ram
        ram_energy /= 3600000
        _ = emissions_tracker.stop()
        ram_energy_cc = round(emissions_tracker._total_ram_energy.kWh, 10)
        self.assertGreaterEqual(ram_energy, 0.0, "RAM energy should be >= 0.")
        self.assertAlmostEqual(
            ram_energy_cc, ram_energy, delta=0.0001,
            msg="EnergyTracker and EmissionsTracker GPU measurements differ significantly."
        )

    def test_ram_details(self):
        # Test RAM details retrieval
        ram_power = self.ram.get_power()
        self.assertGreaterEqual(ram_power, 0.0, "RAM power should be >= 0.")
