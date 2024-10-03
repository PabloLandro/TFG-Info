from pyserini.search.lucene import LuceneSearcher
import xml.etree.ElementTree as ET
import json

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

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
        if qrels[topic_id] is None:
            qrels[topic_id] = [aux]
        else:
            qrels[topic_id].append(aux)



def run_topic(topic_id, num_runs=1000):
    """
    This function generates (usefulness, supportiveness, credibility) evaluations
    for a given topic and a number of documents choosen randomly, but always including
    those for which there exists an evaluation in the qrel for that topic.
    """

    doc_ids = [doc["id"] for doc in searcher.search(topics[topic_id]["query"], k=num_runs)]
    runs = []

    # Dictionary with the docs that we already used for this run
    visited = {}

    for doc_id in doc_ids:
        doc = json.loads(searcher.doc(doc_id).raw())["text"]
        run = append(evaluate(topics[topic_id]["description"], doc))
        runs.append(f'{doc_id} {run["u"]} {run["s"]} {run["cr"]}')




