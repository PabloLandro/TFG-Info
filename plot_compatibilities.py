import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Define global arrays for dataset categories
AUTOMATIC_DATASETS = ["dataset1", "dataset2"]  # Replace with actual dataset names
MANUAL_DATASETS = ["dataset3", "dataset4"]     # Replace with actual dataset names

# Function to read compatibility scores
def read_scores(prompt_path, dataset):
    helpful_path = os.path.join(prompt_path, dataset, "helpful-compatibility.txt")
    harmful_path = os.path.join(prompt_path, dataset, "harmful-compatibility.txt")

    helpful_df = pd.read_csv(helpful_path)
    harmful_df = pd.read_csv(harmful_path)

    helpful_avg = helpful_df[helpful_df["topic"] == "average"]["compatibility"].values[0]
    harmful_avg = harmful_df[harmful_df["topic"] == "average"]["compatibility"].values[0]

    return helpful_avg, harmful_avg

# Function to generate a plot for a specific directory or its dataset subdirectories
def generate_plot(base_path, iterate_subdirs):
    if not os.path.isdir(base_path):
        print(f"Error: {base_path} does not exist or is not a directory.")
        return

    helpful_scores = []
    harmful_scores = []
    labels = []

    # Process dataset subdirectories
    if iterate_subdirs:
        datasets = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    else:
        datasets = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

    for dataset_name in datasets:
        dataset_path = os.path.join(base_path, dataset_name)
        helpful, harmful = read_scores(base_path, dataset_name)
        helpful_scores.append(helpful)
        harmful_scores.append(harmful)
        labels.append(dataset_name)

    # Create the plot
    plt.figure(figsize=(10, 6))
    for i, dataset in enumerate(labels):
        #if dataset in AUTOMATIC_DATASETS:
        plt.scatter(helpful_scores[i], harmful_scores[i], color='red', marker='o', label='Automatic' if i == 0 else "")
        #elif dataset in MANUAL_DATASETS:
        #    plt.scatter(helpful_scores[i], harmful_scores[i], color='blue', marker='s', label='Manual' if i == 0 else "")

    plt.title(f"Prompt: {os.path.basename(base_path)}")
    plt.xlabel("Helpful Compatibility")
    plt.ylabel("Harmful Compatibility")
    plt.legend(title="Run Types")
    plt.grid(True)

    # Save the plot
    output_path = os.path.join(base_path, f"compatibility_plot.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <directory_path> <iterate_subdirs: true/false>")
    else:
        directory_path = sys.argv[1]
        iterate_subdirs = sys.argv[2].lower() == "true"
        generate_plot(directory_path, iterate_subdirs)

