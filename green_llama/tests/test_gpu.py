import unittest
from unittest import mock
from green_llama.metrics.hardware import GPU
from green_llama.metrics.energy_tracker import EnergyTracker


class TestGPUHardware(unittest.TestCase):
    def setUp(self) -> None:
        self.gpu = GPU()

    def test_gpu_power_measurement(self):
        # Test GPU power measurement using EnergyTracker
        energy_tracker = EnergyTracker()
        with energy_tracker:
            # Simulate a workload
            for _ in range(10**6):
                pass
        gpu_energy = energy_tracker.stop().gpu
        self.assertGreaterEqual(gpu_energy, 0.0, "GPU energy should be >= 0.")

    def test_gpu_details(self):
        # Test GPU details retrieval
        if self.gpu.has_gpu:
            gpu_power = self.gpu.get_power()
            self.assertGreaterEqual(gpu_power, 0.0, "GPU power should be >= 0.")
        else:
            self.skipTest("No GPU available on this system.")
