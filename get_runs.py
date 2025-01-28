from pyserini.search.lucene import LuceneSearcher
from gpt import evaluate, evaluate_batch
from trec_utils import get_topics_dict, get_qrels_dict_all
from itertools import combinations
import json
import os

# This script is for evaluating a set of (topic_id, doc_id) using ChatGPT

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

# Load the topics into a dictionary
topics = get_topics_dict("misinfo-2021-topics.xml")

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

def get_run_list(topic_list, qrels_name="all", exclude_list=[]):
    qrels = {}
    if qrels_name == "all":
        qrels = get_qrels_dict_all()
    else:
        qrels = get_qrels_dict(qrels_name) 

    run_list = {}
    for topic_id in qrels:
        if topic_id not in topic_list:
            continue
        run_list[topic_id] = []
        for doc_id in qrels[topic_id]:
            if is_visited(topic_id, doc_id, exclude_list):
                continue
            run_list[topic_id].append(doc_id)
    return run_list

history = {}

def run_run_list(prompt_template, run_list, num_runs=300, directory="runs", prompt_name="placeholder"):
    run_count = 0
    for topic_id, doc_ids in run_list.items():
        with open(os.path.join(directory, topic_id), "a") as file:
            for doc_id in doc_ids:
                if run_count >= num_runs:
                    break
                doc = json.loads(searcher.doc(doc_id).raw())["text"]
                #print(f"Evaluating {topic_id} {doc_id}")
                if (topic_id not in history):
                    history[topic_id] = {}
                if (doc_id not in history[topic_id]):
                        history[topic_id][doc_id] = {}
                if (prompt_template in history[topic_id][doc_id]):
                    print("Fatal error", topic_id, doc_id, prompt_template)
                history[topic_id][doc_id][prompt_template] = True
                #run = evaluate(topics[topic_id]["description"], topics[topic_id]["narrative"], doc, prompt_template)
                evaluate_batch(topics[topic_id]["description"], topics[topic_id]["narrative"], doc, prompt_template, topic_id, doc_id, prompt_name)
                run = None
                if run is not None:
                    run_count += 1
                    print(f"Writing to {os.path.join(directory, topic_id)}")
                    file.write(f'{doc_id} {run["u"]} {run["s"]} {run["cr"]}\n')

# Gives a run_list to run the same (topic,doc) pairs as another runs folder
def copy_run_list_from_folder(directory):
    run_list = {}
    for topic_id in os.listdir(directory):
        run_list[topic_id] = []
        with open(os.path.join(directory, topic_id), "r") as file:
            for line in file:
                doc_id,_,_,_ = line.split()
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
