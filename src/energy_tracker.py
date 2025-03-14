import os
import json
from dataclasses import dataclass, asdict
from typing import Optional, Union, List
from contextlib import contextmanager

from codecarbon import EmissionsTracker, OfflineEmissionsTracker
from codecarbon.output import EmissionsData
import torch

POWER_CONSUMPTION_SAMPLING_RATE = 1.0  # seconds
ENERGY_UNIT = "kWh"

@dataclass
class Energy:
    unit: str
    cpu: float
    ram: float
    gpu: float
    total: float

class EnergyTracker:
    def __init__(self, device: str, backend: str, device_ids: Optional[Union[str, int, List[int]]] = None):
        self.device = device
        self.backend = backend
        self.device_ids = device_ids

        # Check GPU availability
        gpu_available = torch.cuda.is_available() if device == "cuda" else False
        if device == "cuda" and not gpu_available:
            print("\t\t+ GPU requested but not available, falling back to CPU-only mode")
            self.device = "cpu"
            self.device_ids = None

        self.is_gpu = self.device == "cuda"
        self.is_pytorch_cuda = (self.backend, self.device) == ("pytorch", "cuda")

        print("\t\t+ Tracking RAM and CPU energy consumption")

        if self.is_gpu:
            if isinstance(self.device_ids, str):
                self.device_ids = list(map(int, self.device_ids.split(",")))
            elif isinstance(self.device_ids, int):
                self.device_ids = [self.device_ids]
            elif isinstance(self.device_ids, list):
                self.device_ids = self.device_ids
            elif self.device_ids is None:
                raise ValueError("GPU device IDs must be provided for energy tracking on GPUs")
            else:
                raise ValueError("GPU device IDs must be a string, an integer, or a list of integers")

            print(f"\t\t+ Tracking GPU energy consumption on devices {self.device_ids}")

        try:
            self.emission_tracker = EmissionsTracker(
                log_level="warning",
                tracking_mode="machine",
                gpu_ids=self.device_ids,
                allow_multiple_runs=True,
                output_file="codecarbon.csv",
                measure_power_secs=POWER_CONSUMPTION_SAMPLING_RATE,
            )
        except Exception:
            print("\t\t+ Falling back to Offline Emissions Tracker")

            if os.environ.get("COUNTRY_ISO_CODE", None) is None:
                print(
                    "\t\t+ Offline Emissions Tracker requires COUNTRY_ISO_CODE to be set. "
                    "We will set it to USA but the carbon footprint might be inaccurate."
                )

            self.emission_tracker = OfflineEmissionsTracker(
                log_level="warning",
                tracking_mode="machine",
                gpu_ids=self.device_ids,
                allow_multiple_runs=True,
                output_file="codecarbon.csv",
                measure_power_secs=POWER_CONSUMPTION_SAMPLING_RATE,
                country_iso_code=os.environ.get("COUNTRY_ISO_CODE", "USA"),
            )

        self.total_energy: Optional[float] = None
        self.cpu_energy: Optional[float] = None
        self.gpu_energy: Optional[float] = None
        self.ram_energy: Optional[float] = None

    def reset(self):
        self.total_energy = None
        self.cpu_energy = None
        self.gpu_energy = None
        self.ram_energy = None

    @contextmanager
    def track(self, task_name: str = "task"):
        if self.is_pytorch_cuda:
            torch.cuda.synchronize()

        self.emission_tracker.start_task(task_name=task_name)

        yield

        if self.is_pytorch_cuda:
            torch.cuda.synchronize()

        emission_data: EmissionsData = self.emission_tracker.stop_task()

        with open(f"{task_name}_codecarbon.json", "w") as f:
            print(f"\t\t+ Saving codecarbon emission data to {task_name}_codecarbon.json")
            json.dump(asdict(emission_data), f, indent=4)

        self.total_energy = emission_data.energy_consumed
        self.cpu_energy = emission_data.cpu_energy
        self.gpu_energy = emission_data.gpu_energy
        self.ram_energy = emission_data.ram_energy

    def get_energy(self) -> Energy:
        assert self.total_energy is not None, "Energy must be tracked before calling this method"

        return Energy(
            unit=ENERGY_UNIT,
            cpu=self.cpu_energy,
            gpu=self.gpu_energy,
            ram=self.ram_energy,
            total=self.total_energy
        )