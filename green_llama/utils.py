import csv
import os
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from datasets import load_dataset

console = Console()

def save_metrics_to_csv(metric_name, metric_value, elapsed_time):
    with open("metrics.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([metric_name, metric_value, elapsed_time])

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

def display_summary(metrics_storage):
    table = Table(title="Summary of Metrics for this Conversation")
    table.add_column("Metric", style="bold")
    table.add_column("Average Value per Prompt", justify="right")

    for metric_name, data in metrics_storage.items():
        avg_metric = sum(data["values"]) / len(data["values"]) if data["values"] else 0
        table.add_row(metric_name, f"{avg_metric:.2f}")

    console.print(table)

def save_all_metrics_to_csv(model, metrics_storage):
    file_path = f"green_llama/data_collection/{model}_all_metrics.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Metric Name", "Prompt", "Value", "Elapsed Time"])
        for metric_name, data in metrics_storage.items():
            for prompt, value, elapsed_time in zip(data["prompts"], data["values"], data["times"]):
                writer.writerow([metric_name, prompt, value, elapsed_time])

def clear_metrics_storage(metrics_storage):
    for metric in metrics_storage:
        metrics_storage[metric]["prompts"].clear()
        metrics_storage[metric]["values"].clear()
        metrics_storage[metric]["times"].clear()

def read_metrics_from_csv(file_path):
    metrics_storage = {}
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            metric_name = row["Metric Name"]
            value = float(row["Value"])
            if metric_name not in metrics_storage:
                metrics_storage[metric_name] = {"values": []}
            metrics_storage[metric_name]["values"].append(value)
    return metrics_storage

def aggregate_metrics(data_collection_folder):
    aggregated_metrics = {}
    for file_name in os.listdir(data_collection_folder):
        if file_name.endswith("_all_metrics.csv"):
            file_path = os.path.join(data_collection_folder, file_name)
            model_metrics = read_metrics_from_csv(file_path)
            for metric_name, data in model_metrics.items():
                if metric_name not in aggregated_metrics:
                    aggregated_metrics[metric_name] = {"values": []}
                aggregated_metrics[metric_name]["values"].extend(data["values"])
    return aggregated_metrics

def display_ranking(data_collection_folder):
    metrics_storage = aggregate_metrics(data_collection_folder)
    ranking = []
    for metric_name, data in metrics_storage.items():
        avg_metric = sum(data["values"]) / len(data["values"]) if data["values"] else 0
        ranking.append((metric_name, avg_metric))

    ranking.sort(key=lambda x: x[1], reverse=True)

    table = Table(title="Ranking of Metrics Across All Models")
    table.add_column("Rank", style="bold")
    table.add_column("Metric", style="bold")
    table.add_column("Average Value per Prompt", justify="right")

    for rank, (metric_name, avg_metric) in enumerate(ranking, start=1):
        table.add_row(str(rank), metric_name, f"{avg_metric:.2f}")

    console.print(table)

def rank_models_by_co2(data_collection_folder):
    model_averages = []
    for file_name in os.listdir(data_collection_folder):
        if file_name.endswith("_all_metrics.csv"):
            file_path = os.path.join(data_collection_folder, file_name)
            model_name = file_name.replace("_all_metrics.csv", "")
            co2_values = read_co2_emissions_from_csv(file_path)
            avg_co2 = calculate_average(co2_values)
            model_averages.append((model_name, avg_co2))

    model_averages.sort(key=lambda x: x[1])

    table = Table(title="Model Ranking by Average CO2 Emissions")
    table.add_column("Rank", style="bold")
    table.add_column("Model", style="bold")
    table.add_column("Average CO2 Emissions (kgCO2)", justify="right")

    for rank, (model_name, avg_co2) in enumerate(model_averages, start=1):
        table.add_row(str(rank), model_name, f"{avg_co2:.2f}")

def load_benchmark_dataset(task_name="text-generation", num_samples=1000):
    ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    prompts = ds["text"][:num_samples]
    return [p.strip() for p in prompts if len(p.strip()) > 10]
    console.print(table)

def read_co2_emissions_from_csv(file_path):
    co2_values = []
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Metric Name"] == "Carbon Emissions (kgCO2)":
                co2_values.append(float(row["Value"]))
    return co2_values

def calculate_average(values):
    return sum(values) / len(values) if values else 0

