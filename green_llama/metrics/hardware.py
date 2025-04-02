import psutil
import pynvml
from dataclasses import dataclass

@dataclass
class EnergyConsumption:
    cpu: float = 0.0
    gpu: float = 0.0
    ram: float = 0.0
    total: float = 0.0

class CPU:
    def __init__(self):
        self._cpu_power = 0.0
        
    def get_power(self):
        # Get CPU utilization using psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        # Assume 8W TDP per CPU core (adjust based on actual CPU)
        self._cpu_power = cpu_percent * psutil.cpu_count() * 8 / 100
        return self._cpu_power

class GPU:
    def __init__(self):
        self._gpu_power = 0.0
        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.has_gpu = True
        except:
            self.has_gpu = False

    def get_power(self):
        if not self.has_gpu:
            return 0.0
        try:
            return pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0  # Convert to watts
        except:
            return 0.0

class RAM:
    def __init__(self):
        self._ram_power = 0.0
        self.total_ram = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # Convert to GB
        
    def get_power(self):
        # Use 3W/8GB ratio for RAM power calculation
        ram_usage = psutil.virtual_memory().percent / 100
        self._ram_power = (self.total_ram * ram_usage * 3) / 8
        return self._ram_power