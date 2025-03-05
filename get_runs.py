from pyserini.search.lucene import LuceneSearcher
from gpt import evaluate, print_total_tokens
from trec_utils import get_topics_dict, get_qrels_dict_all, get_qrels_dict
from itertools import combinations
import os, argparse, json, sys

# This script is for evaluating a set of (topic_id, doc_id) using ChatGPT

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

# Load the topics into a dictionary
topics = get_topics_dict(os.path.join("resources", "topics", "misinfo-2021-topics.xml"))

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

def get_run_list(topic_list, qrels_name="misinfo-qrels.3aspects", exclude_list=[]):
    qrels = {}
    if qrels_name == "all":
        qrels = get_qrels_dict_all()
    else:
        qrels = get_qrels_dict(qrels_name) 

    run_list = {}
    for topic_id in topic_list:
        run_list[topic_id] = []
        for doc_id in qrels[topic_id]:
            if is_visited(topic_id, doc_id, exclude_list):
                continue
            run_list[topic_id].append(doc_id)
    return run_list

# This is used to check that the same prompt template for the same topic and doc is being sent twice
history = {}

def run_run_list(prompt_template, run_list, output, no_evaluate=False):
    run_count = 0
    for topic_id, doc_ids in run_list.items():
        with open(output, "a") as file:
            for doc_id in doc_ids:
                doc = json.loads(searcher.doc(doc_id).raw())["text"]
                print(f"Evaluating {topic_id} {doc_id} {run_count}/{len(run_list)} for current prompt template")
                run_count += 1
                if (topic_id not in history):
                    history[topic_id] = {}
                if (doc_id not in history[topic_id]):
                        history[topic_id][doc_id] = {}
                if (prompt_template in history[topic_id][doc_id]):
                    print("Fatal error, repeated (topic_id, doc_id, prompt_template) run, should revise code", topic_id, doc_id, prompt_template)
                history[topic_id][doc_id][prompt_template] = True
                run = evaluate(topics[topic_id]["description"], topics[topic_id]["narrative"], doc, prompt_template, no_evaluate=no_evaluate)
                if run is not None:
                    print(f"Writing to {output}")
                    file.write(f'{topic_id} 0 {doc_id} {run["u"]} {run["s"]} {run["cr"]}\n')

# Gives a run_list to run the same (topic,doc) pairs as another runs folder
def copy_run_list_from_file(file):
    run_list = {}
    with open(file, "r") as file:
        for line in file:
            topic_id,_,doc_id,_,_,_ = line.split()
            run_list[topic_id].append(doc_id)
    return run_list

# Replaces all elements in directory that are present in the run_list with new runs
def replace_folder_with_run_list(run_list, directory):
    for topic_id in os.listdir(directory):
        if topic_id not in run_list:
            continue
        with open(os.path.join(directory, topic_id), "r") as file, open("auxfile", "w") as auxfile:
            for line in file:
                doc_id,_,_,_ = line.split()
                if doc_id not in run_list[topic_id]:
                    auxfile.write(line)
                else:
                    doc = json.loads(searcher.doc(doc_id).raw())["text"]
                    print(f"Evaluating {topic_id} {doc_id}")
                    run = evaluate(topics[topic_id]["description"], topics[topic_id]["narrative"], doc)
                    if run is not None:
                        auxfile.write(f'{doc_id} {run["u"]} {run["s"]} {run["cr"]}\n')
                        print(f"Writing to {os.path.join('runs', topic_id)}")
        os.replace("auxfile", os.path.join(directory, topic_id))

def get_runs_featured_prompt(featured_prompt_template, qrels_file, output_dir, topic_list, prompt_names=[], no_evaluate=False):
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
        run_list = get_run_list(topic_list, qrels_file, exclude_list=exclude_list)
        run_run_list(prompt_template, run_list, path, send_request=False, no_evaluate=no_evaluate)

def get_runs_non_featured_prompt(prompt_template, qrels_file, output_file, topic_list, no_evaluate=False):
    exclude_list = copy_run_list_from_file(output_file)
    run_list = get_run_list(topic_list, qrels_file, exclude_list)
    run_run_list(prompt_template, run_list, output_file, no_evaluate=no_evaluate)


def create_parser():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process prompt files and related data.")

    # Required arguments
    parser.add_argument("prompt_file", help="The prompt file to use, if featured prompt, the name should contain the 'feature' substring.")
    parser.add_argument("qrels_file", help="The qrels file to be used.")
    parser.add_argument("output", help="Directory to save the output. If it's a non featured prompt, it should be a file")
    parser.add_argument("topic_list", help="Comma-separated list of topics (e.g. 101,102,103)", type=lambda s: list(map(int, s.split(','))))

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

    # qrels_file

    if not os.path.isfile(args.qrels_file):
        print(f"{args.qrels_file} is not a file, should be the qrels_file.")
        parser.print_help()
        sys.exit()

    # output

    is_feature_prompt = "feature" in args.prompt_file.lower()

    # Check if output is correct
    if os.path.isfile(args.output):
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

    # Call the appropriate function based on the type of prompt
    if is_feature_prompt:
        get_runs_featured_prompt(prompt_template, args.qrels_file, args.output_directory, args.topic_list, prompt_names=args.prompt_name, no_evaluate=args.no_evaluate)
    else:
        get_runs_non_featured_prompt(prompt_template, args.qrels_file, args.output_directory, args.topic_list, no_evaluate=args.no_evaluate)

    print_total_tokens()
