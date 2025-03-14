# SSE_EnergyMeasurement_Part2


# Green Llama: Ollama Performance Monitor

Green Llama is a command-line tool designed to monitor and analyze the performance of Ollama models. It provides real-time CPU usage and estimated FLOPs/sec metrics, allowing you to assess the efficiency of different models and prompts.


![img.png](img.png)

## Features

-   **Model Management:**
    -      Lists locally available Ollama models.
    -      Downloads models directly from the Ollama repository.
-   **Performance Monitoring:**
    -      Measures and displays CPU usage during model inference.
    -      Estimates FLOPs/sec to gauge computational performance.
    -   Real time metric collection.
-   **Data Logging:**
    -      Saves metrics to a CSV file (`metrics.csv`) for further analysis.
-   **Visualization:**
    -   Plots a bar graph of metrics per prompt to visualize performance over time.
-   **Interactive Interface:**
    -      Provides a user-friendly command-line interface with prompts and tables.
    -   Allows for easy model selection and metric choice.
-   **Summary Statistics:**
    -   Calculates and displays average metrics for the session.

## Prerequisites

-      Python 3.6+
-      Ollama installed and running.
-      Required Python libraries:
    -      `psutil`
    -   `ollama`
    -   `rich`
    -   `pyfiglet`
    -   `matplotlib`

## Installation

1.  **Install Ollama:**
    -      Follow the installation instructions on the Ollama website.
2.  **Install Python Dependencies:**
    ```bash
    pip install psutil ollama rich pyfiglet matplotlib
    ```
3.  **Clone the Repository (Optional):**
    -   If you want to modify the code, clone this repository.
    -   otherwise save the python code to a file called `green_llama.py`

## Usage

1.  **Run the script:**
    ```bash
    python green_llama.py
    ```
2.  **Model Selection:**
    -      The script will display a list of locally available models.
    -      Enter the name of the model you want to use.
    -      If the model is not available, you will be prompted to download it.
3.  **Metric Choice:**
    -      Choose between CPU usage and FLOPs/sec monitoring.
4.  **Prompt Input:**
    -      Enter your prompts to interact with the model.
    -      Type `restart` to change the model.
    -      Type `exit` to quit the application.
    -   Type `summary` to view collected metrics and graphs.
5.  **View Results:**
    -      The script will display the model's response and the selected metrics.
    -   A `metrics.csv` file will be generated containing all collected data.
    -   A `metrics_bar_plot.png` file will be generated showing a graph of the collected data.

## This is an automatically generated (provisional) description of the project