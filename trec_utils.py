import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
from pyserini.search.lucene import LuceneSearcher

def preprocess_run(run):
    run["u"] = int(run["u"]) if run["u"] is not None else None
    run["s"] = int(run["s"]) if run["s"] is not None else None
    run["cr"] = int(run["cr"]) if run["cr"] is not None else None

def merge_doc_runs(doc_run1, doc_run2):
    out = {}
    error = False
    for id in doc_run1:
        if doc_run1[id] is None:
            out[id] = doc_run2[id]
        elif doc_run2[id] is None:
            out[id] = doc_run1[id]
        else:
            out[id] = doc_run1[id]
            if doc_run1[id] != doc_run2[id]:
                error = True

    return out, error


# Hay veces que un qrel o un run no tenga alguna de las etiquetas, en ese caso añadimos Nones
# para lo que tenemos que crear una función que lo handlee

def unpack_split(parts):
    return (parts + [None] * 6)[:6]


def get_qrels_dict(name, verbose=True):
    qrels = {}
    path = os.path.join("resources", "qrels", name) 
    total_lines = sum(1 for _ in open(path, "r"))
    with open(path, "r") as file:
        file_iterator = tqdm(file, total=total_lines, desc=f"Loading from {name}", unit=" qrels") if verbose else file
        last_topic_id = ""
        run = {}
        for line in file_iterator:
            doc_run = {}
            doc_run["topic_id"], _, doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = unpack_split(line.split())
            preprocess_run(doc_run)
            if last_topic_id != doc_run["topic_id"]:
                qrels[last_topic_id] = run
                last_topic_id = doc_run["topic_id"]
                run = {}
            run[doc_run["doc_id"]] = doc_run
    return qrels

def get_qrels_dict_all(verbose=True):
    qrels = {}

    for qrel_file_name in os.listdir(os.path.join("resources", "qrels")):
        aux = get_qrels_dict(qrel_file_name, verbose=verbose)
        for topic_id, topic_run in aux.items():
            # If that topic id isnt on our dict, we add it
            if topic_id not in qrels:
                qrels[topic_id] = topic_run
            # In other case we iterate over doc_ids to merge the topic_runs
            else:
                for doc_id, doc_run in aux[topic_id].items():
                    qrels[topic_id][doc_id], error = merge_doc_runs(qrels[topic_id][doc_id], doc_run)
                    if error:
                        print(f"ERROR: pair ({topic_id},{doc_id}) is in more than one qrel file")
    return qrels

def get_topics_dict(name, verbose=True):
    # Open the topics file as an xml tree
    root = ET.parse(os.path.join('resources', name)).getroot()
    n_topics = sum(1 for _ in root.findall("topics"))
    t = root.findall("topic")
    iterator = tqdm(t, total=n_topics, desc="Loading topics", unit=" topics") if verbose else t
    
    # Load the topic into a dictionary
    topics = {}

    for topic in iterator:
        topic_id = topic.find("number").text
        topics[topic_id] = {}
        topics[topic_id]["description"] = topic.find("description").text
        topics[topic_id]["narrative"] = topic.find("narrative").text
        topics[topic_id]["stance"] = topic.find("stance").text
    return topics

def get_correctness(stance, supportiveness):
    if stance == "helpful":
        if supportiveness == 2:
            return 2
        elif supportiveness == 0:
            return 0
        else:
            return 1
    elif stance == "unhelpful":
        if supportiveness == 2:
            return 0
        elif supportiveness == 0:
            return 2
        else:
            return 1
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

