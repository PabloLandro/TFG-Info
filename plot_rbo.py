import os
import pandas as pd
import sys
import matplotlib.pyplot as plt

DEPTH = 70

# Function to read compatibility scores
def read_scores(prompt_path, dataset):
    helpful_path = os.path.join(prompt_path, dataset, "helpful-compatibility.txt")
    harmful_path = os.path.join(prompt_path, dataset, "harmful-compatibility.txt")

    helpful_df = pd.read_csv(helpful_path)
    harmful_df = pd.read_csv(harmful_path)

    helpful_avg = helpful_df[helpful_df["topic"] == "average"]["compatibility"].values[0]
    harmful_avg = harmful_df[harmful_df["topic"] == "average"]["compatibility"].values[0]

    return helpful_avg, harmful_avg

# Function to compute RBO for two rankings
def compute_rbo(run, ideal, p=0.95):
    run_set = set()
    ideal_set = set()

    score = 0.0
    normalizer = 0.0
    weight = 1.0
    for i in range(DEPTH):
        if i < len(run):
            run_set.add(run[i])
        if i < len(ideal):
            ideal_set.add(ideal[i])
        score += weight*len(ideal_set.intersection(run_set))/(i + 1)
        normalizer += weight
        weight *= p
    return score/normalizer 
# Function to get dataset rankings based on helpful - harmful
def get_rankings(base_dir):
    rankings = {}

    for dataset in os.listdir(base_dir):
        dataset_path = os.path.join(base_dir, dataset)
        if os.path.isdir(dataset_path):
            helpful, harmful = read_scores(base_dir, dataset)
            rankings[dataset] = helpful - harmful

    # Sort datasets by helpful - harmful in descending order
    ranked = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked]

# Function to process all prompts and calculate RBO
def process_prompts_with_rbo(prompts_dir, reference_dir):
    if not os.path.isdir(prompts_dir):
        print(f"Error: {prompts_dir} does not exist or is not a directory.")
        return

    if not os.path.isdir(reference_dir):
        print(f"Error: {reference_dir} does not exist or is not a directory.")
        return

    rbo_results = []

    for prompt in os.listdir(prompts_dir):
        prompt_path = os.path.join(prompts_dir, prompt)
        if os.path.isdir(prompt_path):
            prompt_rankings = get_rankings(prompt_path)
            reference_rankings = get_rankings(reference_dir)

            # Compute RBO between the prompt and reference rankings
            rbo = compute_rbo(prompt_rankings, reference_rankings)
            rbo_results.append((prompt, rbo))

    # Save results to CSV
    output_csv = os.path.join(prompts_dir, "rbo_results.csv")
    pd.DataFrame(rbo_results, columns=["Prompt", "RBO"]).to_csv(output_csv, index=False)
    print(f"RBO results saved to {output_csv}")

    # Plot RBO
    prompts = [r[0] for r in rbo_results]
    rbo_scores = [r[1] for r in rbo_results]

    plt.figure(figsize=(12, 6))
    plt.bar(prompts, rbo_scores, color="green")
    plt.xlabel("Prompts")
    plt.ylabel("RBO")
    plt.title("Rank-Biased Overlap (RBO) for Prompt Rankings")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_plot = os.path.join(prompts_dir, "rbo_plot.png")
    plt.savefig(output_plot)
    plt.close()
    print(f"RBO plot saved to {output_plot}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <prompts_dir> <reference_dir>")
    else:
        prompts_dir = sys.argv[1]
        reference_dir = sys.argv[2]
        process_prompts_with_rbo(prompts_dir, reference_dir)

