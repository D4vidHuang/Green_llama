import wmi
import subprocess
import time

def get_gpu_power_ohm():
    """ Retrieves GPU power consumption from Open Hardware Monitor (OHM) """
    c = wmi.WMI(namespace="root/OpenHardwareMonitor")
    sensors = c.Sensor()

    for sensor in sensors:
        if sensor.SensorType == "Power" and "GPU Power" in sensor.Name:
            return sensor.Value  # Returns GPU Power in Watts

    return None

def measure_ollama_energy(ollama_command):
    """ Runs Ollama and measures GPU power usage """
    print("Measuring baseline GPU power...")
    baseline_power = get_gpu_power_ohm()
    if baseline_power is None:
        print("Error: GPU Power sensor not found!")
        return

    print(f"Baseline GPU Power: {baseline_power} W")

    # Start measuring before launching Ollama
    start_time = time.time()
    power_samples = []

    print(f"Running Ollama command: {ollama_command}")
    process = subprocess.Popen(ollama_command, shell=True)

    # Measure GPU power while Ollama runs
    while process.poll() is None:
        power = get_gpu_power_ohm()
        if power:
            power_samples.append(power)
        time.sleep(1)  # Measure every second

    end_time = time.time()

    avg_power = sum(power_samples) / len(power_samples) if power_samples else 0
    duration = end_time - start_time
    energy_used = avg_power * duration / 3600  # Convert to watt-hours (Wh)

    print(f"Average GPU Power During Ollama: {avg_power:.2f} W")
    print(f"Ollama Execution Time: {duration:.2f} seconds")
    print(f"Estimated GPU Energy Consumption: {energy_used:.4f} Wh")

    return {
        "avg_power": avg_power,
        "duration": duration,
        "energy_used": energy_used
    }

# Example: Measure Ollama's power usage
ollama_cmd = "ollama run llama2 'What is the capital of France?'"
measure_ollama_energy(ollama_cmd)
