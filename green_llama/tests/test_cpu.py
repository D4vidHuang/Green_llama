import os
import sys
import unittest
from unittest import mock

from green_llama.metrics.hardware import CPU
from green_llama.metrics.energy_tracker import EnergyTracker


class TestCPUHardware(unittest.TestCase):
    def setUp(self) -> None:
        self.cpu = CPU()

    def test_cpu_power_measurement(self):
        # Test CPU power measurement using EnergyTracker
        energy_tracker = EnergyTracker()
        with energy_tracker:
            # Simulate a workload
            for _ in range(10**6):
                pass
        cpu_energy = energy_tracker.stop().cpu
        self.assertGreater(cpu_energy, 0.0, "CPU energy should be greater than 0.")

    @unittest.skipUnless(sys.platform.lower().startswith("lin"), "requires Linux")
    def test_cpu_details(self):
        # Test CPU details retrieval
        cpu_power = self.cpu.get_power()
        self.assertGreater(cpu_power, 0.0, "CPU power should be greater than 0.")
