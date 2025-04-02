import unittest
from unittest.mock import patch, MagicMock
from green_llama.metrics.metrics import (
    measure_cpu_energy,
    measure_gpu_energy,
    measure_ram_energy,
    measure_total_energy,
    measure_emissions,
    measure_all_metrics,
)


class TestMetricsDecorators(unittest.TestCase):
    @patch("green_llama.metrics.metrics.EnergyTracker")
    def test_measure_cpu_energy(self, mock_energy_tracker):
        # Mock the EnergyTracker behavior
        mock_energy_tracker.return_value.stop.return_value.cpu = 10.0
        mock_energy_tracker.return_value.__enter__ = MagicMock()
        mock_energy_tracker.return_value.__exit__ = MagicMock()

        @measure_cpu_energy
        def dummy_function():
            return "CPU Test"

        result, cpu_energy, elapsed_time = dummy_function()
        self.assertEqual(result, "CPU Test")
        self.assertEqual(cpu_energy, 10.0)
        self.assertGreater(elapsed_time, 0)

    @patch("green_llama.metrics.metrics.EnergyTracker")
    def test_measure_gpu_energy(self, mock_energy_tracker):
        # Mock the EnergyTracker behavior
        mock_energy_tracker.return_value.stop.return_value.gpu = 20.0
        mock_energy_tracker.return_value.__enter__ = MagicMock()
        mock_energy_tracker.return_value.__exit__ = MagicMock()

        @measure_gpu_energy
        def dummy_function():
            return "GPU Test"

        result, gpu_energy, elapsed_time = dummy_function()
        self.assertEqual(result, "GPU Test")
        self.assertEqual(gpu_energy, 20.0)
        self.assertGreater(elapsed_time, 0)

    @patch("green_llama.metrics.metrics.EnergyTracker")
    def test_measure_ram_energy(self, mock_energy_tracker):
        # Mock the EnergyTracker behavior
        mock_energy_tracker.return_value.stop.return_value.ram = 5.0
        mock_energy_tracker.return_value.__enter__ = MagicMock()
        mock_energy_tracker.return_value.__exit__ = MagicMock()

        @measure_ram_energy
        def dummy_function():
            return "RAM Test"

        result, ram_energy, elapsed_time = dummy_function()
        self.assertEqual(result, "RAM Test")
        self.assertEqual(ram_energy, 5.0)
        self.assertGreater(elapsed_time, 0)

    @patch("green_llama.metrics.metrics.EnergyTracker")
    def test_measure_total_energy(self, mock_energy_tracker):
        # Mock the EnergyTracker behavior
        mock_energy_tracker.return_value.stop.return_value.total = 50.0
        mock_energy_tracker.return_value.__enter__ = MagicMock()
        mock_energy_tracker.return_value.__exit__ = MagicMock()

        @measure_total_energy
        def dummy_function():
            return "Total Energy Test"

        result, total_energy, elapsed_time = dummy_function()
        self.assertEqual(result, "Total Energy Test")
        self.assertEqual(total_energy, 50.0)
        self.assertGreater(elapsed_time, 0)

    @patch("green_llama.metrics.metrics.EnergyTracker")
    @patch("green_llama.metrics.metrics.EmissionsTracker")
    def test_measure_emissions(self, mock_emissions_tracker, mock_energy_tracker):
        # Mock the EnergyTracker and EmissionsTracker behavior
        mock_energy_tracker.return_value.stop.return_value.total = 100.0
        mock_emissions_tracker.return_value.compute_emissions.return_value.emissions = 25.0
        mock_energy_tracker.return_value.__enter__ = MagicMock()
        mock_energy_tracker.return_value.__exit__ = MagicMock()

        @measure_emissions
        def dummy_function():
            return "Emissions Test"

        result, emissions, elapsed_time = dummy_function()
        self.assertEqual(result, "Emissions Test")
        self.assertEqual(emissions, 25.0)
        self.assertGreater(elapsed_time, 0)

    @patch("green_llama.metrics.metrics.EnergyTracker")
    @patch("green_llama.metrics.metrics.EmissionsTracker")
    def test_measure_all_metrics(self, mock_emissions_tracker, mock_energy_tracker):
        # Mock the EnergyTracker and EmissionsTracker behavior
        mock_energy_tracker.return_value.stop.return_value = MagicMock(
            cpu=10.0, gpu=20.0, ram=5.0, total=35.0
        )
        mock_emissions_tracker.return_value.compute_emissions.return_value.emissions = 8.0
        mock_energy_tracker.return_value.__enter__ = MagicMock()
        mock_energy_tracker.return_value.__exit__ = MagicMock()

        @measure_all_metrics
        def dummy_function():
            return "All Metrics Test"

        result, metrics = dummy_function()
        self.assertEqual(result, "All Metrics Test")
        self.assertEqual(metrics["CPU Energy (kWh)"], 10.0)
        self.assertEqual(metrics["GPU Energy (kWh)"], 20.0)
        self.assertEqual(metrics["RAM Energy (kWh)"], 5.0)
        self.assertEqual(metrics["Total Energy (kWh)"], 35.0)
        self.assertEqual(metrics["Carbon Emissions (kgCO2)"], 8.0)
        self.assertGreater(metrics["elapsed_time"], 0)
