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
    table.add_column("Value", justify="right")

    total_energy = 0
    total_co2 = 0
    total_time = 0
    num_prompts = 0
    most_costly_prompt = ("", 0)
    least_costly_prompt = ("", float("inf"))

    if not metrics_storage:
        console.print("[yellow]No metrics data available yet[/yellow]")
        return

    for metric_name, data in metrics_storage.items():
        if not data["values"]:
            continue
            
        avg_metric = sum(data["values"]) / len(data["values"])
        if avg_metric > 0: 
            table.add_row(f"Average {metric_name}", f"{avg_metric:.2f}")

            if metric_name == "Total Energy (J)":
                total_energy = sum(data["values"])
                for prompt, value in zip(data["prompts"], data["values"]):
                    if value > most_costly_prompt[1]:
                        most_costly_prompt = (prompt, value)
                    if value < least_costly_prompt[1]:
                        least_costly_prompt = (prompt, value)
            elif metric_name == "Carbon Emissions (gCO2)":
                total_co2 = sum(data["values"])

            total_time += sum(data["times"])
            num_prompts += len(data["prompts"])

    if num_prompts > 0:  
        avg_response_time = total_time / num_prompts
        table.add_row("Average Response Time (s)", f"{avg_response_time:.2f}")
        table.add_row("Number of Prompts", str(num_prompts))
        
        if total_energy > 0:
            table.add_row("Total Energy (J)", f"{total_energy:.2f}")
        if total_co2 > 0:
            table.add_row("Total CO2 Emissions (gCO2)", f"{total_co2:.2f}")
        if most_costly_prompt[0]:  
            table.add_row("Most Costly Prompt", most_costly_prompt[0][:25] + "..." if len(most_costly_prompt[0]) > 25 else most_costly_prompt[0])
        if least_costly_prompt[0]:
            table.add_row("Least Costly Prompt", least_costly_prompt[0][:25] + "..." if len(least_costly_prompt[0]) > 25 else least_costly_prompt[0])

    console.print(table)

def save_all_metrics_to_csv(model, metrics_storage):
    file_path = f"green_llama/data_collection/model_history/{model}_all_metrics.csv"
    out_path = "green_llama/data_collection/conversation_metrics.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Metric Name", "Prompt", "Value", "Elapsed Time"])
        for metric_name, data in metrics_storage.items():
            for prompt, value, elapsed_time in zip(data["prompts"], data["values"], data["times"]):
                writer.writerow([metric_name, prompt, value, elapsed_time])

    with open(out_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric Name", "Prompt", "Value", "Elapsed Time"])

    with open(out_path, mode="a", newline="") as file:
        writer = csv.writer(file)
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

# def rank_models_by_co2(data_collection_folder):
#     model_averages = []
#     for file_name in os.listdir(data_collection_folder):
#
#         if file_name.endswith("_all_metrics.csv"):
#             file_path = os.path.join(data_collection_folder, file_name)
#             model_name = file_name.replace("_all_metrics.csv", "")
#             co2_values = read_co2_emissions_from_csv(file_path)
#             avg_co2 = calculate_average(co2_values)
#             model_averages.append((model_name, avg_co2))
#
#     model_averages.sort(key=lambda x: x[1])
#
#     table = Table(title="Model Ranking by Average CO2 Emissions")
#     table.add_column("Rank", style="bold")
#     table.add_column("Model", style="bold")
#     table.add_column("Average CO2 Emissions (gCO2)", justify="right")
#
#     for rank, (model_name, avg_co2) in enumerate(model_averages, start=1):
#         table.add_row(str(rank), model_name, f"{avg_co2:.2f}")
#     console.print(table)


def rank_models_by_co2(data_collection_folder):
    benchmark_results_folder = os.path.join(data_collection_folder, "benchmark_results")
    model_history_folder = os.path.join(data_collection_folder, "model_history")

    model_averages = {}
    ranked_models = []

    # Process benchmark_results directory first
    for file_name in os.listdir(benchmark_results_folder):
        if file_name.endswith("_all_metrics.csv"):
            file_path = os.path.join(benchmark_results_folder, file_name)
            model_name = file_name.replace("_all_metrics.csv", "")
            co2_values = read_co2_emissions_from_csv(file_path)
            avg_co2 = calculate_average(co2_values)
            model_averages[model_name] = avg_co2

    # Process model_history directory and add models not in benchmark_results
    for file_name in os.listdir(model_history_folder):
        if file_name.endswith("_all_metrics.csv"):
            file_path = os.path.join(model_history_folder, file_name)
            model_name = file_name.replace("_all_metrics.csv", "")
            if model_name not in model_averages:
                co2_values = read_co2_emissions_from_csv(file_path)
                avg_co2 = calculate_average(co2_values)
                model_averages[model_name] = avg_co2
                ranked_models.append((model_name + " (Not Benchmarked) ", avg_co2))
            else:
                ranked_models.append((model_name, model_averages[model_name]))

    # Sort models by average CO2 emissions
    ranked_models.sort(key=lambda x: x[1])

    # Display the ranking
    table = Table(title="Model Ranking by Average CO2 Emissions")
    table.add_column("Rank", style="bold")
    table.add_column("Model", style="bold")
    table.add_column("Average CO2 Emissions (kgCO2)", justify="right")

    for rank, (model_name, avg_co2) in enumerate(ranked_models, start=1):
        table.add_row(str(rank), model_name, f"{avg_co2:.2f}")

    console.print(table)

def load_benchmark_dataset(task_name="text-generation", num_samples=1000):
    if task_name == "text-generation":
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        prompts = ds["text"][:num_samples]
        return [p.strip() for p in prompts if len(p.strip()) > 10]
    elif task_name == "code-generation":
        
        code_prompts = [
            "Write a Python function to sort a list",
            "Create a JavaScript class for a binary tree",
            "Implement a C++ function to reverse a string",
            "Write a SQL query to find duplicate records",
            "Create a Java method to calculate factorial",
            "Write a Python decorator for timing functions",
            "Implement a JavaScript promise-based API call",
            "Create a C++ template class for a stack",
            "Write a SQL stored procedure for user authentication",
            "Implement a Java interface for a database connection"
        ]
        return code_prompts
    else:  # chat-testing
        chat_prompts = [
            "Hello, please introduce yourself", # 
            "What's the weather like today?",
            "Can you help me with my homework?",
            "Tell me a joke",
            "What's your favorite color?",
            "How do you feel about artificial intelligence?",
            "Can you explain quantum computing?",
            "What's your opinion on climate change?",
            "Tell me about your capabilities",
            "What's the meaning of life?"
        ]
        return chat_prompts

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

