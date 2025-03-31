import time
from rich.console import Console
import ollama
import json
import multiprocessing
import os
import csv
from .metrics.metrics import test_all
from . import monitoring

console = Console()

def run_benchmark(model: str, prompts: list, metric_name: str, measure_function, task_name: str = "text-generation"):
    prompts = prompts[:2] # In total we have 678, but it takes too long.
    metrics_storage = {}

    console.print(f"[bold green]Starting benchmark on model: {model} using first {len(prompts)} prompts[/bold green]")
    for i, prompt in enumerate(prompts):
        response, metrics_data = test_all(model, prompt)
        for metric_name, value in metrics_data.items():
            if metric_name != "elapsed_time":
                if metric_name not in metrics_storage:
                    metrics_storage[metric_name] = {"prompts": [], "values": [], "times": []}
                metrics_storage[metric_name]["prompts"].append(prompt)
                metrics_storage[metric_name]["values"].append(value)
                metrics_storage[metric_name]["times"].append(metrics_data["elapsed_time"])
        console.print(f"[blue]Prompt {i+1}/{len(prompts)}[/blue] - Time: {metrics_data['elapsed_time']:.2f}s")

    if task_name == "text-generation":
        novel_prompts = [
            "Generate the beginning of a science fiction story",
            # "Write a poem about the future world",
            # "Tell a humorous joke",
            # "Suggest an innovative business idea",
            # "Describe an abstract art picture"
        ]

        console.print(f"[bold green]Starting novel benchmark tests on model: {model}[/bold green]")
        for i, prompt in enumerate(novel_prompts):
            response, metrics_data = test_all(model, prompt)
            for metric_name, value in metrics_data.items():
                if metric_name != "elapsed_time":
                    if metric_name not in metrics_storage:
                        metrics_storage[metric_name] = {"prompts": [], "values": [], "times": []}
                    metrics_storage[metric_name]["prompts"].append(prompt)
                    metrics_storage[metric_name]["values"].append(value)
                    metrics_storage[metric_name]["times"].append(metrics_data["elapsed_time"])
            console.print(f"[magenta]Novel Prompt {i+1}/{len(novel_prompts)}[/magenta] - Time: {metrics_data['elapsed_time']:.2f}s")

    return metrics_storage


def save_logs(metrics_storage, model, benchmark_name, filename="benchmark_log.csv"):
    directory = f"green_llama/data_collection/benchmark_results/{benchmark_name}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    safe_model_name = model.replace(":", "_")
    file_path = os.path.join(directory, f"{safe_model_name}_{filename}")
    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Metric Name", "Prompt", "Value", "Elapsed Time"])
        for metric_name, data in metrics_storage.items():
            for prompt, value, elapsed_time in zip(data["prompts"], data["values"], data["times"]):
                writer.writerow([metric_name, prompt, value, elapsed_time])

    print(f"[green]Log saved to {file_path}[/green]")
