import os, json, rbo
from gpt import evaluate
from pyserini.search.lucene import LuceneSearcher
import xml.etree.ElementTree as ET

def preprocess_run(run):
    run["u"] = int(run["u"])
    run["s"] = int(run["s"])
    run["cr"] = int(run["cr"])from trec_utils import get_correctness, get_preference, get_topics_dict, get_qrels_dict


# Computes the correctness and preference metrics then orders the run by preference
def order_run(topic, run):
    for doc_run in run:
        doc_run["co"] = get_correctness(topic["stance"], doc_run["s"])
        doc_run["p"] = get_preference(doc_run["u"], doc_run["co"], doc_run["cr"])
    run.sort(key = lambda x: x["p"])

# Compute the Rank Biased Overlap score
def compute_rbo(topic, run, ideal_run):
    order_run(topic, run)
    order_run(topic, ideal_run)
    helpful_ideal_run = [doc_run for doc_run in ideal_run if doc_run["p"] > 0]
    harmful_ideal_run = [doc_run for doc_run in ideal_run if doc_run["p"] <= 0]

    # Reverse the order of harmful documents
    harmful_ideal_run = harmful_ideal_run[::-1]

    # We return a pair with the compatibility with helpful documents and harmful documents
    rbo_helpful = rbo.RankingSimilarity([doc_run["doc_id"] for doc_run in run], [doc_run["doc_id"] for doc_run in helpful_ideal_run]).rbo()
    rbo_harmful = rbo.RankingSimilarity([doc_run["doc_id"] for doc_run in run], [doc_run["doc_id"] for doc_run in harmful_ideal_run]).rbo()
    return rbo_helpful, rbo_harmful

# Load the topic into a dictionary
topics = get_topics_dict("misinfo-2021-topics.xml")

# Load the qrel runs into a dictionary indexed by topic_id
qrels = get_qrels_dict("misinfo-qrels.3aspects")

# Initialize searcher
searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

helpful_rbos = []
harmful_rbos = []


# We iterate over the run files (named with their topic_id)
for topic_id in os.listdir("runs"):

    run = []

    with open(os.path.join("runs", topic_id), "r") as file:
        for line in file:
            doc_run = {}
            doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] =  line.split(" ")
            preprocess_run(doc_run)
            run.append(doc_run)
    helpful_rbo, harmful_rbo = compute_rbo(topics[topic_id], run, qrels[topic_id])
    helpful_rbos.append(helpful_rbo)
    harmful_rbos.append(harmful_rbo)

helpful_avg = sum(helpful_rbos) / len(helpful_rbos)
harmful_avg = sum(harmful_rbos) / len(harmful_rbos)

print(f"Compatibility with helpful documents: {helpful_avg}")
print(f"Compatibility with harmful documents: {harmful_avg}")

for run in qrels.values():
    if len(run) == 0:
        continue
    order_run(topics[run[0]["topic_id"]], run)
    print(f"{run[0]['topic_id']}: {any(doc_run['p']<=0 for doc_run in run)}")
