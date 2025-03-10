import time
import psutil
import ollama
import csv
import threading
import matplotlib.pyplot as plt
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live


def list_available_models():
    """List available models."""
    models = ollama.list()
    return [model['model'] for model in models['models']]


def download_model(model_name):
    """Download a model if not available."""
    console = Console()
    console.print(f"[yellow]Downloading model {model_name}...[/yellow]")
    ollama.pull(model_name)
    console.print(f"[green]Model {model_name} downloaded successfully![/green]")



def monitor_cpu_usage(stop_event, cpu_readings):
    """Continuously monitor CPU usage until stop_event is set."""
    while not stop_event.is_set():
        cpu_readings.append(psutil.cpu_percent(interval=0.1))


def measure_cpu_usage(model, prompt):
    """Measure CPU usage continuously while running inference."""
    stop_event = threading.Event()
    cpu_readings = []

    # Start CPU monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_cpu_usage, args=(stop_event, cpu_readings))
    monitor_thread.start()

    # Run inference
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    end_time = time.time()

    # Stop CPU monitoring
    stop_event.set()
    monitor_thread.join()

    # Compute average CPU usage
    avg_cpu_usage = sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0
    elapsed_time = end_time - start_time

    return response, avg_cpu_usage, elapsed_time


def estimate_flops_per_sec(model, prompt):
    """Estimate FLOPs/sec using time and a rough FLOP approximation."""
    start_time = time.time()
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    end_time = time.time()
    elapsed_time = end_time - start_time

    estimated_flops = 10 ** 12  # Rough estimation per inference
    flops_per_sec = estimated_flops / elapsed_time if elapsed_time > 0 else 0
    return response, flops_per_sec, elapsed_time


def save_metrics_to_csv(metric_name, metric_value, elapsed_time):
    """Save metrics to a CSV file."""
    with open("metrics.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([metric_name, metric_value, elapsed_time])


def plot_metrics(metric_name, values, times):
    """Plot the chosen metric over time."""
    plt.figure(figsize=(8, 5))
    plt.plot(times, values, marker='o', linestyle='-', label=metric_name)
    plt.xlabel("Inference Number")
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} Over Time")
    plt.legend()
    plt.savefig("metrics_plot.png")
    plt.show()


def display_results(response, metric_name, metric_value, elapsed_time):
    console = Console()
    console.print("\n[bold cyan]Model Response:[/bold cyan]")
    console.print(response["message"]["content"] + "\n")

    table = Table(title="Inference Metrics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row(metric_name, f"{metric_value:.2f}")
    table.add_row("Elapsed Time (s)", f"{elapsed_time:.2f}")

    console.print(table)


def real_time_monitoring(model, prompt, metric_name, measure_function):
    console = Console()
    metric_values = []
    times = []
    response, metric_value, elapsed_time = measure_function(model, prompt)
    display_results(response, metric_name, metric_value, elapsed_time)

    with Live(console=console, refresh_per_second=1) as live:
        for i in range(5):  # Collect multiple inferences for plotting
            metric_values.append(metric_value)
            times.append(i + 1)
            save_metrics_to_csv(metric_name, metric_value, elapsed_time)

            table = Table(title="Real-Time Inference Metrics")
            table.add_column("Inference #", style="bold")
            table.add_column(metric_name, justify="right")
            table.add_column("Elapsed Time (s)", justify="right")

            for j in range(len(times)):
                table.add_row(str(times[j]), f"{metric_values[j]:.2f}", f"{elapsed_time:.2f}")

            live.update(table)

    plot_metrics(metric_name, metric_values, times)


def main():
    console = Console()
    console.print("[bold green]Ollama Energy Metrics Wrapper[/bold green]")

    available_models = list_available_models()
    console.print(f"[blue]Available models: {', '.join(available_models)}[/blue]")
    model = Prompt.ask("Enter model name", default="llama2")

    if model not in available_models:
        download_choice = Prompt.ask(f"Model {model} is not available. Do you want to download it? (yes/no)",
                                     choices=["yes", "no"], default="yes")
        if download_choice == "yes":
            download_model(model)

    metric_choice = Prompt.ask("Choose metric: [1] CPU Usage [2] FLOPs/sec", choices=["1", "2"], default="1")
    metric_name = "CPU Usage (%)" if metric_choice == "1" else "FLOPs/sec"
    measure_function = measure_cpu_usage if metric_choice == "1" else estimate_flops_per_sec

    while True:
        prompt = Prompt.ask("Enter your prompt (or type 'exit' to quit)")
        if prompt.lower() == "exit":
            console.print("[bold red]Exiting wrapper...[/bold red]")
            break
        real_time_monitoring(model, prompt, metric_name, measure_function)


if __name__ == "__main__":
    main()
