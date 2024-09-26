import os, json, rbo
from gpt import evaluate
from pyserini.search.lucene import LuceneSearcher
import xml.etree.ElementTree as ET

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
    topics[topic_id] = topic_description


# Initialize searcher
searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

matches = 0
lines = 0

# Open the evaluations file
with open("resources/misinfo-qrels.3aspects", "r") as file:

    doc = None
    # GPT Preferences
    run = []

    ideal_run = []
    last_doc_id = None
    last_topic_id = None

    # Iterate over every evalutaion
    for line in file:
        lines = lines + 1
        if lines > 5:
            exit()
        # Read every parameter from the line
        topic_id, _, doc_id, usefulness_judgement, supportiveness_judgement, credibility_judgement = line.split()
        # We fetch the document content if its not already loaded
        if doc_id != last_doc_id:
            doc = json.loads(searcher.doc(doc_id).raw())["text"]
        if topic_id != last_topic_id:
            run = []
        last_topic_id = topic_id
        last_doc_id = doc_id
        try:
            usefulness, supportiveness, credibility = evaluate(topics[topic_id], doc).split()
            if usefulness == usefulness_judgement and supportiveness == supportiveness_judgement and credibility == credibility_judgement:
                    matches = matches + 1
            print(f"Case ({topic_id}, {doc_id}).\tExpected: ({usefulness_judgement}, {supportiveness_judgement}, {credibility_judgement}).\tResult: ({usefulness}, {supportiveness}, {credibility})")
        except Exception as e:
            print(f"Error in evaluation ({topic_id,doc_id}): {e}")
        print("SUCCESS")
print(f"Matches: {matches} out of {lines}")
