import ollama
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def list_available_models():
    models = ollama.list()
    return [model['model'] for model in models['models']]

def download_model(model_name):
    console.print(f"[yellow]Downloading model {model_name}...[/yellow]")
    ollama.pull(model_name)
    console.print(f"[green]Model {model_name} downloaded successfully![/green]")

def handle_missing_model(model):
    download_choice = Prompt.ask(f"Model {model} is not available. Download it? (yes/no)", choices=["yes", "no"], default="yes")
    if download_choice.lower() == "yes":
        try:
            download_model(model)
            return True
        except Exception as e:
            if "500" in str(e):
                console.print(f"[red]Couldn't find {model} in the Ollama repository.[/red]")
            else:
                console.print(f"[red]Unexpected error: {e}[/red]")
            return False


