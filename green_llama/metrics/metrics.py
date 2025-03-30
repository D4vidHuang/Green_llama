
import time
import ollama
from .energy_tracker import EnergyTracker
from .emissions import EmissionsTracker

def measure_cpu_energy(func):
    """Decorator: Measure CPU energy consumption"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        energy_tracker = EnergyTracker()
        with energy_tracker:
            result = func(*args, **kwargs)
        end_time = time.time()
        return result, energy_tracker.stop().cpu, end_time - start_time
    return wrapper

def measure_gpu_energy(func):
    """Decorator: Measure GPU energy consumption"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        energy_tracker = EnergyTracker()
        with energy_tracker:
            result = func(*args, **kwargs)
        end_time = time.time()
        return result, energy_tracker.stop().gpu, end_time - start_time
    return wrapper

def measure_ram_energy(func):
    """Decorator: Measure RAM energy consumption"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        energy_tracker = EnergyTracker()
        with energy_tracker:
            result = func(*args, **kwargs)
        end_time = time.time()
        return result, energy_tracker.stop().ram, end_time - start_time
    return wrapper

def measure_total_energy(func):
    """Decorator: Measure total energy consumption"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        energy_tracker = EnergyTracker()
        with energy_tracker:
            result = func(*args, **kwargs)
        end_time = time.time()
        return result, energy_tracker.stop().total, end_time - start_time
    return wrapper

def measure_emissions(func):
    """Decorator: Measure carbon emissions"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        energy_tracker = EnergyTracker()
        emissions_tracker = EmissionsTracker()
        with energy_tracker:
            result = func(*args, **kwargs)
        end_time = time.time()
        energy = energy_tracker.stop()
        emissions = emissions_tracker.compute_emissions(energy.total)
        return result, emissions.emissions, end_time - start_time
    return wrapper

def measure_all_metrics(func):
    """Decorator: Measure all metrics (CPU, GPU, RAM energy, total energy, and carbon emissions)"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        energy_tracker = EnergyTracker()
        emissions_tracker = EmissionsTracker()
        with energy_tracker:
            result = func(*args, **kwargs)
        end_time = time.time()
        energy = energy_tracker.stop()
        emissions = emissions_tracker.compute_emissions(energy.total)
        return result, {
            "CPU Energy (J)": energy.cpu,
            "GPU Energy (J)": energy.gpu,
            "RAM Energy (J)": energy.ram,
            "Total Energy (J)": energy.total,
            "Carbon Emissions (gCO2)": emissions.emissions,
            "elapsed_time": end_time - start_time
        }
    return wrapper

@measure_all_metrics
def test_all(model: str, prompt: str):
    return ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

@measure_cpu_energy
def test_cpu(model: str, prompt: str):
    """Test function for CPU energy measurement"""
    return ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

@measure_gpu_energy
def test_gpu(model: str, prompt: str):
    """Test function for GPU energy measurement"""
    return ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

@measure_ram_energy
def test_ram(model: str, prompt: str):
    """Test function for RAM energy measurement"""
    return ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

@measure_total_energy
def test_total_energy(model: str, prompt: str):
    """Test function for total energy measurement"""
    return ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

@measure_emissions
def test_emissions(model: str, prompt: str):
    """Test function for carbon emissions measurement"""
    return ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])