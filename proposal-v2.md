# Adding Energy Metrics to LMStudio/Ollama

## **Problem Statement**

Currently, tools like LMStudio and Ollama provide robust environments for running and experimenting with LLMs but lack built-in energy metrics. This omission makes it difficult for developers and researchers to:

1. **Identify Appropriate Energy Measurement Tasks and Metrics**: Define the right approach for assessing energy consumption.
2. **Measure Energy Consumption**: Understand the energy footprint of their models during training, fine-tuning, or inference.
3. **Optimize for Efficiency**: Identify energy-intensive processes and optimize them for sustainability.
4. **Report Environmental Impact**: Provide transparency about the environmental impact of their AI workflows.

The deliverable of this project will be either:

- **A Tool**: A monitoring tool that allows users to run prompts on local Large Language Models (LLMs) while tracking energy consumption during inference.
- **A Guideline**: A comprehensive guide on how users can manually or with existing tools measure and optimize energy usage.

## **Solution Proposal**

Since the final deliverable (a tool or a guideline) depends on feasibility analysis, we will first conduct experiments to explore energy measurement approaches. The overlapping tasks between both deliverable options include:

- Selecting a Cross-Platform Energy Measurement Tool
- Choosing LLM Models for Testing
- Defining Energy Consumption Benchmarking Tasks
- Researching and Selecting Suitable Energy Metrics

Based on the experimental results, we will determine whether developing a tool or a guideline is more feasible and beneficial.

### **If the Deliverable is a Tool**

- **Integration with Cross-Platform Energy Measurement Tools**: Implement a module that can track energy usage on CPU and GPU.
- **User Interface**: Provide a simple UI/CLI/Scripts for real-time monitoring.
- **Compatibility Testing**: Ensure the tool functions correctly across multiple platforms (Mac, Windows, Linux).
- **Automation and Reporting**: Enable automatic logging and reporting of energy metrics.

### **If the Deliverable is a Guideline**

- **Selecting Energy Measurement Tools**: Guide users in choosing the right tools for CPU and GPU power tracking.
- **Defining Measurement Tasks**: Establish standard benchmarking tasks (e.g., text generation, image generation).
- **Platform-Specific Considerations**: Provide instructions tailored for different OS environments.
- **Optimization Strategies**: Offer recommendations for reducing energy consumption based on observed metrics.

## **Tasks for Each Week**

### **Week 5**

- Select a cross-platform energy measurement tool/library for CPU and GPU power tracking.
- Choose appropriate LLM models for testing (e.g., small quantized models, standard models, large models).
- Define energy consumption benchmarking tasks (e.g., text generation, image generation).
- Research and select suitable energy metrics (e.g., energy consumption per token).
- Conduct experiments to determine whether the final deliverable should be a tool or a guideline.

### **Week 6**

- **If developing a tool:**
  - Conduct requirement analysis.
  - Start implementation of the energy monitoring module.
- **If creating a guideline:**
  - Perform experimental tests across multiple platforms (Mac, Windows, Linux).

### **Week 7**

- **If developing a tool:**
  - Test the tool’s functionality across different platforms.
  - Measure and analyze energy consumption of Ollama.
- **If creating a guideline:**
  - Summarize experimental results.
  - Begin dissemination and social impact efforts (e.g., documentation, community engagement).

### **Weeks 8 - 9**

- Finalize the code and documentation for submission.
- Prepare a presentation and supporting materials (e.g., slides, reports).