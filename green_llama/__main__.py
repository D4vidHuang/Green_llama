from rich.console import Console
from rich.prompt import Prompt
import threading
import ollama
import models
import monitoring
import utils
import interface

def main():
    console = Console()
    interface.display_banner()

    while True:  # Main loop to allow restarting
        available_models = models.list_available_models()
        interface.display_model_list(available_models)

        model = Prompt.ask("Enter model name", default="llama2")

        if model.lower() == "exit":
            console.print("[bold red]Exiting wrapper...[/bold red]")
            return
        elif model not in available_models:
            models.handle_missing_model(model)

        metric_name, measure_function = interface.choose_metric()

        metrics_storage = {"prompts": [], "values": [], "times": []}

        monitoring_thread = threading.Thread(target=monitoring.real_time_monitoring,
                                             args=(model, metric_name, measure_function, metrics_storage))
        monitoring_thread.daemon = True
        monitoring_thread.start()

        while True:
            prompt = Prompt.ask("Enter your prompt ('restart' to change model, 'exit' to quit, 'summary' for stats)")

            if prompt.lower() == "exit":
                console.print("[bold red]Exiting wrapper...[/bold red]")
                return
            elif prompt.lower() == "restart":
                console.print("[bold yellow]Restarting model selection...[/bold yellow]")
                break
            elif prompt.lower() == "summary":
                utils.display_summary(metrics_storage, metric_name)
            else:
                response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
                console.print(response["message"]["content"])

if __name__ == "__main__":
    main()
