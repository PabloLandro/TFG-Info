from pyserini.search.lucene import LuceneSearcher
from gpt import evaluate
from trec_utils import get_topics_dict
import json
import os

print("Starting work")

# Load the topics into a dictionary
topics = get_topics_dict("misinfo-2021-topics.xml")

print("Loaded the topics")

def get_topic(topic_id):
    return topics[topic_id]

# For every topic_id we want to know what doc_ids we have already evaluated
exclude = {}
count = {}
for topic_id in os.listdir("runs"):
    exclude[topic_id] = {}
    count[topic_id] = 0
    with open(os.path.join("runs", topic_id), "r") as file:
        for line in file:
            doc_id,_,_,_ = line.split()
            exclude[topic_id][doc_id] = True
            count[topic_id] += 1

print("Exclude list created")

# Have this function for checking if a topic_id, doc_id pair was already evaluated
def is_visited(topic_id, doc_id):
    if topic_id in exclude and doc_id in exclude[topic_id]:
        return True
    return False

def get_run_list(filename, topic_list):
    run_list = {}
    with open(os.path.join("resources", "qrels", filename), "r") as file:
        for line in file:
            topic_id,_,doc_id,_,_,_ = line.split()
            if topic_id not in topic_list or is_visited(topic_id, doc_id):
                continue
            if topic_id not in run_list:
                run_list[topic_id] = []
            run_list[topic_id].append(doc_id)
    return run_list

def run_run_list(run_list, num_runs=300):
    for topic_id, doc_ids in run_list.items():
        with open(os.path.join("runs", topic_id), "a") as file:
            for doc_id in doc_ids:
                if count[topic_id] >= num_runs:
                    continue
                doc = json.loads(searcher.doc(doc_id).raw())["text"]
                print("Evaluating", topic_id)
                run = evaluate(topics[topic_id]["description"], doc)
                if run is not None:
                    count[topic_id] += 1
                    print(f"Writing to {os.path.join('runs', topic_id)}")
                    file.write(f'{doc_id} {run["u"]} {run["s"]} {run["cr"]}\n')


# topic_id, doc_id pairs we will run
run_list = {}
topic_list = ["101","102","103","104","105","106","107","108","109","110","111","112","114","140"]
run_list = get_run_list("misinfo-qrels.3aspects", topic_list=topic_list)

print("RUN LIST OBTAINED")
#print(run_list)

run_run_list(run_list)
