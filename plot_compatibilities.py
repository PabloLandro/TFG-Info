import os
import pandas as pd
import matplotlib.pyplot as plt

# Define global arrays for dataset categories
AUTOMATIC_DATASETS = ["dataset1", "dataset2"]  # Replace with actual dataset names
MANUAL_DATASETS = ["dataset3", "dataset4"]     # Replace with actual dataset names

# Base directory containing the prompts and datasets
BASE_DIR = "stats/run_evals/runs_features_v1/"  # Replace with your actual base directory

# Function to read compatibility scores
def read_scores(prompt_path, dataset):
    helpful_path = os.path.join(prompt_path, dataset, "helpful-compatibility.txt")
    harmful_path = os.path.join(prompt_path, dataset, "harmful-compatibility.txt")

    helpful_df = pd.read_csv(helpful_path)
    harmful_df = pd.read_csv(harmful_path)

    helpful_avg = helpful_df[helpful_df["topic"] == "average"]["compatibility"].values[0]
    harmful_avg = harmful_df[harmful_df["topic"] == "average"]["compatibility"].values[0]

    return helpful_avg, harmful_avg

# Function to generate plots for each prompt
def generate_plots():
    for prompt in os.listdir(BASE_DIR):
        prompt_path = os.path.join(BASE_DIR, prompt)
        if not os.path.isdir(prompt_path):
            continue

        helpful_scores = []
        harmful_scores = []
        labels = []

        for dataset in os.listdir(prompt_path):
            dataset_path = os.path.join(prompt_path, dataset)
            if not os.path.isdir(dataset_path):
                continue

            helpful, harmful = read_scores(prompt_path, dataset)
            helpful_scores.append(helpful)
            harmful_scores.append(harmful)
            labels.append(dataset)

        # Create the plot
        plt.figure(figsize=(10, 6))
        for i, dataset in enumerate(labels):
            #if dataset in AUTOMATIC_DATASETS:
            plt.scatter(helpful_scores[i], harmful_scores[i], color='red', marker='o', label='Automatic' if i == 0 else "")
            #elif dataset in MANUAL_DATASETS:
            #    plt.scatter(helpful_scores[i], harmful_scores[i], color='blue', marker='s', label='Manual' if i == 0 else "")

        plt.title(f"Prompt: {prompt}")
        plt.xlabel("Helpful Compatibility")
        plt.ylabel("Harmful Compatibility")
        plt.legend(title="Run Types")
        plt.grid(True)

        # Save the plot
        output_path = os.path.join(BASE_DIR, f"{prompt}_compatibility_plot.png")
        plt.savefig(output_path)
        plt.close()

if __name__ == "__main__":
    generate_plots()

