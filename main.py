import os, json, rbo
from gpt import evaluate
from pyserini.search.lucene import LuceneSearcher
import xml.etree.ElementTree as ET



def get_correctness(stance, supportiveness):
    if stance == "helpful":
        if supportiveness == 2:
            return 2
        elif supportiveness == 0:
            return 0
    elif stance == "unhelpful":
        if supportiveness == 2:
            return 0
        elif supportiveness == 0:
            return 2
    else:
        return 1

def get_preference(u, co, cr):

    if u == 0:
        return 0

    # Correct
    if co == 2:
        if cr == 2:
            if u == 2:
                return 12
            elif u == 1:
                return 11
        elif cr == 1:
            if u == 2:
                return 10
            elif u == 1:
                return 9
        elif cr == 0:
            if u == 2:
                return 8
            elif u == 1:
                return 7
    # Neutral
    elif co == 1:
        if cr == 2:
            if u == 2:
                return 6
            elif u == 1:
                return 5
        elif cr == 1:
            if u == 2:
                return 4
            elif u == 1:
                return 3
        elif cr == 0:
            if u == 2:
                return 2
            elif u == 1:
                return 1

    # Incorrect
    elif co == 0:
        if cr == 0:
            return -1
        elif cr == 1:
            return -2
        elif cr == 2:
            return -3
    return -4

# Computes the correctness and preference metrics then orders the run by preference
def order_run(topic, run):
    for doc_run in run:
        doc_run["co"] = get_correctness(topic["stance"], doc_run["s"])
        doc_run["p"] = get_preference(topic["u"], topic["co"], topic["cr"])
    run = sorted(run, key = lambda x: x["p"])

# Compute the Rank Biased Overlap score
def compute_rbo(topic, run, ideal_run):
    order_run(topic, run)
    order_run(topic, ideal_run)
    helpful_ideal_run = [doc_run for doc_run in ideal_run if doc_run["preference"] > 0]
    harmful_ideal_run = [doc_run for doc_run in ideal_run if doc_run["preference"] <= 0]
    # Reverse the order of harmful documents
    harmful_ideal_run = harmful_ideal_run[::-1]
    # We return a pair with the compatibility with helpful documents and harmful documents
    rbo_helpful = rbo.RankingSimilarity([doc_run["doc_id"] for doc_run in run], [doc_run["doc_id"] for doc_run in helpful_ideal_run]).rbo()
    rbo_harmful = rbo.RankingSimilarity([doc_run["doc_id"] for doc_run in run], [doc_run["doc_id"] for doc_run in harmful_ideal_run]).rbo()
    return rbo_helpful, rbo_harmful

# Open the topics file as an xml tree
root = ET.parse('resources/misinfo-2021-topics.xml').getroot()

# Load the topic into a dictionary
topics = {}
for topic in root.findall("topic"):
    topic_id = topic.find("number").text
    topics[topic_id] = {}
    topics[topic_id]["description"] = topic.find("description").text
    topics[topic_id]["stance"] = topic.find("stance").text

# Load the qrel runs into a dictionary indexed by topic_id
qrels = {}
with open(os.path.join("resources", "misinfo-qrels.3aspects") as file:
    last_topic_id = ""
    run = []
    for line in file:
        doc_run = {}
        topic_id, _, doc_id, doc_run["u"], doc_run["s"], doc_run["cr"] = line.split()
        if last_topic_id != topic_id:
            qrels[last_topic_id] = run
            run = [doc_run]
        else:
            run.append(doc_run)

# Initialize searcher
searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

helpful_rbos = []


# We iterate over the run files (named with their topic_id)
for topic_id in os.listdir("runs"):

    run = []

    with open(os.path.join("runs", topic_id) as file:
        for line in file:
            doc_run = {}
            doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] =  line.split(" ")
            run.append(doc_run)
    helpful_rbo, harmful_rbo = compute_rbo(topics["top_id"], run, qrels[topic_id])
    helpful_rbos.append(helpful_rbo)
    harmful_rbos.append(harmful_rbo)

print(f"Compatibility with helpful documents: {helpful_rbos}")
print(f"Compatibility with harmful documents: {harmful_rbos}")
