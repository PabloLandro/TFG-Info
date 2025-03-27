import os, argparse, sys
import pandas as pd
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

def get_prompt_rbo(prompt_path, reference_rankings):
    if not os.path.isdir(prompt_path):
        raise Exception("Expected dir with participant_run stats, got file instead")
    prompt_rankings = get_rankings(prompt_path)

    # Compute RBO between the prompt and reference rankings
    rbo = compute_rbo(prompt_rankings, reference_rankings)
    return rbo

# Function to process all prompts and calculate RBO
def process_prompts_with_rbo(prompts_dir, reference_dir):
    if not os.path.isdir(prompts_dir):
        print(f"Error: {prompts_dir} does not exist or is not a directory.")
        return

    if not os.path.isdir(reference_dir):
        print(f"Error: {reference_dir} does not exist or is not a directory.")
        return

    reference_rankings = get_rankings(reference_dir)

    rbo_results = []

    for prompt in os.listdir(prompts_dir):
        prompt_path = os.path.join(prompts_dir, prompt)
        rbo = get_prompt_rbo(prompt_path, reference_rankings)
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

def create_parser():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Process directories for prompts and references.")

    # Add arguments for prompts_dir and reference_dir
    parser.add_argument("input", type=str, help="Path to the directory containing the participant run stats obtained with our qrels.")
    parser.add_argument("reference", type=str, help="Path to the directory containing the participant run stats obtained with official qrels.")
    parser.add_argument(
    "--mode",
    type=str,
    choices=["single", "features"],
    default="single",
    help="Mode of operation. 'single' for one prompt (input should be directory containing participant run stats) ; 'features' for multiple prompts (input is dir with a subdir for each prompt, inside which there are the participant run stats for each)."
)
    return parser

def verify_args(args, parser):
    # Verify the arguments
    if not os.path.isdir(args.input):
        print(f"Error: The specified prompts directory does not exist or is not a directory: {args.input}")
        parser.print_usage()
        sys.exit(1)

    if not os.path.isdir(args.reference):
        print(f"Error: The specified reference directory does not exist or is not a directory: {args.reference}")
        parser.print_usage()
        sys.exit(1)

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    verify_args(args, parser)
    if args.mode == "single":
        reference_rankings = get_rankings(args.reference)
        get_prompt_rbo(args.input, reference_rankings)
    elif args.mode == "features":
        process_prompts_with_rbo(args.input, args.reference)

