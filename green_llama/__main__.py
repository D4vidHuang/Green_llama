from rich.console import Console
from rich.prompt import Prompt
from green_llama.benchmark import run_benchmark, save_logs
import threading
import ollama
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

            model = Prompt.ask("Enter model name", default="llama2")

            if model.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return
            elif model not in available_models:
                model_choice = models.handle_missing_model(model)
            else:
                model_choice = True

        metric_name, measure_function = ("CPU Usage (%)", monitoring.measure_cpu_usage)

        monitoring_thread = threading.Thread(
            target=monitoring.real_time_monitoring,
            args=(model, metric_name, measure_function, metrics_storage)
        )
        monitoring_thread.daemon = True
        monitoring_thread.start()

        while True:
            prompt = Prompt.ask(
                "Enter your prompt ('restart' to change model, 'exit' to quit, "
                "'summary' for stats, 'benchmark' for benchmark results)"
            )
            if prompt.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return

            elif prompt.lower() == "restart":
                model_choice = False
                console.print("[bold yellow]Restarting model selection...[/bold yellow]")
                break

            elif prompt.lower() == "summary":
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
                response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
                console.print(f"[yellow]{response['message']['content']}[/yellow]")


if __name__ == "__main__":
    main()
