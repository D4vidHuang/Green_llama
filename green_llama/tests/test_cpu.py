import os
import sys
import unittest
from unittest import mock

from codecarbon import EmissionsTracker
from green_llama.metrics.hardware import CPU
from green_llama.metrics.energy_tracker import EnergyTracker


class TestCPUHardware(unittest.TestCase):
    def setUp(self) -> None:
        self.cpu = CPU()

    def test_cpu_power_measurement(self):
        # Test CPU power measurement using EnergyTracker
        energy_tracker = EnergyTracker()
        emissions_tracker = EmissionsTracker()
        emissions_tracker.start()

        with energy_tracker:
            # Simulate a workload
            for _ in range(10**6):
                pass
        cpu_energy = energy_tracker.stop().cpu
        ram_energy = energy_tracker.stop().ram
        _ = emissions_tracker.stop()
        cpu_energy_cc = round(emissions_tracker._total_cpu_energy.kWh, 10)
        # convert to KWh
        cpu_energy /= 3600000
        self.assertGreater(cpu_energy, 0.0, "CPU energy should be greater than 0.")
        print(f"CPU Energy: {cpu_energy:.10f}, CPU Energy CC: {cpu_energy_cc:.10f}")
        # print(f"RAM Energy: {ram_energy:.10f}, RAM Energy CC: {ram_energy_cc:.10f}")
        self.assertAlmostEqual(
            cpu_energy_cc, cpu_energy, delta=0.0001,
            msg="EnergyTracker and EmissionsTracker GPU measurements differ significantly."
        )

    @unittest.skipUnless(sys.platform.lower().startswith("lin"), "requires Linux")
    def test_cpu_details(self):
        # Test CPU details retrieval
        cpu_power = self.cpu.get_power()
        self.assertGreater(cpu_power, 0.0, "CPU power should be greater than 0.")
