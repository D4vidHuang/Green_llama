import time
import psutil
import threading
import ollama
from . import utils

def monitor_cpu_usage(stop_event, cpu_readings):
    while not stop_event.is_set():
        cpu_readings.append(psutil.cpu_percent(interval=0.1))

def measure_cpu_usage(model, prompt):
    stop_event = threading.Event()
    cpu_readings = []

    monitor_thread = threading.Thread(target=monitor_cpu_usage, args=(stop_event, cpu_readings))
    monitor_thread.start()

    start_time = time.time()
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    end_time = time.time()

    stop_event.set()
    monitor_thread.join()

    avg_cpu_usage = sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0
    elapsed_time = end_time - start_time

    return response, avg_cpu_usage, elapsed_time

def estimate_flops_per_sec(model, prompt):
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    end_time = time.time()
    elapsed_time = end_time - start_time

    estimated_flops = 10 ** 12
    flops_per_sec = estimated_flops / elapsed_time if elapsed_time > 0 else 0
    return response, flops_per_sec, elapsed_time

def real_time_monitoring(model, metric_name, measure_function, metrics_storage):
    while True:
        response, metric_value, elapsed_time = measure_function(model, "")
        metrics_storage["values"].append(metric_value)
        metrics_storage["times"].append(elapsed_time)
        utils.save_metrics_to_csv(metric_name, metric_value, elapsed_time)
        time.sleep(0.2)


def record_metrics(prompt,metrics_data, metrics_storage):
    for metric_name, metric_value in metrics_data.items():
        if metric_name in metrics_storage:
            metrics_storage[metric_name]["prompts"].append(prompt)
            metrics_storage[metric_name]["values"].append(metric_value)
            metrics_storage[metric_name]["times"].append(metrics_data["elapsed_time"])

def chat_monitoring(model, metric_name, measure_function, metrics_storage, prompt):
    """
    Executes the monitoring logic once based on the provided prompt.
    Updates metrics_storage with the results.
    """
    response, metric_value, elapsed_time = measure_function(model, prompt)
    metrics_storage["values"].append(metric_value)
    metrics_storage["times"].append(elapsed_time)
    utils.save_metrics_to_csv(metric_name, metric_value, elapsed_time)
    return response