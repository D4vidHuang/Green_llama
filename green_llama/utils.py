import csv
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
console = Console()
def save_metrics_to_csv(metric_name, metric_value, elapsed_time):
    with open("metrics.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([metric_name, metric_value, elapsed_time])

#TODO: Implement make a report
def make_report():
    return 0

def calculate_average_metric(metrics_storage):
    if not metrics_storage["values"]:
        return 0
    return sum(metrics_storage["values"]) / len(metrics_storage["values"])

def plot_metrics(metric_name, values):
    plt.figure(figsize=(8, 5))
    plt.plot(range(len(values)), values, color='skyblue')
    plt.xlabel("Time")
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over Time")
    plt.show()

#TODO: Better summaries
def display_summary(metrics_storage, metric_name):
    avg_metric = calculate_average_metric(metrics_storage)
    table = Table(title="Summary of Metrics")
    table.add_column("Metric", style="bold")
    table.add_column("Average Value", justify="right")
    table.add_row(metric_name, f"{avg_metric:.2f}")
    console.print(table)
    plot_metrics(metric_name, metrics_storage["values"])

def save_all_metrics_to_csv(metrics_storage):
    with open("all_metrics.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric Name", "Prompt", "Value", "Elapsed Time"])
        for metric_name, data in metrics_storage.items():
            for prompt, value, elapsed_time in zip(data["prompts"], data["values"], data["times"]):
                writer.writerow([metric_name, prompt, value, elapsed_time])