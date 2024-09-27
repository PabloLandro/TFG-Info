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


root = ET.parse('resources/misinfo-2021-topics.xml').getroot()

# Load the topic into a dictionary
topics = {}
for topic in root.findall("topic"):
    topic_id = topic.find("number").text
    topic_description = topic.find("description").text
    topic_stance = topic.find("stance").text
    topics[topic_id] = {}
    topics[topic_id]["description"] = topic_description
    topics[topic_id]["stance"] = topic_stance


# Initialize searcher
searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

matches = 0
lines = 0

# Open the evaluations file
with open("resources/misinfo-qrels.3aspects", "r") as file:

    doc = None

    # Lists with GPT and ideal values
    run = []
    ideal_run = []

    rbo_scores = []

    ideal_run = []
    last_doc_id = None
    last_topic_id = None

    # Iterate over every evalutaion
    for line in file:
        lines = lines + 1
        # Read every parameter from the line
        ideal_case = {}
        topic_id, _, doc_id, ideal_case["usefulness"], ideal_case["supportiveness"], ideal_case["credibility"] = line.split()
        ideal_case["correctness"] = get_correctness(topics[topic_id]["stance"], ideal_case["supportiveness"])
        ideal_case["preference"] = get_preference(ideal_case["usefulness"], ideal_case["correctness"], ideal_case["credibility"])
        ideal_case["doc_id"] = doc_id

        ideal_run.append(ideal_case)
        # We fetch the document content if its not already loaded
        if doc_id != last_doc_id:
            doc = json.loads(searcher.doc(doc_id).raw())["text"]
        # We split runs by topic
        if topic_id != last_topic_id:
            # Order the runs according to their preference
            run = sorted(run, key = lambda x: x["preference"])
            ideal_run = sorted(ideal_run, key = lambda x: x["preference"])
            rbo_scores.append(rbo.RankingSimilarity([case["doc_id"] for case in run], [case["doc_id"] for case in ideal_run]).rbo())
            run = []
            ideal_run = []
        last_topic_id = topic_id
        last_doc_id = doc_id

        case = {}

        # Try to read gpt format
        try:
            # Returns a dictionary containing usefulness, supportiveness and credibility
            case = evaluate(topics[topic_id]["description"], doc)

            # Add correctness and preference to the run
            case["correctness"] = get_correctness(topics[topic_id]["stance"], case["supportiveness"])
            case["preference"] = get_preference(case["usefulness"], case["correctness"], case["credibility"])
            case["doc_id"] = doc_id

            # Add to the list of runs
            run.append(case)

        except Exception as e:
            print(f"Error in evaluation ({topic_id,doc_id}): {e}")
        print("SUCCESS")
avg = sum(rbo_scores) / len(rbo_scores)
print(f"Average RBO: {avg}")
