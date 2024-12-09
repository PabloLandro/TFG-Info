from pyserini.search.lucene import LuceneSearcher
from gpt import evaluate
from trec_utils import get_topics_dict, get_qrels_dict_all
import json
import os

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

print("Starting work")

# Load the topics into a dictionary
topics = get_topics_dict("misinfo-2021-topics.xml")

print("Loaded the topics")

def get_topic(topic_id):
    return topics[topic_id]

qrels = get_qrels_dict_all()
print("qrels loaded")

# For every topic_id we want to know what doc_ids we have already evaluated
exclude = {}
count0 = {}
count1 = {}
for topic_id in os.listdir("runs2"):
    exclude[topic_id] = {}
    count0[topic_id] = 0
    count1[topic_id] = 0
    with open(os.path.join("runs2", topic_id), "r") as file:
        for line in file:
            doc_id,_,_,_ = line.split()
            exclude[topic_id][doc_id] = True
            if qrels[topic_id][doc_id]['u'] > 0:
                count1[topic_id] += 1
            else:
                count0[topic_id] += 1

print("Exclude list created")

# Have this function for checking if a topic_id, doc_id pair was already evaluated
def is_visited(topic_id, doc_id):
    if topic_id in exclude and doc_id in exclude[topic_id]:
        return True
    return False

def get_run_list(topic_list):
    run_list = {}
    for topic_id in qrels:
        if topic_id not in topic_list:
            continue
        if topic_id not in count0:
            count0[topic_id] = 0
        if topic_id not in count1:
            count1[topic_id] = 0
        run_list[topic_id] = []
        for doc_id in qrels[topic_id]:
            if is_visited(topic_id, doc_id):
                continue
            run_list[topic_id].append(doc_id)
    return run_list

def run_run_list(run_list, num_runs=300, directory="runs"):
    for topic_id, doc_ids in run_list.items():
        with open(os.path.join(directory, topic_id), "a") as file:
            for doc_id in doc_ids:
                if qrels[topic_id][doc_id]['u'] == 0 and count0[topic_id] >= num_runs:
                    continue
                if qrels[topic_id][doc_id]['u'] > 0 and count1[topic_id] >= num_runs:
                    continue
                doc = json.loads(searcher.doc(doc_id).raw())["text"]
                print(f"Evaluating {topic_id} {doc_id}")
                run = evaluate(topics[topic_id]["description"], topics[topic_id]["narrative"], doc)
                if run is not None:
                    if qrels[topic_id][doc_id]['u'] == 0:
                        count0[topic_id] += 1
                    else:
                        count1[topic_id] += 1
                    print(f"Writing to {os.path.join(directory, topic_id)}")
                    file.write(f'{doc_id} {run["u"]} {run["s"]} {run["cr"]}\n')

# Gives a run_list to run the same (topic,doc) pairs as another runs folder
def copy_run_list(directory):
    run_list = {}
    for topic_id in os.listdir(directory):
        run_list[topic_id] = []
        with open(os.path.join(directory, topic_id), "r") as file:
            for line in file:
                doc_id,_,_,_ = line.split()
                run_list[topic_id].append(doc_id)
    return run_list

# Replaces all elements in directory that are present in the run_list with new runs
def replace_with_run_list(run_list, directory):
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



topic_list = os.listdir("runs")
run_list = get_run_list(topic_list=topic_list)
#run_list = copy_run_list("aux", directory="runs2")

print("RUN LIST OBTAINED")
print(run_list)

run_run_list(run_list, num_runs=500, directory="runs2")
#replace_with_run_list(run_list, "runs")

