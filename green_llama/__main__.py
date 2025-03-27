from rich.console import Console
from rich.prompt import Prompt
from green_llama.benchmark import run_benchmark, save_logs
import threading
import ollama

from green_llama.metrics.metrics import test_all
from . import models
from . import monitoring
from . import utils
from . import interface

def main():
    console = Console()
    interface.display_banner()
    model_choice = False

    metrics_storage = {"prompts": [], "values": [], "times": []}

    while True:
        while not model_choice:
            available_models = models.list_available_models()
            interface.display_model_list(available_models)

            model = Prompt.ask("Enter model name or type 'rankings' to view local rankings", default="llama2")

            if model.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return
            elif model.lower() == "rankings":
                data_collection_folder = "green_llama/data_collection"
                utils.rank_models_by_co2(data_collection_folder)
                continue
            elif model not in available_models:
                model_choice = models.handle_missing_model(model)
            else:
                model_choice = True

        metrics = interface.choose_metric()
        metrics_storage = {metric: {"prompts": [], "values": [], "times": []} for metric in metrics}

        while True:
            prompt = Prompt.ask(
                "Enter your prompt ('restart' to change model, 'exit' to quit, "
                "'summary' for stats, 'benchmark' for benchmark results)"
            )
            if prompt.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                utils.save_all_metrics_to_csv(model, metrics_storage)
                utils.clear_metrics_storage(metrics_storage)
                return
            elif prompt.lower() == "restart":
                model_choice = False
                console.print("[bold yellow]Restarting model selection...[/bold yellow]")
                utils.save_all_metrics_to_csv(model, metrics_storage)
                utils.clear_metrics_storage(metrics_storage)
                break
            elif prompt.lower() == "summary":
                utils.display_summary(metrics_storage)
                utils.display_summary(metrics_storage, metric_name)

            elif prompt.lower() == "benchmark":
                prompts = utils.load_benchmark_dataset()
                console.print(f"[bold green]Running benchmark on {len(prompts)} prompts...[/bold green]")
                results = run_benchmark(model, prompts, metric_name, measure_function)

                metrics_storage["prompts"].extend(results["prompts"])
                metrics_storage["values"].extend(results["values"])
                metrics_storage["times"].extend(results["times"])
                utils.display_summary(metrics_storage, metric_name)
                save_logs(metrics_storage)

            else:
                console.print("[yellow]Thinking...[/yellow]")
                response, metrics_data = test_all(model, prompt)
                monitoring.record_metrics(prompt, metrics_data, metrics_storage)
                console.print(f"[yellow]{response['message']['content']}[/yellow]")

if __name__ == "__main__":
    main()
