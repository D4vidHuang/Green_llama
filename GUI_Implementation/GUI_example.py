import platform
import os
import subprocess
import pandas as pd
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ENERGIBRIDGE_EXECUTABLE = "release-energibridge/energibridge"
TEMP_CSV = "new.csv"

class OllamaEnergyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama & Energy Monitor")
        self.root.geometry("800x600")

        self.prompt_label = ttk.Label(root, text="Enter your prompt:")
        self.prompt_label.pack(pady=5)

        self.prompt_entry = ttk.Entry(root, width=50)
        self.prompt_entry.pack(pady=5)


        self.run_button = ttk.Button(root, text="Run Ollama & Monitor Energy", command=self.run_process)
        self.run_button.pack(pady=10)

        self.output_text = scrolledtext.ScrolledText(root, width=80, height=10)
        self.output_text.pack(pady=5)

        self.visualize_button = ttk.Button(root, text="Visualize Energy Data", command=self.visualize_data)
        self.visualize_button.pack(pady=10)

    def run_ollama(self, prompt):

        self.output_text.insert(tk.END, f"Running Ollama with prompt: {prompt}\n")
        self.output_text.see(tk.END)

        result = subprocess.Popen(
            ["ollama", "run", "llama3.2"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        result.stdin.write(prompt + "\n")
        result.stdin.flush()

        output, error = result.communicate()
        self.output_text.insert(tk.END, f"Ollama Response:\n{output}\n")

        self.output_text.see(tk.END)

    def run_energibridge(self):

        self.output_text.insert(tk.END, "Starting energy monitoring...\n")
        self.output_text.see(tk.END)

        result = subprocess.Popen(
            [ENERGIBRIDGE_EXECUTABLE, "-o", TEMP_CSV, "--summary", "-m", "10"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        result.wait()
        self.output_text.insert(tk.END, "Energy monitoring completed.\n")
        self.output_text.see(tk.END)

    def run_process(self):

        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt before running!")
            return

        self.run_energibridge()
        self.run_ollama(prompt)

    def visualize_data(self):

        if not os.path.exists(TEMP_CSV):
            messagebox.showerror("Error", "No data file found! Please run the process first.")
            return

        df = pd.read_csv(TEMP_CSV)

        df["Time"] = df["Time"] - df["Time"].min()

        cpu_usage_cols = [col for col in df.columns if "CPU_USAGE" in col]
        cpu_temp_cols = [col for col in df.columns if "CPU_TEMP" in col]
        power_col = "SYSTEM_POWER (Watts)"
        memory_col = "USED_MEMORY"

        viz_window = tk.Toplevel(self.root)
        viz_window.title("Energy Data Visualization")
        viz_window.geometry("900x700")

        fig, ax = plt.subplots(2, 2, figsize=(10, 8))

        ax[0, 0].plot(df["Time"], df[power_col], label="Power Consumption (Watts)", linewidth=2, color="red")
        ax[0, 0].set_xlabel("Time (ms)")
        ax[0, 0].set_ylabel("Watts")
        ax[0, 0].set_title("System Power Consumption")
        ax[0, 0].legend()
        ax[0, 0].grid()

        for col in cpu_usage_cols:
            ax[0, 1].plot(df["Time"], df[col], label=col, alpha=0.7)
        ax[0, 1].set_xlabel("Time (ms)")
        ax[0, 1].set_ylabel("CPU Usage (%)")
        ax[0, 1].set_title("CPU Usage Over Time")
        ax[0, 1].legend(fontsize="small", loc="upper right", ncol=2)
        ax[0, 1].grid()

        for col in cpu_temp_cols:
            ax[1, 0].plot(df["Time"], df[col], label=col, alpha=0.7)
        ax[1, 0].set_xlabel("Time (ms)")
        ax[1, 0].set_ylabel("Temperature (°C)")
        ax[1, 0].set_title("CPU Temperature Over Time")
        ax[1, 0].legend(fontsize="small", loc="upper right", ncol=2)
        ax[1, 0].grid()

        ax[1, 1].plot(df["Time"], df[memory_col], label="Used Memory (Bytes)", color="purple", linewidth=2)
        ax[1, 1].set_xlabel("Time (ms)")
        ax[1, 1].set_ylabel("Bytes")
        ax[1, 1].set_title("Memory Usage Over Time")
        ax[1, 1].legend()
        ax[1, 1].grid()

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=viz_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaEnergyGUI(root)
    root.mainloop()
