from gpt import evaluate, print_total_tokens
from trec_utils import get_year_data, set_year, read_gpt_output, write_run_to_file
from itertools import combinations
import os, argparse, json, sys

# Get all combinations of prompts by changing features
def get_prompt_template_list(featured_prompt_template):
    features = {}

    main = ""

    reading = ""

    for line in featured_prompt_template.splitlines():
        if reading == "" and line.endswith(":"):
            reading = line.rstrip(":")
            features[reading] = ""
        elif reading != "" and line != "---":
            features[reading] += "\n" + line
        elif line == "---":
            reading = ""

    main = features["main"]

    del features["main"]

    # Generate all combinations of features
    all_combinations = []
    for r in range(len(features) + 1):
        all_combinations.extend(combinations(features, r))

    # Generate prompts by including or excluding features
    prompts = []
    for combination in all_combinations:
        prompt = main
        for feature in features:
            if feature not in combination:
                prompt = prompt.replace(f"{{{feature}}}", "")
            else:
                prompt = prompt.replace(f"{{{feature}}}", features[feature])
        prompts.append((prompt, combination))
    return prompts


# Have this function for checking if a topic_id, doc_id pair was already evaluated
def is_visited(topic_id, doc_id, exclude_list):
    if topic_id in exclude_list and doc_id in exclude_list[topic_id]:
        return True
    return False

def get_run_list(topic_list, qrels, exclude_list=[]):
    run_list = {}
    print(topic_list)
    if len(topic_list) == 1 and topic_list[0] == "all":
        topic_list = list(qrels.keys())

    for topic_id in topic_list:
        run_list[topic_id] = []
        for doc_id in qrels[topic_id]:
            if is_visited(topic_id, doc_id, exclude_list):
                continue
            run_list[topic_id].append(doc_id)
    return run_list

not_found_list = []

def get_doc_content(searcher, doc_id):
    use_id = doc_id
    if searcher.doc(doc_id) is None:
        print("changing id")
        use_id = "<urn:uuid:" + doc_id + ">"
    try:
        return json.loads(searcher.doc(use_id).raw())["text"]
    except:
        print(f"ERROR, failed with doc_id: {doc_id}")
        if not searcher.doc(use_id) is None:
            return searcher.doc(use_id).raw() 
        not_found_list.append(doc_id)
        return None


# This is used to check that the same prompt template for the same topic and doc is being sent twice
history = {}

def run_run_list(prompt_template, run_list, output, topics, searcher, no_evaluate=False):
    run_count = 0
    for topic_id, doc_ids in run_list.items():
        with open(output, "a") as file:
            for doc_id in doc_ids:
                doc = get_doc_content(searcher, doc_id) 
                if doc is None:
                    continue
                print(f"Evaluating {topic_id} {doc_id} {run_count}/{len(run_list[topic_id])} for current prompt template")
                run_count += 1
                if (topic_id not in history):
                    history[topic_id] = {}
                if (doc_id not in history[topic_id]):
                        history[topic_id][doc_id] = {}
                if (prompt_template in history[topic_id][doc_id]):
                    print("Fatal error, repeated (topic_id, doc_id, prompt_template) run, should revise code", topic_id, doc_id, prompt_template)
                history[topic_id][doc_id][prompt_template] = True
                gpt_output = evaluate(topics[topic_id]["query"], topics[topic_id]["description"], topics[topic_id]["narrative"], doc, prompt_template, no_evaluate=no_evaluate)
                run = read_gpt_output(gpt_output)
                if run is None:
                    raise Exception("None run")
                print(f"Writing to {output}")
                write_run_to_file(file, topic_id, doc_id, run)

# Gives a run_list to run the same (topic,doc) pairs as another runs folder
def copy_run_list_from_file(file):
    run_list = {}
    try:
        with open(file, "r") as file:
            for line in file:
                topic_id, _, doc_id, _, _, _ = line.split()
                if topic_id not in run_list:
                    run_list[topic_id] = []
                run_list[topic_id].append(doc_id)
    except FileNotFoundError:
        print(f"Error: The file '{file}' does not exist, couldn´t copy run list from file.")
    return run_list

def print_not_found_docs():
    global not_found_list
    print("The following docs where not found in the indexes")
    print(not_found_list)


def get_runs_featured_prompt(featured_prompt_template, qrels, topics, searcher, output_dir, topic_list, prompt_names=[], no_evaluate=False):
    prompt_template_list = get_prompt_template_list(featured_prompt_template)
    os.makedirs(output_dir, exist_ok=True)
    for (prompt_template, features) in prompt_template_list:
        file_name = ""
        if len(features) == 0:
            file_name = "Nothing"
        else:
            file_name = "".join([feature[0].upper() + feature[1] + feature[2] for feature in features])
        if len(prompt_names) > 0 and file_name not in  prompt_names:
            continue
        print("Evaluating", file_name)
        path = os.path.join(output_dir, file_name)
        exclude_list = copy_run_list_from_file(path)
        print("Exclude list:")
        print(exclude_list)
        run_list = get_run_list(topic_list, qrels, exclude_list=exclude_list)
        run_run_list(prompt_template, run_list, path, topics, searcher, no_evaluate=no_evaluate)

def get_runs_non_featured_prompt(prompt_template, qrels, topics, searcher, output_file, topic_list, no_evaluate=False):
    exclude_list = copy_run_list_from_file(output_file)
    run_list = get_run_list(topic_list, qrels, exclude_list)
    run_run_list(prompt_template, run_list, output_file, topics, searcher, no_evaluate=no_evaluate)


def create_parser():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process prompt files and related data.")

    # Required arguments
    parser.add_argument("prompt_file", help="The prompt file to use, if featured prompt, the name should contain the 'feature' substring.")
    parser.add_argument(
        "--year",
        type=int,
        choices=[2019, 2020, 2021, 2022],
        required=True,
        help="Year must be one of 2019, 2020, 2021, or 2022."
    )
    parser.add_argument("output", help="Directory to save the output. If it's a non featured prompt, it should be a file")
    
    parser.add_argument("topic_list", help="Comma-separated list of topics (e.g. 101,102,103)", type=lambda s: s.split(','))

    # Optional argument for prompt names
    parser.add_argument("--prompt_names", help="Comma-separated list of prompt names to be run on featured prompt, if not present, all will be ran (optional) (e.g. Str,Nar,Des)", nargs="?", default=[])
    parser.add_argument("--no_evaluate", help="If present, requests will not be sent to LLM API, this can be used to just count tokens (optional)", action="store_true")
    return parser

def check_args(parser, args):

    # prompt_file

    if not os.path.isfile(args.prompt_file):
        print(f"{args.prompt_file} is not a file, should be the prompt_file.")
        parser.print_help()
        sys.exit()

    # output

    is_feature_prompt = "feature" in args.prompt_file.lower()

    # Check if output is correct
    if os.path.isfile(args.output) and is_feature_prompt:
        print(f"{args.output} is a file, when it should be a dir.")
        parser.print_help()
        sys.exit()
    elif os.path.isdir(args.output) and not is_feature_prompt:
        print(f"{args.output} is a directory, when it should be a file.")
        parser.print_help()
        sys.exit()
    elif not os.path.isdir(args.output) and not os.path.isfile(args.output):
        print(f"{args.output} is not a valid output, it does not exist or is neither a file nor a directory.")
        parser.print_help()
        sys.exit()

if __name__ == "__main__":
    
    parser = create_parser()

    # Parse the arguments
    args = parser.parse_args()

    # Read the prompt template from the file
    prompt_template = ""
    with open(args.prompt_file, "r") as file:
        prompt_template = file.read()

    # Check if the prompt file contains "feature"
    is_feature_prompt = "feature" in args.prompt_file.lower()

    check_args(parser, args)

    set_year(args.year)

    qrels, topics, searcher = get_year_data()

    # Call the appropriate function based on the type of prompt
    if is_feature_prompt:
        print("Starting")
        get_runs_featured_prompt(prompt_template, qrels, topics, searcher, args.output, args.topic_list, prompt_names=args.prompt_names, no_evaluate=args.no_evaluate)
    else:
        get_runs_non_featured_prompt(prompt_template, qrels, topics, searcher, args.output, args.topic_list, no_evaluate=args.no_evaluate)

    print_not_found_docs()
    print_total_tokens()
