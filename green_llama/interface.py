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
    console.print("For information about at all available models refer to: https://ollama.com/search")

def choose_metric():
    metric_choice = Prompt.ask("Choose metric: [1] CPU Usage [2] FLOPs/sec", choices=["1", "2"], default="1")
    return ("CPU Usage (%)", monitoring.measure_cpu_usage) if metric_choice == "1" else ("FLOPs/sec", monitoring.estimate_flops_per_sec)
