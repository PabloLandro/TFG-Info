import os
from trec_utils import get_qrels_dict, preprocess_run

# Load the qrel runs into a dictionary indexed by topic_id
qrels = get_qrels_dict("misinfo-qrels.3aspects")
# We will create a similar structure for the LLM runs
runs = {}

# Iterate over every topic run file
for topic_id in os.listdir("runs"):
    run = {}

    with open(os.path.join("runs", topic_id), "r") as file:
        for line in file:
            doc_run = {}

            # Read every doc_run for this topic
            doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = line.split(" ")
            # If there is not qrel run for this document, we skip it
            if not doc_run["doc_id"] in qrels[topic_id]:
                continue
            # Add correctiveness and preference
            preprocess_run(doc_run)
            run[doc_run["doc_id"]] = doc_run
    runs[topic_id] = run
    # Check if there is any document missing
    missing_docs = 0
    for doc_id in qrels[topic_id]:
        if doc_id not in run:
            missing_docs += 1
    if missing_docs > 0:
        print(f"WARN: Missing {missing_docs} documents for topic {topic_id}")

for topic_id in qrels:
    if not topic_id in runs:
        print(f"WARN: Missing topic {topic_id} run")

def print_confussion(stat, pos_vals):
    TP = 0
    FP = 0
    FN = 0
    TN = 0

    for topic_id in runs:
        for doc_id in runs[topic_id]:
            # If there is not a qrel for that doc_id, we skip
            if doc_id not in qrels[topic_id]:
                continue

            if qrels[topic_id][doc_id][stat] in pos_vals:
                if runs[topic_id][doc_id][stat] in pos_vals:
                    TP += 1
                else:
                    FN += 1
            else:
                if runs[topic_id][doc_id]["u"] in pos_vals:
                    FP += 1
                else:
                    TN += 1

    print(f"TP={TP}\tFP={FP}\tFN={FN}\tTN={TN}")


print_confussion("u", [1, 2])
