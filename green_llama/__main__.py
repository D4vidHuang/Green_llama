import signal

from rich.console import Console
from rich.prompt import Prompt
from green_llama.benchmark import run_benchmark, save_logs

from green_llama.metrics.metrics import test_all
from green_llama.utils import clear_terminal
from . import models
from . import monitoring
from . import utils
from . import interface
import subprocess
import platform
import os

def main():
    clear_terminal()
    console = Console()
    interface.display_banner()
    model_choice = False
    report_process = None

    metrics_storage = {"prompts": [], "values": [], "times": []}

    while True:
        while not model_choice:
            available_models = models.list_available_models()
            interface.display_model_list(available_models)

            model = Prompt.ask("Enter model name or type 'rankings' to view local rankings or type 'web report' to launch web report viewer", default="llama2")

            if model.lower() == "exit":
                if report_process:
                    console.print("[cyan]Shutting down report viewer...[/cyan]")
                    try:
                        if platform.system() == "Windows":
                            subprocess.run(
                                ["taskkill", "/PID", str(report_process.pid), "/T", "/F"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                        else:
                            os.killpg(os.getpgid(report_process.pid), signal.SIGTERM)
                        console.print("[cyan]Report viewer shut down successfully[/cyan]")
                    except Exception as e:
                        console.print(f"[red]Failed to shut down viewer: {e}[/red]")
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return
            elif model.lower() == "rankings":
                # data_collection_folder = "green_llama/data_collection"
                data_collection_folder = "report_viewer/public"
                utils.rank_models_by_co2(data_collection_folder)
                continue
            elif model.lower() == "web report":
                if report_process == None:
                    report_process = utils.launch_report_viewer()
                else:
                    console.print("[cyan]Report viewer is already running...[/cyan]")
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
                if report_process:
                    console.print("[cyan]Shutting down report viewer...[/cyan]")
                    try:
                        if platform.system() == "Windows":
                            subprocess.run(
                                ["taskkill", "/PID", str(report_process.pid), "/T", "/F"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                        else:
                            os.killpg(os.getpgid(report_process.pid), signal.SIGTERM)
                        console.print("[cyan]Report viewer shut down successfully[/cyan]")
                    except Exception as e:
                        console.print(f"[red]Failed to shut down viewer: {e}[/red]")
                return
            elif prompt.lower() == "restart":
                model_choice = False
                console.print("[bold yellow]Restarting model selection...[/bold yellow]")
                utils.save_all_metrics_to_csv(model, metrics_storage)
                utils.clear_metrics_storage(metrics_storage)
                break
            elif prompt.lower() == "summary":
                utils.display_summary(metrics_storage)

            elif prompt.lower() == "benchmark":

                benchmark_names = {
                    1: "chat_benchmark",
                    2: "code_benchmark",
                    3: "text_benchmark"
                }
                console.print("\n[bold]Choose benchmark type:[/bold]")
                console.print("1. Text Generation")
                console.print("2. Code Generation")
                console.print("3. Chat Testing")
                
                benchmark_type = Prompt.ask("Enter option number", choices=["1", "2", "3"], default="1")
                
                if benchmark_type == "1":
                    prompts = utils.load_benchmark_dataset(task_name="text-generation")
                    console.print(f"[bold green]Running text generation benchmark with {len(prompts)} prompts...[/bold green]")
                    task_name = "text-generation"
                elif benchmark_type == "2":
                    prompts = utils.load_benchmark_dataset(task_name="code-generation")
                    console.print(f"[bold green]Running code generation benchmark with {len(prompts)} prompts...[/bold green]")
                    task_name = "code-generation"
                else:
                    prompts = utils.load_benchmark_dataset(task_name="chat-testing")
                    console.print(f"[bold green]Running chat testing benchmark with {len(prompts)} prompts...[/bold green]")
                    task_name = "chat-testing"
                
                for metric_name, measure_function in metrics.items():
                    results = run_benchmark(model, prompts, metric_name, measure_function, task_name)
                    for metric, data in results.items():
                        if metric not in metrics_storage:
                            metrics_storage[metric] = {"prompts": [], "values": [], "times": []}
                        metrics_storage[metric]["prompts"].extend(data["prompts"])
                        metrics_storage[metric]["values"].extend(data["values"])
                        metrics_storage[metric]["times"].extend(data["times"])
                    utils.display_summary(metrics_storage)
                    save_logs(metrics_storage, model, benchmark_names[int(benchmark_type)])
                break


            else:
                console.print("[yellow]Thinking...[/yellow]")
                response, metrics_data = test_all(model, prompt)
                monitoring.record_metrics(prompt, metrics_data, metrics_storage)
                console.print(f"[yellow]{response['message']['content']}[/yellow]")


if __name__ == "__main__":
    main()
