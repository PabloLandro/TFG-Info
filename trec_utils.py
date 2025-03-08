import os
import xml.etree.ElementTree as ET

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


def get_qrels_dict(qrels_file, skip_unuseful=True):
    qrels = {}
    with open(qrels_file, "r") as file:
        last_topic_id = ""
        run = {}
        for line in file:
            doc_run = {}
            doc_run["topic_id"], _, doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = unpack_split(line.split())
            preprocess_run(doc_run)
            if doc_run["u"] <= 0 and skip_unuseful:
                continue
            if last_topic_id != doc_run["topic_id"]:
                qrels[last_topic_id] = run
                last_topic_id = doc_run["topic_id"]
                run = {}
            run[doc_run["doc_id"]] = doc_run
    return qrels

def get_qrels_dict_all():
    qrels = {}

    for qrel_file_name in os.listdir(os.path.join("resources", "qrels")):
        qrels_file = os.path.join("resources", "qrels", qrel_file_name)
        aux = get_qrels_dict(qrels_file)
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

def get_topics_dict(topics_file):
    # Open the topics file as an xml tree
    root = ET.parse(topics_file).getroot()
    
    # Load the topic into a dictionary
    topics = {}

    for topic in root.findall("topic"):
        topic_id = topic.find("number").text
        topics[topic_id] = {}
        topics[topic_id]["description"] = topic.find("description").text
        topics[topic_id]["narrative"] = topic.find("narrative").text
    return topics