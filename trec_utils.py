import os
import xml.etree.ElementTree as ET

def preprocess_run(run):
    run["u"] = int(run["u"])
    run["s"] = int(run["s"])
    run["cr"] = int(run["cr"])

def get_qrels_dict(name):
    qrels = {}
    with open(os.path.join("resources", name), "r") as file:
        last_topic_id = ""
        run = []
        for line in file:
            doc_run = {}
            doc_run["topic_id"], _, doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = line.split()
            preprocess_run(doc_run)
            if last_topic_id != doc_run["topic_id"]:
                qrels[last_topic_id] = run
                last_topic_id = doc_run["topic_id"]
                run = [doc_run]
            else:
                run.append(doc_run)
    return qrels

def get_topics_dict(name):
    # Open the topics file as an xml tree
    root = ET.parse(os.path.join('resources', name).getroot()

    # Load the topic into a dictionary
    topics = {}
    for topic in root.findall("topic"):
        topic_id = topic.find("number").text
        topics[topic_id] = {}
        topics[topic_id]["description"] = topic.find("description").text
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

