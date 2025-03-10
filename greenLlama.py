import time
import psutil
import ollama
import csv
import threading
import pyfiglet
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


def plot_metrics_bar(metric_name,prompt_data, values):
    """Plot a bar graph for CPU usage per prompt with dynamic labels (Prompt 1, Prompt 2, etc.)."""
    # Generate prompt labels as "Prompt 1", "Prompt 2", etc.
    prompt_labels = [f"Prompt {i+1}" for i in range(len(values))]

    # Plot the bar graph
    plt.figure(figsize=(8, 5))
    plt.bar(prompt_labels, values, color='skyblue')
    plt.xlabel("Prompts")
    plt.ylabel(f"{metric_name}")
    plt.title(f"{metric_name} per Prompt")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("metrics_bar_plot.png")
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

#TODO: FIX TO MONITOR PER PROMPT
def real_time_monitoring(model, prompt, metric_name, measure_function, metrics_storage):
    """Function to monitor and store metrics in the background."""
    while True:
        response, metric_value, elapsed_time = measure_function(model, prompt)
        metrics_storage["prompts"].append(prompt)
        metrics_storage["values"].append(metric_value)
        metrics_storage["times"].append(elapsed_time)
        save_metrics_to_csv(metric_name, metric_value, elapsed_time)

        # The inference response isn't shown during monitoring
        time.sleep(1)  # Wait before next measurement


def calculate_average_metric(metrics_storage):
    """Calculate average of the collected metrics."""
    if not metrics_storage["values"]:
        return 0
    return sum(metrics_storage["values"]) / len(metrics_storage["values"])


def main():
    console = Console()
    ascii_llama = pyfiglet.figlet_format("Green Llama", font="standard", justify="center")
    console.print(f"[bold green]{ascii_llama}[/bold green]")

    while True:  # Main loop to allow restarting without exiting
        available_models = list_available_models()

        table = Table()
        table.add_column("Locally Available Models", style="cyan")

        for model in available_models:
            table.add_row(model)

        console.print(table)
        console.print(f"For a full list of available models refer to: https://ollama.com/search")
        model = Prompt.ask("Enter model name", default="llama2")

        if model not in available_models:
            if model.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return
            download_choice = Prompt.ask(f"Model {model} is not available. Do you want to download it? (yes/no)",
                                         choices=["yes", "no"], default="yes")
            if download_choice == "yes":
                try:
                    download_model(model)
                except Exception as e:
                    if "500" in str(e):
                        console.print(f"[red]Couldn't find {model} in the Ollama repository[/red]")
                        continue
                    else:
                        console.print(f"[red] Unexpected error: {e} [/red]")
                        continue
            else:
                continue

        metric_choice = Prompt.ask("Choose metric: [1] CPU Usage [2] FLOPs/sec", choices=["1", "2"], default="1")
        metric_name = "CPU Usage (%)" if metric_choice == "1" else "FLOPs/sec"
        measure_function = measure_cpu_usage if metric_choice == "1" else estimate_flops_per_sec

        # Initialize a storage for metrics
        metrics_storage = {"prompts": [], "values": [], "times": []}

        # Start monitoring in a separate thread
        monitoring_thread = threading.Thread(target=real_time_monitoring, args=(
        model, "test prompt", metric_name, measure_function, metrics_storage))
        monitoring_thread.daemon = True
        monitoring_thread.start()

        while True:  # Inner loop for conversation
            prompt = Prompt.ask(
                "Enter your prompt (or type 'restart' to change model, 'exit' to quit, 'summary' to view stats)")
            console.print("Thinking...")
            if prompt.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return  # Fully exit
            elif prompt.lower() == "restart":
                console.print("[bold yellow]Restarting model selection...[/bold yellow]")
                break  # Exit conversation loop, go back to model selection
            elif prompt.lower() == "summary":
                # Calculate and display stats here
                average_metric = calculate_average_metric(metrics_storage)

                # Display the table with the overall average
                table = Table(title="Summary of Metrics")
                table.add_column("Metric", style="bold")
                table.add_column("Average Value", justify="right")

                table.add_row(metric_name, f"{average_metric:.2f}")
                console.print(table)

                # Plot the bar graph for CPU usage per prompt
                plot_metrics_bar(metric_name, metrics_storage["prompts"], metrics_storage["values"])

            else:
                # You could also show the model's response if desired
                response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
                console.print(response["message"]["content"])


if __name__ == "__main__":
    main()
