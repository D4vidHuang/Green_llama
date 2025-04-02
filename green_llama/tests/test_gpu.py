import unittest
from unittest import mock
from green_llama.metrics.hardware import GPU
from green_llama.metrics.energy_tracker import EnergyTracker
from codecarbon import EmissionsTracker


class TestGPUHardware(unittest.TestCase):
    def setUp(self) -> None:
        self.gpu = GPU()

    def test_gpu_power_measurement(self):
        # Test GPU power measurement using EnergyTracker
        energy_tracker = EnergyTracker()
        emissions_tracker = EmissionsTracker()
        emissions_tracker.start()
        with energy_tracker:
            # Simulate a workload
            for _ in range(10**6):
                pass
        gpu_energy = energy_tracker.stop().gpu
        gpu_energy /= 3600000
        _ = emissions_tracker.stop()
        gpu_energy_cc = round(emissions_tracker._total_gpu_energy.kWh, 10)
        self.assertGreaterEqual(gpu_energy, 0.0, "GPU energy should be >= 0.")
        self.assertAlmostEqual(
            gpu_energy_cc, gpu_energy, delta=0.0001,
            msg="EnergyTracker and EmissionsTracker GPU measurements differ significantly."
        )

    def test_gpu_details(self):
        # Test GPU details retrieval
        if self.gpu.has_gpu:
            gpu_power = self.gpu.get_power()
            self.assertGreaterEqual(gpu_power, 0.0, "GPU power should be >= 0.")
        else:
            self.skipTest("No GPU available on this system.")
