import os, argparse, sys
import pandas as pd
import matplotlib.pyplot as plt

DEPTH = 45

def read_scores_2021(prompt_path, dataset):
    helpful_path = os.path.join(prompt_path, dataset, "helpful-compatibility.txt")
    harmful_path = os.path.join(prompt_path, dataset, "harmful-compatibility.txt")

    helpful_df = pd.read_csv(helpful_path)
    harmful_df = pd.read_csv(harmful_path)

    helpful_avg = helpful_df[helpful_df["topic"] == "average"]["compatibility"].values[0]
    harmful_avg = harmful_df[harmful_df["topic"] == "average"]["compatibility"].values[0]

    return helpful_avg, harmful_avg

def read_scores_2022(prompt_path, dataset):
    summary_path = os.path.join(prompt_path, f"{dataset}")

    summary_df = pd.read_csv(summary_path, delimiter=r'\s|,|\t', engine='python')
    helpful_avg = float(summary_df[(summary_df["qrels"] == "graded.helpful-only") & (summary_df["topic"] == "average")]["score"].values[0])
    harmful_avg = float(summary_df[(summary_df["qrels"] == "graded.harmful-only") & (summary_df["topic"] == "average")]["score"].values[0])

    return helpful_avg, harmful_avg

# Function to read compatibility scores
def read_scores(prompt_path, dataset, year):
    if year == 2021:
        return read_scores_2021(prompt_path, dataset)
    elif year == 2022:
        return read_scores_2022(prompt_path, dataset)

# Function to compute RBO for two rankings
def compute_rbo(run, ideal, p=0.95):
    print("ours:")
    print(run)
    print("ideal:")
    print(ideal)
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
def get_rankings(base_dir, year):
    rankings = {}

    for dataset in os.listdir(base_dir):
        dataset_path = os.path.join(base_dir, dataset)
        helpful, harmful = read_scores(base_dir, dataset, year)
        rankings[dataset] = helpful - harmful

    # Sort datasets by helpful - harmful in descending order
    ranked = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked]

def get_prompt_rbo(prompt_path, reference_rankings, year):
    if not os.path.isdir(prompt_path):
        raise Exception("Expected dir with participant_run stats, got file instead")
    prompt_rankings = get_rankings(prompt_path, year)

    # Compute RBO between the prompt and reference rankings
    rbo = compute_rbo(prompt_rankings, reference_rankings)
    return rbo

# Function to process all prompts and calculate RBO
def process_prompts_with_rbo(prompts_dir, reference_dir, year):
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
        rbo = get_prompt_rbo(prompt_path, reference_rankings, year)
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
    parser.add_argument(
        "year", 
        type=int,  # Ensure year is an integer
        choices=[2019, 2020, 2021, 2022],  # Limit to specific years
        help="Year must be one of: 2019, 2020, 2021, 2022"
    )
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

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    verify_args(args, parser)

    reference = ""
    if args.year == 2019:
        pass
    elif args.year == 2020:
        pass
    elif args.year == 2021:
        reference = os.path.join("stats", "run_evals", "qrels-35topics_101.txt")
    elif args.year == 2022:
        reference = os.path.join("stats", "run_evals", "qrels.final.oct-19-2022")

    if args.mode == "single":
        reference_rankings = get_rankings(reference, args.year)
        rbo = get_prompt_rbo(args.input, reference_rankings, args.year)
        print(f"RBO between ranking of systems using official qrels vs ranking using our LLM qrels: {rbo}")
    elif args.mode == "features":
        process_prompts_with_rbo(args.input, reference, args.year)

