import pyfiglet
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import monitoring

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
    metric_choice = Prompt.ask("Choose metric: [1] CPU Usage [2] FLOPs/sec", choices=["1", "2"], default="1")
    return ("CPU Usage (%)", monitoring.measure_cpu_usage) if metric_choice == "1" else ("FLOPs/sec", monitoring.estimate_flops_per_sec)

#TODO: Implement external profiler support
def external_profiler():
    console.print("[red]This has not been implemented yet[/red]")

def choose_profiler():
    profiler_choice = Prompt.ask("Choose a profiler: [1] Built-In [2] External", choices=["1", "2"], default="1")
    return "In-Built (%)", choose_metric() if profiler_choice == "1" else "External", external_profiler()