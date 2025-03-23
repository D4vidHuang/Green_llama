import pyfiglet
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from . import monitoring
from .metrics.metrics import (
    test_cpu, test_gpu, test_ram, 
    test_total_energy, test_emissions
)

console = Console()

def display_banner():
    ascii_llama = pyfiglet.figlet_format("Green Llama", font="standard", justify="center")
    console.print(f"[bold green]{ascii_llama}[/bold green]")

def display_model_list(models):
    table = Table()
    table.add_column("Locally Available Models", style="cyan")
    for model in models:
        table.add_row(model)
    console.print(table)
    console.print("For information about all available models refer to: https://ollama.com/search")

def choose_metric():
    metric_choice = Prompt.ask(
        "Choose metric: [1] CPU Energy [2] GPU Energy [3] RAM Energy [4] Total Energy [5] Carbon Emissions",
        choices=["1", "2", "3", "4", "5"],
        default="1"
    )
    if metric_choice == "1":
        return "CPU Usage (%)", monitoring.measure_cpu_usage
    else:
        metrics = {
        "1": ("CPU Energy (kWh)", test_cpu),
        "2": ("GPU Energy (kWh)", test_gpu),
        "3": ("RAM Energy (kWh)", test_ram),
        "4": ("Total Energy (kWh)", test_total_energy),
        "5": ("Carbon Emissions (kgCO2)", test_emissions)
    }
    return metrics[metric_choice]

#TODO: Implement external profiler support
def external_profiler():
    console.print("[red]This has not been implemented yet[/red]")

def choose_profiler():
    profiler_choice = Prompt.ask("Choose a profiler: [1] Built-In [2] External", choices=["1", "2"], default="1")
    return "In-Built (%)", choose_metric() if profiler_choice == "1" else "External", external_profiler()