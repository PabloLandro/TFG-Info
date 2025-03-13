import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

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
def generate_plots(stats_base_dir):
    for prompt in os.listdir(stats_base_dir):
        prompt_path = os.path.join(stats_base_dir, prompt)
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

        min_harmful = min([d if d != 0 else 10e-6 for d in harmful_scores])
        harmful_scores = [d if d != 0 else min_harmful*10e-2 for d in harmful_scores]

        # Create the plot
        plt.figure(figsize=(10, 6))
        for i, dataset in enumerate(labels):
            plt.scatter(helpful_scores[i], harmful_scores[i], color='red', marker='o', label='Automatic' if i == 0 else "")

        plt.title(f"Prompt: {prompt}")
        plt.yscale("log")
        plt.xlabel("Helpful Compatibility")
        plt.ylabel("Harmful Compatibility")
        plt.legend(title="Run Types")
        plt.grid(True)

        # Save the plot
        output_path = os.path.join(stats_base_dir, f"{prompt}_compatibility_plot.png")
        plt.savefig(output_path)
        plt.close()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process the stats base directory.")
    
    # Add the argument
    parser.add_argument(
        "stats_base_dir",
        type=str,
        help="Path to the stats base directory."
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Access the argument value
    stats_base_dir = args.stats_base_dir
    
    # Check if the directory exists and is not empty
    if not os.path.exists(stats_base_dir):
        print(f"Error: The directory {stats_base_dir} does not exist.")
        return
    
    if not os.path.isdir(stats_base_dir):
        print(f"Error: {stats_base_dir} is not a directory.")
        return
    
    if not os.listdir(stats_base_dir):
        print(f"Error: The directory {stats_base_dir} is empty.")
        return

    generate_plots(stats_base_dir)

if __name__ == "__main__":
    generate_plots()

