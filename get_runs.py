from pyserini.search.lucene import LuceneSearcher
from gpt import evaluate
import xml.etree.ElementTree as ET
import json
import os

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")
root = ET.parse('resources/misinfo-2021-topics.xml').getroot()

# Load the topic into a dictionary
topics = {}
for topic in root.findall("topic"):
    topic_id = topic.find("number").text
    topics[topic_id] = {}
    topics[topic_id]["query"] = topic.find("query").text
    topics[topic_id]["description"] = topic.find("description").text
    topics[topic_id]["stance"] = topic.find("stance").text

def get_topic(topic_id):
    return topics[topic_id]

# We are going to save every qrel on a dictionary using the topic id
qrels = {}

with open("resources/misinfo-qrels.3aspects", "r") as file:

    for line in file:
        topic_id, _, doc_id, u, s, cr = line.split()
        aux = {}
        aux["id"] = doc_id
        aux["u"] = u
        aux["s"] = s
        aux["cr"] = cr
        if not topic_id in qrels:
            qrels[topic_id] = [aux]
        else:
            qrels[topic_id].append(aux)

exclude = {}
for topic_id in os.listdir("runs"):
    exclude[topic_id] = {}
    with open(os.path.join("runs", topic_id), "r") as file:
        for line in file:
            doc_id,_,_,_ = line.split()
            exclude[topic_id][doc_id] = True

def is_visited(topic_id, doc_id):
    if topic_id in exclude and doc_id in exclude[topic_id]:
        return True
    return False


# Evaluates a number of documents for a topic
# The documents are chosen using the pyserini search function using the topic's query
def run_topic(topic_id, num_runs=1000):
    """
    This function generates (usefulness, supportiveness, credibility) evaluations
    for a given topic and a number of documents choosen randomly, but always including
    those for which there exists an evaluation in the qrel for that topic.
    """

    doc_ids = [doc.docid for doc in searcher.search(topics[topic_id]["query"], k=num_runs)]
    runs = []

    # Dictionary with the docs that we already used for this run
    visited = {}

    for doc_id in doc_ids:
        if is_visited(topic_id, doc_id):
            continue
        print(doc_id)
        doc = json.loads(searcher.doc(doc_id).raw())["text"]
        run = evaluate(topics[topic_id]["description"], doc)
        if run is not None:
            runs.append(f'{doc_id} {run["u"]} {run["s"]} {run["cr"]}')
    with open(f"runs/{topic_id}", "w") as file:
        for run in runs:
            file.write(run + "\n")

list = [109, 110, 111, 112, 114]
for id in list:
    print(f"Starting with {id}")
    run_topic(str(id), num_runs=300)
