import time
from .hardware import CPU, GPU, RAM, EnergyConsumption

class EnergyTracker:
    def __init__(self, measure_interval=1.0):
        self.measure_interval = measure_interval
        self.cpu = CPU()
        self.gpu = GPU()
        self.ram = RAM()
        self._start_time = None
        self._energy = EnergyConsumption()
        
    def start(self):
        self._start_time = time.time()
        self._energy = EnergyConsumption()
        
    def stop(self):
        if self._start_time is None:
            return self._energy
            
        duration = time.time() - self._start_time
        # Calculate energy consumption (power * time)
        self._energy.cpu = self.cpu.get_power() * duration / 3600  # Convert to kWh
        self._energy.gpu = self.gpu.get_power() * duration / 3600
        self._energy.ram = self.ram.get_power() * duration / 3600
        self._energy.total = self._energy.cpu + self._energy.gpu + self._energy.ram
        
        return self._energy

    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()