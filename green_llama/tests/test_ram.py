import unittest
import numpy as np
from green_llama.metrics.hardware import RAM
from green_llama.metrics.energy_tracker import EnergyTracker


class TestRAMHardware(unittest.TestCase):
    def setUp(self) -> None:
        self.ram = RAM()

    def test_ram_power_measurement(self):
        # Test RAM power measurement using EnergyTracker
        energy_tracker = EnergyTracker()
        with energy_tracker:
            # Simulate memory allocation
            array = np.ones((1000, 1000), dtype=np.float32)
        ram_energy = energy_tracker.stop().ram
        self.assertGreaterEqual(ram_energy, 0.0, "RAM energy should be >= 0.")

    def test_ram_details(self):
        # Test RAM details retrieval
        ram_power = self.ram.get_power()
        self.assertGreaterEqual(ram_power, 0.0, "RAM power should be >= 0.")
