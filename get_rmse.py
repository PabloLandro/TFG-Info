import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

# Function to read compatibility scores
def read_scores(prompt_path, dataset):
    helpful_path = os.path.join(prompt_path, dataset, "helpful-compatibility.txt")
    harmful_path = os.path.join(prompt_path, dataset, "harmful-compatibility.txt")

    helpful_df = pd.read_csv(helpful_path)
    harmful_df = pd.read_csv(harmful_path)

    helpful_avg = helpful_df[helpful_df["topic"] == "average"]["compatibility"].values[0]
    harmful_avg = harmful_df[harmful_df["topic"] == "average"]["compatibility"].values[0]

    return helpful_avg, harmful_avg

# Function to calculate 2D RMSE between prompt scores and reference scores
def calculate_rmse_2d(prompt_dir, reference_dir):
    prompt_scores = {}
    reference_scores = {}

    # Read scores for the prompt datasets
    for dataset in os.listdir(prompt_dir):
        dataset_path = os.path.join(prompt_dir, dataset)
        if os.path.isdir(dataset_path):
            helpful, harmful = read_scores(prompt_dir, dataset)
            prompt_scores[dataset] = (helpful, harmful)

    # Read scores for the reference datasets
    for dataset in os.listdir(reference_dir):
        dataset_path = os.path.join(reference_dir, dataset)
        if os.path.isdir(dataset_path):
            helpful, harmful = read_scores(reference_dir, dataset)
            reference_scores[dataset] = (helpful, harmful)

    # Calculate RMSE in 2D
    squared_errors = []

    for dataset, (prompt_helpful, prompt_harmful) in prompt_scores.items():
        if dataset in reference_scores:
            ref_helpful, ref_harmful = reference_scores[dataset]
            squared_errors.append(
                (prompt_helpful - ref_helpful) ** 2 + (prompt_harmful - ref_harmful) ** 2
            )

    overall_rmse = np.sqrt(np.mean(squared_errors)) if squared_errors else None
    return overall_rmse

# Function to process all prompt directories and generate RMSE plots
def process_prompts(prompts_dir, reference_dir):
    if not os.path.isdir(prompts_dir):
        print(f"Error: {prompts_dir} does not exist or is not a directory.")
        return

    if not os.path.isdir(reference_dir):
        print(f"Error: {reference_dir} does not exist or is not a directory.")
        return

    results = []

    for prompt in os.listdir(prompts_dir):
        prompt_path = os.path.join(prompts_dir, prompt)
        if os.path.isdir(prompt_path):
            overall_rmse = calculate_rmse_2d(prompt_path, reference_dir)
            results.append((prompt, overall_rmse))

    # Plot RMSE
    prompts = [r[0] for r in results]
    rmses = [r[1] for r in results]

    x = np.arange(len(prompts))

    plt.figure(figsize=(12, 6))
    plt.bar(x, rmses, color="purple")

    plt.xlabel("Prompts")
    plt.ylabel("Overall RMSE")
    plt.title("Overall RMSE of Compatibility Scores in 2D")
    plt.xticks(x, prompts, rotation=45, ha="right")
    plt.tight_layout()

    output_plot = os.path.join(prompts_dir, "overall_rmse_plot.png")
    plt.savefig(output_plot)
    plt.close()
    print(f"Overall RMSE plot saved to {output_plot}")

    # Save results to CSV
    output_csv = os.path.join(prompts_dir, "overall_rmse_results.csv")
    pd.DataFrame(results, columns=["Prompt", "Overall RMSE"]).to_csv(output_csv, index=False)
    print(f"Overall RMSE results saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <prompts_dir> <reference_dir>")
    else:
        prompts_dir = sys.argv[1]
        reference_dir = sys.argv[2]
        process_prompts(prompts_dir, reference_dir)

