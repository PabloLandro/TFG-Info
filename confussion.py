import os
from trec_utils import get_qrels_dict, get_qrels_dict_all, preprocess_run

runs_directory="runs"

# Load the qrel runs into a dictionary indexed by topic_id
qrels = get_qrels_dict_all()
# We will create a similar structure for the LLM runs
runs = {}

def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return false

# Iterate over every topic run file
for topic_id in os.listdir(runs_directory):
    if not is_int(topic_id):
        continue
    run = {}
    with open(os.path.join(runs_directory, topic_id), "r") as file:
        count = 0
        for line in file:
            doc_run = {}

            # Read every doc_run for this topic
            doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = line.split(" ")
            # If there is not qrel run for this document, we skip it
            if not doc_run["doc_id"] in qrels[topic_id]:
                #print("Doc not found in qrels")
                continue
            count += 1
            # Add correctiveness and preference
            preprocess_run(doc_run)
            run[doc_run["doc_id"]] = doc_run
        #print(f"{topic_id} valid: {count}")
    runs[topic_id] = run
    # Check if there is any document missing
    missing_docs = 0
    for doc_id in qrels[topic_id]:
        if doc_id not in run:
            missing_docs += 1
    if missing_docs > 0:
        #print(f"WARN: Missing {missing_docs} documents for topic {topic_id}")
        pass

for topic_id in runs:
    pos = 0
    neg = 0
    for doc_id in runs[topic_id]:
        if qrels[topic_id][doc_id]['u'] > 0:
            pos += 1
        else:
            neg += 1
    #print(f"For topic_id {topic_id} there are {pos} useful qrels and {neg} unuseful")

for topic_id in qrels:
    if not topic_id in runs:
        #print(f"WARN: Missing topic {topic_id} run")
        pass

def print_confussion(stat, pos_vals, name):
    TP = 0
    FP = 0
    FN = 0
    TN = 0

    for topic_id in runs:
        for doc_id in runs[topic_id]:
            # If there is not a qrel for that doc_id, we skip
            if doc_id not in qrels[topic_id]:
                continue

            real = qrels[topic_id][doc_id][stat]
            pred = runs[topic_id][doc_id][stat]

            if real is None or pred is None:
                continue

            if real in pos_vals:
                if pred in pos_vals:
                    TP += 1
                else:
                    FN += 1
            else:
                if pred in pos_vals:
                    FP += 1
                else:
                    TN += 1
    
    print(f"\n{name} confussion matrix:")
    print(f"TP={TP}\tFP={FP}\tFN={FN}\tTN={TN}")

    precision = TP / (TP+FP)
    print(f"Precision: {precision}")

    recall = TP / (TP + FN)
    print(f"Recall: {recall}\n")

print_confussion("u", [1, 2], "Usefulness")

print_confussion("cr", [1,2], "Credibility")

print_confussion("s", [1,2], "Supportiveness")
