import wmi

def get_gpu_power_ohm():
    """ Retrieves GPU power consumption from Open Hardware Monitor (OHM) """
    c = wmi.WMI(namespace="root/OpenHardwareMonitor")
    sensors = c.Sensor()

    for sensor in sensors:
        if sensor.SensorType == "Power" and "GPU Power" in sensor.Name:
            print(f"Found GPU Power Sensor: {sensor.Name} - {sensor.Value} W")
            return sensor.Value  # Returns GPU Power in Watts

    print("GPU Power sensor not found!")
    return None

print(f"GPU Power: {get_gpu_power_ohm()} W")
