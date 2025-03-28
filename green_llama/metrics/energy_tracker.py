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
        self._energy.cpu = self.cpu.get_power() * duration / (3600 * 1000)  # Convert to kWh
        self._energy.gpu = self.gpu.get_power() * duration / (3600 * 1000)
        self._energy.ram = self.ram.get_power() * duration / (3600 * 1000)
        self._energy.total = self._energy.cpu + self._energy.gpu + self._energy.ram
        
        return self._energy

    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

import time

def main():
    """
    Test the EnergyTracker class by simulating a workload.
    """
    print("Starting energy tracking test...")
    
    # Initialize the EnergyTracker
    tracker = EnergyTracker()

    # Start tracking energy
    with tracker:
        # Simulate a workload (e.g., a model inference or computation)
        print("Simulating workload...")
        time.sleep(5)  # Simulate a 5-second workload

    tracker.stop()
    energy = tracker._energy
    # Print the results
    print(f"CPU Energy Consumption: {energy.cpu:.6f} kWh")
    print(f"GPU Energy Consumption: {energy.gpu:.6f} kWh")
    print(f"RAM Energy Consumption: {energy.ram:.6f} kWh")
    print(f"Total Energy Consumption: {energy.total:.6f} kWh")

if __name__ == "__main__":
    main()