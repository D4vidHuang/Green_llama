import time
from rich.console import Console
import ollama
import json

console = Console()

def run_benchmark(model: str, prompts: list, metric_name: str, measure_function):
    prompts = prompts[:20] # In total we have 678, but it takes too long.
    metrics_storage = {"prompts": [], "cpu_usages": [], "times": []}

    console.print(f"[bold green]Starting benchmark on model: {model} using first {len(prompts)} prompts[/bold green]")
    for i, prompt in enumerate(prompts):
        response, cpu_usage, elapsed_time = measure_function(model, prompt)
        metrics_storage["prompts"].append(prompt)
        metrics_storage["cpu_usages"].append(cpu_usage)
        metrics_storage["times"].append(elapsed_time)
        console.print(f"[blue]Prompt {i+1}/{len(prompts)}[/blue] - Time: {elapsed_time:.2f}s - CPU: {cpu_usage:.2f}%")

    novel_prompts = [
        "请生成一个科幻故事的开头", # Please generate the beginning of a science fiction story
        "未来の世界についての詩を書く",
        "Verzin een humoristische grap",
        "Veuillez donner une idée d'entreprise innovante",
        "Describe an abstract art picture"
    ]
    novel_metrics = {"novel_prompts": [], "novel_cpu_usages": [], "novel_times": []}

    console.print(f"[bold green]Starting novel benchmark tests on model: {model}[/bold green]")
    for i, prompt in enumerate(novel_prompts):
        response, cpu_usage, elapsed_time = measure_function(model, prompt)
        novel_metrics["novel_prompts"].append(prompt)
        novel_metrics["novel_cpu_usages"].append(cpu_usage)
        novel_metrics["novel_times"].append(elapsed_time)
        console.print(f"[magenta]Novel Prompt {i+1}/{len(novel_prompts)}[/magenta] - Time: {elapsed_time:.2f}s - CPU: {cpu_usage:.2f}%")

    metrics_storage.update(novel_metrics)
    metrics_storage["values"] = metrics_storage["cpu_usages"]

    return metrics_storage


def save_logs(metrics_storage, filename="benchmark_log.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(metrics_storage, f, indent=2, ensure_ascii=False)
    print(f"[green]Log saved to {filename}[/green]")
